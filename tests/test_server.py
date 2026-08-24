import asyncio

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add project root to sys.path so we can import from backend and src
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.server import app, ensure_rag_citations, kb, sessions

# We use the FastAPI TestClient
client = TestClient(app)


def test_server_guarantees_known_rag_citation():
    context = [{"chunk_id": "chunk_known", "source": "guide.md"}]
    cited = ensure_rag_citations("Grounded answer.", context, "en")
    assert "[KB:chunk_known]" in cited
    assert "guide.md" in cited
    assert ensure_rag_citations(cited, context, "en") == cited


@patch("backend.server.fetch_ollama_models", new_callable=AsyncMock)
def test_models_endpoint_lists_installed_models(mock_models):
    mock_models.return_value = [
        {"name": "gemma3:4b", "size": 123},
        {"name": "ornith-1.5:9b", "size": 456},
    ]

    response = client.get("/api/models")

    assert response.status_code == 200
    assert [model["name"] for model in response.json()["models"]] == [
        "gemma3:4b",
        "ornith-1.5:9b",
    ]
    assert response.json()["selected_model"]


def test_fetch_ollama_models_excludes_embedding_only_models():
    from backend import server

    ollama_response = AsyncMock()
    ollama_response.raise_for_status = lambda: None
    ollama_response.json = lambda: {
        "models": [
            {"name": "chat:latest", "capabilities": ["completion", "tools"]},
            {"name": "embed:latest", "capabilities": ["embedding"]},
            {"name": "legacy:latest"},
        ]
    }
    async_client = AsyncMock()
    async_client.__aenter__.return_value.get.return_value = ollama_response

    with patch("httpx.AsyncClient", return_value=async_client):
        models = asyncio.run(server.fetch_ollama_models())

    assert [model["name"] for model in models] == ["chat:latest", "legacy:latest"]


@patch("backend.server.persist_selected_model")
@patch("backend.server.fetch_ollama_models", new_callable=AsyncMock)
def test_model_can_be_selected_and_persisted(mock_models, mock_persist):
    from backend import server

    previous_model = server.llm_client.model
    mock_models.return_value = [{"name": "gemma3:4b"}]
    try:
        response = client.put("/api/settings/model", json={"model": "gemma3:4b"})
        assert response.status_code == 200
        assert response.json()["selected_model"] == "gemma3:4b"
        assert server.llm_client.model == "gemma3:4b"
        mock_persist.assert_called_once_with("gemma3:4b")
    finally:
        server.llm_client.model = previous_model


@patch("backend.server.fetch_ollama_models", new_callable=AsyncMock)
def test_model_selection_rejects_uninstalled_model(mock_models):
    mock_models.return_value = [{"name": "installed:latest"}]

    response = client.put("/api/settings/model", json={"model": "missing:latest"})

    assert response.status_code == 400


@pytest.fixture
def override_db(tmp_path):
    # This fixture replaces the sessions object with a temporary one
    from src.utils.db import SQLiteSessionManager
    db_file = tmp_path / "test_api.db"
    test_manager = SQLiteSessionManager(db_file)
    
    # We patch the 'sessions' instance inside backend.server
    retrieval = {
        "results": [],
        "trace": {
            "trace_id": "trace_test",
            "status": "no_relevant_context",
            "latency_ms": 1.0,
            "index_version": "index_test",
        },
    }
    with (
        patch("backend.server.sessions", test_manager),
        patch(
            "backend.server.kb.search_with_trace",
            new=AsyncMock(return_value=retrieval),
        ),
    ):
        yield test_manager

