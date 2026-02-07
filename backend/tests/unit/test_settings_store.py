"""Unit tests for settings store."""

import json
from unittest.mock import patch

from backend.src.infrastructure.settings_store import (
    DEFAULT_SETTINGS,
    load_settings,
    save_settings,
)


class TestSettingsStore:
    """Tests for settings load/save with file I/O."""

    def test_load_returns_defaults_when_no_file(self, tmp_path):
        fake_path = tmp_path / "settings.json"
        with patch("backend.src.infrastructure.settings_store.SETTINGS_FILE", fake_path):
            result = load_settings()
        assert result == DEFAULT_SETTINGS

    def test_load_returns_defaults_copy(self, tmp_path):
        fake_path = tmp_path / "settings.json"
        with patch("backend.src.infrastructure.settings_store.SETTINGS_FILE", fake_path):
            result = load_settings()
        # Mutating the result should not affect DEFAULT_SETTINGS
        result["ollama_model"] = "changed"
        assert DEFAULT_SETTINGS["ollama_model"] != "changed"

    def test_save_and_load_roundtrip(self, tmp_path):
        fake_path = tmp_path / "settings.json"
        custom = {"ollama_endpoint": "http://custom:11434", "ai_enabled": False}

        with patch("backend.src.infrastructure.settings_store.SETTINGS_FILE", fake_path):
            save_settings(custom)
            result = load_settings()

        assert result == custom

    def test_save_creates_file(self, tmp_path):
        fake_path = tmp_path / "settings.json"
        with patch("backend.src.infrastructure.settings_store.SETTINGS_FILE", fake_path):
            save_settings({"key": "value"})
        assert fake_path.exists()
        content = json.loads(fake_path.read_text())
        assert content == {"key": "value"}

    def test_save_overwrites_existing(self, tmp_path):
        fake_path = tmp_path / "settings.json"
        with patch("backend.src.infrastructure.settings_store.SETTINGS_FILE", fake_path):
            save_settings({"version": 1})
            save_settings({"version": 2})
            result = load_settings()
        assert result["version"] == 2
