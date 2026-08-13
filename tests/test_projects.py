"""Unit tests for featured projects selection."""

import os
import sys

import pytest

# Add scripts directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from projects import select_featured


@pytest.fixture
def sample_repos():
    """Fixture providing a sample list of repositories."""
    return [
        {"name": "repo1", "stargazers_count": 100, "fork": False},
        {"name": "repo2", "stargazers_count": 50, "fork": True},
        {"name": "repo3", "stargazers_count": 200, "fork": False},
        {"name": "repo4", "stargazers_count": 10, "fork": False},
        {"name": "repo5", "stargazers_count": 300, "fork": True},
    ]


@pytest.fixture
def mock_logger(mocker):
    """Fixture to mock logger.info."""
    return mocker.patch("projects.logger.info")


def test_select_featured_no_pinned(sample_repos, mock_logger):
    """Test selection without pinned repos (excludes forks, sorts by stars)."""
    result = select_featured(sample_repos)

    # Should exclude forks (repo2, repo5)
    assert len(result) == 3
    # Should be sorted by stars descending
    assert result[0]["name"] == "repo3"  # 200 stars
    assert result[1]["name"] == "repo1"  # 100 stars
    assert result[2]["name"] == "repo4"  # 10 stars
    mock_logger.assert_called_once()


def test_select_featured_with_pinned(sample_repos, mock_logger):
    """Test selection with pinned repos (case-insensitive, includes forks)."""
    # Pin repo2 (a fork) and Repo4 (testing case-insensitivity)
    result = select_featured(sample_repos, pinned=["repo2", "Repo4"])

    assert len(result) == 4
    # Pinned repos should come first
    assert result[0]["name"] in ["repo2", "repo4"]
    assert result[1]["name"] in ["repo2", "repo4"]

    # The remaining should be non-forks, sorted by stars descending
    assert result[2]["name"] == "repo3"  # 200 stars
    assert result[3]["name"] == "repo1"  # 100 stars
    mock_logger.assert_called_once()


def test_select_featured_max_count(sample_repos, mock_logger):
    """Test that max_count limits the returned list."""
    result = select_featured(sample_repos, max_count=2)

    assert len(result) == 2
    assert result[0]["name"] == "repo3"
    assert result[1]["name"] == "repo1"
    mock_logger.assert_called_once()


def test_select_featured_empty_repos(mock_logger):
    """Test behavior with an empty list of repositories."""
    result = select_featured([])

    assert result == []
    mock_logger.assert_called_once_with("Selected 0 featured repositories.")
