#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
File Change Logger - PostToolUse Hook

Logs file modifications after tool execution.
Placeholder implementation - echoes hello world.

Tools monitored:
- Edit - File edits
- Write - File writes
- MultiEdit - Multiple file edits
- Bash - Commands that may modify files
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import (
    read_hook_input,
    log_hook_activity,
)


# File modification tools
FILE_MODIFICATION_TOOLS = ["Edit", "Write", "MultiEdit"]

# Bash commands that modify files
FILE_MODIFYING_COMMANDS = [
    "touch", "mkdir", "rm", "mv", "cp",
    "echo", "cat", "tee",
    "sed", "awk",
    "chmod", "chown",
]


def is_file_modifying_bash(command: str) -> bool:
    """Check if bash command likely modifies files."""
    command_lower = command.lower()
    return any(cmd in command_lower for cmd in FILE_MODIFYING_COMMANDS)


def extract_file_path(tool_name: str, tool_input: dict) -> str:
    """Extract file path from tool input."""
    if tool_name in ["Edit", "Write", "Read"]:
        return tool_input.get("file_path", "")
    elif tool_name == "MultiEdit":
        # Return first file path from edits
        edits = tool_input.get("edits", [])
        if edits:
            return edits[0].get("file_path", "")
    return ""


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_result = input_data.get("tool_result", "")

        # Check if this is a file modification operation
        is_file_tool = tool_name in FILE_MODIFICATION_TOOLS
        is_bash_file_mod = (
            tool_name == "Bash" and
            is_file_modifying_bash(tool_input.get("command", ""))
        )

        if not (is_file_tool or is_bash_file_mod):
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - file_change_logger", file=sys.stderr)

        # Extract relevant info
        file_path = extract_file_path(tool_name, tool_input)

        # Log the file change
        log_hook_activity(
            "file_change_logger",
            {
                "tool_name": tool_name,
                "file_path": file_path,
                "command": tool_input.get("command", "") if tool_name == "Bash" else "",
                "result_length": len(str(tool_result)),
            },
            log_subdir="hooks/dev"
        )

        sys.exit(0)

    except Exception:
        # Handle errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
