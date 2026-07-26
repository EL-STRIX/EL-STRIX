"""Featured projects selection module."""

from typing import Any, Dict, List, Optional

from logger import logger


def select_featured(
    repos: List[Dict[str, Any]],
    max_count: int = 6,
    pinned: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Select the top featured repositories for display.

    Selection priority:
        1. Pinned repos (if provided).
        2. Non-fork repos sorted by stars descending.

    Args:
        repos: Full list of repository dictionaries from the GitHub API.
        max_count: Maximum number of featured repos to return.
        pinned: Optional list of repository names to prioritise.

    Returns:
        List of featured repository dictionaries.
    """
    if pinned:
        pinned_set = {name.lower() for name in pinned}
        pinned_repos = [
            r for r in repos if r.get("name", "").lower() in pinned_set
        ]
        remaining = [
            r for r in repos
            if r.get("name", "").lower() not in pinned_set and not r.get("fork", False)
        ]
        remaining.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
        featured = pinned_repos + remaining
    else:
        featured = [r for r in repos if not r.get("fork", False)]
        featured.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)

    result = featured[:max_count]
    logger.info(f"Selected {len(result)} featured repositories.")
    return result


def format_featured(repos: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Normalise featured repo data for template consumption.

    Args:
        repos: Featured repo dictionaries.

    Returns:
        Simplified list of dicts with name, description, url, language, and stars.
    """
    formatted: List[Dict[str, str]] = []
    for repo in repos:
        formatted.append({
            "name": repo.get("name", ""),
            "description": repo.get("description", "") or "No description provided.",
            "url": repo.get("html_url", ""),
            "language": repo.get("language", "N/A") or "N/A",
            "stars": str(repo.get("stargazers_count", 0)),
        })
    return formatted
