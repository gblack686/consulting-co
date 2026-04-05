#!/usr/bin/env python3
"""
List all git worktrees.

Usage:
    python list_worktrees.py
    python list_worktrees.py --json
"""

import argparse
import json
import sys
from worktree_ops import list_worktrees


def main():
    parser = argparse.ArgumentParser(description="List all git worktrees")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--adw-only", action="store_true", help="Only show ADW worktrees")

    args = parser.parse_args()

    worktrees = list_worktrees()

    if args.adw_only:
        worktrees = [wt for wt in worktrees if wt.name.startswith("adw-")]

    if args.json:
        output = [
            {
                "name": wt.name,
                "path": wt.path,
                "branch": wt.branch,
                "commit": wt.commit,
                "is_main": wt.is_main
            }
            for wt in worktrees
        ]
        print(json.dumps(output, indent=2))
        return 0

    print(f"\n{'='*60}")
    print(f"Git Worktrees")
    print(f"{'='*60}")

    if not worktrees:
        print("\nNo worktrees found")
        return 0

    main_wt = [wt for wt in worktrees if wt.is_main]
    adw_wts = [wt for wt in worktrees if wt.name.startswith("adw-")]
    other_wts = [wt for wt in worktrees if not wt.is_main and not wt.name.startswith("adw-")]

    if main_wt:
        print(f"\n MAIN:")
        for wt in main_wt:
            print(f"  {wt.name}")
            print(f"    Path: {wt.path}")
            print(f"    Branch: {wt.branch}")

    if adw_wts:
        print(f"\n ADW WORKTREES ({len(adw_wts)}):")
        for wt in adw_wts:
            print(f"  {wt.name}")
            print(f"    Path: {wt.path}")
            print(f"    Branch: {wt.branch}")
            print(f"    Commit: {wt.commit[:8]}")

    if other_wts:
        print(f"\n OTHER ({len(other_wts)}):")
        for wt in other_wts:
            print(f"  {wt.name}")
            print(f"    Path: {wt.path}")
            print(f"    Branch: {wt.branch}")

    print(f"\n{'='*60}")
    print(f"Total: {len(worktrees)} worktrees ({len(adw_wts)} ADW)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
