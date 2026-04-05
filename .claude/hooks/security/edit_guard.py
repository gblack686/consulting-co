#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyyaml"]
# ///
"""
Edit Guard — PreToolUse Hook (Edit/MultiEdit)

Enforces path protection levels from patterns.yaml:
  - zeroAccess: Block ALL operations (read/write/edit)
  - readOnly:   Block edit operations
  - noDelete:   Allow edits (handled here as allowed)

Exit codes:
  0 — Allow edit
  2 — Block edit (protected path)
"""

import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity

PATTERNS_FILE = Path(__file__).parent / "patterns.yaml"


def load_path_protection() -> dict:
    """Load path protection rules from patterns.yaml."""
    if not PATTERNS_FILE.exists():
        return {}
    with open(PATTERNS_FILE, "r") as f:
        data = yaml.safe_load(f) or {}
    return data.get("path_protection", {})


def matches_path_pattern(file_path: str, pattern: str) -> bool:
    """Check if a file path matches a protection pattern."""
    fp = file_path.replace("\\", "/")
    pat = pattern.replace("\\", "/")

    # Handle home directory
    if pat.startswith("~/"):
        home = str(Path.home()).replace("\\", "/")
        pat = home + pat[1:]

    # Glob-style matching
    if pat.startswith("*."):
        return fp.endswith(pat[1:])

    if pat.endswith("/"):
        # Match as a path segment: /build/ should not match /plan_build_improve.md
        seg = pat.rstrip("/")
        return ("/" + seg + "/") in ("/" + fp)

    # Basename or full path match
    basename = Path(fp).name
    return basename == pat or fp.endswith(pat)


def check_path(file_path: str, protection: dict) -> tuple:
    """
    Check file path against protection levels.

    Returns:
        tuple: (action, reason, level)
    """
    # zeroAccess — block all
    for pattern in protection.get("zeroAccess", []):
        if matches_path_pattern(file_path, pattern):
            return "block", f"Zero-access protected: {pattern}", "zeroAccess"

    # readOnly — block edits
    for pattern in protection.get("readOnly", []):
        if matches_path_pattern(file_path, pattern):
            return "block", f"Read-only protected: {pattern}", "readOnly"

    return None, None, None


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ("Edit", "MultiEdit"):
            sys.exit(0)

        # Extract file paths
        file_paths = []
        if tool_name == "Edit":
            fp = tool_input.get("file_path", "")
            if fp:
                file_paths.append(fp)
        elif tool_name == "MultiEdit":
            for edit in tool_input.get("edits", []):
                fp = edit.get("file_path", "")
                if fp:
                    file_paths.append(fp)

        if not file_paths:
            sys.exit(0)

        protection = load_path_protection()

        for fp in file_paths:
            action, reason, level = check_path(fp, protection)

            if action == "block":
                log_hook_activity(
                    "edit_guard",
                    {
                        "file_path": fp,
                        "action": "block",
                        "reason": reason,
                        "level": level,
                    },
                    log_subdir="hooks/security",
                )
                print(
                    f"BLOCKED: Cannot edit {fp}\n"
                    f"Reason: {reason}",
                    file=sys.stderr,
                )
                sys.exit(2)

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
