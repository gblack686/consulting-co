#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "neo4j",
#     "python-dotenv",
# ]
# ///
"""
Obsidian Note Exporter - Generates Markdown notes from Neo4j sessions.
Creates session notes with timelines, metrics, and entity backlinks.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')


def get_neo4j_driver():
    """Create Neo4j driver from environment variables."""
    from neo4j import GraphDatabase

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    return GraphDatabase.driver(uri, auth=(user, password))


def get_vault_path() -> Path:
    """Get Obsidian vault path from environment or use default."""
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

    if vault_path:
        return Path(vault_path)

    # Default to observability/notes in project root
    return Path(__file__).parent.parent.parent / 'observability' / 'notes'


def fetch_session_data(session_id: str, source_app: str) -> Optional[Dict]:
    """Fetch comprehensive session data from Neo4j."""

    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            # Get session details with tools and entities
            result = session.run("""
                MATCH (s:Session {id: $session_id, source_app: $source_app})
                OPTIONAL MATCH (s)-[:EXECUTED]->(t:Tool)
                OPTIONAL MATCH (t)-[:DISCOVERED]->(e:Entity)
                OPTIONAL MATCH (s)-[:SPAWNED]->(child:Session)
                OPTIONAL MATCH (parent:Session)-[:SPAWNED]->(s)

                WITH s,
                     collect(DISTINCT {
                         name: t.name,
                         start_time: t.start_time,
                         latency_ms: t.latency_ms,
                         status: t.status,
                         input: t.input,
                         output: t.output
                     }) as tools,
                     collect(DISTINCT {
                         name: e.name,
                         type: e.type,
                         description: e.description
                     }) as entities,
                     collect(DISTINCT child.id) as child_sessions,
                     parent.id as parent_session_id

                RETURN
                    s.id as session_id,
                    s.source_app as source_app,
                    s.model_name as model_name,
                    s.start_time as start_time,
                    s.end_time as end_time,
                    s.status as status,
                    s.total_tools as total_tools,
                    s.avg_tool_latency as avg_tool_latency,
                    s.session_duration_sec as session_duration_sec,
                    s.subagent_count as subagent_count,
                    s.entities_discovered as entities_discovered,
                    s.performance_tier as performance_tier,
                    s.tools_breakdown as tools_breakdown,
                    tools,
                    entities,
                    child_sessions,
                    parent_session_id
            """, {
                'session_id': session_id,
                'source_app': source_app
            })

            record = result.single()

            if not record:
                return None

            # Convert to dict
            data = {
                'session_id': record['session_id'],
                'source_app': record['source_app'],
                'model_name': record['model_name'],
                'start_time': record['start_time'],
                'end_time': record['end_time'],
                'status': record['status'],
                'metrics': {
                    'total_tools': record['total_tools'],
                    'avg_tool_latency': record['avg_tool_latency'],
                    'session_duration_sec': record['session_duration_sec'],
                    'subagent_count': record['subagent_count'],
                    'entities_discovered': record['entities_discovered'],
                    'performance_tier': record['performance_tier'],
                    'tools_breakdown': json.loads(record['tools_breakdown']) if record['tools_breakdown'] else {}
                },
                'tools': [t for t in record['tools'] if t['name']],  # Filter out empty entries
                'entities': [e for e in record['entities'] if e['name']],
                'child_sessions': record['child_sessions'],
                'parent_session_id': record['parent_session_id']
            }

            return data

    finally:
        driver.close()


def format_timestamp(timestamp_ms: int) -> str:
    """Convert timestamp to readable format."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%H:%M:%S')


def format_date(timestamp_ms: int) -> str:
    """Convert timestamp to date format."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%Y-%m-%d')


def generate_session_note(data: Dict) -> str:
    """Generate Obsidian-formatted markdown note for a session."""

    session_id = data['session_id']
    source_app = data['source_app']
    short_session_id = session_id[:8]

    # Format frontmatter
    tags = ['agent-session', source_app.replace(' ', '-')]
    entity_names = [e['name'] for e in data['entities']]

    start_date = format_date(data['start_time']) if data['start_time'] else 'unknown'

    frontmatter = f"""---
