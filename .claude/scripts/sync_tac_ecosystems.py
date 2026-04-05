#!/usr/bin/env python3
"""
Sync All TAC .claude Ecosystems to Obsidian

This script processes all .claude directories from TAC projects
and syncs them to the Obsidian AI-Agent-KB.

Usage:
    python sync_tac_ecosystems.py                    # List all directories
    python sync_tac_ecosystems.py --dry-run          # Show what would be synced
    python sync_tac_ecosystems.py --execute          # Run all syncs
    python sync_tac_ecosystems.py --execute --start 5  # Start from index 5
    python sync_tac_ecosystems.py --single 3         # Sync only index 3
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# TAC directories to process
TAC_DIRECTORIES = [
    # TAC Course Projects (12)
    ("agent-experts", "C:/Users/gblac/OneDrive/Desktop/tac/agent-experts/.claude"),
    ("agent-sandbox-skill", "C:/Users/gblac/OneDrive/Desktop/tac/agent-sandbox-skill/.claude"),
    ("agent-sandboxes", "C:/Users/gblac/OneDrive/Desktop/tac/agent-sandboxes/.claude"),
    ("agentic-finance-review", "C:/Users/gblac/OneDrive/Desktop/tac/agentic-finance-review/.claude"),
    ("building-domain-specific-agents", "C:/Users/gblac/OneDrive/Desktop/tac/building-domain-specific-agents/.claude"),
    ("claude-code-damage-control", "C:/Users/gblac/OneDrive/Desktop/tac/claude-code-damage-control/.claude"),
    ("claude-code-hooks-mastery", "C:/Users/gblac/OneDrive/Desktop/tac/claude-code-hooks-mastery/.claude"),
    ("fork-repository-skill", "C:/Users/gblac/OneDrive/Desktop/tac/fork-repository-skill/.claude"),
    ("multi-agent-orchestration-the-o-agent", "C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration-the-o-agent/.claude"),
    ("orchestrator-agent-with-adws", "C:/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/.claude"),
    ("rd-framework-context-window-mastery", "C:/Users/gblac/OneDrive/Desktop/tac/rd-framework-context-window-mastery/.claude"),
    ("seven-levels-agentic-prompt-formats", "C:/Users/gblac/OneDrive/Desktop/tac/seven-levels-agentic-prompt-formats/.claude"),

    # TAC Numbered Projects (7)
    ("tac-1", "C:/Users/gblac/OneDrive/Desktop/tac/tac-1/.claude"),
    ("tac-2", "C:/Users/gblac/OneDrive/Desktop/tac/tac-2/.claude"),
    ("tac-3", "C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude"),
    ("tac-4", "C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude"),
    ("tac-5", "C:/Users/gblac/OneDrive/Desktop/tac/tac-5/.claude"),
    ("tac-6", "C:/Users/gblac/OneDrive/Desktop/tac/tac-6/.claude"),
    ("tac-7", "C:/Users/gblac/OneDrive/Desktop/tac/tac-7/.claude"),

    # TAC-8 Sub-Projects (5)
    ("tac8_app1__agent_layer_primitives", "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app1__agent_layer_primitives/.claude"),
    ("tac8_app2__multi_agent_todone", "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app2__multi_agent_todone/.claude"),
    ("tac8_app3__out_loop_multi_agent_task_board", "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app3__out_loop_multi_agent_task_board/.claude"),
    ("tac8_app4__agentic_prototyping", "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app4__agentic_prototyping/.claude"),
    ("tac8_app5__nlq_to_sql_aea", "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app5__nlq_to_sql_aea/.claude"),
]

LOG_DIR = Path.home() / ".claude" / "logs"
PROGRESS_FILE = Path.home() / ".claude" / "scripts" / "sync-progress.json"


def load_progress():
    """Load sync progress from JSON file."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed": [], "failed": [], "last_run": None}


