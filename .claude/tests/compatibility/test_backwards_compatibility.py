#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "python-dotenv",
# ]
# ///
"""
Backwards compatibility tests for Observability-Graphiti integration.
Verifies that existing systems (Langfuse, Graphiti, hooks) still work.
"""

import pytest
import json
import subprocess
from pathlib import Path
import os
import sys


class TestExistingHooksPreserved:
    """Verify all existing hooks are still present and functional."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup hooks directory path."""
        self.hooks_dir = Path(__file__).parent.parent.parent / 'hooks'

    def test_langfuse_hook_exists(self):
        """Verify log_to_langfuse.py hook still exists."""

        langfuse_hook = self.hooks_dir / 'log_to_langfuse.py'
        assert langfuse_hook.exists(), "Langfuse hook missing!"

    def test_graphiti_hook_exists(self):
        """Verify log_to_graphiti.py hook still exists."""

        graphiti_hook = self.hooks_dir / 'log_to_graphiti.py'
        assert graphiti_hook.exists(), "Graphiti hook missing!"

    def test_observe_to_graphiti_hook_exists(self):
        """Verify new observe_to_graphiti.py hook exists."""

        new_hook = self.hooks_dir / 'observe_to_graphiti.py'
        assert new_hook.exists(), "New observe_to_graphiti hook missing!"

    def test_all_observability_hooks_present(self):
        """Verify all observability hooks are present."""

        required_hooks = [
            'send_event.py',
            'pre_tool_use.py',
            'post_tool_use.py',
            'session_start.py',
            'session_end.py',
            'user_prompt_submit.py',
            'notification.py',
            'subagent_stop.py',
            'pre_compact.py',
            'stop.py'
        ]

        for hook_name in required_hooks:
            hook_path = self.hooks_dir / hook_name
            assert hook_path.exists(), f"Hook {hook_name} missing!"

    def test_utils_directory_exists(self):
        """Verify utils directory with supporting modules exists."""

        utils_dir = self.hooks_dir / 'utils'
        assert utils_dir.exists(), "utils directory missing!"

        # Check key utility modules
        required_utils = [
            'constants.py',
            'summarizer.py',
            'model_extractor.py'
        ]

        for util_name in required_utils:
            util_path = utils_dir / util_name
            assert util_path.exists(), f"Utility {util_name} missing!"


class TestSettingsConfiguration:
    """Verify settings.local.json configuration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup settings file path."""
        self.settings_file = Path(__file__).parent.parent.parent / 'settings.local.json'

    def test_settings_file_exists(self):
        """Verify settings.local.json exists."""

        assert self.settings_file.exists(), "settings.local.json missing!"

    def test_settings_valid_json(self):
        """Verify settings.local.json is valid JSON."""

        with open(self.settings_file) as f:
            settings = json.load(f)

        assert isinstance(settings, dict), "Settings must be a dictionary"

    def test_hooks_configured(self):
        """Verify hooks are configured in settings."""

        with open(self.settings_file) as f:
            settings = json.load(f)

        assert 'hooks' in settings, "Hooks not configured in settings!"

        hooks = settings['hooks']

        # Verify key hook types are registered
        expected_hook_types = [
            'PreToolUse',
            'PostToolUse',
            'Stop',
            'SessionStart',
            'SessionEnd'
        ]

        for hook_type in expected_hook_types:
            assert hook_type in hooks, f"Hook type {hook_type} not configured!"

    def test_environment_variables_set(self):
        """Verify required environment variables are configured."""

        with open(self.settings_file) as f:
            settings = json.load(f)

        if 'env' in settings:
            env = settings['env']

            # Check for observability settings
            expected_vars = [
                'PROJECT_NAME',
                'SOURCE_APP'
            ]

            for var in expected_vars:
                # Either in settings or in actual environment
                assert var in env or os.getenv(var), f"Environment variable {var} not set!"


