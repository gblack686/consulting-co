"""
Full intelligence pull for Fisch Group engagement.
Pulls Gmail threads, Drive transcripts, and Calendar events,
writing everything to the second-brain intelligence folder.

Target: C:/Users/gblac/OneDrive/Desktop/gbauto/fisch-group/second-brain/intelligence/
"""
import sys
import os
import re
import base64
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import google_client

# ── Config ─────────────────────────────────────────────────────────────────
BASE = Path("C:/Users/gblac/OneDrive/Desktop/gbauto/fisch-group/second-brain/intelligence")
CORRESPONDENCE_DIR = BASE / "correspondence"
TRANSCRIPTS_DIR = BASE / "transcripts"
CALENDAR_DIR = BASE / "calendar"

PT = ZoneInfo("America/Los_Angeles")

GMAIL_QUERY = (
    "after:2026/02/15 before:2026/04/10 "
    "("
    "from:mike@piermontbrands.com OR to:mike@piermontbrands.com OR "
    "from:ecaplow@fischgroup.com OR to:ecaplow@fischgroup.com OR "
    'subject:"Fisch Group" OR subject:"Fish Group" OR subject:"Piermont" OR '
    '"Fisch Group" OR "Fish Group" OR "Piermont Brands" OR "Chica Cheetah" OR "Drop Fitness" OR "clientflow" OR "Emilfisch"'
    ")"
)

# Known Fisch Group transcript doc IDs + the weekly AI Sessions
TRANSCRIPT_DOC_IDS = {
    "2026-03-05": {
        "id": "1GOkkbs_cTm896tZwtcVFF6pryj_MGl39YOxZumUHO_E",
        "title": "60 Minute Agent Build w Greg (Michael Fisch) - 2026/03/05 13:37 PST - Transcript",
        "slug": "session-1-intake",
    },
    "2026-03-12": {
        "id": "1daFmADKY8J032oAwxRfZ51Js4FOxawoKYXKXlxheZTc",
        "title": "45 min - AI Session - 2026/03/12 13:44 PDT - Transcript",
        "slug": "session-2-weekly",
    },
    "2026-03-19": {
        "id": "1BvNzLwAvZ-aj3RoysVGVfPfKViMEaj-c5DM7V6c4Ruc",
        "title": "AI Session - 2026/03/19 13:44 PDT - Transcript",
        "slug": "session-3-weekly",
    },
    "2026-03-26": {
        "id": "19ez-Dph-R8lN45Jfbtuorcxm4OIE7Vww5WI_uicbq4M",
        "title": "AI Session - 2026/03/26 13:44 PDT - Transcript",
        "slug": "session-4-weekly",
    },
    "2026-04-02": {
        "id": "1HBq1kLWnJPtXh8g9TTW66VEHsrk7asbvU7FZ_CSmySU",
        "title": "AI Session - 2026/04/02 13:44 PDT - Transcript",
        "slug": "session-5-weekly",
    },
}

FISCH_CALENDAR_EMAILS = {"mike@piermontbrands.com", "ecaplow@fischgroup.com"}


# ── Helpers ─────────────────────────────────────────────────────────────────

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:60]


def to_pt_str(dt_str: str) -> str:
    """Convert ISO datetime string (UTC or with offset) to PT display string."""
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        dt_pt = dt.astimezone(PT)
        return dt_pt.strftime("%Y-%m-%d %H:%M PT")
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
        # Strip HTML tags
        plain = re.sub(r"<[^>]+>", " ", html)
        plain = re.sub(r"\s{3,}", "\n\n", plain)
        return plain.strip(), html

    # multipart
    plain_parts, html_parts = [], []
    for part in payload.get("parts", []):
        p, h = extract_body_parts(part)
        if p:
            plain_parts.append(p)
        if h:
            html_parts.append(h)

    return "\n\n".join(plain_parts), "\n\n".join(html_parts)


def strip_signature(body: str) -> str:
    """Remove common email signature blocks."""
    patterns = [
        r"\n--\s*\n.*",
        r"\nGreg Black\nGBAutomation.*",
        r"\n_{3,}.*",
    ]
    for p in patterns:
        body = re.sub(p, "", body, flags=re.DOTALL)
    return body.strip()


