import os
import sys
from pathlib import Path

# Add scripts directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from utils.file_helpers import ensure_dir

def test_ensure_dir_creates_directory_str_path(tmp_path):
    """Test creating a directory using a string path."""
    dir_path = str(tmp_path / "test_dir")
    ensure_dir(dir_path)
    assert os.path.isdir(dir_path)

def test_ensure_dir_creates_directory_pathlib_path(tmp_path):
    """Test creating a directory using a pathlib.Path object."""
    dir_path = tmp_path / "test_dir"
    ensure_dir(dir_path)
    assert dir_path.is_dir()

def test_ensure_dir_creates_nested_directories(tmp_path):
    """Test creating nested directories."""
    dir_path = tmp_path / "nested" / "test_dir"
    ensure_dir(dir_path)
    assert dir_path.is_dir()

def test_ensure_dir_existing_directory_no_error(tmp_path):
    """Test calling ensure_dir on an existing directory doesn't raise error."""
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    assert dir_path.is_dir()

    # This should not raise an exception
    ensure_dir(dir_path)
    assert dir_path.is_dir()
