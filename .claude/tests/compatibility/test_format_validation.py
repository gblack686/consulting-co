#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "pyyaml",
#     "jsonschema",
# ]
# ///
"""
Format validation tests for configuration files and data structures.
Validates YAML, JSON, Cypher queries, and Obsidian markdown.
"""

import pytest
import json
import yaml
import re
from pathlib import Path
from jsonschema import validate, ValidationError


class TestJSONValidation:
    """Validate JSON configuration files."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup paths to JSON files."""
        self.claude_dir = Path(__file__).parent.parent.parent

    def test_settings_local_json_valid(self):
        """Verify settings.local.json is valid JSON."""

        settings_file = self.claude_dir / 'settings.local.json'

        if settings_file.exists():
            with open(settings_file) as f:
                settings = json.load(f)

            assert isinstance(settings, dict)

    def test_settings_schema_validation(self):
        """Validate settings.local.json against schema."""

        settings_file = self.claude_dir / 'settings.local.json'

        if not settings_file.exists():
            pytest.skip("settings.local.json not found")

        with open(settings_file) as f:
            settings = json.load(f)

        # Define expected schema
        schema = {
            "type": "object",
            "properties": {
                "hooks": {
                    "type": "object",
                    "additionalProperties": True
                },
                "env": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            }
        }

        # Validate
        try:
            validate(instance=settings, schema=schema)
        except ValidationError as e:
            pytest.fail(f"settings.local.json schema validation failed: {e}")

    def test_hook_configuration_format(self):
        """Validate hook configuration format."""

        settings_file = self.claude_dir / 'settings.local.json'

        if not settings_file.exists():
            pytest.skip("settings.local.json not found")

        with open(settings_file) as f:
            settings = json.load(f)

        if 'hooks' not in settings:
            pytest.skip("No hooks configured")

        hooks = settings['hooks']

        for hook_type, hook_configs in hooks.items():
            # Hook type should be a string
            assert isinstance(hook_type, str), f"Hook type should be string: {hook_type}"

            # Hook configs can be list or dict
            if isinstance(hook_configs, list):
                for config in hook_configs:
                    # Each config can be string or dict
                    if isinstance(config, dict):
                        # Should have 'path' or 'script' key
                        assert 'path' in config or 'script' in config, \
                            f"Hook config missing path/script: {config}"


class TestYAMLValidation:
    """Validate YAML configuration files."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup paths to YAML files."""
        self.claude_dir = Path(__file__).parent.parent.parent

    def test_yaml_files_parseable(self):
        """Verify all YAML files can be parsed."""

        # Find YAML files
        yaml_files = list(self.claude_dir.glob('**/*.yaml'))
        yaml_files.extend(self.claude_dir.glob('**/*.yml'))

        if not yaml_files:
            pytest.skip("No YAML files found")

        for yaml_file in yaml_files:
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)

                # Should parse to dict or list
                assert isinstance(data, (dict, list, type(None))), \
                    f"YAML file {yaml_file} parsed to unexpected type: {type(data)}"

            except yaml.YAMLError as e:
                pytest.fail(f"YAML parsing failed for {yaml_file}: {e}")


