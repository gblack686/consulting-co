#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
{{EVENT_TYPE}} Hook — [Description]

Trigger: {{EVENT_TYPE}} event
Matcher: [tool_name or *]

What it does:
- [Describe behavior]
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for shared utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import (
    read_hook_input,
    hook_response,
    log_hook_activity,
)


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # --- Your hook logic here ---

        # Example: Log activity
        log_hook_activity(
            "new_hook",
            {
                "tool_name": tool_name,
                "event": "{{EVENT_TYPE}}",
            },
            log_subdir="hooks/dev"
        )

        # Allow the tool call to proceed
        sys.exit(0)

    except Exception:
        # Always exit 0 on error to avoid blocking
        sys.exit(0)


if __name__ == "__main__":
    main()
