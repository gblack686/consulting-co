"""
Meet Transcript Agent
=====================
Watches for Google Meet transcript emails, fetches the full transcript,
pipes it to Claude CLI for issue extraction + action items, then drafts
a send-ready reply via Gmail.

Can run standalone or be called from email_watcher as a handler.

Usage:
    # Process a specific conference record
    python -m scripts.transcript_agent --conference "conferenceRecords/ID"

    # Watch inbox for transcript emails (poll mode)
    python -m scripts.transcript_agent --watch

    # Dry run (print what would happen, don't draft)
    python -m scripts.transcript_agent --watch --dry-run
"""
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
STATE_FILE = SKILL_ROOT / "state" / "transcript_agent.json"
LOG_DIR = SKILL_ROOT / "logs"

# Patterns that identify a transcript email
TRANSCRIPT_SENDERS = [
    "meet-recordings-noreply@google.com",
    "calendar-notification@google.com",
]
TRANSCRIPT_SUBJECT_PATTERNS = [
    r"transcript",
    r"meeting\s+notes",
    r"recording\s+ready",
]

CLIENT_SESSIONS_DIR = SKILL_ROOT.parent / "consulting-intake" / "client-sessions"

CLAUDE_SYSTEM_PROMPT = r"""You are Greg Black's executive assistant at GBAutomation (greg@gbautomation.xyz).
You have received a Google Meet transcript from a client consulting session.

You must produce TWO sections separated by the exact delimiter ===EMAIL_SEPARATOR===

SECTION 1: Internal analysis (for Greg only, saved to a log file).
SECTION 2: The client-facing follow-up email body (plain text, ready to send).

Rules for the internal analysis (Section 1):
- Use the exact markdown headers shown in the example below.
- In "Action Items", group by owner (Greg, Client, other stakeholders) using checkboxes.
- In "Claude/Automation BUILD Items", extract EVERY mention of Claude, AI, agent, automation,
  skill, or workflow in the context of something TO BUILD or TO DO as a concrete todo.
  Format: - [ ] BUILD: {description of what to build/automate}
- In "Issues & Blockers", list anything blocking progress.
- In "Next Meeting", extract scheduling details ONLY if a specific next meeting was
  discussed in the transcript. Use this exact format:
  - Date: {YYYY-MM-DD or "TBD" or day of week like "next Thursday"}
  - Time: {HH:MM in PT or "TBD"}
  - Duration: {minutes, default 60}
  - Topic: {what the next session will focus on}
  If NO next meeting was discussed at all, write "None discussed" on a single line.
  Do NOT invent or assume a next meeting — only extract what was actually said.

Rules for the email (Section 2):
- Write as Greg Black. First person. Professional but warm.
- Reference specific topics discussed in the call — never be generic.
- Include a bulleted list of action items with owners (Greg vs client).
- If deadlines were discussed, include them.
- Close with next steps and an invitation to reply with questions.
- Do NOT include any agent metadata, system notes, or formatting tags.
- Do NOT include "Subject:" — that is handled separately.
- Do NOT mention AI, agents, automation of this email, or anything that reveals this was machine-generated.
- Sign off as:
  Greg Black
  GBAutomation
  greg@gbautomation.xyz

If the transcript mentions technical issues or products you're unsure about,
use web search to verify current information before including it in the email.

Example output structure:

## Meeting Summary
- Client: Acme Corp (Jane Smith)
- Date: 2026-03-11
- Duration: ~45 min
- Attendees: Jane Smith, Greg Black

## Key Discussion Points
- Migrating from manual spreadsheet tracking to automated pipeline
- Concerns about data privacy with third-party integrations

## Action Items
- [ ] Greg — send API documentation for the webhook integration
- [ ] Client — provide access to their staging environment by Friday
- [ ] Greg — draft architecture diagram for the proposed system

## Claude/Automation BUILD Items
- [ ] BUILD: Automated data pipeline from Shopify to warehouse
- [ ] BUILD: Scheduled daily report skill for inventory levels

## Issues & Blockers
- Client's IT team needs to whitelist our IP range before we can test

## Next Meeting
- Date: 2026-03-18
- Time: 14:00 PT
- Duration: 60
- Topic: Review webhook integration and test staging environment

## Email Subject
Follow-Up: Agent Pipeline Architecture & Next Steps

===EMAIL_SEPARATOR===

Hi Jane,

Great speaking with you today — really productive session...

[rest of email body]

Greg Black
GBAutomation
greg@gbautomation.xyz"""


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"processed_conferences": [], "processed_email_ids": []}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def fetch_transcript_entries(conference_name: str) -> list[dict]:
    """Fetch all transcript entries for a conference via Meet API."""
    from . import google_client
    svc = google_client.meet_service()

    transcripts = svc.conferenceRecords().transcripts().list(
        parent=conference_name
    ).execute().get("transcripts", [])

    if not transcripts:
        return []

    all_entries = []
    for t in transcripts:
        page_token = None
        while True:
            kwargs = {"parent": t["name"], "pageSize": 100}
            if page_token:
                kwargs["pageToken"] = page_token
            resp = svc.conferenceRecords().transcripts().entries().list(**kwargs).execute()
            all_entries.extend(resp.get("transcriptEntries", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    return all_entries


def fetch_transcript_from_docs(transcripts: list[dict]) -> str:
    """Fetch transcript text from the Google Docs export URI."""
    from . import google_client
    drive = google_client.drive_service()

    texts = []
    for t in transcripts:
        docs_dest = t.get("docsDestination", {})
        doc_uri = docs_dest.get("exportUri", "")
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", doc_uri)
        if not match:
            doc = docs_dest.get("document")
            if doc:
                match = re.search(r"/d/([a-zA-Z0-9_-]+)", doc)
        if match:
            file_id = match.group(1)
            content = drive.files().export(fileId=file_id, mimeType="text/plain").execute()
            texts.append(content.decode("utf-8"))

    return "\n\n---\n\n".join(texts)


def entries_to_text(entries: list[dict]) -> str:
    """Convert transcript entries to readable text."""
    lines = []
    for e in entries:
        ts = e.get("startTime", "")
        time_part = ts[11:19] if len(ts) > 19 else ts
        speaker = e.get("participantName", e.get("participant", "Unknown"))
        text = e.get("text", "")
        lines.append(f"[{time_part}] {speaker}: {text}")
    return "\n".join(lines)


def get_conference_transcript(conference_name: str) -> str:
    """Get transcript text, trying entries first, then Docs export."""
    from . import google_client
    svc = google_client.meet_service()

    transcripts = svc.conferenceRecords().transcripts().list(
        parent=conference_name
    ).execute().get("transcripts", [])

    if not transcripts:
        return ""

    entries = fetch_transcript_entries(conference_name)
    if entries:
        return entries_to_text(entries)

    return fetch_transcript_from_docs(transcripts)


def pipe_to_claude(transcript_text: str, dry_run: bool = False) -> dict:
    """Send transcript to Claude CLI. Returns {"analysis": str, "subject": str, "email_body": str}."""
    if dry_run:
        return {
            "analysis": f"[DRY RUN] Would send {len(transcript_text)} chars to Claude CLI",
            "subject": "[DRY RUN] Subject",
            "email_body": "[DRY RUN] Email body",
        }

    prompt = f"Analyze this Google Meet transcript and produce the requested output.\n\n<transcript>\n{transcript_text}\n</transcript>"

    try:
        result = subprocess.run(
            [
                "claude", "-p",
                "--model", "sonnet",
                "--allowedTools", "WebSearch,WebFetch",
                "--system-prompt", CLAUDE_SYSTEM_PROMPT,
                "--no-session-persistence",
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=180,
            env={**__import__("os").environ,
                 "CLAUDECODE": "",
                 "ANTHROPIC_API_KEY": "",
                 "CLAUDE_CODE_OAUTH_TOKEN": ""},
        )
        if result.returncode != 0:
            return {"analysis": f"[ERROR] Claude CLI failed: {result.stderr[:500]}",
                    "subject": "", "email_body": ""}
    except subprocess.TimeoutExpired:
        return {"analysis": "[ERROR] Claude CLI timed out after 180s",
                "subject": "", "email_body": ""}
    except FileNotFoundError:
        return {"analysis": "[ERROR] Claude CLI not found in PATH",
                "subject": "", "email_body": ""}

    raw = result.stdout.strip()
    return parse_claude_output(raw)


def parse_claude_output(raw: str) -> dict:
    """Split Claude's output into analysis + email sections."""
    parts = raw.split("===EMAIL_SEPARATOR===", 1)

    analysis = parts[0].strip()

    # Extract subject from analysis section
    subject_match = re.search(r"## Email Subject\s*\n(.+)", analysis)
    subject = subject_match.group(1).strip() if subject_match else "Follow-Up: Meeting Notes & Action Items"

    email_body = parts[1].strip() if len(parts) > 1 else ""

    return {
        "analysis": analysis,
        "subject": subject,
        "email_body": email_body,
    }


def extract_client_name_from_analysis(analysis: str) -> str | None:
    """Extract client name from the Meeting Summary section."""
    match = re.search(r"##\s*Meeting Summary.*?Client:\s*(.+?)(?:\n|$)", analysis, re.DOTALL)
    if match:
        # "Acme Corp (Jane Smith)" -> "Acme Corp" or "Emil Fisch (Fish Group)" -> client name
        raw = match.group(1).strip()
        # Remove parenthetical and markdown bold markers
        raw = re.sub(r"\s*\(.*?\)\s*", " ", raw).strip()
        raw = raw.strip("*").strip()
        return raw
    return None


def extract_client_slug(analysis: str) -> str | None:
    """Derive a slug from the client name in the analysis."""
    name = extract_client_name_from_analysis(analysis)
    if name:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return None


def generate_analysis_md(analysis: str, subject: str, email_body: str,
                         source_info: str = "") -> Path:
    """Save structured analysis markdown to the client's session folder or logs fallback.
    Returns the path of the saved file."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_compact = datetime.now().strftime("%Y%m%d")
    slug = extract_client_slug(analysis)

    # Try client-sessions folder first
    saved_path = None
    if slug and CLIENT_SESSIONS_DIR.exists():
        # Find existing session folder for this client + date
        for d in CLIENT_SESSIONS_DIR.iterdir():
            if d.is_dir() and slug.split("-")[0] in d.name.lower():
                session_output = d / "session_output"
                session_output.mkdir(exist_ok=True)
                saved_path = session_output / f"session-report-{today}.md"
                break

        # Create new session folder if none found
        if not saved_path:
            session_dir = CLIENT_SESSIONS_DIR / f"{today_compact}-{slug}"
            session_output = session_dir / "session_output"
            session_output.mkdir(parents=True, exist_ok=True)
            saved_path = session_output / f"session-report-{today}.md"

    # Fallback to logs
    if not saved_path:
        LOG_DIR.mkdir(exist_ok=True)
        safe_slug = slug or "unknown"
        saved_path = LOG_DIR / f"transcript_{safe_slug}_{today_compact}_analysis.md"

    content = (
        f"# Session Report — {today}\n\n"
        f"**Source:** {source_info}\n"
        f"**Processed:** {datetime.now().isoformat()}\n"
        f"**Email Subject:** {subject}\n\n"
        f"---\n\n"
        f"{analysis}\n\n"
        f"---\n\n"
        f"## Email Draft\n\n{email_body}"
    )
    saved_path.write_text(content, encoding="utf-8")
    print(f"  Analysis saved to: {saved_path}")
    return saved_path


def upload_analysis_to_drive(analysis_path: Path, client_name: str = None,
                             dry_run: bool = False) -> str | None:
    """Upload the analysis MD to Google Drive under the client's session folder.
    Returns the web view link or None."""
    if dry_run:
        print("  [DRY RUN] Would upload analysis to Drive")
        return None

    try:
        from . import google_client
        from .upload_session_to_drive import get_or_create_folder, upload_file

        drive = google_client.drive_service()
        today = datetime.now().strftime("%Y-%m-%d")

        # Navigate to GBAutomation Clients / {client} / {client} — Session {date}
        root_id = get_or_create_folder(drive, "GBAutomation Clients")
        display_name = client_name or "Unknown Client"
        client_id = get_or_create_folder(drive, display_name, root_id)
        session_folder_name = f"{display_name} — Session {today}"
        session_id = get_or_create_folder(drive, session_folder_name, client_id)

        file_id = upload_file(drive, analysis_path, session_id)

        # Get the web view link
        meta = drive.files().get(fileId=file_id, fields="webViewLink").execute()
        link = meta.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")
        print(f"  Uploaded to Drive: {link}")
        return link
    except Exception as e:
        print(f"  Drive upload failed: {e}")
        return None


def inject_drive_link(email_body: str, drive_link: str) -> str:
    """Insert a session notes link before the sign-off in the email body."""
    sign_off = "Greg Black\nGBAutomation\ngreg@gbautomation.xyz"
    citation = f"You can view the full session notes here: {drive_link}\n\n"
    if sign_off in email_body:
        return email_body.replace(sign_off, citation + sign_off)
    # Fallback: append before last paragraph
    return email_body.rstrip() + "\n\n" + citation.rstrip() + "\n\n" + sign_off


def extract_action_items(analysis: str) -> dict[str, list[str]]:
    """Parse action items from analysis, grouped by owner.
    Returns {"Greg": [...], "Client": [...], "Other": [...]}."""
    items: dict[str, list[str]] = {"Greg": [], "Client": [], "Other": []}
    current_owner = None

    in_action_section = False
    for line in analysis.splitlines():
        stripped = line.strip()
        # Detect "## Action Items" section
        if re.match(r"^##\s*Action Items", stripped, re.IGNORECASE):
            in_action_section = True
            continue
        # Exit on next ## header
        if in_action_section and stripped.startswith("## "):
            break
        if not in_action_section:
            continue

        # Detect owner headers like "**Greg:**" or "Greg:" or "**Emil:**"
        owner_match = re.match(r"^\*{0,2}(\w[\w\s]*?)\s*(?:\(.*?\))?\s*:?\*{0,2}\s*:?\s*$", stripped)
        if owner_match and not stripped.startswith("- "):
            name = owner_match.group(1).strip()
            if "greg" in name.lower():
                current_owner = "Greg"
            elif name.lower() in ("client",):
                current_owner = "Client"
            else:
                # First non-Greg owner is the client, rest are other stakeholders
                if not items["Client"]:
                    current_owner = "Client"
                else:
                    current_owner = "Other"
            continue

        # Detect checkbox items
        item_match = re.match(r"^-\s*\[.\]\s*(.+)", stripped)
        if item_match and current_owner:
            items[current_owner].append(item_match.group(1).strip())

    return items


def extract_build_items(analysis: str) -> list[str]:
    """Extract BUILD items from the Claude/Automation BUILD Items section."""
    items = []
    in_build_section = False
    for line in analysis.splitlines():
        stripped = line.strip()
        if re.match(r"^##\s*Claude/Automation BUILD Items", stripped, re.IGNORECASE):
            in_build_section = True
            continue
        if in_build_section and stripped.startswith("## "):
            break
        if not in_build_section:
            continue
        item_match = re.match(r"^-\s*\[.\]\s*(?:BUILD:\s*)?(.+)", stripped)
        if item_match:
            items.append(item_match.group(1).strip())
    return items


def create_tasks_from_analysis(analysis: str, client_name: str = None,
                                dry_run: bool = False) -> str | None:
    """Create a Google Tasks list from the extracted action items.
    Returns the task list ID or None."""
    if dry_run:
        print("  [DRY RUN] Would create Google Tasks from action items")
        return None

    action_items = extract_action_items(analysis)
    build_items = extract_build_items(analysis)

    greg_items = action_items.get("Greg", [])
    # BUILD items are also Greg's responsibility
    for bi in build_items:
        greg_items.append(f"BUILD: {bi}")

    if not greg_items:
        print("  No action items found for Greg — skipping task creation")
        return None

    try:
        from . import google_client
        tasks_svc = google_client.tasks_service()

        today = datetime.now().strftime("%Y-%m-%d")
        display_name = client_name or "Client"
        list_title = f"{display_name} — Session {today}"

        # Create the task list
        task_list = tasks_svc.tasklists().insert(body={"title": list_title}).execute()
        list_id = task_list["id"]
        print(f"  Created task list: {list_title} ({list_id})")

        # Add each item as a task
        for item in greg_items:
            tasks_svc.tasks().insert(
                tasklist=list_id,
                body={"title": item, "status": "needsAction"},
            ).execute()

        print(f"  Added {len(greg_items)} tasks")
        return list_id
    except Exception as e:
        print(f"  Task creation failed: {e}")
        return None


def extract_next_meeting(analysis: str) -> dict | None:
    """Parse the ## Next Meeting section from the analysis.
    Returns {"date": str, "time": str, "duration": int, "topic": str} or None."""
    in_section = False
    fields = {}
    for line in analysis.splitlines():
        stripped = line.strip()
        if re.match(r"^##\s*Next Meeting", stripped, re.IGNORECASE):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue
        # "None discussed" means no meeting
        if "none discussed" in stripped.lower():
            return None
        # Parse "- Date: 2026-04-09" or "- Time: 14:00 PT"
        m = re.match(r"^-\s*(Date|Time|Duration|Topic)\s*:\s*(.+)", stripped, re.IGNORECASE)
        if m:
            fields[m.group(1).lower()] = m.group(2).strip()

    if not fields or not fields.get("date"):
        return None
    # Skip if date is TBD
    if "tbd" in fields.get("date", "").lower():
        return None

    return {
        "date": fields.get("date", ""),
        "time": fields.get("time", "TBD"),
        "duration": int(fields.get("duration", "60")),
        "topic": fields.get("topic", "Follow-up session"),
    }


def resolve_meeting_date(date_str: str) -> datetime | None:
    """Parse a date string into a datetime. Handles YYYY-MM-DD and relative
    day names like 'next Thursday', 'Wednesday'."""
    from datetime import timedelta
    # Try YYYY-MM-DD first
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    # Try relative day names: "next Thursday", "Thursday", "next week"
    day_names = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
    }
    lower = date_str.lower().replace("next ", "")
    for name, dow in day_names.items():
        if name in lower:
            today = datetime.now()
            days_ahead = dow - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
    return None


def create_followup_event(analysis: str, client_name: str = None,
                          client_email: str = None,
                          dry_run: bool = False) -> str | None:
    """Create a calendar event from the ## Next Meeting section of the analysis.
    Only creates an event if concrete meeting details were extracted.
    Returns the event HTML link or None."""
    meeting = extract_next_meeting(analysis)
    if not meeting:
        print("  No next meeting details found — skipping calendar event")
        return None

    meeting_date = resolve_meeting_date(meeting["date"])
    if not meeting_date:
        print(f"  Could not parse meeting date '{meeting['date']}' — skipping")
        return None

    if dry_run:
        print(f"  [DRY RUN] Would create calendar event: {meeting['topic']} on {meeting_date.strftime('%Y-%m-%d')}")
        return None

    try:
        from . import google_client
        from datetime import timedelta
        cal = google_client.calendar_service()

        display_name = client_name or "Client"
        duration = meeting["duration"]

        # Parse time if provided, default to 1pm PT
        hour, minute = 13, 0
        if meeting["time"].lower() != "tbd":
            time_match = re.match(r"(\d{1,2}):(\d{2})", meeting["time"])
            if time_match:
                hour, minute = int(time_match.group(1)), int(time_match.group(2))

        start_dt = meeting_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        end_dt = start_dt + timedelta(minutes=duration)

        event_body = {
            "summary": f"{display_name} — {meeting['topic']}",
            "description": (
                f"Follow-up from {datetime.now().strftime('%Y-%m-%d')} session.\n"
                f"Topic: {meeting['topic']}"
            ),
            "start": {
                "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "America/Los_Angeles",
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": f"transcript-agent-{datetime.now().strftime('%Y%m%d')}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                },
            },
        }

        if client_email:
            event_body["attendees"] = [
                {"email": client_email},
                {"email": "greg@gbautomation.xyz"},
            ]

        event = cal.events().insert(
            calendarId="primary",
            body=event_body,
            conferenceDataVersion=1,
        ).execute()

        link = event.get("htmlLink", "")
        print(f"  Calendar event created: {meeting_date.strftime('%Y-%m-%d')} {hour}:{minute:02d} PT — {link}")
        return link
    except Exception as e:
        print(f"  Calendar event creation failed: {e}")
        return None


def draft_reply(original_msg_id: str, subject: str, email_body: str,
                client_email: str = None, dry_run: bool = False) -> str:
    """Create a send-ready Gmail draft. Threads to original if replying."""
    if dry_run:
        return "[DRY RUN] Would create Gmail draft"

    from . import gmail_client

    # Build simple HTML from plain text (preserve paragraphs)
    paragraphs = email_body.split("\n\n")
    html_parts = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Detect bullet lists
        if p.startswith("- ") or p.startswith("* "):
            items = re.split(r"\n[-*] ", "\n" + p)
            li_tags = "".join(f"<li>{item.strip()}</li>" for item in items if item.strip())
            html_parts.append(f"<ul>{li_tags}</ul>")
        else:
            html_parts.append(f"<p>{p.replace(chr(10), '<br>')}</p>")

    body_html = "\n".join(html_parts)

    if original_msg_id:
        # Threaded reply
        draft_id = gmail_client.create_draft(
            to=client_email or "",
            subject=subject,
            body_html=body_html,
            body_text=email_body,
            reply_to_message_id=original_msg_id,
        )
    else:
        # Standalone draft (for --conference mode)
        draft_id = gmail_client.create_draft(
            to=client_email or "",
            subject=subject,
            body_html=body_html,
            body_text=email_body,
        )
    return draft_id


def is_transcript_email(headers: dict, snippet: str) -> bool:
    """Check if an email is a Meet transcript notification."""
    sender = headers.get("From", "").lower()
    subject = headers.get("Subject", "").lower()

    for s in TRANSCRIPT_SENDERS:
        if s in sender:
            return True

    for pat in TRANSCRIPT_SUBJECT_PATTERNS:
        if re.search(pat, subject, re.IGNORECASE):
            return True

    return False


def extract_conference_id(msg_body: str) -> str | None:
    """Try to extract a conference record ID from email body."""
    match = re.search(r"conferenceRecords/([a-zA-Z0-9_-]+)", msg_body)
    if match:
        return f"conferenceRecords/{match.group(1)}"

    meet_match = re.search(r"meet\.google\.com/([a-z]{3}-[a-z]{4}-[a-z]{3})", msg_body)
    if meet_match:
        return meet_match.group(1)

    return None


def extract_client_email(headers: dict, body_text: str) -> str | None:
    """Try to determine the client's email from the transcript email context."""
    # The transcript email itself is from Google, so check for participant
    # emails in the body or other headers
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", body_text)
    for email in emails:
        email_lower = email.lower()
        if email_lower not in ("greg@gbautomation.xyz", "gblack686@gmail.com",
                               "meet-recordings-noreply@google.com",
                               "calendar-notification@google.com"):
            return email
    return None


def handle_transcript_email(msg_id: str, headers: dict, body_text: str,
                            dry_run: bool = False) -> bool:
    """Process a single transcript email. Called by email_watcher or watch_inbox.
    Returns True if processed successfully."""
    subject = headers.get("Subject", "(no subject)")
    print(f"\n{'='*60}")
    print(f"Processing transcript email: {subject}")
    print(f"{'='*60}")

    # Try to get the transcript text
    conference_id = extract_conference_id(body_text)
    transcript_text = ""

    if conference_id:
        print(f"  Found conference: {conference_id}")
        transcript_text = get_conference_transcript(conference_id)

    if not transcript_text:
        doc_match = re.search(r"docs\.google\.com/document/d/([a-zA-Z0-9_-]+)", body_text)
        if doc_match:
            from .fetch_transcript import fetch_transcript
            transcript_text = fetch_transcript(doc_match.group(1))

    if not transcript_text:
        transcript_text = f"[Email subject: {subject}]\n\n{body_text}"

    print(f"  Transcript length: {len(transcript_text)} chars")

    # Pipe to Claude for analysis
    print("  Sending to Claude for analysis...")
    result = pipe_to_claude(transcript_text, dry_run=dry_run)

    # Generate structured analysis markdown
    analysis_path = generate_analysis_md(
        analysis=result["analysis"],
        subject=result["subject"],
        email_body=result["email_body"],
        source_info=f"Email: {subject}",
    )

    # Upload analysis to Google Drive
    client_name = extract_client_name_from_analysis(result["analysis"])
    drive_link = upload_analysis_to_drive(
        analysis_path, client_name=client_name, dry_run=dry_run,
    )

    # Create Google Tasks from action items
    task_list_id = create_tasks_from_analysis(
        result["analysis"], client_name=client_name, dry_run=dry_run,
    )

    # Create follow-up calendar event if mentioned
    client_email = extract_client_email(headers, body_text)
    calendar_link = create_followup_event(
        result["analysis"], client_name=client_name,
        client_email=client_email, dry_run=dry_run,
    )

    # Draft the send-ready reply (with Drive link if available)
    if result["email_body"] and not result["email_body"].startswith("["):
        email_body = result["email_body"]
        if drive_link:
            email_body = inject_drive_link(email_body, drive_link)

        try:
            draft_id = draft_reply(
                original_msg_id=msg_id,
                subject=result["subject"],
                email_body=email_body,
                client_email=client_email,
                dry_run=dry_run,
            )
            print(f"  Gmail draft created: {draft_id}")
            if client_email:
                print(f"  To: {client_email}")
        except Exception as e:
            print(f"  Draft creation failed: {e}")

    # Notify via Telegram
    try:
        from . import telegram_client
        extras = []
        if drive_link:
            extras.append(f"<b>Drive:</b> <a href=\"{drive_link}\">Session Notes</a>")
        if task_list_id:
            extras.append(f"<b>Tasks:</b> {task_list_id}")
        if calendar_link:
            extras.append(f"<b>Calendar:</b> <a href=\"{calendar_link}\">Follow-up event</a>")
        extras_str = "\n".join(extras) if extras else "<b>Drive:</b> N/A"

        telegram_client.send(
            f"📋 <b>Meet Transcript Processed</b>\n"
            f"<b>Subject:</b> {html.escape(subject)}\n"
            f"<b>Transcript:</b> {len(transcript_text)} chars\n"
            f"<b>Analysis:</b> {analysis_path.name}\n"
            f"{extras_str}\n"
            f"{'[DRY RUN]' if dry_run else '📝 Draft ready — check Gmail drafts'}"
        )
    except Exception:
        pass

    return True


def watch_inbox(dry_run: bool = False):
    """Poll inbox for transcript emails and process them."""
    from . import google_client

    state = load_state()
    processed_ids = set(state.get("processed_email_ids", []))

    gmail = google_client.gmail_service()

    query = "from:meet-recordings-noreply@google.com OR subject:transcript OR subject:recording"
    results = gmail.users().messages().list(
        userId="me", q=query, maxResults=20,
    ).execute()

    processed_count = 0
    for meta in results.get("messages", []):
        if meta["id"] in processed_ids:
            continue

        msg = gmail.users().messages().get(
            userId="me", id=meta["id"], format="full",
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}

        if not is_transcript_email(headers, msg.get("snippet", "")):
            processed_ids.add(meta["id"])
            continue

        # Extract full body text
        import base64
        body_text = msg.get("snippet", "")
        parts = msg["payload"].get("parts", [])
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    break

        handle_transcript_email(meta["id"], headers, body_text, dry_run=dry_run)

        processed_ids.add(meta["id"])
        processed_count += 1

    state["processed_email_ids"] = list(processed_ids)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {processed_count} transcript(s) processed")


def process_conference(conference_name: str, dry_run: bool = False):
    """Process a specific conference record directly."""
    print(f"Fetching transcript for {conference_name}...")
    transcript_text = get_conference_transcript(conference_name)

    if not transcript_text:
        print("No transcript found for this conference.")
        return

    print(f"Transcript: {len(transcript_text)} chars")
    print("Sending to Claude for analysis...")

    result = pipe_to_claude(transcript_text, dry_run=dry_run)

    # Generate structured analysis markdown
    analysis_path = generate_analysis_md(
        analysis=result["analysis"],
        subject=result["subject"],
        email_body=result["email_body"],
        source_info=f"Conference: {conference_name}",
    )

    # Upload to Drive
    client_name = extract_client_name_from_analysis(result["analysis"])
    drive_link = upload_analysis_to_drive(
        analysis_path, client_name=client_name, dry_run=dry_run,
    )

    # Create Google Tasks from action items
    task_list_id = create_tasks_from_analysis(
        result["analysis"], client_name=client_name, dry_run=dry_run,
    )

    # Create follow-up calendar event if mentioned
    calendar_link = create_followup_event(
        result["analysis"], client_name=client_name, dry_run=dry_run,
    )

    print(f"\n{result['analysis']}")
    print(f"\n{'='*60}")
    print(f"DRAFT EMAIL (Subject: {result['subject']})")
    print(f"{'='*60}")
    email_body = result["email_body"]
    if drive_link:
        email_body = inject_drive_link(email_body, drive_link)
    print(email_body)

    print(f"\n{'='*60}")
    print("POST-PROCESSING RESULTS")
    print(f"{'='*60}")
    print(f"  Analysis: {analysis_path}")
    if drive_link:
        print(f"  Drive:    {drive_link}")
    if task_list_id:
        print(f"  Tasks:    {task_list_id}")
    if calendar_link:
        print(f"  Calendar: {calendar_link}")


if __name__ == "__main__":
    import argparse
    import os

    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))

    parser = argparse.ArgumentParser(description="Meet Transcript Agent")
    parser.add_argument("--watch", action="store_true", help="Watch inbox for transcript emails")
    parser.add_argument("--conference", type=str, help="Process a specific conference record")
    parser.add_argument("--dry-run", action="store_true", help="Don't create drafts or call Claude")
    args = parser.parse_args()

    if args.conference:
        process_conference(args.conference, dry_run=args.dry_run)
    elif args.watch:
        watch_inbox(dry_run=args.dry_run)
    else:
        parser.print_help()
