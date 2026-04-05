#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Pipeline Status Loader — SessionStart Hook

Injects latest CI/CD pipeline status at session start.
Fetches from GitHub Actions via `gh` CLI:
  - Last 3 workflow runs (status, conclusion, branch)
  - Any failing checks on current branch
  - Open PRs for this branch

Output: JSON to stdout (additionalContext for SessionStart hooks)
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, timeout: int = 10) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def get_current_branch() -> str:
    """Get current git branch."""
    return run_command("git branch --show-current")


def get_recent_runs() -> list:
    """Get last 3 GitHub Actions workflow runs."""
    output = run_command(
        "gh run list --limit 3 --json status,conclusion,name,headBranch,createdAt,url"
    )
    if not output:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def get_failing_checks(branch: str) -> list:
    """Get failing checks on current branch."""
    if not branch:
        return []
    output = run_command(
        f"gh pr checks --json name,state,link 2>/dev/null"
    )
    if not output:
        return []
    try:
        checks = json.loads(output)
        return [c for c in checks if c.get("state") == "FAILURE"]
    except json.JSONDecodeError:
        return []


def get_open_prs(branch: str) -> list:
    """Get open PRs for this branch."""
    if not branch:
        return []
    output = run_command(
        f'gh pr list --head "{branch}" --json number,title,url,state --limit 3'
    )
    if not output:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def main():
    try:
        # Check if gh CLI is available
        gh_check = run_command("gh --version")
        if not gh_check:
            sys.exit(0)

        # Check if we're in a git repo with a GitHub remote
        remote = run_command("gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null")
        if not remote:
            sys.exit(0)

        branch = get_current_branch()
        runs = get_recent_runs()
        failing = get_failing_checks(branch)
        prs = get_open_prs(branch)

        # Build status report
        lines = [f"CI/CD Pipeline Status ({remote})"]

        if runs:
            lines.append("Recent Workflow Runs:")
            for run in runs:
                status = run.get("conclusion") or run.get("status", "unknown")
                icon = "pass" if status == "success" else "FAIL" if status == "failure" else status
                lines.append(
                    f"  [{icon}] {run.get('name', 'N/A')} on {run.get('headBranch', '?')}"
                )

        if failing:
            lines.append(f"Failing Checks on {branch}:")
            for check in failing:
                lines.append(f"  FAIL: {check.get('name', 'N/A')}")

        if prs:
            lines.append(f"Open PRs for {branch}:")
            for pr in prs:
                lines.append(f"  #{pr.get('number')}: {pr.get('title', 'N/A')}")

        if not runs and not failing and not prs:
            lines.append("No CI/CD activity found")

        # Output as additionalContext
        print("\n".join(lines))
        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
