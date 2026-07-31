"""Environment variable loading and validation."""

import os
from pathlib import Path

from dotenv import load_dotenv
from exceptions import EnvironmentError
from paths import PathManager
from logger import logger


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
    def get(cls, key: str, default: str | None = None) -> str | None:
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
    def _is_placeholder_token(cls, token: str | None) -> bool:
        """Detect placeholder or invalid token values from environment or config."""
        if not token:
            return True
        normalized = token.strip()
        placeholder_values = {
            "", "****", "******", "null", "none", "<token>", "<gh_token>", "<github_token>",
            "token", "TOKEN", "YOUR_TOKEN_HERE"
        }
        return normalized in placeholder_values or normalized.startswith("<") or normalized.endswith(">")

    @classmethod
    def get_github_token(cls) -> str:
        """Get the GitHub token from standard environment variables."""
        cls.load()
        token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        if cls._is_placeholder_token(token):
            raise EnvironmentError("GitHub token is missing. Please set GH_TOKEN or GITHUB_TOKEN.")
        return token
        
    @classmethod
    def get_github_username(cls) -> str:
        """Get the GitHub username from environment or config fallback."""
        cls.load()
        username = os.getenv("GITHUB_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER")
        if username:
            return username
        
        # Fallback: try to read from config/profile.json
        try:
            import json
            config_path = Path(__file__).resolve().parent.parent / "config" / "profile.json"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    uname = profile.get("username")
                    if uname:
                        return uname
        except Exception as e:
            logger.warning(f"Failed to read username from profile.json: {e}")
        
        return "EL-STRIX"
