#!/usr/bin/env python3
"""Session start context — SessionStart hook for consulting-co.

Injects second brain knowledge index + latest daily log into Claude's context
at the start of each session.
"""

import json
import sys
from pathlib import Path

SECOND_BRAIN = Path("C:/Users/gblac/OneDrive/Desktop/gbauto/gbautomation/second-brain")


def read_file_safe(path: Path, max_chars: int = 2000) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
        return text[:max_chars] if len(text) > max_chars else text
    except (FileNotFoundError, PermissionError, OSError):
        return None


def find_latest_daily() -> Path | None:
    daily_dir = SECOND_BRAIN / "daily"
    if not daily_dir.is_dir():
        return None
    md_files = sorted(daily_dir.glob("????-??-??.md"), reverse=True)
    return md_files[0] if md_files else None


def main() -> None:
    # Read hook input
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    sections: list[str] = []

    # 1. Knowledge index
    index = read_file_safe(SECOND_BRAIN / "knowledge" / "index.md")
    if index:
        sections.append(f"[Knowledge Index]\n{index}")

    # 2. Latest daily log
    latest = find_latest_daily()
    if latest:
        content = read_file_safe(latest, max_chars=1500)
        if content:
            sections.append(f"[Daily Log: {latest.stem}]\n{content}")

    if sections:
        context = "\n\n".join(sections)
        response = {
            "systemMessage": f"Second brain context loaded ({len(sections)} sections)"
        }
    else:
        response = {}

    print(json.dumps(response))


if __name__ == "__main__":
    main()