def save_progress(progress):
    """Save sync progress to JSON file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


def list_directories():
    """List all directories with their status."""
    progress = load_progress()
    print("\n" + "=" * 60)
    print("TAC Ecosystem Directories")
    print("=" * 60 + "\n")

    for idx, (name, path) in enumerate(TAC_DIRECTORIES):
        exists = Path(path).exists()
        status = "✅" if name in progress["completed"] else ("❌" if name in progress["failed"] else "⏳")
        exists_str = "📁" if exists else "⚠️"
        print(f"[{idx:2d}] {status} {exists_str} {name}")
        print(f"      {path}")

    print(f"\nTotal: {len(TAC_DIRECTORIES)} directories")
    print(f"Completed: {len(progress['completed'])}")
    print(f"Failed: {len(progress['failed'])}")
    print(f"Pending: {len(TAC_DIRECTORIES) - len(progress['completed']) - len(progress['failed'])}")


def sync_directory(name: str, path: str, dry_run: bool = True) -> bool:
    """Sync a single directory."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Syncing: {name}")
    print(f"  Path: {path}")

    if not Path(path).exists():
        print(f"  ⚠️ Directory not found!")
        return False

    cmd = f'/sync-claude-ecosystem {path}'

    if dry_run:
        print(f"  Command: claude -p \"{cmd}\"")
        return True

    try:
        # Run claude CLI with the sync command
        result = subprocess.run(
            ["claude", "-p", cmd, "--dangerously-skip-permissions"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per directory
        )

        if result.returncode == 0:
            print(f"  ✅ Success")
            return True
        else:
            print(f"  ❌ Failed: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ⏰ Timeout after 5 minutes")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def run_sync(execute: bool = False, start_idx: int = 0, single_idx: int = None):
    """Run the sync process."""
    progress = load_progress()
    progress["last_run"] = datetime.now().isoformat()

    if single_idx is not None:
        # Sync single directory
        if 0 <= single_idx < len(TAC_DIRECTORIES):
            name, path = TAC_DIRECTORIES[single_idx]
            success = sync_directory(name, path, dry_run=not execute)
            if execute:
                if success:
                    if name not in progress["completed"]:
                        progress["completed"].append(name)
                    if name in progress["failed"]:
                        progress["failed"].remove(name)
                else:
                    if name not in progress["failed"]:
                        progress["failed"].append(name)
                save_progress(progress)
        else:
            print(f"Invalid index: {single_idx}")
        return

    # Sync all directories from start_idx
    total = len(TAC_DIRECTORIES)
    success_count = 0
    fail_count = 0

    print("\n" + "=" * 60)
    print(f"TAC Ecosystem Sync - {'EXECUTE' if execute else 'DRY RUN'}")
    print(f"Processing {total - start_idx} directories (starting from {start_idx})")
    print("=" * 60)

    for idx in range(start_idx, total):
        name, path = TAC_DIRECTORIES[idx]
        print(f"\n[{idx + 1}/{total}] ", end="")

        success = sync_directory(name, path, dry_run=not execute)

        if execute:
            if success:
                success_count += 1
                if name not in progress["completed"]:
                    progress["completed"].append(name)
                if name in progress["failed"]:
                    progress["failed"].remove(name)
            else:
                fail_count += 1
                if name not in progress["failed"]:
                    progress["failed"].append(name)

            save_progress(progress)

    print("\n" + "=" * 60)
    print("Sync Complete")
    print(f"  Processed: {total - start_idx}")
    if execute:
        print(f"  Success: {success_count}")
        print(f"  Failed: {fail_count}")
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync TAC ecosystems to Obsidian")
    parser.add_argument("--list", action="store_true", help="List all directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced")
    parser.add_argument("--execute", action="store_true", help="Actually run syncs")
    parser.add_argument("--start", type=int, default=0, help="Start from index N")
    parser.add_argument("--single", type=int, help="Sync only index N")
    parser.add_argument("--reset", action="store_true", help="Reset progress tracking")

    args = parser.parse_args()

    if args.reset:
        save_progress({"completed": [], "failed": [], "last_run": None})
        print("Progress reset.")
        return

    if args.list or (not args.dry_run and not args.execute and args.single is None):
        list_directories()
        return

    run_sync(
        execute=args.execute,
        start_idx=args.start,
        single_idx=args.single
    )


if __name__ == "__main__":
    main()
