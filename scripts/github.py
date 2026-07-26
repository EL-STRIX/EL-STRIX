"""GitHub API helper functions for fetching user metrics and repository stats."""

import os
from typing import Any, Dict, Optional
import requests
from utils import logger

GITHUB_API_URL = "https://api.github.com"


class GitHubClient:
    """Wrapper for fetching user stats via GitHub REST & GraphQL APIs."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch basic public profile information for a user."""
        url = f"{GITHUB_API_URL}/users/{username}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch profile for {username}: {e}")
            return {}

    def get_user_repos(self, username: str) -> list:
        """Fetch repositories for a user."""
        url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch repos for {username}: {e}")
            return []
