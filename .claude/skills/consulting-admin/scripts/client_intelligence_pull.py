"""
Generalized intelligence pull for any consulting client.
Pulls Gmail threads, Drive transcripts, and Calendar events,
writing everything to a client's second-brain intelligence folder.

Usage:
  python client_intelligence_pull.py --config clients/fisch-group.json
  python client_intelligence_pull.py --config clients/gbautomation.json
  python client_intelligence_pull.py --config clients/gbautomation.json --skip-transcripts
"""
import sys
import os
import re
import argparse
import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import google_client

PT = ZoneInfo("America/Los_Angeles")


# ── Config Loading ────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    """Load client intelligence config from JSON file.

    Expected schema:
    {
      "client_name": "Fisch Group",
      "client_slug": "fish-group",
      "output_base": "C:/Users/.../second-brain/intelligence",
      "gmail_query": "after:2026/02/15 (from:mike@... OR to:mike@...)",
      "calendar_emails": ["mike@piermontbrands.com"],
      "calendar_keywords": ["fisch", "fish", "piermont"],
      "calendar_range": {"start": "2026-02-15T00:00:00Z", "end": "2026-04-15T00:00:00Z"},
      "transcript_docs": {
        "2026-03-05": {"id": "...", "title": "...", "slug": "session-1-intake"}
      },
      "contacts": "Michael Fisch (mike@piermontbrands.com)",
      "engagement_start": "2026-03-05",
      "status": "Active"
    }
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:60]


def to_pt_str(dt_str: str) -> str:
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.astimezone(PT).strftime("%Y-%m-%d %H:%M PT")
    except Exception:
        return dt_str


def extract_body_parts(payload: dict) -> tuple[str, str]:
    """Recursively extract (plain_text, html) from Gmail payload."""
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        text = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""
        return text, ""
    if mime == "text/html":
        data = payload.get("body", {}).get("data", "")
        html = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""
        plain = re.sub(r"<[^>]+>", " ", html)
        plain = re.sub(r"\s{3,}", "\n\n", plain)
        return plain.strip(), html
    plain_parts, html_parts = [], []
    for part in payload.get("parts", []):
        p, h = extract_body_parts(part)
        if p:
            plain_parts.append(p)
        if h:
            html_parts.append(h)
    return "\n\n".join(plain_parts), "\n\n".join(html_parts)


def strip_signature(body: str) -> str:
    patterns = [r"\n--\s*\n.*", r"\nGreg Black\nGBAutomation.*", r"\n_{3,}.*"]
    for p in patterns:
        body = re.sub(p, "", body, flags=re.DOTALL)
    return body.strip()


# ── Gmail Pull ────────────────────────────────────────────────────────────────

def pull_gmail_threads(gmail, query: str) -> list:
    result = gmail.users().threads().list(userId="me", q=query, maxResults=500).execute()
    thread_metas = result.get("threads", [])
    print(f"  Found {len(thread_metas)} threads")

    threads_out = []
    for meta in thread_metas:
        thread = gmail.users().threads().get(userId="me", id=meta["id"], format="full").execute()
        messages = thread.get("messages", [])
        if not messages:
            continue

        def get_headers(msg):
            return {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}

        first_headers = get_headers(messages[0])
        last_headers = get_headers(messages[-1])

        participants = set()
        parsed_messages = []
        for msg in messages:
            h = get_headers(msg)
            from_addr = h.get("From", "")
            to_addr = h.get("To", "")
            participants.add(from_addr)
            for addr in to_addr.split(","):
                participants.add(addr.strip())
            plain, html = extract_body_parts(msg["payload"])
            body = plain or re.sub(r"<[^>]+>", " ", html)
            body = strip_signature(body)
            parsed_messages.append({
                "id": msg["id"],
                "from": from_addr,
                "to": to_addr,
                "date": h.get("Date", ""),
                "body": body.strip(),
            })

        threads_out.append({
            "thread_id": meta["id"],
            "subject": first_headers.get("Subject", "(no subject)"),
            "first_date": first_headers.get("Date", ""),
            "last_date": last_headers.get("Date", ""),
            "message_count": len(messages),
            "participants": sorted(participants),
            "messages": parsed_messages,
        })
    return threads_out


