"""Reusable validation utilities."""

from typing import Any
from urllib.parse import urlparse

from exceptions import ValidationError


class Validator:
    """Provides methods for validating common data structures."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Check if a URL is valid."""
        if not url:
            return False
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def validate_github_username(username: str) -> bool:
        """Check if a GitHub username looks valid."""
        if not username or len(username) > 39:
            return False
        # Simplistic validation: alphanumeric and hyphens
        return username.replace("-", "").isalnum()

    @staticmethod
    def validate_json_schema(data: dict[str, Any], required_keys: list[str], filename: str = "JSON") -> None:
        """Ensure a dictionary contains required keys."""
        if not isinstance(data, dict):
            raise ValidationError(f"{filename} must be a dictionary.")
        missing = [key for key in required_keys if key not in data]
        if missing:
            raise ValidationError(f"{filename} is missing required keys: {', '.join(missing)}")
