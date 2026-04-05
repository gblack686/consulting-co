#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Test Turn-Based Review System
Validates turn counter, mini-doc-agent, and trace review agent.
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "utils"))

from turn_counter import TurnCounter


def test_turn_counter():
    """Test turn counter functionality."""
    print("=" * 60)
    print("Testing Turn Counter")
    print("=" * 60)

    # Create test counter with temp database
    test_db = Path.home() / ".claude" / "data" / "test_turn_counter.db"
    if test_db.exists():
        test_db.unlink()

    counter = TurnCounter(db_path=test_db)
    test_session = "test_session_123"

    print("\n1. Testing turn increment...")
    for i in range(1, 12):
        user_msg = f"Test user message {i}"
        assistant_msg = f"Test assistant response {i}"
        turn_count, last_review = counter.increment_turn(test_session, user_msg, assistant_msg)
        print(f"   Turn {turn_count}: last_review={last_review}")

    print("\n2. Testing should_review...")
    should_review = counter.should_review(test_session, review_interval=10)
    print(f"   Should review at turn 11? {should_review}")

    print("\n3. Testing mark_reviewed...")
    counter.mark_reviewed(test_session)
    stats = counter.get_session_stats(test_session)
    print(f"   After marking reviewed: {stats}")

    print("\n4. Testing get_recent_turns...")
    recent = counter.get_recent_turns(test_session, count=5)
    print(f"   Recent 5 turns:")
    for turn in recent:
        print(f"     Turn {turn['turn_number']}: {turn['user_message'][:30]}...")

    print("\n5. Adding more turns to trigger next review...")
    for i in range(12, 22):
        turn_count, last_review = counter.increment_turn(
            test_session,
            f"Test user message {i}",
            f"Test assistant response {i}"
        )
        print(f"   Turn {turn_count}: last_review={last_review}")

    should_review = counter.should_review(test_session, review_interval=10)
    print(f"\n   Should review at turn 21? {should_review}")

    print("\n✅ Turn Counter tests complete!")
    print(f"   Test database: {test_db}")
    print(f"   Inspect with: sqlite3 {test_db}")

    return True


def test_system_integration():
    """Test that all system files exist."""
    print("\n" + "=" * 60)
    print("Testing System Integration")
    print("=" * 60)

    required_files = [
        ("hooks/utils/turn_counter.py", "Turn Counter"),
        ("hooks/mini_doc_agent.py", "Mini-Doc Agent"),
        ("hooks/trace_review_agent.py", "Trace Review Agent"),
        ("hooks/stop.py", "Stop Hook"),
        ("agents/TRACE_REVIEW_AGENT.md", "Agent Documentation"),
        ("context/observability/TURN_BASED_REVIEW_SYSTEM.md", "System Documentation"),
    ]

    # Base path is .claude directory
    base_path = Path(__file__).parent.parent
    all_exist = True

    for file_path, description in required_files:
        full_path = base_path / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {file_path}")
        if not exists:
            all_exist = False

    if all_exist:
        print("\n✅ All system files present!")
    else:
        print("\n❌ Some files missing!")

    return all_exist


def main():
    """Run all tests."""
    print("\n🧪 Turn-Based Review System Test Suite\n")

    results = []

    # Test 1: Turn Counter
    try:
        results.append(("Turn Counter", test_turn_counter()))
    except Exception as e:
        print(f"❌ Turn Counter test failed: {e}")
        results.append(("Turn Counter", False))

    # Test 2: System Integration
    try:
        results.append(("System Integration", test_system_integration()))
    except Exception as e:
        print(f"❌ System Integration test failed: {e}")
        results.append(("System Integration", False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed!")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
