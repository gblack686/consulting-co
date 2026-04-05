#!/usr/bin/env python3
"""
GitHub Operations Module for Claude Code Issue Management

Core functions for creating, updating, and managing GitHub issues via gh CLI.
Based on TAC's adw_modules/github.py pattern.
"""

import json
import subprocess
import sys
from typing import Optional

# Bot identifier to prevent loops (matches TAC pattern)
CLAUDE_CODE_BOT_IDENTIFIER = "[CLAUDE-CODE-FIX]"


def run_gh_command(args: list, capture_output: bool = True) -> tuple[int, str, str]:
    """
    Run a gh CLI command and return results.

    Args:
        args: List of arguments for gh command
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except FileNotFoundError:
        return 1, "", "gh CLI not found. Install from https://cli.github.com/"
    except Exception as e:
        return 1, "", str(e)


def check_auth() -> tuple[bool, str]:
    """
    Check if gh CLI is authenticated.

    Returns:
        Tuple of (is_authenticated, message)
    """
    code, stdout, stderr = run_gh_command(["auth", "status"])
    if code == 0:
        return True, stdout
    return False, stderr


def create_issue(
    repo: str,
    title: str,
    body: str,
    labels: list = None,
    assignees: list = None
) -> tuple[bool, str]:
    """
    Create a GitHub issue.

    Args:
        repo: Repository in format "owner/repo"
        title: Issue title
        body: Issue body (markdown)
        labels: Optional list of labels
        assignees: Optional list of assignees

    Returns:
        Tuple of (success, issue_url_or_error)
    """
    args = [
        "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body
    ]

    if labels:
        for label in labels:
            args.extend(["--label", label])

    if assignees:
        for assignee in assignees:
            args.extend(["--assignee", assignee])

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        # stdout contains the issue URL
        return True, stdout
    return False, stderr


def update_issue(
    repo: str,
    issue_number: int,
    title: str = None,
    body: str = None,
    state: str = None,
    add_labels: list = None,
    remove_labels: list = None,
    add_assignees: list = None,
    remove_assignees: list = None
) -> tuple[bool, str]:
    """
    Update an existing GitHub issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number to update
        title: New title (optional)
        body: New body (optional)
        state: New state - "open" or "closed" (optional)
        add_labels: Labels to add (optional)
        remove_labels: Labels to remove (optional)
        add_assignees: Assignees to add (optional)
        remove_assignees: Assignees to remove (optional)

    Returns:
        Tuple of (success, message)
    """
    args = ["issue", "edit", str(issue_number), "--repo", repo]

    if title:
        args.extend(["--title", title])
    if body:
        args.extend(["--body", body])
    if add_labels:
        for label in add_labels:
            args.extend(["--add-label", label])
    if remove_labels:
        for label in remove_labels:
            args.extend(["--remove-label", label])
    if add_assignees:
        for assignee in add_assignees:
            args.extend(["--add-assignee", assignee])
    if remove_assignees:
        for assignee in remove_assignees:
            args.extend(["--remove-assignee", assignee])

    code, stdout, stderr = run_gh_command(args)

    # Handle state change separately (close/reopen)
    if state and code == 0:
        if state == "closed":
            state_code, _, state_err = run_gh_command([
                "issue", "close", str(issue_number), "--repo", repo
            ])
            if state_code != 0:
                return False, f"Failed to close issue: {state_err}"
        elif state == "open":
            state_code, _, state_err = run_gh_command([
                "issue", "reopen", str(issue_number), "--repo", repo
            ])
            if state_code != 0:
                return False, f"Failed to reopen issue: {state_err}"

    if code == 0:
        return True, f"Issue #{issue_number} updated successfully"
    return False, stderr


def close_issue(
    repo: str,
    issue_number: int,
    comment: str = None,
    reason: str = None
) -> tuple[bool, str]:
    """
    Close a GitHub issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number to close
        comment: Optional closing comment
        reason: Optional close reason ("completed" or "not_planned")

    Returns:
        Tuple of (success, message)
    """
    # Add comment first if provided
    if comment:
        add_issue_comment(repo, issue_number, comment)

    args = ["issue", "close", str(issue_number), "--repo", repo]

    if reason:
        args.extend(["--reason", reason])

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        return True, f"Issue #{issue_number} closed"
    return False, stderr


def add_issue_comment(
    repo: str,
    issue_number: int,
    comment: str,
    add_bot_identifier: bool = True
) -> tuple[bool, str]:
    """
    Add a comment to an issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number
        comment: Comment text
        add_bot_identifier: Whether to add bot identifier to comment

    Returns:
        Tuple of (success, message)
    """
    if add_bot_identifier:
        comment = f"{CLAUDE_CODE_BOT_IDENTIFIER}\n\n{comment}"

    args = [
        "issue", "comment", str(issue_number),
        "--repo", repo,
        "--body", comment
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        return True, f"Comment added to issue #{issue_number}"
    return False, stderr


def list_issues(
    repo: str,
    state: str = "open",
    labels: list = None,
    limit: int = 30,
    json_output: bool = True
) -> tuple[bool, list | str]:
    """
    List issues in a repository.

    Args:
        repo: Repository in format "owner/repo"
        state: Filter by state - "open", "closed", or "all"
        labels: Optional list of labels to filter by
        limit: Maximum number of issues to return
        json_output: Return as parsed JSON list

    Returns:
        Tuple of (success, issues_list_or_error)
    """
    args = [
        "issue", "list",
        "--repo", repo,
        "--state", state,
        "--limit", str(limit)
    ]

    if labels:
        for label in labels:
            args.extend(["--label", label])

    if json_output:
        args.extend(["--json", "number,title,state,labels,createdAt,url,body"])

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        if json_output:
            try:
                return True, json.loads(stdout) if stdout else []
            except json.JSONDecodeError:
                return True, []
        return True, stdout
    return False, stderr


def search_issues(
    repo: str,
    query: str,
    state: str = "all",
    limit: int = 20
) -> tuple[bool, list | str]:
    """
    Search for issues in a repository.

    Args:
        repo: Repository in format "owner/repo"
        query: Search query
        state: Filter by state - "open", "closed", or "all"
        limit: Maximum results

    Returns:
        Tuple of (success, issues_list_or_error)
    """
    # Build search query
    search_query = f"repo:{repo} is:issue {query}"
    if state != "all":
        search_query += f" state:{state}"

    args = [
        "search", "issues",
        "--limit", str(limit),
        "--json", "number,title,state,labels,createdAt,url,body",
        search_query
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        try:
            return True, json.loads(stdout) if stdout else []
        except json.JSONDecodeError:
            return True, []
    return False, stderr


def get_issue(repo: str, issue_number: int) -> tuple[bool, dict | str]:
    """
    Get details of a specific issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number

    Returns:
        Tuple of (success, issue_dict_or_error)
    """
    args = [
        "issue", "view", str(issue_number),
        "--repo", repo,
        "--json", "number,title,state,labels,body,createdAt,closedAt,url,author,assignees,comments"
    ]

    code, stdout, stderr = run_gh_command(args)

    if code == 0:
        try:
            return True, json.loads(stdout)
        except json.JSONDecodeError:
            return False, "Failed to parse issue data"
    return False, stderr


def find_duplicate_issues(
    repo: str,
    title: str,
    labels: list = None,
    similarity_threshold: float = 0.7
) -> list:
    """
    Find potentially duplicate issues based on title similarity.

    Args:
        repo: Repository in format "owner/repo"
        title: Title to check against
        labels: Optional labels to filter by
        similarity_threshold: Minimum similarity ratio (0-1)

    Returns:
        List of potentially duplicate issues
    """
    # Get open issues with matching labels
    success, issues = list_issues(repo, state="open", labels=labels, limit=50)

    if not success or not issues:
        return []

    duplicates = []
    title_words = set(title.lower().split())

    for issue in issues:
        issue_title_words = set(issue.get("title", "").lower().split())

        # Simple word overlap similarity
        if title_words and issue_title_words:
            intersection = len(title_words & issue_title_words)
            union = len(title_words | issue_title_words)
            similarity = intersection / union if union > 0 else 0

            if similarity >= similarity_threshold:
                duplicates.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "url": issue.get("url"),
                    "similarity": round(similarity, 2)
                })

    return sorted(duplicates, key=lambda x: x["similarity"], reverse=True)


def create_issue_body(
    fix_type: str,
    description: str,
    files_changed: list = None,
    confidence: float = 0,
    session_id: str = None
) -> str:
    """
    Generate a formatted issue body for a detected fix.

    Args:
        fix_type: Type of fix (bug_fix, security_fix, etc.)
        description: Description of the fix
        files_changed: List of files that were changed
        confidence: Confidence score (0-1)
        session_id: Optional session ID for reference

    Returns:
        Formatted markdown body
    """
    body = f"""## Fix Applied During Claude Code Session

**Type**: {fix_type.replace('_', ' ').title()}
**Confidence**: {int(confidence * 100)}%

### Description
{description}

"""

    if files_changed:
        body += "### Files Changed\n"
        for file in files_changed:
            body += f"- `{file}`\n"
        body += "\n"

    if session_id:
        body += f"**Session ID**: `{session_id}`\n\n"

    body += "---\n*Auto-generated by Claude Code GitHub Issue Hook*"

    return body


if __name__ == "__main__":
    # Test basic functionality
    auth_ok, auth_msg = check_auth()
    print(f"Auth status: {'OK' if auth_ok else 'FAILED'}")
    print(auth_msg)

    if auth_ok:
        # Test listing issues
        success, issues = list_issues("gblack686/consulting-co", limit=5)
        if success:
            print(f"\nFound {len(issues)} issues")
            for issue in issues[:3]:
                print(f"  #{issue['number']}: {issue['title']}")
        else:
            print(f"Failed to list issues: {issues}")
