"""Unit tests for Statistics Engine."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from stats import StatisticsEngine


@pytest.fixture
def mock_engine(mocker):
    mocker.patch("stats.load_json", side_effect=[
        {"public_repos": 10, "followers": 50, "created_at": "2020-01-01T00:00:00Z"},
        [
            {"name": "repo1", "stargazers_count": 100, "forks_count": 20, "private": False, "size": 1024, "language": "Python"},
            {"name": "repo2", "stargazers_count": 50, "forks_count": 10, "fork": True, "size": 512, "language": "Python"},
            {"name": "repo3", "stargazers_count": 10, "forks_count": 2, "private": True, "size": 2048, "language": "JavaScript"}
        ],
        {"totalCommitContributions": 500, "totalIssueContributions": 50, "contributionCalendar": {"totalContributions": 1000}},
        {"repo1": {"total_lines": 1024}},
        [{"state": "open", "merged_at": None}, {"state": "closed", "pull_request": {"merged_at": None}}],
        {}, # releases.json
        []  # issues.json
    ])
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
    assert stats["total_stars"] == 110 # repo1 (100) + repo3 (10)
    assert stats["most_starred_repository"] == "repo1"

def test_calculate_language_stats(mock_engine):
    stats = mock_engine._calculate_language_stats()
    assert stats["languages_used"] == 2
    assert stats["most_used_language"] == "JavaScript" # repo3 (2048 * 1024) > repo1 (1024 * 1024)

