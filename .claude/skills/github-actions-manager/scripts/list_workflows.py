#!/usr/bin/env python3
"""
List GitHub Actions workflows for a repository.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gh_actions_ops import list_workflows, list_runs, format_status


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"default_repo": "gblack686/consulting-co"}


def main():
    parser = argparse.ArgumentParser(description="List GitHub Actions workflows")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--with-status", "-s", action="store_true",
                        help="Include latest run status for each workflow")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")

    print(f"Workflows in {repo}:\n")

    success, workflows = list_workflows(repo)

    if not success:
        print(f"Error: {workflows}")
        return 1

    if not workflows:
        print("No workflows found.")
        print("\nTo create a workflow, add a .yml file to .github/workflows/")
        return 0

    if args.json:
        print(json.dumps(workflows, indent=2))
        return 0

    # Get latest run status for each workflow if requested
    workflow_status = {}
    if args.with_status:
        for wf in workflows:
            wf_name = wf.get("name")
            wf_path = Path(wf.get("path", "")).name
            ok, runs = list_runs(repo, workflow=wf_path, limit=1)
            if ok and runs:
                run = runs[0]
                workflow_status[wf_name] = {
                    "status": format_status(run.get("status"), run.get("conclusion")),
                    "branch": run.get("headBranch"),
                    "run_id": run.get("databaseId")
                }

    # Print workflows
    print(f"{'Workflow':<30} {'State':<10} {'File':<25}", end="")
    if args.with_status:
        print(f" {'Latest Run':<15} {'Branch':<15}")
    else:
        print()

    print("-" * (80 if args.with_status else 65))

    for wf in workflows:
        name = wf.get("name", "unknown")[:28]
        state = wf.get("state", "unknown")
        path = Path(wf.get("path", "")).name[:23]

        line = f"{name:<30} {state:<10} {path:<25}"

        if args.with_status and name in workflow_status:
            status_info = workflow_status[name]
            line += f" {status_info['status']:<15} {status_info['branch']:<15}"

        print(line)

    print(f"\nTotal: {len(workflows)} workflow(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