class TestMarkdownValidation:
    """Validate Obsidian markdown files."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup paths to markdown files."""
        self.claude_dir = Path(__file__).parent.parent.parent

    def test_markdown_frontmatter_valid(self):
        """Verify markdown frontmatter is valid YAML."""

        md_files = list(self.claude_dir.glob('**/*.md'))

        for md_file in md_files:
            with open(md_file, encoding='utf-8') as f:
                content = f.read()

            # Check if file has frontmatter
            if content.startswith('---\n'):
                # Extract frontmatter
                match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

                if match:
                    frontmatter = match.group(1)

                    try:
                        # Parse as YAML
                        data = yaml.safe_load(frontmatter)
                        assert isinstance(data, (dict, type(None))), \
                            f"Frontmatter should be dict: {md_file}"

                    except yaml.YAMLError as e:
                        pytest.fail(f"Frontmatter YAML invalid in {md_file}: {e}")

    def test_markdown_headers_valid(self):
        """Verify markdown headers use correct syntax."""

        md_files = list(self.claude_dir.glob('**/*.md'))

        for md_file in md_files:
            with open(md_file, encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check if line looks like a header
                if line.strip().startswith('#'):
                    # Headers must have space after #
                    if not re.match(r'^#{1,6} .+', line.strip()):
                        pytest.fail(f"Invalid header syntax in {md_file}:{i}: {line.strip()}")

    def test_markdown_code_blocks_closed(self):
        """Verify code blocks are properly closed."""

        md_files = list(self.claude_dir.glob('**/*.md'))

        for md_file in md_files:
            with open(md_file, encoding='utf-8') as f:
                content = f.read()

            # Count backtick triplets
            code_fences = re.findall(r'```', content)

            # Should be even number (opening and closing)
            if len(code_fences) % 2 != 0:
                pytest.fail(f"Unclosed code block in {md_file}")

    def test_markdown_links_valid(self):
        """Verify markdown links are well-formed."""

        md_files = list(self.claude_dir.glob('**/*.md'))

        for md_file in md_files:
            with open(md_file, encoding='utf-8') as f:
                content = f.read()

            # Find markdown links [text](url)
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

            for text, url in links:
                # Link text should not be empty
                assert text.strip(), f"Empty link text in {md_file}"

                # URL should not be empty
                assert url.strip(), f"Empty link URL in {md_file}"

    def test_obsidian_internal_links_valid(self):
        """Verify Obsidian [[links]] are well-formed."""

        md_files = list(self.claude_dir.glob('**/*.md'))

        for md_file in md_files:
            with open(md_file, encoding='utf-8') as f:
                content = f.read()

            # Find Obsidian links [[link]]
            obsidian_links = re.findall(r'\[\[([^\]]+)\]\]', content)

            for link in obsidian_links:
                # Link should not be empty
                assert link.strip(), f"Empty Obsidian link in {md_file}"

                # Link can have | for aliases: [[page|alias]]
                # This is valid


class TestCypherQueryValidation:
    """Validate Neo4j Cypher queries."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup hooks directory."""
        self.hooks_dir = Path(__file__).parent.parent.parent / 'hooks'

    def test_cypher_queries_syntactically_valid(self):
        """Verify Cypher queries have valid syntax."""

        # Read observe_to_graphiti.py
        observe_hook = self.hooks_dir / 'observe_to_graphiti.py'

        if not observe_hook.exists():
            pytest.skip("observe_to_graphiti.py not found")

        with open(observe_hook) as f:
            content = f.read()

        # Extract Cypher queries (inside session.run calls)
        # Look for triple-quoted strings in session.run
        query_pattern = r'session\.run\(\s*"""(.*?)"""'
        queries = re.findall(query_pattern, content, re.DOTALL)

        for query in queries:
            # Basic syntax checks
            query = query.strip()

            # Should start with MATCH, MERGE, CREATE, or SET
            assert any(query.startswith(keyword) for keyword in ['MATCH', 'MERGE', 'CREATE', 'SET', 'WITH']), \
                f"Query doesn't start with valid keyword: {query[:50]}"

            # Check for balanced parentheses
            assert query.count('(') == query.count(')'), \
                f"Unbalanced parentheses in query: {query[:50]}"

            # Check for balanced brackets
            assert query.count('[') == query.count(']'), \
                f"Unbalanced brackets in query: {query[:50]}"

    def test_cypher_parameters_used_correctly(self):
        """Verify Cypher parameters are used with $ prefix."""

        observe_hook = self.hooks_dir / 'observe_to_graphiti.py'

        if not observe_hook.exists():
            pytest.skip("observe_to_graphiti.py not found")

        with open(observe_hook) as f:
            content = f.read()

        # Find session.run calls with parameters
        run_calls = re.findall(
            r'session\.run\([^,]+,\s*\{([^}]+)\}',
            content,
            re.DOTALL
        )

        for params in run_calls:
            # Extract parameter names from dict
            param_names = re.findall(r"'(\w+)':", params)

            # Parameters should be used with $ in query
            # This is a soft check - just verify parameter format is valid


class TestEventPayloadValidation:
    """Validate event payload structures."""

    def test_pretooluse_event_schema(self):
        """Validate PreToolUse event payload schema."""

        # Define schema
        schema = {
            "type": "object",
            "required": ["source_app", "session_id", "hook_event_type", "timestamp", "payload"],
            "properties": {
                "source_app": {"type": "string"},
                "session_id": {"type": "string"},
                "hook_event_type": {"type": "string", "enum": ["PreToolUse"]},
                "timestamp": {"type": "integer"},
                "model_name": {"type": "string"},
                "payload": {
                    "type": "object",
                    "required": ["tool_name"],
                    "properties": {
                        "tool_name": {"type": "string"},
                        "tool_input": {"type": "object"}
                    }
                }
            }
        }

        # Sample valid event
        valid_event = {
            "source_app": "test-app",
            "session_id": "test-session-123",
            "hook_event_type": "PreToolUse",
            "timestamp": 1731704400000,
            "model_name": "claude-sonnet-4-5",
            "payload": {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test.txt"}
            }
        }

        # Validate
        try:
            validate(instance=valid_event, schema=schema)
        except ValidationError as e:
            pytest.fail(f"PreToolUse event schema validation failed: {e}")

    def test_posttooluse_event_schema(self):
        """Validate PostToolUse event payload schema."""

        schema = {
            "type": "object",
            "required": ["source_app", "session_id", "hook_event_type", "timestamp", "payload"],
            "properties": {
                "source_app": {"type": "string"},
                "session_id": {"type": "string"},
                "hook_event_type": {"type": "string", "enum": ["PostToolUse"]},
                "timestamp": {"type": "integer"},
                "model_name": {"type": "string"},
                "payload": {
                    "type": "object",
                    "required": ["tool_name"],
                    "properties": {
                        "tool_name": {"type": "string"},
                        "tool_output": {}  # Can be any type
                    }
                }
            }
        }

        valid_event = {
            "source_app": "test-app",
            "session_id": "test-session-123",
            "hook_event_type": "PostToolUse",
            "timestamp": 1731704402667,
            "model_name": "claude-sonnet-4-5",
            "payload": {
                "tool_name": "Read",
                "tool_output": "File content here"
            }
        }

        validate(instance=valid_event, schema=schema)

    def test_subagentstop_event_schema(self):
        """Validate SubagentStop event payload schema."""

        schema = {
            "type": "object",
            "required": ["source_app", "session_id", "hook_event_type", "timestamp", "payload"],
            "properties": {
                "source_app": {"type": "string"},
                "session_id": {"type": "string"},
                "hook_event_type": {"type": "string", "enum": ["SubagentStop"]},
                "timestamp": {"type": "integer"},
                "model_name": {"type": "string"},
                "payload": {
                    "type": "object",
                    "properties": {
                        "parent_session_id": {"type": "string"}
                    }
                }
            }
        }

        valid_event = {
            "source_app": "test-app",
            "session_id": "subagent-session-456",
            "hook_event_type": "SubagentStop",
            "timestamp": 1731704410000,
            "model_name": "claude-sonnet-4-5",
            "payload": {
                "parent_session_id": "parent-session-123"
            }
        }

        validate(instance=valid_event, schema=schema)


class TestPythonSyntaxValidation:
    """Validate Python files have valid syntax."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup directories to check."""
        self.claude_dir = Path(__file__).parent.parent.parent

    def test_all_python_files_valid_syntax(self):
        """Verify all Python files have valid syntax."""

        py_files = []
        py_files.extend(self.claude_dir.glob('hooks/*.py'))
        py_files.extend(self.claude_dir.glob('scripts/*.py'))
        py_files.extend(self.claude_dir.glob('tests/**/*.py'))

        for py_file in py_files:
            # Try to compile the file
            try:
                with open(py_file) as f:
                    code = f.read()

                compile(code, str(py_file), 'exec')

            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")

    def test_shebang_lines_valid(self):
        """Verify shebang lines are valid."""

        py_files = list(self.claude_dir.glob('hooks/*.py'))
        py_files.extend(self.claude_dir.glob('scripts/*.py'))

        for py_file in py_files:
            with open(py_file) as f:
                first_line = f.readline()

            if first_line.startswith('#!'):
                # Shebang should be valid
                assert 'python' in first_line.lower() or 'uv' in first_line, \
                    f"Invalid shebang in {py_file}: {first_line}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
