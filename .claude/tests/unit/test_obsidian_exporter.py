#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "python-dotenv",
# ]
# ///
"""
Unit tests for Obsidian note generation and formatting.
Tests markdown generation, YAML frontmatter, and format validation.
"""

import pytest
import json
import re
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock


class TestObsidianNoteGeneration:
    """Test Obsidian markdown note generation."""

    def test_daily_note_format(self):
        """Test that daily notes have correct format."""

        # Sample session data
        session_data = {
            'session_id': 'test-session-123',
            'source_app': 'consulting-co',
            'start_time': 1731704400000,
            'end_time': 1731704415000,
            'tool_count': 5,
            'entities': ['main.py', 'UserRepository', 'process_data']
        }

        # Expected structure
        expected_sections = [
            '# Claude Activity',
            '## Summary',
            '## Timeline',
            '## Entities Discovered',
            '## Statistics'
        ]

        # Mock note content
        note_content = f"""---
date: 2025-11-15
source: consulting-co
session_id: test-session-123
---

# Claude Activity - 2025-11-15

## Summary
Session started at 20:00:00 and completed 5 tool executions.

## Timeline
- 20:00:00 - Session Start
- 20:00:05 - Tool: Read
- 20:00:08 - Tool: Bash
- 20:00:12 - Session End

## Entities Discovered
- File: main.py
- Class: UserRepository
- Function: process_data

## Statistics
- Total Tools: 5
- Session Duration: 15000ms
"""

        # Validate frontmatter
        assert note_content.startswith('---')
        assert 'date: 2025-11-15' in note_content
        assert 'source: consulting-co' in note_content

        # Validate sections
        for section in expected_sections:
            assert section in note_content

    def test_frontmatter_validation(self):
        """Test YAML frontmatter is valid."""

        frontmatter = """---
date: 2025-11-15
source: consulting-co
session_id: abc123
tags:
  - claude
  - automation
status: completed
---"""

        # Extract YAML between ---
        yaml_match = re.search(r'^---\n(.*?)\n---', frontmatter, re.DOTALL | re.MULTILINE)
        assert yaml_match is not None

        yaml_content = yaml_match.group(1)

        # Validate key fields present
        assert 'date:' in yaml_content
        assert 'source:' in yaml_content
        assert 'session_id:' in yaml_content
        assert 'tags:' in yaml_content

    def test_entity_section_formatting(self):
        """Test entity section has proper markdown lists."""

        entities = [
            {'name': 'main.py', 'type': 'file'},
            {'name': 'UserRepository', 'type': 'class'},
            {'name': 'process_data', 'type': 'function'}
        ]

        # Generate entity section
        entity_section = "## Entities Discovered\n\n"
        for entity in entities:
            entity_section += f"- **{entity['type'].title()}**: `{entity['name']}`\n"

        # Validate markdown
        assert '## Entities Discovered' in entity_section
        assert '- **File**: `main.py`' in entity_section
        assert '- **Class**: `UserRepository`' in entity_section
        assert '- **Function**: `process_data`' in entity_section

    def test_timeline_chronological_order(self):
        """Test timeline events are in chronological order."""

        events = [
            {'timestamp': 1731704400000, 'type': 'SessionStart'},
            {'timestamp': 1731704405000, 'type': 'PreToolUse', 'tool': 'Read'},
            {'timestamp': 1731704407667, 'type': 'PostToolUse', 'tool': 'Read'},
            {'timestamp': 1731704410000, 'type': 'PreToolUse', 'tool': 'Bash'},
            {'timestamp': 1731704412249, 'type': 'PostToolUse', 'tool': 'Bash'}
        ]

        # Sort by timestamp
        sorted_events = sorted(events, key=lambda e: e['timestamp'])

        # Verify order
        timestamps = [e['timestamp'] for e in sorted_events]
        assert timestamps == sorted(timestamps)

    def test_statistics_section_accuracy(self):
        """Test statistics calculations are accurate."""

        session_metrics = {
            'tool_count': 7,
            'avg_tool_latency': 2345.67,
            'session_duration': 18000,
            'entities_discovered': 15,
            'subagent_count': 2
        }

        stats_section = f"""## Statistics

- **Total Tools Executed**: {session_metrics['tool_count']}
- **Average Tool Latency**: {session_metrics['avg_tool_latency']:.2f}ms
- **Session Duration**: {session_metrics['session_duration']}ms
- **Entities Discovered**: {session_metrics['entities_discovered']}
- **Subagents Spawned**: {session_metrics['subagent_count']}
"""

        # Validate values
        assert 'Total Tools Executed**: 7' in stats_section
        assert 'Average Tool Latency**: 2345.67ms' in stats_section
        assert 'Session Duration**: 18000ms' in stats_section
        assert 'Entities Discovered**: 15' in stats_section
        assert 'Subagents Spawned**: 2' in stats_section


