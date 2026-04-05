#!/usr/bin/env python3
"""
Auto-route ADW based on task complexity.

Usage:
    python auto_route.py "task description"
    python auto_route.py "task description" --force local
    python auto_route.py "task description" --force github
"""

import argparse
import sys
from adw_ops import auto_route, estimate_complexity


def main():
    parser = argparse.ArgumentParser(description="Auto-route ADW based on complexity")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--force", choices=["local", "github"], help="Force execution mode")
    parser.add_argument("--dry-run", action="store_true", help="Show routing decision without executing")
    parser.add_argument("--working-dir", help="Working directory")

    args = parser.parse_args()

    if args.dry_run:
        # Just show the estimate
        estimate = estimate_complexity(args.task)
        print(f"\n{'='*60}")
        print(f"ADW Routing Analysis (Dry Run)")
        print(f"{'='*60}")
        print(f"Task: {args.task}")
        print(f"Estimated tokens: {estimate.estimated_tokens}")
        print(f"Files touched: {estimate.files_touched}")
        print(f"Complexity: {estimate.complexity_level}")
        print(f"Recommended mode: {estimate.recommended_mode.value}")
        print(f"Reasoning: {estimate.reasoning}")
        print(f"{'='*60}")

        if estimate.recommended_mode.value == "local":
            print(f"\nWould execute: LOCAL HAIKU (~$0.005)")
        else:
            print(f"\nWould execute: GITHUB ACTIONS OPUS ($0.00)")
        return 0

    # Execute the routing
    result = auto_route(args.task, args.working_dir, args.force)

    if result.success:
        print(f"\n[SUCCESS] ADW dispatched via {result.mode.value}")
        print(f"Message: {result.message}")
        if result.workflow_run_url:
            print(f"Workflow URL: {result.workflow_run_url}")
        return 0
    else:
        print(f"\n[FAILED] ADW dispatch failed")
        print(f"Mode: {result.mode.value}")
        print(f"Error: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
