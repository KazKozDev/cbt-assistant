import pytest
import os
from pathlib import Path
from src.utils.db import SQLiteSessionManager
from src.llm.ollama_client import OllamaClient
from src.memory.summarizer import MemorySummarizer

# Skipped by default in CI unless running explicitly locally
@pytest.mark.asyncio
async def test_real_memory_summarization(tmp_path):
    # Determine base URL
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Check if Ollama is accessible
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{ollama_url}/api/tags")
            if resp.status_code != 200:
                pytest.skip("Ollama is not responding")
    except Exception:
        pytest.skip("Ollama is not accessible")

    # Set up DB path
    db_file = tmp_path / "test_real_memory.db"
    db_manager = SQLiteSessionManager(db_file)
    
    # Init client, using a fast model if available or fallback
    model_name = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    llm_client = OllamaClient(ollama_url, model=model_name)
    
    # Init summarizer with low threshold to quickly trigger 
    summarizer = MemorySummarizer(db_manager, llm_client)
    summarizer.trigger_threshold = 2
    
    session_id = "real_mem_test_1"
    
    # Insert a conversation
    db_manager.add_message(session_id, "user", "Я очень переживаю из-за предстоящего собеседования на работу.")
    db_manager.add_message(session_id, "assistant", "Это нормально испытывать волнение перед интервью. Вы пробовали подготовить ответы на частые вопросы?")
    db_manager.add_message(session_id, "user", "Да, но у меня начинается паника и я забываю всё. У меня есть собака Рекс, обычно я с ней гуляю, чтобы успокоиться.")
    
    # Trigger summarizer manually
    await summarizer._process_summarization(session_id)
    
    # Fetch summary
    summary = db_manager.get_session_summary(session_id)
    
    # Assertions
    assert summary is not None
    assert summary != ""
    assert len(summary) > 20
    
    # Since LLM output varies, we just print it. When pytest runs, we'll see it in stdout if we use -s.
    print(f"\n[LLM Generated Summary]:\n{summary}\n")
    
    # Add a follow-up conversation to test recursive summarizing
    db_manager.add_message(session_id, "assistant", "Прогулка с Рексом - отличный способ. Давайте попробуем дыхательную технику: вдох на 4 счета, выдох на 4 счета.")
    db_manager.add_message(session_id, "user", "Окей, вроде стало легче.")
    
    await summarizer._process_summarization(session_id)
    
    new_summary = db_manager.get_session_summary(session_id)
    assert new_summary is not None
    assert len(new_summary) > 20
    assert new_summary != summary # should be updated with new context
    
    print(f"\n[Updated LLM Generated Summary]:\n{new_summary}\n")