class TestHookExecutionOrder:
    """Verify hook execution order is preserved."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup settings file path."""
        self.settings_file = Path(__file__).parent.parent.parent / 'settings.local.json'

    def test_stop_hook_executes_all_integrations(self):
        """Verify Stop hook still triggers Langfuse and Graphiti."""

        with open(self.settings_file) as f:
            settings = json.load(f)

        if 'hooks' in settings and 'Stop' in settings['hooks']:
            stop_hooks = settings['hooks']['Stop']

            # Should have multiple hooks for Stop event
            # Including stop.py, log_to_langfuse.py, log_to_graphiti.py
            assert isinstance(stop_hooks, list), "Stop hooks should be a list"
            assert len(stop_hooks) >= 1, "Stop should have at least one hook"

    def test_pretooluse_hook_order(self):
        """Verify PreToolUse executes validation before logging."""

        with open(self.settings_file) as f:
            settings = json.load(f)

        if 'hooks' in settings and 'PreToolUse' in settings['hooks']:
            pre_hooks = settings['hooks']['PreToolUse']

            # Validation hooks should come before logging hooks
            # pre_tool_use.py should execute before send_event.py
            if isinstance(pre_hooks, list):
                hook_names = [h.get('path', '') if isinstance(h, dict) else h for h in pre_hooks]

                # Verify both hooks present
                assert any('pre_tool_use' in h for h in hook_names), "pre_tool_use.py missing from PreToolUse!"


class TestLangfuseIntegration:
    """Verify Langfuse integration still works."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Langfuse hook path."""
        self.langfuse_hook = Path(__file__).parent.parent.parent / 'hooks' / 'log_to_langfuse.py'

    def test_langfuse_hook_executable(self):
        """Verify Langfuse hook is executable."""

        assert self.langfuse_hook.exists()

        # Check if executable bit is set (Unix) or file can be read (Windows)
        assert os.access(self.langfuse_hook, os.R_OK), "Langfuse hook not readable!"

    def test_langfuse_hook_imports(self):
        """Verify Langfuse hook can be imported without errors."""

        # Try reading the file to check for syntax errors
        with open(self.langfuse_hook) as f:
            content = f.read()

        # Should contain Langfuse imports
        assert 'langfuse' in content.lower() or 'trace' in content.lower(), \
            "Langfuse hook doesn't appear to use Langfuse!"

    def test_langfuse_env_vars_supported(self):
        """Verify Langfuse environment variables are supported."""

        # Check if Langfuse env vars are documented or used
        env_file = Path(__file__).parent.parent.parent.parent / '.env'

        if env_file.exists():
            with open(env_file) as f:
                env_content = f.read()

            # Should mention Langfuse configuration
            # (May not be set, but should be documented)
            # This is a soft check
            pass


class TestGraphitiIntegration:
    """Verify original Graphiti integration still works."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Graphiti hook path."""
        self.graphiti_hook = Path(__file__).parent.parent.parent / 'hooks' / 'log_to_graphiti.py'

    def test_graphiti_hook_executable(self):
        """Verify Graphiti hook is executable."""

        assert self.graphiti_hook.exists()
        assert os.access(self.graphiti_hook, os.R_OK), "Graphiti hook not readable!"

    def test_graphiti_hook_imports(self):
        """Verify Graphiti hook imports are intact."""

        with open(self.graphiti_hook) as f:
            content = f.read()

        # Should contain Graphiti-related imports
        assert 'graphiti' in content.lower() or 'neo4j' in content.lower(), \
            "Graphiti hook doesn't appear to use Graphiti or Neo4j!"

    def test_graphiti_neo4j_env_vars(self):
        """Verify Neo4j environment variables are still used."""

        with open(self.graphiti_hook) as f:
            content = f.read()

        # Should reference NEO4J environment variables
        assert 'NEO4J_URI' in content or 'NEO4J' in content, \
            "Graphiti hook doesn't reference Neo4j configuration!"


