#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyyaml"]
# ///
"""
Dangerous Command Blocker — PreToolUse Hook (Bash)

Loads patterns from patterns.yaml and blocks/warns on dangerous commands.
Replaces the basic blocker in dev/ with a comprehensive, configurable system.

Exit codes:
  0 — Allow command
  2 — Block command (dangerous pattern matched)
"""

import json
import re
import sys
from pathlib import Path

import yaml

# Add parent directory to path for shared utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity, get_bash_command

# Load patterns from YAML
PATTERNS_FILE = Path(__file__).parent / "patterns.yaml"


def load_patterns() -> dict:
    """Load dangerous patterns from YAML config."""
    if not PATTERNS_FILE.exists():
        return {}
    with open(PATTERNS_FILE, "r") as f:
        return yaml.safe_load(f) or {}


def check_command(command: str, patterns: dict) -> tuple:
    """
    Check command against all pattern categories.

    Returns:
        tuple: (action, reason, category)
        action: "block", "ask", or None
    """
    normalized = " ".join(command.split())

    # Skip path_protection — handled by edit_guard/write_guard
    skip_categories = {"path_protection"}

    for category, rules in patterns.items():
        if category in skip_categories:
            continue
        if not isinstance(rules, list):
            continue

        for rule in rules:
            pattern = rule.get("pattern", "")
            match_type = rule.get("type", "regex")
            action = rule.get("action", "ask")
            reason = rule.get("reason", "Unknown dangerous pattern")

            matched = False
            if match_type == "regex":
                try:
                    matched = bool(re.search(pattern, normalized, re.IGNORECASE))
                except re.error:
                    continue
            elif match_type == "exact":
                matched = pattern.lower() in normalized.lower()

            if matched:
                return action, reason, category

    return None, None, None


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

        patterns = load_patterns()
        action, reason, category = check_command(command, patterns)

        if action == "block":
            log_hook_activity(
                "dangerous_command_blocker",
                {
                    "command": command,
                    "action": "block",
                    "reason": reason,
                    "category": category,
                },
                log_subdir="hooks/security",
            )
            print(
                f"BLOCKED: {reason} [{category}]\n"
                f"Command: {command[:100]}",
                file=sys.stderr,
            )
            sys.exit(2)

        elif action == "ask":
            log_hook_activity(
                "dangerous_command_blocker",
                {
                    "command": command,
                    "action": "warn",
                    "reason": reason,
                    "category": category,
                },
                log_subdir="hooks/security",
            )
            print(
                f"WARNING: {reason} [{category}]\n"
                f"Command: {command[:100]}",
                file=sys.stderr,
            )

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
