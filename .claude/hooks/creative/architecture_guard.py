#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Architecture Guard — PreToolUse Hook (Write)

Enforces file placement conventions:
  - client/ → .ts, .tsx, .js, .jsx, .css, .scss, .html only
  - server/ → .py only
  - .claude/hooks/ → .py only
  - .claude/agents/ → .md only
  - .claude/commands/ → .md only

Action: WARN (stderr message, allow but flag)
Never blocks — informational only.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity


# Architecture rules: directory pattern → allowed extensions
ARCHITECTURE_RULES = [
    {
        "dir_pattern": r"client/",
        "allowed_extensions": {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".html", ".svg", ".json", ".md"},
        "description": "Client directory — frontend files only",
    },
    {
        "dir_pattern": r"server/",
        "allowed_extensions": {".py", ".pyi", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".md", ".sql"},
        "description": "Server directory — Python/config files only",
    },
    {
        "dir_pattern": r"\.claude/hooks/",
        "allowed_extensions": {".py", ".sh", ".yaml", ".yml", ".json"},
        "description": "Hooks directory — Python/shell scripts only",
    },
    {
        "dir_pattern": r"\.claude/agents/",
        "allowed_extensions": {".md"},
        "description": "Agents directory — Markdown files only",
    },
    {
        "dir_pattern": r"\.claude/commands/",
        "allowed_extensions": {".md"},
        "description": "Commands directory — Markdown files only",
    },
]

# Paths to skip checking
SKIP_PATHS = {"node_modules/", "dist/", "build/", ".git/", "__pycache__/", "venv/"}


def check_architecture(file_path: str) -> tuple:
    """
    Check if a file placement violates architecture rules.

    Returns:
        tuple: (violates, rule_description, extension) or (False, None, None)
    """
    fp = file_path.replace("\\", "/")

    # Skip certain paths
    for skip in SKIP_PATHS:
        if skip in fp:
            return False, None, None

    ext = Path(fp).suffix.lower()
    if not ext:
        return False, None, None

    for rule in ARCHITECTURE_RULES:
        if re.search(rule["dir_pattern"], fp, re.IGNORECASE):
            if ext not in rule["allowed_extensions"]:
                return True, rule["description"], ext

    return False, None, None


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name != "Write":
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        violates, description, ext = check_architecture(file_path)

        if violates:
            log_hook_activity(
                "architecture_guard",
                {
                    "file_path": file_path,
                    "extension": ext,
                    "rule": description,
                },
                log_subdir="hooks/creative",
            )

            print(
                f"ARCHITECTURE WARNING: {Path(file_path).name} ({ext}) "
                f"may not belong here\n"
                f"  Rule: {description}\n"
                f"  Path: {file_path}",
                file=sys.stderr,
            )

        # Never block — informational only
        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
