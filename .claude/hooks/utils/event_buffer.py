#!/usr/bin/env python3
"""
Event buffer for Claude Code observability.
Buffers hook events per session with SQLite persistence for cross-process access.

Phase 5 Fix: Switched from JSON to SQLite for reliable event persistence across hooks.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class EventBuffer:
    """SQLite-persisted event buffer for session events.

    Uses SQLite for atomic, reliable persistence that works across
    different hook processes (session_start, pre_tool_use, post_tool_use, session_end).
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize event buffer with SQLite.

        Args:
            db_path: Path to SQLite database (defaults to ~/.claude/logs/events.db)
        """
        self.db_path = db_path or Path.home() / ".claude" / "logs" / "events.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database schema
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        hook_event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        data TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_id
                    ON events(session_id, timestamp)
                """)
                conn.commit()
        except Exception as e:
            import sys
            print(f"⚠️  Failed to initialize event buffer DB: {e}", file=sys.stderr)

    def add_event(self, session_id: str, event: Dict[str, Any]) -> None:
        """Add event to session buffer (SQLite).

        Args:
            session_id: Unique session identifier
            event: Event dict with hook data
        """
        try:
            # Ensure event has timestamp if not present
            if "timestamp" not in event:
                event["timestamp"] = datetime.now().isoformat()

            hook_event_type = event.get("hook_event_type", "unknown")
            timestamp = event["timestamp"]
            event_data = json.dumps(event, default=str)

            # Insert into SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (session_id, hook_event_type, timestamp, data)
                    VALUES (?, ?, ?, ?)
                """, (session_id, hook_event_type, timestamp, event_data))
                conn.commit()

        except Exception as e:
            import sys
            print(f"⚠️  Failed to add event to buffer: {e}", file=sys.stderr)

    def get_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all events for a session from SQLite.

        Args:
            session_id: Unique session identifier

        Returns:
            List of events in chronological order
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT data FROM events
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,)).fetchall()

            events = [json.loads(row[0]) for row in rows]
            return events

        except Exception as e:
            import sys
            print(f"⚠️  Failed to retrieve events for {session_id}: {e}", file=sys.stderr)
            return []

    def clear_session(self, session_id: str) -> bool:
        """Clear session events from SQLite.

        Args:
            session_id: Unique session identifier

        Returns:
            True if cleared successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM events WHERE session_id = ?", (session_id,))
                conn.commit()
            return True

        except Exception as e:
            import sys
            print(f"⚠️  Failed to clear event buffer for {session_id}: {e}", file=sys.stderr)
            return False

    def list_sessions(self) -> List[str]:
        """List all session IDs with buffered events from SQLite.

        Returns:
            List of session IDs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT DISTINCT session_id FROM events
                    ORDER BY session_id DESC
                """).fetchall()

            return [row[0] for row in rows]

        except Exception as e:
            import sys
            print(f"⚠️  Failed to list sessions: {e}", file=sys.stderr)
            return []

    def get_session_size(self, session_id: str) -> int:
        """Get number of events for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Number of events
        """
        return len(self.get_events(session_id))

    def get_event_types(self, session_id: str) -> Dict[str, int]:
        """Get breakdown of event types for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Dict of event_type -> count
        """
        events = self.get_events(session_id)
        event_types = {}

        for event in events:
            event_type = event.get("hook_event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return event_types

    def print_session_summary(self, session_id: str) -> None:
        """Pretty print summary of session events.

        Args:
            session_id: Unique session identifier
        """
        events = self.get_events(session_id)
        event_types = self.get_event_types(session_id)

        print("\n" + "="*60)
        print(f"📊 EVENT BUFFER: {session_id[:16]}...")
        print("="*60)
        print(f"Total Events: {len(events)}")
        print(f"\nEvent Types:")
        for event_type, count in sorted(event_types.items()):
            print(f"  {event_type}: {count}")

        if events:
            first_event = events[0]
            last_event = events[-1]
            print(f"\nTime Range:")
            print(f"  First: {first_event.get('timestamp', 'N/A')}")
            print(f"  Last:  {last_event.get('timestamp', 'N/A')}")

        print()


# Global instance for easy access
_default_buffer = None


def get_default_buffer() -> EventBuffer:
    """Get or create the default event buffer instance.

    Returns:
        EventBuffer instance
    """
    global _default_buffer
    if _default_buffer is None:
        _default_buffer = EventBuffer()
    return _default_buffer


def main():
    """CLI for event buffer management."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Event buffer management")
    parser.add_argument("command", choices=["list", "summary", "clear", "export"], help="Command")
    parser.add_argument("--session-id", help="Session ID (required for summary/clear)")
    parser.add_argument("--output", help="Output file (for export)")

    args = parser.parse_args()
    buffer = get_default_buffer()

    if args.command == "list":
        sessions = buffer.list_sessions()
        print(f"\n{'='*60}")
        print(f"📋 SESSIONS ({len(sessions)} total)")
        print(f"{'='*60}")
        for session_id in sessions:
            size = buffer.get_session_size(session_id)
            event_types = buffer.get_event_types(session_id)
            print(f"\n{session_id[:20]}...")
            print(f"  Events: {size}")
            print(f"  Types: {', '.join(event_types.keys())}")

    elif args.command == "summary":
        if not args.session_id:
            print("Error: --session-id required")
            sys.exit(1)
        buffer.print_session_summary(args.session_id)

    elif args.command == "clear":
        if not args.session_id:
            print("Error: --session-id required")
            sys.exit(1)
        if buffer.clear_session(args.session_id):
            print(f"✓ Cleared session {args.session_id}")
        else:
            print(f"✗ Failed to clear session {args.session_id}")

    elif args.command == "export":
        if not args.session_id or not args.output:
            print("Error: --session-id and --output required")
            sys.exit(1)
        events = buffer.get_events(args.session_id)
        with open(args.output, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        print(f"✓ Exported {len(events)} events to {args.output}")


if __name__ == "__main__":
    main()
