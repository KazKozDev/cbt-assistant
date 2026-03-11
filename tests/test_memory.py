import pytest
from unittest.mock import AsyncMock, MagicMock
from src.utils.db import SQLiteSessionManager
from src.memory.summarizer import MemorySummarizer

@pytest.fixture
def db_manager(tmp_path):
    db_file = tmp_path / "test_memory.db"
    manager = SQLiteSessionManager(db_file)
    yield manager

@pytest.fixture
def mock_llm_client():
    from src.llm.ollama_client import OllamaClient
    client = MagicMock(spec=OllamaClient)
    client.chat = AsyncMock()
    return client

def test_memory_tables_created(db_manager):
    with db_manager._get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "session_summaries" in tables

def test_save_and_get_session_summary(db_manager):
    session_id = "mem_sess_1"
    
    # Init empty
    summary = db_manager.get_session_summary(session_id)
    assert summary == ""
    
    # Save a summary
    db_manager.save_session_summary(session_id, "Summary 1")
    assert db_manager.get_session_summary(session_id) == "Summary 1"
    
    # Update summary
    db_manager.save_session_summary(session_id, "Summary 2")
    assert db_manager.get_session_summary(session_id) == "Summary 2"

def test_get_message_count_since_last_summary(db_manager):
    session_id = "mem_sess_2"
    
    assert db_manager.get_message_count_since_last_summary(session_id) == 0
    
    # Add 5 messages
    for i in range(5):
        db_manager.add_message(session_id, "user", f"Msg {i}")
        
    assert db_manager.get_message_count_since_last_summary(session_id) == 5
    
    # Save summary (which updates last_summarized_msg_id to max message id)
    db_manager.save_session_summary(session_id, "Sum")
    
    # Count should reset
    assert db_manager.get_message_count_since_last_summary(session_id) == 0
    
    # Add 2 more
    db_manager.add_message(session_id, "user", "Msg 6")
    db_manager.add_message(session_id, "assistant", "Msg 7")
    
    assert db_manager.get_message_count_since_last_summary(session_id) == 2

def test_get_unsummarized_messages(db_manager):
    session_id = "mem_sess_3"
    
    # Add 2 messages
    db_manager.add_message(session_id, "user", "Hello")
    db_manager.add_message(session_id, "assistant", "Hi")
    
    unsummarized = db_manager.get_unsummarized_messages(session_id)
    assert len(unsummarized) == 2
    assert unsummarized[0]["content"] == "Hello"
    assert unsummarized[1]["content"] == "Hi"
    
    db_manager.save_session_summary(session_id, "Said hi")
    
    assert len(db_manager.get_unsummarized_messages(session_id)) == 0

@pytest.mark.asyncio
async def test_summarizer_logic_threshold(db_manager, mock_llm_client):
    summarizer = MemorySummarizer(db_manager, mock_llm_client)
    summarizer.trigger_threshold = 3
    session_id = "mem_sess_4"
    
    # Process when below threshold
    db_manager.add_message(session_id, "user", "1")
    db_manager.add_message(session_id, "assistant", "2")
    
    await summarizer._process_summarization(session_id)
    assert mock_llm_client.chat.call_count == 0
    
    # Hit threshold
    db_manager.add_message(session_id, "user", "3")
    
    mock_llm_client.chat.return_value = {"content": "New Summary"}
    await summarizer._process_summarization(session_id)
    
    assert mock_llm_client.chat.call_count == 1
    assert db_manager.get_session_summary(session_id) == "New Summary"
    assert db_manager.get_message_count_since_last_summary(session_id) == 0
