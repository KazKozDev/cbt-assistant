"""Local, inspectable retrieval for the bundled CBT knowledge base."""

from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from typing import Any

import numpy as np


CHUNKING_VERSION = "markdown-hierarchy-v2"


class RAGIndexError(RuntimeError):
    """Raised when a complete, usable RAG index cannot be built."""


class SemanticRAG:
    """Semantic retrieval with a cached, versioned and observable local index."""

    def __init__(
        self,
        kb_dir: Path,
        ollama_url: str | None = None,
        embed_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        *,
        cache_path: Path | None = None,
        trace_path: Path | None = None,
        score_threshold: float = 0.46,
        max_chunk_chars: int = 1600,
        overlap_chars: int = 180,
    ):
        self.kb_dir = Path(kb_dir)
        self.ollama_url = (ollama_url or "").rstrip("/")
        self.embed_model = embed_model
        self.cache_path = Path(cache_path) if cache_path else None
        self.trace_path = Path(trace_path) if trace_path else None
        self.score_threshold = score_threshold
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

        self.chunks: list[dict[str, Any]] = []
        self.vectors = np.empty((0, 0), dtype=np.float32)
        self.index_version = ""
        self.state = "not_loaded"
        self.last_error: str | None = None
        self.loaded_from_cache = False
        self._index_lock = asyncio.Lock()
        self._recent_traces: deque[dict[str, Any]] = deque(maxlen=100)
        self._embedding_engine: Any = None

    async def load_and_embed(self) -> None:
        """Build or restore the complete index, then swap it into service atomically."""
        async with self._index_lock:
            self.state = "indexing"
            self.last_error = None
            raw_chunks, fingerprint = self._load_chunks()

            cached = self._load_cache(fingerprint)
            if cached is not None:
                chunks, vectors = cached
                self.chunks, self.vectors = chunks, vectors
                self.index_version = fingerprint
                self.loaded_from_cache = True
                self.state = "ready"
                return

            self.loaded_from_cache = False
            try:
                await self._ensure_model_loaded()
                texts = [f"{c['section_path']}\n{c['content']}" for c in raw_chunks]
                vectors = await self._embed_many(texts)
                if len(vectors) != len(raw_chunks):
                    raise RAGIndexError(
                        f"Embedding count mismatch: {len(vectors)} for {len(raw_chunks)} chunks"
                    )
                matrix = self._normalize_matrix(np.asarray(vectors, dtype=np.float32))
                if matrix.ndim != 2 or matrix.shape[0] != len(raw_chunks):
                    raise RAGIndexError("Embedding service returned an invalid matrix")
                self._write_cache(fingerprint, raw_chunks, matrix)
            except Exception as exc:
                self.state = "failed" if not self.chunks else "degraded"
                self.last_error = str(exc)
                raise RAGIndexError(
                    f"Could not build complete RAG index: {exc}"
                ) from exc

            self.chunks, self.vectors = raw_chunks, matrix
            self.index_version = fingerprint
            self.state = "ready"

    def _load_chunks(self) -> tuple[list[dict[str, Any]], str]:
        files = sorted(self.kb_dir.glob("*.md"))
        if not files:
            raise RAGIndexError(f"No Markdown documents found in {self.kb_dir}")

        digest = hashlib.sha256()
        digest.update(CHUNKING_VERSION.encode())
        digest.update(self.embed_model.encode())
        digest.update(str(self.max_chunk_chars).encode())
        digest.update(str(self.overlap_chars).encode())
        chunks: list[dict[str, Any]] = []

        for path in files:
            text = path.read_text(encoding="utf-8")
            digest.update(path.name.encode())
            digest.update(text.encode())
            chunks.extend(self._chunk_document(path.name, text))

        if not chunks:
            raise RAGIndexError("Knowledge base produced no usable chunks")
        return chunks, digest.hexdigest()[:16]

    def _chunk_document(self, source: str, text: str) -> list[dict[str, Any]]:
        """Split Markdown on its heading hierarchy, then bound oversized sections."""
        heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
        hierarchy: list[str] = []
        sections: list[tuple[list[str], list[str]]] = []
        current_path: list[str] = []
        current_lines: list[str] = []

        def flush() -> None:
            if current_lines and any(line.strip() for line in current_lines):
                sections.append((current_path.copy(), current_lines.copy()))

        for line in text.splitlines():
            match = heading_re.match(line)
            if match:
                flush()
                level = len(match.group(1))
                title = match.group(2).strip()
                hierarchy[level - 1 :] = []
                while len(hierarchy) < level - 1:
                    hierarchy.append("")
                hierarchy.append(title)
                current_path = [part for part in hierarchy if part]
                current_lines = [line]
            else:
                current_lines.append(line)
        flush()

        document_id = "doc_" + hashlib.sha256(source.encode()).hexdigest()[:12]
        output: list[dict[str, Any]] = []
        pending = ""
        ordinal = 0

        for path_parts, lines in sections:
            content = "\n".join(lines).strip()
            if len(content) < 120:
                pending = f"{pending}\n\n{content}".strip()
                continue
            if pending:
                content = f"{pending}\n\n{content}"
                pending = ""
            section_path = " > ".join(path_parts) or source
            for part_number, part in enumerate(
                self._split_long_section(content), start=1
            ):
                ordinal += 1
                identity = f"{source}\n{section_path}\n{part_number}\n{part}"
                chunk_id = "chunk_" + hashlib.sha256(identity.encode()).hexdigest()[:16]
                output.append(
                    {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "source": source,
                        "title": path_parts[-1] if path_parts else source,
                        "section_path": section_path,
                        "part": part_number,
                        "ordinal": ordinal,
                        "content": part,
                    }
                )

        if (
            pending
            and output
            and len(output[-1]["content"]) + len(pending) + 2 <= self.max_chunk_chars
        ):
            output[-1]["content"] = f"{output[-1]['content']}\n\n{pending}"
            identity = (
                f"{source}\n{output[-1]['section_path']}\n"
                f"{output[-1]['part']}\n{output[-1]['content']}"
            )
            output[-1]["chunk_id"] = (
                "chunk_" + hashlib.sha256(identity.encode()).hexdigest()[:16]
            )
        return output

    def _split_long_section(self, text: str) -> list[str]:
        if len(text) <= self.max_chunk_chars:
            return [text]

        paragraphs = re.split(r"\n\s*\n", text)
        parts: list[str] = []
        current = ""
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if len(paragraph) > self.max_chunk_chars:
                if current:
                    parts.append(current)
                    current = ""
                step = max(1, self.max_chunk_chars - self.overlap_chars)
                parts.extend(
                    paragraph[start : start + self.max_chunk_chars].strip()
                    for start in range(0, len(paragraph), step)
                    if paragraph[start : start + self.max_chunk_chars].strip()
                )
                continue
            candidate = f"{current}\n\n{paragraph}".strip()
            if current and len(candidate) > self.max_chunk_chars:
                parts.append(current)
                available = max(0, self.max_chunk_chars - len(paragraph) - 2)
                overlap = current[-min(self.overlap_chars, available) :].lstrip()
                current = f"{overlap}\n\n{paragraph}".strip()
            else:
                current = candidate
        if current:
            parts.append(current)
        return parts

    def _get_embedding_engine(self) -> Any:
        if self._embedding_engine is None:
            try:
                from fastembed import TextEmbedding

                self._embedding_engine = TextEmbedding(model_name=self.embed_model)
            except Exception as exc:
                raise RAGIndexError(
                    f"Failed to load embedding model {self.embed_model!r} via FastEmbed: {exc}"
                ) from exc
        return self._embedding_engine

    async def _ensure_model_loaded(self) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._get_embedding_engine)

    async def _embed_many(
        self, texts: list[str], batch_size: int = 32
    ) -> list[list[float]]:
        if not texts:
            return []
        engine = self._get_embedding_engine()
        loop = asyncio.get_running_loop()

        def _run_embed() -> list[list[float]]:
            return [vec.tolist() for vec in engine.embed(texts, batch_size=batch_size)]

        return await loop.run_in_executor(None, _run_embed)

    async def _embed_query(self, query: str) -> np.ndarray:
        values = await self._embed_many([query], batch_size=1)
        if not values or not values[0]:
            raise RAGIndexError("Embedding service returned an invalid query vector")
        vector = np.asarray(values[0], dtype=np.float32)
        if vector.ndim != 1 or not vector.size:
            raise RAGIndexError("Embedding service returned an invalid query vector")
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector

    @staticmethod
    def _normalize_matrix(matrix: np.ndarray) -> np.ndarray:
        if matrix.ndim != 2 or not matrix.size:
            raise RAGIndexError("No embeddings were returned")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.where(norms == 0, 1, norms)

    def _load_cache(
        self, fingerprint: str
    ) -> tuple[list[dict[str, Any]], np.ndarray] | None:
        if not self.cache_path or not self.cache_path.exists():
            return None
        try:
            with np.load(self.cache_path, allow_pickle=False) as cached:
                metadata = json.loads(str(cached["metadata"].item()))
                vectors = np.asarray(cached["vectors"], dtype=np.float32)
            if (
                metadata.get("fingerprint") != fingerprint
                or metadata.get("embed_model") != self.embed_model
                or metadata.get("chunking_version") != CHUNKING_VERSION
                or len(metadata.get("chunks", [])) != len(vectors)
                or vectors.ndim != 2
                or not vectors.size
                or not np.isfinite(vectors).all()
            ):
                return None
            return metadata["chunks"], vectors
        except Exception:
            return None

    def _write_cache(
        self, fingerprint: str, chunks: list[dict[str, Any]], vectors: np.ndarray
    ) -> None:
        if not self.cache_path:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "fingerprint": fingerprint,
            "embed_model": self.embed_model,
            "chunking_version": CHUNKING_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunks": chunks,
        }
        handle = tempfile.NamedTemporaryFile(
            prefix="rag-index-", suffix=".npz", dir=self.cache_path.parent, delete=False
        )
        temporary = Path(handle.name)
        handle.close()
        try:
            np.savez_compressed(
                temporary,
                vectors=vectors,
                metadata=np.array(json.dumps(metadata, ensure_ascii=False)),
            )
            os.replace(temporary, self.cache_path)
        finally:
            temporary.unlink(missing_ok=True)

    async def search_with_trace(self, query: str, top_k: int = 3) -> dict[str, Any]:
        query = query.strip()
        if not query:
            raise ValueError("query must not be empty")
        if len(query) > 2000:
            raise ValueError("query must be at most 2000 characters")
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")
        if self.state not in {"ready", "degraded"} or not len(self.chunks):
            raise RAGIndexError(f"RAG index is not ready (state={self.state})")

        started = time.perf_counter()
        trace_id = (
            "trace_"
            + hashlib.sha256(f"{time.time_ns()}:{query}".encode()).hexdigest()[:16]
        )
        try:
            query_vector = await self._embed_query(query)
            if self.vectors.shape[1] != query_vector.shape[0]:
                raise RAGIndexError(
                    f"Embedding dimension changed: index={self.vectors.shape[1]}, "
                    f"query={query_vector.shape[0]}"
                )
        except Exception as exc:
            failed_trace = {
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "query": query,
                "top_k": top_k,
                "score_threshold": self.score_threshold,
                "embedding_model": self.embed_model,
                "index_version": self.index_version,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "candidate_scores": [],
                "selected": [],
                "status": "retrieval_error",
                "error": str(exc),
            }
            self._record_trace(failed_trace)
            raise

        similarities = np.dot(self.vectors, query_vector)
        candidate_count = min(max(top_k * 3, 10), len(self.chunks))
        candidate_indices = np.argsort(similarities)[::-1][:candidate_count]
        results = [
            {"chunk": self.chunks[int(index)], "score": float(similarities[index])}
            for index in candidate_indices
            if float(similarities[index]) >= self.score_threshold
        ][:top_k]

        trace = {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "top_k": top_k,
            "score_threshold": self.score_threshold,
            "embedding_model": self.embed_model,
            "index_version": self.index_version,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "candidate_scores": [
                {
                    "chunk_id": self.chunks[int(index)]["chunk_id"],
                    "score": round(float(similarities[index]), 6),
                }
                for index in candidate_indices
            ],
            "selected": [
                {
                    "chunk_id": item["chunk"]["chunk_id"],
                    "document_id": item["chunk"]["document_id"],
                    "source": item["chunk"]["source"],
                    "section_path": item["chunk"]["section_path"],
                    "score": round(item["score"], 6),
                }
                for item in results
            ],
            "status": "grounded" if results else "no_relevant_context",
        }
        self._record_trace(trace)
        return {"results": results, "trace": trace}

    async def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        return (await self.search_with_trace(query, top_k))["results"]

    def _record_trace(self, trace: dict[str, Any]) -> None:
        self._recent_traces.append(trace)
        if not self.trace_path:
            return
        try:
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)
            with self.trace_path.open("a", encoding="utf-8") as output:
                output.write(json.dumps(trace, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def get_recent_traces(self, limit: int = 20) -> list[dict[str, Any]]:
        return list(self._recent_traces)[-max(1, min(limit, 100)) :]

    def get_status(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "chunk_count": len(self.chunks),
            "embedding_model": self.embed_model,
            "index_version": self.index_version,
            "score_threshold": self.score_threshold,
            "loaded_from_cache": self.loaded_from_cache,
            "last_error": self.last_error,
        }

    @staticmethod
    def get_tool_schema() -> dict[str, Any]:
        """Kept for third-party tool clients; chat routes use deterministic retrieval."""
        return {
            "type": "function",
            "function": {
                "name": "search_cbt_knowledge",
                "description": (
                    "Search the local evidence-based CBT knowledge base. Results include "
                    "stable chunk identifiers and provenance."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 1, "maxLength": 2000},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["query"],
                },
            },
        }
