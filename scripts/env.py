"""Environment variable loading and validation."""

import os
from typing import Optional
from dotenv import load_dotenv

from paths import PathManager
from exceptions import EnvironmentError

class EnvManager:
    """Manages environment variables securely."""

    _loaded: bool = False

    @classmethod
    def load(cls) -> None:
        """Load environment variables from .env file."""
        if not cls._loaded:
            if PathManager.ENV_FILE.exists():
                load_dotenv(dotenv_path=PathManager.ENV_FILE)
            else:
                # Still try loading system environment variables
                load_dotenv()
            cls._loaded = True

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an environment variable."""
        cls.load()
        return os.getenv(key, default)

    @classmethod
    def require(cls, key: str) -> str:
        """Get a required environment variable or raise an error."""
        val = cls.get(key)
        if not val:
            raise EnvironmentError(f"Required environment variable '{key}' is missing or empty.")
        return val

    @classmethod
    def get_github_token(cls) -> str:
        """Get the GitHub token from standard environment variables."""
        cls.load()
        token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        if not token:
            raise EnvironmentError("GitHub token is missing. Please set GH_TOKEN or GITHUB_TOKEN.")
        return token
        
    @classmethod
    def get_github_username(cls) -> str:
        """Get the GitHub username, falling back to 'EL-STRIX' if running locally without it."""
        cls.load()
        return os.getenv("GITHUB_REPOSITORY_OWNER") or os.getenv("GITHUB_USERNAME") or "EL-STRIX"
