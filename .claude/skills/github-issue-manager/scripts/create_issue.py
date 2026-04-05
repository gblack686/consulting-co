#!/usr/bin/env python3
"""
Manual issue creation script for the GitHub Issue Manager skill.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from github_ops import create_issue, create_issue_body, find_duplicate_issues


def load_config() -> dict:
    """Load configuration from settings.json."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        "default_repo": "gblack686/consulting-co",
        "default_labels": ["claude-code-fix"]
    }


def main():
    parser = argparse.ArgumentParser(description="Create a GitHub issue manually")
    parser.add_argument("--title", "-t", required=True, help="Issue title")
    parser.add_argument("--body", "-b", help="Issue body (markdown)")
    parser.add_argument("--type", "-T", default="bug_fix",
                        choices=["bug_fix", "security_fix", "enhancement", "documentation"],
                        help="Fix type for formatted body")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--labels", "-l", nargs="+", help="Labels to add")
    parser.add_argument("--files", "-f", nargs="+", help="Files changed")
    parser.add_argument("--check-duplicates", "-c", action="store_true",
                        help="Check for duplicate issues first")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be created without creating")

    args = parser.parse_args()

    # Load config
    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")
    labels = args.labels or config.get("default_labels", [])

    print(f"Repository: {repo}")
    print(f"Title: {args.title}")
    print(f"Labels: {', '.join(labels) if labels else 'none'}")

    # Check for duplicates if requested
    if args.check_duplicates:
        print("\nChecking for duplicate issues...")
        duplicates = find_duplicate_issues(repo, args.title, labels)
        if duplicates:
            print(f"Found {len(duplicates)} potentially similar issues:")
            for dup in duplicates[:3]:
                print(f"  #{dup['number']} ({dup['similarity']*100:.0f}% similar): {dup['title']}")
            if not args.dry_run:
                response = input("\nCreate issue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return 0
        else:
            print("No duplicates found.")

    # Build body
    if args.body:
        body = args.body
    else:
        body = create_issue_body(
            fix_type=args.type,
            description=args.title,  # Use title as description if no body provided
            files_changed=args.files,
            confidence=0.9
        )

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print(f"Would create issue in {repo}:")
        print(f"Title: {args.title}")
        print(f"Labels: {labels}")
        print(f"Body:\n{body}")
        return 0

    # Create the issue
    print("\nCreating issue...")
    success, result = create_issue(repo, args.title, body, labels)

    if success:
        print(f"[SUCCESS] Issue created: {result}")
        return 0
    else:
        print(f"[ERROR] Failed to create issue: {result}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
