#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "langfuse",
# ]
# ///

import argparse
import json
import os
import sys
import random
import subprocess
import time
from pathlib import Path
from datetime import datetime
from utils.constants import ensure_session_log_dir

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Add utils to path for event_buffer and Langfuse integration
sys.path.insert(0, str(Path(__file__).parent / "utils"))

# Import turn counter
from turn_counter import get_default_counter


def get_completion_messages():
    """Return list of friendly completion messages."""
    return [
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!",
    ]


def load_hook_settings():
    """Load hook settings from shared config file.

    Settings are stored in ~/.claude/hook_settings.json and shared
    between the orchestrator frontend and hooks.

    Returns:
        dict: Hook settings with defaults applied
    """
    settings_path = Path.home() / ".claude" / "hook_settings.json"
    default_settings = {"ttsNotificationsEnabled": True}

    try:
        if settings_path.exists():
            return json.loads(settings_path.read_text())
    except Exception:
        pass

    return default_settings


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"

    # Check for ElevenLabs API key (highest priority)
    if os.getenv("ELEVENLABS_API_KEY"):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv("OPENAI_API_KEY"):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None


def log_turn_error(message):
    """Log error to turn debug file."""
    try:
        debug_file = Path.home() / ".claude" / "logs" / "stop_send_turn_debug.log"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception as e:
        print(f"[TURN-DEBUG] {message}", file=sys.stderr)


def extract_all_generations(transcript_path):
    """Extract ALL generations from current turn in Claude Code transcript for Phase 4.

    Detects each assistant message in the CURRENT TURN as a separate generation,
    enabling tracking of multi-turn model calls within a single user turn.

    CRITICAL: Only extracts from the current turn, not the entire session.
    Looks for: user message → (assistant message)+ → stop

    Args:
        transcript_path: Path to .jsonl transcript file

    Returns:
        List of generation dicts with:
        - sequence: Order of generation (1-indexed)
        - content: Assistant message text
        - input_tokens: Input tokens for this generation
        - output_tokens: Output tokens for this generation
        - cache_read_tokens: Cache read tokens (if applicable)
        - cache_creation_tokens: Cache creation tokens (if applicable)
        - thinking_tokens: Thinking tokens (if applicable)
        - is_final: Whether this is the final generation in the turn
    """
    generations = []

    try:
        if not transcript_path or not Path(transcript_path).exists():
            log_turn_error(f"Transcript not found for multi-gen extraction: {transcript_path}")
            return generations

        # Read transcript from the END backwards to find current turn
        # Current turn = most recent user message → most recent stop/system event
        all_lines = []
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        all_lines.append((line, json.loads(line)))
                    except json.JSONDecodeError:
                        continue

        if not all_lines:
            log_turn_error("No valid JSON lines in transcript")
            return generations

        # Find the most recent user message (start of current turn)
        current_turn_start_idx = -1
        for idx in range(len(all_lines) - 1, -1, -1):
            line, msg = all_lines[idx]
            # Look for user message (not system, not file-history)
            if msg.get("type") == "user":
                current_turn_start_idx = idx
                break

        if current_turn_start_idx == -1:
            log_turn_error("No user message found in transcript (likely system event)")
            return generations

        log_turn_error(f"Current turn starts at line {current_turn_start_idx}")

        # Extract only assistant messages AFTER the user message in current turn
        for idx in range(current_turn_start_idx + 1, len(all_lines)):
            line, message = all_lines[idx]

            # Stop at system events (stop hook, etc) that end the turn
            if message.get("type") == "system" or message.get("subtype") == "stop_hook_summary":
                log_turn_error(f"Current turn ends at line {idx} (system event)")
                break

            # Extract assistant messages
            if message.get("type") == "assistant":
                msg_data = message.get("message", {})
                usage = msg_data.get("usage", {})

                # Extract content - handle both list and string formats
                content = ""
                if isinstance(msg_data.get("content"), list):
                    # Content is a list of items (text, thinking, etc)
                    for item in msg_data.get("content", []):
                        if isinstance(item, dict) and item.get("type") == "text":
                            content += item.get("text", "")
                elif isinstance(msg_data.get("content"), str):
                    content = msg_data.get("content", "")

                if usage or content:
                    generation = {
                        "sequence": len(generations) + 1,
                        "content": content[:1000] if content else "",  # Truncate very long content
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
                        "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
                        "thinking_tokens": usage.get("thinking_tokens", 0),
                        "is_final": False  # Will set below
                    }
                    generations.append(generation)
                    log_turn_error(f"Extracted Gen #{generation['sequence']}: in={usage.get('input_tokens', 0)}, out={usage.get('output_tokens', 0)}")

        # Mark the last generation as final
        if generations:
            generations[-1]["is_final"] = True
            log_turn_error(f"Found {len(generations)} generations in CURRENT TURN (not session)")
            for gen in generations:
                log_turn_error(f"  Gen #{gen['sequence']}: in={gen['input_tokens']}, out={gen['output_tokens']}, final={gen['is_final']}")
        else:
            log_turn_error("No generations extracted for current turn")

    except Exception as e:
        log_turn_error(f"Error extracting all generations: {type(e).__name__}: {str(e)}")
        import traceback
        log_turn_error(traceback.format_exc())

    return generations


