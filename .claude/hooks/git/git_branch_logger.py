#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Git Branch Logger - PostToolUse Hook

Logs git branch operation results after execution.
Placeholder implementation - echoes hello world.

Commands logged:
- git checkout -b - Branch creation
- git switch -c - Branch creation (new syntax)
- git branch - Branch operations
- git worktree - Worktree operations
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
    GIT_BRANCH_PATTERNS,
    GIT_WORKTREE_PATTERNS,
    contains_pattern,
)


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_result = input_data.get("tool_result", "")

        # Only process Bash commands
        if tool_name != "Bash":
            sys.exit(0)

        command = get_bash_command(tool_input)

        # Only process git branch/worktree commands
        patterns = GIT_BRANCH_PATTERNS + GIT_WORKTREE_PATTERNS
        if not (is_git_command(command) and contains_pattern(command, patterns)):
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - git_branch_logger", file=sys.stderr)

        # Log the git branch operation result
        log_hook_activity(
            "git_branch_logger",
            {
                "command": command,
                "tool_name": tool_name,
                "result_length": len(str(tool_result)),
            },
            log_subdir="hooks/git"
        )

        sys.exit(0)

    except Exception:
        # Handle errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
