#!/usr/bin/env python3
"""
Check if budget is approaching alert threshold.

Usage:
    python alert_threshold.py
    python alert_threshold.py --json

Exit codes:
    0 - Within budget
    1 - Near limit (warning)
    2 - Over budget (critical)
"""

import argparse
import json
import sys
from cost_ops import get_budget_status, load_settings


def main():
    parser = argparse.ArgumentParser(description="Check budget alert threshold")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress output (exit code only)")

    args = parser.parse_args()

    status = get_budget_status()
    settings = load_settings()
    budget_config = settings.get("budget", {})
    alert_threshold = budget_config.get("alert_threshold", 0.80)
    critical_threshold = budget_config.get("critical_threshold", 0.95)

    alert_level = "ok"
    if status.is_over_budget:
        alert_level = "critical"
        exit_code = 2
    elif status.percentage_used >= critical_threshold * 100:
        alert_level = "critical"
        exit_code = 2
    elif status.is_near_limit:
        alert_level = "warning"
        exit_code = 1
    else:
        exit_code = 0

    if args.json:
        output = {
            "alert_level": alert_level,
            "percentage_used": status.percentage_used,
            "used_today": status.used_today,
            "daily_budget": status.daily_budget,
            "remaining": status.remaining,
            "thresholds": {
                "alert": alert_threshold * 100,
                "critical": critical_threshold * 100
            }
        }
        print(json.dumps(output, indent=2))
        return exit_code

    if args.quiet:
        return exit_code

    if alert_level == "critical":
        print(f"\n CRITICAL: Budget at {status.percentage_used:.1f}%!")
        print(f"\nUsed: ${status.used_today:.4f} / ${status.daily_budget:.2f}")
        print(f"Remaining: ${status.remaining:.4f}")
        print(f"\nRecommendations:")
        print(f"  1. Use GitHub Actions (free with Max) for remaining tasks")
        print(f"  2. Defer non-urgent tasks to tomorrow")
        print(f"  3. Review recent usage: python daily_report.py")

    elif alert_level == "warning":
        print(f"\n WARNING: Budget at {status.percentage_used:.1f}%")
        print(f"Threshold: {alert_threshold * 100:.0f}%")
        print(f"\nUsed: ${status.used_today:.4f} / ${status.daily_budget:.2f}")
        print(f"Remaining: ${status.remaining:.4f}")
        print(f"\nConsider routing complex tasks to GitHub Actions (free).")

    else:
        print(f"\n OK: Budget at {status.percentage_used:.1f}%")
        print(f"\nUsed: ${status.used_today:.4f} / ${status.daily_budget:.2f}")
        print(f"Remaining: ${status.remaining:.4f}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
