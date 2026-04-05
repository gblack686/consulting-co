#!/usr/bin/env python3
"""
List all running ADWs (local and GitHub Actions).

Usage:
    python list_running.py
    python list_running.py --json
"""

import argparse
import json
import sys
from status_ops import (
    get_local_tasks,
    get_github_runs,
    get_cost_summary,
    format_time_ago,
    TaskStatus
)


def main():
    parser = argparse.ArgumentParser(description="List all running ADWs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--running-only", action="store_true", help="Show only running tasks")

    args = parser.parse_args()

    local_tasks = get_local_tasks()
    github_runs = get_github_runs()
    cost_summary = get_cost_summary()

    if args.running_only:
        local_tasks = [t for t in local_tasks if t.status == TaskStatus.RUNNING]
        github_runs = [r for r in github_runs if r.status in ["queued", "in_progress"]]

    if args.json:
        output = {
            "local_tasks": [
                {
                    "task_id": t.task_id,
                    "task": t.task,
                    "status": t.status.value,
                    "tokens": t.tokens_used,
                    "cost": t.cost_usd
                }
                for t in local_tasks
            ],
            "github_runs": [
                {
                    "run_id": r.run_id,
                    "status": r.status,
                    "conclusion": r.conclusion,
                    "url": r.url,
                    "started_at": r.started_at
                }
                for r in github_runs
            ],
            "cost_summary": {
                "daily_total": cost_summary.daily_total,
                "daily_budget": cost_summary.daily_budget,
                "percentage_used": cost_summary.percentage_used
            }
        }
        print(json.dumps(output, indent=2))
        return 0

    # Text output
    print(f"\n{'='*60}")
    print(f"ADW Status Report")
    print(f"{'='*60}")

    # Local tasks
    running_local = [t for t in local_tasks if t.status == TaskStatus.RUNNING]
    print(f"\nLOCAL TASKS ({len(running_local)} running):")
    if local_tasks:
        for task in local_tasks:
            status_icon = "" if task.status == TaskStatus.RUNNING else ""
            print(f"  {status_icon} [{task.status.value}] {task.task_id}")
            print(f"      Task: {task.task[:60]}...")
            if task.tokens_used:
                print(f"      Tokens: {task.tokens_used:,} | Cost: ${task.cost_usd:.4f}")
    else:
        print("  No local tasks found")

    # GitHub runs
    running_gh = [r for r in github_runs if r.status in ["queued", "in_progress"]]
    print(f"\nGITHUB ACTIONS ({len(running_gh)} active):")
    if github_runs:
        for run in github_runs[:5]:  # Show last 5
            if run.status == "in_progress":
                status_icon = ""
            elif run.status == "queued":
                status_icon = ""
            elif run.conclusion == "success":
                status_icon = ""
            else:
                status_icon = ""

            print(f"  {status_icon} [{run.status}] #{run.run_number}")
            print(f"      Workflow: {run.workflow}")
            print(f"      Started: {format_time_ago(run.started_at)}")
            print(f"      URL: {run.url}")
    else:
        print("  No GitHub Actions runs found")

    # Cost summary
    print(f"\nCOST SUMMARY:")
    bar_width = 30
    filled = int((cost_summary.percentage_used / 100) * bar_width)
    bar = "" * filled + "" * (bar_width - filled)
    print(f"  Today: ${cost_summary.daily_total:.4f} / ${cost_summary.daily_budget:.2f}")
    print(f"  [{bar}] {cost_summary.percentage_used:.1f}%")
    print(f"  Local: ${cost_summary.local_cost:.4f} | GitHub: ${cost_summary.github_cost:.2f}")

    if cost_summary.percentage_used >= 80:
        print(f"\n  WARNING: Approaching daily budget limit!")

    print(f"\n{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
