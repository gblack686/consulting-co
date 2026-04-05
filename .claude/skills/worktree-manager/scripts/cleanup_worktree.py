#!/usr/bin/env python3
"""
Cleanup (remove) a git worktree.

Usage:
    python cleanup_worktree.py feature-name
    python cleanup_worktree.py feature-name --keep-branch
"""

import argparse
import sys
from worktree_ops import cleanup_worktree, list_worktrees


def main():
    parser = argparse.ArgumentParser(description="Cleanup a git worktree")
    parser.add_argument("name", help="Name of the worktree to cleanup")
    parser.add_argument("--keep-branch", action="store_true", help="Keep the branch after removing worktree")
    parser.add_argument("--all", action="store_true", help="Cleanup all ADW worktrees")

    args = parser.parse_args()

    if args.all:
        # Cleanup all ADW worktrees
        worktrees = list_worktrees()
        adw_wts = [wt for wt in worktrees if wt.name.startswith("adw-")]

        if not adw_wts:
            print("No ADW worktrees to cleanup")
            return 0

        print(f"\n{'='*60}")
        print(f"Cleaning up {len(adw_wts)} ADW worktrees")
        print(f"{'='*60}\n")

        for wt in adw_wts:
            name = wt.name.replace("adw-", "")
            print(f"Cleaning up: {wt.name}...")
            result = cleanup_worktree(name)
            if result.success:
                print(f"  [OK] {result.message}")
            else:
                print(f"  [FAIL] {result.message}")

        print(f"\n{'='*60}")
        return 0

    # Verify worktree exists
    worktrees = list_worktrees()
    matching = [wt for wt in worktrees if args.name in wt.name or args.name in wt.branch]

    if not matching:
        print(f"\n[WARNING] No worktree found matching '{args.name}'")
        print(f"It may have already been cleaned up.")
        return 0

    print(f"\n{'='*60}")
    print(f"Cleaning Up Worktree")
    print(f"{'='*60}")
    print(f"Name: {args.name}")
    print(f"Delete branch: {'No' if args.keep_branch else 'Yes'}")
    print(f"{'='*60}\n")

    result = cleanup_worktree(args.name)

    if result.success:
        print(f"[SUCCESS] {result.message}")
        return 0
    else:
        print(f"[FAILED] {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
