#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from utils.constants import ensure_session_log_dir

# Import event buffer for Langfuse integration
try:
    from utils.event_buffer import get_default_buffer
    HAS_EVENT_BUFFER = True
except ImportError:
    HAS_EVENT_BUFFER = False

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Extract session_id
        session_id = input_data.get('session_id', 'unknown')
        
        # Ensure session log directory exists
        log_dir = ensure_session_log_dir(session_id)
        log_path = log_dir / 'post_tool_use.json'
        
        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        # Buffer event for Langfuse integration
        if HAS_EVENT_BUFFER:
            try:
                buffer = get_default_buffer()

                # DEBUG: Log all available fields
                debug_log = Path.home() / ".claude" / "logs" / "post_tool_debug.log"
                debug_log.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with open(debug_log, "a") as f:
                        f.write(f"\n{'='*60}\n")
                        f.write(f"[{datetime.now().isoformat()}] PostToolUse Hook Fired\n")
                        f.write(f"{'='*60}\n")
                        f.write(f"Session ID: {session_id}\n")
                        f.write(f"Input data keys: {list(input_data.keys())}\n")
                        # Don't dump full output as it could be very long
                        f.write(f"tool_name: {input_data.get('tool_name', 'unknown')}\n")
                        f.write(f"exit_code: {input_data.get('exit_code', 'N/A')}\n")
                        f.write(f"error: {input_data.get('error', 'N/A')}\n")
                        output_len = len(str(input_data.get('output', '')))
                        f.write(f"output length: {output_len} chars\n")
                        f.write(f"{'='*60}\n")
                except Exception as log_err:
                    pass  # Ignore logging errors

                # Extract tool information
                output = input_data.get('output', '')
                error = input_data.get('error')
                tool_name = input_data.get('tool_name', 'unknown')

                # If tool_name is unknown, try alternate field names
                if tool_name == 'unknown':
                    tool_name = input_data.get('name') or \
                               input_data.get('tool') or \
                               input_data.get('Tool') or \
                               input_data.get('TOOL_NAME') or \
                               'unknown'

                event = {
                    "hook_event_type": "PostToolUse",
                    "timestamp": datetime.now().isoformat(),
                    "tool_name": tool_name,
                    "output": str(output)[:2000],  # Truncate long outputs
                    "error": error,
                    "exit_code": input_data.get('exit_code', 0)
                }
                buffer.add_event(session_id, event)

                # Log the extracted values
                try:
                    with open(debug_log, "a") as f:
                        f.write(f"[EXTRACTED] tool_name='{tool_name}', exit_code={event['exit_code']}\n")
                except:
                    pass

            except Exception as e:
                # Log error but don't crash
                import traceback
                try:
                    debug_log = Path.home() / ".claude" / "logs" / "post_tool_debug.log"
                    with open(debug_log, "a") as f:
                        f.write(f"[ERROR] {e}\n{traceback.format_exc()}\n")
                except:
                    pass

        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Exit cleanly on any other error
        sys.exit(0)

if __name__ == '__main__':
    main()