def extract_token_counts(transcript_path):
    """Extract token counts from Claude Code transcript (last generation).

    PHASE 3 COMPATIBILITY: Extracts only the final/last generation for backward compatibility.
    For Phase 4+ use extract_all_generations() instead.

    Args:
        transcript_path: Path to .jsonl transcript file

    Returns:
        Dict with input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens
    """
    token_counts = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_creation_tokens": 0,
        "thinking_tokens": 0
    }

    try:
        # Use the new multi-generation extractor and get the final one
        generations = extract_all_generations(transcript_path)
        if generations:
            final_gen = generations[-1]
            token_counts["input_tokens"] = final_gen.get("input_tokens", 0)
            token_counts["output_tokens"] = final_gen.get("output_tokens", 0)
            token_counts["cache_read_tokens"] = final_gen.get("cache_read_tokens", 0)
            token_counts["cache_creation_tokens"] = final_gen.get("cache_creation_tokens", 0)
            token_counts["thinking_tokens"] = final_gen.get("thinking_tokens", 0)

            log_turn_error(f"Found usage: in={token_counts['input_tokens']}, out={token_counts['output_tokens']}, cache_read={token_counts['cache_read_tokens']}")

    except Exception as e:
        log_turn_error(f"Error extracting tokens: {type(e).__name__}: {str(e)}")

    return token_counts


def send_turn_trace_to_langfuse(session_id, input_data=None):
    """Send completed turn's trace to Langfuse immediately.

    This is called after Claude finishes responding (stop event).
    Sends one trace per turn (conversation turn, not session).
    Clears buffer after successful send.

    Args:
        session_id: Session ID
        input_data: Hook input data containing transcript_path and other metadata
    """
    try:
        log_turn_error(f"=== Sending turn trace for session: {session_id} ===")

        # Check if Langfuse is enabled
        enable_langfuse = os.getenv("ENABLE_LANGFUSE", "false").lower() == "true"
        if not enable_langfuse:
            log_turn_error("Langfuse not enabled, skipping")
            return

        # Check credentials
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        if not public_key or not secret_key:
            log_turn_error("Missing Langfuse credentials")
            return

        log_turn_error("✓ Langfuse enabled with credentials")

        # Import event buffer
        from event_buffer import get_default_buffer
        buffer = get_default_buffer()
        log_turn_error("✓ Imported event_buffer")

        # Get all buffered events for this turn
        all_events = buffer.get_events(session_id)
        log_turn_error(f"Retrieved {len(all_events)} events for turn")

        if not all_events:
            log_turn_error("No events to send, skipping")
            return

        # Import Langfuse integration
        from log_to_langfuse import trace_to_langfuse, extract_metadata_from_events
        log_turn_error("✓ Imported log_to_langfuse")

        # Extract metadata from events
        metadata = extract_metadata_from_events(all_events)
        log_turn_error(f"Extracted metadata: tools={metadata.get('unique_tools', [])}")

        # Extract token counts from transcript if available
        token_counts = {}
        generations = []  # NEW: For Phase 4 multi-generation support
        if input_data and "transcript_path" in input_data:
            token_counts = extract_token_counts(input_data.get("transcript_path"))
            log_turn_error(f"Extracted tokens: {token_counts}")

            # NEW: Also extract all generations for Phase 4
            generations = extract_all_generations(input_data.get("transcript_path"))
            if len(generations) > 1:
                log_turn_error(f"Phase 4: Detected {len(generations)} total generations in this turn")

        # Get organization and project from environment
        organization = os.getenv("ORGANIZATION", "consulting-co")
        project = os.getenv("PROJECT_NAME", "consulting-co")

        # Add timestamp to trace name to differentiate turns
        timestamp = datetime.now().strftime("%H%M%S")

        # Send turn trace to Langfuse
        log_turn_error(f"Sending turn trace to Langfuse: {organization}/{project} (ts:{timestamp})")
        trace_to_langfuse(
            session_id=session_id,
            organization=organization,
            project_name=project,
            user_message=metadata.get("user_message", ""),
            assistant_message=metadata.get("assistant_message", ""),
            tool_calls=metadata.get("tool_calls", []),
            tool_timings={},
            model_name=metadata.get("model_name", "claude-3-5-sonnet"),
            all_events=all_events,
            token_counts=token_counts,  # PHASE 3: Pass token counts (final generation)
            generations=generations  # PHASE 4: Pass all generations
        )

        # Clear buffer after successful send (ready for next turn)
        buffer.clear_session(session_id)
        log_turn_error(f"✓ Turn trace sent and buffer cleared for next turn")

    except Exception as e:
        log_turn_error(f"✗ Exception sending turn trace: {type(e).__name__}: {str(e)}")
        import traceback
        log_turn_error(traceback.format_exc())


