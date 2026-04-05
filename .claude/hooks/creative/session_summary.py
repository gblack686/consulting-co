#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Session Summary — Stop Hook

Generates a structured summary of what was accomplished this session:
  - Files changed (from git diff)
  - Hook activity summary
  - Session duration
  - Key operations performed

Output: .claude/logs/sessions/{date}_{time}_summary.md
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input


def run_command(cmd: str, timeout: int = 10) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_git_changes() -> dict:
    """Get files changed since session start (uncommitted + recent commits)."""
    staged = run_command("git diff --cached --name-only")
    unstaged = run_command("git diff --name-only")
    untracked = run_command("git ls-files --others --exclude-standard")

    return {
        "staged": staged.split("\n") if staged else [],
        "unstaged": unstaged.split("\n") if unstaged else [],
        "untracked": untracked.split("\n") if untracked else [],
    }


def get_recent_commits(limit: int = 5) -> list:
    """Get recent commits from this session."""
    output = run_command(
        f'git log --oneline --since="4 hours ago" -n {limit}'
    )
    return output.split("\n") if output else []


def get_hook_activity_summary() -> dict:
    """Summarize hook activity from log files."""
    log_dirs = [
        Path.cwd() / "logs" / "hooks" / "security",
        Path.cwd() / "logs" / "hooks" / "cicd",
        Path.cwd() / "logs" / "hooks" / "creative",
        Path.cwd() / "logs" / "hooks" / "dev",
        Path.cwd() / "logs" / "hooks" / "primitive",
    ]

    summary = {}
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        for log_file in log_dir.glob("*.json"):
            try:
                with open(log_file) as f:
                    entries = json.load(f)
                if isinstance(entries, list):
                    summary[log_file.stem] = len(entries)
            except Exception:
                continue

    return summary


def main():
    try:
        input_data = read_hook_input()

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        date_str = now.strftime("%Y-%m-%d %H:%M")

        # Gather data
        git_changes = get_git_changes()
        recent_commits = get_recent_commits()
        hook_activity = get_hook_activity_summary()
        branch = run_command("git branch --show-current")

        # Build summary
        lines = [
            f"# Session Summary — {date_str}",
            "",
            f"**Branch**: {branch or 'N/A'}",
            "",
            "## Files Changed",
            "",
        ]

        total_files = (
            len(git_changes["staged"])
            + len(git_changes["unstaged"])
            + len(git_changes["untracked"])
        )

        if total_files > 0:
            if git_changes["staged"]:
                lines.append(f"### Staged ({len(git_changes['staged'])})")
                for f in git_changes["staged"][:20]:
                    lines.append(f"- {f}")
                lines.append("")

            if git_changes["unstaged"]:
                lines.append(f"### Modified ({len(git_changes['unstaged'])})")
                for f in git_changes["unstaged"][:20]:
                    lines.append(f"- {f}")
                lines.append("")

            if git_changes["untracked"]:
                lines.append(f"### New Files ({len(git_changes['untracked'])})")
                for f in git_changes["untracked"][:20]:
                    lines.append(f"- {f}")
                lines.append("")
        else:
            lines.append("No changes detected.\n")

        if recent_commits:
            lines.append("## Recent Commits")
            lines.append("")
            for c in recent_commits:
                lines.append(f"- {c}")
            lines.append("")

        if hook_activity:
            lines.append("## Hook Activity")
            lines.append("")
            for hook, count in sorted(hook_activity.items()):
                lines.append(f"- **{hook}**: {count} events")
            lines.append("")

        # Write summary file
        output_dir = Path.cwd() / ".claude" / "logs" / "sessions"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{timestamp}_summary.md"

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(
            f"Session summary saved: {output_path.name}",
            file=sys.stderr,
        )

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
