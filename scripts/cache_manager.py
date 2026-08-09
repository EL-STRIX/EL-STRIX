"""Cache foundation architecture."""

import hashlib
import json
import time
from typing import Any

from exceptions import CacheError
from paths import PathManager


class CacheManager:
    """Manages reading and writing to the file-based cache."""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.cache_dir = PathManager.GENERATED_CACHE_DIR

    def _get_path(self, key: str) -> str:
        """Get the file path for a cache key."""
        if not key:
            raise CacheError("Invalid cache key")
        # Hash key to avoid path traversal and length issues
        safe_key = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return str(self.cache_dir / f"{safe_key}.json")

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache if it hasn't expired."""
        filepath = self._get_path(key)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            timestamp = data.get("timestamp", 0)
            if time.time() - timestamp > self.ttl_seconds:
                return None  # Expired

            return data.get("payload")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def set(self, key: str, payload: Any) -> None:
        """Save a value to the cache with the current timestamp."""
        filepath = self._get_path(key)
        data = {"timestamp": time.time(), "payload": payload}
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except OSError as e:
            raise CacheError(f"Failed to write cache for {key}: {e}")
