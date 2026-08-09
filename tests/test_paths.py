import os
import sys

import pytest

# Add scripts directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from exceptions import PathError
from paths import PathManager


def test_ensure_directories_os_error(mocker) -> None:
    """Test that PathManager.ensure_directories raises PathError on OSError."""
    # Mock Path.mkdir to raise an OSError
    mocker.patch('paths.Path.mkdir', side_effect=OSError("Permission denied"))

    with pytest.raises(PathError) as exc_info:
        PathManager.ensure_directories()

    assert "Failed to create directories:" in str(exc_info.value)
