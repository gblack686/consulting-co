#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Obsidian Ecosystem Sync Hook - PostToolUse Hook

Triggers the /sync-claude-ecosystem command when significant changes
are made to .claude folder components (agents, commands, hooks, skills).

This hook monitors file operations and triggers sync when:
- New agent/command/hook/skill files are created
- Existing component files are modified
- Component files are deleted

The sync is debounced to avoid excessive triggers during batch operations.
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


# Debounce settings
DEBOUNCE_FILE = Path.home() / ".claude" / "logs" / "obsidian_sync_debounce.json"
DEBOUNCE_SECONDS = 30  # Minimum seconds between syncs


def should_trigger_sync() -> bool:
    """Check if enough time has passed since last sync trigger."""
    try:
        if DEBOUNCE_FILE.exists():
            with open(DEBOUNCE_FILE, "r") as f:
                data = json.load(f)
                last_trigger = data.get("last_trigger", 0)
                if time.time() - last_trigger < DEBOUNCE_SECONDS:
                    return False
    except (json.JSONDecodeError, ValueError, IOError):
        pass
    return True


def update_debounce_timestamp():
    """Update the debounce timestamp."""
    try:
        DEBOUNCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DEBOUNCE_FILE, "w") as f:
            json.dump({"last_trigger": time.time()}, f)
    except IOError:
        pass


def is_claude_component_path(file_path: str) -> bool:
    """Check if the file path is within a .claude component folder."""
    if not file_path:
        return False

    # Normalize path separators
    normalized = file_path.replace("\\", "/").lower()

    # Component folders to monitor
    component_patterns = [
        ".claude/agents/",
        ".claude/commands/",
        ".claude/hooks/",
        ".claude/skills/",
    ]

    return any(pattern in normalized for pattern in component_patterns)


def log_sync_trigger(file_path: str, tool_name: str, action: str):
    """Log sync trigger for debugging."""
    log_dir = Path.home() / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "obsidian_ecosystem_sync.log"

    try:
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] SYNC TRIGGERED\n")
            f.write(f"  Tool: {tool_name}\n")
            f.write(f"  Action: {action}\n")
            f.write(f"  File: {file_path}\n")
            f.write("---\n")
    except IOError:
        pass


def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process file modification tools
        if tool_name not in ["Edit", "Write", "MultiEdit", "Bash"]:
            sys.exit(0)

        # Extract file path(s) based on tool type
        file_paths = []

        if tool_name in ["Edit", "Write"]:
            file_path = tool_input.get("file_path", "")
            if file_path:
                file_paths.append(file_path)

        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])
            for edit in edits:
                file_path = edit.get("file_path", "")
                if file_path:
                    file_paths.append(file_path)

        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            # Check for file operations in bash commands that might affect .claude
            if ".claude" in command and any(
                op in command for op in ["touch", "mkdir", "cp", "mv", "rm", "echo", "cat", ">"]
            ):
                # Can't easily extract paths from bash, but flag for potential sync
                file_paths.append(command)

        # Check if any paths are Claude component paths
        should_sync = any(is_claude_component_path(fp) for fp in file_paths)

        if not should_sync:
            sys.exit(0)

        # Placeholder: echo hello world
        print("hello world - obsidian_ecosystem_sync", file=sys.stderr)

        # Check debounce
        if not should_trigger_sync():
            print("Sync debounced - too recent", file=sys.stderr)
            sys.exit(0)

        # Log the trigger
        for fp in file_paths:
            if is_claude_component_path(fp):
                log_sync_trigger(fp, tool_name, "modified")

        # Update debounce timestamp
        update_debounce_timestamp()

        # Output message about triggering sync
        # In the future, this would invoke the /sync-claude-ecosystem command
        print("Would trigger: /sync-claude-ecosystem .claude/", file=sys.stderr)
        print("NOTE: Auto-sync is placeholder - run /sync-claude-ecosystem manually", file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
