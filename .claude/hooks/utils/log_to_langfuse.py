#!/usr/bin/env python3
"""
Langfuse trace integration for Claude Code hooks.

Provides trace building, naming, tagging, and sending to Langfuse.
This is the main integration point for sending enhanced traces.

Phase 5B: Trace Builder + Langfuse Integration
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import trace building components
from trace_builder import TraceBuilder


def debug_log(message: str) -> None:
    """Write debug message to log file."""
    debug_file = Path.home() / ".claude" / "logs" / "langfuse_integration.log"
    debug_file.parent.mkdir(parents=True, exist_ok=True)

    with open(debug_file, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")


def generate_trace_name(user_message: str, tool_names: List[str], model: str) -> str:
    """Generate descriptive trace name from execution context.

    Format: {project}-{prompt_summary}-{tools}
    Example: consulting-co-search-obsidian-tools2

    Args:
        user_message: User's input prompt
        tool_names: List of tool names used (may have duplicates)
        model: Model name

    Returns:
        Descriptive trace name
    """
    # Extract first 2 significant words from user prompt (max 20 chars)
    words = user_message.split() if user_message else []
    prompt_summary = ""

    if words:
        # Skip common words and extract meaningful ones
        skip_words = {"the", "a", "an", "and", "or", "to", "for", "with", "of", "do", "can"}
        meaningful = [w.lower() for w in words if w.lower() not in skip_words]
        prompt_summary = "-".join(meaningful[:2])[:20] if meaningful else words[0].lower()[:20]

    if not prompt_summary:
        prompt_summary = "query"

    # Get unique tool names, preserve order
    unique_tools = list(dict.fromkeys(tool_names))

    # If too many tools, show count instead
    if len(unique_tools) > 3:
        tools_str = f"tools{len(unique_tools)}"
    else:
        tools_str = "-".join(unique_tools).lower()[:30] if unique_tools else "no-tools"

    # Build project name (from environment)
    project = os.getenv("PROJECT", "consulting-co")

    # Return: project-prompt-tools
    return f"{project}-{prompt_summary}-{tools_str}"


def generate_tags(
    tool_names: List[str],
    model_name: str,
    has_errors: bool,
    is_subagent: bool,
    hierarchy_depth: int,
    organization: str,
    project: str,
    subagent_count: int = 0
) -> List[str]:
    """Generate meaningful tags for filtering and analysis.

    Tags include:
    - Organization/Project
    - Model type (sonnet, haiku, opus)
    - Tool types used (tool:bash, tool:read, etc)
    - Status (success, error)
    - Agent type (root, subagent)
    - Hierarchy depth (for nested agents)
    - Complexity (low, medium, high based on tool count)

    Args:
        tool_names: List of tool names (may have duplicates)
        model_name: Model name/version
        has_errors: Whether trace contains errors
        is_subagent: Whether this is a subagent call
        hierarchy_depth: Nesting depth
        organization: Organization name
        project: Project name
        subagent_count: Number of subagent calls

    Returns:
        List of meaningful tags
    """
    tags = [
        organization,
        project,
        "claude-code",
    ]

    # Add model tags
    if "sonnet" in model_name.lower():
        tags.append("model:sonnet")
    elif "haiku" in model_name.lower():
        tags.append("model:haiku")
    elif "opus" in model_name.lower():
        tags.append("model:opus")
    else:
        tags.append("model:unknown")

    # Add tool tags (unique only)
    unique_tools = list(dict.fromkeys(tool_names))
    for tool in unique_tools:
        # Clean up tool name
        tool_clean = tool.lower().replace("_", "-").replace(" ", "-")
        tags.append(f"tool:{tool_clean}")

    # Add status tags
    if has_errors:
        tags.append("status:error")
    else:
        tags.append("status:success")

    # Add agent hierarchy tags
    if is_subagent:
        tags.append("agent:subagent")
    else:
        tags.append("agent:root")

    if hierarchy_depth > 1:
        tags.append(f"depth:{hierarchy_depth}")

    if subagent_count > 0:
        tags.append(f"subagents:{subagent_count}")

    # Add complexity tags based on tool count
    unique_tool_count = len(unique_tools)
    if unique_tool_count > 5:
        tags.append("complexity:high")
    elif unique_tool_count > 2:
        tags.append("complexity:medium")
    else:
        tags.append("complexity:low")

    return tags


def extract_metadata_from_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract key metadata from buffered events.

    Args:
        events: List of buffered hook events

    Returns:
        Dict with extracted metadata
    """
    user_message = ""
    tool_calls = []
    model_name = "claude-3-5-sonnet"

    for event in events:
        event_type = event.get("hook_event_type", "")
        hook_data = event.get("hook_data", {})

        # Extract user prompt
        if event_type == "UserPromptSubmit":
            user_message = hook_data.get("user_input", "")

        # Extract tool calls
        elif event_type == "PreToolUse":
            tool_name = hook_data.get("tool_name", "unknown")
            tool_calls.append(tool_name)

        # Extract model information
        if "model" in hook_data:
            model_name = hook_data.get("model", model_name)

    return {
        "user_message": user_message,
        "tool_calls": tool_calls,
        "model_name": model_name,
        "unique_tools": list(dict.fromkeys(tool_calls))  # Preserve order, remove duplicates
    }


