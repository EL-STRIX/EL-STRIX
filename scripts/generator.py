"""Banner and content data generator module."""

from typing import Any, Dict
from utils import logger, save_json


class ProfileGenerator:
    """Generates profile data structures and banner metadata."""

    def __init__(self, username: str = "EL-STRIX"):
        self.username = username

    def generate_data(self, profile_info: Dict[str, Any], repos: list) -> Dict[str, Any]:
        """Process raw user data into structured data for rendering."""
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos if isinstance(repo, dict))
        total_forks = sum(repo.get("forks_count", 0) for repo in repos if isinstance(repo, dict))

        data = {
            "username": self.username,
            "name": profile_info.get("name", self.username),
            "bio": profile_info.get("bio", "GitHub Profile & Dynamic Banner Engine"),
            "public_repos": profile_info.get("public_repos", len(repos)),
            "followers": profile_info.get("followers", 0),
            "following": profile_info.get("following", 0),
            "total_stars": total_stars,
            "total_forks": total_forks,
        }

        save_json(data, "generated/data/profile.json")
        logger.info(f"Generated profile data for {self.username}")
        return data
