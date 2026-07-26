"""Centralized JSON configuration loader."""

import json
from typing import Any

from exceptions import ConfigurationError
from paths import PathManager


class ConfigLoader:
    """Loads and validates JSON configuration files."""

    @staticmethod
    def load_json(filename: str) -> dict[str, Any]:
        """Load a JSON configuration file from the config directory."""
        filepath = PathManager.get_config_file(filename)
        if not filepath.exists():
            raise ConfigurationError(f"Configuration file not found: {filepath}")
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ConfigurationError(f"Configuration file {filename} must contain a JSON object.")
            return data
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {filename}: {e}")
        except OSError as e:
            raise ConfigurationError(f"Failed to read {filename}: {e}")

    @classmethod
    def load_all(cls) -> dict[str, dict[str, Any]]:
        """Load all core configuration files."""
        return {
            "profile": cls.load_json("profile.json")
        }
