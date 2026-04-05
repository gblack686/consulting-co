#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
AWS Command Watcher - PreToolUse Hook

Watches and logs AWS CLI commands before execution.
Placeholder implementation - echoes hello world.

Commands watched:
- aws s3 - S3 operations
- aws sts - Identity operations
- aws secretsmanager - Secrets access
- aws bedrock - AI model calls
- aws ce - Cost Explorer queries
- aws cdk - CDK deployments
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import (
    read_hook_input,
    hook_response,
    log_hook_activity,
    get_bash_command,
    is_aws_command,
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

        # Only process AWS commands
        if not is_aws_command(command):
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - aws_command_watcher", file=sys.stderr)

        # Log the AWS command
        log_hook_activity(
            "aws_command_watcher",
            {
                "command": command,
                "tool_name": tool_name,
            },
            log_subdir="hooks/aws"
        )

        # Allow the command to proceed
        sys.exit(0)

    except Exception:
        # Handle errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