# ── Gmail Pull ───────────────────────────────────────────────────────────────

def pull_gmail_threads(gmail):
    """Pull all matching threads, return list of thread dicts."""
    # Get thread IDs
    result = gmail.users().threads().list(
        userId="me",
        q=GMAIL_QUERY,
        maxResults=500,
    ).execute()
    thread_metas = result.get("threads", [])
    print(f"  Found {len(thread_metas)} threads")

    threads_out = []
    for meta in thread_metas:
        thread = gmail.users().threads().get(
            userId="me",
            id=meta["id"],
            format="full",
        ).execute()
        messages = thread.get("messages", [])
        if not messages:
            continue

        # Extract thread-level info from first/last message headers
        def get_headers(msg):
            return {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}

        first_headers = get_headers(messages[0])
        last_headers = get_headers(messages[-1])

        subject = first_headers.get("Subject", "(no subject)")
        first_date = first_headers.get("Date", "")
        last_date = last_headers.get("Date", "")

        # Collect all participants
        participants = set()
        parsed_messages = []
        for msg in messages:
            h = get_headers(msg)
            from_addr = h.get("From", "")
            to_addr = h.get("To", "")
            date_str = h.get("Date", "")
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
                "date": date_str,
                "body": body.strip(),
            })

        threads_out.append({
            "thread_id": meta["id"],
            "subject": subject,
            "first_date": first_date,
            "last_date": last_date,
            "message_count": len(messages),
            "participants": sorted(participants),
            "messages": parsed_messages,
        })

    return threads_out


def write_thread_files(threads: list) -> list:
    """Write one .md file per thread, return list of (date, slug, subject, filepath)."""
    CORRESPONDENCE_DIR.mkdir(parents=True, exist_ok=True)
    index_entries = []

    for t in threads:
        # Parse first date for filename
        date_str = ""
        try:
            # Date header like "Thu, 5 Mar 2026 10:00:00 -0800"
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(t["first_date"])
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = "0000-00-00"

        slug = slugify(t["subject"])
        filename = f"{date_str}-{slug}.md"
        filepath = CORRESPONDENCE_DIR / filename

        # Build markdown
        lines = [
            "---",
            f'thread_id: "{t["thread_id"]}"',
            f'subject: "{t["subject"].replace(chr(34), chr(39))}"',
            f'participants: {json.dumps(t["participants"])}',
            f'first_message_date: "{t["first_date"]}"',
            f'last_message_date: "{t["last_date"]}"',
            f'message_count: {t["message_count"]}',
            "client: Fisch Group",
            "type: email-thread",
            "---",
            "",
            f"# {t['subject']}",
            "",
            f"**Thread ID**: `{t['thread_id']}`  ",
            f"**Messages**: {t['message_count']}  ",
            f"**Date range**: {t['first_date']} → {t['last_date']}  ",
            f"**Participants**: {', '.join(t['participants'])}",
            "",
            "---",
            "",
        ]

        for i, msg in enumerate(t["messages"], 1):
            lines.append(f"## Message {i}")
            lines.append(f"**From**: {msg['from']}  ")
            lines.append(f"**To**: {msg['to']}  ")
            lines.append(f"**Date**: {msg['date']}  ")
            lines.append("")
            body = msg["body"]
            if len(body) > 8000:
                body = body[:8000] + "\n\n[... truncated ...]"
            lines.append(body)
            lines.append("")
            lines.append("---")
            lines.append("")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        index_entries.append((date_str, slug, t["subject"], filename, t["message_count"]))
        print(f"    Wrote: {filename}")

    return index_entries


# ── Drive Transcripts ────────────────────────────────────────────────────────

def export_doc_as_text(drive, doc_id: str) -> str:
    """Export a Google Doc as plain text."""
    request = drive.files().export_media(fileId=doc_id, mimeType="text/plain")
    content = request.execute()
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return str(content)


