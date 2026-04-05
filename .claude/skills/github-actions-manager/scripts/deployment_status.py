#!/usr/bin/env python3
"""
Show deployment status across environments.

Looks for workflows with 'deploy' in the name and shows
the latest deployment status for each environment.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from gh_actions_ops import list_workflows, list_runs, format_status


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        "default_repo": "gblack686/consulting-co",
        "environments": ["production", "staging", "dev"],
        "deploy_workflow_patterns": ["deploy", "release", "publish"]
    }


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


def detect_environment(run: dict, environments: list) -> str:
    """Try to detect which environment a run deployed to."""
    title = run.get("displayTitle", "").lower()
    branch = run.get("headBranch", "").lower()

    for env in environments:
        if env.lower() in title or env.lower() in branch:
            return env

    # Default mappings
    if "main" in branch or "master" in branch:
        return "production"
    elif "staging" in branch or "stage" in branch:
        return "staging"
    elif "dev" in branch or "develop" in branch:
        return "dev"

    return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Show deployment status")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")
    environments = config.get("environments", ["production", "staging", "dev"])
    patterns = config.get("deploy_workflow_patterns", ["deploy", "release"])

    print(f"Deployment Status for {repo}\n")

    # Find deploy workflows
    success, workflows = list_workflows(repo)
    if not success:
        print(f"Error listing workflows: {workflows}")
        return 1

    deploy_workflows = []
    for wf in workflows:
        name = wf.get("name", "").lower()
        if any(p in name for p in patterns):
            deploy_workflows.append(wf)

    if not deploy_workflows:
        print("No deployment workflows found.")
        print(f"\nLooking for workflows containing: {', '.join(patterns)}")
        print("\nAll workflows:")
        for wf in workflows:
            print(f"  - {wf.get('name')}")
        return 0

    # Get recent deploy runs
    deployments = {}

    for wf in deploy_workflows:
        wf_path = Path(wf.get("path", "")).name
        success, runs = list_runs(repo, workflow=wf_path, limit=20)

        if success:
            for run in runs:
                env = detect_environment(run, environments)
                if env not in deployments or run.get("createdAt") > deployments[env].get("createdAt", ""):
                    deployments[env] = {
                        "workflow": wf.get("name"),
                        "status": run.get("status"),
                        "conclusion": run.get("conclusion"),
                        "branch": run.get("headBranch"),
                        "title": run.get("displayTitle"),
                        "createdAt": run.get("createdAt"),
                        "run_id": run.get("databaseId"),
                        "url": run.get("url")
                    }

    if args.json:
        print(json.dumps(deployments, indent=2))
        return 0

    # Display table
    print(f"{'Environment':<15} {'Status':<15} {'Branch':<15} {'Last Deploy':<12} {'Run ID':<10}")
    print("-" * 67)

    for env in environments:
        if env in deployments:
            d = deployments[env]
            status = format_status(d.get("status"), d.get("conclusion"))
            branch = d.get("branch", "")[:13]
            time_ago = format_time_ago(d.get("createdAt", ""))
            run_id = str(d.get("run_id", ""))

            print(f"{env:<15} {status:<15} {branch:<15} {time_ago:<12} {run_id:<10}")
        else:
            print(f"{env:<15} {'⚪ no deploys':<15} {'-':<15} {'-':<12} {'-':<10}")

    # Additional info
    if deployments:
        print(f"\nDeploy workflows found: {', '.join(wf.get('name') for wf in deploy_workflows)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
