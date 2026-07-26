"""Unit tests for generator module."""

import sys
import os
import pytest

# Ensure scripts module path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from generator import ProfileGenerator  # noqa: E402


def test_profile_generator_data():
    generator = ProfileGenerator(username="test-user")
    mock_profile = {
        "name": "Test User",
        "bio": "Developer",
        "public_repos": 10,
        "followers": 5,
        "following": 2,
    }
    mock_repos = [
        {"stargazers_count": 15, "forks_count": 3},
        {"stargazers_count": 5, "forks_count": 1},
    ]

    data = generator.generate_data(mock_profile, mock_repos)

    assert data["username"] == "test-user"
    assert data["total_stars"] == 20
    assert data["total_forks"] == 4
    assert data["public_repos"] == 10