def pull_transcripts(drive) -> list:
    """Pull all Fisch Group transcripts from Drive, return index entries."""
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    index_entries = []

    for date_str, info in TRANSCRIPT_DOC_IDS.items():
        doc_id = info["id"]
        slug = info["slug"]
        title = info["title"]
        filename = f"{date_str}-{slug}.md"
        filepath = TRANSCRIPTS_DIR / filename

        print(f"  Fetching transcript: {title}")
        try:
            content = export_doc_as_text(drive, doc_id)
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
            "client: Fisch Group",
            "type: meet-transcript",
            "---",
            "",
            f"# {title}",
            "",
            f"**Drive**: [{doc_id}]({drive_url})  ",
            f"**Date**: {date_str}  ",
            "",
            "---",
            "",
            content,
        ]
        filepath.write_text("\n".join(lines), encoding="utf-8")
        char_count = len(content)
        index_entries.append((date_str, slug, title, filename, char_count))
        print(f"    Wrote: {filename}  ({char_count:,} chars)")

    return index_entries


# ── Calendar ─────────────────────────────────────────────────────────────────

def pull_calendar_events(cal) -> list:
    """Pull Fish Group calendar events."""
    events_result = cal.events().list(
        calendarId="primary",
        timeMin="2026-02-15T00:00:00Z",
        timeMax="2026-04-10T00:00:00Z",
        maxResults=500,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    all_events = events_result.get("items", [])

    fish_events = []
    for ev in all_events:
        attendees = [a.get("email", "").lower() for a in ev.get("attendees", [])]
        title = ev.get("summary", "").lower()
        desc = ev.get("description", "").lower() if ev.get("description") else ""
        is_fish = (
            "mike@piermontbrands.com" in attendees
            or "ecaplow@fischgroup.com" in attendees
            or any(kw in title for kw in ["fisch", "fish", "piermont", "michael fisch"])
            or any(kw in desc for kw in ["fisch", "fish", "piermont", "michael fisch"])
        )
        if is_fish:
            fish_events.append(ev)

    return fish_events


def write_calendar_file(events: list) -> None:
    CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
    filepath = CALENDAR_DIR / "fish-group-meetings.md"

    lines = [
        "---",
        "client: Fisch Group",
        "type: calendar-events",
        "date_range: \"2026-02-15 to 2026-04-09\"",
        "---",
        "",
        "# Fish Group — All Calendar Events",
        "",
        f"*{len(events)} events pulled from greg@gbautomation.xyz calendar*",
        "",
        "---",
        "",
    ]

    for ev in events:
        start_raw = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))
        end_raw = ev.get("end", {}).get("dateTime", ev.get("end", {}).get("date", ""))
        start_pt = to_pt_str(start_raw)
        end_pt = to_pt_str(end_raw)

        # Duration
        duration_str = ""
        try:
            dt_start = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            dt_end = datetime.fromisoformat(end_raw.replace("Z", "+00:00"))
            mins = int((dt_end - dt_start).total_seconds() / 60)
            duration_str = f"{mins} min"
        except Exception:
            pass

        title = ev.get("summary", "(no title)")
        attendees = [a.get("email", "") for a in ev.get("attendees", [])]
        meet_link = ev.get("hangoutLink", "")
        description = ev.get("description", "") or ""
        event_id = ev.get("id", "")

        # Find matching transcript
        date_for_match = ""
        try:
            dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            dt_pt = dt.astimezone(PT)
            date_for_match = dt_pt.strftime("%Y-%m-%d")
        except Exception:
            pass

        transcript_link = ""
        if date_for_match in TRANSCRIPT_DOC_IDS:
            t = TRANSCRIPT_DOC_IDS[date_for_match]
            transcript_link = f"[Transcript]({TRANSCRIPTS_DIR}/{date_for_match}-{t['slug']}.md)"

        lines.append(f"## {start_pt} — {title}")
        lines.append("")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| Date (PT) | {start_pt} |")
        lines.append(f"| Duration | {duration_str} |")
        lines.append(f"| Attendees | {', '.join(attendees)} |")
        if meet_link:
            lines.append(f"| Meet Link | [{meet_link}]({meet_link}) |")
        if transcript_link:
            lines.append(f"| Transcript | {transcript_link} |")
        lines.append(f"| Event ID | `{event_id}` |")
        lines.append("")
        if description:
            lines.append("**Description:**")
            lines.append("")
            lines.append(description[:1000])
            lines.append("")
        lines.append("---")
        lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


# ── Index + Timeline ─────────────────────────────────────────────────────────

