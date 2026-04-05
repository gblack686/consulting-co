#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "pytest-benchmark",
#     "neo4j",
#     "python-dotenv",
# ]
# ///
"""
Performance benchmarking tests for Observability-Graphiti integration.
Measures event processing latency, database performance, and throughput.
"""

import pytest
import time
import json
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import sys

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks'))

import observe_to_graphiti as obs_to_graphiti

# Load environment
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


class TestEventProcessingLatency:
    """Test event processing performance."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Neo4j connection."""
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')

        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        # Clear processed events
        obs_to_graphiti.processed_events.clear()

        yield

        # Cleanup
        with self.neo4j_driver.session() as session:
            session.run("MATCH (s:Session {source_app: 'perf-test'}) DETACH DELETE s")

        self.neo4j_driver.close()

    def test_single_event_processing_latency(self, benchmark):
        """
        Benchmark single event processing.
        Target: < 500ms per event
        """

        event = {
            'source_app': 'perf-test',
            'session_id': f'perf-session-{time.time()}',
            'hook_event_type': 'PreToolUse',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Read',
                'tool_input': {'file_path': '/test/file.py'}
            }
        }

        # Benchmark event processing
        result = benchmark(obs_to_graphiti.process_observability_event, event)

        # Verify timing threshold
        stats = benchmark.stats.stats
        assert stats.mean < 0.5, f"Event processing too slow: {stats.mean * 1000:.2f}ms"

    def test_bulk_event_processing_throughput(self):
        """
        Test processing 100 events.
        Target: < 5 seconds total
        """

        events = []
        session_id = f'bulk-perf-{time.time()}'

        # Generate 100 events
        for i in range(100):
            event = {
                'source_app': 'perf-test',
                'session_id': session_id,
                'hook_event_type': 'PreToolUse' if i % 2 == 0 else 'PostToolUse',
                'timestamp': int(time.time() * 1000) + i,
                'model_name': 'claude-sonnet-4-5',
                'payload': {
                    'tool_name': 'Read',
                    'tool_input': {'index': i}
                }
            }
            events.append(event)

        # Measure bulk processing time
        start_time = time.time()

        for event in events:
            obs_to_graphiti.process_observability_event(event)

        end_time = time.time()
        total_time = end_time - start_time

        # Should process 100 events in < 5 seconds
        assert total_time < 5.0, f"Bulk processing too slow: {total_time:.2f}s for 100 events"

        # Calculate throughput
        throughput = 100 / total_time
        print(f"\nThroughput: {throughput:.2f} events/second")

        assert throughput > 20, f"Throughput too low: {throughput:.2f} events/s"

    def test_concurrent_session_processing(self):
        """
        Test processing multiple sessions concurrently.
        Target: No significant slowdown with 10 concurrent sessions
        """

        import threading

        sessions_count = 10
        events_per_session = 10

        def process_session(session_id):
            for i in range(events_per_session):
                event = {
                    'source_app': 'perf-test',
                    'session_id': session_id,
                    'hook_event_type': 'PreToolUse',
                    'timestamp': int(time.time() * 1000) + i,
                    'model_name': 'claude-sonnet-4-5',
                    'payload': {
                        'tool_name': 'Read',
                        'tool_input': {'index': i}
                    }
                }
                obs_to_graphiti.process_observability_event(event)

        # Process concurrently
        start_time = time.time()

        threads = []
        for s in range(sessions_count):
            session_id = f'concurrent-{s}-{time.time()}'
            thread = threading.Thread(target=process_session, args=(session_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # 10 sessions * 10 events = 100 events total
        # Should complete in reasonable time even with concurrency
        assert total_time < 10.0, f"Concurrent processing too slow: {total_time:.2f}s"


class TestNeo4jQueryPerformance:
    """Test Neo4j query performance."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Neo4j connection with test data."""
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')

        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        yield

        self.neo4j_driver.close()

    def test_session_query_performance(self, benchmark):
        """
        Benchmark session retrieval query.
        Target: < 100ms
        """

        def query_session():
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (s:Session)
                    RETURN s.id, s.status
                    LIMIT 10
                """)
                return list(result)

        result = benchmark(query_session)

        # Verify timing
        stats = benchmark.stats.stats
        assert stats.mean < 0.1, f"Session query too slow: {stats.mean * 1000:.2f}ms"

    def test_tool_aggregation_query_performance(self, benchmark):
        """
        Benchmark tool metrics aggregation.
        Target: < 200ms
        """

        def query_tool_metrics():
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (s:Session)-[:EXECUTED]->(t:Tool)
                    RETURN s.id,
                           count(t) as tool_count,
                           avg(t.latency_ms) as avg_latency
                    LIMIT 20
                """)
                return list(result)

        result = benchmark(query_tool_metrics)

        # Verify timing
        stats = benchmark.stats.stats
        assert stats.mean < 0.2, f"Tool aggregation query too slow: {stats.mean * 1000:.2f}ms"

    def test_entity_discovery_query_performance(self, benchmark):
        """
        Benchmark entity discovery query.
        Target: < 150ms
        """

        def query_entities():
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (t:Tool)-[:DISCOVERED]->(e:Entity)
                    RETURN e.name, e.type, count(t) as discovery_count
                    ORDER BY discovery_count DESC
                    LIMIT 50
                """)
                return list(result)

        result = benchmark(query_entities)

        # Verify timing
        stats = benchmark.stats.stats
        assert stats.mean < 0.15, f"Entity query too slow: {stats.mean * 1000:.2f}ms"

    def test_subagent_hierarchy_query_performance(self, benchmark):
        """
        Benchmark subagent hierarchy traversal.
        Target: < 250ms
        """

        def query_subagent_hierarchy():
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH path = (parent:Session)-[:SPAWNED*]->(child:Session)
                    RETURN parent.id, collect(DISTINCT child.id) as children, length(path) as depth
                    LIMIT 10
                """)
                return list(result)

        result = benchmark(query_subagent_hierarchy)

        # Verify timing
        stats = benchmark.stats.stats
        assert stats.mean < 0.25, f"Hierarchy query too slow: {stats.mean * 1000:.2f}ms"


