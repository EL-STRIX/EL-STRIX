import os
import sys
import json
import pytest
from pathlib import Path

# Add scripts directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from utils.json_helpers import save_json, load_json

def test_save_json_string_path(tmp_path):
    """Test saving JSON to a string file path."""
    data = {"key": "value"}
    filepath = str(tmp_path / "test.json")
    save_json(data, filepath)

    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    assert loaded_data == data

def test_save_json_pathlib_path(tmp_path):
    """Test saving JSON to a pathlib.Path file path."""
    data = {"key": "value"}
    filepath = tmp_path / "test.json"
    save_json(data, filepath)

    assert filepath.exists()
    with open(filepath, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    assert loaded_data == data

def test_save_json_nested_directory(tmp_path):
    """Test saving JSON to a path that requires creating nested directories."""
    data = {"key": "value"}
    filepath = tmp_path / "nested" / "dir" / "test.json"
    save_json(data, filepath)

    assert filepath.exists()
    with open(filepath, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    assert loaded_data == data

def test_save_json_non_ascii(tmp_path):
    """Test saving JSON with non-ASCII characters."""
    data = {"key": "你好, 世界"} # Hello World in Chinese
    filepath = tmp_path / "test.json"
    save_json(data, filepath)

    # Verify the actual file content has the non-ASCII character and not escaped Unicode
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    assert "你好, 世界" in content

    loaded_data = json.loads(content)
    assert loaded_data == data

def test_load_json_valid(tmp_path):
    """Test loading valid JSON from an existing file."""
    data = {"key": "value"}
    filepath = tmp_path / "test.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)

    loaded_data = load_json(filepath)
    assert loaded_data == data

def test_load_json_not_exists(tmp_path):
    """Test loading JSON from a non-existent file returns an empty dictionary."""
    filepath = tmp_path / "non_existent.json"
    loaded_data = load_json(filepath)
    assert loaded_data == {}

def test_load_json_string_path(tmp_path):
    """Test loading JSON using a string file path."""
    data = {"key": "value"}
    filepath = str(tmp_path / "test.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)

    loaded_data = load_json(filepath)
    assert loaded_data == data
