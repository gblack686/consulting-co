#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "neo4j",
#     "python-dotenv",
# ]
# ///
"""
Real-time observability events to Graphiti Neo4j bridge.
Transforms observability SQLite events into Neo4j graph structure.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

# Event tracking for deduplication
processed_events: Set[str] = set()


def get_neo4j_driver():
    """Create Neo4j driver from environment variables."""
    from neo4j import GraphDatabase

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    return GraphDatabase.driver(uri, auth=(user, password))


def process_observability_event(event: dict) -> None:
    """Transform observability event to Neo4j nodes/relationships."""

    event_type = event.get('hook_event_type', '')
    session_id = event.get('session_id', 'unknown')
    source_app = event.get('source_app', 'unknown')
    timestamp = event.get('timestamp', int(datetime.now().timestamp() * 1000))

    # Create unique event ID for deduplication
    event_id = f"{source_app}:{session_id}:{event_type}:{timestamp}"

    if event_id in processed_events:
        return  # Skip duplicate

    processed_events.add(event_id)

    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            # Create or update Session node
            session.run("""
                MERGE (s:Session {id: $session_id, source_app: $source_app})
                ON CREATE SET
                    s.start_time = $timestamp,
                    s.status = 'active',
                    s.model_name = $model_name
                ON MATCH SET
                    s.last_event_time = $timestamp
            """, {
                'session_id': session_id,
                'source_app': source_app,
                'timestamp': timestamp,
                'model_name': event.get('model_name', 'unknown')
            })

            # Route to specific handler
            if event_type == 'PreToolUse':
                handle_pre_tool_use(session, event, session_id, source_app)
            elif event_type == 'PostToolUse':
                handle_post_tool_use(session, event, session_id, source_app)
            elif event_type == 'Stop':
                handle_stop(session, event, session_id, source_app)
            elif event_type == 'SubagentStop':
                handle_subagent_completion(session, event, session_id, source_app)

    finally:
        driver.close()


def handle_pre_tool_use(session, event: dict, session_id: str, source_app: str) -> None:
    """Create Tool node when tool execution starts."""

    payload = event.get('payload', {})
    tool_name = payload.get('tool_name', 'unknown')
    tool_input = payload.get('tool_input', {})
    timestamp = event.get('timestamp', 0)

    # Create unique tool execution ID
    tool_exec_id = f"{session_id}:{tool_name}:{timestamp}"

    session.run("""
        MERGE (t:Tool {id: $tool_id})
        SET
            t.name = $tool_name,
            t.input = $tool_input,
            t.start_time = $timestamp,
            t.status = 'running'

        WITH t
        MATCH (s:Session {id: $session_id, source_app: $source_app})
        MERGE (s)-[:EXECUTED]->(t)
    """, {
        'tool_id': tool_exec_id,
        'tool_name': tool_name,
        'tool_input': json.dumps(tool_input),
        'timestamp': timestamp,
        'session_id': session_id,
        'source_app': source_app
    })


def handle_post_tool_use(session, event: dict, session_id: str, source_app: str) -> None:
    """Update Tool node with execution results and extract entities."""

    payload = event.get('payload', {})
    tool_name = payload.get('tool_name', 'unknown')
    tool_output = payload.get('tool_output', '')
    timestamp = event.get('timestamp', 0)

    # Find the most recent tool execution for this session and tool
    # Calculate latency
    result = session.run("""
        MATCH (s:Session {id: $session_id, source_app: $source_app})-[:EXECUTED]->(t:Tool {name: $tool_name})
        WHERE t.status = 'running'
        WITH t ORDER BY t.start_time DESC LIMIT 1
        SET
            t.output = $tool_output,
            t.end_time = $timestamp,
            t.latency_ms = $timestamp - t.start_time,
            t.status = 'completed'
        RETURN t.id as tool_id, t.latency_ms as latency
    """, {
        'session_id': session_id,
        'source_app': source_app,
        'tool_name': tool_name,
        'tool_output': str(tool_output)[:5000],  # Limit output size
        'timestamp': timestamp
    })

    # Extract entities from tool output
    record = result.single()
    if record:
        tool_id = record['tool_id']
        entities = extract_entities_from_tool_output(str(tool_output), tool_name)

        # Link extracted entities to this tool execution
        for entity in entities:
            session.run("""
                MERGE (e:Entity {name: $name, type: $type})
                SET e.description = $description

                WITH e
                MATCH (t:Tool {id: $tool_id})
                MERGE (t)-[:DISCOVERED]->(e)
            """, {
                'name': entity['name'],
                'type': entity['type'],
                'description': entity.get('description', ''),
                'tool_id': tool_id
            })


def handle_stop(session, event: dict, session_id: str, source_app: str) -> None:
    """Mark session as completed."""

    timestamp = event.get('timestamp', 0)

    session.run("""
        MATCH (s:Session {id: $session_id, source_app: $source_app})
        SET
            s.end_time = $timestamp,
            s.status = 'completed'
    """, {
        'session_id': session_id,
        'source_app': source_app,
        'timestamp': timestamp
    })


def handle_subagent_completion(session, event: dict, session_id: str, source_app: str) -> None:
    """Track subagent hierarchy and completion."""

    payload = event.get('payload', {})
    parent_session_id = payload.get('parent_session_id')
    timestamp = event.get('timestamp', 0)

    # Create Subagent relationship
    if parent_session_id:
        session.run("""
            MATCH (parent:Session {id: $parent_id})
            MATCH (child:Session {id: $session_id, source_app: $source_app})
            MERGE (parent)-[r:SPAWNED]->(child)
            SET
                r.spawn_time = $timestamp,
                child.status = 'completed',
                child.end_time = $timestamp
        """, {
            'parent_id': parent_session_id,
            'session_id': session_id,
            'source_app': source_app,
            'timestamp': timestamp
        })


def extract_entities_from_tool_output(output: str, tool_name: str) -> List[dict]:
    """
    Extract entities from tool output using simple pattern matching.
    For file operations, extract file paths.
    For code operations, extract function/class names.
    """

    entities = []

    # Extract file paths for Read/Write/Edit tools
    if tool_name in ['Read', 'Write', 'Edit', 'Glob']:
        # Simple file path extraction (paths with .ext or /dir/)
        import re

        # Match file paths
        file_pattern = r'(?:[A-Za-z]:[/\\]|/)(?:[^/\\:\*\?"<>\|\r\n]+[/\\])*[^/\\:\*\?"<>\|\r\n]+\.[a-zA-Z0-9]+'
        files = re.findall(file_pattern, output[:2000])

        for file_path in files[:10]:  # Limit to 10 files
            entities.append({
                'name': Path(file_path).name,
                'type': 'file',
                'description': f'File accessed via {tool_name}'
            })

    # Extract function/class names for code tools
    elif tool_name in ['Grep', 'Bash']:
        import re

        # Match function definitions
        func_pattern = r'(?:def|function|async\s+def)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        functions = re.findall(func_pattern, output[:2000])

        for func_name in functions[:5]:
            entities.append({
                'name': func_name,
                'type': 'function',
                'description': f'Function mentioned in {tool_name} output'
            })

        # Match class definitions
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        classes = re.findall(class_pattern, output[:2000])

        for class_name in classes[:5]:
            entities.append({
                'name': class_name,
                'type': 'class',
                'description': f'Class mentioned in {tool_name} output'
            })

    return entities


def main():
    """Main hook entry point - reads stdin and processes event."""

    try:
        # Read hook data from stdin
        hook_data = json.load(sys.stdin)

        # Get observability database path
        db_path = Path(__file__).parent.parent.parent / 'observability' / 'apps' / 'server' / 'events.db'

        if not db_path.exists():
            # Fallback: just process the current event
            process_observability_event(hook_data)
            print(f"✓ Processed event (no DB found)", file=sys.stderr)
            return

        # Connect to observability database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get recent unprocessed events (last 100)
        cursor.execute("""
            SELECT source_app, session_id, hook_event_type, payload, timestamp, model_name
            FROM events
            ORDER BY timestamp DESC
            LIMIT 100
        """)

        rows = cursor.fetchall()

        # Process each event
        for row in rows:
            event = {
                'source_app': row[0],
                'session_id': row[1],
                'hook_event_type': row[2],
                'payload': json.loads(row[3]) if row[3] else {},
                'timestamp': row[4],
                'model_name': row[5] or 'unknown'
            }

            process_observability_event(event)

        conn.close()

        print(f"✓ Processed {len(rows)} events to Neo4j", file=sys.stderr)

    except Exception as e:
        print(f"✗ Failed to process events: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Always exit 0 to not block Claude
    sys.exit(0)


if __name__ == "__main__":
    main()
