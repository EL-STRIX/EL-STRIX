"""Unit tests for GitHub API Client."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from exceptions import GitHubAPIError
from github import GitHubClient


@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_github_client_init(mock_token):
    """Test client initialization and headers."""
    client = GitHubClient()
    assert client.headers["Authorization"] == "token fake_token"
    assert client.headers["Accept"] == "application/vnd.github.v3+json"
    assert client.headers["User-Agent"] == "EL-STRIX-Profile-Engine"

@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_github_rest_request_success(mock_token, mocker):
    """Test a successful REST API request."""
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "test_user"}
    
    mocker.patch("requests.Session.request", return_value=mock_response)
    
    data = client.rest_request("GET", "/user", use_cache=False)
    assert data["login"] == "test_user"

@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_github_rest_request_failure(mock_token, mocker):
    """Test REST API failure handling."""
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Rate limited"
    
    import requests
    mock_response.raise_for_status.side_effect = requests.HTTPError("403 Client Error")
    
    mocker.patch("requests.Session.request", return_value=mock_response)
    mocker.patch("time.sleep") # avoid actual sleeping in tests
    
    with pytest.raises(GitHubAPIError) as exc:
        client.rest_request("GET", "/user", use_cache=False)
    
    assert "403" in str(exc.value)