def trace_to_langfuse(
    session_id: str,
    organization: str,
    project_name: str,
    user_message: str,
    assistant_message: str,
    tool_calls: List[str],
    tool_timings: Dict[str, int],
    model_name: str,
    all_events: List[Dict[str, Any]],
    token_counts: Optional[Dict[str, int]] = None,
    generations: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """Send enhanced trace to Langfuse using buffered events.

    This is the main entry point for sending traces. It:
    1. Builds trace metadata from events using TraceBuilder
    2. Generates descriptive name and tags
    3. Creates trace and observations in Langfuse
    4. Includes token counts in generation observation for cost tracking
    5. PHASE 4: Creates separate generation observations for each detected generation

    Args:
        session_id: Session identifier
        organization: Organization name
        project_name: Project name
        user_message: User's input prompt
        assistant_message: Assistant's response
        tool_calls: List of tool calls (may have duplicates)
        tool_timings: Dict of {tool_name: latency_ms}
        model_name: Model used
        all_events: All buffered events for the session
        token_counts: Optional dict with input_tokens, output_tokens, cache tokens, etc. (for final generation)
        generations: Optional list of all generation dicts (PHASE 4) with sequence, content, tokens

    Returns:
        True if successfully sent to Langfuse
    """
    if not os.getenv("ENABLE_LANGFUSE", "false").lower() == "true":
        debug_log("ENABLE_LANGFUSE not set, skipping Langfuse trace")
        return False

    try:
        from langfuse import Langfuse

        # Get credentials
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            debug_log("Langfuse credentials not configured")
            return False

        # Initialize Langfuse client
        client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )

        # Build trace metadata from events
        trace_builder = TraceBuilder(session_id, all_events)

        # Generate descriptive trace name
        trace_name = generate_trace_name(user_message, tool_calls, model_name)

        # Generate meaningful tags
        tags = generate_tags(
            tool_names=tool_calls,
            model_name=model_name,
            has_errors=trace_builder.has_errors,
            is_subagent=False,  # This is a root trace
            hierarchy_depth=trace_builder.hierarchy_depth,
            organization=organization,
            project=project_name,
            subagent_count=len(trace_builder.subagent_calls)
        )

        debug_log(f"Creating trace: {trace_name}")
        debug_log(f"Tools: {tool_calls}, Subagents: {len(trace_builder.subagent_calls)}")

        # Create root trace
        trace = client.trace(
            id=session_id,
            name=trace_name,
            input={"messages": [{"role": "user", "content": user_message}]},
            output={"message": assistant_message[:1000]},  # Truncate long responses
            tags=tags,
            metadata={
                "session_id": session_id,
                "organization": organization,
                "project": project_name,
                "model": model_name,
                "source_app": trace_builder.source_app,
                "agent_id": trace_builder.agent_id,
                "tool_count": len(trace_builder.tool_pairs),
                "unique_tools": trace_builder.source_app and list(dict.fromkeys([t.tool_name for t in trace_builder.tool_pairs])) or [],
                "subagent_count": len(trace_builder.subagent_calls),
                "hierarchy_depth": trace_builder.hierarchy_depth,
                "has_errors": trace_builder.has_errors,
                "total_events_buffered": len(all_events)
            }
        )

        # PHASE 4: Create generation observations (multiple if available, else single)
        # If we have multiple generations, create separate observations for each
        if generations and len(generations) > 1:
            debug_log(f"PHASE 4: Creating {len(generations)} separate generation observations")
            for gen in generations:
                # Build usage_details for this specific generation
                usage_details = {}
                if gen:
                    usage_details["input"] = gen.get("input_tokens", 0)
                    usage_details["output"] = gen.get("output_tokens", 0)

                    if gen.get("cache_read_tokens", 0) > 0:
                        usage_details["cache_read_input_tokens"] = gen.get("cache_read_tokens", 0)
                    if gen.get("cache_creation_tokens", 0) > 0:
                        usage_details["cache_creation_input_tokens"] = gen.get("cache_creation_tokens", 0)
                    if gen.get("thinking_tokens", 0) > 0:
                        usage_details["thinking_tokens"] = gen.get("thinking_tokens", 0)

                client.generation(
                    trace_id=session_id,
                    name=f"generation-{gen['sequence']}" + (" (final)" if gen.get("is_final") else ""),
                    model=model_name,
                    input={"user_message": user_message[:500]} if gen['sequence'] == 1 else {"tool_results": "previous tool output"},
                    output={"content": gen.get("content", "")[:1000]},
                    usage_details=usage_details if usage_details else None,
                    metadata={
                        "sequence": gen['sequence'],
                        "is_final": gen.get("is_final", False),
                        "total_generations": len(generations),
                        "input_tokens": gen.get("input_tokens", 0),
                        "output_tokens": gen.get("output_tokens", 0),
                        "cache_read_tokens": gen.get("cache_read_tokens", 0),
                        "cache_creation_tokens": gen.get("cache_creation_tokens", 0)
                    }
                )
        else:
            # PHASE 3 COMPATIBILITY: Single generation (legacy behavior)
            # Build usage_details from token counts if available
            usage_details = {}
            if token_counts:
                # Standard token fields (required by Langfuse)
                usage_details["input"] = token_counts.get("input_tokens", 0)
                usage_details["output"] = token_counts.get("output_tokens", 0)

                # Optional cache token fields (Anthropic prompt caching)
                if token_counts.get("cache_read_tokens", 0) > 0:
                    usage_details["cache_read_input_tokens"] = token_counts.get("cache_read_tokens", 0)
                if token_counts.get("cache_creation_tokens", 0) > 0:
                    usage_details["cache_creation_input_tokens"] = token_counts.get("cache_creation_tokens", 0)

                # Optional thinking tokens (extended thinking mode)
                if token_counts.get("thinking_tokens", 0) > 0:
                    usage_details["thinking_tokens"] = token_counts.get("thinking_tokens", 0)

            generation = client.generation(
                trace_id=session_id,
                name="claude-response",
                model=model_name,
                input={"user_message": user_message[:1000]},
                output={"assistant_message": assistant_message[:1000]},
                usage_details=usage_details if usage_details else None,  # Only pass if we have data
                metadata={
                    "tool_count": len(trace_builder.tool_pairs),
                    "subagent_count": len(trace_builder.subagent_calls),
                    "has_tools": len(trace_builder.tool_pairs) > 0,
                    # Add token summary to metadata for visibility
                    "input_tokens": token_counts.get("input_tokens", 0) if token_counts else 0,
                    "output_tokens": token_counts.get("output_tokens", 0) if token_counts else 0
                }
            )

        # Add observations for each tool invocation
        for tool_inv in trace_builder.tool_pairs:
            observation = client.span(
                trace_id=session_id,
                name=f"{tool_inv.tool_name} (#{tool_inv.sequence_number})",
                input=tool_inv.input_data,
                output=tool_inv.output_data,
                start_time=tool_inv.pre_event.get("timestamp"),
                end_time=tool_inv.post_event.get("timestamp"),
                metadata={
                    "tool_name": tool_inv.tool_name,
                    "sequence_number": tool_inv.sequence_number,
                    "status": tool_inv.status,
                    "latency_ms": tool_inv.latency_ms
                }
            )

        # PHASE 3: Add user prompt observations from events
        for event in all_events:
            if event.get("hook_event_type") == "UserPromptSubmit":
                hook_data = event.get("hook_data", {})
                user_input = hook_data.get("user_input", "")
                if user_input:
                    client.span(
                        trace_id=session_id,
                        name="user-prompt",
                        input=user_input[:500],
                        metadata={
                            "event_type": "UserPromptSubmit",
                            "timestamp": event.get("timestamp")
                        }
                    )

        # Flush to ensure all data is sent
        client.flush()

        debug_log(f"✓ Sent trace to Langfuse: {trace_name} (tools: {len(trace_builder.tool_pairs)}, subagents: {len(trace_builder.subagent_calls)})")
        return True

    except ImportError:
        debug_log("Langfuse SDK not available")
        return False
    except Exception as e:
        debug_log(f"✗ Failed to send trace to Langfuse: {str(e)}")
        import traceback
        debug_log(traceback.format_exc())
        return False


if __name__ == "__main__":
    # Test the naming and tagging functions
    print("=== Trace Naming Examples ===")
    print(generate_trace_name("Do a Google search for Obsidian plugins", ["Bash", "Read", "Task"], "sonnet"))
    print(generate_trace_name("Find files in current directory", ["Bash"], "haiku"))
    print(generate_trace_name("Search for documentation on Python asyncio patterns",
                            ["WebFetch", "Glob", "Read", "Grep", "Edit"], "opus"))

    print("\n=== Tag Examples ===")
    tags = generate_tags(
        tool_names=["Bash", "Read", "Task"],
        model_name="claude-3-5-sonnet",
        has_errors=False,
        is_subagent=False,
        hierarchy_depth=1,
        organization="consulting-co",
        project="consulting-co",
        subagent_count=0
    )
    print(tags)
