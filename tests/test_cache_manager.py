import os
import sys
import pytest

# Add scripts directory to path to resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from cache_manager import CacheManager

@pytest.fixture
def cache_manager(tmp_path):
    """Fixture providing a CacheManager instance with a temporary directory."""
    manager = CacheManager()
    manager.cache_dir = tmp_path
    return manager


def test_get_file_not_found(cache_manager):
    """Test get() with a non-existent key returns None."""
    assert cache_manager.get("non_existent_key") is None


def test_get_invalid_json(cache_manager, tmp_path):
    """Test get() with invalid JSON file content returns None."""
    key = "invalid_json_key"
    filepath = tmp_path / f"{key}.json"

    # Write invalid JSON content
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("{invalid json")

    assert cache_manager.get(key) is None
