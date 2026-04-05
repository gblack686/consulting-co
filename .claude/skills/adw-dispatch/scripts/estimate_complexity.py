#!/usr/bin/env python3
"""
Estimate task complexity for routing decisions.

Usage:
    python estimate_complexity.py "task description"
    python estimate_complexity.py "task description" --json
"""

import argparse
import json
import sys
from adw_ops import estimate_complexity


def main():
    parser = argparse.ArgumentParser(description="Estimate ADW task complexity")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    estimate = estimate_complexity(args.task)

    if args.json:
        output = {
            "task": estimate.task,
            "estimated_tokens": estimate.estimated_tokens,
            "files_touched": estimate.files_touched,
            "complexity_level": estimate.complexity_level,
            "recommended_mode": estimate.recommended_mode.value,
            "reasoning": estimate.reasoning
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Task Complexity Estimate")
        print(f"{'='*60}")
        print(f"Task: {estimate.task}")
        print(f"")
        print(f"Estimated Tokens: {estimate.estimated_tokens:,}")
        print(f"Files Touched: {estimate.files_touched}")
        print(f"Complexity Level: {estimate.complexity_level.upper()}")
        print(f"")
        print(f"Recommended Mode: {estimate.recommended_mode.value.upper()}")
        print(f"Reasoning: {estimate.reasoning}")
        print(f"{'='*60}")

        # Cost estimate
        if estimate.recommended_mode.value == "local":
            cost = estimate.estimated_tokens * 0.000003  # ~$3 per 1M tokens for Haiku
            print(f"\nEstimated Cost: ~${cost:.4f} (Local Haiku)")
        else:
            print(f"\nEstimated Cost: $0.00 (GitHub Actions - Max subscription)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
