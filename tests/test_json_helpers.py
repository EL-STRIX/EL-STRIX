import json
import os
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from utils.json_helpers import load_json, save_json

def test_save_json_basic(tmp_path: Path) -> None:
    """Test saving a basic dictionary to a JSON file."""
    test_data = {"key": "value"}
    test_file = tmp_path / "test.json"

    save_json(test_data, test_file)

    assert test_file.exists()
    assert json.loads(test_file.read_text(encoding="utf-8")) == test_data

def test_save_json_with_string_path(tmp_path: Path) -> None:
    """Test saving to a JSON file when providing a string path."""
    test_data = {"key": "value"}
    test_file = tmp_path / "test.json"

    save_json(test_data, str(test_file))

    assert test_file.exists()
    assert json.loads(test_file.read_text(encoding="utf-8")) == test_data

def test_save_json_creates_directories(tmp_path: Path) -> None:
    """Test saving to a JSON file creates intermediate directories."""
    test_data = {"key": "value"}
    test_file = tmp_path / "nested" / "dir" / "test.json"

    save_json(test_data, test_file)

    assert test_file.exists()
    assert json.loads(test_file.read_text(encoding="utf-8")) == test_data

def test_save_json_non_ascii(tmp_path: Path) -> None:
    """Test saving dictionary with non-ASCII characters."""
    test_data = {"emoji": "🚀", "text": "こんにちは"}
    test_file = tmp_path / "test.json"

    save_json(test_data, test_file)

    assert test_file.exists()
    assert json.loads(test_file.read_text(encoding="utf-8")) == test_data

    # Ensure characters are actually saved as non-ASCII (not escaped)
    content = test_file.read_text(encoding="utf-8")
    assert "🚀" in content
    assert "こんにちは" in content

def test_load_json_existing(tmp_path: Path) -> None:
    """Test loading an existing valid JSON file."""
    test_file = tmp_path / "test.json"
    test_data = {"key": "value"}
    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    loaded_data = load_json(test_file)

    assert loaded_data == test_data

def test_load_json_non_existing(tmp_path: Path) -> None:
    """Test loading a non-existing file returns an empty dictionary."""
    test_file = tmp_path / "non_existing.json"

    loaded_data = load_json(test_file)

    assert loaded_data == {}

def test_load_json_with_string_path(tmp_path: Path) -> None:
    """Test loading from a JSON file when providing a string path."""
    test_file = tmp_path / "test.json"
    test_data = {"key": "value"}
    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    loaded_data = load_json(str(test_file))

    assert loaded_data == test_data
