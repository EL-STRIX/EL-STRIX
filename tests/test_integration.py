"""Integration and Configuration tests."""

import os
import pytest
import sys

# Ensure scripts module path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from config_loader import ConfigLoader
from paths import PathManager
from exceptions import ConfigurationError
from env import EnvManager

def test_path_manager_directories(tmp_path, monkeypatch):
    """Test PathManager creates directories securely."""
    monkeypatch.setattr(PathManager, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(PathManager, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(PathManager, "GENERATED_DIR", tmp_path / "generated")
    
    # We must patch all child directories to point to tmp_path as well
    monkeypatch.setattr(PathManager, "GENERATED_CACHE_DIR", tmp_path / "generated/cache")
    monkeypatch.setattr(PathManager, "GENERATED_JSON_DIR", tmp_path / "generated/json")
    monkeypatch.setattr(PathManager, "GENERATED_STATS_DIR", tmp_path / "generated/stats")
    monkeypatch.setattr(PathManager, "GENERATED_SVG_DIR", tmp_path / "generated/svg")
    monkeypatch.setattr(PathManager, "GENERATED_TEMP_DIR", tmp_path / "generated/temp")
    monkeypatch.setattr(PathManager, "GENERATED_LOGS_DIR", tmp_path / "generated/logs")
    monkeypatch.setattr(PathManager, "ASSET_IMAGE_DIR", tmp_path / "assets/image")
    monkeypatch.setattr(PathManager, "ASSET_ASCII_DIR", tmp_path / "assets/ascii")
    monkeypatch.setattr(PathManager, "ASSET_SVG_DIR", tmp_path / "assets/svg")
    monkeypatch.setattr(PathManager, "TEMPLATES_DIR", tmp_path / "templates")

    PathManager.ensure_directories()
    
    assert PathManager.CONFIG_DIR.exists()
    assert PathManager.GENERATED_DIR.exists()

def test_config_loader_missing_file(tmp_path, monkeypatch):
    """Test ConfigLoader raises error on missing files."""
    monkeypatch.setattr(PathManager, "CONFIG_DIR", tmp_path)
    
    with pytest.raises(ConfigurationError):
        ConfigLoader.load_json("nonexistent.json")

def test_env_manager_missing_vars(tmp_path, monkeypatch):
    """Test EnvManager validation logic."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setattr(EnvManager, "load", classmethod(lambda cls: None))
    monkeypatch.setattr(EnvManager, "_loaded", False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "user/repo")
    
    # When no valid GitHub token is configured, the manager should raise.
    with pytest.raises(Exception):
        EnvManager.get_github_token()

    # But we can set it and it should pass
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    assert EnvManager.get_github_token() == "fake_token"

