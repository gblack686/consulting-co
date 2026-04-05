#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
AWS Post Command - PostToolUse Hook

Logs AWS CLI command results after execution.
Placeholder implementation - echoes hello world.

Commands logged:
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
    log_hook_activity,
    get_bash_command,
    is_aws_command,
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

        # Only process AWS commands
        if not is_aws_command(command):
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - aws_post_command", file=sys.stderr)

        # Log the AWS command result
        log_hook_activity(
            "aws_post_command",
            {
                "command": command,
                "tool_name": tool_name,
                "result_length": len(str(tool_result)),
            },
            log_subdir="hooks/aws"
        )

        sys.exit(0)

    except Exception:
        # Handle errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