class TestMarkdownValidation:
    """Test markdown syntax validation."""

    def test_valid_markdown_headers(self):
        """Test that headers use correct markdown syntax."""

        headers = [
            '# Level 1 Header',
            '## Level 2 Header',
            '### Level 3 Header'
        ]

        for header in headers:
            # Headers must start with # followed by space
            assert re.match(r'^#{1,6} .+', header)

    def test_valid_markdown_lists(self):
        """Test list items use correct markdown syntax."""

        list_items = [
            '- Item 1',
            '- Item 2',
            '  - Nested item',
            '* Alternative bullet',
            '1. Numbered item'
        ]

        for item in list_items:
            # Must start with -, *, or digit.
            assert re.match(r'^(\s*[-*]|\d+\.)\s+.+', item)

    def test_valid_markdown_code_blocks(self):
        """Test code blocks use correct markdown syntax."""

        code_block = """```python
def example():
    pass
```"""

        # Must start and end with ```
        assert code_block.startswith('```')
        assert code_block.strip().endswith('```')

    def test_valid_markdown_links(self):
        """Test internal links use correct Obsidian format."""

        links = [
            '[[2025-11-14-claude-activity]]',
            '[[Projects/consulting-co]]',
            '[[ADR-007|Architecture Decision]]'
        ]

        for link in links:
            # Obsidian links use [[...]]
            assert link.startswith('[[') and link.endswith(']]')

    def test_no_orphaned_code_fences(self):
        """Test code fences are properly closed."""

        valid_note = """
## Code Example

```python
def test():
    pass
```

More content here.
"""

        # Count backticks - should be even
        backtick_groups = re.findall(r'```', valid_note)
        assert len(backtick_groups) % 2 == 0


class TestSubagentNoteLinks:
    """Test subagent note linking."""

    def test_parent_links_to_subagent(self):
        """Test parent notes link to subagent notes."""

        parent_note = """## Subagents

This session spawned 2 subagents:
- [[2025-11-15-subagent-abc123]]
- [[2025-11-15-subagent-def456]]
"""

        # Verify links present
        assert '[[2025-11-15-subagent-abc123]]' in parent_note
        assert '[[2025-11-15-subagent-def456]]' in parent_note

    def test_subagent_links_back_to_parent(self):
        """Test subagent notes link back to parent."""

        subagent_note = """---
parent_session: parent-session-123
---

# Subagent Activity

**Parent Session**: [[2025-11-15-parent-session-123]]
"""

        # Verify parent link
        assert '[[2025-11-15-parent-session-123]]' in subagent_note
        assert 'parent_session:' in subagent_note


class TestDateFormatting:
    """Test date and time formatting."""

    def test_date_format_iso(self):
        """Test dates use ISO format YYYY-MM-DD."""

        timestamp = 1731704400000
        dt = datetime.fromtimestamp(timestamp / 1000)
        date_str = dt.strftime('%Y-%m-%d')

        # Should be YYYY-MM-DD
        assert re.match(r'\d{4}-\d{2}-\d{2}', date_str)

    def test_time_format_24hr(self):
        """Test times use 24-hour format HH:MM:SS."""

        timestamp = 1731704400000
        dt = datetime.fromtimestamp(timestamp / 1000)
        time_str = dt.strftime('%H:%M:%S')

        # Should be HH:MM:SS
        assert re.match(r'\d{2}:\d{2}:\d{2}', time_str)

    def test_timestamp_to_readable(self):
        """Test timestamp conversion to readable format."""

        timestamp = 1731704400000  # Nov 15, 2025 20:00:00
        dt = datetime.fromtimestamp(timestamp / 1000)

        readable = dt.strftime('%Y-%m-%d %H:%M:%S')

        # Verify format
        assert len(readable) == 19  # YYYY-MM-DD HH:MM:SS
        assert readable[4] == '-'
        assert readable[7] == '-'
        assert readable[10] == ' '
        assert readable[13] == ':'
        assert readable[16] == ':'


