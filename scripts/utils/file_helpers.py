"""File and directory helpers."""

import os
from typing import Union
from pathlib import Path

def ensure_dir(directory_path: Union[str, Path]) -> None:
    """Ensure a directory exists on disk."""
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
