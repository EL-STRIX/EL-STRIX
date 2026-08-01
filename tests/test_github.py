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


@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_github_rest_request_external_url_security_violation(mock_token):
    """Test REST API correctly blocks requests to external domains to prevent token leakage."""
    client = GitHubClient()

    with pytest.raises(GitHubAPIError) as exc:
        client.rest_request("GET", "https://external-domain.com/api/data", use_cache=False)

    assert "Security violation" in str(exc.value)
    assert "Attempted to send GitHub API token to external host" in str(exc.value)


@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_download_avatar_valid_url(mock_token, mocker):
    """Test avatar download with a valid GitHub avatar URL."""
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b"image_data"]

    mocker.patch("requests.get", return_value=mock_response)
    mocker.patch("github.ensure_dir")
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("github.PathManager.ASSET_IMAGE_DIR", MagicMock(return_value="fake_dir"))

    # Should not raise any error
    client.download_avatar("https://avatars.githubusercontent.com/u/12345")


@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_download_avatar_invalid_scheme(mock_token):
    """Test avatar download rejects non-HTTPS URLs."""
    client = GitHubClient()

    with pytest.raises(GitHubAPIError) as exc:
        client.download_avatar("http://avatars.githubusercontent.com/u/12345")

    assert "Security violation: Avatar URL must use HTTPS." in str(exc.value)


@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_download_avatar_external_domain(mock_token):
    """Test avatar download rejects external domains to prevent SSRF."""
    client = GitHubClient()

    with pytest.raises(GitHubAPIError) as exc:
        client.download_avatar("https://attacker.com/avatar.png")

    assert "Security violation: Attempted to download avatar from external host" in str(exc.value)


@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_download_avatar_bypass_suffix(mock_token):
    """Test avatar download rejects suffix bypass attempts for SSRF."""
    client = GitHubClient()

    with pytest.raises(GitHubAPIError) as exc:
        client.download_avatar("https://avatars.githubusercontent.com.attacker.com/avatar.png")

    assert "Security violation: Attempted to download avatar from external host" in str(exc.value)

@patch("github.EnvManager.get_github_token", return_value="fake_token")
def test_github_rest_request_external_url_security_violation_bypass(mock_token):
    """Test REST API correctly blocks requests to domains constructed to bypass startswith checks."""
    client = GitHubClient()

    with pytest.raises(GitHubAPIError) as exc:
        client.rest_request("GET", "https://api.github.com.attacker.com/api/data", use_cache=False)

    assert "Security violation" in str(exc.value)
    assert "Attempted to send GitHub API token to external host" in str(exc.value)