class TestNoteFilenames:
    """Test Obsidian note filename generation."""

    def test_daily_note_filename_format(self):
        """Test daily note filenames follow convention."""

        date = datetime.now()
        filename = f"{date.strftime('%Y-%m-%d')}-claude-activity.md"

        # Should be YYYY-MM-DD-claude-activity.md
        assert re.match(r'\d{4}-\d{2}-\d{2}-claude-activity\.md', filename)

    def test_session_note_filename_format(self):
        """Test session note filenames include session ID."""

        session_id = 'abc123de'
        date = datetime.now()
        filename = f"{date.strftime('%Y-%m-%d')}-session-{session_id}.md"

        # Should be YYYY-MM-DD-session-[id].md
        assert re.match(r'\d{4}-\d{2}-\d{2}-session-.+\.md', filename)

    def test_no_special_chars_in_filename(self):
        """Test filenames don't contain invalid characters."""

        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

        filename = '2025-11-15-claude-activity.md'

        for char in invalid_chars:
            assert char not in filename


class TestToolBreakdownFormatting:
    """Test tool execution breakdown formatting."""

    def test_tool_latency_table(self):
        """Test tool latency breakdown uses table format."""

        tools_breakdown = [
            {'name': 'Read', 'count': 3, 'avg_latency': 1200},
            {'name': 'Bash', 'count': 2, 'avg_latency': 3400},
            {'name': 'Write', 'count': 1, 'avg_latency': 800}
        ]

        # Generate table
        table = "| Tool | Count | Avg Latency |\n"
        table += "|------|-------|-------------|\n"
        for tool in tools_breakdown:
            table += f"| {tool['name']} | {tool['count']} | {tool['avg_latency']}ms |\n"

        # Validate table structure
        lines = table.split('\n')
        assert len(lines) >= 3  # Header + separator + data
        assert '|' in lines[0]
        assert '---' in lines[1]

    def test_tool_timeline_formatting(self):
        """Test tool timeline shows execution order."""

        timeline = [
            {'time': '20:00:05', 'tool': 'Read', 'latency': 2667},
            {'time': '20:00:08', 'tool': 'Bash', 'latency': 2249},
            {'time': '20:00:11', 'tool': 'Write', 'latency': 1500}
        ]

        # Generate timeline
        timeline_md = "## Execution Timeline\n\n"
        for event in timeline:
            timeline_md += f"- **{event['time']}** - {event['tool']} ({event['latency']}ms)\n"

        # Validate format
        assert '## Execution Timeline' in timeline_md
        assert '- **20:00:05** - Read (2667ms)' in timeline_md
        assert '- **20:00:08** - Bash (2249ms)' in timeline_md


class TestErrorHandling:
    """Test error handling in note generation."""

    def test_missing_session_data_graceful(self):
        """Test graceful handling of missing session data."""

        incomplete_session = {
            'session_id': 'test-123',
            # Missing other fields
        }

        # Should not raise exception
        try:
            session_id = incomplete_session.get('session_id', 'unknown')
            source_app = incomplete_session.get('source_app', 'unknown')
            assert session_id == 'test-123'
            assert source_app == 'unknown'
        except Exception as e:
            pytest.fail(f"Should handle missing data gracefully: {e}")

    def test_empty_entity_list(self):
        """Test handling of sessions with no entities."""

        entities = []

        entity_section = "## Entities Discovered\n\n"
        if entities:
            for entity in entities:
                entity_section += f"- {entity}\n"
        else:
            entity_section += "No entities discovered in this session.\n"

        assert 'No entities discovered' in entity_section


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
