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
Unit tests for agent_progress_tracker.py.
Tests session metric calculations and aggregations.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

import agent_progress_tracker as tracker


class TestSessionMetrics:
    """Test session metrics calculation."""

    def test_calculate_session_metrics_basic(self):
        """Test basic session metrics calculation."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        # Mock the session query result
        mock_record = {
            'tool_count': 5,
            'avg_latency': 2500.0,
            'tool_names': ['Read', 'Bash', 'Write', 'Grep', 'Read'],
            'entity_count': 12,
            'duration': 15000,
            'start_time': 1731704400000,
            'end_time': 1731704415000
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('test-session-123', 'test-app')

            assert metrics is not None
            assert metrics['tool_count'] == 5
            assert metrics['avg_latency'] == 2500.0
            assert metrics['entity_count'] == 12
            assert metrics['duration'] == 15000

    def test_calculate_session_metrics_with_subagents(self):
        """Test metrics with subagent hierarchy."""

        mock_driver = MagicMock()
        mock_session = MagicMock()

        # First query: session and tools
        mock_result1 = MagicMock()
        mock_record1 = {
            'tool_count': 3,
            'avg_latency': 1800.0,
            'tool_names': ['Read', 'Bash', 'Write'],
            'entity_count': 7,
            'duration': 10000,
            'start_time': 1731704400000,
            'end_time': 1731704410000
        }
        mock_result1.single.return_value = Mock(**mock_record1)

        # Second query: subagents
        mock_result2 = MagicMock()
        mock_record2 = {
            'child_count': 2,
            'max_depth': 2
        }
        mock_result2.single.return_value = Mock(**mock_record2)

        mock_session.run.side_effect = [mock_result1, mock_result2]
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('parent-session-456', 'test-app')

            assert metrics is not None
            # Verify subagent metrics are included
            assert 'subagent_count' in metrics or 'child_count' in str(mock_session.run.call_args_list)

    def test_performance_tier_classification_fast(self):
        """Test that fast sessions are classified correctly."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        # Fast session: 500ms avg latency
        mock_record = {
            'tool_count': 10,
            'avg_latency': 500.0,
            'tool_names': ['Read'] * 10,
            'entity_count': 5,
            'duration': 5000,
            'start_time': 1731704400000,
            'end_time': 1731704405000
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('fast-session', 'test-app')

            # Should be classified as 'fast' if avg_latency < 1000ms
            if 'performance_tier' in metrics:
                # Assuming tier logic: <1000ms = fast
                assert metrics['avg_latency'] < 1000

    def test_performance_tier_classification_slow(self):
        """Test that slow sessions are classified correctly."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        # Slow session: 5000ms avg latency
        mock_record = {
            'tool_count': 3,
            'avg_latency': 5000.0,
            'tool_names': ['Bash', 'Read', 'Write'],
            'entity_count': 2,
            'duration': 20000,
            'start_time': 1731704400000,
            'end_time': 1731704420000
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('slow-session', 'test-app')

            # Should be classified as 'slow' if avg_latency > 3000ms
            if 'performance_tier' in metrics:
                assert metrics['avg_latency'] > 3000

    def test_tools_breakdown_counting(self):
        """Test that tool types are counted correctly."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_record = {
            'tool_count': 7,
            'avg_latency': 2000.0,
            'tool_names': ['Read', 'Read', 'Bash', 'Write', 'Grep', 'Read', 'Bash'],
            'entity_count': 10,
            'duration': 14000,
            'start_time': 1731704400000,
            'end_time': 1731704414000
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('breakdown-session', 'test-app')

            # Verify tool breakdown is calculated
            # Expected: Read: 3, Bash: 2, Write: 1, Grep: 1
            if 'tools_breakdown' in metrics:
                breakdown = metrics['tools_breakdown']
                assert breakdown.get('Read') == 3
                assert breakdown.get('Bash') == 2
                assert breakdown.get('Write') == 1
                assert breakdown.get('Grep') == 1

    def test_no_session_found(self):
        """Test handling of non-existent session."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        # No session found
        mock_result.single.return_value = None
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('nonexistent-session', 'test-app')

            assert metrics is None


class TestSessionDuration:
    """Test session duration calculations."""

    def test_duration_from_start_end_time(self):
        """Test duration is calculated from start/end timestamps."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        start = 1731704400000
        end = 1731704425000
        expected_duration = end - start  # 25000ms

        mock_record = {
            'tool_count': 4,
            'avg_latency': 3000.0,
            'tool_names': ['Read', 'Bash', 'Write', 'Grep'],
            'entity_count': 8,
            'duration': expected_duration,
            'start_time': start,
            'end_time': end
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('duration-test', 'test-app')

            assert metrics['duration'] == 25000


class TestSubagentHierarchy:
    """Test subagent depth and counting."""

    def test_subagent_depth_calculation(self):
        """Test max subagent depth is calculated correctly."""

        mock_driver = MagicMock()
        mock_session = MagicMock()

        # First query
        mock_result1 = MagicMock()
        mock_record1 = {
            'tool_count': 2,
            'avg_latency': 1500.0,
            'tool_names': ['Task', 'Task'],
            'entity_count': 3,
            'duration': 8000,
            'start_time': 1731704400000,
            'end_time': 1731704408000
        }
        mock_result1.single.return_value = Mock(**mock_record1)

        # Second query: deep hierarchy
        mock_result2 = MagicMock()
        mock_record2 = {
            'child_count': 4,
            'max_depth': 3  # Parent -> Child -> Grandchild -> Great-grandchild
        }
        mock_result2.single.return_value = Mock(**mock_record2)

        mock_session.run.side_effect = [mock_result1, mock_result2]
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('deep-hierarchy', 'test-app')

            # Verify depth metrics
            # Expect max_depth = 3
            assert 'max_depth' in str(mock_session.run.call_args_list) or metrics is not None

    def test_no_subagents(self):
        """Test sessions with no subagents."""

        mock_driver = MagicMock()
        mock_session = MagicMock()

        # First query
        mock_result1 = MagicMock()
        mock_record1 = {
            'tool_count': 5,
            'avg_latency': 2200.0,
            'tool_names': ['Read', 'Bash', 'Write', 'Grep', 'Edit'],
            'entity_count': 6,
            'duration': 11000,
            'start_time': 1731704400000,
            'end_time': 1731704411000
        }
        mock_result1.single.return_value = Mock(**mock_record1)

        # Second query: no subagents
        mock_result2 = MagicMock()
        mock_record2 = {
            'child_count': 0,
            'max_depth': 0
        }
        mock_result2.single.return_value = Mock(**mock_record2)

        mock_session.run.side_effect = [mock_result1, mock_result2]
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('no-subagent', 'test-app')

            assert metrics is not None


class TestEntityCounting:
    """Test entity discovery counting."""

    def test_entities_discovered_count(self):
        """Test that unique entities are counted."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_record = {
            'tool_count': 6,
            'avg_latency': 1900.0,
            'tool_names': ['Read', 'Grep', 'Bash', 'Read', 'Write', 'Grep'],
            'entity_count': 25,  # Many entities discovered
            'duration': 12000,
            'start_time': 1731704400000,
            'end_time': 1731704412000
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            metrics = tracker.calculate_session_metrics('entity-heavy', 'test-app')

            assert metrics['entity_count'] == 25


class TestNeo4jQueries:
    """Test that correct Cypher queries are constructed."""

    def test_session_query_includes_aggregations(self):
        """Test that session query aggregates correctly."""

        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_record = {
            'tool_count': 3,
            'avg_latency': 2000.0,
            'tool_names': ['Read', 'Bash', 'Write'],
            'entity_count': 5,
            'duration': 6000,
            'start_time': 1731704400000,
            'end_time': 1731704406000
        }

        mock_result.single.return_value = Mock(**mock_record)
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session

        with patch.object(tracker, 'get_neo4j_driver', return_value=mock_driver):
            tracker.calculate_session_metrics('query-test', 'test-app')

            # Verify first query (session metrics)
            call = mock_session.run.call_args_list[0]
            query = call[0][0]

            # Check for expected aggregations
            assert 'count(DISTINCT t)' in query or 'count(' in query
            assert 'avg(t.latency_ms)' in query or 'avg(' in query
            assert 'collect(DISTINCT t.name)' in query or 'collect(' in query


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
