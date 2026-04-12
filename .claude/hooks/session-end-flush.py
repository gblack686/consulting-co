#!/usr/bin/env python3
"""Session end flush — Stop hook for consulting-co.

Appends a timestamped 'session ended' entry to today's daily log.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
DAILY_DIR = Path("C:/Users/gblac/OneDrive/Desktop/gbauto/gbautomation/second-brain/daily")

FRONTMATTER_TEMPLATE = """---
type: daily
title: GBAutomation — {date}
date: {date}
tags: [daily, gbautomation, auto]
generated_by: claude-code-hooks
---
"""


def ensure_daily_log(date_str: str) -> Path:
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    path = DAILY_DIR / f"{date_str}.md"
    if not path.exists():
        path.write_text(FRONTMATTER_TEMPLATE.format(date=date_str).lstrip(), encoding="utf-8")
    return path


def main() -> None:
    # Read hook input
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    now = datetime.now(TZ)
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H:%M:%S %Z")

    log_path = ensure_daily_log(date_str)

    entry = f"\n- **{timestamp}** -- Claude Code session ended (consulting-co)\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)

    # Valid Stop hook response
    response = {}
    print(json.dumps(response))


if __name__ == "__main__":
    main()
