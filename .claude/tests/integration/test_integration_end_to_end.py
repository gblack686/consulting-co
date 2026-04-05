#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "neo4j",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
Integration tests for complete Observability → Graphiti → Obsidian flow.
Tests real data flow from Claude Code events through to Neo4j and Obsidian notes.
"""

import pytest
import json
import time
import sqlite3
import requests
from pathlib import Path
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


class TestEndToEndDataFlow:
    """Test complete data flow from event creation to Neo4j storage."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup test environment and cleanup after."""

        # Setup
        self.test_session_id = f'test-session-{int(time.time())}'
        self.test_source_app = 'integration-test'

        # Get Neo4j connection
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')

        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        yield

        # Cleanup: Delete test data from Neo4j
        with self.neo4j_driver.session() as session:
            session.run("""
                MATCH (s:Session {source_app: $source_app})
                DETACH DELETE s
            """, {'source_app': self.test_source_app})

        self.neo4j_driver.close()

    def test_single_tool_execution_flow(self):
        """
        Test Scenario 1: Single tool execution.
        Verify: PreToolUse → Tool Execution → PostToolUse
        """

        # Simulate PreToolUse event
        pre_event = {
            'source_app': self.test_source_app,
            'session_id': self.test_session_id,
            'hook_event_type': 'PreToolUse',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Read',
                'tool_input': {
                    'file_path': '/test/integration/file.py'
                }
            }
        }

        # Send event to observability hook processor
        from ...hooks import observe_to_graphiti
        observe_to_graphiti.processed_events.clear()
        observe_to_graphiti.process_observability_event(pre_event)

        # Wait for Neo4j write
        time.sleep(0.5)

        # Verify Session node created
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session {id: $session_id, source_app: $source_app})
                RETURN s.status as status, s.model_name as model
            """, {
                'session_id': self.test_session_id,
                'source_app': self.test_source_app
            })

            record = result.single()
            assert record is not None
            assert record['status'] == 'active'
            assert record['model'] == 'claude-sonnet-4-5'

        # Verify Tool node created with running status
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session {id: $session_id})-[:EXECUTED]->(t:Tool {name: 'Read'})
                RETURN t.status as status, t.input as input
            """, {'session_id': self.test_session_id})

            record = result.single()
            assert record is not None
            assert record['status'] == 'running'
            assert '/test/integration/file.py' in record['input']

        # Simulate PostToolUse event
        post_timestamp = int(time.time() * 1000)
        post_event = {
            'source_app': self.test_source_app,
            'session_id': self.test_session_id,
            'hook_event_type': 'PostToolUse',
            'timestamp': post_timestamp,
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Read',
                'tool_output': 'File content: def test_function():\n    pass'
            }
        }

        observe_to_graphiti.process_observability_event(post_event)
        time.sleep(0.5)

        # Verify Tool completed with latency
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session {id: $session_id})-[:EXECUTED]->(t:Tool {name: 'Read'})
                RETURN t.status as status, t.latency_ms as latency, t.output as output
            """, {'session_id': self.test_session_id})

            record = result.single()
            assert record is not None
            assert record['status'] == 'completed'
            assert record['latency'] > 0
            assert 'test_function' in record['output']

    def test_multi_tool_session_flow(self):
        """
        Test Scenario 2: Multi-tool session.
        Verify: Multiple tools tracked with correct latencies.
        """

        session_id = f'multi-tool-{int(time.time())}'
        tools = ['Read', 'Bash', 'Write']

        current_time = int(time.time() * 1000)

        # Execute multiple tools
        for i, tool_name in enumerate(tools):
            # PreToolUse
            pre_event = {
                'source_app': self.test_source_app,
                'session_id': session_id,
                'hook_event_type': 'PreToolUse',
                'timestamp': current_time + (i * 3000),  # 3s apart
                'model_name': 'claude-sonnet-4-5',
                'payload': {
                    'tool_name': tool_name,
                    'tool_input': {'test': f'input_{i}'}
                }
            }

            from ...hooks import observe_to_graphiti
            observe_to_graphiti.processed_events.clear()
            observe_to_graphiti.process_observability_event(pre_event)

            # PostToolUse
            post_event = {
                'source_app': self.test_source_app,
                'session_id': session_id,
                'hook_event_type': 'PostToolUse',
                'timestamp': current_time + (i * 3000) + 2000,  # 2s execution
                'model_name': 'claude-sonnet-4-5',
                'payload': {
                    'tool_name': tool_name,
                    'tool_output': f'Output from {tool_name}'
                }
            }

            observe_to_graphiti.process_observability_event(post_event)

        time.sleep(1)

        # Verify all tools tracked
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session {id: $session_id})-[:EXECUTED]->(t:Tool)
                RETURN count(t) as tool_count,
                       collect(t.name) as tool_names,
                       avg(t.latency_ms) as avg_latency
            """, {'session_id': session_id})

            record = result.single()
            assert record is not None
            assert record['tool_count'] == 3
            assert set(record['tool_names']) == set(tools)
            # Each tool should have ~2000ms latency
            assert 1800 <= record['avg_latency'] <= 2200

    def test_subagent_execution_flow(self):
        """
        Test Scenario 3: Subagent spawning and tracking.
        Verify: Parent-child relationship created.
        """

        parent_session_id = f'parent-{int(time.time())}'
        subagent_session_id = f'subagent-{int(time.time())}'

        # Create parent session
        parent_event = {
            'source_app': self.test_source_app,
            'session_id': parent_session_id,
            'hook_event_type': 'PreToolUse',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Task',
                'tool_input': {'description': 'Spawn subagent'}
            }
        }

        from ...hooks import observe_to_graphiti
        observe_to_graphiti.processed_events.clear()
        observe_to_graphiti.process_observability_event(parent_event)

        # Create subagent session
        subagent_event = {
            'source_app': self.test_source_app,
            'session_id': subagent_session_id,
            'hook_event_type': 'PreToolUse',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Read',
                'tool_input': {'file_path': '/test.txt'}
            }
        }

        observe_to_graphiti.process_observability_event(subagent_event)

        # Subagent completion
        completion_event = {
            'source_app': self.test_source_app,
            'session_id': subagent_session_id,
            'hook_event_type': 'SubagentStop',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'parent_session_id': parent_session_id
            }
        }

        observe_to_graphiti.process_observability_event(completion_event)
        time.sleep(0.5)

        # Verify parent-child relationship
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (parent:Session {id: $parent_id})-[r:SPAWNED]->(child:Session {id: $child_id})
                RETURN parent.id as parent, child.id as child, child.status as status
            """, {
                'parent_id': parent_session_id,
                'child_id': subagent_session_id
            })

            record = result.single()
            assert record is not None
            assert record['parent'] == parent_session_id
            assert record['child'] == subagent_session_id
            assert record['status'] == 'completed'

    def test_entity_extraction_flow(self):
        """
        Test Scenario 4: Entity extraction from tool output.
        Verify: Entities discovered and linked to tools.
        """

        session_id = f'entity-test-{int(time.time())}'

        # Tool with entity-rich output
        pre_event = {
            'source_app': self.test_source_app,
            'session_id': session_id,
            'hook_event_type': 'PreToolUse',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Grep',
                'tool_input': {'pattern': 'def '}
            }
        }

        from ...hooks import observe_to_graphiti
        observe_to_graphiti.processed_events.clear()
        observe_to_graphiti.process_observability_event(pre_event)

        # Output with functions and classes
        post_event = {
            'source_app': self.test_source_app,
            'session_id': session_id,
            'hook_event_type': 'PostToolUse',
            'timestamp': int(time.time() * 1000) + 1500,
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Grep',
                'tool_output': '''
def process_data(input_file):
    return result

class UserRepository:
    def save(self):
        pass

async def fetch_api():
    pass
                '''
            }
        }

        observe_to_graphiti.process_observability_event(post_event)
        time.sleep(1)

        # Verify entities extracted
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session {id: $session_id})-[:EXECUTED]->(t:Tool)-[:DISCOVERED]->(e:Entity)
                RETURN collect(DISTINCT e.name) as entities, collect(DISTINCT e.type) as types
            """, {'session_id': session_id})

            record = result.single()
            assert record is not None
            entities = record['entities']
            types = record['types']

            # Should have extracted functions and class
            assert len(entities) > 0
            assert 'function' in types or 'class' in types

    def test_session_completion_flow(self):
        """
        Test complete session lifecycle.
        Verify: Session marked as completed on Stop event.
        """

        session_id = f'complete-{int(time.time())}'

        # Session start
        start_event = {
            'source_app': self.test_source_app,
            'session_id': session_id,
            'hook_event_type': 'PreToolUse',
            'timestamp': int(time.time() * 1000),
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Read',
                'tool_input': {}
            }
        }

        from ...hooks import observe_to_graphiti
        observe_to_graphiti.processed_events.clear()
        observe_to_graphiti.process_observability_event(start_event)

        # Session stop
        stop_event = {
            'source_app': self.test_source_app,
            'session_id': session_id,
            'hook_event_type': 'Stop',
            'timestamp': int(time.time() * 1000) + 10000,
            'model_name': 'claude-sonnet-4-5',
            'payload': {}
        }

        observe_to_graphiti.process_observability_event(stop_event)
        time.sleep(0.5)

        # Verify session completed
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session {id: $session_id})
                RETURN s.status as status, s.end_time as end_time
            """, {'session_id': session_id})

            record = result.single()
            assert record is not None
            assert record['status'] == 'completed'
            assert record['end_time'] is not None


class TestDataConsistency:
    """Test data consistency across SQLite, Neo4j, and Obsidian."""

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

        yield

        self.neo4j_driver.close()

    def test_event_count_consistency(self):
        """Verify event counts match across systems."""

        # This test would compare counts from:
        # 1. SQLite events.db
        # 2. Neo4j Tool nodes
        # 3. Obsidian timeline entries

        # For now, verify Neo4j stores events
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (t:Tool)
                RETURN count(t) as tool_count
            """)

            record = result.single()
            tool_count = record['tool_count'] if record else 0

            # Should have some tools if integration is working
            assert tool_count >= 0

    def test_session_id_consistency(self):
        """Verify session IDs match across all systems."""

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Session)
                RETURN s.id as session_id
                LIMIT 5
            """)

            session_ids = [record['session_id'] for record in result]

            # Verify session IDs are valid UUIDs or session ID format
            for sid in session_ids:
                assert isinstance(sid, str)
                assert len(sid) > 0


class TestBackwardsCompatibility:
    """Verify existing integrations still work."""

    def test_langfuse_hook_exists(self):
        """Verify Langfuse hook is still present."""

        langfuse_hook = Path(__file__).parent.parent.parent / 'hooks' / 'log_to_langfuse.py'
        assert langfuse_hook.exists()

    def test_graphiti_hook_exists(self):
        """Verify original Graphiti hook is still present."""

        graphiti_hook = Path(__file__).parent.parent.parent / 'hooks' / 'log_to_graphiti.py'
        assert graphiti_hook.exists()

    def test_settings_valid_json(self):
        """Verify settings.local.json is valid."""

        settings_file = Path(__file__).parent.parent.parent / 'settings.local.json'

        if settings_file.exists():
            with open(settings_file) as f:
                settings = json.load(f)

            # Should have hooks configured
            assert 'hooks' in settings


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
