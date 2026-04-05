#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic",
#     "boto3",
# ]
# ///

"""
Session Summary Hook (SessionEnd)

Reads the full session transcript, calls Haiku to generate a templated
summary, and saves it to .claude/session-summaries/YYYYMMDD-{slug}.md
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SUMMARIES_DIR = Path(__file__).resolve().parent.parent / "session-summaries"
SECRET_ID = "claude-observability/anthropic"
AWS_REGION = "us-east-1"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
MAX_TRANSCRIPT_CHARS = 80_000  # keep prompt under context limit


# ── logging ──────────────────────────────────────────────────────────
def _log(msg: str):
    try:
        log_file = Path.home() / ".claude" / "logs" / "session_summary_debug.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        print(f"[SESSION-SUMMARY] {msg}", file=sys.stderr)


# ── API key retrieval ────────────────────────────────────────────────
def get_api_key() -> str | None:
    """Try env var first, then AWS Secrets Manager."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if key and key.startswith("sk-ant-api"):
        return key
    try:
        import boto3
        sm = boto3.client("secretsmanager", region_name=AWS_REGION)
        resp = sm.get_secret_value(SecretId=SECRET_ID)
        val = resp["SecretString"]
        # could be raw string or JSON
        try:
            parsed = json.loads(val)
            return parsed.get("api_key") or parsed.get("ANTHROPIC_API_KEY") or val
        except json.JSONDecodeError:
            return val
    except Exception as e:
        _log(f"Failed to get API key from Secrets Manager: {e}")
    return None


# ── transcript parsing ───────────────────────────────────────────────
def parse_transcript(path: str) -> dict:
    """Extract structured data from a .jsonl transcript file."""
    messages = []
    tools_used = set()
    total_input = 0
    total_output = 0
    first_user_msg = ""
    last_user_msg = ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = entry.get("type", "")
                msg_data = entry.get("message", {})

                if msg_type == "user":
                    content = ""
                    raw_content = msg_data.get("content") or entry.get("content", "")
                    if isinstance(raw_content, list):
                        content = " ".join(
                            item.get("text", "")
                            for item in raw_content
                            if isinstance(item, dict) and item.get("type") == "text"
                        )
                    elif isinstance(raw_content, str):
                        content = raw_content
                    if content.strip():
                        messages.append({"role": "user", "text": content.strip()[:500]})
                        if not first_user_msg:
                            first_user_msg = content.strip()[:200]
                        last_user_msg = content.strip()[:200]

                elif msg_type == "assistant":
                    content = ""
                    raw_content = msg_data.get("content", [])
                    if isinstance(raw_content, list):
                        for item in raw_content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    content += item.get("text", "")
                                elif item.get("type") == "tool_use":
                                    tools_used.add(item.get("name", "unknown"))
                    elif isinstance(raw_content, str):
                        content = raw_content
                    if content.strip():
                        messages.append({"role": "assistant", "text": content.strip()[:500]})

                    usage = msg_data.get("usage", {})
                    total_input += usage.get("input_tokens", 0)
                    total_output += usage.get("output_tokens", 0)

    except Exception as e:
        _log(f"Error parsing transcript: {e}")

    return {
        "messages": messages,
        "tools_used": sorted(tools_used),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "turn_count": sum(1 for m in messages if m["role"] == "user"),
        "first_user_msg": first_user_msg,
        "last_user_msg": last_user_msg,
    }


# ── Haiku summary generation ────────────────────────────────────────
SUMMARY_PROMPT = """\
You are a session summarizer. Given a Claude Code session transcript, produce a structured markdown report using EXACTLY this template. Fill in every section. Be concise.

```template
# Session Summary — {date}

## Session Name
{2-5 word descriptive name for this session, lowercase kebab-case is fine}

## TL;DR
{1-2 sentence executive summary of what was accomplished}

## Topics Covered
{bulleted list of main topics/tasks, 3-8 items}

## Key Decisions & Outcomes
{bulleted list of decisions made, outcomes reached, or artifacts produced}

## Tools & Integrations Used
{bulleted list of tools/services/APIs invoked during the session}

## Files Modified
{bulleted list of files created or edited, if identifiable from transcript}

## Open Items / Next Steps
{bulleted list of anything left unfinished or explicitly deferred}

## Session Stats
- **Turns**: {n}
- **Input tokens**: {n}
- **Output tokens**: {n}
- **Duration**: {estimate or "unknown"}
```

Here is the transcript (user/assistant messages, truncated):

{transcript}
"""


