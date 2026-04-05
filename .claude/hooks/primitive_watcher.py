#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Primitive Watcher — PostToolUse Hook (Write/Edit)

Detects when Claude Code primitives are created or modified:
  - .claude/agents/*.md        → Agent
  - .claude/commands/**/*.md   → Command
  - .claude/skills/**/SKILL.md → Skill
  - .claude/hooks/*.py         → Hook

Actions:
  1. Log primitive creation/modification with timestamp
  2. Flag if settings.json needs updating (for hooks)
  3. Output notification to stderr
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.hook_utils import read_hook_input, log_hook_activity


# Primitive detection patterns
PRIMITIVE_PATTERNS = {
    "agent": {
        "patterns": [
            r"\.claude[/\\]agents[/\\].*\.md$",
        ],
        "description": "Agent definition",
    },
    "command": {
        "patterns": [
            r"\.claude[/\\]commands[/\\].*\.md$",
        ],
        "description": "Slash command",
    },
    "skill": {
        "patterns": [
            r"\.claude[/\\]skills[/\\].*SKILL\.md$",
            r"\.claude[/\\]skills[/\\].*\.md$",
        ],
        "description": "Skill definition",
    },
    "hook": {
        "patterns": [
            r"\.claude[/\\]hooks[/\\].*\.py$",
        ],
        "description": "Hook script",
    },
    "settings": {
        "patterns": [
            r"\.claude[/\\]settings\.json$",
            r"\.claude[/\\]settings\.local\.json$",
        ],
        "description": "Settings configuration",
    },
}


def detect_primitive(file_path: str) -> tuple:
    """
    Detect what type of primitive was modified.

    Returns:
        tuple: (primitive_type, description) or (None, None)
    """
    normalized = file_path.replace("\\", "/")

    for ptype, config in PRIMITIVE_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, normalized, re.IGNORECASE):
                return ptype, config["description"]

    return None, None


def check_settings_needs_update(file_path: str, primitive_type: str) -> bool:
    """Check if a hook was created that may need settings.json registration."""
    if primitive_type != "hook":
        return False

    # Check if this hook script is referenced in settings.json
    settings_path = Path.cwd() / ".claude" / "settings.json"
    if not settings_path.exists():
        return True

    try:
        with open(settings_path) as f:
            settings = json.load(f)
        settings_str = json.dumps(settings)
        # Get just the relative path from .claude/hooks/
        basename = Path(file_path).name
        return basename not in settings_str
    except Exception:
        return False


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        # Extract file path(s)
        file_paths = []
        if tool_name in ("Write", "Edit"):
            fp = tool_input.get("file_path", "")
            if fp:
                file_paths.append(fp)
        elif tool_name == "MultiEdit":
            for edit in tool_input.get("edits", []):
                fp = edit.get("file_path", "")
                if fp:
                    file_paths.append(fp)

        for fp in file_paths:
            primitive_type, description = detect_primitive(fp)
            if not primitive_type:
                continue

            # Determine if this is a create or modify
            target = Path(fp)
            action = "modified" if target.exists() else "created"

            # Check if settings.json needs updating
            needs_settings = check_settings_needs_update(fp, primitive_type)

            # Log the event
            log_entry = {
                "primitive_type": primitive_type,
                "description": description,
                "file_path": fp,
                "action": action,
                "needs_settings_update": needs_settings,
            }

            log_hook_activity(
                "primitive_watcher",
                log_entry,
                log_subdir="hooks/primitive",
            )

            # Notify via stderr
            icon = {
                "agent": "🤖",
                "command": "⚡",
                "skill": "🎯",
                "hook": "🪝",
                "settings": "⚙️",
            }.get(primitive_type, "📄")

            print(
                f"{icon} Primitive {action}: {primitive_type} — {Path(fp).name}",
                file=sys.stderr,
            )

            if needs_settings:
                print(
                    f"   ⚠️  Hook not found in settings.json — register it!",
                    file=sys.stderr,
                )

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
