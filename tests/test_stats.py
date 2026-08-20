"""Unit tests for Statistics Engine."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from stats import StatisticsEngine


@pytest.fixture
def mock_engine(mocker):
    mocker.patch(
        "stats.load_json",
        side_effect=[
            {"public_repos": 10, "followers": 50, "created_at": "2020-01-01T00:00:00Z", "timezone": "UTC"},
            [
                {
                    "name": "repo1",
                    "stargazers_count": 100,
                    "forks_count": 20,
                    "private": False,
                    "size": 1024,
                    "language": "Python",
                },
                {
                    "name": "repo2",
                    "stargazers_count": 50,
                    "forks_count": 10,
                    "fork": True,
                    "size": 512,
                    "language": "Python",
                },
                {
                    "name": "repo3",
                    "stargazers_count": 10,
                    "forks_count": 2,
                    "private": True,
                    "size": 2048,
                    "language": "JavaScript",
                },
            ],
            {
                "totalCommitContributions": 500,
                "totalIssueContributions": 50,
                "contributionCalendar": {"totalContributions": 1000},
            },
            {"repo1": {"total_lines": 1024}},
            [
                {"state": "open", "merged_at": None},
                {"state": "closed", "pull_request": {"merged_at": None}},
            ],
            {},  # releases.json
            [],  # issues.json
        ],
    )
    return StatisticsEngine()


def test_calculate_profile_stats(mock_engine):
    stats = mock_engine._calculate_profile_stats()
    assert stats["total_public_repositories"] == 10
    assert stats["total_followers"] == 50
    assert stats["profile_creation_date"] == "2020-01-01T00:00:00Z"
    assert stats["days_since_account_creation"] > 0


def test_calculate_repo_stats(mock_engine):
    stats = mock_engine._calculate_repo_stats()
    assert stats["repository_count"] == 3
    assert stats["public_repository_count"] == 2
    assert stats["private_repository_count"] == 1
    assert stats["forked_repository_count"] == 1
    assert stats["original_repository_count"] == 2


def test_calculate_star_stats(mock_engine):
    stats = mock_engine._calculate_star_stats()
    # Should exclude forks
    assert stats["total_stars"] == 110  # repo1 (100) + repo3 (10)
    assert stats["most_starred_repository"] == "repo1"


def test_calculate_language_stats(mock_engine):
    stats = mock_engine._calculate_language_stats()
    assert stats["languages_used"] == 2
    assert stats["most_used_language"] == "JavaScript"  # repo3 (2048 * 1024) > repo1 (1024 * 1024)


def test_calculate_contribution_stats_active_today(mock_engine):
    from datetime import UTC, datetime, timedelta

    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)

    mock_engine.contrib_data = {
        "totalCommitContributions": 10,
        "restrictedContributionsCount": 2,
        "contributionCalendar": {
            "totalContributions": 8,
            "weeks": [
                {
                    "contributionDays": [
                        {"date": day_before.strftime("%Y-%m-%d"), "contributionCount": 3},
                        {"date": yesterday.strftime("%Y-%m-%d"), "contributionCount": 2},
                        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 1},
                    ]
                }
            ],
        },
    }

    stats = mock_engine._calculate_contribution_stats()
    assert stats["current_streak"] == 3
    assert stats["longest_streak"] == 3
    assert stats["max_daily_contributions"] == 3
    assert stats["total_contributions"] == 8


def test_calculate_contribution_stats_active_yesterday(mock_engine):
    from datetime import UTC, datetime, timedelta

    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    gap_day = today - timedelta(days=3)

    mock_engine.contrib_data = {
        "totalCommitContributions": 5,
        "restrictedContributionsCount": 0,
        "contributionCalendar": {
            "weeks": [
                {
                    "contributionDays": [
                        {"date": gap_day.strftime("%Y-%m-%d"), "contributionCount": 0},
                        {"date": day_before.strftime("%Y-%m-%d"), "contributionCount": 4},
                        {"date": yesterday.strftime("%Y-%m-%d"), "contributionCount": 1},
                        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 0},
                    ]
                }
            ]
        },
    }

    stats = mock_engine._calculate_contribution_stats()
    # Streak should be 2 because yesterday and day_before had contributions, even if today is 0 so far
    assert stats["current_streak"] == 2
    assert stats["longest_streak"] == 2


def test_calculate_contribution_stats_broken_streak(mock_engine):
    from datetime import UTC, datetime, timedelta

    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)

    mock_engine.contrib_data = {
        "totalCommitContributions": 5,
        "restrictedContributionsCount": 0,
        "contributionCalendar": {
            "weeks": [
                {
                    "contributionDays": [
                        {"date": day_before.strftime("%Y-%m-%d"), "contributionCount": 5},
                        {"date": yesterday.strftime("%Y-%m-%d"), "contributionCount": 0},
                        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 0},
                    ]
                }
            ]
        },
    }

    stats = mock_engine._calculate_contribution_stats()
    assert stats["current_streak"] == 0
    assert stats["longest_streak"] == 1


def test_calculate_commit_stats_timeline(mock_engine):
    from datetime import UTC, datetime, timedelta

    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)

    mock_engine.contrib_data = {
        "totalCommitContributions": 100,
        "restrictedContributionsCount": 0,
        "contributionCalendar": {
            "weeks": [
                {
                    "contributionDays": [
                        {"date": yesterday.strftime("%Y-%m-%d"), "contributionCount": 5},
                        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 3},
                    ]
                }
            ]
        },
    }
    mock_engine.loc_data = {"repo1": {"total_commits": 50}}

    stats = mock_engine._calculate_commit_stats()
    assert stats["total_commits"] == 100
    assert stats["recent_commits"] == 8
    assert len(stats["commit_timeline"]) == 31  # 30 days ago to today inclusive
    assert stats["commits_per_repository"] == {"repo1": 50}


def test_calculate_contribution_stats_forward_active_date(mock_engine):
    from datetime import UTC, datetime, timedelta

    today = datetime.now(UTC).date()
    tomorrow = today + timedelta(days=1)

    mock_engine.contrib_data = {
        "totalCommitContributions": 10,
        "restrictedContributionsCount": 0,
        "contributionCalendar": {
            "weeks": [
                {
                    "contributionDays": [
                        {"date": today.strftime("%Y-%m-%d"), "contributionCount": 2},
                        {"date": tomorrow.strftime("%Y-%m-%d"), "contributionCount": 1},
                    ]
                }
            ]
        },
    }

    stats = mock_engine._calculate_contribution_stats()
    assert stats["current_streak"] == 2
    assert stats["longest_streak"] == 2


def test_calculate_contribution_stats_year_boundary(mock_engine):
    mock_engine.contrib_data = {
        "totalCommitContributions": 4,
        "restrictedContributionsCount": 0,
        "contributionCalendar": {
            "weeks": [
                {
                    "contributionDays": [
                        {"date": "2025-12-30", "contributionCount": 1},
                        {"date": "2025-12-31", "contributionCount": 1},
                        {"date": "2026-01-01", "contributionCount": 1},
                        {"date": "2026-01-02", "contributionCount": 1},
                    ]
                }
            ]
        },
    }

    stats = mock_engine._calculate_contribution_stats()
    assert stats["longest_streak"] == 4


def test_calculate_trends_deduplication(mock_engine):
    mock_engine.repos_data = [
        {"created_at": "2024-05-01T00:00:00Z"},
        {"created_at": "2024-08-01T00:00:00Z"},
        {"created_at": "2025-01-01T00:00:00Z"},
    ]
    mock_engine.contrib_data = {
        "contributionCalendar": {
            "weeks": [
                {"contributionDays": [{"date": "2025-01-01", "contributionCount": 2}]},
                {"contributionDays": [{"date": "2025-01-01", "contributionCount": 2}]},  # Duplicate week
                {"contributionDays": [{"date": "2025-01-08", "contributionCount": 4}]},
            ]
        }
    }

    trends = mock_engine._calculate_trends()
    assert len(trends["repository_growth"]) == 2  # 2024 (2), 2025 (1)
    assert trends["repository_growth"][0] == {"year": "2024", "count": 2}
    assert trends["repository_growth"][1] == {"year": "2025", "count": 1}
    assert len(trends["commit_trend"]) == 2  # Deduplicated to 2 weeks


def test_get_user_timezone(mock_engine, monkeypatch):
    from datetime import timezone

    mock_engine.profile_data = {"timezone": "UTC"}
    tz = mock_engine._get_user_timezone()
    assert tz == timezone.utc

    mock_engine.profile_data = {}
    monkeypatch.delenv("TZ", raising=False)
    tz_default = mock_engine._get_user_timezone()
    assert tz_default is not None



