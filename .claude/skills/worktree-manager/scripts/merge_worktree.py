#!/usr/bin/env python3
"""
Merge worktree branch to main.

Usage:
    python merge_worktree.py feature-name
    python merge_worktree.py feature-name --keep
"""

import argparse
import sys
from worktree_ops import merge_worktree, list_worktrees


def main():
    parser = argparse.ArgumentParser(description="Merge worktree branch to main")
    parser.add_argument("name", help="Name of the worktree to merge")
    parser.add_argument("--keep", action="store_true", help="Keep worktree after merge")

    args = parser.parse_args()

    # Verify worktree exists
    worktrees = list_worktrees()
    matching = [wt for wt in worktrees if args.name in wt.name or args.name in wt.branch]

    if not matching:
        print(f"\n[ERROR] No worktree found matching '{args.name}'")
        print(f"\nAvailable worktrees:")
        for wt in worktrees:
            if wt.name.startswith("adw-"):
                print(f"  - {wt.name} ({wt.branch})")
        return 1

    print(f"\n{'='*60}")
    print(f"Merging Worktree")
    print(f"{'='*60}")
    print(f"Name: {args.name}")
    print(f"Cleanup after merge: {'No' if args.keep else 'Yes'}")
    print(f"{'='*60}\n")

    result = merge_worktree(args.name, delete_after=not args.keep)

    if result.success:
        print(f"[SUCCESS] {result.message}")
        if not args.keep:
            print(f"\nWorktree and branch have been cleaned up.")
        else:
            print(f"\nWorktree preserved. To cleanup later:")
            print(f"  python cleanup_worktree.py {args.name}")
        return 0
    else:
        print(f"[FAILED] {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        print(f"\nTo resolve merge conflicts:")
        print(f"  1. Resolve conflicts in files")
        print(f"  2. git add <resolved-files>")
        print(f"  3. git commit")
        return 1


if __name__ == "__main__":
    sys.exit(main())
