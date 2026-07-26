"""Banner and content data generator module."""

from typing import Any, Dict
from pathlib import Path
from logger import logger
from utils.json_helpers import load_json, save_json
from paths import PathManager


class ProfileGenerator:
    """Generates profile data structures and banner metadata."""

    def __init__(self, username: str = "EL-STRIX"):
        self.username = username

    def generate_data(self) -> Dict[str, Any]:
        """Process raw user data into structured data for rendering, using Phase 03 statistics."""
        stats_path = PathManager.GENERATED_STATS_DIR / "processed_statistics.json"
        stats = load_json(stats_path)

        profile_stats = stats.get("profile", {})
        star_stats = stats.get("stars", {})
        fork_stats = stats.get("forks", {})

        data = {
            "username": self.username,
            "name": self.username, # Should be updated if bio/name are added to stats
            "bio": "GitHub Profile & Dynamic Banner Engine",
            "public_repos": profile_stats.get("total_public_repositories", 0),
            "followers": profile_stats.get("total_followers", 0),
            "following": profile_stats.get("total_following", 0),
            "total_stars": star_stats.get("total_stars", 0),
            "total_forks": fork_stats.get("total_forks", 0),
        }

        output_path = PathManager.GENERATED_JSON_DIR / "profile_render_data.json"
        save_json(data, output_path)
        logger.info(f"Generated profile data for {self.username} using processed stats")
        return data