def write_thread_files(threads: list, output_dir: Path, client_name: str) -> list:
    output_dir.mkdir(parents=True, exist_ok=True)
    index_entries = []
    for t in threads:
        date_str = "0000-00-00"
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(t["first_date"])
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            pass

        slug = slugify(t["subject"])
        filename = f"{date_str}-{slug}.md"
        filepath = output_dir / filename

        lines = [
            "---",
            f'thread_id: "{t["thread_id"]}"',
            f'subject: "{t["subject"].replace(chr(34), chr(39))}"',
            f'participants: {json.dumps(t["participants"])}',
            f'first_message_date: "{t["first_date"]}"',
            f'last_message_date: "{t["last_date"]}"',
            f'message_count: {t["message_count"]}',
            f"client: {client_name}",
            "type: email-thread",
            "---", "",
            f"# {t['subject']}", "",
            f"**Thread ID**: `{t['thread_id']}`  ",
            f"**Messages**: {t['message_count']}  ",
            f"**Date range**: {t['first_date']} → {t['last_date']}  ",
            f"**Participants**: {', '.join(t['participants'])}", "",
            "---", "",
        ]
        for i, msg in enumerate(t["messages"], 1):
            lines.extend([
                f"## Message {i}",
                f"**From**: {msg['from']}  ",
                f"**To**: {msg['to']}  ",
                f"**Date**: {msg['date']}  ", "",
            ])
            body = msg["body"]
            if len(body) > 8000:
                body = body[:8000] + "\n\n[... truncated ...]"
            lines.extend([body, "", "---", ""])

        filepath.write_text("\n".join(lines), encoding="utf-8")
        index_entries.append((date_str, slug, t["subject"], filename, t["message_count"]))
        print(f"    Wrote: {filename}")
    return index_entries


# ── Drive Transcripts ─────────────────────────────────────────────────────────

def pull_transcripts(drive, transcript_docs: dict, output_dir: Path, client_name: str) -> list:
    if not transcript_docs:
        return []
    output_dir.mkdir(parents=True, exist_ok=True)
    index_entries = []

    for date_str, info in transcript_docs.items():
        doc_id = info["id"]
        slug = info["slug"]
        title = info["title"]
        filename = f"{date_str}-{slug}.md"
        filepath = output_dir / filename

        print(f"  Fetching transcript: {title}")
        try:
            request = drive.files().export_media(fileId=doc_id, mimeType="text/plain")
            content = request.execute()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            else:
                content = str(content)
        except Exception as e:
            print(f"    ERROR: {e}")
            content = f"[Export failed: {e}]"

        drive_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        lines = [
            "---",
            f'title: "{title}"',
            f'date: "{date_str}"',
            f'drive_doc_id: "{doc_id}"',
            f'drive_url: "{drive_url}"',
            f"client: {client_name}",
            "type: meet-transcript",
            "---", "",
            f"# {title}", "",
            f"**Drive**: [{doc_id}]({drive_url})  ",
            f"**Date**: {date_str}  ", "",
            "---", "",
            content,
        ]
        filepath.write_text("\n".join(lines), encoding="utf-8")
        char_count = len(content)
        index_entries.append((date_str, slug, title, filename, char_count))
        print(f"    Wrote: {filename}  ({char_count:,} chars)")
    return index_entries


# ── Calendar ──────────────────────────────────────────────────────────────────

def pull_calendar_events(cal, config: dict) -> list:
    cal_range = config.get("calendar_range", {})
    time_min = cal_range.get("start", "2026-01-01T00:00:00Z")
    time_max = cal_range.get("end", "2026-12-31T00:00:00Z")

    events_result = cal.events().list(
        calendarId="primary",
        timeMin=time_min, timeMax=time_max,
        maxResults=500, singleEvents=True, orderBy="startTime",
    ).execute()

    cal_emails = {e.lower() for e in config.get("calendar_emails", [])}
    cal_keywords = [kw.lower() for kw in config.get("calendar_keywords", [])]

    matched = []
    for ev in events_result.get("items", []):
        attendees = [a.get("email", "").lower() for a in ev.get("attendees", [])]
        title = ev.get("summary", "").lower()
        desc = (ev.get("description") or "").lower()

        if (any(e in attendees for e in cal_emails)
                or any(kw in title or kw in desc for kw in cal_keywords)):
            matched.append(ev)
    return matched


