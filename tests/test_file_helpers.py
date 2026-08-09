import os
import sys
from pathlib import Path

# Add scripts directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from utils.file_helpers import ensure_dir


def test_ensure_dir_creates_new_directory(tmp_path: Path) -> None:
    """Test creating a new directory."""
    test_dir = tmp_path / "new_dir"
    assert not test_dir.exists()

    ensure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

def test_ensure_dir_creates_nested_directories(tmp_path: Path) -> None:
    """Test creating nested directories."""
    test_dir = tmp_path / "parent" / "child" / "grandchild"
    assert not test_dir.exists()

    ensure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

def test_ensure_dir_existing_directory(tmp_path: Path) -> None:
    """Test that function succeeds when directory already exists."""
    test_dir = tmp_path / "existing_dir"
    test_dir.mkdir()
    assert test_dir.exists()

    # Should not raise any exception
    ensure_dir(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()

def test_ensure_dir_with_string_path(tmp_path: Path) -> None:
    """Test that function handles string paths correctly."""
    test_dir = tmp_path / "string_dir"
    assert not test_dir.exists()

    # Pass path as string
    ensure_dir(str(test_dir))

    assert test_dir.exists()
    assert test_dir.is_dir()
