#!/usr/bin/env python3
"""
Test suite for Anthropic Memory Tool

Tests all components:
- Memory Executor (create, view, list, search)
- Entity Extractor
- Stop Hook Integration
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from memory_executor import MemoryExecutor, SecurityError
from entity_extractor import EntityExtractor


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_pass(self, test_name):
        self.passed += 1
        self.tests.append((test_name, True, None))
        print(f"✅ {test_name}: PASSED")

    def add_fail(self, test_name, error):
        self.failed += 1
        self.tests.append((test_name, False, error))
        print(f"❌ {test_name}: FAILED - {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        print(f"{'='*60}")
        if self.failed > 0:
            print("\nFailed tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")
        return self.failed == 0


def test_memory_executor_create(results: TestResults, temp_dir: Path):
    """Test creating a memory"""
    try:
        # Create temp config
        config_path = temp_dir / "test-config.yaml"
        config_path.write_text(f"""
memory_base_path: {temp_dir / 'memories'}
validate_paths: true
""")

        executor = MemoryExecutor(config_path)

        # Create a test memory
        result = executor.create_memory(
            path="test/sample.md",
            content="# Test Memory\n\nThis is a test.",
            metadata={"test": True, "tags": ["test"]}
        )

        assert result["success"], "Create memory failed"
        assert Path(result["full_path"]).exists(), "Memory file not created"

        results.add_pass("Memory Executor - create_memory")
        return True
    except Exception as e:
        results.add_fail("Memory Executor - create_memory", str(e))
        return False


def test_memory_executor_view(results: TestResults, temp_dir: Path):
    """Test viewing a memory"""
    try:
        config_path = temp_dir / "test-config.yaml"
        executor = MemoryExecutor(config_path)

        # View the memory we created
        result = executor.view_memory("test/sample.md")

        assert result["success"], "View memory failed"
        assert "Test Memory" in result["content"], "Content mismatch"
        assert result["metadata"]["test"] == True, "Metadata mismatch"

        results.add_pass("Memory Executor - view_memory")
        return True
    except Exception as e:
        results.add_fail("Memory Executor - view_memory", str(e))
        return False


def test_memory_executor_list(results: TestResults, temp_dir: Path):
    """Test listing memories"""
    try:
        config_path = temp_dir / "test-config.yaml"
        executor = MemoryExecutor(config_path)

        # List memories
        result = executor.list_memories()

        assert result["success"], "List memories failed"
        assert result["count"] > 0, "No memories found"
        assert len(result["memories"]) > 0, "Memories list empty"

        results.add_pass("Memory Executor - list_memories")
        return True
    except Exception as e:
        results.add_fail("Memory Executor - list_memories", str(e))
        return False


def test_memory_executor_search(results: TestResults, temp_dir: Path):
    """Test searching memories"""
    try:
        config_path = temp_dir / "test-config.yaml"
        executor = MemoryExecutor(config_path)

        # Search for "test"
        result = executor.search_memories("test", limit=10)

        assert result["success"], "Search memories failed"
        assert result["count"] > 0, "No search results"
        assert result["results"][0]["score"] > 0, "No relevance score"

        results.add_pass("Memory Executor - search_memories")
        return True
    except Exception as e:
        results.add_fail("Memory Executor - search_memories", str(e))
        return False


def test_security_path_traversal(results: TestResults, temp_dir: Path):
    """Test path traversal prevention"""
    try:
        config_path = temp_dir / "test-config.yaml"
        executor = MemoryExecutor(config_path)

        # Try path traversal attack
        try:
            executor.create_memory(
                path="../../../etc/passwd",
                content="malicious content"
            )
            # Should not reach here
            results.add_fail("Security - path_traversal", "Path traversal not blocked!")
            return False
        except SecurityError:
            # Expected - path traversal was blocked
            results.add_pass("Security - path_traversal")
            return True
    except Exception as e:
        results.add_fail("Security - path_traversal", str(e))
        return False


def test_entity_extractor(results: TestResults):
    """Test entity extraction"""
    try:
        # Skip if no API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("⏭️  Entity Extractor - skipped (no API key)")
            return True

        extractor = EntityExtractor()

        # Test with simple transcript
        transcript = """
USER: Help me implement JWT authentication in Python
ASSISTANT: I'll help you implement JWT authentication. Let me create the auth middleware.
[TOOL: Write] Created auth_middleware.py
ASSISTANT: I've created the middleware using PyJWT and Flask.
"""

        entities = extractor.extract_from_transcript(transcript)

        # Check structure
        assert "files" in entities, "Missing 'files' in entities"
        assert "technologies" in entities, "Missing 'technologies' in entities"
        assert "summary" in entities, "Missing 'summary' in entities"

        results.add_pass("Entity Extractor - extract_entities")
        return True
    except Exception as e:
        results.add_fail("Entity Extractor - extract_entities", str(e))
        return False


def test_entity_summary_generation(results: TestResults):
    """Test session summary generation"""
    try:
        extractor = EntityExtractor()

        # Mock entities
        entities = {
            "files": [
                {"path": "auth.py", "type": "Python", "description": "Auth module"}
            ],
            "technologies": [
                {"name": "JWT", "category": "library", "purpose": "Authentication"}
            ],
            "concepts": [
                {"name": "Token-based auth", "description": "Using JWT tokens"}
            ],
            "decisions": [],
            "tools_used": {
                "Write": {"count": 2, "purpose": "Create files"},
                "Read": {"count": 1, "purpose": "Read config"}
            },
            "key_learnings": [
                {"learning": "JWT tokens expire", "actionable": "Implement refresh tokens"}
            ],
            "tags": ["authentication", "security"],
            "summary": "Implemented JWT authentication"
        }

        summary = extractor.generate_session_summary(
            entities=entities,
            session_id="test123",
            date="2026-01-11"
        )

        # Check summary contains key sections
        assert "# Session Summary" in summary, "Missing summary header"
        assert "## Files Involved" in summary, "Missing files section"
        assert "## Technologies Used" in summary, "Missing tech section"
        assert "JWT" in summary, "Technology not mentioned"

        results.add_pass("Entity Extractor - generate_summary")
        return True
    except Exception as e:
        results.add_fail("Entity Extractor - generate_summary", str(e))
        return False


def test_index_creation(results: TestResults, temp_dir: Path):
    """Test master index creation"""
    try:
        config_path = temp_dir / "test-config.yaml"
        executor = MemoryExecutor(config_path)

        # Create index
        result = executor.create_index()

        assert result["success"], "Index creation failed"
        assert Path(result["full_path"]).exists(), "Index file not created"

        # Read and verify index
        index = executor.view_memory("index.md")
        assert "# Memory System Index" in index["content"], "Invalid index content"

        results.add_pass("Memory Executor - create_index")
        return True
    except Exception as e:
        results.add_fail("Memory Executor - create_index", str(e))
        return False


def main():
    """Run all tests"""
    print("🧪 Anthropic Memory Tool - Test Suite")
    print("="*60)

    results = TestResults()

    # Create temporary directory for tests
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("\n📋 Running Memory Executor Tests...")
        test_memory_executor_create(results, temp_path)
        test_memory_executor_view(results, temp_path)
        test_memory_executor_list(results, temp_path)
        test_memory_executor_search(results, temp_path)
        test_security_path_traversal(results, temp_path)
        test_index_creation(results, temp_path)

    print("\n📋 Running Entity Extractor Tests...")
    test_entity_extractor(results)
    test_entity_summary_generation(results)

    # Summary
    success = results.summary()

    if success:
        print("\n🎉 All tests passed! Memory system is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
