#!/usr/bin/env python3
"""
ADW Status Operations Module

Core operations for monitoring ADW status.
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List


class TaskStatus(Enum):
    """Task status states"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class LocalTask:
    """Local task information"""
    task_id: str
    task: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    duration_seconds: float = 0
    tokens_used: int = 0
    cost_usd: float = 0
    output_file: Optional[str] = None


@dataclass
class GitHubRun:
    """GitHub Actions workflow run"""
    run_id: int
    run_number: int
    status: str  # queued, in_progress, completed
    conclusion: Optional[str] = None  # success, failure, cancelled
    workflow: str = ""
    branch: str = ""
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    url: str = ""
    task: str = ""


@dataclass
class CostSummary:
    """Cost summary data"""
    daily_total: float = 0
    daily_budget: float = 1.00
    local_cost: float = 0
    github_cost: float = 0  # Always 0 with Max subscription
    tokens_used: int = 0
    percentage_used: float = 0


def load_settings() -> Dict[str, Any]:
    """Load skill settings from config file"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


def get_local_tasks() -> List[LocalTask]:
    """
    Get status of local Claude tasks.

    Returns:
        List of LocalTask objects
    """
    tasks = []

    # Check for running Claude processes
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq claude.exe", "/FO", "CSV"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if "claude.exe" in result.stdout:
            # Found running Claude processes
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    tasks.append(LocalTask(
                        task_id=parts[1],  # PID
                        task="Local Claude process",
                        status=TaskStatus.RUNNING
                    ))
    except Exception:
        pass

    # Check task output files
    task_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "claude"
    if task_dir.exists():
        for output_file in task_dir.glob("**/*.output"):
            try:
                stat = output_file.stat()
                age = datetime.now().timestamp() - stat.st_mtime
                if age < 3600:  # Last hour
                    content = output_file.read_text()[:500]
                    tasks.append(LocalTask(
                        task_id=output_file.stem,
                        task=content[:100] if content else "Unknown task",
                        status=TaskStatus.COMPLETED if age > 60 else TaskStatus.RUNNING,
                        output_file=str(output_file)
                    ))
            except Exception:
                continue

    return tasks


def get_github_runs(max_runs: int = 10) -> List[GitHubRun]:
    """
    Get GitHub Actions workflow runs.

    Args:
        max_runs: Maximum runs to fetch

    Returns:
        List of GitHubRun objects
    """
    settings = load_settings()
    gh_config = settings.get("github_actions", {})
    repo = gh_config.get("repo", "gblack686/consulting-co")
    workflow = gh_config.get("workflow", "adw-plan-build-review.yml")

    runs = []

    try:
        cmd = [
            "gh", "run", "list",
            "--repo", repo,
            "--workflow", workflow,
            "--limit", str(max_runs),
            "--json", "databaseId,number,status,conclusion,workflowName,headBranch,startedAt,updatedAt,url"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            for run in data:
                runs.append(GitHubRun(
                    run_id=run.get("databaseId", 0),
                    run_number=run.get("number", 0),
                    status=run.get("status", "unknown"),
                    conclusion=run.get("conclusion"),
                    workflow=run.get("workflowName", ""),
                    branch=run.get("headBranch", ""),
                    started_at=run.get("startedAt"),
                    updated_at=run.get("updatedAt"),
                    url=run.get("url", "")
                ))

    except Exception as e:
        print(f"Error fetching GitHub runs: {e}")

    return runs


def get_github_run_details(run_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific GitHub Actions run.

    Args:
        run_id: The workflow run ID

    Returns:
        Run details dict or None
    """
    settings = load_settings()
    gh_config = settings.get("github_actions", {})
    repo = gh_config.get("repo", "gblack686/consulting-co")

    try:
        cmd = [
            "gh", "run", "view", str(run_id),
            "--repo", repo,
            "--json", "databaseId,number,status,conclusion,workflowName,startedAt,updatedAt,url,jobs"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return json.loads(result.stdout)

    except Exception as e:
        print(f"Error fetching run details: {e}")

    return None


def get_cost_summary() -> CostSummary:
    """
    Get cost summary for today.

    Returns:
        CostSummary object
    """
    settings = load_settings()
    cost_config = settings.get("cost_tracking", {})
    usage_log_path = cost_config.get("usage_log")
    daily_budget = cost_config.get("daily_budget", 1.00)

    summary = CostSummary(daily_budget=daily_budget)

    if usage_log_path:
        log_path = Path(__file__).parent.parent.parent / usage_log_path
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    usage_data = json.load(f)

                today = datetime.now().strftime("%Y-%m-%d")
                today_entries = usage_data.get("entries", {}).get(today, [])

                for entry in today_entries:
                    summary.tokens_used += entry.get("tokens", 0)
                    summary.local_cost += entry.get("cost", 0)

                summary.daily_total = summary.local_cost
                summary.percentage_used = (summary.daily_total / summary.daily_budget) * 100

            except Exception:
                pass

    return summary


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_time_ago(timestamp: str) -> str:
    """Format timestamp as 'X minutes ago'"""
    if not timestamp:
        return "unknown"

    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = (now - dt).total_seconds()
        return format_duration(diff) + " ago"
    except Exception:
        return timestamp


if __name__ == "__main__":
    # Quick test
    print("Local Tasks:")
    for task in get_local_tasks():
        print(f"  [{task.status.value}] {task.task_id}: {task.task[:50]}")

    print("\nGitHub Runs:")
    for run in get_github_runs(5):
        print(f"  [{run.status}] #{run.run_number}: {run.workflow}")

    print("\nCost Summary:")
    summary = get_cost_summary()
    print(f"  Today: ${summary.daily_total:.4f} / ${summary.daily_budget:.2f}")