def test_sync_endpoints(override_db):
    session_id = "test_sync_endpoint"
    
    # Sync Sleeps
    sleep_payload = {
        "session_id": session_id,
        "items": [
            {"bed": "23:00", "wake": "07:00", "awk": 1, "qual": 8, "notes": "good", "durHrs": "8.0", "isoDate": "2026-03-03T20:00:00.000Z"}
        ]
    }
    response = client.post("/api/sync/sleep", json=sleep_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Sync Tests
    test_payload = {
        "session_id": session_id,
        "items": [
            {"name": "PHQ-9", "score": 10, "level": "Умеренная", "date": "2026"}
        ]
    }
    response = client.post("/api/sync/tests", json=test_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Sync Activities
    act_payload = {
        "session_id": session_id,
        "items": [
            {"text": "Walk the dog", "done": True, "isoDate": "2026"}
        ]
    }
    response = client.post("/api/sync/activities", json=act_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Verify in DB
    activities = override_db.get_activities(session_id)
    assert len(activities) == 1
    assert activities[0]["activity_text"] == "Walk the dog"

def test_mood_endpoint(override_db):
    session_id = "test_mood_endpoint"
    mood_payload = {
        "session_id": session_id,
        "score": 9,
        "note": "Happy test"
    }
    response = client.post("/api/mood", json=mood_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Get mood
    response = client.get(f"/api/mood/{session_id}")
    assert response.status_code == 200
    moods = response.json()["mood_log"]
    assert len(moods) == 1
    assert moods[0]["score"] == 9
    assert moods[0]["note"] == "Happy test"

def test_thought_record_endpoint(override_db):
    session_id = "test_thought_endpoint"
    tr_payload = {
        "session_id": session_id,
        "situation": "Testing API",
        "thought": "It will fail",
        "emotion": "Anxiety",
        "intensity": 6,
        "distortion": "Fortune Telling",
        "rational_response": "It's just code"
    }
    response = client.post("/api/thoughts", json=tr_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Get thoughts
    session_data = client.get(f"/api/session/{session_id}").json()
    trs = session_data["thought_records"]
    assert len(trs) == 1
    assert trs[0]["situation"] == "Testing API"

def test_update_thought_record_endpoint(override_db):
    session_id = "test_thought_update_endpoint"
    thought_id = override_db.add_thought_record(
        session_id,
        "Before",
        "Old thought",
        "Anxiety",
        6,
        "Fortune Telling",
        "It's just code",
    )

    tr_payload = {
        "session_id": session_id,
        "situation": "After",
        "thought": "New thought",
        "emotion": "Calm",
        "intensity": 3,
        "distortion": "Не знаю",
        "rational_response": "Updated response",
    }
    response = client.put(f"/api/thoughts/{thought_id}", json=tr_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    session_data = client.get(f"/api/session/{session_id}").json()
    trs = session_data["thought_records"]
    assert len(trs) == 1
    assert trs[0]["id"] == thought_id
    assert trs[0]["situation"] == "After"
    assert trs[0]["thought"] == "New thought"

@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_endpoint(mock_chat, override_db):
    session_id = "test_chat_endpoint"
    mock_chat.return_value = {"content": "Mocked response", "tool_calls": []}
    
    chat_payload = {
        "session_id": session_id,
        "message": "Hello there"
    }
    response = client.post("/api/chat", json=chat_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Mocked response"
    assert data["session_id"] == session_id
    assert data["context_used"] == []
    assert data["rag_trace"]["status"] == "no_relevant_context"

    request_messages = mock_chat.await_args.args[0]
    assert "Reply in English only" in request_messages[0]["content"]
    
    # Check history is saved
    history = override_db.get_history(session_id)
    assert len(history) == 2  # user and assistant
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello there"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Mocked response"


@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_returns_provenance_and_guaranteed_citation(mock_chat, override_db):
    mock_chat.return_value = {"content": "Use stimulus control.", "tool_calls": []}
    kb.search_with_trace.return_value = {
        "results": [
            {
                "chunk": {
                    "chunk_id": "chunk_sleep",
                    "document_id": "doc_sleep",
                    "source": "sleep.md",
                    "title": "Stimulus control",
                    "section_path": "CBT-I > Stimulus control",
                    "content": "Leave the bed when unable to sleep.",
                },
                "score": 0.81,
            }
        ],
        "trace": {
            "trace_id": "trace_sleep",
            "status": "grounded",
            "latency_ms": 2.0,
            "index_version": "index_sleep",
        },
    }
    response = client.post(
        "/api/chat",
        json={"session_id": "grounded", "message": "How can I sleep?", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["context_used"][0]["chunk_id"] == "chunk_sleep"
    assert data["context_used"][0]["source"] == "sleep.md"
    assert "[KB:chunk_sleep]" in data["response"]


@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_hard_abstains_on_unsupported_clinical_advice(mock_chat, override_db):
    response = client.post(
        "/api/chat",
        json={
            "session_id": "unsupported_clinical",
            "message": "Как лечить неизвестную тревогу специальной техникой?",
            "language": "ru",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rag_trace"]["status"] == "abstained"
    assert "не буду придумывать" in data["response"]
    mock_chat.assert_not_awaited()


@patch("backend.server.summarizer.maybe_summarize", new_callable=AsyncMock)
@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_rest_chat_persists_profile_and_triggers_summary(
    mock_chat, mock_maybe_summarize, override_db
):
    mock_chat.return_value = {"content": "Рад знакомству.", "tool_calls": []}
    response = client.post(
        "/api/chat",
        json={
            "session_id": "persistent-browser-session",
            "message": "Меня зовут Артём, а мою собаку зовут Рекс.",
            "language": "ru",
        },
    )
    assert response.status_code == 200
    memory = client.get("/api/memory/persistent-browser-session").json()
    assert memory["profile"]["user_name"] == "Артём"
    assert memory["profile"]["pets"] == [{"kind": "dog", "name": "Рекс"}]
    system_prompt = mock_chat.await_args.args[0][0]["content"]
    assert '"user_name": "Артём"' in system_prompt
    assert '"name": "Рекс"' in system_prompt
    mock_maybe_summarize.assert_awaited_once_with("persistent-browser-session")


def test_memory_can_be_cleared_through_api(override_db):
    override_db.save_profile_memory("forget-me", {"user_name": "Артём"})
    response = client.delete("/api/memory/forget-me")
    assert response.status_code == 200
    assert client.get("/api/memory/forget-me").json()["profile"] == {}

@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_add_activity_tool(mock_chat, override_db):
    session_id = "test_chat_add_activity"
    
    # We mock the first call to return a tool call
    mock_chat.side_effect = [
        {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "add_user_activity",
                        "arguments": {"activity_text": "Выпить стакан воды"}
                    }
                }
            ]
        },
        {
            "content": "Я добавил активность в ваш список.",
            "tool_calls": []
        }
    ]
    
    chat_payload = {
        "session_id": session_id,
        "message": "Добавь мне задачу выпить воды"
    }
    
    response = client.post("/api/chat", json=chat_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Я добавил активность в ваш список."
    assert "client_events" in data
    
    events = data["client_events"]
    assert len(events) == 1
    assert events[0]["type"] == "add_activity"
    assert events[0]["text"] == "Выпить стакан воды"
