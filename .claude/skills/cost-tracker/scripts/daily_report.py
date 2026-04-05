#!/usr/bin/env python3
"""
Generate daily cost report.

Usage:
    python daily_report.py
    python daily_report.py --date 2026-01-15
    python daily_report.py --week
"""

import argparse
import json
import sys
from datetime import datetime
from cost_ops import get_daily_entries, get_weekly_summary, get_budget_status


def main():
    parser = argparse.ArgumentParser(description="Generate daily cost report")
    parser.add_argument("--date", help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--week", action="store_true", help="Show weekly summary")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.week:
        summary = get_weekly_summary()

        if args.json:
            print(json.dumps(summary, indent=2))
            return 0

        print(f"\n{'='*50}")
        print(f"Weekly Cost Summary")
        print(f"{'='*50}")

        total = sum(summary.values())
        for date, cost in summary.items():
            bar_width = 20
            max_cost = max(summary.values()) if max(summary.values()) > 0 else 1
            filled = int((cost / max_cost) * bar_width)
            bar = "" * filled + "" * (bar_width - filled)
            print(f"{date}: [{bar}] ${cost:.4f}")

        print(f"\nWeekly Total: ${total:.4f}")
        print(f"Daily Average: ${total/7:.4f}")
        print(f"{'='*50}")
        return 0

    # Daily report
    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    entries = get_daily_entries(target_date)
    status = get_budget_status()

    if args.json:
        output = {
            "date": target_date,
            "entries": [
                {
                    "timestamp": e.timestamp,
                    "input_tokens": e.input_tokens,
                    "output_tokens": e.output_tokens,
                    "cost": e.cost,
                    "model": e.model,
                    "task": e.task
                }
                for e in entries
            ],
            "total_cost": sum(e.cost for e in entries),
            "total_tokens": sum(e.input_tokens + e.output_tokens for e in entries)
        }
        print(json.dumps(output, indent=2))
        return 0

    print(f"\n{'='*60}")
    print(f"Daily Cost Report - {target_date}")
    print(f"{'='*60}")

    if not entries:
        print("\nNo usage entries for this date.")
        return 0

    # Summary
    total_cost = sum(e.cost for e in entries)
    total_input = sum(e.input_tokens for e in entries)
    total_output = sum(e.output_tokens for e in entries)

    print(f"\nSUMMARY:")
    print(f"  Total Cost: ${total_cost:.4f}")
    print(f"  Total Tokens: {total_input + total_output:,}")
    print(f"  Input: {total_input:,} | Output: {total_output:,}")
    print(f"  Entries: {len(entries)}")

    # Budget bar
    bar_width = 40
    filled = int((status.percentage_used / 100) * bar_width)
    filled = min(filled, bar_width)
    bar = "" * filled + "" * (bar_width - filled)
    print(f"\n  Budget: [{bar}] {status.percentage_used:.1f}%")

    # Model breakdown
    models = {}
    for e in entries:
        if e.model not in models:
            models[e.model] = {"cost": 0, "count": 0}
        models[e.model]["cost"] += e.cost
        models[e.model]["count"] += 1

    print(f"\nBY MODEL:")
    for model, data in sorted(models.items()):
        print(f"  {model}: ${data['cost']:.4f} ({data['count']} calls)")

    # Recent entries
    print(f"\nRECENT ENTRIES (last 5):")
    for entry in entries[-5:]:
        time = entry.timestamp.split("T")[1][:8]
        tokens = entry.input_tokens + entry.output_tokens
        print(f"  [{time}] {entry.model}: {tokens:,} tokens = ${entry.cost:.6f}")
        if entry.task:
            print(f"           Task: {entry.task[:40]}...")

    print(f"\n{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
