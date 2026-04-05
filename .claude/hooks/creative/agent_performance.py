#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Agent Performance Logger — SubagentStart/SubagentStop Hook

Tracks agent execution times and success rates:
  - SubagentStart: Record start time
  - SubagentStop:  Calculate duration, log result

Logs to: logs/hooks/creative/agent_performance.json
Dashboard aggregation available via the justfile.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity


# In-session tracking file for start times
TRACKING_FILE = Path.cwd() / "logs" / "hooks" / "creative" / "agent_tracking.json"


def load_tracking() -> dict:
    """Load active agent tracking data."""
    if TRACKING_FILE.exists():
        try:
            with open(TRACKING_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return {}


def save_tracking(data: dict):
    """Save agent tracking data."""
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def handle_start(input_data: dict):
    """Handle SubagentStart event."""
    agent_id = input_data.get("agent_id", "unknown")
    agent_type = input_data.get("agent_type", "unknown")
    prompt = input_data.get("prompt", "")

    tracking = load_tracking()
    tracking[agent_id] = {
        "agent_type": agent_type,
        "start_time": time.time(),
        "start_iso": datetime.now().isoformat(),
        "prompt_preview": prompt[:200] if prompt else "",
    }
    save_tracking(tracking)

    log_hook_activity(
        "agent_performance",
        {
            "event": "start",
            "agent_id": agent_id,
            "agent_type": agent_type,
            "prompt_preview": prompt[:100],
        },
        log_subdir="hooks/creative",
    )

    print(
        f"Agent started: {agent_type} ({agent_id[:12]}...)",
        file=sys.stderr,
    )


def handle_stop(input_data: dict):
    """Handle SubagentStop event."""
    agent_id = input_data.get("agent_id", "unknown")
    agent_type = input_data.get("agent_type", "unknown")
    result = input_data.get("result", "")

    tracking = load_tracking()
    start_info = tracking.pop(agent_id, None)
    save_tracking(tracking)

    duration = None
    if start_info and "start_time" in start_info:
        duration = round(time.time() - start_info["start_time"], 2)

    log_entry = {
        "event": "stop",
        "agent_id": agent_id,
        "agent_type": agent_type,
        "duration_seconds": duration,
        "result_length": len(str(result)),
        "result_preview": str(result)[:200],
    }

    log_hook_activity(
        "agent_performance",
        log_entry,
        log_subdir="hooks/creative",
    )

    duration_str = f"{duration}s" if duration else "unknown"
    print(
        f"Agent finished: {agent_type} ({agent_id[:12]}...) — {duration_str}",
        file=sys.stderr,
    )


def main():
    try:
        input_data = read_hook_input()

        event = input_data.get("hook_event_name", "")

        if event == "SubagentStart":
            handle_start(input_data)
        elif event == "SubagentStop":
            handle_stop(input_data)

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
