"""Centralized Data Engine for fetching and storing GitHub data."""

from typing import Any

from env import EnvManager
from github import GitHubClient
from logger import logger
from paths import PathManager
from utils.json_helpers import load_json, save_json


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
        """Fetch base profile information."""
        logger.info("Fetching profile information...")
        # Try /user first for private repo counts
        profile = self.client.rest_request("GET", "/user")

        # If the token belongs to a bot (e.g. GitHub Actions default token) or another user,
        # fallback to the target username's public profile to avoid breaking all stats.
        if profile.get("login") != self.username:
            logger.info(
                f"Authenticated as {profile.get('login')}, falling back to public profile for {self.username}"
            )
            profile = self.client.rest_request("GET", f"/users/{self.username}")

        save_json(profile, PathManager.GENERATED_JSON_DIR / "profile.json")
        return profile

    def download_avatar(self, avatar_url: str) -> None:
        """Download the user's avatar."""
        import os
        avatar_path = PathManager.ASSET_IMAGE_DIR / "avatar.png"
        if os.environ.get("GITHUB_ACTIONS") != "true" and avatar_path.exists():
            logger.info("Avatar already exists locally. Skipping download.")
            return
        self.client.download_avatar(avatar_url)

    def fetch_repositories(self) -> None:
        """Fetch all repositories for the user, including private ones if the token has access."""
        logger.info("Fetching repositories...")
        # Check authentication identity
        auth_user = self.client.rest_request("GET", "/user")
        if auth_user.get("login") == self.username:
            endpoint = "/user/repos?type=owner&per_page=100"
        else:
            logger.info(
                f"Token does not belong to {self.username}, fetching public repositories only."
            )
            endpoint = f"/users/{self.username}/repos?type=owner&per_page=100"

        repos = self.client.rest_request("GET", endpoint, paginated=True)
        save_json(repos, PathManager.GENERATED_JSON_DIR / "repos.json")

    def fetch_contributions(self) -> None:
        """Fetch all-time contribution graphs and statistics via GraphQL."""
        logger.info("Fetching all-time contribution data...")

        # Load profile to get account creation date
        profile_file = PathManager.GENERATED_JSON_DIR / "profile.json"
        created_at_str = None
        if profile_file.exists():
            profile_data = load_json(profile_file)
            if isinstance(profile_data, dict):
                created_at_str = profile_data.get("created_at")

        from datetime import UTC, datetime, timedelta

        if not created_at_str:
            created_at_str = datetime.now(UTC).isoformat()

        try:
            created_date = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except ValueError:
            created_date = datetime.now(UTC)

        current_year = datetime.now(UTC).year
        start_year = created_date.year

        unified_contribs: dict[str, Any] = {
            "contributionCalendar": {"totalContributions": 0, "weeks": []},
            "totalCommitContributions": 0,
            "totalIssueContributions": 0,
            "totalPullRequestContributions": 0,
            "totalPullRequestReviewContributions": 0,
            "restrictedContributionsCount": 0,
        }

        # We calculate the true 'today' dynamically in stats.py to account for timezone differences
        # between the local system and GitHub's servers, so we just set a baseline UTC date here.
        from datetime import UTC

        unified_contribs["github_today"] = datetime.now(UTC).strftime("%Y-%m-%d")

        for year in range(start_year, current_year + 1):
            # Calculate GitHub UI week bounds (Sunday to Saturday) to match the yearly totals exactly
            start_date = datetime(year, 1, 1)
            start_date = start_date - timedelta(days=(start_date.weekday() + 1) % 7)

            end_date = datetime(year, 12, 31)
            end_date = end_date + timedelta(days=(5 - end_date.weekday()) % 7)

            from_date = start_date.strftime("%Y-%m-%dT00:00:00Z")
            to_date = end_date.strftime("%Y-%m-%dT23:59:59Z")

            query = """
            query($username: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $username) {
                contributionsCollection(from: $from, to: $to) {
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
            try:
                data = self.client.graphql_request(
                    query, {"username": self.username, "from": from_date, "to": to_date}
                )
                contribs = data.get("user", {}).get("contributionsCollection", {})

                cal = contribs.get("contributionCalendar", {})
                unified_contribs["contributionCalendar"]["totalContributions"] += cal.get(
                    "totalContributions", 0
                )
                unified_contribs["contributionCalendar"]["weeks"].extend(cal.get("weeks", []))

                unified_contribs["totalCommitContributions"] += contribs.get(
                    "totalCommitContributions", 0
                )
                unified_contribs["totalIssueContributions"] += contribs.get(
                    "totalIssueContributions", 0
                )
                unified_contribs["totalPullRequestContributions"] += contribs.get(
                    "totalPullRequestContributions", 0
                )
                unified_contribs["totalPullRequestReviewContributions"] += contribs.get(
                    "totalPullRequestReviewContributions", 0
                )
                unified_contribs["restrictedContributionsCount"] += contribs.get(
                    "restrictedContributionsCount", 0
                )
            except Exception as e:
                logger.error(f"Failed to fetch contributions for year {year}: {e}")

        # Sort weeks to ensure streak calculations are correct across year boundaries
        weeks = unified_contribs["contributionCalendar"]["weeks"]
        weeks.sort(key=lambda w: w.get("contributionDays", [{"date": ""}])[0].get("date", ""))

        save_json(unified_contribs, PathManager.GENERATED_JSON_DIR / "contributions.json")

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

        # 1. Fetch all PRs authored by the user via Search API (sort by updated to get most recent if hitting 1000 limit)
        prs_search = self.client.rest_request(
            "GET",
            f"/search/issues?q=type:pr+author:{self.username}&sort=updated&order=desc&per_page=100",
            paginated=True,
        )
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
            repos = load_json(repos_file)
            if not isinstance(repos, list):
                repos = []

            endpoints = []
            for repo in repos:
                repo_name = repo.get("name")
                owner = repo.get("owner", {}).get("login")
                if owner and repo_name:
                    endpoints.append(f"/repos/{owner}/{repo_name}/pulls?state=all&per_page=100")

            if endpoints:
                batch_results = self.client.batch_rest_requests(
                    "GET", endpoints, max_workers=15, paginated=True
                )
                for endpoint, repo_prs in batch_results.items():
                    if isinstance(repo_prs, list):
                        for pr in repo_prs:
                            if isinstance(pr, dict):
                                all_prs[pr.get("html_url")] = pr

        save_json(list(all_prs.values()), PathManager.GENERATED_JSON_DIR / "pull_requests.json")

    def fetch_issues(self) -> None:
        """Fetch user's issues."""
        logger.info("Fetching issue data...")
        issues = self.client.rest_request(
            "GET",
            f"/search/issues?q=type:issue+author:{self.username}&sort=updated&order=desc&per_page=100",
            paginated=True,
        )

        if (
            isinstance(issues, list)
            and len(issues) > 0
            and isinstance(issues[0], dict)
            and "items" in issues[0]
        ):
            all_items = []
            for page in issues:
                all_items.extend(page.get("items", []))
            save_json(all_items, PathManager.GENERATED_JSON_DIR / "issues.json")
        elif isinstance(issues, dict):
            save_json(issues.get("items", []), PathManager.GENERATED_JSON_DIR / "issues.json")
        else:
            save_json(issues, PathManager.GENERATED_JSON_DIR / "issues.json")

    def fetch_releases(self) -> None:
        """Fetch releases for user's repositories via GraphQL with pagination."""
        logger.info("Fetching release data...")
        query = """
        query($username: String!, $cursor: String) {
          user(login: $username) {
            repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                name
                releases(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
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
        all_releases = {}
        has_next_page = True
        cursor = None

        while has_next_page:
            variables = {"username": self.username}
            if cursor:
                variables["cursor"] = cursor

            data = self.client.graphql_request(query, variables)
            repos_data = data.get("user", {}).get("repositories", {})
            repos = repos_data.get("nodes", [])

            for repo in repos:
                repo_releases = repo.get("releases", {}).get("nodes", [])
                if repo_releases:
                    # If this repo was fetched in a previous page, extend it, though they should be distinct repos
                    if repo["name"] not in all_releases:
                        all_releases[repo["name"]] = []
                    all_releases[repo["name"]].extend(repo_releases)

            page_info = repos_data.get("pageInfo", {})
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")

        save_json(all_releases, PathManager.GENERATED_JSON_DIR / "releases.json")

    def _process_contributor_stats(self, stats: list) -> dict | None:
        """Extract the current user's LOC stats from contributor stats."""
        for contributor in stats:
            author = contributor.get("author") or {}
            if author.get("login") == self.username:
                weeks = contributor.get("weeks", [])
                total_lines = sum(w.get("a", 0) for w in weeks)
                return {
                    "total_commits": contributor.get("total", 0),
                    "total_lines": total_lines,
                    "weeks": weeks,
                }
        return None

    def fetch_loc_stats(self) -> None:
        """Fetch contributor stats for LOC calculation."""
        logger.info("Fetching Lines of Code (LOC) statistics...")
        repos_file = PathManager.GENERATED_JSON_DIR / "repos.json"

        loc_stats = {}
        if not repos_file.exists():
            save_json(loc_stats, PathManager.GENERATED_JSON_DIR / "loc_stats.json")
            return

        repos = load_json(repos_file)
        if not isinstance(repos, list):
            repos = []

        endpoints = {}
        for repo in repos:
            # Skip forks to avoid taking credit for huge copied codebases
            if repo.get("fork"):
                continue
            repo_name = repo.get("name")
            owner = repo.get("owner", {}).get("login")
            if owner and repo_name:
                endpoints[f"/repos/{owner}/{repo_name}/stats/contributors"] = repo_name

        if not endpoints:
            save_json(loc_stats, PathManager.GENERATED_JSON_DIR / "loc_stats.json")
            return

        batch_results = self.client.batch_rest_requests(
            "GET", list(endpoints.keys()), max_workers=15, use_cache=True
        )

        for endpoint, stats in batch_results.items():
            if not stats or not isinstance(stats, list):
                continue

            repo_name = endpoints[endpoint]
            user_stats = self._process_contributor_stats(stats)
            if user_stats:
                loc_stats[repo_name] = user_stats

        save_json(loc_stats, PathManager.GENERATED_JSON_DIR / "loc_stats.json")

    def fetch_recent_activity(self) -> None:
        """Fetch recent events from the user."""
        logger.info("Fetching recent activity...")
        events = self.client.rest_request(
            "GET", f"/users/{self.username}/events/public?per_page=100", paginated=True
        )
        # Limit to the most recent 100 events to prevent massive JSON files
        save_json(
            events[:100] if isinstance(events, list) else events,
            PathManager.GENERATED_JSON_DIR / "activity.json",
        )


if __name__ == "__main__":
    from logger import setup_logger

    setup_logger(debug_mode=True)
    engine = DataEngine()
    engine.run_all()