def write_correspondence_index(index_entries: list) -> None:
    """Write _INDEX.md for correspondence."""
    filepath = CORRESPONDENCE_DIR / "_INDEX.md"
    sorted_entries = sorted(index_entries, key=lambda x: x[0])

    lines = [
        "---",
        "type: index",
        "section: correspondence",
        "client: Fisch Group",
        "---",
        "",
        "# Fisch Group — Email Correspondence Index",
        "",
        f"*{len(sorted_entries)} threads pulled from greg@gbautomation.xyz*  ",
        f"*Date range: 2026-02-15 to 2026-04-09*",
        "",
        "| Date | Subject | Messages | File |",
        "|------|---------|----------|------|",
    ]
    for date_str, slug, subject, filename, msg_count in sorted_entries:
        lines.append(f"| {date_str} | {subject[:60]} | {msg_count} | [{filename}]({filename}) |")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


def write_transcripts_index(index_entries: list) -> None:
    """Write _INDEX.md for transcripts."""
    filepath = TRANSCRIPTS_DIR / "_INDEX.md"
    sorted_entries = sorted(index_entries, key=lambda x: x[0])

    existing_note = (
        "\n> **Note**: Sessions 1 (2026-03-05) and 2 (2026-03-12) also have handcrafted transcripts "
        "in `obsidian/intelligence/transcripts/`. The files here are raw Google Meet exports.\n"
    )

    lines = [
        "---",
        "type: index",
        "section: transcripts",
        "client: Fisch Group",
        "---",
        "",
        "# Fisch Group — Meet Transcript Index",
        "",
        existing_note,
        "",
        f"*{len(sorted_entries)} transcripts pulled from Google Drive*",
        "",
        "| Date | Session | Characters | File |",
        "|------|---------|------------|------|",
    ]
    for date_str, slug, title, filename, char_count in sorted_entries:
        lines.append(f"| {date_str} | {title[:60]} | {char_count:,} | [{filename}]({filename}) |")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


