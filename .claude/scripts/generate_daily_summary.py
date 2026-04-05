#!/usr/bin/env python3
"""
Daily Obsidian Summary Generator
Queries Langfuse and Neo4j/Graphiti to generate beautiful daily activity reports.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

def main():
    """Generate daily summary for Obsidian."""

    # Get target date (default: today)
    target_date = datetime.now().date()
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    print(f"📊 Generating summary for {target_date}...")

    # Query both systems
    langfuse_data = query_langfuse(target_date)
    graphiti_data = query_graphiti(target_date)

    # Generate markdown
    markdown = generate_markdown(target_date, langfuse_data, graphiti_data)

    # Save to Obsidian daily notes directory
    obsidian_path = Path.home() / "obsidian-vault" / "daily-notes"
    obsidian_path.mkdir(parents=True, exist_ok=True)

    output_file = obsidian_path / f"{target_date.isoformat()}-claude-activity.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✓ Summary written to: {output_file}")
    print(f"\n{markdown}")


def query_langfuse(target_date):
    """Query Langfuse for today's conversation data."""
    from langfuse import Langfuse

    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_BASE_URL", "http://localhost:3000")
    )

    # Calculate time range
    start_time = datetime.combine(target_date, datetime.min.time())
    end_time = start_time + timedelta(days=1)

    # Get all traces/events for today
    # Note: Langfuse SDK 3.9.3 doesn't have a query API, so we'll use basic fetch
    # In production, you'd use the Langfuse REST API or wait for SDK updates

    # For now, return placeholder that we'll enhance
    return {
        "conversations": [],
        "tools_used": Counter(),
        "total_tokens": 0,
        "total_cost": 0.0
    }


def query_graphiti(target_date):
    """Query Neo4j/Graphiti for today's episodes and entities."""
    from neo4j import GraphDatabase
    from neo4j.time import DateTime as Neo4jDateTime

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Calculate time range in UTC
    start_time = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_time = start_time + timedelta(days=1)

    # Convert to Neo4j DateTime objects
    start_ts = Neo4jDateTime.from_native(start_time)
    end_ts = Neo4jDateTime.from_native(end_time)

    with driver.session() as session:
        # Get episodes created today
        episodes_result = session.run("""
            MATCH (e:Episodic)
            WHERE e.created_at >= $start_ts AND e.created_at < $end_ts
            RETURN e.name as name,
                   e.content as content,
                   e.created_at as created_at,
                   e.source as source
            ORDER BY e.created_at DESC
        """, start_ts=start_ts, end_ts=end_ts)

        episodes = [dict(record) for record in episodes_result]

        # Get entities created or updated today
        entities_result = session.run("""
            MATCH (e:Entity)
            WHERE e.created_at >= $start_ts AND e.created_at < $end_ts
            RETURN e.name as name,
                   e.labels as labels,
                   e.summary as summary,
                   e.created_at as created_at
            ORDER BY e.created_at DESC
            LIMIT 20
        """, start_ts=start_ts, end_ts=end_ts)

        entities = [dict(record) for record in entities_result]

        # Get most connected entities (using COUNT instead of size)
        popular_entities = session.run("""
            MATCH (e:Entity)
            WHERE e.created_at >= $start_ts
            WITH e, COUNT { (e)--() } as connections
            WHERE connections > 0
            RETURN e.name as name, connections
            ORDER BY connections DESC
            LIMIT 10
        """, start_ts=start_ts)

        popular = [dict(record) for record in popular_entities]

    driver.close()

    return {
        "episodes": episodes,
        "entities": entities,
        "popular_entities": popular
    }


def generate_markdown(target_date, langfuse_data, graphiti_data):
    """Generate formatted markdown report."""

    project_name = os.getenv("PROJECT_NAME", Path.cwd().name)

    # Extract data
    episodes = graphiti_data["episodes"]
    entities = graphiti_data["entities"]
    popular = graphiti_data["popular_entities"]

    # Calculate statistics
    conversation_count = len(episodes)
    entity_count = len(entities)

    # Build markdown
    md = f"""# {target_date.isoformat()} - Claude Code Activity Report

## 🎯 Summary

**Project:** `{project_name}`
**Conversations:** {conversation_count}
**New Knowledge:** {entity_count} entities extracted
**System:** Claude Sonnet 4.5 with Graphiti + Langfuse observability

---

## 💬 Conversations Today

"""

    if episodes:
        for i, episode in enumerate(episodes, 1):
            name = episode['name']
            created = episode['created_at']
            content_preview = episode.get('content', '')[:200] + "..." if episode.get('content') else "No content"

            md += f"""### {i}. {name}

**Time:** {created}
**Preview:** {content_preview}

"""
    else:
        md += "*No conversations recorded today.*\n\n"

    md += """---

## 🧠 Knowledge Discovered

"""

    if entities:
        # Group entities by labels
        by_label = defaultdict(list)
        for entity in entities:
            # labels is a list, take first label or use 'concept'
            labels = entity.get('labels', ['concept'])
            primary_label = labels[0] if labels else 'concept'
            by_label[primary_label].append(entity)

        for label, items in sorted(by_label.items()):
            md += f"### {label.title()}s\n\n"
            for entity in items[:5]:  # Limit to 5 per label
                name = entity['name']
                summary = entity.get('summary', 'No summary')
                md += f"- **{name}** - {summary}\n"
            md += "\n"
    else:
        md += "*No new entities extracted today.*\n\n"

    md += """---

## 🔗 Knowledge Graph Insights

### Most Connected Concepts

"""

    if popular:
        for entity in popular[:10]:
            name = entity['name']
            connections = entity['connections']
            md += f"- **[[{name}]]** ({connections} connections)\n"
    else:
        md += "*No graph data available.*\n"

    md += f"""

---

## 📈 Growth Metrics

- **Total episodes in graph:** {conversation_count} (today)
- **Total entities created:** {entity_count} (today)
- **Knowledge density:** {entity_count / max(conversation_count, 1):.1f} entities per conversation

---

## 🔄 Data Sources

- ✅ **Neo4j/Graphiti** - Knowledge graph with temporal entity extraction
- ✅ **Langfuse** - Observability and trace logging
- 📝 **Obsidian** - You're reading this summary!

---

## 📝 Notes

This summary was auto-generated from your Claude Code activity using:
- `.claude/hooks/log_to_graphiti.py` - Automatic episode logging
- `.claude/hooks/log_to_langfuse.py` - Trace and metrics logging
- `.claude/scripts/generate_daily_summary.py` - This report generator

**Generated:** {datetime.now().isoformat()}

---

## 🚀 Next Session Prep

Based on today's activity:
"""

    # Add intelligent suggestions based on entities
    if entities:
        # Get unique labels from all entities
        all_labels = []
        for e in entities:
            labels = e.get('labels', ['concept'])
            all_labels.extend(labels)
        unique_labels = list(set(all_labels))
        md += f"\n- [ ] Review {len(entities)} new concepts: {', '.join(unique_labels[:3])}\n"

    if popular:
        top_concept = popular[0]['name']
        md += f"- [ ] Deep dive into most connected concept: [[{top_concept}]]\n"

    md += f"- [ ] Continue work on `{project_name}` project\n"

    md += "\n"

    return md


if __name__ == "__main__":
    main()
