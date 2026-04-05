#!/usr/bin/env python3
"""
Dispatch ADW to local Haiku execution.

Usage:
    python dispatch_local.py "task description"
    python dispatch_local.py "task description" --working-dir /path/to/dir
"""

import argparse
import sys
from adw_ops import dispatch_local


def main():
    parser = argparse.ArgumentParser(description="Dispatch ADW to local Haiku")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--working-dir", help="Working directory")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"Dispatching to LOCAL HAIKU")
    print(f"{'='*60}")
    print(f"Task: {args.task}")
    print(f"Model: claude-haiku-4-5-20251001")
    print(f"Est. Cost: ~$0.005")
    print(f"{'='*60}\n")

    result = dispatch_local(args.task, args.working_dir)

    if result.success:
        print(f"\n[SUCCESS] Local execution completed")
        print(f"Message: {result.message}")
        return 0
    else:
        print(f"\n[FAILED] Local execution failed")
        print(f"Error: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
