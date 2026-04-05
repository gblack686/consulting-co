#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "langfuse",
#     "python-dotenv",
#     "python-dateutil",
#     "PyYAML",
#     "requests",
# ]
# ///
"""
Hook to log Claude Code conversations to Langfuse for observability.
Uses Langfuse SDK v3 with proper trace/generation/span structure.
Supports multi-event buffering for enhanced trace construction.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file in project root
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Debug: log if .env is not found
    import sys
    print(f"[WARNING] .env not found at {env_path}", file=sys.stderr)

# Import event buffer
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from event_buffer import get_default_buffer

def main():
    """Main hook entry point - reads stdin and buffers/processes events."""

    # Debug logging
    debug_log = Path(__file__).parent.parent / "langfuse_hook_debug.log"
    with open(debug_log, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"🔔 Hook called at {datetime.now().isoformat()}\n")

    # Check if Langfuse is enabled
    if os.getenv("ENABLE_LANGFUSE", "false").lower() != "true":
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write("❌ ENABLE_LANGFUSE not set to true\n")
        return

    # Read hook data from stdin
    hook_data = json.load(sys.stdin)

    session_id = hook_data.get("session_id", "unknown")
    transcript_path = hook_data.get("transcript_path")
    hook_event = hook_data.get("hook_event_name", "unknown")

    debug_log = Path(__file__).parent.parent / "langfuse_hook_debug.log"
    with open(debug_log, "a", encoding="utf-8") as f:
        f.write(f"📥 Hook data received:\n")
        f.write(f"  - Session ID: {session_id}\n")
        f.write(f"  - Event: {hook_event}\n")
        f.write(f"  - Transcript: {transcript_path}\n")

    # Get event buffer
    buffer = get_default_buffer()

    # PHASE 1: Buffer all events
    # Buffer this event for later trace construction
    event_entry = {
        "hook_event_type": hook_event,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "hook_data": hook_data
    }
    buffer.add_event(session_id, event_entry)

    with open(debug_log, "a", encoding="utf-8") as f:
        f.write(f"📌 Buffered event: {hook_event}\n")
        f.write(f"   Total events in session: {buffer.get_session_size(session_id)}\n")

    # Only send to Langfuse on Stop event
    if hook_event != "Stop":
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"⏭️  Buffering for later trace construction\n")
        return

    with open(debug_log, "a", encoding="utf-8") as f:
        f.write(f"🛑 Stop event received - building trace from buffered events\n")

    if not transcript_path or not Path(transcript_path).exists():
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"❌ Transcript not found: {transcript_path}\n")
        print(f"✗ Transcript not found: {transcript_path}", file=sys.stderr)
        return

    # Read transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_lines = f.readlines()

    # Parse JSONL
    messages = [json.loads(line) for line in transcript_lines if line.strip()]

    # Extract last user/assistant exchange
    # Find the most recent user message, then the assistant response that follows
    user_message = None
    assistant_message = None
    tool_calls = []
    model_name = None
    usage_data = None
    start_timestamp = None
    end_timestamp = None

    # Claude Code transcript format: {"type": "user" or "assistant", "message": {...}}
    # Find the most recent COMPLETE exchange (user → assistant)
    # This handles cases where transcript ends with tool_results
    last_user_idx = None
    last_assistant_idx = None

    # First pass: find the most recent assistant message
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("type") == "assistant":
            last_assistant_idx = i
            break

    # If no assistant message, nothing to log
    if last_assistant_idx is None:
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"❌ No assistant message found in transcript\n")
        print("✗ No assistant message found in transcript", file=sys.stderr)
        return

    # Second pass: find the user message BEFORE the assistant message
    for i in range(last_assistant_idx - 1, -1, -1):
        if messages[i].get("type") == "user":
            message = messages[i].get("message", {})
            content = message.get("content")

            # Skip if this is a tool_result (tool output, not user input)
            is_tool_result = False
            if isinstance(content, list) and content:
                first_item = content[0]
                if isinstance(first_item, dict) and first_item.get("type") == "tool_result":
                    is_tool_result = True

            if not is_tool_result:
                last_user_idx = i
                break

    # If we found a user message and assistant message, use them
    if last_user_idx is not None and last_assistant_idx is not None:
        user_msg = messages[last_user_idx]
        message = user_msg.get("message", {})
        content = message.get("content")
        start_timestamp = user_msg.get("timestamp")

        # Content can be: string (plain text), dict (tool_result), or list (structured messages)
        if isinstance(content, str):
            # Plain text content
            user_message = content
        elif isinstance(content, dict):
            # Tool result or other structured content
            user_message = content.get("content", "") or content.get("text", "")
        elif isinstance(content, list) and content:
            # Structured message list - extract text from first text content block
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    user_message = block.get("text", "")
                    break
            # If no text block, try tool_result content
            if not user_message and len(content) > 0:
                first_block = content[0]
                if isinstance(first_block, dict):
                    user_message = first_block.get("content", "") or first_block.get("text", "")

        # Extract the assistant message we found in the first pass
        if last_assistant_idx is not None:
            assistant_msg = messages[last_assistant_idx]
            message = assistant_msg.get("message", {})
            content = message.get("content")

            # Extract model name and usage from message
            model_name = message.get("model")
            usage_data = message.get("usage")
            end_timestamp = assistant_msg.get("timestamp")

            # Content can be: string (plain text), dict (single message), or list (structured messages)
            if isinstance(content, str):
                # Plain text content
                assistant_message = content
            elif isinstance(content, dict):
                # Single message dict
                assistant_message = content.get("text", "") or content.get("content", "")
            elif isinstance(content, list) and content:
                # Structured message list - extract text and tool_use blocks
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            assistant_message = block.get("text", "")
                        elif block.get("type") == "tool_use":
                            tool_calls.append({
                                "name": block.get("name"),
                                "input": block.get("input", {})
                            })

    if not user_message or not assistant_message:
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"❌ No complete exchange found\n")
        print("✗ No complete exchange found in transcript", file=sys.stderr)
        return

    # Send to Langfuse
    try:
        debug_log = Path(__file__).parent.parent / "langfuse_hook_debug.log"
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"📊 Sending to Langfuse:\n")
            f.write(f"  - User message: {len(user_message)} chars\n")
            f.write(f"  - Assistant message: {len(assistant_message)} chars\n")
            f.write(f"  - Tool calls: {len(tool_calls)}\n")

        print("📊 Sending trace to Langfuse...", file=sys.stderr)

        # Get all buffered events for this session
        all_events = buffer.get_events(session_id)

        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"📋 Buffered events: {len(all_events)}\n")

        trace_to_langfuse(
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            tool_calls=tool_calls,
            model_name=model_name,
            usage_data=usage_data,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            all_events=all_events  # NEW: Pass buffered events
        )

        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"✅ Successfully logged to Langfuse\n")
            f.write(f"🗑️  Clearing event buffer for session\n")

        print(f"✓ Logged to Langfuse: session {session_id}", file=sys.stderr)

        # Clear event buffer after successful send
        buffer.clear_session(session_id)

    except Exception as e:
        debug_log = Path(__file__).parent.parent / "langfuse_hook_debug.log"
        with open(debug_log, "a", encoding="utf-8") as f:
            f.write(f"❌ Error: {e}\n")
            import traceback
            traceback.print_exception(type(e), e, e.__traceback__, file=f)

        print(f"✗ Failed to log to Langfuse: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def extract_metadata_from_events(all_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract metadata and tool information from buffered events.

    Processes all buffered events to extract:
    - User message (from UserPromptSubmit)
    - Tool calls (from PreToolUse events)
    - Tool timings (from Pre/Post pairs)
    - Model info (if available)

    Args:
        all_events: List of buffered hook events

    Returns:
        Dict with: user_message, assistant_message, tool_calls, unique_tools, etc.
    """
    # Debug logging
    debug_log = Path(__file__).parent.parent / "extraction_debug.log"

    def log_debug(msg: str) -> None:
        """Write debug message to log file."""
        try:
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] {msg}\n")
        except Exception:
            pass  # Ignore logging errors

    log_debug("="*60)
    log_debug("🔍 EXTRACTION STARTED")
    log_debug("="*60)
    log_debug(f"Total events to process: {len(all_events)}")

    # Log all event types present
    event_types_present = {}
    for event in all_events:
        et = event.get("hook_event_type", "unknown")
        event_types_present[et] = event_types_present.get(et, 0) + 1
    log_debug(f"Event types present: {event_types_present}")

    metadata = {
        "user_message": "",
        "assistant_message": "",
        "tool_calls": [],
        "unique_tools": [],
        "model_name": None,
        "event_count": len(all_events)
    }

    # Group events by type
    user_prompts = []
    pre_tools = {}  # Map: (timestamp, tool_name) → PreToolUse event
    post_tools = {}  # Map: (timestamp, tool_name) → PostToolUse event

    for event in all_events:
        event_type = event.get("hook_event_type")

        if event_type == "UserPromptSubmit":
            user_prompts.append(event)
            log_debug(f"✓ Found UserPromptSubmit: '{event.get('input', '')[:50]}'")
        elif event_type == "PreToolUse":
            # Extract tool_name from root level first, then try nested hook_data
            tool_name = event.get("tool_name")
            if not tool_name and 'hook_data' in event:
                tool_name = event['hook_data'].get('tool_name', 'unknown')
            if not tool_name:
                tool_name = 'unknown'

            # DEBUG: If tool_name is unknown, dump the entire event structure
            if tool_name == 'unknown':
                log_debug(f"⚠️ PreToolUse has unknown tool_name. Full event structure:")
                log_debug(f"  Root-level keys: {sorted(event.keys())}")
                if 'hook_data' in event:
                    log_debug(f"  hook_data keys: {sorted(event['hook_data'].keys())}")
                    log_debug(f"  hook_data type: {type(event['hook_data'])}")
                    # Try to extract from various possible field names
                    possible_names = [
                        ('hook_data.tool_name', event['hook_data'].get('tool_name')),
                        ('hook_data.name', event['hook_data'].get('name')),
                        ('hook_data.tool', event['hook_data'].get('tool')),
                        ('hook_data.Tool', event['hook_data'].get('Tool')),
                        ('hook_data.input', event['hook_data'].get('input')),
                        ('hook_data.tool_input', event['hook_data'].get('tool_input')),
                    ]
                    log_debug(f"  Possible tool_name locations:")
                    for field_name, value in possible_names:
                        if value:
                            log_debug(f"    ✓ {field_name}: {value}")
                        else:
                            log_debug(f"    - {field_name}: empty/None")
                else:
                    log_debug(f"  ⚠️ No hook_data field present!")

            key = (event.get("timestamp"), tool_name)
            pre_tools[key] = event
            log_debug(f"✓ Found PreToolUse: tool_name='{tool_name}', timestamp={event.get('timestamp')}")
        elif event_type == "PostToolUse":
            # Extract tool_name from root level first, then try nested hook_data
            tool_name = event.get("tool_name")
            if not tool_name and 'hook_data' in event:
                tool_name = event['hook_data'].get('tool_name', 'unknown')
            if not tool_name:
                tool_name = 'unknown'

            # DEBUG: If tool_name is unknown, dump the entire event structure
            if tool_name == 'unknown':
                log_debug(f"⚠️ PostToolUse has unknown tool_name. Full event structure:")
                log_debug(f"  Root-level keys: {sorted(event.keys())}")
                if 'hook_data' in event:
                    log_debug(f"  hook_data keys: {sorted(event['hook_data'].keys())}")
                    log_debug(f"  hook_data type: {type(event['hook_data'])}")
                    # Try to extract from various possible field names
                    possible_names = [
                        ('hook_data.tool_name', event['hook_data'].get('tool_name')),
                        ('hook_data.name', event['hook_data'].get('name')),
                        ('hook_data.tool', event['hook_data'].get('tool')),
                        ('hook_data.Tool', event['hook_data'].get('Tool')),
                        ('hook_data.output', event['hook_data'].get('output')),
                        ('hook_data.tool_response', event['hook_data'].get('tool_response')),
                    ]
                    log_debug(f"  Possible tool_name locations:")
                    for field_name, value in possible_names:
                        if value:
                            log_debug(f"    ✓ {field_name}: {str(value)[:100]}")
                        else:
                            log_debug(f"    - {field_name}: empty/None")
                else:
                    log_debug(f"  ⚠️ No hook_data field present!")

            key = (event.get("timestamp"), tool_name)
            post_tools[key] = event
            log_debug(f"✓ Found PostToolUse: tool_name='{tool_name}', exit_code={event.get('exit_code', 'N/A')}")

    log_debug(f"Grouped events: {len(pre_tools)} PreToolUse, {len(post_tools)} PostToolUse, {len(user_prompts)} UserPrompt")

    # Extract user message (from most recent UserPromptSubmit)
    if user_prompts:
        last_prompt = sorted(user_prompts, key=lambda e: e.get("timestamp", ""))[-1]
        metadata["user_message"] = last_prompt.get("input", "")
        log_debug(f"Extracted user message: '{metadata['user_message'][:50]}'")

    # Extract and match tool calls
    log_debug(f"\n📍 Starting tool call matching...")
    tool_sequence = 1
    for (ts, tool_name), pre_event in pre_tools.items():
        log_debug(f"\n  Processing PreToolUse #{tool_sequence}: {tool_name}")
        log_debug(f"    Timestamp: {ts}")

        # Extract input from root level or nested hook_data
        input_data = pre_event.get("input", "")
        if not input_data and 'hook_data' in pre_event:
            input_data = pre_event['hook_data'].get('input', "")

        description = pre_event.get("description", "")
        if not description and 'hook_data' in pre_event:
            description = pre_event['hook_data'].get('description', "")

        tool_call = {
            "name": tool_name,
            "input": input_data,
            "description": description,
            "timestamp": ts,
            "sequence": tool_sequence
        }
        tool_sequence += 1

        # Try to find matching PostToolUse by looking for closest subsequent event
        matching_post = None
        closest_time_diff = float('inf')

        for (post_ts, post_tool), post_event in post_tools.items():
            if post_tool == tool_name:
                try:
                    # Parse timestamps and calculate difference
                    pre_time = datetime.fromisoformat(ts)
                    post_time = datetime.fromisoformat(post_ts)

                    if post_time >= pre_time:  # PostToolUse must be after PreToolUse
                        time_diff = (post_time - pre_time).total_seconds()
                        log_debug(f"    Candidate PostToolUse: time_diff={time_diff:.3f}s")

                        if time_diff < closest_time_diff:
                            closest_time_diff = time_diff
                            matching_post = post_event
                            log_debug(f"    → Selected as best match")
                except (ValueError, TypeError) as e:
                    log_debug(f"    ✗ Error parsing timestamps: {e}")
                    pass  # Skip if timestamp parsing fails

        if matching_post:
            # Extract output from root level or nested hook_data
            output = matching_post.get("output", "")
            if not output and 'hook_data' in matching_post:
                output = matching_post['hook_data'].get('output', "")

            error = matching_post.get("error")
            if error is None and 'hook_data' in matching_post:
                error = matching_post['hook_data'].get('error')

            tool_call["output"] = output
            tool_call["error"] = error
            tool_call["latency_ms"] = int(closest_time_diff * 1000)
            tool_call["status"] = "error" if error else "success"
            log_debug(f"    ✅ MATCHED: status={tool_call['status']}, latency={tool_call['latency_ms']}ms")
        else:
            tool_call["latency_ms"] = 0
            tool_call["status"] = "unknown"
            log_debug(f"    ❌ NO MATCH: No PostToolUse found for {tool_name}")

        metadata["tool_calls"].append(tool_call)

    # Track unique tool names in order of appearance
    metadata["unique_tools"] = list(dict.fromkeys(
        [tc["name"] for tc in metadata["tool_calls"]]
    ))

    log_debug(f"\n{'='*60}")
    log_debug(f"📊 EXTRACTION COMPLETE")
    log_debug(f"{'='*60}")
    log_debug(f"Extracted {len(metadata['tool_calls'])} tool calls")
    log_debug(f"Unique tools: {metadata['unique_tools']}")
    log_debug(f"Total latency: {sum(tc.get('latency_ms', 0) for tc in metadata['tool_calls'])}ms")
    log_debug("")

    return metadata


