"""Unit tests for Automation Engine."""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from exceptions import ELSTRIXError
from automation import AutomationEngine

@patch("automation.subprocess.run")
def test_run_git_success(mock_run):
    """Test successful git command execution."""
    mock_result = MagicMock()
    mock_result.stdout = "success\n"
    mock_run.return_value = mock_result

    engine = AutomationEngine()
    success, output = engine._run_git(["status"])

    assert success is True
    assert output == "success"
    mock_run.assert_called_once_with(
        ["git", "status"],
        cwd=engine.cwd,
        capture_output=True,
        text=True,
        check=True,
    )

@patch("automation.subprocess.run")
def test_run_git_called_process_error(mock_run):
    """Test git command raising CalledProcessError."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "status"],
        stderr="error\n"
    )

    engine = AutomationEngine()
    success, output = engine._run_git(["status"])

    assert success is False
    assert output == "error"
    mock_run.assert_called_once_with(
        ["git", "status"],
        cwd=engine.cwd,
        capture_output=True,
        text=True,
        check=True,
    )

@patch("automation.subprocess.run")
def test_run_git_file_not_found_error(mock_run):
    """Test git command raising FileNotFoundError."""
    mock_run.side_effect = FileNotFoundError()

    engine = AutomationEngine()

    with pytest.raises(ELSTRIXError) as exc_info:
        engine._run_git(["status"])

    assert str(exc_info.value) == "Git is not installed or not found in system path."
    mock_run.assert_called_once_with(
        ["git", "status"],
        cwd=engine.cwd,
        capture_output=True,
        text=True,
        check=True,
    )
