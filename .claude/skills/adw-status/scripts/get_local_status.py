#!/usr/bin/env python3
"""
Get local Claude task status.

Usage:
    python get_local_status.py
    python get_local_status.py --task-id abc123
"""

import argparse
import json
import sys
from pathlib import Path
from status_ops import get_local_tasks, TaskStatus


def main():
    parser = argparse.ArgumentParser(description="Get local task status")
    parser.add_argument("--task-id", help="Specific task ID to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    tasks = get_local_tasks()

    if args.task_id:
        tasks = [t for t in tasks if t.task_id == args.task_id]

    if args.json:
        output = [
            {
                "task_id": t.task_id,
                "task": t.task,
                "status": t.status.value,
                "tokens_used": t.tokens_used,
                "cost_usd": t.cost_usd,
                "output_file": t.output_file
            }
            for t in tasks
        ]
        print(json.dumps(output, indent=2))
        return 0

    print(f"\nLocal Claude Tasks")
    print(f"{'='*60}")

    if not tasks:
        print("No local tasks found")
        return 0

    running = [t for t in tasks if t.status == TaskStatus.RUNNING]
    completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]

    if running:
        print(f"\n RUNNING ({len(running)}):")
        for task in running:
            print(f"\n  Task ID: {task.task_id}")
            print(f"  Status: {task.status.value}")
            if task.tokens_used:
                print(f"  Tokens: {task.tokens_used:,}")
                print(f"  Cost: ${task.cost_usd:.4f}")

    if completed:
        print(f"\n RECENT COMPLETED ({len(completed)}):")
        for task in completed[:5]:
            print(f"\n  Task ID: {task.task_id}")
            print(f"  Task: {task.task[:80]}...")
            if task.output_file:
                print(f"  Output: {task.output_file}")

    print(f"\n{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
