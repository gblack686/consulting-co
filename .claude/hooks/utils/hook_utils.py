#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Shared utilities for Claude Code hooks.

Provides common functions for:
- Reading hook input from stdin
- Generating hook responses
- Logging hook activity
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


def read_hook_input() -> dict:
    """
    Read and parse JSON input from stdin.

    Returns:
        dict: Parsed hook input data containing tool_name, tool_input, etc.
    """
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def hook_response(
    allow: bool = True,
    message: Optional[str] = None,
    reason: Optional[str] = None
) -> None:
    """
    Generate appropriate hook response and exit.

    Args:
        allow: If True, allow the tool call (exit 0). If False, block it (exit 2).
        message: Optional message to display to the user.
        reason: Optional reason for blocking (only used when allow=False).
    """
    if message:
        print(message, file=sys.stderr)

    if not allow and reason:
        print(f"Reason: {reason}", file=sys.stderr)

    sys.exit(0 if allow else 2)


def log_hook_activity(
    hook_name: str,
    data: dict,
    log_subdir: Optional[str] = None
) -> None:
    """
    Log hook activity to a JSON file.

    Args:
        hook_name: Name of the hook (used for log filename).
        data: Data to log.
        log_subdir: Optional subdirectory within logs/.
    """
    log_dir = Path.cwd() / "logs"
    if log_subdir:
        log_dir = log_dir / log_subdir
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / f"{hook_name}.json"

    # Add timestamp to data
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        **data
    }

    # Read existing log or initialize
    if log_path.exists():
        try:
            with open(log_path, "r") as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Append and write
    log_data.append(log_entry)

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)


def get_bash_command(tool_input: dict) -> str:
    """
    Extract bash command from tool input.

    Args:
        tool_input: The tool_input dictionary from hook data.

    Returns:
        str: The bash command, or empty string if not found.
    """
    return tool_input.get("command", "")


def contains_pattern(text: str, patterns: list) -> bool:
    """
    Check if text contains any of the specified patterns.

    Args:
        text: Text to search.
        patterns: List of substrings to look for.

    Returns:
        bool: True if any pattern is found.
    """
    text_lower = text.lower()
    return any(pattern.lower() in text_lower for pattern in patterns)


def is_aws_command(command: str) -> bool:
    """Check if command is an AWS CLI command."""
    return "aws " in command or command.startswith("aws ")


def is_git_command(command: str) -> bool:
    """Check if command is a git command."""
    return "git " in command or command.startswith("git ")


# AWS command categories
AWS_S3_PATTERNS = ["aws s3", "aws s3api"]
AWS_STS_PATTERNS = ["aws sts"]
AWS_SECRETS_PATTERNS = ["aws secretsmanager"]
AWS_BEDROCK_PATTERNS = ["aws bedrock"]
AWS_COST_PATTERNS = ["aws ce", "aws cost-explorer"]
AWS_CDK_PATTERNS = ["aws cdk", "cdk deploy", "cdk diff", "cdk synth"]

# Git command categories
GIT_WORKTREE_PATTERNS = ["git worktree"]
GIT_BRANCH_PATTERNS = ["git checkout -b", "git switch -c", "git branch"]
GIT_COMMIT_PATTERNS = ["git commit", "git push", "git rebase", "git merge"]
GIT_DANGEROUS_PATTERNS = ["--force", "-f", "push --force", "push -f"]
