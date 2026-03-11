import numpy as np
import httpx
from pathlib import Path


class SemanticRAG:
    """RAG system with semantic search using Ollama embeddings."""

    def __init__(
        self, kb_dir: Path, ollama_url: str, embed_model: str = "qwen3-embedding:4b"
    ):
        self.kb_dir = kb_dir
        self.ollama_url = ollama_url
        self.embed_model = embed_model
        self.chunks = []
        self.vectors = []

    async def load_and_embed(self):
        """Load markdown files, chunk them, and compute embeddings."""
        print(f"[RAG] Loading knowledge base from {self.kb_dir}...")

        # Determine if we need to pull the embedding model
        await self._ensure_model_loaded()

        raw_chunks = []
        for fpath in self.kb_dir.glob("*.md"):
            text = fpath.read_text(encoding="utf-8")
            import re

            sections = re.split(r"\n(?=##\s)", text)
            for section in sections:
                if len(section.strip()) < 50:
                    continue
                lines = section.strip().split("\n")
                title = lines[0].replace("#", "").strip() if lines else ""
                raw_chunks.append(
                    {"title": title, "content": section.strip(), "source": fpath.name}
                )

        # Generate embeddings or load cached (not implementing cache for simplicity now, but could)
        self.chunks = []
        vectors = []
        async with httpx.AsyncClient(timeout=120.0) as client:
            for idx, c in enumerate(raw_chunks):
                # We could batch this, but Ollama embeddings API doesn't fully support batching yet in /api/embeddings vs /api/embed
                try:
                    resp = await client.post(
                        f"{self.ollama_url}/api/embeddings",
                        json={
                            "model": self.embed_model,
                            "prompt": c["title"] + "\n" + c["content"],
                        },
                    )
                    resp.raise_for_status()
                    emb = resp.json().get("embedding")
                    if emb:
                        vectors.append(emb)
                        self.chunks.append(c)
                except Exception as e:
                    print(f"Error embedding chunk {idx}: {e}")

        if vectors:
            self.vectors = np.array(vectors)
            # normalize for cosine similarity
            norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            self.vectors = self.vectors / np.where(norms == 0, 1, norms)
            print(f"[RAG] Successfully loaded and embedded {len(self.chunks)} chunks.")
        else:
            self.vectors = np.array([])
            print("[RAG] No chunks were successfully embedded.")

    async def _ensure_model_loaded(self):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.ollama_url}/api/tags")
                models = [m.get("name") for m in resp.json().get("models", [])]
                if not any(m.startswith(self.embed_model) for m in models):
                    print(
                        f"[RAG] Model {self.embed_model} not found locally, attempting to pull it..."
                    )
                    # Warning: pulling might take a while, in a real scenario we'd do this via a setup script
                    # For MVP, we'll try to pull async
                    await client.post(
                        f"{self.ollama_url}/api/pull", json={"name": self.embed_model}
                    )
        except Exception as e:
            print(f"[RAG] Warning: {e}")

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        if len(self.chunks) == 0:
            return []

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embed_model, "prompt": query},
            )
            resp.raise_for_status()
            q_emb = np.array(resp.json()["embedding"])

        q_norm = np.linalg.norm(q_emb)
        if q_norm > 0:
            q_emb = q_emb / q_norm

        # compute cosine similarities
        similarities = np.dot(self.vectors, q_emb)

        # get top k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append(
                {"chunk": self.chunks[idx], "score": float(similarities[idx])}
            )

        return results

    @staticmethod
    def get_tool_schema():
        return {
            "type": "function",
            "function": {
                "name": "search_cbt_knowledge",
                "description": "Поиск по базе клинических знаний, исследований и практик когнитивно-поведенческой терапии (КПТ). Используй этот инструмент, чтобы получить точную информацию из базы перед тем, как давать конкретные психологические советы или использовать техники.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Поисковый запрос для поиска по материалам КПТ, например: 'техники преодоления тревоги' или 'как работать с бессонницей'."
                        }
                    },
                    "required": ["query"]
                }
            }
        }