tags: [{', '.join(tags)}]
session_id: {session_id}
source_app: {source_app}
model: {data['model_name']}
date: {start_date}
status: {data['status']}
performance: {data['metrics']['performance_tier']}
entities: [{', '.join(entity_names[:20])}]
"""

    if data['parent_session_id']:
        frontmatter += f"parent_session: [[{data['parent_session_id'][:8]}]]\n"

    frontmatter += "---\n\n"

    # Title
    note = frontmatter
    note += f"# Agent Session: {source_app}:{short_session_id}\n\n"

    # Summary
    note += "## Summary\n\n"
    note += f"- **Model**: {data['model_name']}\n"
    note += f"- **Status**: {data['status']}\n"
    note += f"- **Duration**: {data['metrics']['session_duration_sec']}s\n"
    note += f"- **Tools Used**: {data['metrics']['total_tools']}\n"
    note += f"- **Entities Discovered**: {data['metrics']['entities_discovered']}\n"
    note += f"- **Performance**: {data['metrics']['performance_tier']}\n"

    if data['parent_session_id']:
        parent_short = data['parent_session_id'][:8]
        note += f"- **Parent Session**: [[{parent_short}]]\n"

    if data['child_sessions']:
        child_links = [f"[[{cid[:8]}]]" for cid in data['child_sessions']]
        note += f"- **Spawned Subagents**: {', '.join(child_links)}\n"

    note += "\n"

    # Timeline
    if data['tools']:
        note += "## Timeline\n\n"

        # Sort tools by start time
        sorted_tools = sorted(data['tools'], key=lambda t: t['start_time'] or 0)

        for tool in sorted_tools:
            if not tool['name']:
                continue

            time_str = format_timestamp(tool['start_time']) if tool['start_time'] else 'unknown'
            latency = f"{tool['latency_ms']}ms" if tool['latency_ms'] else 'N/A'

            note += f"- **{time_str}** - `{tool['name']}` ({latency})\n"

        note += "\n"

    # Entities Discovered
    if data['entities']:
        note += "## Entities Discovered\n\n"

        # Group entities by type
        entities_by_type = {}
        for entity in data['entities']:
            entity_type = entity['type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)

        for entity_type, entities in sorted(entities_by_type.items()):
            note += f"### {entity_type.capitalize()}s\n\n"
            for entity in entities[:15]:  # Limit to 15 per type
                desc = entity['description'] or 'No description'
                note += f"- **[[{entity['name']}]]**: {desc}\n"
            note += "\n"

    # Performance Metrics
    note += "## Performance Metrics\n\n"
    note += f"- **Average Tool Latency**: {data['metrics']['avg_tool_latency']}ms\n"
    note += f"- **Total Session Duration**: {data['metrics']['session_duration_sec']}s\n"
    note += f"- **Performance Tier**: {data['metrics']['performance_tier']}\n"

    if data['metrics']['tools_breakdown']:
        note += "\n### Tools Breakdown\n\n"
        for tool_name, count in sorted(data['metrics']['tools_breakdown'].items(), key=lambda x: x[1], reverse=True):
            note += f"- `{tool_name}`: {count} times\n"

    note += "\n"

    # Related Sessions
    if data['parent_session_id'] or data['child_sessions']:
        note += "## Related Sessions\n\n"

        if data['parent_session_id']:
            parent_short = data['parent_session_id'][:8]
            note += f"- **Parent**: [[{parent_short}]]\n"

        if data['child_sessions']:
            note += "- **Children**:\n"
            for child_id in data['child_sessions']:
                child_short = child_id[:8]
                note += f"  - [[{child_short}]]\n"

        note += "\n"

    # Footer
    note += "---\n"
    note += f"*Generated by Obsidian Exporter on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    return note


def write_session_note(session_id: str, source_app: str, note_content: str) -> Path:
    """Write session note to Obsidian vault."""

    vault_path = get_vault_path()

    # Ensure vault directory exists
    vault_path.mkdir(parents=True, exist_ok=True)

    # Create sessions subdirectory
    sessions_dir = vault_path / 'sessions'
    sessions_dir.mkdir(exist_ok=True)

    # Generate filename
    short_session_id = session_id[:8]
    filename = f"{source_app.replace(' ', '-')}_{short_session_id}.md"
    note_path = sessions_dir / filename

    # Write note
    note_path.write_text(note_content, encoding='utf-8')

    return note_path


def update_daily_summary(session_id: str, source_app: str, data: Dict) -> None:
    """Update daily summary with link to this session."""

    vault_path = get_vault_path()

    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')

    # Create daily notes directory
    daily_dir = vault_path / 'daily'
    daily_dir.mkdir(exist_ok=True)

    daily_note_path = daily_dir / f"{today}.md"

    # Read existing daily note or create new
    if daily_note_path.exists():
        daily_content = daily_note_path.read_text(encoding='utf-8')
    else:
        daily_content = f"""---
date: {today}
tags: [daily-summary]
---

# Daily Summary - {today}

## Agent Sessions

"""

    # Add session link
    short_session_id = session_id[:8]
    session_link = f"- [[{source_app.replace(' ', '-')}_{short_session_id}]] - "
    session_link += f"{data['metrics']['total_tools']} tools, "
    session_link += f"{data['metrics']['entities_discovered']} entities, "
    session_link += f"{data['metrics']['performance_tier']} performance\n"

    # Append to daily note
    daily_content += session_link

    # Write updated daily note
    daily_note_path.write_text(daily_content, encoding='utf-8')


def main():
    """Main entry point - reads stdin and generates notes."""

    try:
        # Read hook data from stdin
        hook_data = json.load(sys.stdin)

        session_id = hook_data.get('session_id', 'unknown')
        source_app = hook_data.get('payload', {}).get('source_app', 'unknown')
        hook_event = hook_data.get('hook_event_name', 'unknown')

        # Only process on Stop event
        if hook_event != 'Stop':
            sys.exit(0)

        # Fetch session data from Neo4j
        data = fetch_session_data(session_id, source_app)

        if not data:
            print(f"⚠ No data found for {source_app}:{session_id[:8]}", file=sys.stderr)
            sys.exit(0)

        # Generate note
        note_content = generate_session_note(data)

        # Write to vault
        note_path = write_session_note(session_id, source_app, note_content)

        # Update daily summary
        update_daily_summary(session_id, source_app, data)

        print(f"✓ Exported session note to {note_path}", file=sys.stderr)
        print(f"  {data['metrics']['total_tools']} tools, "
              f"{data['metrics']['entities_discovered']} entities", file=sys.stderr)

    except Exception as e:
        print(f"✗ Failed to export note: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Always exit 0 to not block Claude
    sys.exit(0)


if __name__ == "__main__":
    main()
