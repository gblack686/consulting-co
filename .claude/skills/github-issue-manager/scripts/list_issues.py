#!/usr/bin/env python3
"""
List and filter GitHub issues for the GitHub Issue Manager skill.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from github_ops import list_issues, search_issues, get_issue


def load_config() -> dict:
    """Load configuration from settings.json."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"default_repo": "gblack686/consulting-co"}


def format_issue(issue: dict, verbose: bool = False) -> str:
    """Format a single issue for display."""
    labels = ", ".join(l["name"] for l in issue.get("labels", [])) or "none"
    created = issue.get("createdAt", "")[:10]  # Just the date

    if verbose:
        body_preview = issue.get("body", "")[:200]
        if len(issue.get("body", "")) > 200:
            body_preview += "..."
        return f"""
#{issue['number']} - {issue['title']}
  State: {issue['state']} | Labels: {labels} | Created: {created}
  URL: {issue['url']}
  {body_preview}
"""
    else:
        title = issue['title'][:60]
        if len(issue['title']) > 60:
            title += "..."
        return f"#{issue['number']:4d} [{issue['state']:6s}] {title} ({labels})"


def main():
    parser = argparse.ArgumentParser(description="List GitHub issues")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--state", "-s", default="open",
                        choices=["open", "closed", "all"],
                        help="Filter by state")
    parser.add_argument("--labels", "-l", nargs="+", help="Filter by labels")
    parser.add_argument("--search", "-q", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=20,
                        help="Maximum issues to return")
    parser.add_argument("--issue", "-i", type=int,
                        help="Get details of a specific issue")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()

    # Load config
    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")

    # Get specific issue
    if args.issue:
        success, result = get_issue(repo, args.issue)
        if success:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\nIssue #{result['number']}: {result['title']}")
                print("-" * 50)
                print(f"State: {result['state']}")
                print(f"URL: {result['url']}")
                labels = ", ".join(l["name"] for l in result.get("labels", []))
                print(f"Labels: {labels or 'none'}")
                print(f"Created: {result.get('createdAt', 'unknown')}")
                if result.get("closedAt"):
                    print(f"Closed: {result['closedAt']}")
                print(f"\n{result.get('body', 'No body')}")
        else:
            print(f"Error: {result}")
            return 1
        return 0

    # Search or list issues
    if args.search:
        print(f"Searching '{args.search}' in {repo}...")
        success, issues = search_issues(repo, args.search, args.state, args.limit)
    else:
        print(f"Listing {args.state} issues from {repo}...")
        success, issues = list_issues(repo, args.state, args.labels, args.limit)

    if not success:
        print(f"Error: {issues}")
        return 1

    if args.json:
        print(json.dumps(issues, indent=2))
        return 0

    if not issues:
        print("No issues found.")
        return 0

    print(f"\nFound {len(issues)} issues:\n")
    for issue in issues:
        print(format_issue(issue, args.verbose))

    # Summary stats
    if len(issues) > 5:
        open_count = sum(1 for i in issues if i.get("state") == "OPEN")
        closed_count = len(issues) - open_count
        print(f"\nSummary: {open_count} open, {closed_count} closed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
