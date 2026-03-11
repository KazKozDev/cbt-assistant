import pytest
from pathlib import Path
import sqlite3
from src.utils.db import SQLiteSessionManager

@pytest.fixture
def db_manager(tmp_path):
    db_file = tmp_path / "test.db"
    manager = SQLiteSessionManager(db_file)
    yield manager
    # Teardown: delete db file if needed (tmp_path handles it automatically)

def test_init_db(db_manager):
    # Verify tables are created
    with db_manager._get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "sessions" in tables
        assert "messages" in tables
        assert "mood_logs" in tables
        assert "thought_records" in tables
        assert "sleep_logs" in tables
        assert "tests" in tables
        assert "activities" in tables

def test_get_or_create_session(db_manager):
    session_id = "test_sess_1"
    session = db_manager.get_or_create(session_id)
    assert session["id"] == session_id
    assert session["messages"] == []
    assert session["mood_log"] == []
    assert session["thought_records"] == []
    
    # Check if retrieving again returns the same
    session2 = db_manager.get_or_create(session_id)
    assert session2["created_at"] == session["created_at"]

def test_add_and_get_message(db_manager):
    session_id = "test_sess_2"
    db_manager.add_message(session_id, "user", "Hello CBT")
    
    history = db_manager.get_history(session_id)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello CBT"
    assert "timestamp" in history[0]

def test_add_mood(db_manager):
    session_id = "test_sess_3"
    db_manager.add_mood(session_id, 8, "Feeling great")
    
    session = db_manager.get_or_create(session_id)
    moods = session["mood_log"]
    assert len(moods) == 1
    assert moods[0]["score"] == 8
    assert moods[0]["note"] == "Feeling great"

def test_add_thought_record(db_manager):
    session_id = "test_sess_4"
    thought_id = db_manager.add_thought_record(
        session_id, "situ", "thought", "emotion", 9, "distort", "rational"
    )
    
    session = db_manager.get_or_create(session_id)
    records = session["thought_records"]
    assert len(records) == 1
    assert records[0]["id"] == thought_id
    assert records[0]["situation"] == "situ"
    assert records[0]["distortion"] == "distort"

def test_update_thought_record(db_manager):
    session_id = "test_sess_4_update"
    thought_id = db_manager.add_thought_record(
        session_id, "situ", "thought", "emotion", 9, "distort", "rational"
    )

    updated = db_manager.update_thought_record(
        thought_id,
        session_id,
        "updated situation",
        "updated thought",
        "relief",
        4,
        "Не знаю",
        "updated response",
    )

    assert updated is True
    session = db_manager.get_or_create(session_id)
    records = session["thought_records"]
    assert len(records) == 1
    assert records[0]["situation"] == "updated situation"
    assert records[0]["thought"] == "updated thought"
    assert records[0]["emotion"] == "relief"

def test_sync_and_get_sleep_logs(db_manager):
    session_id = "test_sess_5"
    logs = [
        {"bed": "23:00", "wake": "07:00", "awk": 1, "qual": 8, "notes": "good", "durHrs": "8.0", "isoDate": "2026-03-03T20:00:00.000Z"}
    ]
    db_manager.sync_sleep_logs(session_id, logs)
    
    fetched = db_manager.get_sleep_logs(session_id)
    assert len(fetched) == 1
    assert fetched[0]["dur_hrs"] == 8.0
    assert fetched[0]["qual"] == 8

def test_sync_and_get_test_results(db_manager):
    session_id = "test_sess_6"
    tests = [
        {"name": "PHQ-9", "score": 10, "level": "Умеренная", "date": "2026"}
    ]
    db_manager.sync_test_results(session_id, tests)
    
    fetched = db_manager.get_tests(session_id)
    assert len(fetched) == 1
    assert fetched[0]["test_name"] == "PHQ-9"
    assert fetched[0]["score"] == 10

def test_sync_and_get_activities(db_manager):
    session_id = "test_sess_7"
    activities = [
        {"text": "Walk the dog", "done": True, "isoDate": "2026"}
    ]
    db_manager.sync_activities(session_id, activities)
    
    fetched = db_manager.get_activities(session_id)
    assert len(fetched) == 1
    assert fetched[0]["activity_text"] == "Walk the dog"
    assert fetched[0]["done"] == 1
