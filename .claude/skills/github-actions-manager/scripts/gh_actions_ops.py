#!/usr/bin/env python3
"""
GitHub Actions Operations Module

Core functions for managing GitHub Actions workflows via gh CLI.
"""

import json
import subprocess
from typing import Optional
from datetime import datetime, timedelta


def run_gh_command(args: list, capture_output: bool = True) -> tuple[int, str, str]:
    """
    Run a gh CLI command and return results.

    Args:
        args: List of arguments for gh command
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=capture_output,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except FileNotFoundError:
        return 1, "", "gh CLI not found. Install from https://cli.github.com/"
    except Exception as e:
        return 1, "", str(e)


def list_workflows(repo: str) -> tuple[bool, list | str]:
    """
    List all workflows in a repository.

    Args:
        repo: Repository in format "owner/repo"

    Returns:
        Tuple of (success, workflows_list_or_error)
    """
    args = [
        "workflow", "list",
        "--repo", repo,
        "--json", "id,name,path,state"
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        try:
            return True, json.loads(stdout) if stdout else []
        except json.JSONDecodeError:
            return True, []
    return False, stderr


def get_workflow(repo: str, workflow: str) -> tuple[bool, dict | str]:
    """
    Get details of a specific workflow.

    Args:
        repo: Repository in format "owner/repo"
        workflow: Workflow filename or ID

    Returns:
        Tuple of (success, workflow_dict_or_error)
    """
    args = [
        "workflow", "view", workflow,
        "--repo", repo,
        "--json", "id,name,path,state"
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        try:
            return True, json.loads(stdout)
        except json.JSONDecodeError:
            return False, "Failed to parse workflow data"
    return False, stderr


def list_runs(
    repo: str,
    workflow: str = None,
    status: str = None,
    branch: str = None,
    limit: int = 20
) -> tuple[bool, list | str]:
    """
    List workflow runs.

    Args:
        repo: Repository in format "owner/repo"
        workflow: Filter by workflow filename (optional)
        status: Filter by status: queued, in_progress, completed (optional)
        branch: Filter by branch (optional)
        limit: Maximum runs to return

    Returns:
        Tuple of (success, runs_list_or_error)
    """
    args = [
        "run", "list",
        "--repo", repo,
        "--limit", str(limit),
        "--json", "databaseId,displayTitle,status,conclusion,workflowName,headBranch,createdAt,updatedAt,url"
    ]

    if workflow:
        args.extend(["--workflow", workflow])
    if status:
        args.extend(["--status", status])
    if branch:
        args.extend(["--branch", branch])

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        try:
            return True, json.loads(stdout) if stdout else []
        except json.JSONDecodeError:
            return True, []
    return False, stderr


def get_run(repo: str, run_id: int) -> tuple[bool, dict | str]:
    """
    Get details of a specific run.

    Args:
        repo: Repository in format "owner/repo"
        run_id: Run ID

    Returns:
        Tuple of (success, run_dict_or_error)
    """
    args = [
        "run", "view", str(run_id),
        "--repo", repo,
        "--json", "databaseId,displayTitle,status,conclusion,workflowName,headBranch,createdAt,updatedAt,url,jobs"
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        try:
            return True, json.loads(stdout)
        except json.JSONDecodeError:
            return False, "Failed to parse run data"
    return False, stderr


def get_run_logs(repo: str, run_id: int, failed_only: bool = False) -> tuple[bool, str]:
    """
    Get logs from a workflow run.

    Args:
        repo: Repository in format "owner/repo"
        run_id: Run ID
        failed_only: Only get logs from failed steps

    Returns:
        Tuple of (success, logs_or_error)
    """
    args = [
        "run", "view", str(run_id),
        "--repo", repo
    ]

    if failed_only:
        args.append("--log-failed")
    else:
        args.append("--log")

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        return True, stdout
    return False, stderr


def trigger_workflow(
    repo: str,
    workflow: str,
    ref: str = "main",
    inputs: dict = None
) -> tuple[bool, str]:
    """
    Trigger a workflow run.

    Args:
        repo: Repository in format "owner/repo"
        workflow: Workflow filename
        ref: Branch or tag to run on
        inputs: Workflow inputs as dict

    Returns:
        Tuple of (success, message)
    """
    args = [
        "workflow", "run", workflow,
        "--repo", repo,
        "--ref", ref
    ]

    if inputs:
        for key, value in inputs.items():
            args.extend(["-f", f"{key}={value}"])

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        return True, f"Workflow '{workflow}' triggered on {ref}"
    return False, stderr


def cancel_run(repo: str, run_id: int) -> tuple[bool, str]:
    """
    Cancel a workflow run.

    Args:
        repo: Repository in format "owner/repo"
        run_id: Run ID to cancel

    Returns:
        Tuple of (success, message)
    """
    args = [
        "run", "cancel", str(run_id),
        "--repo", repo
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        return True, f"Run {run_id} cancelled"
    return False, stderr


def rerun_workflow(repo: str, run_id: int, failed_only: bool = False) -> tuple[bool, str]:
    """
    Rerun a workflow.

    Args:
        repo: Repository in format "owner/repo"
        run_id: Run ID to rerun
        failed_only: Only rerun failed jobs

    Returns:
        Tuple of (success, message)
    """
    args = [
        "run", "rerun", str(run_id),
        "--repo", repo
    ]

    if failed_only:
        args.append("--failed")

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        return True, f"Run {run_id} rerun triggered"
    return False, stderr


def get_run_duration(run: dict) -> str:
    """Calculate and format run duration."""
    try:
        created = datetime.fromisoformat(run["createdAt"].replace("Z", "+00:00"))
        updated = datetime.fromisoformat(run["updatedAt"].replace("Z", "+00:00"))
        duration = updated - created

        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)

        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    except:
        return "unknown"


def format_status(status: str, conclusion: str = None) -> str:
    """Format status with emoji."""
    if status == "completed":
        if conclusion == "success":
            return "✅ success"
        elif conclusion == "failure":
            return "❌ failure"
        elif conclusion == "cancelled":
            return "⚪ cancelled"
        elif conclusion == "skipped":
            return "⏭️ skipped"
        else:
            return f"⚪ {conclusion}"
    elif status == "in_progress":
        return "🔄 running"
    elif status == "queued":
        return "⏳ queued"
    else:
        return status


def get_failure_analysis(repo: str, days: int = 30, limit: int = 100) -> dict:
    """
    Analyze workflow failures over a period.

    Args:
        repo: Repository
        days: Number of days to analyze
        limit: Max runs to fetch

    Returns:
        Analysis dict with failure patterns
    """
    success, runs = list_runs(repo, limit=limit)
    if not success:
        return {"error": runs}

    # Filter to failures
    failures = [r for r in runs if r.get("conclusion") == "failure"]

    # Group by workflow
    by_workflow = {}
    for run in failures:
        wf = run.get("workflowName", "unknown")
        if wf not in by_workflow:
            by_workflow[wf] = []
        by_workflow[wf].append(run)

    return {
        "total_runs": len(runs),
        "total_failures": len(failures),
        "success_rate": round((len(runs) - len(failures)) / len(runs) * 100, 1) if runs else 0,
        "failures_by_workflow": {k: len(v) for k, v in by_workflow.items()},
        "recent_failures": failures[:5]
    }


if __name__ == "__main__":
    # Test basic functionality
    import sys

    repo = "gblack686/consulting-co"

    print("Testing GitHub Actions operations...")
    print(f"Repository: {repo}\n")

    # List workflows
    success, workflows = list_workflows(repo)
    if success:
        print(f"Found {len(workflows)} workflows:")
        for wf in workflows:
            print(f"  - {wf.get('name')} ({wf.get('state')})")
    else:
        print(f"No workflows found or error: {workflows}")

    # List recent runs
    print("\nRecent runs:")
    success, runs = list_runs(repo, limit=5)
    if success:
        for run in runs:
            status = format_status(run.get("status"), run.get("conclusion"))
            print(f"  {run.get('databaseId')}: {run.get('displayTitle')[:40]} - {status}")
    else:
        print(f"No runs or error: {runs}")
