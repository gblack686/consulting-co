#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "neo4j",
#     "python-dotenv",
# ]
# ///
"""
Unit tests for observe_to_graphiti.py hook.
Tests event transformation, Neo4j writes, and entity extraction.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks'))

import observe_to_graphiti as obs_to_graphiti


class TestEventProcessing:
    """Test event transformation and routing."""

    def test_process_observability_event_deduplication(self):
        """Test that duplicate events are not processed twice."""

        event = {
            'source_app': 'test-app',
            'session_id': 'test-session-123',
            'hook_event_type': 'PreToolUse',
            'timestamp': 1731704400000,
            'model_name': 'claude-sonnet-4-5',
            'payload': {
                'tool_name': 'Read',
                'tool_input': {'file_path': '/test/file.py'}
            }
        }

        with patch.object(obs_to_graphiti, 'get_neo4j_driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            # First call should process
            obs_to_graphiti.process_observability_event(event)
            assert mock_session.run.called

            # Reset mock
            mock_session.run.reset_mock()

            # Second call with same event should skip
            obs_to_graphiti.process_observability_event(event)
            assert not mock_session.run.called

    def test_session_node_creation(self):
        """Test that Session nodes are created with correct properties."""

        event = {
            'source_app': 'test-app',
            'session_id': 'test-session-456',
            'hook_event_type': 'PreToolUse',
            'timestamp': 1731704400000,
            'model_name': 'claude-sonnet-4-5',
            'payload': {}
        }

        # Clear processed events set
        obs_to_graphiti.processed_events.clear()

        with patch.object(obs_to_graphiti, 'get_neo4j_driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            obs_to_graphiti.process_observability_event(event)

            # Verify Session MERGE query was called
            calls = mock_session.run.call_args_list
            assert len(calls) > 0

            # Check first call is Session creation
            session_query = calls[0][0][0]
            assert 'MERGE (s:Session' in session_query
            assert calls[0][1]['session_id'] == 'test-session-456'
            assert calls[0][1]['source_app'] == 'test-app'
            assert calls[0][1]['model_name'] == 'claude-sonnet-4-5'


class TestPreToolUseHandler:
    """Test PreToolUse event handling."""

    def test_tool_node_creation(self):
        """Test that Tool nodes are created with running status."""

        event = {
            'timestamp': 1731704400000,
            'payload': {
                'tool_name': 'Bash',
                'tool_input': {'command': 'ls -la'}
            }
        }

        mock_session = MagicMock()

        obs_to_graphiti.handle_pre_tool_use(
            mock_session,
            event,
            'test-session-789',
            'test-app'
        )

        # Verify Tool MERGE query
        query = mock_session.run.call_args[0][0]
        params = mock_session.run.call_args[1]

        assert 'MERGE (t:Tool' in query
        assert params['tool_name'] == 'Bash'
        assert 'ls -la' in params['tool_input']
        assert params['timestamp'] == 1731704400000
        assert 'running' in query.lower()

    def test_tool_session_relationship(self):
        """Test that EXECUTED relationship is created."""

        event = {
            'timestamp': 1731704400000,
            'payload': {
                'tool_name': 'Read',
                'tool_input': {'file_path': '/test.txt'}
            }
        }

        mock_session = MagicMock()

        obs_to_graphiti.handle_pre_tool_use(
            mock_session,
            event,
            'test-session-xyz',
            'test-app'
        )

        # Verify relationship creation
        query = mock_session.run.call_args[0][0]
        assert 'MERGE (s)-[:EXECUTED]->(t)' in query or 'MERGE (s)-[:EXECUTED]->(t)' in query


class TestPostToolUseHandler:
    """Test PostToolUse event handling."""

    def test_tool_completion_update(self):
        """Test that Tool nodes are updated with results."""

        event = {
            'timestamp': 1731704402667,
            'payload': {
                'tool_name': 'Read',
                'tool_output': 'File content here...'
            }
        }

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__ = lambda self, key: 'test-tool-123' if key == 'tool_id' else 2667
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result

        obs_to_graphiti.handle_post_tool_use(
            mock_session,
            event,
            'test-session-abc',
            'test-app'
        )

        # Verify update query
        query = mock_session.run.call_args_list[0][0][0]
        params = mock_session.run.call_args_list[0][1]

        assert 'SET' in query
        assert 't.output' in query
        assert 't.end_time' in query
        assert 't.latency_ms' in query
        assert 't.status' in query
        assert params['tool_name'] == 'Read'

    def test_latency_calculation(self):
        """Test that latency is calculated correctly."""

        event = {
            'timestamp': 1731704405000,
            'payload': {
                'tool_name': 'Bash',
                'tool_output': 'Command executed'
            }
        }

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__ = lambda self, key: 'test-tool-456' if key == 'tool_id' else 5000
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result

        obs_to_graphiti.handle_post_tool_use(
            mock_session,
            event,
            'test-session-def',
            'test-app'
        )

        # Verify latency is calculated
        query = mock_session.run.call_args_list[0][0][0]
        assert 't.latency_ms = $timestamp - t.start_time' in query


class TestEntityExtraction:
    """Test entity extraction from tool outputs."""

    def test_file_extraction_from_read_tool(self):
        """Test extracting file paths from Read tool output."""

        output = """
        Reading file: /c/Users/test/project/src/main.py
        Also found: /home/user/docs/readme.md
        And C:\\Windows\\System32\\config.ini
        """

        entities = obs_to_graphiti.extract_entities_from_tool_output(output, 'Read')

        assert len(entities) > 0
        assert any(e['type'] == 'file' for e in entities)
        assert any('main.py' in e['name'] for e in entities)

    def test_function_extraction_from_code(self):
        """Test extracting function names from code output."""

        output = """
        def process_data(input_file):
            return result

        async def fetch_api_data():
            pass
        """

        entities = obs_to_graphiti.extract_entities_from_tool_output(output, 'Grep')

        function_entities = [e for e in entities if e['type'] == 'function']
        assert len(function_entities) > 0
        assert any('process_data' in e['name'] for e in function_entities)
        assert any('fetch_api_data' in e['name'] for e in function_entities)

    def test_class_extraction_from_code(self):
        """Test extracting class names from code output."""

        output = """
        class UserRepository:
            def __init__(self):
                pass

        class DataProcessor:
            pass
        """

        entities = obs_to_graphiti.extract_entities_from_tool_output(output, 'Bash')

        class_entities = [e for e in entities if e['type'] == 'class']
        assert len(class_entities) > 0
        assert any('UserRepository' in e['name'] for e in class_entities)
        assert any('DataProcessor' in e['name'] for e in class_entities)

    def test_entity_limit(self):
        """Test that entity extraction is limited to prevent overflow."""

        # Create output with many file paths
        output = '\n'.join([f'/path/to/file_{i}.txt' for i in range(100)])

        entities = obs_to_graphiti.extract_entities_from_tool_output(output, 'Glob')

        # Should be limited to 10 files
        assert len(entities) <= 10


class TestSubagentHandling:
    """Test subagent tracking and hierarchy."""

    def test_subagent_completion_with_parent(self):
        """Test SubagentStop creates parent-child relationship."""

        event = {
            'timestamp': 1731704410000,
            'payload': {
                'parent_session_id': 'parent-session-123'
            }
        }

        mock_session = MagicMock()

        obs_to_graphiti.handle_subagent_completion(
            mock_session,
            event,
            'subagent-session-456',
            'test-app'
        )

        # Verify SPAWNED relationship
        query = mock_session.run.call_args[0][0]
        params = mock_session.run.call_args[1]

        assert 'SPAWNED' in query
        assert params['parent_id'] == 'parent-session-123'
        assert params['session_id'] == 'subagent-session-456'

    def test_subagent_status_update(self):
        """Test that subagent status is set to completed."""

        event = {
            'timestamp': 1731704415000,
            'payload': {
                'parent_session_id': 'parent-xyz'
            }
        }

        mock_session = MagicMock()

        obs_to_graphiti.handle_subagent_completion(
            mock_session,
            event,
            'subagent-789',
            'test-app'
        )

        query = mock_session.run.call_args[0][0]

        assert "child.status = 'completed'" in query
        assert 'child.end_time' in query


class TestStopHandler:
    """Test Stop event handling."""

    def test_session_completion(self):
        """Test that session is marked as completed."""

        event = {
            'timestamp': 1731704420000,
            'payload': {}
        }

        mock_session = MagicMock()

        obs_to_graphiti.handle_stop(
            mock_session,
            event,
            'session-complete-123',
            'test-app'
        )

        query = mock_session.run.call_args[0][0]
        params = mock_session.run.call_args[1]

        assert "s.status = 'completed'" in query
        assert 's.end_time' in query
        assert params['session_id'] == 'session-complete-123'


class TestNeo4jDriver:
    """Test Neo4j driver creation."""

    @patch.dict('os.environ', {
        'NEO4J_URI': 'bolt://test:7687',
        'NEO4J_USER': 'test_user',
        'NEO4J_PASSWORD': 'test_pass'
    })
    @patch('observe_to_graphiti.GraphDatabase')
    def test_driver_from_env(self, mock_graphdb):
        """Test that driver is created from environment variables."""

        obs_to_graphiti.get_neo4j_driver()

        mock_graphdb.driver.assert_called_once_with(
            'bolt://test:7687',
            auth=('test_user', 'test_pass')
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