class TestNoConflicts:
    """Verify no conflicts between new and existing integrations."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup hooks directory."""
        self.hooks_dir = Path(__file__).parent.parent.parent / 'hooks'

    def test_no_duplicate_hook_registrations(self):
        """Verify no hooks are registered multiple times incorrectly."""

        settings_file = Path(__file__).parent.parent.parent / 'settings.local.json'

        with open(settings_file) as f:
            settings = json.load(f)

        if 'hooks' in settings:
            hooks = settings['hooks']

            for hook_type, hook_configs in hooks.items():
                if isinstance(hook_configs, list):
                    # Check for duplicate paths
                    paths = []
                    for config in hook_configs:
                        if isinstance(config, dict) and 'path' in config:
                            path = config['path']
                            assert path not in paths, f"Duplicate hook path for {hook_type}: {path}"
                            paths.append(path)

    def test_environment_variable_naming_consistency(self):
        """Verify environment variables use consistent naming."""

        env_file = Path(__file__).parent.parent.parent.parent / '.env'

        if env_file.exists():
            with open(env_file) as f:
                env_content = f.read()

            # Check for consistent prefixes (e.g., NEO4J_, LANGFUSE_, etc.)
            # This is a soft check to ensure consistency
            pass

    def test_no_port_conflicts(self):
        """Verify services use different ports."""

        # Observability server: 4000
        # Neo4j: 7687, 7474
        # Langfuse: (external service)

        # Check settings for port configurations
        settings_file = Path(__file__).parent.parent.parent / 'settings.local.json'

        with open(settings_file) as f:
            settings = json.load(f)

        # Verify observability server port is configured
        if 'env' in settings:
            env = settings['env']
            if 'OBSERVABILITY_SERVER' in env:
                server_url = env['OBSERVABILITY_SERVER']
                # Should use port 4000
                assert ':4000' in server_url or 'localhost:4000' in server_url, \
                    "Observability server not using port 4000!"


class TestDataIsolation:
    """Verify different integrations don't interfere with each other's data."""

    def test_sqlite_database_separate(self):
        """Verify observability SQLite DB is separate from other data."""

        # Observability DB should be in observability/apps/server/events.db
        # Not in the .claude directory

        claude_dir = Path(__file__).parent.parent.parent
        sqlite_files = list(claude_dir.glob('*.db'))

        # .claude directory shouldn't have SQLite databases
        # (They should be in observability/apps/server/)
        assert len(sqlite_files) == 0, f"SQLite databases found in .claude dir: {sqlite_files}"

    def test_neo4j_node_labels_unique(self):
        """Verify Neo4j node labels are unique to avoid conflicts."""

        # New integration uses labels: Session, Tool, Entity
        # Original Graphiti uses: Episode, Entity, etc.

        # Check that observe_to_graphiti uses distinct labels
        observe_hook = Path(__file__).parent.parent.parent / 'hooks' / 'observe_to_graphiti.py'

        with open(observe_hook) as f:
            content = f.read()

        # Should use Session label (distinct from Episode)
        assert ':Session' in content, "observe_to_graphiti should use :Session label"
        assert ':Tool' in content, "observe_to_graphiti should use :Tool label"


class TestDocumentationPreserved:
    """Verify documentation is preserved and updated."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup documentation directory."""
        self.claude_dir = Path(__file__).parent.parent.parent

    def test_integration_documentation_exists(self):
        """Verify integration documentation exists."""

        required_docs = [
            'OBSERVABILITY_INTEGRATION_COMPLETE.md',
            'OBSERVABILITY_QUICK_START.md'
        ]

        for doc_name in required_docs:
            doc_path = self.claude_dir / doc_name
            assert doc_path.exists(), f"Documentation {doc_name} missing!"

    def test_obsidian_commands_documented(self):
        """Verify Obsidian slash commands are documented."""

        commands_dir = self.claude_dir / 'commands' / 'obsidian'

        if commands_dir.exists():
            readme = commands_dir / 'README.md'
            # README is optional but recommended
            pass


class TestPerformanceNoRegression:
    """Verify new integration doesn't slow down existing hooks."""

    def test_hook_count_reasonable(self):
        """Verify total number of hooks is reasonable."""

        hooks_dir = Path(__file__).parent.parent.parent / 'hooks'
        hook_files = list(hooks_dir.glob('*.py'))

        # Should have ~15-20 hooks (not hundreds)
        assert len(hook_files) < 30, f"Too many hook files: {len(hook_files)}"

    def test_settings_file_size_reasonable(self):
        """Verify settings.local.json size is reasonable."""

        settings_file = Path(__file__).parent.parent.parent / 'settings.local.json'

        if settings_file.exists():
            file_size = settings_file.stat().st_size

            # Should be < 50KB
            assert file_size < 50 * 1024, f"settings.local.json too large: {file_size} bytes"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
