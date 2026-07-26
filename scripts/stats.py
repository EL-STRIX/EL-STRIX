"""GitHub statistics aggregation module."""

import os
import json
from typing import Any, Dict, List, Optional

from logger import logger
from config import (
    GENERATED_STATS_DIR,
    GENERATED_JSON_DIR,
    GITHUB_GRAPHQL_URL,
    GITHUB_TOKEN,
    REQUEST_TIMEOUT,
)

import requests


def fetch_contribution_stats(username: str) -> Dict[str, Any]:
    """Fetch contribution statistics via the GitHub GraphQL API.

    Args:
        username: GitHub username to query.

    Returns:
        Dictionary containing contribution calendar data.
    """
    if not GITHUB_TOKEN:
        logger.warning("No GitHub token set – contribution stats unavailable.")
        return {}

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          totalRepositoryContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    headers = {
        "Authorization": f"bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            GITHUB_GRAPHQL_URL,
            json={"query": query, "variables": {"login": username}},
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("data", {}).get("user", {}).get("contributionsCollection", {})
    except requests.RequestException as exc:
        logger.error(f"Failed to fetch contribution stats for {username}: {exc}")
        return {}


def compute_language_stats(repos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Compute aggregated language byte counts across repositories.

    Args:
        repos: List of repository dictionaries from the GitHub API.

    Returns:
        Mapping of language name → total byte count.
    """
    lang_totals: Dict[str, int] = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            lang_totals[lang] = lang_totals.get(lang, 0) + repo.get("size", 0)
    return dict(sorted(lang_totals.items(), key=lambda x: x[1], reverse=True))


def compute_repo_stats(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Derive aggregate repository metrics.

    Args:
        repos: List of repository dictionaries from the GitHub API.

    Returns:
        Dictionary containing total stars, forks, watchers, and language breakdown.
    """
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    total_watchers = sum(r.get("watchers_count", 0) for r in repos)
    languages = compute_language_stats(repos)

    return {
        "total_repos": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_watchers": total_watchers,
        "languages": languages,
    }


def save_stats(stats: Dict[str, Any], filename: str = "stats.json") -> None:
    """Persist computed statistics to disk.

    Args:
        stats: Statistics dictionary to save.
        filename: Output filename inside the generated stats directory.
    """
    os.makedirs(str(GENERATED_STATS_DIR), exist_ok=True)
    filepath = os.path.join(str(GENERATED_STATS_DIR), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"Stats saved to {filepath}")


def gather_all_stats(
    username: str,
    repos: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Collect and merge all available statistics.

    Args:
        username: GitHub username.
        repos: List of repository dictionaries.

    Returns:
        Merged statistics dictionary.
    """
    repo_stats = compute_repo_stats(repos)
    contribution_stats = fetch_contribution_stats(username)

    merged: Dict[str, Any] = {
        **repo_stats,
        "contributions": contribution_stats,
    }

    save_stats(merged)
    return merged
