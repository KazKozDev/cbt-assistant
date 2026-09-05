import asyncio

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add project root to sys.path so we can import from backend and src
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.server import (
    app,
    ensure_rag_citations,
    execute_app_tool,
    get_user_data_tools,
    kb,
)

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


def test_fetch_ollama_models_returns_every_installed_model():
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

    assert [model["name"] for model in models] == [
        "chat:latest",
        "embed:latest",
        "legacy:latest",
    ]


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


@patch("backend.server.fetch_ollama_models", new_callable=AsyncMock)
def test_model_selection_rejects_embedding_only_model(mock_models):
    mock_models.return_value = [{"name": "embed:latest", "capabilities": ["embedding"]}]

    response = client.put("/api/settings/model", json={"model": "embed:latest"})

    assert response.status_code == 400
    assert "does not support chat" in response.json()["detail"]


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
            {
                "bed": "23:00",
                "wake": "07:00",
                "awk": 1,
                "qual": 8,
                "notes": "good",
                "durHrs": "8.0",
                "isoDate": "2026-03-03T20:00:00.000Z",
            }
        ],
    }
    response = client.post("/api/sync/sleep", json=sleep_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Sync Tests
    test_payload = {
        "session_id": session_id,
        "items": [{"name": "PHQ-9", "score": 10, "level": "Умеренная", "date": "2026"}],
    }
    response = client.post("/api/sync/tests", json=test_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Sync Activities
    act_payload = {
        "session_id": session_id,
        "items": [{"text": "Walk the dog", "done": True, "isoDate": "2026"}],
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
    mood_payload = {"session_id": session_id, "score": 9, "note": "Happy test"}
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
        "rational_response": "It's just code",
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

    chat_payload = {"session_id": session_id, "message": "Hello there"}
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
        json={
            "session_id": "grounded",
            "message": "How can I sleep?",
            "language": "en",
        },
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


def test_sos_tool_contract_exposes_portal_parameters():
    tools = {
        item["function"]["name"]: item["function"] for item in get_user_data_tools()
    }
    sos_tool = tools["start_sos_exercise"]
    parameters = sos_tool["parameters"]

    assert parameters["required"] == ["technique", "scene", "duration"]
    assert parameters["properties"]["technique"]["enum"] == [
        "breathing",
        "grounding",
        "pmr",
        "stop",
    ]
    assert "sea" in parameters["properties"]["scene"]["enum"]
    assert parameters["properties"]["duration"]["maximum"] == 10


def test_sleep_diary_has_a_separate_write_tool_contract():
    tools = {
        item["function"]["name"]: item["function"] for item in get_user_data_tools()
    }

    assert "add_thought_record" in tools
    assert "add_sleep_diary_record" in tools
    sleep_tool = tools["add_sleep_diary_record"]
    assert sleep_tool["parameters"]["required"] == ["bed", "wake"]
    assert "add_thought_record" in sleep_tool["description"]


def test_sos_tool_builds_client_portal_event_and_clamps_duration():
    content, event = execute_app_tool(
        "portal-session",
        {
            "function": {
                "name": "start_sos_exercise",
                "arguments": {"technique": "pmr", "scene": "sea", "duration": 25},
            }
        },
    )

    assert "pmr" in content
    assert event == {
        "type": "start_sos_exercise",
        "technique": "pmr",
        "scene": "sea",
        "duration": 10,
    }


@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_returns_sos_portal_event(mock_chat, override_db):
    mock_chat.side_effect = [
        {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "start_sos_exercise",
                        "arguments": {
                            "technique": "pmr",
                            "scene": "sea",
                            "duration": 5,
                        },
                    }
                }
            ],
        },
        {"content": "Давайте на пять минут перейдём к морю.", "tool_calls": []},
    ]

    response = client.post(
        "/api/chat",
        json={
            "session_id": "sos-portal",
            "message": "Давай расслабим мышцы у моря пять минут",
            "language": "ru",
        },
    )

    assert response.status_code == 200
    assert response.json()["client_events"] == [
        {
            "type": "start_sos_exercise",
            "technique": "pmr",
            "scene": "sea",
            "duration": 5,
        }
    ]


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
                        "arguments": {"activity_text": "Выпить стакан воды"},
                    }
                }
            ],
        },
        {"content": "Я добавил активность в ваш список.", "tool_calls": []},
    ]

    chat_payload = {
        "session_id": session_id,
        "message": "Добавь мне задачу выпить воды",
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


@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_add_thought_record_tool(mock_chat, override_db):
    session_id = "test_chat_add_thought"

    mock_chat.side_effect = [
        {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "add_thought_record",
                        "arguments": {
                            "situation": "Собеседование",
                            "thought": "Я все забуду",
                            "emotion": "Тревога",
                            "intensity": 8,
                            "distortion": "Катастрофизация",
                            "rational_response": "Я готовился и могу отвечать спокойно",
                        },
                    }
                }
            ],
        },
        {"content": "Я записал эту мысль в дневник.", "tool_calls": []},
    ]

    chat_payload = {
        "session_id": session_id,
        "message": "Запиши мысль в дневник",
    }

    response = client.post("/api/chat", json=chat_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Я записал эту мысль в дневник."
    assert "client_events" in data
    assert len(data["client_events"]) == 1
    event = data["client_events"][0]
    assert event["type"] == "add_thought_record"
    assert event["record"]["thought"] == "Я все забуду"
    assert event["record"]["intensity"] == 8

    # Verify directly in database
    records = override_db.get_or_create(session_id)["thought_records"]
    assert len(records) == 1
    assert records[0]["thought"] == "Я все забуду"


@patch("backend.server.llm_client.chat", new_callable=AsyncMock)
def test_chat_add_sleep_record_tool(mock_chat, override_db):
    session_id = "test_chat_add_sleep"

    mock_chat.side_effect = [
        {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "add_sleep_diary_record",
                        "arguments": {
                            "bed": "23:30",
                            "wake": "07:30",
                            "quality": 8,
                            "awakenings": 1,
                            "notes": "Спал хорошо",
                            "date": "2026-08-28",
                        },
                    }
                }
            ],
        },
        {"content": "Запись о сне добавлена.", "tool_calls": []},
    ]

    chat_payload = {
        "session_id": session_id,
        "message": "Я лег в 23:30 и встал в 07:30",
    }

    response = client.post("/api/chat", json=chat_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Запись о сне добавлена."
    assert len(data["client_events"]) == 1
    event = data["client_events"][0]
    assert event["type"] == "add_sleep_log"
    assert event["log"]["bed"] == "23:30"
    assert event["log"]["wake"] == "07:30"
    assert event["log"]["qual"] == 8
    assert event["log"]["durHrs"] == 8.0

    # Verify directly in database
    logs = override_db.get_sleep_logs(session_id)
    assert len(logs) == 1
    assert logs[0]["bed"] == "23:30"
    assert logs[0]["wake"] == "07:30"
    assert logs[0]["dur_hrs"] == 8.0


def test_resource_tools_in_user_data_tools():
    tools = get_user_data_tools()
    tool_names = [t["function"]["name"] for t in tools]
    assert "get_user_resources" in tool_names
    assert "add_user_resource" in tool_names


def test_execute_app_tool_resources(override_db):
    session_id = "test_tool_resources"
    # Test add_user_resource
    tc_add = {
        "function": {
            "name": "add_user_resource",
            "arguments": {
                "title": "Слушать шум дождя",
                "category": "joy",
                "description": "через наушники",
            },
        }
    }
    content, event = execute_app_tool(session_id, tc_add)
    assert "saved to Resource Bank" in content
    assert event is not None
    assert event["type"] == "add_resource"
    assert event["resource"]["title"] == "Слушать шум дождя"

    # Test get_user_resources
    tc_get = {
        "function": {
            "name": "get_user_resources",
            "arguments": {"category": "all"},
        }
    }
    import json

    content, event = execute_app_tool(session_id, tc_get)
    assert event is None
    data = json.loads(content)
    assert len(data) == 1
    assert data[0]["title"] == "Слушать шум дождя"


def test_resources_api_crud(override_db):
    session_id = "test_api_res"
    # 1. Add resource
    resp = client.post(
        "/api/resources",
        json={
            "session_id": session_id,
            "title": "Зеленый чай",
            "category": "joy",
            "description": "с жасмином",
        },
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["status"] == "ok"
    r_id = res_data["id"]
    assert len(res_data["resources"]) == 1

    # 2. Get resources
    get_resp = client.get(f"/api/resources/{session_id}")
    assert get_resp.status_code == 200
    items = get_resp.json()["resources"]
    assert len(items) == 1
    assert items[0]["title"] == "Зеленый чай"

    # 3. Delete resource
    del_resp = client.delete(f"/api/resources/{session_id}/{r_id}")
    assert del_resp.status_code == 200
    assert len(del_resp.json()["resources"]) == 0

    # 4. Delete non-existent
    del_404 = client.delete(f"/api/resources/{session_id}/99999")
    assert del_404.status_code == 404
