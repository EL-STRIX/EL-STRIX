"""README updater – commits generated README changes back to the repository."""

import os
import subprocess
from typing import Optional

from logger import logger
from config import ROOT_DIR


def commit_and_push(
    filepath: str = "README.md",
    commit_message: str = "docs: auto-update profile README",
    branch: str = "main",
) -> bool:
    """Stage, commit, and push changes to the remote repository.

    This function is intended to run inside a GitHub Actions environment
    where ``GITHUB_TOKEN`` is available and the repo is already cloned.

    Args:
        filepath: Relative path to the file to commit.
        commit_message: Conventional commit message.
        branch: Branch to push to.

    Returns:
        ``True`` if the push succeeded, ``False`` otherwise.
    """
    cwd = str(ROOT_DIR)

    try:
        # Configure git identity for CI
        _run_git(["config", "user.name", "EL-STRIX Bot"], cwd)
        _run_git(["config", "user.email", "el-strix-bot@users.noreply.github.com"], cwd)

        # Check for actual changes
        result = _run_git(["diff", "--name-only", filepath], cwd)
        if not result.strip():
            logger.info("No changes detected – skipping commit.")
            return True

        _run_git(["add", filepath], cwd)
        _run_git(["commit", "-m", commit_message], cwd)
        _run_git(["push", "origin", branch], cwd)

        logger.info(f"Pushed updated {filepath} to origin/{branch}.")
        return True

    except subprocess.CalledProcessError as exc:
        logger.error(f"Git operation failed: {exc}")
        return False


def _run_git(args: list, cwd: str) -> str:
    """Execute a git command and return its stdout.

    Args:
        args: Git sub-command and arguments (without the leading ``git``).
        cwd: Working directory.

    Returns:
        Captured stdout as a string.

    Raises:
        subprocess.CalledProcessError: If the command exits with a non-zero code.
    """
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
