#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Git Commit Watcher - PreToolUse Hook

Watches and logs git commit/push commands before execution.
Placeholder implementation - echoes hello world.

Commands watched:
- git commit - Commit operations
- git push - Push operations (especially --force)
- git rebase - Rebase operations
- git merge - Merge operations
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import (
    read_hook_input,
    log_hook_activity,
    get_bash_command,
    is_git_command,
    GIT_COMMIT_PATTERNS,
    GIT_DANGEROUS_PATTERNS,
    contains_pattern,
)


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process Bash commands
        if tool_name != "Bash":
            sys.exit(0)

        command = get_bash_command(tool_input)

        # Only process git commit/push related commands
        if not (is_git_command(command) and contains_pattern(command, GIT_COMMIT_PATTERNS)):
            sys.exit(0)

        # Check for dangerous patterns
        is_dangerous = contains_pattern(command, GIT_DANGEROUS_PATTERNS)

        # Placeholder: echo hello world
        print("hello world - git_commit_watcher", file=sys.stderr)
        if is_dangerous:
            print("WARNING: Dangerous git operation detected!", file=sys.stderr)

        # Log the git commit command
        log_hook_activity(
            "git_commit_watcher",
            {
                "command": command,
                "tool_name": tool_name,
                "is_dangerous": is_dangerous,
            },
            log_subdir="hooks/git"
        )

        # Allow the command to proceed
        sys.exit(0)

    except Exception:
        # Handle errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
