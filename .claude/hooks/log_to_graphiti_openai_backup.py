#!/usr/bin/env python3
"""
Hook to log Claude Code conversations to Graphiti knowledge graph.
Simplified version - creates episodes directly from transcript.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

async def main():
    """Main hook entry point - reads stdin and processes transcript."""

    # Read hook data from stdin
    hook_data = json.load(sys.stdin)

    session_id = hook_data.get("session_id", "unknown")
    transcript_path = hook_data.get("transcript_path")
    hook_event = hook_data.get("hook_event_name", "unknown")

    # Only process on Stop event (after each Claude response)
    if hook_event != "Stop":
        return

    if not transcript_path or not Path(transcript_path).exists():
        print(f"✗ Transcript not found: {transcript_path}", file=sys.stderr)
        return

    # Read transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_lines = f.readlines()

    # Parse JSONL
    messages = [json.loads(line) for line in transcript_lines if line.strip()]

    # Extract last user/assistant exchange
    user_message = None
    assistant_message = None
    tool_calls = []

    for msg in reversed(messages):
        msg_type = msg.get("type")

        if msg_type == "user_message" and not user_message:
            content = msg.get("content", [])
            if content and isinstance(content, list):
                user_message = content[0].get("text", "")

        elif msg_type == "assistant_message" and not assistant_message:
            content = msg.get("content", [])
            for block in content:
                if block.get("type") == "text":
                    assistant_message = block.get("text", "")
                elif block.get("type") == "tool_use":
                    tool_calls.append({
                        "name": block.get("name"),
                        "input": block.get("input", {})
                    })

        if user_message and assistant_message:
            break

    if not user_message or not assistant_message:
        print("✗ No complete exchange found in transcript", file=sys.stderr)
        return

    # Create simple episode text
    episode_text = format_episode(user_message, assistant_message, tool_calls)

    # Send to Graphiti
    try:
        from graphiti_core import Graphiti

        # Get Neo4j credentials from environment
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        graphiti = Graphiti(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
        )

        episode_name = f"claude-session-{session_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        await graphiti.add_episode(
            name=episode_name,
            episode_body=episode_text,
            reference_time=datetime.now(),
            source_description=f"Claude Code Session {session_id}",
        )

        await graphiti.close()

        print(f"✓ Logged to Graphiti: {episode_name}", file=sys.stderr)

    except Exception as e:
        print(f"✗ Failed to log: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def format_episode(user_input: str, assistant_response: str, tool_calls: list) -> str:
    """Format conversation as episode text for Graphiti."""

    episode = f"""[CONVERSATION TURN]
Timestamp: {datetime.now().isoformat()}

[USER REQUEST]
{user_input[:1000]}

[ASSISTANT RESPONSE]
{assistant_response[:1000]}
"""

    if tool_calls:
        episode += "\n[TOOLS USED]\n"
        for tool in tool_calls[:10]:
            episode += f"- {tool['name']}\n"

    return episode


if __name__ == "__main__":
    asyncio.run(main())