def trace_to_langfuse(session_id: str, user_message: str, assistant_message: str, tool_calls: list,
                      model_name: str = None, usage_data: dict = None,
                      start_timestamp: str = None, end_timestamp: str = None, all_events: list = None):
    """Send properly structured trace to Langfuse using SDK v3.

    Args:
        all_events: (NEW for Phase 1) All buffered events for this session
    """

    from langfuse import get_client
    from dateutil import parser as date_parser

    # Import tool timing utility and trace builder
    # Try local first, then global
    try:
        sys.path.insert(0, str(Path(__file__).parent / "utils"))
        from tool_timing import get_session_timings, get_total_tool_latency_ms
        from langfuse_config import LangfuseConfig
        from trace_builder import TraceBuilder  # NEW for Phase 2
    except ImportError:
        # Fall back to global hooks
        sys.path.insert(0, str(Path.home() / ".claude" / "hooks" / "utils"))
        from tool_timing import get_session_timings, get_total_tool_latency_ms
        from langfuse_config import LangfuseConfig
        from trace_builder import TraceBuilder  # NEW for Phase 2

    # Debug logging
    debug_log = Path(__file__).parent.parent / "langfuse_hook_debug.log"

    # Use smart configuration to detect organization and credentials
    config = LangfuseConfig()
    organization, project_name_from_path = config.detect_organization()

    # Determine project name: path detection first, then env, then cwd
    project_name = project_name_from_path or os.getenv("PROJECT_NAME", Path.cwd().name)

    # Get credentials for the detected organization
    creds = config.get_credentials_for_org(organization)

    # Set environment variables with correct credentials for this organization
    os.environ["LANGFUSE_PUBLIC_KEY"] = creds["public_key"]
    os.environ["LANGFUSE_SECRET_KEY"] = creds["secret_key"]

    # For RevStar organization, try to create project if it doesn't exist
    project_id = os.getenv("LANGFUSE_PROJECT_ID")
    if organization == "RevStar" and not project_id and project_name:
        project_id = config.get_or_create_project(organization, project_name)
        if project_id:
            os.environ["LANGFUSE_PROJECT_ID"] = project_id

    # Initialize Langfuse client with correct credentials now set
    langfuse = get_client()

    # Debug logging
    with open(debug_log, "a", encoding="utf-8") as f:
        f.write(f"\n📋 Project Configuration:\n")
        f.write(f"  - Organization: {organization}\n")
        f.write(f"  - Project Name: {project_name}\n")
        f.write(f"  - Project ID: {project_id}\n")
        f.write(f"  - Base URL: {os.getenv('LANGFUSE_BASE_URL')}\n")

    # Use actual model name from transcript, or fallback
    model = model_name or "claude-sonnet-4-5-20250929"

    # Extract actual token usage from Claude's response
    # Token types explained:
    # - input_tokens: Fresh input tokens (full price)
    # - output_tokens: Response tokens (full price)
    # - cache_read_input_tokens: Tokens read from cache (90% discount)
    # - cache_creation_input_tokens: Tokens written to cache (full price, one-time)
    # - thinking_tokens: Extended thinking tokens (if enabled, not present in this session)
    if usage_data:
        input_tokens = usage_data.get("input_tokens", 0)
        output_tokens = usage_data.get("output_tokens", 0)
        cache_read_tokens = usage_data.get("cache_read_input_tokens", 0)
        cache_creation_tokens = usage_data.get("cache_creation_input_tokens", 0)
        thinking_tokens = usage_data.get("thinking_tokens", 0)
    else:
        # Fallback to estimation if usage data not available
        input_tokens = int(len(user_message.split()) * 1.3)
        output_tokens = int(len(assistant_message.split()) * 1.3)
        cache_read_tokens = 0
        cache_creation_tokens = 0
        thinking_tokens = 0

    # Calculate timestamps and conversation latency
    start_time = None
    end_time = None
    conversation_latency_ms = 0
    tool_timings = {}
    total_tool_latency_ms = 0

    if start_timestamp and end_timestamp:
        try:
            start_time = date_parser.parse(start_timestamp)
            end_time = date_parser.parse(end_timestamp)
            # Calculate actual conversation latency in milliseconds
            latency_delta = end_time - start_time
            conversation_latency_ms = int(latency_delta.total_seconds() * 1000)
        except Exception as e:
            pass

    # Retrieve tool execution timings from PreToolUse/PostToolUse hooks
    try:
        tool_timings = get_session_timings(session_id)
        total_tool_latency_ms = get_total_tool_latency_ms(session_id)
    except Exception as e:
        # Gracefully handle if timing data unavailable
        pass

    # Create trace (top-level container for this conversation turn)
    # Set as current span to ensure all child observations are nested properly
    with langfuse.start_as_current_span(name=f"{project_name}-conversation") as trace_span:

        # PHASE 1: Add event information to metadata
        event_types = {}
        if all_events:
            for event in all_events:
                event_type = event.get("hook_event_type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1

        # PHASE 3 & 4: Extract subagent and agent metadata if available
        subagent_info = {}
        phase4_info = {}
        if os.getenv("ENABLE_ENHANCED_TRACING", "false").lower() == "true" and all_events:
            try:
                builder = TraceBuilder(session_id, all_events)
                # PHASE 3: Subagent hierarchy
                subagent_info = {
                    "is_subagent": builder.parent_session_id is not None,
                    "parent_session_id": builder.parent_session_id,
                    "hierarchy_depth": builder.hierarchy_depth,
                    "subagent_count": len(builder.subagent_calls)
                }
                # PHASE 4: Enhanced metadata
                phase4_info = {
                    "agent_id": builder.agent_id,
                    "source_app": builder.source_app,
                    "has_errors": builder.has_errors
                }
            except Exception:
                pass

        # Calculate tool metadata from buffered events
        tool_metadata = {
            "tool_count": {"intValue": len(tool_calls)},
            "unique_tools": [],
            "total_tool_latency_ms": {"intValue": 0}
        }

        if tool_calls:
            # Extract unique tool names
            tool_metadata["unique_tools"] = list(dict.fromkeys([tc.get("name") for tc in tool_calls]))
            # Calculate total latency from all tool calls
            total_latency = sum(tc.get("latency_ms", 0) for tc in tool_calls)
            tool_metadata["total_tool_latency_ms"] = {"intValue": total_latency}

        # Set trace-level attributes
        trace_metadata = {
            "organization": organization,  # Track which org this trace belongs to
            "project": project_name,
            "project_id": project_id,  # Explicitly include project ID
            "timestamp": datetime.now().isoformat(),
            "user_message_length": len(user_message),
            "assistant_message_length": len(assistant_message),
            **tool_metadata,  # Include tool counts, unique tools, and latency
            # PHASE 1: New event tracking
            "total_events_buffered": len(all_events) if all_events else 0,
            "event_types_captured": event_types,
            # PHASE 3: Subagent hierarchy
            **subagent_info,  # Merge subagent info
            # PHASE 4: Agent metadata
            **phase4_info  # Merge agent identity and error status
        }

        # Add conversation latency as custom metric if calculated
        if conversation_latency_ms > 0:
            trace_metadata["conversation_latency_ms"] = conversation_latency_ms
            trace_metadata["conversation_latency_seconds"] = round(conversation_latency_ms / 1000, 3)
            trace_metadata["llm_time_ms"] = max(0, conversation_latency_ms - total_tool_latency_ms)

        # Add breakdown of tool latencies
        if tool_timings:
            tool_breakdown = {}
            for tool_key, timing_data in tool_timings.items():
                tool_name = timing_data.get("tool_name", "unknown")
                latency = timing_data.get("latency_ms", 0)
                if latency:
                    if tool_name not in tool_breakdown:
                        tool_breakdown[tool_name] = {"count": 0, "total_ms": 0}
                    tool_breakdown[tool_name]["count"] += 1
                    tool_breakdown[tool_name]["total_ms"] += latency

            if tool_breakdown:
                trace_metadata["tool_breakdown"] = tool_breakdown

        langfuse.update_current_trace(
            session_id=session_id,
            tags=[organization, project_name, "claude-code", "conversation"],  # Include org for filtering
            input=user_message[:5000],  # Trace-level input (first 5000 chars of user message)
            output=assistant_message[:5000],  # Trace-level output (first 5000 chars of assistant message)
            metadata=trace_metadata
        )

        # Create generation for Claude's response as a child observation
        with langfuse.start_as_current_observation(
            name="claude-response",
            as_type="generation",
            model=model,  # Use actual model from transcript (e.g., claude-sonnet-4-5-20250929)
            input=user_message[:5000],  # First 5000 chars
            model_parameters={
                "max_tokens": 8192,  # Claude Code default
                "temperature": 1.0
            }
        ) as generation:

            # Build usage_details with all token types from actual Claude response
            # Langfuse expects "input" and "output" as base fields
            # Additional token types are passed for observability and cost calculation
            usage_details = {
                "input": input_tokens,
                "output": output_tokens,
            }

            # Add cache token types if available (Anthropic prompt caching)
            # These affect cost calculation - cache reads are 90% cheaper
            if cache_read_tokens > 0:
                usage_details["cache_read_input_tokens"] = cache_read_tokens
            if cache_creation_tokens > 0:
                usage_details["cache_creation_input_tokens"] = cache_creation_tokens

            # Add thinking tokens if available (extended thinking mode)
            if thinking_tokens > 0:
                usage_details["thinking_tokens"] = thinking_tokens

            # Note: Total token count in Langfuse may show:
            # input + cache_read + output (for display purposes)
            # But cost calculation considers cache pricing discounts

            # Build metadata for generation including latency
            generation_metadata = {}
            if conversation_latency_ms > 0:
                generation_metadata["conversation_latency_ms"] = conversation_latency_ms
                generation_metadata["conversation_latency_seconds"] = round(conversation_latency_ms / 1000, 3)

            # Update with output and actual token usage
            # Langfuse will auto-calculate cost based on model name!
            generation.update(
                output=assistant_message[:5000],  # First 5000 chars
                usage_details=usage_details,
                metadata=generation_metadata if generation_metadata else None
            )

        # Phase 3: Create tool spans from buffered events
        if all_events:
            try:
                # Extract tool calls from buffered events
                from trace_builder import TraceBuilder
                builder = TraceBuilder(session_id, all_events)

                # Create span for each matched tool call
                for tool_inv in builder.tool_pairs:
                    try:
                        tool_span = langfuse.span(
                            name=tool_inv.tool_name,
                            input=json.dumps(tool_inv.input_data, default=str),
                            output=tool_inv.output_data,
                            metadata={
                                "tool_name": tool_inv.tool_name,
                                "latency_ms": tool_inv.latency_ms,
                                "status": tool_inv.status,
                                "sequence": tool_inv.sequence_number,
                                "error": tool_inv.error_message
                            }
                        )
                    except Exception as e:
                        with open(debug_log, "a", encoding="utf-8") as f:
                            f.write(f"⚠️  Failed to create tool span for {tool_inv.tool_name}: {e}\n")
            except Exception as e:
                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"⚠️  Failed to build tool spans from events: {e}\n")

        # PHASE 2: Use TraceBuilder for enhanced trace construction if enabled
        if os.getenv("ENABLE_ENHANCED_TRACING", "false").lower() == "true" and all_events:
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"🔨 PHASE 2: Building enhanced trace from {len(all_events)} events\n")

            try:
                builder = TraceBuilder(session_id, all_events)
                observations = builder.build_observations()

                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"📊 Generated {len(observations)} observations from events\n")

                # Create observations from events
                for obs in observations:
                    obs_type = obs.get("type")
                    obs_name = obs.get("name")
                    obs_input = obs.get("input")
                    obs_output = obs.get("output")
                    obs_metadata = obs.get("metadata", {})

                    with langfuse.start_as_current_span(name=obs_name) as obs_span:
                        obs_span.update(
                            input=obs_input,
                            output=obs_output,
                            metadata=obs_metadata
                        )

                        with open(debug_log, "a", encoding="utf-8") as f:
                            f.write(f"  ✓ Created {obs_type}: {obs_name}\n")

            except Exception as e:
                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"⚠️  Error in Phase 2 trace building: {e}\n")
                    import traceback
                    traceback.print_exc(file=f)

        # FALLBACK: Create spans for each tool call with recorded latencies (for backward compatibility)
        else:
            for i, tool in enumerate(tool_calls):
                tool_name = tool.get("name", "unknown")

                # Find recorded latency for this tool
                tool_latency_ms = 0
                for timing_key, timing_data in tool_timings.items():
                    if timing_data.get("tool_name") == tool_name and timing_data.get("latency_ms"):
                        tool_latency_ms = timing_data.get("latency_ms", 0)
                        break

                with langfuse.start_as_current_span(name=f"tool-{tool_name}") as tool_span:
                    tool_span.update(
                        input=tool.get("input", {}),
                        metadata={
                            "tool_name": tool_name,
                            "tool_index": i,
                            "tool_input_preview": str(tool.get("input", {}))[:500],
                            "latency_ms": tool_latency_ms
                        }
                    )

    # Flush to ensure data is sent
    langfuse.flush()


if __name__ == "__main__":
    main()