def call_mini_doc_agent(session_id, input_data):
    """Call mini-doc-agent to record turn details."""
    try:
        log_turn_error(f"Calling mini-doc-agent for session: {session_id}")

        # Check if mini-doc-agent is enabled
        if os.getenv("ENABLE_MINI_DOC", "true").lower() != "true":
            log_turn_error("Mini-doc-agent disabled")
            return

        # Get mini-doc-agent script path
        script_dir = Path(__file__).parent
        mini_doc_script = script_dir / "mini_doc_agent.py"

        if not mini_doc_script.exists():
            log_turn_error("mini-doc-agent script not found")
            return

        # Call mini-doc-agent with input data
        import subprocess
        result = subprocess.run(
            ["uv", "run", str(mini_doc_script), "--session-id", session_id],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            log_turn_error("✓ mini-doc-agent completed")
        else:
            log_turn_error(f"✗ mini-doc-agent failed: {result.stderr}")

    except Exception as e:
        log_turn_error(f"Error calling mini-doc-agent: {type(e).__name__}: {str(e)}")


def check_and_trigger_review(session_id, input_data):
    """Check if review should be triggered and call trace review agent."""
    try:
        log_turn_error(f"Checking if review needed for session: {session_id}")

        # Get turn counter
        counter = get_default_counter()

        # Get current turn count
        stats = counter.get_session_stats(session_id)
        if not stats:
            log_turn_error("No session stats found")
            return

        turn_count = stats["turn_count"]
        log_turn_error(f"Current turn count: {turn_count}")

        # Check if review is needed
        review_interval = int(os.getenv("REVIEW_INTERVAL", "10"))
        if counter.should_review(session_id, review_interval):
            log_turn_error(f"Review needed at turn {turn_count}")

            # Call trace review agent
            script_dir = Path(__file__).parent
            review_script = script_dir / "trace_review_agent.py"

            if not review_script.exists():
                log_turn_error("trace_review_agent script not found")
                return

            transcript_path = input_data.get("transcript_path", "")

            import subprocess
            result = subprocess.run(
                [
                    "uv", "run", str(review_script),
                    "--session-id", session_id,
                    "--transcript-path", transcript_path,
                    "--turn-count", str(turn_count)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                log_turn_error("✓ Trace review completed")
                # Mark as reviewed
                counter.mark_reviewed(session_id)
            else:
                log_turn_error(f"✗ Trace review failed: {result.stderr}")

    except Exception as e:
        log_turn_error(f"Error checking/triggering review: {type(e).__name__}: {str(e)}")
        import traceback
        log_turn_error(traceback.format_exc())


def buffer_stop_event(session_id, input_data):
    """Buffer stop event to SQLite for Langfuse integration."""
    # Always write a marker file to confirm this function is called
    try:
        debug_dir = Path.home() / ".claude" / "logs"
        debug_dir.mkdir(parents=True, exist_ok=True)
        with open(debug_dir / "stop_buffer_called.txt", 'a') as f:
            f.write(f"{datetime.now().isoformat()} - session:{session_id}\n")
    except:
        pass

    try:
        from event_buffer import get_default_buffer
        buffer = get_default_buffer()
        buffer.add_event(session_id, {
            "hook_event_type": "Stop",
            "timestamp": datetime.now().isoformat(),
            "hook_data": {
                "session_id": session_id,
                "reason": input_data.get("stop_hook_active", False),
                "assistant_message": input_data.get("assistant_message", "")
            }
        })
        # Log success
        try:
            with open(Path.home() / ".claude" / "logs" / "stop_buffer_called.txt", 'a') as f:
                f.write(f"  ✓ event added\n")
        except:
            pass
    except Exception as e:
        try:
            with open(Path.home() / ".claude" / "logs" / "stop_buffer_called.txt", 'a') as f:
                f.write(f"  ✗ {type(e).__name__}: {str(e)}\n")
        except:
            pass


def get_llm_completion_message():
    """
    Generate completion message using available LLM services.
    Priority order: OpenAI > Anthropic > fallback to random message

    Returns:
        str: Generated or fallback completion message
    """
    # Get current script directory and construct utils/llm path
    script_dir = Path(__file__).parent
    llm_dir = script_dir / "utils" / "llm"

    # Try Anthropic second
    if os.getenv("ANTHROPIC_API_KEY"):
        anth_script = llm_dir / "anth.py"
        if anth_script.exists():
            try:
                result = subprocess.run(
                    ["uv", "run", str(anth_script), "--completion"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try OpenAI first (highest priority)
    if os.getenv("OPENAI_API_KEY"):
        oai_script = llm_dir / "oai.py"
        if oai_script.exists():
            try:
                result = subprocess.run(
                    ["uv", "run", str(oai_script), "--completion"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Fallback to random predefined message
    messages = get_completion_messages()
    return random.choice(messages)


def announce_completion():
    """Announce completion using the best available TTS service.

    Checks hook_settings.json for ttsNotificationsEnabled setting.
    If disabled, skips both the Haiku API call AND TTS playback.
    """
    try:
        # Check settings - if TTS is disabled, skip entirely
        settings = load_hook_settings()
        if not settings.get("ttsNotificationsEnabled", True):
            return  # TTS + Haiku disabled via settings

        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available

        # Get completion message (LLM-generated or fallback)
        completion_message = get_llm_completion_message()

        # Call the TTS script with the completion message
        subprocess.run(
            ["uv", "run", tts_script, completion_message],
            capture_output=True,  # Suppress output
            timeout=10,  # 10-second timeout
        )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Fail silently if TTS encounters issues
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--chat", action="store_true", help="Copy transcript to chat.json"
        )
        parser.add_argument(
            "--notify", action="store_true", help="Announce completion via TTS"
        )
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Extract required fields
        session_id = input_data.get("session_id", "")
        stop_hook_active = input_data.get("stop_hook_active", False)

        # Buffer stop event for Langfuse integration
        buffer_stop_event(session_id, input_data)

        # NEW: Send completed turn's trace to Langfuse immediately
        # This happens AFTER the stop event is buffered
        # Each turn (user prompt + claude response) gets its own trace
        # Pass input_data to enable token counting from transcript
        send_turn_trace_to_langfuse(session_id, input_data)

        # NEW: Increment turn counter and track this turn
        try:
            counter = get_default_counter()
            user_msg = input_data.get("user_message", "")
            assistant_msg = input_data.get("assistant_message", "")
            turn_count, last_review = counter.increment_turn(session_id, user_msg, assistant_msg)
            log_turn_error(f"Turn count incremented to {turn_count} (last review: {last_review})")
        except Exception as e:
            log_turn_error(f"Error incrementing turn counter: {type(e).__name__}: {str(e)}")

        # NEW: Call mini-doc-agent to record turn details (uses Haiku for speed)
        call_mini_doc_agent(session_id, input_data)

        # NEW: Check if review should be triggered (every 10 turns)
        check_and_trigger_review(session_id, input_data)

        # Ensure session log directory exists
        log_dir = ensure_session_log_dir(session_id)
        log_path = log_dir / "stop.json"

        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, "r") as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

        # Handle --chat switch
        if args.chat and "transcript_path" in input_data:
            transcript_path = input_data["transcript_path"]
            if os.path.exists(transcript_path):
                # Read .jsonl file and convert to JSON array
                chat_data = []
                try:
                    with open(transcript_path, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    chat_data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    pass  # Skip invalid lines

                    # Write to logs/chat.json
                    chat_file = os.path.join(log_dir, "chat.json")
                    with open(chat_file, "w") as f:
                        json.dump(chat_data, f, indent=2)
                except Exception:
                    pass  # Fail silently

        if args.notify:
            # Announce completion via TTS
            announce_completion()

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
