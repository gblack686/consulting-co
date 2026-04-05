#!/usr/bin/env python3
"""
Log API usage.

Usage:
    python log_usage.py <input_tokens> <output_tokens> [model]
    python log_usage.py 1500 2000 haiku
    python log_usage.py 5000 10000 sonnet --task "Implement feature X"
"""

import argparse
import json
import sys
from cost_ops import log_usage, get_budget_status


def main():
    parser = argparse.ArgumentParser(description="Log API usage")
    parser.add_argument("input_tokens", type=int, help="Number of input tokens")
    parser.add_argument("output_tokens", type=int, help="Number of output tokens")
    parser.add_argument("model", nargs="?", default="haiku", help="Model name (haiku, sonnet, opus)")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    entry = log_usage(
        input_tokens=args.input_tokens,
        output_tokens=args.output_tokens,
        model=args.model,
        task=args.task
    )

    status = get_budget_status()

    if args.json:
        output = {
            "logged": {
                "timestamp": entry.timestamp,
                "input_tokens": entry.input_tokens,
                "output_tokens": entry.output_tokens,
                "cost": entry.cost,
                "model": entry.model
            },
            "budget_status": {
                "used_today": status.used_today,
                "remaining": status.remaining,
                "percentage_used": status.percentage_used
            }
        }
        print(json.dumps(output, indent=2))
        return 0

    print(f"\n{'='*50}")
    print(f"Usage Logged")
    print(f"{'='*50}")
    print(f"Model: {entry.model}")
    print(f"Input Tokens: {entry.input_tokens:,}")
    print(f"Output Tokens: {entry.output_tokens:,}")
    print(f"Cost: ${entry.cost:.6f}")
    if args.task:
        print(f"Task: {args.task}")
    print(f"\nDaily Total: ${status.used_today:.4f} / ${status.daily_budget:.2f} ({status.percentage_used:.1f}%)")
    print(f"{'='*50}")

    if status.is_near_limit:
        print(f"\n WARNING: Approaching daily budget limit!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
