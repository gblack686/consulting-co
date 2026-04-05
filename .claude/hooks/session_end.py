#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Add utils to path for event_buffer and Langfuse integration
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def log_session_end(input_data):
    """Log session end event to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'session_end.json'

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Append the entire input data with timestamp
    entry = {
        **input_data,
        "logged_at": datetime.now().isoformat()
    }
    log_data.append(entry)

    # Write back to file with formatting
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def log_error(message):
    """Log error to a debug file."""
    try:
        debug_file = Path.home() / ".claude" / "logs" / "session_end_debug.log"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception as e:
        # If file logging fails, try stderr
        print(f"[LANGFUSE-DEBUG] {message}", file=sys.stderr)


def check_session_cleanup(input_data):
    """Check if session has any remaining buffered events (shouldn't happen).

    In turn-level logging, each turn's trace is sent immediately via stop.py.
    By the time session_end is called, the buffer should be empty.
    This is just a sanity check.
    """
    session_id = input_data.get('session_id', 'unknown')
    try:
        log_error(f"=== session_end.py called for session: {session_id} ===")
        log_error("(Note: Turn-level logging now sends traces via stop.py, not session_end.py)")

        try:
            from event_buffer import get_default_buffer
            buffer = get_default_buffer()

            remaining_events = buffer.get_events(session_id)
            if remaining_events:
                log_error(f"⚠️  WARNING: {len(remaining_events)} events still in buffer!")
                log_error("These should have been sent by stop.py for each turn")
                log_error(f"Events: {[e.get('hook_event_type') for e in remaining_events]}")
            else:
                log_error("✓ Buffer is clean (as expected for turn-level logging)")

        except Exception as e:
            log_error(f"Could not check buffer status: {e}")

    except Exception as e:
        log_error(f"✗ Exception: {type(e).__name__}: {str(e)}")


def save_session_statistics(input_data):
    """Save session statistics for analytics."""
    try:
        session_id = input_data.get('session_id', 'unknown')
        reason = input_data.get('reason', 'other')
        transcript_path = input_data.get('transcript_path', '')

        # Count messages in transcript if available
        message_count = 0
        if transcript_path and Path(transcript_path).exists():
            try:
                with open(transcript_path, 'r') as f:
                    # JSONL format - count lines
                    message_count = sum(1 for _ in f)
            except Exception:
                pass

        # Save statistics
        stats_dir = Path("logs")
        stats_dir.mkdir(parents=True, exist_ok=True)
        stats_file = stats_dir / 'session_statistics.json'

        if stats_file.exists():
            with open(stats_file, 'r') as f:
                try:
                    stats = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    stats = []
        else:
            stats = []

        stats.append({
            "session_id": session_id,
            "ended_at": datetime.now().isoformat(),
            "reason": reason,
            "message_count": message_count
        })

        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

    except Exception:
        pass  # Don't fail the hook on stats errors


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--announce', action='store_true',
                          help='Announce session end via TTS')
        parser.add_argument('--save-stats', action='store_true',
                          help='Save session statistics')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract fields
        session_id = input_data.get('session_id', 'unknown')
        reason = input_data.get('reason', 'other')

        # Check session cleanup (buffer should be empty from turn-level logging)
        check_session_cleanup(input_data)

        # Log the session end event
        log_session_end(input_data)

        # Save session statistics if requested
        if args.save_stats:
            save_session_statistics(input_data)

        # Announce session end if requested
        if args.announce:
            try:
                # Try to use TTS to announce session end
                script_dir = Path(__file__).parent
                tts_script = script_dir / "utils" / "tts" / "pyttsx3_tts.py"

                if tts_script.exists():
                    messages = {
                        "clear": "Session cleared",
                        "logout": "Logging out",
                        "prompt_input_exit": "Session ended",
                        "other": "Session ended"
                    }
                    message = messages.get(reason, "Session ended")

                    subprocess.run(
                        ["uv", "run", str(tts_script), message],
                        capture_output=True,
                        timeout=5
                    )
            except Exception:
                pass

        # Success
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()
