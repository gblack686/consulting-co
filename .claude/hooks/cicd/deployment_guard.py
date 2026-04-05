#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Deployment Guard — PreToolUse Hook (Bash)

Blocks destructive deployment commands without confirmation.
Focused on CI/CD and infrastructure teardown patterns.

Patterns:
  BLOCK: cdk destroy, terraform destroy, force push to main/master
  ASK:   service scale to zero, remote branch deletion, docker prune

Exit codes:
  0 — Allow
  2 — Block
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity, get_bash_command


# Deployment-specific patterns (complementary to security/dangerous_command_blocker)
DEPLOYMENT_BLOCK_PATTERNS = [
    (r"cdk\s+destroy", "CDK destroy — infrastructure teardown"),
    (r"terraform\s+destroy", "Terraform destroy — infrastructure teardown"),
    (r"pulumi\s+destroy", "Pulumi destroy — infrastructure teardown"),
    (r"git\s+push\s+.*--force\s+.*(?:main|master)", "Force push to protected branch"),
    (r"git\s+push\s+-f\s+.*(?:main|master)", "Force push to protected branch"),
    (r"aws\s+cloudformation\s+delete-stack", "CloudFormation stack deletion"),
    (r"serverless\s+remove", "Serverless Framework removal"),
]

DEPLOYMENT_ASK_PATTERNS = [
    (r"aws\s+ecs\s+update-service.*--desired-count\s+0", "ECS service scale to zero"),
    (r"git\s+push.*--delete", "Remote branch deletion"),
    (r"docker\s+system\s+prune", "Docker system prune"),
    (r"npm\s+publish", "Publishing to npm registry"),
    (r"pip\s+.*upload", "Uploading to PyPI"),
    (r"gh\s+release\s+create", "Creating GitHub release"),
    (r"aws\s+deploy", "AWS deployment command"),
    (r"gcloud\s+.*deploy", "GCP deployment command"),
]


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name != "Bash":
            sys.exit(0)

        command = get_bash_command(tool_input)
        if not command:
            sys.exit(0)

        normalized = " ".join(command.split())

        # Check block patterns
        for pattern, reason in DEPLOYMENT_BLOCK_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                log_hook_activity(
                    "deployment_guard",
                    {
                        "command": command,
                        "action": "block",
                        "reason": reason,
                    },
                    log_subdir="hooks/cicd",
                )
                print(
                    f"DEPLOYMENT BLOCKED: {reason}\n"
                    f"Command: {command[:100]}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Check warning patterns
        for pattern, reason in DEPLOYMENT_ASK_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                log_hook_activity(
                    "deployment_guard",
                    {
                        "command": command,
                        "action": "warn",
                        "reason": reason,
                    },
                    log_subdir="hooks/cicd",
                )
                print(
                    f"DEPLOYMENT WARNING: {reason}\n"
                    f"Command: {command[:100]}",
                    file=sys.stderr,
                )

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
