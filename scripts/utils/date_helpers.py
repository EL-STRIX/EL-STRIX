"""Date and time formatting helpers."""

from datetime import UTC, datetime


def get_current_utc_iso() -> str:
    """Get the current time in UTC formatted as ISO 8601."""
    return datetime.now(UTC).isoformat()

def get_current_timestamp() -> int:
    """Get the current unix timestamp."""
    return int(datetime.now(UTC).timestamp())
