#!/usr/bin/env python3
"""
Get cost summary for ADW operations.

Usage:
    python cost_summary.py
    python cost_summary.py --date 2026-01-15
"""

import argparse
import json
import sys
from datetime import datetime
from status_ops import get_cost_summary


def main():
    parser = argparse.ArgumentParser(description="Get cost summary")
    parser.add_argument("--date", help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    summary = get_cost_summary()

    if args.json:
        output = {
            "date": args.date or datetime.now().strftime("%Y-%m-%d"),
            "daily_total": summary.daily_total,
            "daily_budget": summary.daily_budget,
            "local_cost": summary.local_cost,
            "github_cost": summary.github_cost,
            "tokens_used": summary.tokens_used,
            "percentage_used": summary.percentage_used
        }
        print(json.dumps(output, indent=2))
        return 0

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")

    print(f"\nCost Summary - {date_str}")
    print(f"{'='*50}")

    # Progress bar
    bar_width = 40
    filled = int((summary.percentage_used / 100) * bar_width)
    bar = "" * filled + "" * (bar_width - filled)

    print(f"\nDaily Budget: ${summary.daily_budget:.2f}")
    print(f"Used Today:   ${summary.daily_total:.4f}")
    print(f"\n[{bar}] {summary.percentage_used:.1f}%")

    print(f"\nBreakdown:")
    print(f"  Local Haiku:     ${summary.local_cost:.4f}")
    print(f"  GitHub Actions:  ${summary.github_cost:.2f} (free with Max)")
    print(f"  Tokens Used:     {summary.tokens_used:,}")

    remaining = summary.daily_budget - summary.daily_total
    print(f"\nRemaining Budget: ${remaining:.4f}")

    # Estimate remaining capacity
    avg_cost_per_task = 0.005  # ~$0.005 per Haiku task
    estimated_tasks = int(remaining / avg_cost_per_task)
    print(f"Est. Remaining Tasks: ~{estimated_tasks} (at ~$0.005/task)")

    # Warnings
    if summary.percentage_used >= 90:
        print(f"\n CRITICAL: Budget nearly exhausted!")
    elif summary.percentage_used >= 80:
        print(f"\n WARNING: Approaching budget limit")
    elif summary.percentage_used >= 50:
        print(f"\n INFO: Half of daily budget used")

    print(f"\n{'='*50}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
