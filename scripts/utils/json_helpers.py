"""JSON parsing and saving helpers."""

import json
from pathlib import Path
from typing import Any

from .file_helpers import ensure_dir


def save_json(data: Any, filepath: str | Path) -> None:
    """Save dictionary to a JSON file safely."""
    path = Path(filepath)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str | Path) -> Any:
    """Load JSON file content safely."""
    path = Path(filepath)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
