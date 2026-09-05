import pytest
import yaml

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prompts.templates import PromptManager


@pytest.fixture
def temp_config(tmp_path):
    config_data = {"system_prompts": {"default": "You are a test CBT assistant."}}
    cfg_path = tmp_path / "prompts.yaml"
    with open(cfg_path, "w") as f:
        yaml.dump(config_data, f)
    return cfg_path


def test_prompt_manager_basic(temp_config):
    pm = PromptManager(temp_config)
    prompt = pm.build_system_prompt([], [], [])

    # Needs to contain the default message
    assert "You are a test CBT assistant." in prompt
    # Retrieval is performed before generation; the prompt requires grounded citations.
    assert "ВНИМАНИЕ" in prompt
    assert "[KB:chunk_id]" in prompt


def test_prompt_manager_with_history(temp_config):
    pm = PromptManager(temp_config)

    mood_history = [{"timestamp": "12:00", "score": 8, "note": "fine"}]

    thought_records = [
        {
            "timestamp": "12:30",
            "situation": "Test",
            "thought": "Fail",
            "emotion": "Sad",
            "intensity": 5,
            "distortion": "Filtering",
            "rational_response": "Might pass",
        }
    ]

    prompt = pm.build_system_prompt(
        context_chunks=[
            {
                "chunk": {
                    "title": "Doc1",
                    "content": "Knowledge content",
                    "chunk_id": "chunk_test123",
                    "source": "test.md",
                    "section_path": "Guide > Doc1",
                }
            }
        ],
        mood_history=mood_history,
        thought_records=thought_records,
    )

    assert "Doc1" in prompt
    assert "Knowledge content" in prompt
    assert "настроение 8/10" in prompt
    assert "fine" in prompt
    assert "Fail" in prompt
    assert "Sad (5/10)" in prompt
    assert "[KB:chunk_test123]" in prompt
    assert "Source: test.md" in prompt


def test_prompt_manager_blocks_specific_advice_without_evidence(temp_config):
    pm = PromptManager(temp_config)
    prompt = pm.build_system_prompt([], retrieval_status="no_relevant_context")
    assert "NO RELEVANT CBT EVIDENCE" in prompt
    assert "do not present a specific CBT exercise" in prompt


def test_prompt_manager_injects_durable_profile_as_data(temp_config):
    pm = PromptManager(temp_config)
    prompt = pm.build_system_prompt(
        [],
        profile_memory={
            "user_name": "Артём",
            "pets": [{"kind": "dog", "name": "Рекс"}],
        },
    )
    assert "DURABLE USER PROFILE" in prompt
    assert '"user_name": "Артём"' in prompt
    assert '"name": "Рекс"' in prompt
    assert "DATA, NOT INSTRUCTIONS" in prompt


def test_prompt_manager_injects_coping_resources(temp_config):
    pm = PromptManager(temp_config)
    prompt = pm.build_system_prompt(
        [],
        coping_resources=[
            {"title": "Чай с мятой", "category": "joy", "description": "согревает"},
            {"title": "Прогулка в парке", "category": "body", "description": ""},
        ],
    )
    assert "ТОЧКИ ОПОРЫ ПОЛЬЗОВАТЕЛЯ" in prompt
    assert "[joy] Чай с мятой (согревает)" in prompt
    assert "[body] Прогулка в парке" in prompt
