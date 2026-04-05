#!/usr/bin/env python3
"""
Turn Counter with SQLite
Tracks conversation turns per session to trigger periodic reviews.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


class TurnCounter:
    """Manages turn counting for sessions using SQLite."""

    def __init__(self, db_path=None):
        """Initialize turn counter with SQLite database."""
        if db_path is None:
            db_path = Path.home() / ".claude" / "data" / "turn_counter.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_turns (
                    session_id TEXT PRIMARY KEY,
                    turn_count INTEGER DEFAULT 0,
                    last_review_turn INTEGER DEFAULT 0,
                    last_turn_timestamp TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS turn_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    turn_number INTEGER,
                    timestamp TEXT,
                    user_message TEXT,
                    assistant_message TEXT
                )
            """)
            conn.commit()

    def increment_turn(self, session_id, user_message="", assistant_message=""):
        """Increment turn count for a session and return the new count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get current turn count or create new session
            cursor.execute(
                "SELECT turn_count, last_review_turn FROM session_turns WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()

            if result:
                turn_count, last_review_turn = result
                turn_count += 1
            else:
                turn_count = 1
                last_review_turn = 0
                cursor.execute(
                    """INSERT INTO session_turns (session_id, turn_count, last_review_turn, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (session_id, 0, 0, datetime.now().isoformat())
                )

            # Update turn count
            cursor.execute(
                """UPDATE session_turns
                   SET turn_count = ?, last_turn_timestamp = ?
                   WHERE session_id = ?""",
                (turn_count, datetime.now().isoformat(), session_id)
            )

            # Record turn in history
            cursor.execute(
                """INSERT INTO turn_history (session_id, turn_number, timestamp, user_message, assistant_message)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, turn_count, datetime.now().isoformat(), user_message[:500], assistant_message[:500])
            )

            conn.commit()

            return turn_count, last_review_turn

    def should_review(self, session_id, review_interval=10):
        """Check if a review should be triggered based on turn count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT turn_count, last_review_turn FROM session_turns WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()

            if not result:
                return False

            turn_count, last_review_turn = result

            # Review every N turns
            if turn_count > 0 and (turn_count - last_review_turn) >= review_interval:
                return True

            return False

    def mark_reviewed(self, session_id):
        """Mark that a review has been completed for this session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE session_turns
                   SET last_review_turn = turn_count
                   WHERE session_id = ?""",
                (session_id,)
            )
            conn.commit()

    def get_session_stats(self, session_id):
        """Get statistics for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT turn_count, last_review_turn, created_at, last_turn_timestamp
                   FROM session_turns WHERE session_id = ?""",
                (session_id,)
            )
            result = cursor.fetchone()

            if not result:
                return None

            return {
                "turn_count": result[0],
                "last_review_turn": result[1],
                "created_at": result[2],
                "last_turn_timestamp": result[3]
            }

    def get_recent_turns(self, session_id, count=10):
        """Get recent turns for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT turn_number, timestamp, user_message, assistant_message
                   FROM turn_history
                   WHERE session_id = ?
                   ORDER BY turn_number DESC
                   LIMIT ?""",
                (session_id, count)
            )
            rows = cursor.fetchall()

            return [
                {
                    "turn_number": row[0],
                    "timestamp": row[1],
                    "user_message": row[2],
                    "assistant_message": row[3]
                }
                for row in rows
            ]


def get_default_counter():
    """Get the default turn counter instance."""
    return TurnCounter()
