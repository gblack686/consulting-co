#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Git Worktree Watcher - PreToolUse Hook

Watches and logs git worktree commands before execution.
Placeholder implementation - echoes hello world.

Commands watched:
- git worktree add - Create new worktree
- git worktree remove - Remove worktree
- git worktree list - List worktrees
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
    GIT_WORKTREE_PATTERNS,
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

        # Only process git worktree commands
        if not (is_git_command(command) and contains_pattern(command, GIT_WORKTREE_PATTERNS)):
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - git_worktree_watcher", file=sys.stderr)

        # Log the git worktree command
        log_hook_activity(
            "git_worktree_watcher",
            {
                "command": command,
                "tool_name": tool_name,
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
