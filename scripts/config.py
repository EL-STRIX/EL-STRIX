"""Centralized configuration for the EL-STRIX engine."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# ──────────────────────────────────────────────
# Directory Paths
# ──────────────────────────────────────────────
ROOT_DIR: Path = Path(__file__).resolve().parent.parent
SCRIPTS_DIR: Path = ROOT_DIR / "scripts"
ASSETS_DIR: Path = ROOT_DIR / "assets"
TEMPLATES_DIR: Path = ROOT_DIR / "templates"
GENERATED_DIR: Path = ROOT_DIR / "generated"

# Asset sub-directories
ASSET_IMAGE_DIR: Path = ASSETS_DIR / "image"
ASSET_ASCII_DIR: Path = ASSETS_DIR / "ascii"
ASSET_SVG_DIR: Path = ASSETS_DIR / "svg"
ASSET_TEMPLATE_DIR: Path = ASSETS_DIR / "template"

# Generated sub-directories
GENERATED_CACHE_DIR: Path = GENERATED_DIR / "cache"
GENERATED_JSON_DIR: Path = GENERATED_DIR / "json"
GENERATED_STATS_DIR: Path = GENERATED_DIR / "stats"
GENERATED_SVG_DIR: Path = GENERATED_DIR / "svg"
GENERATED_TEMP_DIR: Path = GENERATED_DIR / "temp"

# ──────────────────────────────────────────────
# GitHub Configuration
# ──────────────────────────────────────────────
GITHUB_TOKEN: Optional[str] = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME: str = os.getenv("GITHUB_REPOSITORY_OWNER", "EL-STRIX")
GITHUB_API_URL: str = "https://api.github.com"
GITHUB_GRAPHQL_URL: str = "https://api.github.com/graphql"

# ──────────────────────────────────────────────
# Rendering Configuration
# ──────────────────────────────────────────────
SVG_WIDTH: int = 850
SVG_HEIGHT: int = 280
ASCII_WIDTH: int = 80
ASCII_CHARSET: str = " .:-=+*#%@"

# ──────────────────────────────────────────────
# Template Files
# ──────────────────────────────────────────────
README_TEMPLATE: Path = TEMPLATES_DIR / "README.template.md"
HEADER_TEMPLATE: Path = TEMPLATES_DIR / "header.md"
FOOTER_TEMPLATE: Path = TEMPLATES_DIR / "footer.md"
PROFILE_SVG_TEMPLATE: Path = TEMPLATES_DIR / "profile.svg"

# ──────────────────────────────────────────────
# Cache Settings
# ──────────────────────────────────────────────
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL", "3600"))
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))


def ensure_directories() -> None:
    """Create all required directories if they do not exist."""
    dirs = [
        ASSET_IMAGE_DIR,
        ASSET_ASCII_DIR,
        ASSET_SVG_DIR,
        ASSET_TEMPLATE_DIR,
        GENERATED_CACHE_DIR,
        GENERATED_JSON_DIR,
        GENERATED_STATS_DIR,
        GENERATED_SVG_DIR,
        GENERATED_TEMP_DIR,
        TEMPLATES_DIR,
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
