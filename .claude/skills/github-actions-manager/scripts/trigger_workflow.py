#!/usr/bin/env python3
"""
Trigger a GitHub Actions workflow.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gh_actions_ops import trigger_workflow, list_workflows


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"default_repo": "gblack686/consulting-co"}


def main():
    parser = argparse.ArgumentParser(description="Trigger a GitHub Actions workflow")
    parser.add_argument("workflow", nargs="?", help="Workflow filename (e.g., ci.yml)")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--ref", default="main",
                        help="Branch or tag to run on (default: main)")
    parser.add_argument("--input", "-i", action="append", dest="inputs",
                        help="Workflow input in key=value format (can repeat)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available workflows")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be triggered without triggering")

    args = parser.parse_args()

    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")

    # List workflows if requested
    if args.list or not args.workflow:
        print(f"Available workflows in {repo}:\n")
        success, workflows = list_workflows(repo)
        if success and workflows:
            for wf in workflows:
                if wf.get("state") == "active":
                    path = Path(wf.get("path", "")).name
                    print(f"  {path:<30} - {wf.get('name')}")
            print(f"\nUsage: python trigger_workflow.py <workflow.yml> [--input key=value]")
        else:
            print("No workflows found.")
        return 0

    # Parse inputs
    inputs = {}
    if args.inputs:
        for inp in args.inputs:
            if "=" in inp:
                key, value = inp.split("=", 1)
                inputs[key] = value
            else:
                print(f"Invalid input format: {inp} (use key=value)")
                return 1

    # Show what would be triggered
    print(f"Workflow: {args.workflow}")
    print(f"Repository: {repo}")
    print(f"Branch/Ref: {args.ref}")
    if inputs:
        print(f"Inputs:")
        for k, v in inputs.items():
            print(f"  {k}: {v}")

    if args.dry_run:
        print("\n[DRY RUN] Would trigger workflow with above parameters")
        return 0

    # Confirm
    print()
    response = input("Trigger this workflow? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    # Trigger
    success, result = trigger_workflow(repo, args.workflow, args.ref, inputs or None)

    if success:
        print(f"\n✅ {result}")
        print(f"\nView runs: gh run list --repo {repo} --workflow {args.workflow}")
    else:
        print(f"\n❌ Failed: {result}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
