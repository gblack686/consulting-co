#!/usr/bin/env python3
"""Diagnostic script to debug event buffer issues."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

db_path = Path.home() / ".claude" / "logs" / "events.db"

def diagnose():
    """Run diagnostics on event buffer."""
    if not db_path.exists():
        print(f"❌ Database does not exist at {db_path}")
        return

    print(f"📊 Database path: {db_path}")
    print(f"📊 File size: {db_path.stat().st_size} bytes")

    with sqlite3.connect(db_path) as conn:
        # Check schema
        cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='events'")
        schema = cursor.fetchone()
        if schema:
            print(f"\n📋 Table schema:\n{schema[0]}\n")

        # Get total events
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        print(f"📊 Total events in DB: {total}")

        # Get event breakdown by type
        print(f"\n📊 Event types breakdown:")
        cursor = conn.execute("""
            SELECT hook_event_type, COUNT(*) as count FROM events
            GROUP BY hook_event_type
            ORDER BY count DESC
        """)
        for event_type, count in cursor.fetchall():
            print(f"  - {event_type}: {count}")

        # Get session breakdown
        print(f"\n📊 Last 10 sessions:")
        cursor = conn.execute("""
            SELECT session_id, COUNT(*) as count FROM events
            GROUP BY session_id
            ORDER BY MAX(created_at) DESC
            LIMIT 10
        """)
        for session_id, count in cursor.fetchall():
            short_id = session_id[:16] + "..."
            cursor2 = conn.execute("""
                SELECT hook_event_type, COUNT(*) FROM events
                WHERE session_id = ?
                GROUP BY hook_event_type
            """, (session_id,))
            types = ", ".join([f"{t}:{c}" for t, c in cursor2.fetchall()])
            print(f"  {short_id} ({count} events: {types})")

        # Check for Stop events
        print(f"\n📊 Stop events:")
        cursor = conn.execute("""
            SELECT session_id, timestamp FROM events
            WHERE hook_event_type = 'Stop'
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        stop_events = cursor.fetchall()
        if stop_events:
            for session_id, timestamp in stop_events:
                short_id = session_id[:16] + "..."
                print(f"  {short_id} @ {timestamp}")
        else:
            print(f"  ❌ No Stop events found in database!")

        # Check if Stop event is immediately deleted
        print(f"\n📊 Checking event lifecycle for Stop events...")
        cursor = conn.execute("""
            SELECT session_id, hook_event_type, timestamp, created_at FROM events
            WHERE hook_event_type IN ('UserPromptSubmit', 'Stop')
            ORDER BY session_id DESC, timestamp ASC
            LIMIT 20
        """)
        rows = cursor.fetchall()
        if rows:
            last_session = None
            for session_id, event_type, timestamp, created_at in rows:
                if session_id != last_session:
                    print(f"\n  Session: {session_id[:16]}...")
                    last_session = session_id
                print(f"    - {event_type}: {timestamp} (created: {created_at})")

        # Test buffer operations
        print(f"\n🔧 Testing buffer operations...")
        test_session = "test-session-" + datetime.now().isoformat().replace(':', '-')

        # Insert test event
        conn.execute("""
            INSERT INTO events (session_id, hook_event_type, timestamp, data)
            VALUES (?, ?, ?, ?)
        """, (test_session, "TestEvent", datetime.now().isoformat(), json.dumps({"test": "data"})))
        conn.commit()

        # Query immediately
        cursor = conn.execute("SELECT COUNT(*) FROM events WHERE session_id = ?", (test_session,))
        count = cursor.fetchone()[0]
        print(f"  ✓ Inserted test event, retrieved count: {count}")

        # Clean up
        conn.execute("DELETE FROM events WHERE session_id = ?", (test_session,))
        conn.commit()
        print(f"  ✓ Cleaned up test event")

if __name__ == "__main__":
    diagnose()
