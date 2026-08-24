from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from src.llm.ollama_client import ContentCleaner
from src.rag.knowledge_base import RAGIndexError, SemanticRAG


def test_rag_tool_schema():
    schema = SemanticRAG.get_tool_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "search_cbt_knowledge"
    assert schema["function"]["parameters"]["properties"]["top_k"]["maximum"] == 20


@pytest.fixture
def mock_rag(tmp_path):
    kb_path = tmp_path / "mock_kb"
    kb_path.mkdir()
    (kb_path / "test.md").write_text(
        "# Protocol\n\n"
        "## Sleep\n"
        "Leave the bed after twenty minutes awake. This is stimulus control guidance "
        "with enough detail to form a useful retrieval chunk.\n\n"
        "## Anxiety\n"
        "Scheduled worry time can help postpone repetitive worry. This section also "
        "contains enough detail to form a separate useful retrieval chunk.",
        encoding="utf-8",
    )
    return SemanticRAG(
        kb_dir=kb_path,
        ollama_url="http://mock.local",
        cache_path=tmp_path / "rag_index.npz",
        trace_path=tmp_path / "rag_traces.jsonl",
        embed_model="test-embedding",
        score_threshold=0.6,
        max_chunk_chars=300,
    )


@pytest.mark.asyncio
async def test_rag_build_search_provenance_trace_and_cache(mock_rag):
    with (
        patch.object(mock_rag, "_ensure_model_loaded", new=AsyncMock()),
        patch.object(
            mock_rag,
            "_embed_many",
            new=AsyncMock(side_effect=[[[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0]]]),
        ),
    ):
        await mock_rag.load_and_embed()
        retrieval = await mock_rag.search_with_trace("cannot sleep", top_k=1)

    assert mock_rag.state == "ready"
    assert len(mock_rag.chunks) == 2
    assert retrieval["results"][0]["chunk"]["section_path"].endswith("Sleep")
    assert retrieval["results"][0]["chunk"]["chunk_id"].startswith("chunk_")
    assert retrieval["results"][0]["chunk"]["document_id"].startswith("doc_")
    assert retrieval["trace"]["status"] == "grounded"
    assert retrieval["trace"]["selected"][0]["source"] == "test.md"
    assert mock_rag.trace_path.read_text(encoding="utf-8").count("trace_id") == 1

    restored = SemanticRAG(
        mock_rag.kb_dir,
        mock_rag.ollama_url,
        mock_rag.embed_model,
        cache_path=mock_rag.cache_path,
        score_threshold=0.6,
        max_chunk_chars=300,
    )
    ensure = AsyncMock()
    with patch.object(restored, "_ensure_model_loaded", new=ensure):
        await restored.load_and_embed()
    ensure.assert_not_awaited()
    assert restored.loaded_from_cache is True
    assert [chunk["chunk_id"] for chunk in restored.chunks] == [
        chunk["chunk_id"] for chunk in mock_rag.chunks
    ]


@pytest.mark.asyncio
async def test_rag_abstains_below_threshold(mock_rag):
    with (
        patch.object(mock_rag, "_ensure_model_loaded", new=AsyncMock()),
        patch.object(
            mock_rag,
            "_embed_many",
            new=AsyncMock(side_effect=[[[1.0, 0.0], [0.0, 1.0]], [[-1.0, -1.0]]]),
        ),
    ):
        await mock_rag.load_and_embed()
        retrieval = await mock_rag.search_with_trace("unrelated", top_k=2)
    assert retrieval["results"] == []
    assert retrieval["trace"]["status"] == "no_relevant_context"


@pytest.mark.asyncio
async def test_incomplete_index_fails_closed(mock_rag):
    with (
        patch.object(mock_rag, "_ensure_model_loaded", new=AsyncMock()),
        patch.object(mock_rag, "_embed_many", new=AsyncMock(return_value=[[1.0, 0.0]])),
        pytest.raises(RAGIndexError, match="Embedding count mismatch"),
    ):
        await mock_rag.load_and_embed()
    assert mock_rag.state == "failed"
    assert mock_rag.chunks == []


def test_structural_chunking_bounds_large_sections(mock_rag):
    text = "# Guide\n\n## Large section\n\n" + "A useful paragraph. " * 100
    chunks = mock_rag._chunk_document("large.md", text)
    assert len(chunks) > 1
    assert all(len(chunk["content"]) <= mock_rag.max_chunk_chars for chunk in chunks)
    assert all("Large section" in chunk["section_path"] for chunk in chunks)


@pytest.mark.asyncio
async def test_search_validates_inputs(mock_rag):
    mock_rag.state = "ready"
    mock_rag.chunks = [{"chunk_id": "one"}]
    with pytest.raises(ValueError, match="empty"):
        await mock_rag.search("")


@pytest.mark.asyncio
async def test_retrieval_errors_are_traced(mock_rag):
    mock_rag.state = "ready"
    mock_rag.index_version = "test-version"
    mock_rag.chunks = [{"chunk_id": "chunk_one"}]
    mock_rag.vectors = np.array([[1.0, 0.0]], dtype=np.float32)
    with (
        patch.object(
            mock_rag, "_embed_query", new=AsyncMock(side_effect=RuntimeError("offline"))
        ),
        pytest.raises(RuntimeError, match="offline"),
    ):
        await mock_rag.search("valid query")
    assert mock_rag.get_recent_traces(1)[0]["status"] == "retrieval_error"
    assert mock_rag.get_recent_traces(1)[0]["error"] == "offline"


def test_content_cleaner():
    cleaner = ContentCleaner()
    assert cleaner.strip_think_tags("<think>process</think>Hello") == "Hello"
    assert cleaner.strip_think_tags("<think>unfinished") == "<think>unfinished"
    assert cleaner.strip_think_tags("Normally text") == "Normally text"
    assert cleaner.strip_think_tags("<think>A</think>B<think>C</think>D") == "BD"