def write_master_timeline(
    thread_index: list,
    transcript_index: list,
    calendar_events: list,
) -> None:
    """Write the master _ENGAGEMENT_TIMELINE.md combining all touchpoints."""
    filepath = BASE / "_ENGAGEMENT_TIMELINE.md"

    # Build unified touchpoint list
    touchpoints = []

    for date_str, slug, subject, filename, msg_count in thread_index:
        touchpoints.append({
            "date": date_str,
            "type": "email",
            "summary": f"Email: {subject[:70]}",
            "link": f"correspondence/{filename}",
            "detail": f"{msg_count} message(s)",
        })

    for date_str, slug, title, filename, char_count in transcript_index:
        touchpoints.append({
            "date": date_str,
            "type": "transcript",
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
            date_str = "0000-00-00"
            time_str = ""

        title = ev.get("summary", "(no title)")
        meet_link = ev.get("hangoutLink", "")
        attendees = [a.get("email", "") for a in ev.get("attendees", [])]

        touchpoints.append({
            "date": date_str,
            "type": "meeting",
            "summary": f"Meeting: {title} @ {time_str}",
            "link": "calendar/fish-group-meetings.md",
            "detail": f"{', '.join(a for a in attendees if 'gbautomation' not in a)}",
        })

    touchpoints.sort(key=lambda x: x["date"])

    type_emoji = {
        "email": "[EMAIL]",
        "transcript": "[TRANSCRIPT]",
        "meeting": "[MEETING]",
    }

    lines = [
        "---",
        "client: Fisch Group",
        "type: engagement-timeline",
        "generated: \"2026-04-09\"",
        "---",
        "",
        "# Fisch Group — Master Engagement Timeline",
        "",
        "A chronological record of every touchpoint in the GBAutomation x Fisch Group engagement.",
        "Read this first to understand the full history.",
        "",
        "**Contacts**: Michael Fisch (mike@piermontbrands.com) · Emil Caplow (ecaplow@fischgroup.com)  ",
        "**Engagement start**: 2026-03-05  ",
        "**Status**: Active (weekly sessions ongoing)",
        "",
        "---",
        "",
        "## Quick Stats",
        "",
        f"- **Email threads**: {len(thread_index)}",
        f"- **Meet transcripts pulled**: {len(transcript_index)}",
        f"- **Calendar events**: {len(calendar_events)}",
        "",
        "### Sessions",
        "| Session | Date | Notes |",
        "|---------|------|-------|",
        "| 1 — Intake | 2026-03-05 | 60-min initial build session with Michael Fisch |",
        "| 2 — Weekly | 2026-03-12 | 45-min session, Emil joined, GitHub org created |",
        "| 3 — Weekly | 2026-03-19 | AI Session (transcript in Drive) |",
        "| 4 — Weekly | 2026-03-26 | AI Session (transcript in Drive) |",
        "| 5 — Weekly | 2026-04-02 | AI Session (transcript in Drive) |",
        "| 6 — Weekly | 2026-04-09 | AI Session (today, transcript TBD) |",
        "",
        "---",
        "",
        "## Chronological Touchpoints",
        "",
    ]

    current_month = ""
    for tp in touchpoints:
        month = tp["date"][:7] if tp["date"] else "Unknown"
        if month != current_month:
            current_month = month
            try:
                m_dt = datetime.strptime(month, "%Y-%m")
                lines.append(f"### {m_dt.strftime('%B %Y')}")
                lines.append("")
            except Exception:
                pass

        tag = type_emoji.get(tp["type"], "[?]")
        link = tp["link"]
        detail = tp["detail"]
        lines.append(f"- **{tp['date']}** {tag} [{tp['summary']}]({link}) — {detail}")

    lines.extend([
        "",
        "---",
        "",
        "## Intelligence Folders",
        "",
        "- [correspondence/](_INDEX_CORRESPONDENCE) — All Gmail threads (one file per thread)",
        "- [transcripts/](_INDEX_TRANSCRIPTS) — Google Meet transcript exports",
        "- [calendar/fish-group-meetings.md](calendar/fish-group-meetings.md) — All calendar events",
        "",
        "## Existing Second-Brain Files (Not Overwritten)",
        "",
        "- `obsidian/intelligence/transcripts/2026-03-05-session-1.md` — Handcrafted Session 1 notes",
        "- `obsidian/intelligence/transcripts/2026-03-12-session-2.md` — Handcrafted Session 2 notes",
        "- `obsidian/intelligence/decisions/2026-03-05-architecture.md` — Architecture decisions",
        "- `obsidian/agents/` — Agent definitions (finn.md, garys-cs.md, etc.)",
        "- `sessions/2026-03-05/` — Session 1 output files",
        "",
    ])

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("FISCH GROUP — FULL INTELLIGENCE PULL")
    print("=" * 60)

    gmail = google_client.gmail_service()
    drive = google_client.drive_service()
    cal = google_client.calendar_service()

    # Ensure output dirs exist
    BASE.mkdir(parents=True, exist_ok=True)

    # ── 1. Gmail ────────────────────────────────────────────────────────────
    print("\n[1/4] Pulling Gmail threads...")
    threads = pull_gmail_threads(gmail)
    print(f"  Processing {len(threads)} threads...")
    thread_index = write_thread_files(threads)
    write_correspondence_index(thread_index)
    print(f"  Done: {len(thread_index)} threads written")

    # ── 2. Transcripts ──────────────────────────────────────────────────────
    print("\n[2/4] Pulling Drive transcripts...")
    transcript_index = pull_transcripts(drive)
    write_transcripts_index(transcript_index)
    print(f"  Done: {len(transcript_index)} transcripts written")

    # ── 3. Calendar ─────────────────────────────────────────────────────────
    print("\n[3/4] Pulling Calendar events...")
    calendar_events = pull_calendar_events(cal)
    write_calendar_file(calendar_events)
    print(f"  Done: {len(calendar_events)} events written")

    # ── 4. Master timeline ──────────────────────────────────────────────────
    print("\n[4/4] Writing master timeline...")
    write_master_timeline(thread_index, transcript_index, calendar_events)

    print("\n" + "=" * 60)
    print("PULL COMPLETE")
    print(f"  Output: {BASE}")
    print(f"  Threads: {len(thread_index)}")
    print(f"  Transcripts: {len(transcript_index)}")
    print(f"  Calendar events: {len(calendar_events)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
