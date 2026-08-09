"""Unit tests for GitHub API Client."""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from github import GitHubClient
from exceptions import GitHubAPIError

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
@patch("requests.get")
def test_download_avatar_size_limit(mock_get, mock_token, tmp_path, mocker):
    """Test downloading an avatar that exceeds the maximum size limit."""
    mocker.patch("github.PathManager.ASSET_IMAGE_DIR", tmp_path)
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.status_code = 200

    # Generate chunks that together exceed 5MB
    # 5MB + 1 byte in 1MB chunks
    def chunk_generator(*args, **kwargs):
        for _ in range(6):
            yield b"0" * (1024 * 1024)

    mock_response.iter_content = chunk_generator
    mock_get.return_value = mock_response

    with pytest.raises(GitHubAPIError) as exc:
        client.download_avatar("http://fake.url/avatar.png")

    assert "exceeds maximum allowed size" in str(exc.value)


@patch("github.EnvManager.get_github_token", return_value="fake_token")
@patch("requests.get")
def test_download_avatar_success(mock_get, mock_token, tmp_path, mocker):
    """Test successfully downloading an avatar within the size limit."""
    mocker.patch("github.PathManager.ASSET_IMAGE_DIR", tmp_path)
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.status_code = 200

    # Generate chunk under the 5MB limit
    def chunk_generator(*args, **kwargs):
        yield b"1" * 1024

    mock_response.iter_content = chunk_generator
    mock_get.return_value = mock_response

    save_path = client.download_avatar("http://fake.url/avatar.png")

    assert save_path == tmp_path / "avatar.png"
    assert save_path.exists()
    assert save_path.read_bytes() == b"1" * 1024


