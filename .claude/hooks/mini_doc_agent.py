#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "anthropic",
# ]
# ///

"""
Mini-Doc Agent (Haiku)
Fast, lightweight documentation agent that records session details after each turn.
Uses Claude Haiku for efficiency.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def log_mini_doc(message):
    """Log mini-doc agent messages."""
    try:
        debug_file = Path.home() / ".claude" / "logs" / "mini_doc_debug.log"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception:
        print(f"[MINI-DOC] {message}", file=sys.stderr)


def extract_turn_summary(input_data):
    """Extract key information from the turn."""
    try:
        summary = {
            "session_id": input_data.get("session_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "user_message": "",
            "assistant_message": "",
            "tools_used": [],
            "errors": []
        }

        # Extract user message
        if "user_message" in input_data:
            summary["user_message"] = str(input_data["user_message"])[:300]

        # Extract assistant message
        if "assistant_message" in input_data:
            summary["assistant_message"] = str(input_data["assistant_message"])[:300]

        # Extract tools used (if available)
        if "tools_used" in input_data:
            summary["tools_used"] = input_data["tools_used"]

        return summary

    except Exception as e:
        log_mini_doc(f"Error extracting turn summary: {type(e).__name__}: {str(e)}")
        return None


def generate_doc_entry(summary, review_file=None):
    """Use Claude Haiku to generate a concise documentation entry."""
    try:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            log_mini_doc("No Anthropic API key found")
            return None

        client = anthropic.Anthropic(api_key=api_key)

        # Build prompt for Haiku
        prompt = f"""Summarize this conversation turn in 2-3 sentences:

User asked: {summary['user_message']}
Assistant responded: {summary['assistant_message']}
Tools used: {', '.join(summary['tools_used']) if summary['tools_used'] else 'None'}

Provide a concise summary of what was accomplished.
"""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Use Haiku for speed and cost
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )

        doc_entry = message.content[0].text.strip()
        log_mini_doc(f"Generated doc entry: {len(doc_entry)} chars")
        return doc_entry

    except Exception as e:
        log_mini_doc(f"Error generating doc entry: {type(e).__name__}: {str(e)}")
        import traceback
        log_mini_doc(traceback.format_exc())
        return None


def save_doc_entry(session_id, doc_entry, review_file=None):
    """Save documentation entry to session log."""
    try:
        # Save to session-specific log
        doc_dir = Path.home() / ".claude" / "data" / "session_docs" / session_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Append to session log
        log_file = doc_dir / "session_log.md"

        # Create or append to log
        mode = 'a' if log_file.exists() else 'w'
        with open(log_file, mode, encoding='utf-8') as f:
            if mode == 'w':
                f.write(f"# Session Documentation: {session_id}\n\n")
                f.write(f"**Started**: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")

            f.write(f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"{doc_entry}\n\n")

            if review_file:
                f.write(f"*Related review: [{review_file}]({review_file})*\n\n")

            f.write("---\n\n")

        log_mini_doc(f"Doc entry saved to {log_file}")
        return str(log_file)

    except Exception as e:
        log_mini_doc(f"Error saving doc entry: {type(e).__name__}: {str(e)}")
        return None


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--session-id", help="Session ID")
        parser.add_argument("--review-file", help="Optional review file to reference")
        parser.add_argument("--input", help="JSON input file")
        args = parser.parse_args()

        log_mini_doc(f"=== Starting mini-doc-agent ===")

        # Read input from stdin if not provided via file
        if args.input:
            with open(args.input, 'r') as f:
                input_data = json.load(f)
        else:
            try:
                input_data = json.load(sys.stdin)
            except:
                input_data = {}

        # Get session ID
        session_id = args.session_id or input_data.get("session_id", "unknown")

        # Extract turn summary
        summary = extract_turn_summary(input_data)
        if not summary:
            log_mini_doc("Failed to extract turn summary")
            return

        # Generate documentation entry with Haiku
        doc_entry = generate_doc_entry(summary, args.review_file)
        if not doc_entry:
            # Fallback to simple summary
            doc_entry = f"User: {summary['user_message'][:100]}... | Tools: {', '.join(summary['tools_used'][:3]) if summary['tools_used'] else 'None'}"
            log_mini_doc("Using fallback doc entry")

        # Save documentation entry
        log_file = save_doc_entry(session_id, doc_entry, args.review_file)
        if not log_file:
            log_mini_doc("Failed to save doc entry")
            return

        log_mini_doc("=== Mini-doc-agent complete ===")

        # Return success
        print(json.dumps({"status": "success", "log_file": log_file}))

    except Exception as e:
        log_mini_doc(f"Error in mini-doc-agent: {type(e).__name__}: {str(e)}")
        import traceback
        log_mini_doc(traceback.format_exc())


if __name__ == "__main__":
    main()
