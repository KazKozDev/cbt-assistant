import pytest
from unittest.mock import patch
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.knowledge_base import SemanticRAG
from src.llm.ollama_client import ContentCleaner

def test_rag_tool_schema():
    schema = SemanticRAG.get_tool_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "search_cbt_knowledge"
    assert "query" in schema["function"]["parameters"]["properties"]

@pytest.fixture
def mock_rag(tmp_path):
    # This creates a RAG instance without doing any slow HTTP embedding calls initially
    base_url = "http://mock.local"
    kb_path = tmp_path / "mock_kb"
    kb_path.mkdir(exist_ok=True)
    
    # create dummy md file
    with open(kb_path / "test.md", "w") as f:
        f.write("# Protocol\n\n## Section 1\nThis content needs to be longer than 50 characters to not be skipped by the chunker. Here is some extra text to make it longer.\n\n## Section 2\nThis is another section that also needs to be sufficiently long so it doesn't get skipped. 50 chars is the limit.")
        
    rag = SemanticRAG(kb_dir=kb_path, ollama_url=base_url, embed_model="qwen3-embedding:4b")
    return rag

@patch('src.rag.knowledge_base.SemanticRAG._ensure_model_loaded')
@patch('src.rag.knowledge_base.httpx.AsyncClient.post')
@pytest.mark.asyncio
async def test_rag_embed_and_search(mock_post, mock_ensure, mock_rag):
    import json
    # Mock embedding response
    class MockResponse:
        def __init__(self, embedding):
            self.embedding = embedding
        def raise_for_status(self): pass
        def json(self): return {"embedding": self.embedding}
        
    # the load_and_embed function will call embed_text for each chunk
    # There are 2 chunks in our test.md
    mock_post.return_value = MockResponse([0.1]*768)
    mock_ensure.return_value = None
    
    await mock_rag.load_and_embed()
    
    assert len(mock_rag.chunks) == 2
    assert len(mock_rag.vectors) == 2
    
    # Test search
    # This calls embed_text for the query
    mock_post.return_value = MockResponse([0.1]*768)
    results = await mock_rag.search("protocol content", top_k=1)
    
    assert len(results) == 1
    assert "score" in results[0]
    assert "chunk" in results[0]

def test_content_cleaner():
    cleaner = ContentCleaner()
    # Test basic think stripping
    text = "<think>I need to process this.</think>Hello user!"
    assert cleaner.strip_think_tags(text) == "Hello user!"
    
    # Unfinished think block
    text_unfin = "<think>Almost there..."
    assert cleaner.strip_think_tags(text_unfin) == "<think>Almost there..."
    
    # Normal text
    assert cleaner.strip_think_tags("Normally text") == "Normally text"
    
    # Multiple thinks
    multi = "<think>A</think>B<think>C</think>D"
    assert cleaner.strip_think_tags(multi) == "BD"
