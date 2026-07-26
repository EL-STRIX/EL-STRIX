"""String manipulation helpers."""

import re

def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename."""
    # Keep alphanumeric, dashes, underscores, and dots
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
