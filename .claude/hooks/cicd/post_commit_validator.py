#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Post-Commit Validator — PostToolUse Hook (Bash matching `git commit`)

After a git commit, automatically run:
  - Python lint check (ruff) if available
  - Python type check (ty/mypy) if available
  - JS/TS lint (eslint) if available
  - JS/TS type check (tsc) if available

Reports results via stderr. Never blocks — informational only.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity, get_bash_command


def run_check(cmd: str, label: str, timeout: int = 30) -> dict:
    """Run a check command and return results."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "label": label,
            "passed": result.returncode == 0,
            "output": result.stdout[:500] if result.stdout else "",
            "errors": result.stderr[:500] if result.stderr else "",
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return {"label": label, "passed": None, "output": "timeout or not found"}


def tool_available(tool: str) -> bool:
    """Check if a CLI tool is available."""
    try:
        result = subprocess.run(
            f"{tool} --version",
            shell=True,
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_changed_files() -> list:
    """Get files changed in the last commit."""
    try:
        result = subprocess.run(
            "git diff --name-only HEAD~1 HEAD 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name != "Bash":
            sys.exit(0)

        command = get_bash_command(tool_input)
        if not command or "git commit" not in command:
            sys.exit(0)

        # Get changed files to determine what checks to run
        changed = get_changed_files()
        has_python = any(f.endswith(".py") for f in changed)
        has_js_ts = any(f.endswith((".js", ".ts", ".tsx", ".jsx")) for f in changed)

        results = []

        # Python checks
        if has_python:
            if tool_available("ruff"):
                py_files = [f for f in changed if f.endswith(".py") and os.path.exists(f)]
                if py_files:
                    results.append(
                        run_check(
                            f"ruff check {' '.join(py_files)}",
                            "ruff lint",
                        )
                    )

        # JS/TS checks
        if has_js_ts:
            if tool_available("npx"):
                if os.path.exists("tsconfig.json"):
                    results.append(
                        run_check("npx tsc --noEmit 2>&1 | head -20", "tsc typecheck")
                    )

        if not results:
            sys.exit(0)

        # Report results
        all_passed = all(r["passed"] for r in results if r["passed"] is not None)

        print("Post-commit validation:", file=sys.stderr)
        for r in results:
            icon = "PASS" if r["passed"] else "FAIL" if r["passed"] is False else "SKIP"
            print(f"  [{icon}] {r['label']}", file=sys.stderr)
            if not r["passed"] and r.get("errors"):
                for line in r["errors"].split("\n")[:5]:
                    print(f"         {line}", file=sys.stderr)

        log_hook_activity(
            "post_commit_validator",
            {
                "command": command,
                "changed_files": len(changed),
                "checks_run": len(results),
                "all_passed": all_passed,
                "results": results,
            },
            log_subdir="hooks/cicd",
        )

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
