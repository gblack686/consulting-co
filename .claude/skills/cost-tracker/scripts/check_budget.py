#!/usr/bin/env python3
"""
Check current budget status.

Usage:
    python check_budget.py
    python check_budget.py --json
"""

import argparse
import json
import sys
from cost_ops import get_budget_status, load_settings


def main():
    parser = argparse.ArgumentParser(description="Check current budget status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    status = get_budget_status()

    if args.json:
        output = {
            "daily_budget": status.daily_budget,
            "used_today": status.used_today,
            "remaining": status.remaining,
            "percentage_used": status.percentage_used,
            "is_over_budget": status.is_over_budget,
            "is_near_limit": status.is_near_limit
        }
        print(json.dumps(output, indent=2))
        return 0

    # Text output with visual budget bar
    print(f"\n{'='*50}")
    print(f"Budget Status")
    print(f"{'='*50}")

    # Progress bar
    bar_width = 40
    filled = int((status.percentage_used / 100) * bar_width)
    filled = min(filled, bar_width)  # Cap at 100%

    if status.is_over_budget:
        bar = "" * bar_width
        color_indicator = " OVER BUDGET"
    elif status.is_near_limit:
        bar = "" * filled + "" * (bar_width - filled)
        color_indicator = " NEAR LIMIT"
    else:
        bar = "" * filled + "" * (bar_width - filled)
        color_indicator = ""

    print(f"\nDaily Budget: ${status.daily_budget:.2f}")
    print(f"Used Today:   ${status.used_today:.4f}")
    print(f"\n[{bar}] {status.percentage_used:.1f}%{color_indicator}")
    print(f"\nRemaining: ${status.remaining:.4f}")

    # Estimate remaining tasks
    avg_cost = 0.005  # ~$0.005 per Haiku task
    estimated_tasks = int(status.remaining / avg_cost)
    print(f"Est. Remaining Tasks: ~{estimated_tasks} (at ~$0.005/task)")

    # Status alerts
    if status.is_over_budget:
        print(f"\n CRITICAL: Daily budget exceeded!")
        print(f"Consider using GitHub Actions (free with Max) for remaining tasks.")
        return 2
    elif status.is_near_limit:
        settings = load_settings()
        threshold = settings.get("budget", {}).get("alert_threshold", 0.80) * 100
        print(f"\n WARNING: Budget usage at {status.percentage_used:.1f}% (threshold: {threshold:.0f}%)")
        return 1

    print(f"\n{'='*50}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
