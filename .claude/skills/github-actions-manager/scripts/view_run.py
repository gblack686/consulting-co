#!/usr/bin/env python3
"""
View details of a specific GitHub Actions workflow run.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gh_actions_ops import get_run, get_run_logs, format_status, get_run_duration


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"default_repo": "gblack686/consulting-co"}


def main():
    parser = argparse.ArgumentParser(description="View GitHub Actions run details")
    parser.add_argument("run_id", type=int, help="Run ID to view")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--logs", "-l", action="store_true",
                        help="Show full logs")
    parser.add_argument("--logs-failed", "-f", action="store_true",
                        help="Show only failed step logs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")

    # Get run details
    success, run = get_run(repo, args.run_id)

    if not success:
        print(f"Error: {run}")
        return 1

    if args.json:
        print(json.dumps(run, indent=2))
        return 0

    # Display run info
    status = format_status(run.get("status"), run.get("conclusion"))
    duration = get_run_duration(run)

    print(f"Run #{run.get('databaseId')}: {run.get('displayTitle')}")
    print("=" * 60)
    print(f"Workflow: {run.get('workflowName')}")
    print(f"Status:   {status}")
    print(f"Branch:   {run.get('headBranch')}")
    print(f"Duration: {duration}")
    print(f"Started:  {run.get('createdAt')}")
    print(f"Updated:  {run.get('updatedAt')}")
    print(f"URL:      {run.get('url')}")

    # Show jobs
    jobs = run.get("jobs", [])
    if jobs:
        print(f"\nJobs ({len(jobs)}):")
        print("-" * 60)
        for job in jobs:
            job_status = format_status(job.get("status"), job.get("conclusion"))
            print(f"  {job.get('name')}: {job_status}")

            # Show steps for failed jobs
            if job.get("conclusion") == "failure":
                steps = job.get("steps", [])
                for step in steps:
                    if step.get("conclusion") == "failure":
                        print(f"    ❌ {step.get('name')}")

    # Show logs if requested
    if args.logs or args.logs_failed:
        print("\n" + "=" * 60)
        print("LOGS")
        print("=" * 60)

        log_success, logs = get_run_logs(repo, args.run_id, failed_only=args.logs_failed)

        if log_success:
            # Truncate if very long
            if len(logs) > 10000:
                print(logs[:10000])
                print(f"\n... (truncated, {len(logs)} total characters)")
            else:
                print(logs)
        else:
            print(f"Error fetching logs: {logs}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
