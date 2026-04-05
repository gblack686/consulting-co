#!/usr/bin/env python3
"""
Analyze GitHub Actions workflow failures.

Provides insights into failure patterns, common errors,
and recommendations for improving CI/CD reliability.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

from gh_actions_ops import list_runs, get_run, get_run_logs, format_status


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"default_repo": "gblack686/consulting-co"}


def extract_error_pattern(logs: str) -> str:
    """Try to extract a meaningful error pattern from logs."""
    lines = logs.lower().split('\n')

    # Look for common error patterns
    error_keywords = [
        "error:", "failed:", "exception:", "traceback",
        "fatal:", "cannot", "unable to", "not found",
        "timeout", "permission denied", "exit code"
    ]

    for line in lines:
        for keyword in error_keywords:
            if keyword in line:
                # Return a cleaned up error snippet
                return line.strip()[:100]

    return "Unknown error"


def main():
    parser = argparse.ArgumentParser(description="Analyze workflow failures")
    parser.add_argument("--repo", "-r", help="Repository (owner/repo)")
    parser.add_argument("--days", "-d", type=int, default=30,
                        help="Number of days to analyze (default: 30)")
    parser.add_argument("--workflow", "-w", help="Filter by workflow")
    parser.add_argument("--detailed", action="store_true",
                        help="Fetch logs for detailed error analysis")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    config = load_config()
    repo = args.repo or config.get("default_repo", "gblack686/consulting-co")

    print(f"Analyzing failures in {repo} (last {args.days} days)\n")

    # Fetch runs (get more to cover the time period)
    limit = min(args.days * 5, 200)  # Rough estimate
    success, runs = list_runs(repo, workflow=args.workflow, limit=limit)

    if not success:
        print(f"Error: {runs}")
        return 1

    if not runs:
        print("No runs found.")
        return 0

    # Filter to the time period
    cutoff = datetime.now().astimezone() - timedelta(days=args.days)
    runs_in_period = []
    for run in runs:
        try:
            created = datetime.fromisoformat(run.get("createdAt", "").replace("Z", "+00:00"))
            if created >= cutoff:
                runs_in_period.append(run)
        except:
            pass

    # Separate by conclusion
    all_runs = runs_in_period
    failures = [r for r in all_runs if r.get("conclusion") == "failure"]
    successes = [r for r in all_runs if r.get("conclusion") == "success"]

    # Calculate metrics
    total = len(all_runs)
    failure_count = len(failures)
    success_count = len(successes)
    success_rate = (success_count / total * 100) if total > 0 else 0

    # Group failures by workflow
    failures_by_workflow = Counter(r.get("workflowName") for r in failures)

    # Group failures by branch
    failures_by_branch = Counter(r.get("headBranch") for r in failures)

    analysis = {
        "period_days": args.days,
        "total_runs": total,
        "failures": failure_count,
        "successes": success_count,
        "success_rate": round(success_rate, 1),
        "failures_by_workflow": dict(failures_by_workflow.most_common(10)),
        "failures_by_branch": dict(failures_by_branch.most_common(10)),
        "recent_failures": []
    }

    # Get recent failure details
    for run in failures[:5]:
        failure_info = {
            "run_id": run.get("databaseId"),
            "title": run.get("displayTitle"),
            "workflow": run.get("workflowName"),
            "branch": run.get("headBranch"),
            "created": run.get("createdAt"),
            "url": run.get("url")
        }

        # Optionally fetch logs for detailed analysis
        if args.detailed:
            print(f"  Fetching logs for run {run.get('databaseId')}...", end="", flush=True)
            ok, logs = get_run_logs(repo, run.get("databaseId"), failed_only=True)
            if ok:
                failure_info["error_pattern"] = extract_error_pattern(logs)
            print(" done")

        analysis["recent_failures"].append(failure_info)

    if args.json:
        print(json.dumps(analysis, indent=2))
        return 0

    # Display analysis
    print("=" * 60)
    print(f"FAILURE ANALYSIS - Last {args.days} Days")
    print("=" * 60)

    print(f"\n📊 Overview:")
    print(f"   Total Runs:   {total}")
    print(f"   Successes:    {success_count} ✅")
    print(f"   Failures:     {failure_count} ❌")
    print(f"   Success Rate: {success_rate:.1f}%")

    if failures_by_workflow:
        print(f"\n📋 Failures by Workflow:")
        for wf, count in failures_by_workflow.most_common(5):
            pct = count / failure_count * 100 if failure_count > 0 else 0
            print(f"   {wf}: {count} ({pct:.0f}%)")

    if failures_by_branch:
        print(f"\n🌿 Failures by Branch:")
        for branch, count in failures_by_branch.most_common(5):
            print(f"   {branch}: {count}")

    if analysis["recent_failures"]:
        print(f"\n🔴 Recent Failures:")
        for f in analysis["recent_failures"][:5]:
            print(f"   #{f['run_id']}: {f['title'][:50]}")
            print(f"      Workflow: {f['workflow']} | Branch: {f['branch']}")
            if "error_pattern" in f:
                print(f"      Error: {f['error_pattern']}")

    # Recommendations
    print(f"\n💡 Recommendations:")
    if success_rate < 80:
        print("   ⚠️  Success rate below 80% - investigate frequent failures")
    if failures_by_workflow:
        top_failing = failures_by_workflow.most_common(1)[0]
        print(f"   🔧 Focus on '{top_failing[0]}' workflow ({top_failing[1]} failures)")
    if failure_count == 0:
        print("   ✅ No failures in this period - great job!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
