#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "neo4j",
#     "python-dotenv",
# ]
# ///
"""
Integration test script for Observability-Graphiti-Obsidian integration.
Tests all three components and verifies output.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")


def test_neo4j_connection():
    """Test Neo4j connection."""
    print_header("Testing Neo4j Connection")

    try:
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record['test'] == 1:
                print_success(f"Connected to Neo4j at {uri}")
                driver.close()
                return True
            else:
                print_error("Neo4j connection failed")
                return False

    except Exception as e:
        print_error(f"Neo4j connection failed: {e}")
        return False


def test_observability_db():
    """Test observability database exists."""
    print_header("Testing Observability Database")

    db_path = Path(__file__).parent.parent.parent / 'observability' / 'apps' / 'server' / 'events.db'

    if db_path.exists():
        print_success(f"Observability database found at {db_path}")

        # Try to query it
        import sqlite3
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            count = cursor.fetchone()[0]
            conn.close()
            print_success(f"Database has {count} events")
            return True
        except Exception as e:
            print_warning(f"Database exists but query failed: {e}")
            return True  # Database exists, even if empty

    else:
        print_warning(f"Observability database not found at {db_path}")
        print_warning("This is OK if observability server hasn't run yet")
        return False


def test_script(script_name: str, script_path: Path) -> bool:
    """Test a script by running it with mock data."""
    print_header(f"Testing {script_name}")

    # Create mock hook data
    test_data = {
        "session_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "hook_event_name": "Stop",
        "payload": {
            "source_app": "test-integration"
        },
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

    try:
        # Run script with test data
        result = subprocess.run(
            ['uv', 'run', str(script_path)],
            input=json.dumps(test_data),
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check output
        if result.returncode == 0:
            print_success(f"{script_name} executed successfully")

            # Print stderr (where our scripts print status)
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        print(f"  {line}")

            return True
        else:
            print_error(f"{script_name} failed with return code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print_error(f"{script_name} timed out")
        return False
    except Exception as e:
        print_error(f"{script_name} failed: {e}")
        return False


def verify_neo4j_data():
    """Verify that test data was created in Neo4j."""
    print_header("Verifying Neo4j Data")

    try:
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            # Count test sessions
            result = session.run("""
                MATCH (s:Session)
                WHERE s.source_app = 'test-integration'
                RETURN count(s) as count
            """)

            record = result.single()
            count = record['count'] if record else 0

            if count > 0:
                print_success(f"Found {count} test session(s) in Neo4j")

                # Get latest session details
                result = session.run("""
                    MATCH (s:Session)
                    WHERE s.source_app = 'test-integration'
                    RETURN s.id as id, s.total_tools as tools, s.performance_tier as tier
                    ORDER BY s.start_time DESC
                    LIMIT 1
                """)

                record = result.single()
                if record:
                    print(f"  Latest session: {record['id'][:16]}...")
                    print(f"  Tools: {record['tools']}, Tier: {record['tier']}")

                driver.close()
                return True
            else:
                print_warning("No test sessions found in Neo4j")
                print_warning("This is OK if this is the first test run")
                driver.close()
                return False

    except Exception as e:
        print_error(f"Failed to verify Neo4j data: {e}")
        return False


def verify_obsidian_notes():
    """Verify that test notes were created in Obsidian vault."""
    print_header("Verifying Obsidian Notes")

    vault_path = Path(os.getenv("OBSIDIAN_VAULT_PATH", "./observability/notes"))
    sessions_dir = vault_path / 'sessions'

    if not sessions_dir.exists():
        print_warning(f"Sessions directory not found at {sessions_dir}")
        print_warning("This is OK if this is the first test run")
        return False

    # Find test session notes
    test_notes = list(sessions_dir.glob("test-integration_*.md"))

    if test_notes:
        print_success(f"Found {len(test_notes)} test session note(s)")

        # Read latest note
        latest_note = max(test_notes, key=lambda p: p.stat().st_mtime)
        print(f"  Latest note: {latest_note.name}")

        # Show first few lines
        content = latest_note.read_text(encoding='utf-8')
        lines = content.split('\n')[:10]
        print("\n  Preview:")
        for line in lines[:5]:
            print(f"    {line}")

        return True
    else:
        print_warning("No test session notes found")
        print_warning("This is OK if this is the first test run")
        return False


def cleanup_test_data():
    """Optionally clean up test data."""
    print_header("Cleanup")

    print("Test data will remain in Neo4j and Obsidian for inspection.")
    print("To clean up manually:")
    print("\n  Neo4j:")
    print("    MATCH (s:Session {source_app: 'test-integration'}) DETACH DELETE s")
    print("\n  Obsidian:")
    vault_path = Path(os.getenv("OBSIDIAN_VAULT_PATH", "./observability/notes"))
    print(f"    rm {vault_path}/sessions/test-integration_*.md")


def main():
    """Run all tests."""
    print_header("Observability-Graphiti-Obsidian Integration Test")

    results = {}

    # Test prerequisites
    results['neo4j'] = test_neo4j_connection()
    results['observability_db'] = test_observability_db()

    # Test scripts
    base_dir = Path(__file__).parent.parent

    results['observe_to_graphiti'] = test_script(
        "observe_to_graphiti.py",
        base_dir / 'hooks' / 'observe_to_graphiti.py'
    )

    results['agent_progress_tracker'] = test_script(
        "agent_progress_tracker.py",
        base_dir / 'scripts' / 'agent_progress_tracker.py'
    )

    results['obsidian_exporter'] = test_script(
        "obsidian_exporter.py",
        base_dir / 'scripts' / 'obsidian_exporter.py'
    )

    # Verify outputs
    results['neo4j_data'] = verify_neo4j_data()
    results['obsidian_notes'] = verify_obsidian_notes()

    # Summary
    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}\n")

    for test_name, result in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {test_name:30} {status}")

    cleanup_test_data()

    # Exit code
    if passed == total:
        print(f"\n{GREEN}All tests passed!{RESET}\n")
        return 0
    else:
        print(f"\n{YELLOW}Some tests failed or skipped{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
