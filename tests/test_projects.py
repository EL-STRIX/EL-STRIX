"""Unit tests for Featured projects selection module."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from projects import select_featured


def test_select_featured_basic_sorting():
    repos = [
        {"name": "repo1", "stargazers_count": 10, "fork": False},
        {"name": "repo2", "stargazers_count": 50, "fork": False},
        {"name": "repo3", "stargazers_count": 5, "fork": False},
        {"name": "repo4", "stargazers_count": 100, "fork": True}, # Should be excluded
    ]
    featured = select_featured(repos)

    assert len(featured) == 3
    assert featured[0]["name"] == "repo2"
    assert featured[1]["name"] == "repo1"
    assert featured[2]["name"] == "repo3"


def test_select_featured_max_count():
    repos = [
        {"name": f"repo{i}", "stargazers_count": i, "fork": False} for i in range(10)
    ]
    featured = select_featured(repos, max_count=3)

    assert len(featured) == 3
    assert featured[0]["name"] == "repo9"
    assert featured[1]["name"] == "repo8"
    assert featured[2]["name"] == "repo7"


def test_select_featured_empty():
    repos = []
    featured = select_featured(repos)

    assert len(featured) == 0


def test_select_featured_pinned():
    repos = [
        {"name": "repo1", "stargazers_count": 100, "fork": False},
        {"name": "repo2", "stargazers_count": 10, "fork": False},
        {"name": "repo3", "stargazers_count": 5, "fork": False},
    ]
    pinned = ["repo3", "repo2"]
    featured = select_featured(repos, pinned=pinned)

    assert len(featured) == 3
    # Pinned repos should be first, order within pinned depends on original repo order
    assert featured[0]["name"] == "repo2"
    assert featured[1]["name"] == "repo3"
    assert featured[2]["name"] == "repo1"


def test_select_featured_pinned_case_insensitivity():
    repos = [
        {"name": "RepoOne", "stargazers_count": 10, "fork": False},
        {"name": "repotwo", "stargazers_count": 5, "fork": False},
    ]
    pinned = ["repoONE", "REPOTWO"]
    featured = select_featured(repos, pinned=pinned)

    assert len(featured) == 2
    assert featured[0]["name"] == "RepoOne"
    assert featured[1]["name"] == "repotwo"


def test_select_featured_pinned_forks():
    repos = [
        {"name": "repo1", "stargazers_count": 10, "fork": True},
        {"name": "repo2", "stargazers_count": 50, "fork": True},
        {"name": "repo3", "stargazers_count": 5, "fork": False},
    ]
    pinned = ["repo1"]
    featured = select_featured(repos, pinned=pinned)

    assert len(featured) == 2
    assert featured[0]["name"] == "repo1" # Pinned fork included
    assert featured[1]["name"] == "repo3" # Unpinned non-fork included
    # repo2 is excluded because it's an unpinned fork
