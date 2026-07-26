"""README Template Generation Engine."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import jinja2

from logger import logger
from paths import PathManager
from config_loader import ConfigLoader
from exceptions import ELSTRIXError
from utils.json_helpers import load_json
from projects import select_featured, format_featured

class ReadmeEngine:
    """Core engine for generating the README.md from templates and data."""

    def __init__(self):
        """Initialize the ReadmeEngine."""
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(PathManager.TEMPLATES_DIR)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.readme_path = PathManager.ROOT_DIR / "README.md"
        
    def _prepare_data(self) -> Dict[str, Any]:
        """Gather all necessary data for the templates."""
        logger.debug("Loading configuration and statistical data for README generation.")
        
        try:
            # Load configs
            configs = ConfigLoader.load_all()
            profile_cfg = configs.get("profile", {})
            skills_cfg = configs.get("skills", {})
            social_cfg = configs.get("social", {})
            settings_cfg = configs.get("settings", {})
            theme_cfg = configs.get("theme", {})
            
            # Load stats
            stats_path = PathManager.GENERATED_STATS_DIR / "processed_statistics.json"
            stats = load_json(stats_path)
            
            profile_stats = stats.get("profile", {})
            star_stats = stats.get("stars", {})
            fork_stats = stats.get("forks", {})
            lang_stats = stats.get("languages", {})
            
            # Load featured projects
            repos_path = PathManager.GENERATED_JSON_DIR / "repos.json"
            repos_data = load_json(repos_path)
            
            featured_repos = []
            if isinstance(repos_data, list) and repos_data:
                selected = select_featured(repos_data, max_count=6)
                featured_repos = format_featured(selected)
                
            # Timestamp
            last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            # Prepare context dictionary
            context = {
                # Profile & Header
                "name": profile_cfg.get("name", "Unknown"),
                "username": profile_cfg.get("username", "Unknown"),
                "bio": profile_cfg.get("bio", ""),
                "company": profile_cfg.get("company", ""),
                "location": profile_cfg.get("location", ""),
                "website": profile_cfg.get("website", ""),
                "email": profile_cfg.get("email", ""),
                
                # Stats
                "total_stars": star_stats.get("total_stars", 0),
                "total_forks": fork_stats.get("total_forks", 0),
                "public_repos": profile_stats.get("total_public_repositories", 0),
                "followers": profile_stats.get("total_followers", 0),
                "following": profile_stats.get("total_following", 0),
                "total_commits": stats.get("commits", {}).get("total_commits", 0),
                "total_contributions": stats.get("contributions", {}).get("total_contributions", 0),
                "total_issues": stats.get("issues", {}).get("total_issues", 0),
                "total_prs": stats.get("pull_requests", {}).get("total_pull_requests", 0),
                "total_releases": stats.get("releases", {}).get("total_releases", 0),
                
                # Languages
                "languages": lang_stats.get("percentage_per_language", {}),
                
                # Featured Projects
                "featured_repos": featured_repos,
                
                # Skills & Socials
                "skills": skills_cfg,
                "social": social_cfg,
                
                # Additional context
                "last_updated": last_updated,
                "settings": settings_cfg,
                "theme": theme_cfg,
            }
            
            return context
        except Exception as e:
            logger.error(f"Failed to prepare data for README: {e}")
            raise ELSTRIXError(f"Data preparation failed: {e}") from e

    def render(self) -> str:
        """Render the README markdown."""
        try:
            logger.info("Loading README template...")
            template = self.env.get_template("README.template.md")
            
            logger.info("Rendering README content...")
            context = self._prepare_data()
            content = template.render(**context)
            
            # Simple Markdown validations could go here
            if not content.strip():
                raise ELSTRIXError("Rendered README is empty.")
                
            return content
        except jinja2.TemplateError as e:
            logger.error(f"Template rendering failed: {e}")
            raise ELSTRIXError(f"Template rendering error: {e}") from e
        except ELSTRIXError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error rendering README: {e}")
            raise ELSTRIXError(f"Unexpected error rendering README: {e}") from e

    def save(self, content: str) -> bool:
        """Save the README.md if content has changed."""
        current_content = ""
        if self.readme_path.exists():
            with open(self.readme_path, "r", encoding="utf-8") as f:
                current_content = f.read()
                
        if current_content == content:
            logger.info("README.md is identical to generated content. Skipping write.")
            return False
            
        try:
            with open(self.readme_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Successfully generated and updated {self.readme_path}")
            return True
        except OSError as e:
            logger.error(f"Failed to write README.md: {e}")
            raise ELSTRIXError(f"Write failure: {e}") from e
        
    def run(self) -> None:
        """Execute the README generation pipeline."""
        logger.info("--- PHASE 06: README GENERATOR ENGINE ---")
        try:
            content = self.render()
            self.save(content)
            logger.info("--- PHASE 06 COMPLETED ---")
        except ELSTRIXError as e:
            logger.error(f"README Engine Failed: {e}")
            raise

if __name__ == "__main__":
    from logger import setup_logger
    setup_logger()
    engine = ReadmeEngine()
    engine.run()
