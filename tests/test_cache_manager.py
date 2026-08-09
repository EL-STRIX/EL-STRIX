import hashlib
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from cache_manager import CacheManager
from exceptions import CacheError
from paths import PathManager


def test_cache_manager_path_hashing(mocker, tmp_path):
    """Test that the cache manager hashes keys correctly and generates safe paths."""
    mocker.patch.object(PathManager, 'GENERATED_CACHE_DIR', tmp_path)

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
    assert ".." not in path2.split("/")[-1] # The filename itself should not have traversal


def test_cache_manager_empty_key(mocker, tmp_path):
    """Test that the cache manager raises CacheError when given an empty key."""
    mocker.patch.object(PathManager, 'GENERATED_CACHE_DIR', tmp_path)

    manager = CacheManager()

    with pytest.raises(CacheError, match="Invalid cache key"):
        manager._get_path("")

    with pytest.raises(CacheError, match="Invalid cache key"):
        manager.get("")

    with pytest.raises(CacheError, match="Invalid cache key"):
        manager.set("", {"some": "data"})