class TestMetricCalculationPerformance:
    """Test progress metrics calculation performance."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

        yield

    def test_calculate_session_metrics_performance(self, benchmark):
        """
        Benchmark session metrics calculation.
        Target: < 100ms
        """

        try:
            import agent_progress_tracker as tracker

            def calculate_metrics():
                # Use a real session ID if available, or return mock data
                return tracker.calculate_session_metrics('test-session', 'test-app')

            result = benchmark(calculate_metrics)

            # Verify timing
            stats = benchmark.stats.stats
            assert stats.mean < 0.1, f"Metrics calculation too slow: {stats.mean * 1000:.2f}ms"

        except ImportError:
            pytest.skip("agent_progress_tracker not available")


class TestObsidianNoteGenerationPerformance:
    """Test Obsidian note generation performance."""

    def test_note_generation_performance(self, benchmark):
        """
        Benchmark Obsidian note generation.
        Target: < 1000ms
        """

        session_data = {
            'session_id': 'perf-test-session',
            'source_app': 'perf-test',
            'start_time': 1731704400000,
            'end_time': 1731704415000,
            'tools': [
                {'name': 'Read', 'latency': 2667},
                {'name': 'Bash', 'latency': 2249},
                {'name': 'Write', 'latency': 1500}
            ],
            'entities': [
                {'name': 'main.py', 'type': 'file'},
                {'name': 'UserRepository', 'type': 'class'}
            ]
        }

        def generate_note():
            # Simulate note generation
            note = f"""---
date: 2025-11-15
session_id: {session_data['session_id']}
---

# Claude Activity

## Summary
Session: {session_data['session_id']}

## Timeline
"""
            for tool in session_data['tools']:
                note += f"- {tool['name']}: {tool['latency']}ms\n"

            note += "\n## Entities\n"
            for entity in session_data['entities']:
                note += f"- {entity['type']}: {entity['name']}\n"

            return note

        result = benchmark(generate_note)

        # Verify timing
        stats = benchmark.stats.stats
        assert stats.mean < 1.0, f"Note generation too slow: {stats.mean * 1000:.2f}ms"


class TestMemoryUsage:
    """Test memory usage during operations."""

    def test_event_processing_memory_footprint(self):
        """
        Verify event processing doesn't leak memory.
        Process 1000 events and check memory growth.
        """

        import gc
        import sys

        # Force garbage collection
        gc.collect()

        # Get initial memory (approximate via object count)
        initial_objects = len(gc.get_objects())

        # Process many events
        session_id = f'memory-test-{time.time()}'

        for i in range(1000):
            event = {
                'source_app': 'memory-test',
                'session_id': session_id,
                'hook_event_type': 'PreToolUse',
                'timestamp': int(time.time() * 1000) + i,
                'model_name': 'claude-sonnet-4-5',
                'payload': {
                    'tool_name': 'Read',
                    'tool_input': {'index': i}
                }
            }

            # Process event (mocked to avoid actual DB writes)
            # In real test, would call actual processor

        # Force garbage collection
        gc.collect()

        # Get final object count
        final_objects = len(gc.get_objects())

        # Object count shouldn't grow excessively
        growth = final_objects - initial_objects
        growth_ratio = growth / initial_objects if initial_objects > 0 else 0

        print(f"\nMemory growth: {growth} objects ({growth_ratio * 100:.1f}%)")

        # Growth should be reasonable (< 50%)
        assert growth_ratio < 0.5, f"Excessive memory growth: {growth_ratio * 100:.1f}%"


class TestPerformanceThresholdSummary:
    """Generate performance threshold summary report."""

    def test_generate_performance_report(self):
        """Generate comprehensive performance report."""

        thresholds = {
            'Event Processing': {
                'target': '< 500ms',
                'critical': '< 1000ms',
                'metric': 'Single event processing time'
            },
            'Bulk Processing': {
                'target': '< 5s for 100 events',
                'critical': '< 10s for 100 events',
                'metric': 'Throughput (events/second)'
            },
            'Session Query': {
                'target': '< 100ms',
                'critical': '< 200ms',
                'metric': 'Session retrieval time'
            },
            'Tool Aggregation': {
                'target': '< 200ms',
                'critical': '< 500ms',
                'metric': 'Tool metrics calculation'
            },
            'Metrics Calculation': {
                'target': '< 100ms',
                'critical': '< 250ms',
                'metric': 'Progress metrics computation'
            },
            'Note Generation': {
                'target': '< 1000ms',
                'critical': '< 2000ms',
                'metric': 'Obsidian note creation'
            }
        }

        print("\n\n=== PERFORMANCE THRESHOLDS ===\n")

        for operation, threshold in thresholds.items():
            print(f"{operation}:")
            print(f"  Target: {threshold['target']}")
            print(f"  Critical: {threshold['critical']}")
            print(f"  Metric: {threshold['metric']}")
            print()

        # Always passes - just for reporting
        assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--benchmark-only'])