def write_calendar_file(events: list, output_dir: Path, config: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    client_name = config["client_name"]
    client_slug = config["client_slug"]
    filepath = output_dir / f"{client_slug}-meetings.md"

    lines = [
        "---",
        f"client: {client_name}",
        "type: calendar-events",
        "---", "",
        f"# {client_name} — All Calendar Events", "",
        f"*{len(events)} events pulled from greg@gbautomation.xyz calendar*", "",
        "---", "",
    ]

    transcript_docs = config.get("transcript_docs", {})
    for ev in events:
        start_raw = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))
        end_raw = ev.get("end", {}).get("dateTime", ev.get("end", {}).get("date", ""))
        start_pt = to_pt_str(start_raw)
        duration_str = ""
        try:
            dt_s = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            dt_e = datetime.fromisoformat(end_raw.replace("Z", "+00:00"))
            duration_str = f"{int((dt_e - dt_s).total_seconds() / 60)} min"
        except Exception:
            pass

        title = ev.get("summary", "(no title)")
        attendees = [a.get("email", "") for a in ev.get("attendees", [])]
        meet_link = ev.get("hangoutLink", "")

        lines.extend([
            f"## {start_pt} — {title}", "",
            "| Field | Value |",
            "|-------|-------|",
            f"| Date (PT) | {start_pt} |",
            f"| Duration | {duration_str} |",
            f"| Attendees | {', '.join(attendees)} |",
        ])
        if meet_link:
            lines.append(f"| Meet Link | [{meet_link}]({meet_link}) |")
        lines.extend(["", "---", ""])

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


# ── Indexes ───────────────────────────────────────────────────────────────────

def write_correspondence_index(index_entries: list, output_dir: Path, client_name: str) -> None:
    filepath = output_dir / "_INDEX.md"
    sorted_entries = sorted(index_entries, key=lambda x: x[0])
    lines = [
        "---", "type: index", "section: correspondence",
        f"client: {client_name}", "---", "",
        f"# {client_name} — Email Correspondence Index", "",
        f"*{len(sorted_entries)} threads pulled from greg@gbautomation.xyz*", "",
        "| Date | Subject | Messages | File |",
        "|------|---------|----------|------|",
    ]
    for date_str, slug, subject, filename, msg_count in sorted_entries:
        lines.append(f"| {date_str} | {subject[:60]} | {msg_count} | [{filename}]({filename}) |")
    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


def write_transcripts_index(index_entries: list, output_dir: Path, client_name: str) -> None:
    filepath = output_dir / "_INDEX.md"
    sorted_entries = sorted(index_entries, key=lambda x: x[0])
    lines = [
        "---", "type: index", "section: transcripts",
        f"client: {client_name}", "---", "",
        f"# {client_name} — Meet Transcript Index", "",
        f"*{len(sorted_entries)} transcripts pulled from Google Drive*", "",
        "| Date | Session | Characters | File |",
        "|------|---------|------------|------|",
    ]
    for date_str, slug, title, filename, char_count in sorted_entries:
        lines.append(f"| {date_str} | {title[:60]} | {char_count:,} | [{filename}]({filename}) |")
    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


