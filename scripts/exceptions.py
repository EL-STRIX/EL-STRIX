"""Custom exceptions for the EL-STRIX engine."""

class ELSTRIXError(Exception):
    """Base exception for all EL-STRIX errors."""
    pass

class ConfigurationError(ELSTRIXError):
    """Raised when there is an issue with the configuration (JSON files)."""
    pass

class EnvironmentError(ELSTRIXError):
    """Raised when required environment variables are missing or invalid."""
    pass

class ValidationError(ELSTRIXError):
    """Raised when data validation fails."""
    pass

class CacheError(ELSTRIXError):
    """Raised when there is an issue interacting with the cache."""
    pass

class PathError(ELSTRIXError):
    """Raised when required paths or directories are inaccessible or invalid."""
    pass
