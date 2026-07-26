"""Date and time formatting helpers."""

from datetime import datetime, timezone

def get_current_utc_iso() -> str:
    """Get the current time in UTC formatted as ISO 8601."""
    return datetime.now(timezone.utc).isoformat()

def get_current_timestamp() -> int:
    """Get the current unix timestamp."""
    return int(datetime.now(timezone.utc).timestamp())
