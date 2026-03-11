import pytest
import yaml

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prompts.templates import PromptManager

@pytest.fixture
def temp_config(tmp_path):
    config_data = {
        "system_prompts": {
            "default": "You are a test CBT assistant."
        }
    }
    cfg_path = tmp_path / "prompts.yaml"
    with open(cfg_path, "w") as f:
        yaml.dump(config_data, f)
    return cfg_path

def test_prompt_manager_basic(temp_config):
    pm = PromptManager(temp_config)
    prompt = pm.build_system_prompt([], [], [])
    
    # Needs to contain the default message
    assert "You are a test CBT assistant." in prompt
    # And the required tool instruction we added
    assert "ВНИМАНИЕ" in prompt
    assert "search_cbt_knowledge" in prompt

def test_prompt_manager_with_history(temp_config):
    pm = PromptManager(temp_config)
    
    mood_history = [
        {"timestamp": "12:00", "score": 8, "note": "fine"}
    ]
    
    thought_records = [
        {"timestamp": "12:30", "situation": "Test", "thought": "Fail", "emotion": "Sad", "intensity": 5, "distortion": "Filtering", "rational_response": "Might pass"}
    ]
    
    prompt = pm.build_system_prompt(
        context_chunks=[{"chunk": {"title": "Doc1", "content": "Knowledge content"}}],
        mood_history=mood_history,
        thought_records=thought_records
    )
    
    assert "Doc1" in prompt
    assert "Knowledge content" in prompt
    assert "настроение 8/10" in prompt
    assert "fine" in prompt
    assert "Fail" in prompt
    assert "Sad (5/10)" in prompt
