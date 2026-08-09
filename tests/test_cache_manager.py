import hashlib
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from cache_manager import CacheManager
from exceptions import CacheError
from paths import PathManager


def test_cache_manager_path_hashing(mocker, tmp_path):
    """Test that the cache manager hashes keys correctly and generates safe paths."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    manager = CacheManager()

    # Test with a normal key
    key1 = "normal_key"
    path1 = manager._get_path(key1)
    expected_hash1 = hashlib.sha256(key1.encode("utf-8")).hexdigest()
    assert expected_hash1 in path1
    assert path1.endswith(".json")

    # Test with a path traversal key
    key2 = "../../../etc/passwd"
    path2 = manager._get_path(key2)
    expected_hash2 = hashlib.sha256(key2.encode("utf-8")).hexdigest()
    assert expected_hash2 in path2
    assert path2.endswith(".json")
    assert ".." not in path2.split("/")[-1]  # The filename itself should not have traversal


def test_cache_manager_empty_key(mocker, tmp_path):
    """Test that the cache manager raises CacheError when given an empty key."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    manager = CacheManager()

    with pytest.raises(CacheError, match="Invalid cache key"):
        manager._get_path("")

    with pytest.raises(CacheError, match="Invalid cache key"):
        manager.get("")

    with pytest.raises(CacheError, match="Invalid cache key"):
        manager.set("", {"some": "data"})


def test_cache_manager_set_and_get(mocker, tmp_path):
    """Test that the cache manager can set and get a value."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    manager = CacheManager()

    # Set a value
    manager.set("my_key", {"data": 123})

    # Get the value
    result = manager.get("my_key")
    assert result == {"data": 123}


def test_cache_manager_get_expired(mocker, tmp_path):
    """Test that the cache manager returns None for an expired key."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    # Mock time.time to control the timestamp
    mock_time = mocker.patch("time.time")

    # Set initial time
    mock_time.return_value = 1000.0

    manager = CacheManager(ttl_seconds=3600)

    # Set a value
    manager.set("my_key", "my_value")

    # Advance time to just before expiration
    mock_time.return_value = 1000.0 + 3600.0
    assert manager.get("my_key") == "my_value"

    # Advance time to just after expiration
    mock_time.return_value = 1000.0 + 3600.1
    assert manager.get("my_key") is None


def test_cache_manager_get_file_not_found(mocker, tmp_path):
    """Test that the cache manager returns None when the file doesn't exist."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    manager = CacheManager()

    # Get a missing key
    result = manager.get("missing_key")
    assert result is None


def test_cache_manager_get_invalid_json(mocker, tmp_path):
    """Test that the cache manager returns None when the cache file contains invalid JSON."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    manager = CacheManager()

    # Create a mock file with invalid JSON
    key = "invalid_json_key"
    filepath = manager._get_path(key)
    with open(filepath, "w") as f:
        f.write("{invalid_json:")

    # Attempt to get the value
    result = manager.get(key)
    assert result is None


def test_cache_manager_set_os_error(mocker, tmp_path):
    """Test that the cache manager raises CacheError on OSError when setting a value."""
    mocker.patch.object(PathManager, "GENERATED_CACHE_DIR", tmp_path)

    # Mock open to raise OSError
    mocker.patch("builtins.open", side_effect=OSError("Permission denied"))

    manager = CacheManager()

    # Attempt to set a value
    with pytest.raises(CacheError, match="Failed to write cache for my_key: Permission denied"):
        manager.set("my_key", "value")
