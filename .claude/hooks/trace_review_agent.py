#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "anthropic",
# ]
# ///

"""
Trace Review Agent
Analyzes session traces every N turns to extract patterns and insights.
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

sys.path.insert(0, str(Path(__file__).parent / "utils"))


def log_review(message):
    """Log review messages to debug file."""
    try:
        debug_file = Path.home() / ".claude" / "logs" / "trace_review_debug.log"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception as e:
        print(f"[REVIEW-DEBUG] {message}", file=sys.stderr)


def get_recent_transcript_data(transcript_path, count=10):
    """Extract recent turns from transcript file."""
    turns = []
    try:
        if not transcript_path or not Path(transcript_path).exists():
            log_review(f"Transcript not found: {transcript_path}")
            return turns

        with open(transcript_path, 'r', encoding='utf-8') as f:
            all_lines = []
            for line in f:
                if line.strip():
                    try:
                        all_lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Extract user/assistant pairs
        current_turn = {}
        for msg in all_lines:
            if msg.get("type") == "user":
                if current_turn and "user" in current_turn:
                    turns.append(current_turn)
                current_turn = {"user": msg.get("message", {}).get("content", "")}
            elif msg.get("type") == "assistant":
                content = ""
                msg_data = msg.get("message", {})
                if isinstance(msg_data.get("content"), list):
                    for item in msg_data.get("content", []):
                        if isinstance(item, dict) and item.get("type") == "text":
                            content += item.get("text", "")
                elif isinstance(msg_data.get("content"), str):
                    content = msg_data.get("content", "")

                current_turn["assistant"] = content
                usage = msg_data.get("usage", {})
                current_turn["usage"] = usage

        if current_turn and "user" in current_turn:
            turns.append(current_turn)

        # Return last N turns
        return turns[-count:]

    except Exception as e:
        log_review(f"Error extracting transcript data: {type(e).__name__}: {str(e)}")
        return turns


def analyze_with_claude(turns, session_id, turn_count):
    """Use Claude to analyze the session turns and generate insights."""
    try:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            log_review("No Anthropic API key found")
            return None

        client = anthropic.Anthropic(api_key=api_key)

        # Build analysis prompt
        turns_summary = []
        for idx, turn in enumerate(turns, 1):
            user_msg = turn.get("user", "")[:200]
            assistant_msg = turn.get("assistant", "")[:200]
            usage = turn.get("usage", {})
            turns_summary.append(
                f"Turn {idx}:\n"
                f"  User: {user_msg}...\n"
                f"  Assistant: {assistant_msg}...\n"
                f"  Tokens: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out\n"
            )

        prompt = f"""Analyze the following session turns and provide insights:

Session ID: {session_id}
Current Turn: {turn_count}
Turns Analyzed: {len(turns)}

{chr(10).join(turns_summary)}

Please provide:
1. **Summary**: High-level overview of what's happening in this session
2. **Key Patterns**: Recurring themes, tool usage patterns, or workflows
3. **Issues Detected**: Any errors, inefficiencies, or problems
4. **Recommendations**: Actionable suggestions for improvement
5. **Next Steps**: What should happen next in this session

Format your response as markdown.
"""

        message = client.messages.create(
            model=os.getenv("REVIEW_MODEL", "claude-haiku-4-5-20251001"),  # Haiku 4.5 for cost efficiency
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        analysis = message.content[0].text
        log_review(f"Analysis complete: {len(analysis)} chars")
        return analysis

    except Exception as e:
        log_review(f"Error analyzing with Claude: {type(e).__name__}: {str(e)}")
        import traceback
        log_review(traceback.format_exc())
        return None


def save_review(session_id, turn_count, analysis):
    """Save review analysis to file."""
    try:
        review_dir = Path.home() / ".claude" / "data" / "reviews" / session_id
        review_dir.mkdir(parents=True, exist_ok=True)

        review_file = review_dir / f"review_turn_{turn_count}.md"

        content = f"""# Session Review - Turn {turn_count}
**Session ID**: {session_id}
**Timestamp**: {datetime.now().isoformat()}
**Review Generated By**: Trace Review Agent

---

{analysis}

---

*Generated automatically every 10 turns*
"""

        with open(review_file, 'w', encoding='utf-8') as f:
            f.write(content)

        log_review(f"Review saved to {review_file}")
        return str(review_file)

    except Exception as e:
        log_review(f"Error saving review: {type(e).__name__}: {str(e)}")
        return None


def trigger_mini_doc_agent(session_id, review_file):
    """Trigger mini-doc-agent to record the review."""
    try:
        log_review(f"Triggering mini-doc-agent for review: {review_file}")

        # Call mini-doc-agent script
        import subprocess
        mini_doc_script = Path(__file__).parent / "mini_doc_agent.py"

        if not mini_doc_script.exists():
            log_review("mini-doc-agent script not found")
            return

        result = subprocess.run(
            ["uv", "run", str(mini_doc_script), "--session-id", session_id, "--review-file", review_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            log_review("mini-doc-agent completed successfully")
        else:
            log_review(f"mini-doc-agent failed: {result.stderr}")

    except Exception as e:
        log_review(f"Error triggering mini-doc-agent: {type(e).__name__}: {str(e)}")


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--session-id", required=True, help="Session ID")
        parser.add_argument("--transcript-path", help="Path to transcript file")
        parser.add_argument("--turn-count", type=int, help="Current turn count")
        args = parser.parse_args()

        log_review(f"=== Starting trace review for session {args.session_id} ===")

        # Check if reviews are enabled
        if os.getenv("ENABLE_TRACE_REVIEW", "true").lower() != "true":
            log_review("Trace reviews disabled")
            return

        # Extract recent turns from transcript
        turns = get_recent_transcript_data(args.transcript_path, count=10)
        log_review(f"Extracted {len(turns)} turns from transcript")

        if not turns:
            log_review("No turns to analyze")
            return

        # Analyze with Claude
        analysis = analyze_with_claude(turns, args.session_id, args.turn_count or 0)
        if not analysis:
            log_review("Analysis failed")
            return

        # Save review
        review_file = save_review(args.session_id, args.turn_count or 0, analysis)
        if not review_file:
            log_review("Failed to save review")
            return

        # Trigger mini-doc-agent to record the review
        trigger_mini_doc_agent(args.session_id, review_file)

        log_review("=== Trace review complete ===")

    except Exception as e:
        log_review(f"Error in trace review: {type(e).__name__}: {str(e)}")
        import traceback
        log_review(traceback.format_exc())


if __name__ == "__main__":
    main()
