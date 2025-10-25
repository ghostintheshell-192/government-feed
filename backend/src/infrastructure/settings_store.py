"""Simple settings storage."""

import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")

DEFAULT_SETTINGS = {
    "ollama_endpoint": "http://localhost:11434",
    "ollama_model": "deepseek-r1:7b",
    "ai_enabled": True,
    "summary_max_words": 200,
}


def load_settings() -> dict:
    """Load settings from file."""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    """Save settings to file."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
