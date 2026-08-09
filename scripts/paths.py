"""Dynamic path management for the EL-STRIX engine."""

from pathlib import Path

from exceptions import PathError


class PathManager:
    """Centralized path manager handling dynamic absolute paths."""

    # Core Directories
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    SCRIPTS_DIR: Path = ROOT_DIR / "scripts"
    CONFIG_DIR: Path = ROOT_DIR / "config"
    ASSETS_DIR: Path = ROOT_DIR / "assets"
    TEMPLATES_DIR: Path = ROOT_DIR / "templates"
    GENERATED_DIR: Path = ROOT_DIR / "generated"

    # Asset sub-directories
    ASSET_IMAGE_DIR: Path = ASSETS_DIR / "image"
    ASSET_ASCII_DIR: Path = ASSETS_DIR / "ascii"
    ASSET_SVG_DIR: Path = ASSETS_DIR / "svg"

    # Generated sub-directories
    GENERATED_CACHE_DIR: Path = GENERATED_DIR / "cache"
    GENERATED_JSON_DIR: Path = GENERATED_DIR / "json"
    GENERATED_STATS_DIR: Path = GENERATED_DIR / "stats"
    GENERATED_SVG_DIR: Path = GENERATED_DIR / "svg"
    GENERATED_TEMP_DIR: Path = GENERATED_DIR / "temp"
    GENERATED_LOGS_DIR: Path = GENERATED_DIR / "logs"

    # Important Files
    ENV_FILE: Path = ROOT_DIR / ".env"

    @classmethod
    def get_config_file(cls, filename: str) -> Path:
        """Get the absolute path to a configuration file."""
        return cls.CONFIG_DIR / filename

    @classmethod
    def ensure_directories(cls) -> None:
        """Create all required directories if they do not exist."""
        dirs = [
            cls.CONFIG_DIR,
            cls.ASSET_IMAGE_DIR,
            cls.ASSET_ASCII_DIR,
            cls.ASSET_SVG_DIR,
            cls.GENERATED_CACHE_DIR,
            cls.GENERATED_JSON_DIR,
            cls.GENERATED_STATS_DIR,
            cls.GENERATED_SVG_DIR,
            cls.GENERATED_TEMP_DIR,
            cls.GENERATED_LOGS_DIR,
            cls.TEMPLATES_DIR,
        ]
        try:
            for directory in dirs:
                directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise PathError(f"Failed to create directories: {e}") from e
