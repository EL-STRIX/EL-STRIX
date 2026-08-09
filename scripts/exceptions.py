"""Custom exceptions for the EL-STRIX engine."""


class ELSTRIXError(Exception):
    """Base exception for all EL-STRIX errors."""


class ConfigurationError(ELSTRIXError):
    """Raised when there is an issue with the configuration (JSON files)."""


class EnvironmentError(ELSTRIXError):
    """Raised when required environment variables are missing or invalid."""


class CacheError(ELSTRIXError):
    """Raised when there is an issue interacting with the cache."""


class PathError(ELSTRIXError):
    """Raised when required paths or directories are inaccessible or invalid."""


class GitHubAPIError(ELSTRIXError):
    """Raised when GitHub API requests fail."""


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""
