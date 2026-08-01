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


def test_set_and_get_success(cache_manager):
    """Test successful set() and get()."""
    key = "test_key"
    payload = {"data": "value"}
    cache_manager.set(key, payload)

    retrieved = cache_manager.get(key)
    assert retrieved == payload


def test_get_expired(cache_manager, mocker):
    """Test get() returns None when the cache is expired."""
    key = "test_key"
    payload = {"data": "value"}
    cache_manager.ttl_seconds = 60 # Set TTL to 60 seconds

    # Mock time.time to return current time during set()
    current_time = 1000.0
    mocker.patch("cache_manager.time.time", return_value=current_time)
    cache_manager.set(key, payload)

    # Mock time.time to return a time past TTL during get()
    mocker.patch("cache_manager.time.time", return_value=current_time + 61.0)
    retrieved = cache_manager.get(key)
    assert retrieved is None


def test_invalid_cache_key_raises_error(cache_manager):
    """Test using an invalid cache key raises CacheError."""
    from exceptions import CacheError
    with pytest.raises(CacheError, match="Invalid cache key"):
        cache_manager._get_path("!@#$%^&*()")

    with pytest.raises(CacheError, match="Invalid cache key"):
        cache_manager.get("!@#$%^&*()")

    with pytest.raises(CacheError, match="Invalid cache key"):
        cache_manager.set("!@#$%^&*()", {"data": "value"})


def test_set_os_error(cache_manager, mocker):
    """Test set() raises CacheError on OSError during write."""
    from exceptions import CacheError
    key = "test_key"
    payload = {"data": "value"}

    # Mock the open function to raise OSError
    mocker.patch("builtins.open", side_effect=OSError("Permission denied"))

    with pytest.raises(CacheError, match="Failed to write cache for test_key: Permission denied"):
        cache_manager.set(key, payload)
