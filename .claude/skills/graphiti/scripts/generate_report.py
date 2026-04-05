#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Graphiti Knowledge Graph Report Generator

Generates an aggregate report from Graphiti knowledge graph data.

Since Graphiti uses MCP protocol (not REST), this script works in two modes:

1. **Claude Mode** (recommended): Claude fetches data via MCP tools and pipes JSON:
   ```
   # Claude calls MCP tools, then:
   echo '{"episodes": [...], "nodes": [...], "facts": [...]}' | \\
       uv run .claude/skills/graphiti/scripts/generate_report.py --stdin
   ```

2. **File Mode**: Read pre-fetched JSON data from a file:
   ```
   uv run .claude/skills/graphiti/scripts/generate_report.py --input data.json
   ```

The report includes:
- Episode timeline and statistics
- Session breakdown with turn counts
- Token usage analysis
- Tool usage patterns
- Entity catalog grouped by type
- Relationship/fact summary

Usage:
    uv run .claude/skills/graphiti/scripts/generate_report.py --stdin
    uv run .claude/skills/graphiti/scripts/generate_report.py --input data.json [--output report.md]
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def parse_episode_content(content: str) -> dict | None:
    """Parse JSON content from episode."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def generate_report(data: dict) -> str:
    """Generate the aggregate report from data."""
    lines = []

    group_id = data.get("group_id", "unknown")
    episodes = data.get("episodes", [])
    nodes = data.get("nodes", [])
    facts = data.get("facts", [])

    # Header
    lines.append("# Graphiti Knowledge Graph Report")
    lines.append(f"\n**Generated**: {datetime.now().isoformat()}")
    lines.append(f"**Group ID**: `{group_id}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === SUMMARY SECTION ===
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Episodes | {len(episodes)} |")
    lines.append(f"| Entities (Nodes) | {len(nodes)} |")
    lines.append(f"| Facts (Relationships) | {len(facts)} |")
    lines.append("")

    # === EPISODES SECTION ===
    lines.append("---")
    lines.append("")
    lines.append("## Episodes")
    lines.append("")

    if episodes:
        # Parse episode content for analysis
        parsed_episodes = []
        for ep in episodes:
            content = parse_episode_content(ep.get("content", "{}"))
            if content:
                parsed_episodes.append({
                    "uuid": ep.get("uuid", ""),
                    "name": ep.get("name", ""),
                    "created_at": ep.get("created_at", ""),
                    **content
                })

        # Session analysis
        sessions = defaultdict(list)
        for ep in parsed_episodes:
            sid = ep.get("session_id", "unknown")
            sessions[sid].append(ep)

        lines.append(f"### Session Breakdown")
        lines.append(f"")
        lines.append(f"| Session | Turns | First | Last |")
        lines.append(f"|---------|-------|-------|------|")
        for sid, turns in sorted(sessions.items(), key=lambda x: x[1][0].get("timestamp", "") if x[1] else ""):
            first_ts = turns[0].get("timestamp", "")[:19] if turns else ""
            last_ts = turns[-1].get("timestamp", "")[:19] if turns else ""
            lines.append(f"| `{sid[:8]}...` | {len(turns)} | {first_ts} | {last_ts} |")
        lines.append("")

        # Token usage
        total_input = 0
        total_output = 0
        total_cache_read = 0
        total_cache_create = 0

        for ep in parsed_episodes:
            usage = ep.get("token_usage", {})
            total_input += usage.get("input_tokens", 0)
            total_output += usage.get("output_tokens", 0)
            total_cache_read += usage.get("cache_read_tokens", 0)
            total_cache_create += usage.get("cache_creation_tokens", 0)

        lines.append(f"### Token Usage")
        lines.append(f"")
        lines.append(f"| Type | Tokens |")
        lines.append(f"|------|--------|")
        lines.append(f"| Input | {total_input:,} |")
        lines.append(f"| Output | {total_output:,} |")
        lines.append(f"| Cache Read | {total_cache_read:,} |")
        lines.append(f"| Cache Creation | {total_cache_create:,} |")
        lines.append(f"| **Total** | **{total_input + total_output + total_cache_read + total_cache_create:,}** |")
        lines.append("")

        # Tool usage
        tool_counts = defaultdict(int)
        for ep in parsed_episodes:
            for tool in ep.get("tools_used", []):
                tool_counts[tool] += 1

        if tool_counts:
            lines.append(f"### Tool Usage")
            lines.append(f"")
            lines.append(f"| Tool | Count |")
            lines.append(f"|------|-------|")
            for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                lines.append(f"| {tool} | {count} |")
            lines.append("")

        # Recent episodes
        lines.append(f"### Recent Episodes")
        lines.append(f"")
        for ep in sorted(parsed_episodes, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]:
            ts = ep.get("timestamp", "")[:19]
            user_msg = (ep.get("user_message", "") or "(no message)")[:50]
            if len(ep.get("user_message", "")) > 50:
                user_msg += "..."
            lines.append(f"- **{ts}**: {user_msg}")
        lines.append("")
    else:
        lines.append("*No episodes found.*")
        lines.append("")

    # === ENTITIES SECTION ===
    lines.append("---")
    lines.append("")
    lines.append("## Entities")
    lines.append("")

    if nodes:
        # Group by label/type
        entities_by_type = defaultdict(list)
        for node in nodes:
            labels = node.get("labels", [])
            # Get primary type (exclude "Entity" base label)
            primary_type = next((l for l in labels if l != "Entity"), "Unknown")
            entities_by_type[primary_type].append(node)

        for entity_type, entities in sorted(entities_by_type.items()):
            lines.append(f"### {entity_type} ({len(entities)})")
            lines.append(f"")
            lines.append(f"| Name | Summary |")
            lines.append(f"|------|---------|")
            for entity in sorted(entities, key=lambda x: x.get("name", "")):
                name = entity.get("name", "")[:40]
                summary = (entity.get("summary", "") or "")[:80]
                if len(entity.get("summary", "")) > 80:
                    summary += "..."
                # Escape pipes in markdown table
                name = name.replace("|", "\\|")
                summary = summary.replace("|", "\\|")
                lines.append(f"| {name} | {summary} |")
            lines.append("")
    else:
        lines.append("*No entities found.*")
        lines.append("")

    # === FACTS/RELATIONSHIPS SECTION ===
    lines.append("---")
    lines.append("")
    lines.append("## Facts & Relationships")
    lines.append("")

    if facts:
        # Group by relationship type
        facts_by_type = defaultdict(list)
        for fact in facts:
            rel_type = fact.get("name", "UNKNOWN")
            facts_by_type[rel_type].append(fact)

        lines.append(f"### Relationship Types")
        lines.append(f"")
        lines.append(f"| Type | Count |")
        lines.append(f"|------|-------|")
        for rel_type, rel_facts in sorted(facts_by_type.items(), key=lambda x: -len(x[1])):
            lines.append(f"| {rel_type} | {len(rel_facts)} |")
        lines.append("")

        # Active vs expired facts
        active_facts = [f for f in facts if f.get("expired_at") is None]
        expired_facts = [f for f in facts if f.get("expired_at") is not None]

        lines.append(f"### Fact Validity")
        lines.append(f"")
        lines.append(f"| Status | Count |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Active | {len(active_facts)} |")
        lines.append(f"| Expired | {len(expired_facts)} |")
        lines.append("")

        # Sample facts
        lines.append(f"### Sample Facts (Active)")
        lines.append(f"")
        for fact in active_facts[:10]:
            fact_text = fact.get("fact", "")[:100]
            if len(fact.get("fact", "")) > 100:
                fact_text += "..."
            lines.append(f"- {fact_text}")
        lines.append("")
    else:
        lines.append("*No facts found.*")
        lines.append("")

    # === FOOTER ===
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by `.claude/skills/graphiti/scripts/generate_report.py`*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Graphiti knowledge graph report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read from stdin (Claude pipes MCP data)
  echo '{"episodes": [...], "nodes": [...], "facts": [...]}' | %(prog)s --stdin

  # Read from file
  %(prog)s --input data.json --output report.md

  # Output JSON structure for Claude to fill
  %(prog)s --template
"""
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read JSON data from stdin"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input JSON file path"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Output the JSON template that Claude should provide"
    )
    parser.add_argument(
        "--group-id", "-g",
        default="claude-code-nci-oa-agent",
        help="Group ID for the report header"
    )

    args = parser.parse_args()

    if args.template:
        template = {
            "group_id": "claude-code-nci-oa-agent",
            "episodes": [
                {
                    "uuid": "...",
                    "name": "...",
                    "content": "{\"timestamp\": \"...\", \"session_id\": \"...\", ...}",
                    "created_at": "..."
                }
            ],
            "nodes": [
                {
                    "uuid": "...",
                    "name": "...",
                    "labels": ["Entity", "Procedure"],
                    "summary": "...",
                    "created_at": "..."
                }
            ],
            "facts": [
                {
                    "uuid": "...",
                    "name": "RELATIONSHIP_TYPE",
                    "fact": "...",
                    "expired_at": None
                }
            ]
        }
        print(json.dumps(template, indent=2))
        return

    # Load data
    if args.stdin:
        data = json.load(sys.stdin)
    elif args.input:
        data = json.loads(Path(args.input).read_text())
    else:
        print("Error: Provide --stdin, --input, or --template", file=sys.stderr)
        print("\nFor Claude to generate a report, use the MCP tools to fetch data,", file=sys.stderr)
        print("then pipe the JSON to this script:", file=sys.stderr)
        print("  1. mcp__graphiti__get_episodes", file=sys.stderr)
        print("  2. mcp__graphiti__search_nodes", file=sys.stderr)
        print("  3. mcp__graphiti__search_memory_facts", file=sys.stderr)
        print("  4. Pipe combined JSON to this script with --stdin", file=sys.stderr)
        sys.exit(1)

    # Add group_id if not in data
    if "group_id" not in data:
        data["group_id"] = args.group_id

    # Generate report
    report = generate_report(data)

    # Output
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