def generate_summary(api_key: str, transcript_data: dict, date_str: str) -> str | None:
    """Call Haiku to produce the templated summary."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Build condensed transcript for the prompt
        condensed = []
        for m in transcript_data["messages"]:
            role = "USER" if m["role"] == "user" else "ASSISTANT"
            condensed.append(f"[{role}]: {m['text']}")
        transcript_text = "\n\n".join(condensed)
        if len(transcript_text) > MAX_TRANSCRIPT_CHARS:
            # Keep first third and last third
            third = MAX_TRANSCRIPT_CHARS // 3
            transcript_text = (
                transcript_text[:third]
                + "\n\n... [middle of session truncated] ...\n\n"
                + transcript_text[-third:]
            )

        prompt = SUMMARY_PROMPT.replace("{date}", date_str).replace(
            "{transcript}", transcript_text
        )

        resp = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()

    except Exception as e:
        _log(f"Haiku summary generation failed: {e}")
        return None


def fallback_summary(transcript_data: dict, date_str: str) -> str:
    """Generate a basic summary without LLM when no API key is available."""
    tools = ", ".join(transcript_data["tools_used"][:15]) or "None detected"
    first = transcript_data["first_user_msg"] or "N/A"
    last = transcript_data["last_user_msg"] or "N/A"

    return f"""# Session Summary — {date_str}

## Session Name
auto-generated-fallback

## TL;DR
Session with {transcript_data['turn_count']} user turns. First request: "{first[:100]}..."

## Topics Covered
- First message: {first[:150]}
- Last message: {last[:150]}

## Key Decisions & Outcomes
- (LLM summary unavailable — no API key found)

## Tools & Integrations Used
- {tools}

## Files Modified
- (not extracted)

## Open Items / Next Steps
- (not extracted)

## Session Stats
- **Turns**: {transcript_data['turn_count']}
- **Input tokens**: {transcript_data['total_input_tokens']:,}
- **Output tokens**: {transcript_data['total_output_tokens']:,}
- **Duration**: unknown
"""


# ── slug generation ──────────────────────────────────────────────────
def extract_slug(summary_text: str, session_id: str) -> str:
    """Pull the session name from the summary or fall back to session_id."""
    # Look for the "## Session Name" line
    match = re.search(r"## Session Name\s*\n+(.+)", summary_text)
    if match:
        raw = match.group(1).strip().strip("`").strip()
        # Sanitize to filesystem-safe slug
        slug = re.sub(r"[^a-zA-Z0-9_-]", "-", raw.lower())
        slug = re.sub(r"-+", "-", slug).strip("-")
        if slug and len(slug) >= 3:
            return slug[:60]
    return session_id[:12]


# ── main ─────────────────────────────────────────────────────────────
def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        _log("No valid JSON on stdin")
        sys.exit(0)

    session_id = input_data.get("session_id", "unknown")
    transcript_path = input_data.get("transcript_path", "")
    reason = input_data.get("reason", "unknown")

    _log(f"=== session_summary.py called: session={session_id}, reason={reason} ===")

    if not transcript_path or not Path(transcript_path).exists():
        _log(f"No transcript found at: {transcript_path}")
        sys.exit(0)

    # Parse the transcript
    transcript_data = parse_transcript(transcript_path)
    if transcript_data["turn_count"] < 2:
        _log(f"Only {transcript_data['turn_count']} turns — skipping summary for trivial session")
        sys.exit(0)

    date_str = datetime.now().strftime("%Y-%m-%d")
    date_prefix = datetime.now().strftime("%Y%m%d")

    # Generate summary
    api_key = get_api_key()
    if api_key:
        _log("Calling Haiku for summary...")
        summary = generate_summary(api_key, transcript_data, date_str)
        if not summary:
            _log("Haiku failed, using fallback")
            summary = fallback_summary(transcript_data, date_str)
    else:
        _log("No API key found, using fallback summary")
        summary = fallback_summary(transcript_data, date_str)

    # Extract slug for filename
    slug = extract_slug(summary, session_id)
    filename = f"{date_prefix}-{slug}.md"

    # Save
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SUMMARIES_DIR / filename

    # Handle duplicate filenames within same day
    counter = 1
    while out_path.exists():
        counter += 1
        filename = f"{date_prefix}-{slug}-{counter}.md"
        out_path = SUMMARIES_DIR / filename

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)
        f.write(f"\n\n---\n_Generated by session_summary.py | session_id: {session_id} | reason: {reason}_\n")

    _log(f"Summary saved to {out_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
