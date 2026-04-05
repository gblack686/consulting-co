#!/usr/bin/env python3
"""
List GitHub Actions workflow runs.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from gh_actions_ops import list_runs, format_status, get_run_duration


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"default_repo": "gblack686/consulting-co"}


def format_time_ago(iso_time: str) -> str:
    """Format ISO time as relative time."""
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    except:
        return iso_time[:10]


def main():
    parser = argparse.ArgumentParser(description="List GitHub Actions workflow runs")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--workflow", "-w", help="Filter by workflow filename")
    parser.add_argument("--status", "-s",
                        choices=["queued", "in_progress", "completed"],
                        help="Filter by status")
    parser.add_argument("--branch", "-b", help="Filter by branch")
    parser.add_argument("--limit", "-n", type=int, default=20,
                        help="Maximum runs to show (default: 20)")
    parser.add_argument("--failures", "-f", action="store_true",
                        help="Show only failed runs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show more details")

    args = parser.parse_args()

    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")

    # Build filters description
    filters = []
    if args.workflow:
        filters.append(f"workflow={args.workflow}")
    if args.status:
        filters.append(f"status={args.status}")
    if args.branch:
        filters.append(f"branch={args.branch}")
    if args.failures:
        filters.append("failures only")

    filter_str = f" ({', '.join(filters)})" if filters else ""
    print(f"Workflow runs in {repo}{filter_str}:\n")

    success, runs = list_runs(
        repo,
        workflow=args.workflow,
        status=args.status,
        branch=args.branch,
        limit=args.limit
    )

    if not success:
        print(f"Error: {runs}")
        return 1

    # Filter to failures if requested
    if args.failures:
        runs = [r for r in runs if r.get("conclusion") == "failure"]

    if not runs:
        print("No runs found matching criteria.")
        return 0

    if args.json:
        print(json.dumps(runs, indent=2))
        return 0

    # Print runs
    if args.verbose:
        for run in runs:
            status = format_status(run.get("status"), run.get("conclusion"))
            duration = get_run_duration(run)
            time_ago = format_time_ago(run.get("createdAt", ""))

            print(f"Run #{run.get('databaseId')}")
            print(f"  Title: {run.get('displayTitle')}")
            print(f"  Workflow: {run.get('workflowName')}")
            print(f"  Status: {status}")
            print(f"  Branch: {run.get('headBranch')}")
            print(f"  Duration: {duration}")
            print(f"  Started: {time_ago}")
            print(f"  URL: {run.get('url')}")
            print()
    else:
        print(f"{'ID':<10} {'Status':<15} {'Workflow':<25} {'Branch':<15} {'Time':<10}")
        print("-" * 75)

        for run in runs:
            run_id = str(run.get("databaseId", ""))[:8]
            status = format_status(run.get("status"), run.get("conclusion"))
            workflow = run.get("workflowName", "")[:23]
            branch = run.get("headBranch", "")[:13]
            time_ago = format_time_ago(run.get("createdAt", ""))

            print(f"{run_id:<10} {status:<15} {workflow:<25} {branch:<15} {time_ago:<10}")

    # Summary
    total = len(runs)
    success_count = sum(1 for r in runs if r.get("conclusion") == "success")
    failure_count = sum(1 for r in runs if r.get("conclusion") == "failure")
    in_progress = sum(1 for r in runs if r.get("status") == "in_progress")

    print(f"\nTotal: {total} run(s)")
    if total > 0:
        print(f"  ✅ {success_count} success | ❌ {failure_count} failed | 🔄 {in_progress} in progress")

    return 0


if __name__ == "__main__":
    sys.exit(main())
