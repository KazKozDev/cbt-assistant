import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add project root to sys.path so we can import from backend and src
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.server import app, sessions

# We use the FastAPI TestClient
client = TestClient(app)

@pytest.fixture
def override_db(tmp_path):
    # This fixture replaces the sessions object with a temporary one
    from src.utils.db import SQLiteSessionManager
    db_file = tmp_path / "test_api.db"
    test_manager = SQLiteSessionManager(db_file)
    
    # We patch the 'sessions' instance inside backend.server
    with patch("backend.server.sessions", test_manager):
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
    
    # Check history is saved
    history = override_db.get_history(session_id)
    assert len(history) == 2  # user and assistant
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello there"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Mocked response"

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
