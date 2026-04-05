#!/usr/bin/env python3
"""
Worktree Operations Module

Core operations for git worktree management.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class Worktree:
    """Worktree information"""
    name: str
    path: str
    branch: str
    commit: str
    is_bare: bool = False
    is_main: bool = False
    created_at: Optional[str] = None


@dataclass
class WorktreeResult:
    """Result of worktree operation"""
    success: bool
    message: str
    worktree: Optional[Worktree] = None
    error: Optional[str] = None


def load_settings() -> Dict[str, Any]:
    """Load skill settings from config file"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


def get_repo_root() -> str:
    """Get the git repository root directory"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def slugify(name: str) -> str:
    """Convert name to slug format"""
    # Lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug[:50]  # Max 50 chars


def list_worktrees() -> List[Worktree]:
    """
    List all git worktrees.

    Returns:
        List of Worktree objects
    """
    worktrees = []

    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            current_worktree = {}
            for line in result.stdout.split("\n"):
                if line.startswith("worktree "):
                    if current_worktree:
                        worktrees.append(Worktree(**current_worktree))
                    current_worktree = {"path": line[9:]}
                elif line.startswith("HEAD "):
                    current_worktree["commit"] = line[5:]
                elif line.startswith("branch "):
                    branch = line[7:]
                    current_worktree["branch"] = branch
                    current_worktree["name"] = Path(current_worktree["path"]).name
                    current_worktree["is_main"] = branch.endswith("/main") or branch.endswith("/master")
                elif line == "bare":
                    current_worktree["is_bare"] = True

            if current_worktree and "branch" in current_worktree:
                worktrees.append(Worktree(**current_worktree))

    except Exception as e:
        print(f"Error listing worktrees: {e}")

    return worktrees


def create_worktree(name: str, from_branch: Optional[str] = None) -> WorktreeResult:
    """
    Create a new worktree.

    Args:
        name: Name for the worktree
        from_branch: Branch to create from (default: main)

    Returns:
        WorktreeResult
    """
    settings = load_settings()
    worktree_config = settings.get("worktree", {})
    git_config = settings.get("git", {})

    base_dir = worktree_config.get("base_dir", "../adw-workspaces")
    branch_prefix = worktree_config.get("branch_prefix", "adw/")
    main_branch = git_config.get("main_branch", "main")

    slug = slugify(name)
    branch_name = f"{branch_prefix}{slug}"
    repo_root = get_repo_root()
    worktree_path = str(Path(repo_root) / base_dir / f"adw-{slug}")

    # Ensure base directory exists
    base_path = Path(repo_root) / base_dir
    base_path.mkdir(parents=True, exist_ok=True)

    try:
        # Fetch latest if configured
        if git_config.get("auto_fetch", True):
            subprocess.run(["git", "fetch", "origin"], capture_output=True)

        # Create worktree with new branch
        source_branch = from_branch or main_branch
        cmd = ["git", "worktree", "add", "-b", branch_name, worktree_path, source_branch]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            worktree = Worktree(
                name=f"adw-{slug}",
                path=worktree_path,
                branch=branch_name,
                commit="HEAD",
                created_at=datetime.now().isoformat()
            )
            return WorktreeResult(
                success=True,
                message=f"Created worktree '{slug}' at {worktree_path}",
                worktree=worktree
            )
        else:
            return WorktreeResult(
                success=False,
                message="Failed to create worktree",
                error=result.stderr
            )

    except Exception as e:
        return WorktreeResult(
            success=False,
            message="Worktree creation error",
            error=str(e)
        )


def merge_worktree(name: str, delete_after: bool = True) -> WorktreeResult:
    """
    Merge worktree branch to main.

    Args:
        name: Name of the worktree
        delete_after: Delete branch and worktree after merge

    Returns:
        WorktreeResult
    """
    settings = load_settings()
    worktree_config = settings.get("worktree", {})
    git_config = settings.get("git", {})

    branch_prefix = worktree_config.get("branch_prefix", "adw/")
    main_branch = git_config.get("main_branch", "main")

    slug = slugify(name)
    branch_name = f"{branch_prefix}{slug}"

    try:
        # Checkout main
        result = subprocess.run(
            ["git", "checkout", main_branch],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return WorktreeResult(
                success=False,
                message=f"Failed to checkout {main_branch}",
                error=result.stderr
            )

        # Merge the branch
        result = subprocess.run(
            ["git", "merge", branch_name, "--no-ff", "-m", f"Merge ADW: {slug}"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return WorktreeResult(
                success=False,
                message="Merge failed - resolve conflicts manually",
                error=result.stderr
            )

        # Cleanup if requested
        if delete_after:
            cleanup_worktree(name)

        return WorktreeResult(
            success=True,
            message=f"Merged {branch_name} into {main_branch}"
        )

    except Exception as e:
        return WorktreeResult(
            success=False,
            message="Merge error",
            error=str(e)
        )


def cleanup_worktree(name: str) -> WorktreeResult:
    """
    Remove worktree and optionally delete branch.

    Args:
        name: Name of the worktree

    Returns:
        WorktreeResult
    """
    settings = load_settings()
    worktree_config = settings.get("worktree", {})
    cleanup_config = settings.get("cleanup", {})

    base_dir = worktree_config.get("base_dir", "../adw-workspaces")
    branch_prefix = worktree_config.get("branch_prefix", "adw/")
    remove_branch = cleanup_config.get("remove_branch", True)

    slug = slugify(name)
    branch_name = f"{branch_prefix}{slug}"
    repo_root = get_repo_root()
    worktree_path = str(Path(repo_root) / base_dir / f"adw-{slug}")

    try:
        # Remove worktree
        result = subprocess.run(
            ["git", "worktree", "remove", worktree_path, "--force"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0 and "is not a working tree" not in result.stderr:
            return WorktreeResult(
                success=False,
                message="Failed to remove worktree",
                error=result.stderr
            )

        # Delete branch if configured
        if remove_branch:
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                capture_output=True,
                text=True
            )

        # Prune worktrees
        subprocess.run(
            ["git", "worktree", "prune"],
            capture_output=True
        )

        return WorktreeResult(
            success=True,
            message=f"Cleaned up worktree '{slug}'"
        )

    except Exception as e:
        return WorktreeResult(
            success=False,
            message="Cleanup error",
            error=str(e)
        )


if __name__ == "__main__":
    # Quick test
    print("Active Worktrees:")
    for wt in list_worktrees():
        print(f"  {wt.name}: {wt.branch} @ {wt.path}")
