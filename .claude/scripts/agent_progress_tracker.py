#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "neo4j",
#     "python-dotenv",
# ]
# ///
"""
Agent Progress Tracker - Background processor for session metrics.
Calculates and updates Neo4j with aggregated session statistics.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
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


def calculate_session_metrics(session_id: str, source_app: str) -> Optional[Dict]:
    """
    Calculate comprehensive metrics for a session.

    Returns:
        dict with:
            - total_tools: Number of tools executed
            - avg_tool_latency: Average tool execution time
            - session_duration: Total session time in ms
            - subagent_count: Number of spawned subagents
            - subagent_depth: Maximum depth of subagent hierarchy
            - entities_discovered: Number of unique entities
            - performance_tier: fast/medium/slow classification
            - tools_breakdown: Count by tool type
    """

    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            # Get session and tool metrics
            result = session.run("""
                MATCH (s:Session {id: $session_id, source_app: $source_app})
                OPTIONAL MATCH (s)-[:EXECUTED]->(t:Tool)
                OPTIONAL MATCH (t)-[:DISCOVERED]->(e:Entity)
                WITH s,
                     count(DISTINCT t) as tool_count,
                     avg(t.latency_ms) as avg_latency,
                     collect(DISTINCT t.name) as tool_names,
                     count(DISTINCT e) as entity_count,
                     s.end_time - s.start_time as duration
                RETURN
                    tool_count,
                    avg_latency,
                    tool_names,
                    entity_count,
                    duration,
                    s.start_time as start_time,
                    s.end_time as end_time
            """, {
                'session_id': session_id,
                'source_app': source_app
            })

            record = result.single()
            if not record:
                return None

            # Get subagent metrics
            subagent_result = session.run("""
                MATCH (s:Session {id: $session_id, source_app: $source_app})
                OPTIONAL MATCH path = (s)-[:SPAWNED*]->(child:Session)
                WITH s,
                     count(DISTINCT child) as child_count,
                     max(length(path)) as max_depth
                RETURN child_count, max_depth
            """, {
                'session_id': session_id,
                'source_app': source_app
            })

            subagent_record = subagent_result.single()

            # Calculate metrics
            total_tools = record['tool_count'] or 0
            avg_latency = record['avg_latency'] or 0
            duration = record['duration'] or 0
            entity_count = record['entity_count'] or 0
            tool_names = record['tool_names'] or []

            subagent_count = subagent_record['child_count'] if subagent_record else 0
            subagent_depth = subagent_record['max_depth'] if subagent_record else 0

            # Tools breakdown
            tools_breakdown = {}
            for tool_name in tool_names:
                tools_breakdown[tool_name] = tools_breakdown.get(tool_name, 0) + 1

            # Performance tier classification
            # Fast: avg < 1000ms, Medium: 1000-3000ms, Slow: > 3000ms
            if avg_latency < 1000:
                performance_tier = 'fast'
            elif avg_latency < 3000:
                performance_tier = 'medium'
            else:
                performance_tier = 'slow'

            metrics = {
                'total_tools': total_tools,
                'avg_tool_latency': round(avg_latency, 2),
                'session_duration_ms': duration,
                'session_duration_sec': round(duration / 1000, 2) if duration else 0,
                'subagent_count': subagent_count,
                'subagent_depth': subagent_depth,
                'entities_discovered': entity_count,
                'performance_tier': performance_tier,
                'tools_breakdown': tools_breakdown,
                'entity_discovery_rate': round(entity_count / total_tools, 2) if total_tools > 0 else 0
            }

            return metrics

    finally:
        driver.close()


def update_session_metrics(session_id: str, source_app: str, metrics: Dict) -> None:
    """Update session node with calculated metrics."""

    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            session.run("""
                MATCH (s:Session {id: $session_id, source_app: $source_app})
                SET
                    s.total_tools = $total_tools,
                    s.avg_tool_latency = $avg_tool_latency,
                    s.session_duration_ms = $session_duration_ms,
                    s.session_duration_sec = $session_duration_sec,
                    s.subagent_count = $subagent_count,
                    s.subagent_depth = $subagent_depth,
                    s.entities_discovered = $entities_discovered,
                    s.performance_tier = $performance_tier,
                    s.entity_discovery_rate = $entity_discovery_rate,
                    s.tools_breakdown = $tools_breakdown,
                    s.metrics_updated_at = $timestamp
            """, {
                'session_id': session_id,
                'source_app': source_app,
                'total_tools': metrics['total_tools'],
                'avg_tool_latency': metrics['avg_tool_latency'],
                'session_duration_ms': metrics['session_duration_ms'],
                'session_duration_sec': metrics['session_duration_sec'],
                'subagent_count': metrics['subagent_count'],
                'subagent_depth': metrics['subagent_depth'],
                'entities_discovered': metrics['entities_discovered'],
                'performance_tier': metrics['performance_tier'],
                'entity_discovery_rate': metrics['entity_discovery_rate'],
                'tools_breakdown': json.dumps(metrics['tools_breakdown']),
                'timestamp': int(datetime.now().timestamp() * 1000)
            })

    finally:
        driver.close()


def calculate_performance_baselines() -> Dict:
    """
    Calculate performance baselines across all sessions.

    Returns:
        dict with p50, p90, p99 latencies and tool usage stats
    """

    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            # Get latency percentiles
            result = session.run("""
                MATCH (t:Tool)
                WHERE t.latency_ms IS NOT NULL
                WITH t.latency_ms as latency
                ORDER BY latency
                WITH collect(latency) as latencies
                WITH latencies,
                     size(latencies) as total_count,
                     latencies[toInteger(size(latencies) * 0.5)] as p50,
                     latencies[toInteger(size(latencies) * 0.9)] as p90,
                     latencies[toInteger(size(latencies) * 0.99)] as p99
                RETURN p50, p90, p99, total_count
            """)

            record = result.single()

            if not record:
                return {'p50': 0, 'p90': 0, 'p99': 0, 'total_count': 0}

            # Get most used tools
            tool_result = session.run("""
                MATCH (t:Tool)
                WITH t.name as tool_name, count(*) as usage_count
                ORDER BY usage_count DESC
                LIMIT 10
                RETURN collect({name: tool_name, count: usage_count}) as top_tools
            """)

            tool_record = tool_result.single()

            baselines = {
                'p50_latency': record['p50'] or 0,
                'p90_latency': record['p90'] or 0,
                'p99_latency': record['p99'] or 0,
                'total_tool_executions': record['total_count'],
                'top_tools': tool_record['top_tools'] if tool_record else []
            }

            return baselines

    finally:
        driver.close()


def main():
    """Main entry point - reads stdin and calculates metrics."""

    try:
        # Read hook data from stdin
        hook_data = json.load(sys.stdin)

        session_id = hook_data.get('session_id', 'unknown')
        source_app = hook_data.get('payload', {}).get('source_app', 'unknown')
        hook_event = hook_data.get('hook_event_name', 'unknown')

        # Only process on Stop event (when session completes)
        if hook_event != 'Stop':
            sys.exit(0)

        # Calculate session metrics
        metrics = calculate_session_metrics(session_id, source_app)

        if metrics:
            # Update session with metrics
            update_session_metrics(session_id, source_app, metrics)

            # Calculate global baselines
            baselines = calculate_performance_baselines()

            print(f"✓ Updated metrics for {source_app}:{session_id[:8]}", file=sys.stderr)
            print(f"  Tools: {metrics['total_tools']}, "
                  f"Avg Latency: {metrics['avg_tool_latency']}ms, "
                  f"Entities: {metrics['entities_discovered']}, "
                  f"Tier: {metrics['performance_tier']}", file=sys.stderr)
            print(f"  Baselines - P50: {baselines['p50_latency']}ms, "
                  f"P90: {baselines['p90_latency']}ms", file=sys.stderr)
        else:
            print(f"⚠ No metrics found for {source_app}:{session_id[:8]}", file=sys.stderr)

    except Exception as e:
        print(f"✗ Failed to calculate metrics: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Always exit 0 to not block Claude
    sys.exit(0)


if __name__ == "__main__":
    main()
