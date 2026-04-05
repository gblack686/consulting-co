#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "graphiti-core",
#     "python-dotenv",
#     "neo4j",
# ]
# ///
"""
Hook to log Claude Code conversations to Graphiti knowledge graph.
Uses Claude Code subagent (via headless mode) for entity extraction!
Meta: Claude extracting entities from its own conversations.
"""

import os
import sys
import json
import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(Path(__file__).parent.parent.parent / '.env')

def find_claude_executable():
    """Find the claude executable in PATH."""
    claude_path = shutil.which('claude')
    if claude_path:
        return claude_path

    # Fallback: try common locations
    possible_paths = [
        Path.home() / '.local' / 'bin' / 'claude',
        Path.home() / 'AppData' / 'Local' / 'Programs' / 'Claude' / 'claude.exe',
        Path('C:/Program Files/Claude/claude.exe'),
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return 'claude'  # Fallback to just 'claude'

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

    # Extract entities using Claude Code subagent!
    try:
        print("🤖 Spawning Claude subagent for entity extraction...", file=sys.stderr)

        entities = await extract_entities_with_claude_subagent(
            user_message,
            assistant_message,
            tool_calls
        )

        # Create rich episode text with extracted entities
        episode_text = format_episode_with_entities(
            user_message,
            assistant_message,
            tool_calls,
            entities
        )

        # Send to Graphiti
        await store_in_graphiti(session_id, episode_text)

        entity_count = len(entities.get('entities', []))
        print(f"✓ Logged to Graphiti with {entity_count} entities (extracted by Claude subagent)", file=sys.stderr)

    except Exception as e:
        print(f"✗ Failed to log: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


async def extract_entities_with_claude_subagent(
    user_message: str,
    assistant_message: str,
    tool_calls: List[Dict]
) -> Dict:
    """
    Use Claude Code in headless mode to extract entities.
    This spawns a Claude subagent that analyzes the conversation!
    """

    # Create temp file with conversation data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        f.write(f"""USER REQUEST:
{user_message[:800]}

CLAUDE RESPONSE:
{assistant_message[:800]}

TOOLS USED:
{', '.join([t['name'] for t in tool_calls[:5]])}
""")

    try:
        # Build the extraction prompt for Claude subagent
        prompt = f"""Read the conversation in {temp_file} and extract structured information.

Analyze the conversation and return ONLY a valid JSON object (no markdown formatting, no explanation) with this structure:

{{
  "intent": "what the user wanted to accomplish",
  "complexity": "simple|moderate|complex",
  "entities": [
    {{"name": "entity name", "type": "file|function|concept|technology|pattern", "description": "brief"}}
  ],
  "relationships": [
    {{"from": "entity1", "to": "entity2", "type": "uses|implements|depends_on|modifies"}}
  ],
  "key_concepts": ["concept1", "concept2"],
  "outcome": "what was accomplished"
}}

Focus on:
- Files mentioned or created
- Technologies/frameworks used
- Key concepts discussed
- Patterns or approaches

Return ONLY the JSON object, nothing else."""

        # Call Claude Code in headless mode with the prompt
        # -p flag = headless prompt mode
        claude_exe = find_claude_executable()
        result = subprocess.run(
            [claude_exe, '-p', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"⚠ Claude subagent failed: {result.stderr[:200]}", file=sys.stderr)
            return {"entities": [], "relationships": []}

        # Parse the response
        response_text = result.stdout.strip()

        # Extract JSON from response (Claude might add some text)
        # Look for JSON object
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx >= 0 and end_idx > start_idx:
            json_text = response_text[start_idx:end_idx]
            entities_data = json.loads(json_text)

            print(f"✓ Claude subagent extracted: {entities_data.get('intent', 'unknown')}", file=sys.stderr)
            return entities_data
        else:
            print(f"⚠ No JSON found in Claude response", file=sys.stderr)
            return {"entities": [], "relationships": []}

    except subprocess.TimeoutExpired:
        print("⚠ Claude subagent timed out", file=sys.stderr)
        return {"entities": [], "relationships": []}
    except json.JSONDecodeError as e:
        print(f"⚠ Failed to parse Claude response as JSON: {e}", file=sys.stderr)
        print(f"Response was: {response_text[:200]}", file=sys.stderr)
        return {"entities": [], "relationships": []}
    except Exception as e:
        print(f"⚠ Entity extraction failed: {e}", file=sys.stderr)
        return {"entities": [], "relationships": []}
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass


def format_episode_with_entities(
    user_input: str,
    assistant_response: str,
    tool_calls: list,
    entities_data: Dict
) -> str:
    """Format conversation with Claude-extracted entities as episode text."""

    episode = f"""[CONVERSATION TURN]
Timestamp: {datetime.now().isoformat()}
Extracted by: Claude Code Subagent

[INTENT]
{entities_data.get('intent', 'Unknown')} (Complexity: {entities_data.get('complexity', 'unknown')})

[USER REQUEST]
{user_input[:1000]}

[ASSISTANT RESPONSE]
{assistant_response[:1000]}
"""

    if tool_calls:
        episode += "\n[TOOLS USED]\n"
        for tool in tool_calls[:10]:
            episode += f"- {tool['name']}\n"

    # Add extracted entities
    entities = entities_data.get('entities', [])
    if entities:
        episode += "\n[ENTITIES (Claude Subagent)]\n"
        for entity in entities[:15]:
            episode += f"- {entity.get('name')} ({entity.get('type')}): {entity.get('description', '')}\n"

    # Add relationships
    relationships = entities_data.get('relationships', [])
    if relationships:
        episode += "\n[RELATIONSHIPS]\n"
        for rel in relationships[:10]:
            episode += f"- {rel.get('from')} --[{rel.get('type')}]--> {rel.get('to')}\n"

    # Add key concepts
    concepts = entities_data.get('key_concepts', [])
    if concepts:
        episode += f"\n[KEY CONCEPTS]\n{', '.join(concepts[:10])}\n"

    # Add outcome
    outcome = entities_data.get('outcome')
    if outcome:
        episode += f"\n[OUTCOME]\n{outcome}\n"

    return episode


async def store_in_graphiti(session_id: str, episode_text: str):
    """Store episode in Graphiti/Neo4j."""

    from graphiti_core import Graphiti

    # Get Neo4j credentials from environment
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

    # Get project name from current directory
    project_name = os.getenv("PROJECT_NAME", Path.cwd().name)

    graphiti = Graphiti(
        uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password,
    )

    episode_name = f"{project_name}-{session_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Store episode with our pre-extracted entities
    await graphiti.add_episode(
        name=episode_name,
        episode_body=episode_text,
        reference_time=datetime.now(),
        source_description=f"[{project_name}] Claude Code Session {session_id} (Meta: Claude extracted by Claude)",
    )

    await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
