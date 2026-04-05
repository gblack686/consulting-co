#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Graphiti Queue Processor

Reads queued turn files from logs/graphiti_queue/ and outputs
commands for Claude to ingest them via MCP.

This script is meant to be called by Claude, not run standalone,
since MCP tools can only be called from within a Claude session.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


QUEUE_DIR = Path.cwd() / "logs" / "graphiti_queue"


def get_queue_files() -> list[Path]:
    """Get all pending queue files sorted by modification time."""
    if not QUEUE_DIR.exists():
        return []
    files = list(QUEUE_DIR.glob("*.json"))
    return sorted(files, key=lambda f: f.stat().st_mtime)


def read_queue_file(file_path: Path) -> dict | None:
    """Read and parse a queue file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None


def extract_mcp_args(payload: dict) -> dict | None:
    """Extract the add_memory arguments from the MCP payload."""
    try:
        return payload.get("params", {}).get("arguments", {})
    except Exception:
        return None


def format_for_claude(queue_items: list[tuple[Path, dict]]) -> str:
    """Format queue items as instructions for Claude."""
    if not queue_items:
        return "No items in queue."

    lines = [
        f"## Graphiti Queue: {len(queue_items)} items to process",
        "",
        "Process each item by calling `mcp__graphiti__add_memory` with the arguments below,",
        "then delete the source file.",
        ""
    ]

    for i, (file_path, args) in enumerate(queue_items, 1):
        lines.append(f"### Item {i}: `{file_path.name}`")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(args, indent=2))
        lines.append("```")
        lines.append("")
        lines.append(f"After successful ingestion, delete: `{file_path}`")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    files = get_queue_files()

    if not files:
        print("Queue is empty. No items to process.")
        sys.exit(0)

    print(f"Found {len(files)} items in queue.\n")

    queue_items = []
    for f in files:
        payload = read_queue_file(f)
        if payload:
            args = extract_mcp_args(payload)
            if args:
                queue_items.append((f, args))
            else:
                print(f"Warning: Could not extract args from {f.name}", file=sys.stderr)

    if queue_items:
        print(format_for_claude(queue_items))
    else:
        print("No valid items found in queue.")


if __name__ == "__main__":
    main()
