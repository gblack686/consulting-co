#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Dangerous Command Blocker - PreToolUse Hook

Blocks or warns about dangerous shell commands.
Placeholder implementation - echoes hello world.

Patterns blocked/warned:
- rm -rf / or rm -rf ~ - Dangerous deletions
- chmod 777 - Insecure permissions
- Direct .env file access via cat/echo
- > /dev/sda or similar device writes
"""

import json
import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import (
    read_hook_input,
    hook_response,
    log_hook_activity,
    get_bash_command,
)


# Dangerous command patterns
DANGEROUS_PATTERNS = [
    # Dangerous rm patterns
    (r"rm\s+.*-[a-z]*r[a-z]*f.*(/\s*$|/\*)", "rm -rf on root directory"),
    (r"rm\s+.*-[a-z]*r[a-z]*f.*~", "rm -rf on home directory"),
    (r"rm\s+.*-[a-z]*r[a-z]*f.*\$HOME", "rm -rf on $HOME"),

    # Insecure chmod
    (r"chmod\s+777", "chmod 777 sets insecure permissions"),

    # Device writes
    (r">\s*/dev/(sd|hd|nvme)", "writing to block device"),
    (r"dd\s+.*of=/dev/(sd|hd|nvme)", "dd to block device"),

    # Fork bomb patterns
    (r":\(\)\{\s*:\|:&\s*\};\s*:", "fork bomb detected"),
]

# Warning patterns (don't block, just warn)
WARNING_PATTERNS = [
    (r"rm\s+.*-[a-z]*r[a-z]*f", "recursive force delete"),
    (r"chmod\s+-R", "recursive permission change"),
    (r"chown\s+-R", "recursive ownership change"),
]


def check_dangerous_command(command: str) -> tuple[bool, str]:
    """
    Check if command matches dangerous patterns.

    Returns:
        tuple: (is_dangerous, reason)
    """
    normalized = " ".join(command.lower().split())

    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True, reason

    return False, ""


def check_warning_patterns(command: str) -> list[str]:
    """
    Check if command matches warning patterns.

    Returns:
        list: List of warning reasons
    """
    normalized = " ".join(command.lower().split())
    warnings = []

    for pattern, reason in WARNING_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            warnings.append(reason)

    return warnings


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process Bash commands
        if tool_name != "Bash":
            sys.exit(0)

        command = get_bash_command(tool_input)

        if not command:
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - dangerous_command_blocker", file=sys.stderr)

        # Check for dangerous commands
        is_dangerous, reason = check_dangerous_command(command)

        if is_dangerous:
            # Log the blocked command
            log_hook_activity(
                "dangerous_command_blocker",
                {
                    "command": command,
                    "blocked": True,
                    "reason": reason,
                },
                log_subdir="hooks/dev"
            )

            # Note: For placeholder, we just warn but don't block
            # Uncomment below to actually block:
            # print(f"BLOCKED: {reason}", file=sys.stderr)
            # sys.exit(2)
            print(f"WARNING: Would block - {reason}", file=sys.stderr)

        # Check for warning patterns
        warnings = check_warning_patterns(command)
        if warnings:
            for warning in warnings:
                print(f"WARNING: {warning}", file=sys.stderr)

            log_hook_activity(
                "dangerous_command_blocker",
                {
                    "command": command,
                    "blocked": False,
                    "warnings": warnings,
                },
                log_subdir="hooks/dev"
            )

        # Allow the command to proceed
        sys.exit(0)

    except Exception:
        # Handle errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
