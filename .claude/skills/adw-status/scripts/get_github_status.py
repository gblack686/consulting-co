#!/usr/bin/env python3
"""
Get GitHub Actions workflow status.

Usage:
    python get_github_status.py
    python get_github_status.py --run-id 12345
    python get_github_status.py --watch
"""

import argparse
import json
import sys
import time
from status_ops import get_github_runs, get_github_run_details, format_time_ago


def main():
    parser = argparse.ArgumentParser(description="Get GitHub Actions status")
    parser.add_argument("--run-id", type=int, help="Specific run ID to check")
    parser.add_argument("--watch", action="store_true", help="Watch for updates")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--limit", type=int, default=10, help="Max runs to show")

    args = parser.parse_args()

    if args.run_id:
        # Get specific run details
        details = get_github_run_details(args.run_id)
        if args.json:
            print(json.dumps(details, indent=2))
        else:
            if details:
                print(f"\nWorkflow Run #{details.get('number', args.run_id)}")
                print(f"{'='*50}")
                print(f"Status: {details.get('status', 'unknown')}")
                print(f"Conclusion: {details.get('conclusion', 'pending')}")
                print(f"Workflow: {details.get('workflowName', 'unknown')}")
                print(f"Started: {format_time_ago(details.get('startedAt', ''))}")
                print(f"URL: {details.get('url', '')}")

                jobs = details.get("jobs", [])
                if jobs:
                    print(f"\nJobs:")
                    for job in jobs:
                        conclusion = job.get("conclusion") or job.get("status")
                        print(f"  - {job.get('name', 'unknown')}: {conclusion}")
            else:
                print(f"Run {args.run_id} not found")
        return 0

    def display_runs():
        runs = get_github_runs(args.limit)

        if args.json:
            output = [
                {
                    "run_id": r.run_id,
                    "run_number": r.run_number,
                    "status": r.status,
                    "conclusion": r.conclusion,
                    "workflow": r.workflow,
                    "branch": r.branch,
                    "started_at": r.started_at,
                    "url": r.url
                }
                for r in runs
            ]
            print(json.dumps(output, indent=2))
        else:
            print(f"\nGitHub Actions - Recent Workflow Runs")
            print(f"{'='*60}")

            if not runs:
                print("No workflow runs found")
                return

            for run in runs:
                # Status icon
                if run.status == "in_progress":
                    icon = ""
                elif run.status == "queued":
                    icon = ""
                elif run.conclusion == "success":
                    icon = ""
                elif run.conclusion == "failure":
                    icon = ""
                elif run.conclusion == "cancelled":
                    icon = ""
                else:
                    icon = ""

                status_text = run.conclusion or run.status
                print(f"\n{icon} Run #{run.run_number} - {status_text.upper()}")
                print(f"   Workflow: {run.workflow}")
                print(f"   Branch: {run.branch}")
                print(f"   Started: {format_time_ago(run.started_at)}")
                print(f"   URL: {run.url}")

            print(f"\n{'='*60}")

        return runs

    if args.watch:
        print("Watching GitHub Actions... (Ctrl+C to stop)")
        while True:
            runs = display_runs()
            active = [r for r in runs if r.status in ["queued", "in_progress"]]
            if not active:
                print("\nNo active runs. Stopping watch.")
                break
            time.sleep(10)
    else:
        display_runs()

    return 0


if __name__ == "__main__":
    sys.exit(main())
