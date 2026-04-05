#!/usr/bin/env python3
"""
Create a new git worktree for isolated ADW work.

Usage:
    python create_worktree.py feature-name
    python create_worktree.py feature-name --from develop
"""

import argparse
import sys
from worktree_ops import create_worktree, list_worktrees


def main():
    parser = argparse.ArgumentParser(description="Create a new git worktree")
    parser.add_argument("name", help="Name for the worktree (will be slugified)")
    parser.add_argument("--from", dest="from_branch", help="Branch to create from")

    args = parser.parse_args()

    # Check if already exists
    existing = [wt for wt in list_worktrees() if args.name in wt.name or args.name in wt.branch]
    if existing:
        print(f"\n[WARNING] Worktree with similar name already exists:")
        for wt in existing:
            print(f"  - {wt.name} ({wt.branch})")
        print(f"\nUse a different name or cleanup the existing worktree first.")
        return 1

    print(f"\n{'='*60}")
    print(f"Creating Worktree")
    print(f"{'='*60}")
    print(f"Name: {args.name}")
    if args.from_branch:
        print(f"From: {args.from_branch}")
    print(f"{'='*60}\n")

    result = create_worktree(args.name, args.from_branch)

    if result.success:
        print(f"[SUCCESS] {result.message}")
        if result.worktree:
            print(f"\nWorktree Details:")
            print(f"  Path: {result.worktree.path}")
            print(f"  Branch: {result.worktree.branch}")
            print(f"\nTo work in this worktree:")
            print(f"  cd {result.worktree.path}")
        return 0
    else:
        print(f"[FAILED] {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
