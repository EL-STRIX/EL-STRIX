"""File and directory helpers."""

from pathlib import Path


def ensure_dir(directory_path: str | Path) -> None:
    """Ensure a directory exists on disk."""
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
