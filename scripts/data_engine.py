"""Centralized Data Engine for fetching and storing GitHub data."""

from typing import Any

from env import EnvManager
from github import GitHubClient
from logger import logger
from paths import PathManager
from utils.json_helpers import save_json


class DataEngine:
    """Orchestrates the fetching of all raw data from GitHub and saving it to structured JSON."""

    def __init__(self):
        self.client = GitHubClient()
        self.username = EnvManager.get_github_username()

    def run_all(self):
        """Execute the full data collection pipeline."""
        logger.info(f"Starting Data Engine pipeline for {self.username}")
        
        # 1. Profile and Avatar
        profile = self.fetch_profile()
        if profile.get("avatar_url"):
            self.download_avatar(profile["avatar_url"])
            
        # 2. Repositories
        self.fetch_repositories()
        
        # 3. Contributions & Statistics
        self.fetch_contributions()
        
        # 4. Pinned Repositories
        self.fetch_pinned_repositories()
        
        # 5. Pull Requests and Issues
        self.fetch_pull_requests()
        self.fetch_issues()
        
        # 6. Releases
        self.fetch_releases()
        
        # 7. Lines of Code Stats
        self.fetch_loc_stats()
        
        # 8. Recent Activity (Events)
        self.fetch_recent_activity()
        
        logger.info("Data Engine pipeline completed successfully.")

    def fetch_profile(self) -> dict[str, Any]:
        """Fetch base profile information using the authenticated endpoint."""
        logger.info("Fetching profile information...")
        # Use /user (authenticated) to get private repo counts
        profile = self.client.rest_request("GET", "/user")
        save_json(profile, PathManager.GENERATED_JSON_DIR / "profile.json")
        return profile

    def download_avatar(self, avatar_url: str) -> None:
        """Download the user's avatar."""
        self.client.download_avatar(avatar_url)

    def fetch_repositories(self) -> None:
        """Fetch all repositories for the user, including private ones if the token has access."""
        logger.info("Fetching repositories...")
        # Use /user/repos instead of /users/{username}/repos to get private repositories for the authenticated user
        repos = self.client.rest_request("GET", "/user/repos?type=owner&per_page=100", paginated=True)
        save_json(repos, PathManager.GENERATED_JSON_DIR / "repos.json")

    def fetch_contributions(self) -> None:
        """Fetch contribution graphs and statistics via GraphQL."""
        logger.info("Fetching contribution data...")
        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
              totalCommitContributions
              totalIssueContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              restrictedContributionsCount
            }
          }
        }
        """
        data = self.client.graphql_request(query, {"username": self.username})
        # Extract just the contributions collection
        contribs = data.get("user", {}).get("contributionsCollection", {})
        save_json(contribs, PathManager.GENERATED_JSON_DIR / "contributions.json")

    def fetch_pinned_repositories(self) -> None:
        """Fetch pinned repositories via GraphQL."""
        logger.info("Fetching pinned repositories...")
        query = """
        query($username: String!) {
          user(login: $username) {
            pinnedItems(first: 6, types: REPOSITORY) {
              nodes {
                ... on Repository {
                  name
                  description
                  url
                  stargazerCount
                  forkCount
                  primaryLanguage {
                    name
                    color
                  }
                }
              }
            }
          }
        }
        """
        data = self.client.graphql_request(query, {"username": self.username})
        pinned = data.get("user", {}).get("pinnedItems", {}).get("nodes", [])
        save_json(pinned, PathManager.GENERATED_JSON_DIR / "pinned_repos.json")

    def fetch_pull_requests(self) -> None:
        """Fetch user's pull requests and PRs made to user's repositories."""
        logger.info("Fetching pull request data...")
        all_prs = {}

        # 1. Fetch all PRs authored by the user via Search API
        prs_search = self.client.rest_request("GET", f"/search/issues?q=type:pr+author:{self.username}&per_page=100", paginated=True)
        if isinstance(prs_search, list):
            for page in prs_search:
                if isinstance(page, dict) and "items" in page:
                    for item in page.get("items", []):
                        all_prs[item.get("html_url")] = item
        elif isinstance(prs_search, dict) and "items" in prs_search:
            for item in prs_search.get("items", []):
                all_prs[item.get("html_url")] = item
                
        # 2. Fetch all PRs (including dependabot/others) for all user's repositories
        repos_file = PathManager.GENERATED_JSON_DIR / "repos.json"
        if repos_file.exists():
            import json
            with open(repos_file, "r", encoding="utf-8") as f:
                repos = json.load(f)
            for repo in repos:
                repo_name = repo.get("name")
                owner = repo.get("owner", {}).get("login")
                if owner and repo_name:
                    repo_prs = self.client.rest_request("GET", f"/repos/{owner}/{repo_name}/pulls?state=all&per_page=100", paginated=True)
                    if isinstance(repo_prs, list):
                        for pr in repo_prs:
                            if isinstance(pr, dict):
                                all_prs[pr.get("html_url")] = pr

        save_json(list(all_prs.values()), PathManager.GENERATED_JSON_DIR / "pull_requests.json")

    def fetch_issues(self) -> None:
        """Fetch user's issues."""
        logger.info("Fetching issue data...")
        issues = self.client.rest_request("GET", f"/search/issues?q=type:issue+author:{self.username}&per_page=100", paginated=True)
        
        if isinstance(issues, list) and len(issues) > 0 and isinstance(issues[0], dict) and "items" in issues[0]:
            all_items = []
            for page in issues:
                all_items.extend(page.get("items", []))
            save_json(all_items, PathManager.GENERATED_JSON_DIR / "issues.json")
        elif isinstance(issues, dict):
            save_json(issues.get("items", []), PathManager.GENERATED_JSON_DIR / "issues.json")
        else:
            save_json(issues, PathManager.GENERATED_JSON_DIR / "issues.json")

    def fetch_releases(self) -> None:
        """Fetch releases for user's repositories via GraphQL."""
        logger.info("Fetching release data...")
        query = """
        query($username: String!) {
          user(login: $username) {
            repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes {
                name
                releases(first: 10, orderBy: {field: CREATED_AT, direction: DESC}) {
                  nodes {
                    name
                    tagName
                    publishedAt
                    url
                  }
                }
              }
            }
          }
        }
        """
        data = self.client.graphql_request(query, {"username": self.username})
        repos = data.get("user", {}).get("repositories", {}).get("nodes", [])
        
        # Flatten releases
        all_releases = {}
        for repo in repos:
            repo_releases = repo.get("releases", {}).get("nodes", [])
            if repo_releases:
                all_releases[repo["name"]] = repo_releases
                
        save_json(all_releases, PathManager.GENERATED_JSON_DIR / "releases.json")

    def fetch_loc_stats(self) -> None:
        """Fetch contributor stats for LOC calculation."""
        logger.info("Fetching Lines of Code (LOC) statistics...")
        repos_file = PathManager.GENERATED_JSON_DIR / "repos.json"
        
        loc_stats = {}
        if repos_file.exists():
            import json
            with open(repos_file, "r", encoding="utf-8") as f:
                repos = json.load(f)
                
            for repo in repos:
                # Skip forks to avoid taking credit for huge copied codebases
                if repo.get("fork"): continue
                repo_name = repo.get("name")
                owner = repo.get("owner", {}).get("login")
                if not owner or not repo_name: continue
                
                # Fetch contributor stats
                endpoint = f"/repos/{owner}/{repo_name}/stats/contributors"
                try:
                    stats = self.client.rest_request("GET", endpoint, use_cache=True)
                    if isinstance(stats, list):
                        for contributor in stats:
                            author = contributor.get("author") or {}
                            if author.get("login") == self.username:
                                loc_stats[repo_name] = {
                                    "total_commits": contributor.get("total", 0),
                                    "weeks": contributor.get("weeks", [])
                                }
                                break
                except Exception as e:
                    logger.warning(f"Could not fetch LOC for {repo_name}: {e}")
                    
        save_json(loc_stats, PathManager.GENERATED_JSON_DIR / "loc_stats.json")

    def fetch_recent_activity(self) -> None:
        """Fetch recent events from the user."""
        logger.info("Fetching recent activity...")
        events = self.client.rest_request("GET", f"/users/{self.username}/events/public?per_page=100", paginated=True)
        # Limit to the most recent 100 events to prevent massive JSON files
        save_json(events[:100] if isinstance(events, list) else events, PathManager.GENERATED_JSON_DIR / "activity.json")

if __name__ == "__main__":
    from logger import setup_logger
    setup_logger(debug_mode=True)
    engine = DataEngine()
    engine.run_all()
