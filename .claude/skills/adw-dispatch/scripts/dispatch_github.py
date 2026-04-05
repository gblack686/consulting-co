#!/usr/bin/env python3
"""
Dispatch ADW to GitHub Actions for Opus execution.

Usage:
    python dispatch_github.py "task description"
    python dispatch_github.py "task description" --working-dir /path/to/dir
"""

import argparse
import sys
from adw_ops import dispatch_github


def main():
    parser = argparse.ArgumentParser(description="Dispatch ADW to GitHub Actions Opus")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--working-dir", help="Working directory context")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"Dispatching to GITHUB ACTIONS (Opus)")
    print(f"{'='*60}")
    print(f"Task: {args.task}")
    print(f"Model: claude-opus-4-5 (via Max subscription)")
    print(f"Est. Cost: $0.00 (free with Max)")
    print(f"{'='*60}\n")

    result = dispatch_github(args.task, args.working_dir)

    if result.success:
        print(f"\n[SUCCESS] GitHub Actions workflow triggered")
        print(f"Message: {result.message}")
        if result.workflow_run_url:
            print(f"Monitor at: {result.workflow_run_url}")
        return 0
    else:
        print(f"\n[FAILED] GitHub Actions trigger failed")
        print(f"Error: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