def write_master_timeline(config: dict, base: Path,
                          thread_index: list, transcript_index: list,
                          calendar_events: list) -> None:
    filepath = base / "_ENGAGEMENT_TIMELINE.md"
    client_name = config["client_name"]
    today = datetime.now(PT).strftime("%Y-%m-%d")

    touchpoints = []
    for date_str, slug, subject, filename, msg_count in thread_index:
        touchpoints.append({
            "date": date_str, "type": "email",
            "summary": f"Email: {subject[:70]}",
            "link": f"correspondence/{filename}",
            "detail": f"{msg_count} message(s)",
        })
    for date_str, slug, title, filename, char_count in transcript_index:
        touchpoints.append({
            "date": date_str, "type": "transcript",
            "summary": f"Transcript: {title[:60]}",
            "link": f"transcripts/{filename}",
            "detail": f"{char_count:,} chars",
        })
    for ev in calendar_events:
        start_raw = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))
        try:
            dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            dt_pt = dt.astimezone(PT)
            date_str = dt_pt.strftime("%Y-%m-%d")
            time_str = dt_pt.strftime("%H:%M PT")
        except Exception:
            date_str, time_str = "0000-00-00", ""
        title = ev.get("summary", "(no title)")
        attendees = [a.get("email", "") for a in ev.get("attendees", [])]
        touchpoints.append({
            "date": date_str, "type": "meeting",
            "summary": f"Meeting: {title} @ {time_str}",
            "link": f"calendar/{config['client_slug']}-meetings.md",
            "detail": f"{', '.join(a for a in attendees if 'gbautomation' not in a)}",
        })

    touchpoints.sort(key=lambda x: x["date"])

    lines = [
        "---",
        f"client: {client_name}",
        "type: engagement-timeline",
        f'generated: "{today}"',
        "---", "",
        f"# {client_name} — Master Engagement Timeline", "",
        "A chronological record of every touchpoint in the engagement.", "",
        f"**Contacts**: {config.get('contacts', 'TBD')}  ",
        f"**Engagement start**: {config.get('engagement_start', 'TBD')}  ",
        f"**Status**: {config.get('status', 'Active')}", "",
        "---", "",
        "## Quick Stats", "",
        f"- **Email threads**: {len(thread_index)}",
        f"- **Meet transcripts pulled**: {len(transcript_index)}",
        f"- **Calendar events**: {len(calendar_events)}", "",
        "---", "",
        "## Chronological Touchpoints", "",
    ]

    current_month = ""
    for tp in touchpoints:
        month = tp["date"][:7] if tp["date"] else "Unknown"
        if month != current_month:
            current_month = month
            try:
                m_dt = datetime.strptime(month, "%Y-%m")
                lines.extend([f"### {m_dt.strftime('%B %Y')}", ""])
            except Exception:
                pass
        tag = {"email": "[EMAIL]", "transcript": "[TRANSCRIPT]", "meeting": "[MEETING]"}.get(tp["type"], "[?]")
        lines.append(f"- **{tp['date']}** {tag} [{tp['summary']}]({tp['link']}) — {tp['detail']}")

    lines.extend(["", "---", ""])
    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Pull intelligence for a consulting client")
    parser.add_argument("--config", "-c", required=True, help="Path to client config JSON")
    parser.add_argument("--skip-gmail", action="store_true", help="Skip Gmail pull")
    parser.add_argument("--skip-transcripts", action="store_true", help="Skip transcript pull")
    parser.add_argument("--skip-calendar", action="store_true", help="Skip calendar pull")
    args = parser.parse_args()

    config = load_config(args.config)
    client_name = config["client_name"]
    base = Path(config["output_base"])

    correspondence_dir = base / "correspondence"
    transcripts_dir = base / "transcripts"
    calendar_dir = base / "calendar"

    print("=" * 60)
    print(f"{client_name.upper()} — INTELLIGENCE PULL")
    print("=" * 60)

    gmail = google_client.gmail_service()
    drive = google_client.drive_service()
    cal = google_client.calendar_service()
    base.mkdir(parents=True, exist_ok=True)

    # 1. Gmail
    thread_index = []
    if not args.skip_gmail and config.get("gmail_query"):
        print("\n[1/4] Pulling Gmail threads...")
        threads = pull_gmail_threads(gmail, config["gmail_query"])
        print(f"  Processing {len(threads)} threads...")
        thread_index = write_thread_files(threads, correspondence_dir, client_name)
        write_correspondence_index(thread_index, correspondence_dir, client_name)
        print(f"  Done: {len(thread_index)} threads written")
    else:
        print("\n[1/4] Gmail — skipped")

    # 2. Transcripts
    transcript_index = []
    if not args.skip_transcripts and config.get("transcript_docs"):
        print("\n[2/4] Pulling Drive transcripts...")
        transcript_index = pull_transcripts(drive, config["transcript_docs"], transcripts_dir, client_name)
        write_transcripts_index(transcript_index, transcripts_dir, client_name)
        print(f"  Done: {len(transcript_index)} transcripts written")
    else:
        print("\n[2/4] Transcripts — skipped")

    # 3. Calendar
    calendar_events = []
    if not args.skip_calendar and (config.get("calendar_emails") or config.get("calendar_keywords")):
        print("\n[3/4] Pulling Calendar events...")
        calendar_events = pull_calendar_events(cal, config)
        write_calendar_file(calendar_events, calendar_dir, config)
        print(f"  Done: {len(calendar_events)} events written")
    else:
        print("\n[3/4] Calendar — skipped")

    # 4. Timeline
    print("\n[4/4] Writing master timeline...")
    write_master_timeline(config, base, thread_index, transcript_index, calendar_events)

    print("\n" + "=" * 60)
    print("PULL COMPLETE")
    print(f"  Output: {base}")
    print(f"  Threads: {len(thread_index)}")
    print(f"  Transcripts: {len(transcript_index)}")
    print(f"  Calendar events: {len(calendar_events)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
