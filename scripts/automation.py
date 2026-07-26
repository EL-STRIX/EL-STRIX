"""Automation Engine for Git Operations and Change Detection."""

import os
import subprocess
from datetime import datetime, timezone
from typing import List, Tuple

from logger import logger
from paths import PathManager
from exceptions import ELSTRIXError

class AutomationEngine:
    """Handles git operations, change detection, and automated commits."""

    def __init__(self, branch: str = "main"):
        self.cwd = str(PathManager.ROOT_DIR)
        self.branch = branch
        self.files_to_track = [
            "README.md",
            "assets/svg/light.svg",
            "assets/svg/dark.svg",
            "assets/ascii/matrix.json",
            "generated/json/profile.json",
            "generated/json/repos.json",
            "generated/json/contributions.json",
            "generated/stats/processed_statistics.json",
            "generated/avatar/avatar.png"
        ]

    def _run_git(self, args: List[str]) -> Tuple[bool, str]:
        """Execute a git command and return its success status and stdout."""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=True,
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # We don't want to log error here for things like git diff which might return non-zero
            # Actually git diff returns 0 if no changes, 1 if changes (with --exit-code).
            # If we don't use --exit-code, it returns 0.
            return False, e.stderr.strip()
        except FileNotFoundError:
            raise ELSTRIXError("Git is not installed or not found in system path.")

    def _detect_changes(self) -> List[str]:
        """Detect modified, added, or deleted files."""
        # Add all tracked files explicitly so untracked new files are staged
        # We only want to track changes in our specific files
        changed_files = []
        for file in self.files_to_track:
            file_path = PathManager.ROOT_DIR / file
            if file_path.exists():
                self._run_git(["add", file])
        
        # Check what is staged
        success, stdout = self._run_git(["diff", "--cached", "--name-only"])
        if success and stdout:
            changed_files = [f for f in stdout.split('\n') if f]
            
        return changed_files

    def _generate_commit_message(self, changed_files: List[str]) -> str:
        """Generate a meaningful commit message based on changed files."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        updates = []
        if "README.md" in changed_files:
            updates.append("Regenerate README")
        if any("svg" in f for f in changed_files):
            updates.append("Update SVG Profile")
        if any("ascii" in f for f in changed_files):
            updates.append("Update Avatar ASCII")
        if any("json" in f or "stats" in f for f in changed_files):
            updates.append("Refresh GitHub Statistics")
        
        if updates:
            action = ", ".join(updates)
        else:
            action = "Automated Profile Refresh"
            
        return f"chore: {action} [{timestamp}]"

    def _configure_git(self) -> None:
        """Configure git user if running in CI."""
        if os.environ.get("GITHUB_ACTIONS") == "true":
            self._run_git(["config", "user.name", "EL-STRIX Bot"])
            self._run_git(["config", "user.email", "el-strix-bot@users.noreply.github.com"])

    def run(self) -> None:
        """Execute the automation pipeline."""
        logger.info("--- PHASE 07: FULL AUTOMATION ENGINE ---")
        
        try:
            self._configure_git()
            
            # Detect changes
            logger.info("Detecting file changes...")
            changed_files = self._detect_changes()
            
            if not changed_files:
                logger.info("No changes detected. Workflow finished successfully.")
                logger.info("--- PHASE 07 COMPLETED ---")
                return

            logger.info(f"Detected changes in: {', '.join(changed_files)}")
            
            # Commit
            commit_message = self._generate_commit_message(changed_files)
            logger.info(f"Creating commit: {commit_message}")
            success, output = self._run_git(["commit", "-m", commit_message])
            
            if not success:
                logger.error(f"Failed to create commit: {output}")
                raise ELSTRIXError(f"Git commit failed: {output}")
                
            # Push
            logger.info("Pushing changes to remote repository...")
            
            # In GitHub actions, we push to origin main
            success, output = self._run_git(["push", "origin", f"HEAD:{self.branch}"])
            
            if not success:
                logger.error(f"Failed to push changes: {output}")
                raise ELSTRIXError(f"Git push failed: {output}")
                
            logger.info("Successfully pushed changes.")
            logger.info("--- PHASE 07 COMPLETED ---")
            
        except ELSTRIXError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Automation Engine: {e}")
            raise ELSTRIXError(f"Automation failed: {e}")
