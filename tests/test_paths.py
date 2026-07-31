import pytest
from unittest.mock import call

from scripts.paths import PathManager


def test_ensure_directories_success(mocker):
    """Test that all required directories are created successfully."""
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")

    PathManager.ensure_directories()

    # Verify mkdir was called for each directory with correct arguments
    expected_dirs_count = 11
    assert mock_mkdir.call_count == expected_dirs_count
    mock_mkdir.assert_has_calls([
        call(parents=True, exist_ok=True) for _ in range(expected_dirs_count)
    ])


def test_ensure_directories_failure(mocker):
    """Test that an OSError during directory creation raises a PathError."""
    mocker.patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied"))

    with pytest.raises(Exception) as exc_info:
        PathManager.ensure_directories()

    assert exc_info.type.__name__ == "PathError"
    assert "Failed to create directories: Permission denied" in str(exc_info.value)


def test_get_config_file():
    """Test that get_config_file returns the correct absolute path."""
    filename = "test.json"
    config_file = PathManager.get_config_file(filename)

    assert config_file == PathManager.CONFIG_DIR / filename
