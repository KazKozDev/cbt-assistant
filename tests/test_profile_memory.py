from src.memory.profile import (
    extract_profile_updates,
    has_profile_updates,
    merge_profiles,
)
from src.utils.db import SQLiteSessionManager


def test_extracts_explicit_names_pets_people_and_preferences():
    updates = extract_profile_updates(
        "Меня зовут Артём. У меня есть собака Рекс. "
        "Мою жену зовут Анна. Я люблю долгие прогулки."
    )
    assert updates["user_name"] == "Артём"
    assert updates["pets"] == [{"kind": "dog", "name": "Рекс"}]
    assert updates["people"] == [{"relation": "partner", "name": "Анна"}]
    assert updates["preferences"] == ["долгие прогулки"]
    assert has_profile_updates(updates) is True


def test_extracts_pet_from_natural_conversation():
    updates = extract_profile_updates(
        "У меня есть собака Рекс, обычно я с ней гуляю, чтобы успокоиться."
    )
    assert updates["pets"] == [{"kind": "dog", "name": "Рекс"}]


def test_profile_merge_updates_name_without_duplicating_facts():
    initial = merge_profiles({}, extract_profile_updates("Меня зовут Артём. Я люблю чай."))
    updated = merge_profiles(
        initial, extract_profile_updates("Вообще, зови меня Артемий. Я люблю чай.")
    )
    assert updated["user_name"] == "Артемий"
    assert updated["preferences"] == ["чай"]


def test_profile_survives_database_reopen(tmp_path):
    db_path = tmp_path / "persistent.db"
    first_process = SQLiteSessionManager(db_path)
    profile = merge_profiles(
        {}, extract_profile_updates("My name is Alice. My dog is named Charlie.")
    )
    first_process.save_profile_memory("browser-session", profile)

    after_restart = SQLiteSessionManager(db_path)
    restored = after_restart.get_profile_memory("browser-session")
    assert restored["user_name"] == "Alice"
    assert restored["pets"] == [{"kind": "dog", "name": "Charlie"}]


def test_clear_memory_preserves_messages(tmp_path):
    manager = SQLiteSessionManager(tmp_path / "memory.db")
    manager.add_message("session", "user", "Меня зовут Артём")
    manager.save_profile_memory("session", {"user_name": "Артём"})
    manager.save_session_summary("session", "Пользователя зовут Артём")
    manager.clear_memory("session")
    assert manager.get_profile_memory("session") == {}
    assert manager.get_session_summary("session") == ""
    assert manager.get_history("session")[0]["content"] == "Меня зовут Артём"
