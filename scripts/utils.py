"""Utility functions and logging configuration for EL-STRIX."""

import os
import json
import logging
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("EL-STRIX")


def ensure_dir(directory_path: str) -> None:
    """Ensure a directory exists on disk."""
    os.makedirs(directory_path, exist_ok=True)


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """Save dictionary to a JSON file."""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved JSON data to {filepath}")


def load_json(filepath: str) -> Dict[str, Any]:
    """Load JSON file content."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
