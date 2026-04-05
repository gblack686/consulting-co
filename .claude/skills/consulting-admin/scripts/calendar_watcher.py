"""
Calendar Watcher
=================
Scans greg@gbautomation.xyz calendar for upcoming booked calls.
Booking page: https://calendar.app.google/suUCCrvV7aDnwLzZA  (AI Discovery Call)

For each new event:
  - Extracts attendee name + email (skips Greg's own accounts)
  - Checks if they already have a client folder in Drive
  - If new client → runs full onboarding (new_client.py) automatically
  - Sends Telegram notification either way

State file: state/calendar_watcher.json  (tracks processed event IDs)

Usage:
    python -m scripts.calendar_watcher
    python -m scripts.calendar_watcher --dry-run
    python -m scripts.calendar_watcher --days 14   # look ahead 14 days (default: 7)
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
STATE_FILE = SKILL_ROOT / "state" / "calendar_watcher.json"

# Keywords that identify a booked client call (case-insensitive, any match)
# Primary: "60 Minute Agent Build with Greg" booking page
# Legacy: older vibe coding / build session titles
CALL_KEYWORDS = [
    "agent build",
    "60 minute agent build",
    "vibe coding", "vibe-coding", "coding call", "build session",
]

# Duration range for qualifying events (minutes) — 60 min build session
DURATION_MIN = 50
DURATION_MAX = 70

# Greg's own emails to skip when scanning attendees
GREG_EMAILS = {"greg@gbautomation.xyz", "gblack686@gmail.com"}


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"processed_event_ids": []}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# Calendar helpers
# ─────────────────────────────────────────────────────────────────────────────

def _event_duration_minutes(event: dict) -> int | None:
    """Return event duration in minutes, or None if all-day/can't parse."""
    start = event.get("start", {})
    end = event.get("end", {})
    if "dateTime" not in start or "dateTime" not in end:
        return None
    try:
        s = datetime.fromisoformat(start["dateTime"])
        e = datetime.fromisoformat(end["dateTime"])
        return int((e - s).total_seconds() / 60)
    except Exception:
        return None


def _is_vibe_coding_call(event: dict) -> bool:
    title = event.get("summary", "").lower()
    return any(kw in title for kw in CALL_KEYWORDS)


def _get_client_attendees(event: dict) -> list[dict]:
    """Return list of {name, email} for non-Greg attendees."""
    attendees = []
    for a in event.get("attendees", []):
        email = a.get("email", "").lower()
        if email in GREG_EMAILS:
            continue
        if a.get("resource"):  # skip conference rooms
            continue
        name = a.get("displayName") or email.split("@")[0].replace(".", " ").title()
        attendees.append({"name": name, "email": email})
    return attendees


# ─────────────────────────────────────────────────────────────────────────────
# Client existence check
# ─────────────────────────────────────────────────────────────────────────────

def _client_folder_exists(client_name: str, client_email: str) -> bool:
    """
    Check if this person already has a folder under GBAutomation Clients/.
    Matches by folder name (client_name) OR by checking if email is a known sharer.
    """
    from . import google_client, drive_manager

    drive = google_client.drive_service()
    root_id = drive_manager.get_root_folder_id()

    # Check by name match
    q = (
        f"name='{client_name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"'{root_id}' in parents and trashed=false"
    )
    resp = drive.files().list(q=q, fields="files(id, name)").execute()
    if resp.get("files"):
        return True

    # Also check partial name match (first name only)
    first_name = client_name.split()[0]
    q2 = (
        f"name contains '{first_name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"'{root_id}' in parents and trashed=false"
    )
    resp2 = drive.files().list(q=q2, fields="files(id, name)").execute()
    if resp2.get("files"):
        return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run(dry_run: bool = False, days_ahead: int = 7):
    from . import google_client, telegram_client
    from .new_client import run as onboard_client

    state = load_state()
    processed = set(state.get("processed_event_ids", []))

    cal = google_client.calendar_service()

    now = datetime.now(timezone.utc)
    time_max = now + timedelta(days=days_ahead)

    print(f"\n{'='*60}")
    print(f"  CALENDAR WATCHER — {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Looking ahead: {days_ahead} days")
    print(f"  Already processed: {len(processed)} event(s)")
    if dry_run:
        print(f"  Mode: DRY RUN")
    print(f"{'='*60}\n")

    # Fetch upcoming events
    resp = cal.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=time_max.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=100,
    ).execute()

    events = resp.get("items", [])
    print(f"[1/3] Fetched {len(events)} upcoming event(s)\n")

    qualifying = []
    for event in events:
        if event["id"] in processed:
            continue
        duration = _event_duration_minutes(event)
        if duration is None:
            continue
        if not (DURATION_MIN <= duration <= DURATION_MAX):
            continue
        if not _is_vibe_coding_call(event):
            continue
        qualifying.append(event)

    print(f"[2/3] Found {len(qualifying)} new qualifying vibe coding call(s)\n")

    if not qualifying:
        state["processed_event_ids"] = list(processed)
        save_state(state)
        print("  Nothing to action. Done.\n")
        return

    for event in qualifying:
        title = event.get("summary", "(untitled)")
        start_dt = event.get("start", {}).get("dateTime", "")
        duration = _event_duration_minutes(event)
        attendees = _get_client_attendees(event)

        print(f"  Event: \"{title}\"")
        print(f"  When:  {start_dt}  ({duration} min)")
        print(f"  Attendees: {[a['email'] for a in attendees]}")

        if not attendees:
            print(f"  ⚠ No non-Greg attendees found — skipping\n")
            processed.add(event["id"])
            continue

        for attendee in attendees:
            name = attendee["name"]
            email = attendee["email"]

            is_existing = _client_folder_exists(name, email)
            status = "EXISTING CLIENT" if is_existing else "NEW CLIENT"
            print(f"\n  [{status}] {name} <{email}>")

            if is_existing:
                msg = (
                    f"📅 <b>Vibe Coding Call Scheduled</b>\n"
                    f"<b>Client:</b> {name} ({email})\n"
                    f"<b>When:</b> {start_dt}\n"
                    f"<b>Note:</b> Existing client — no onboarding needed"
                )
                if not dry_run:
                    telegram_client.send(msg)
                    print(f"  ✓ Telegram sent (existing client notice)")
                else:
                    print(f"  [DRY RUN] Telegram → existing client notice")

            else:
                msg = (
                    f"🆕 <b>New Client Call Detected!</b>\n"
                    f"<b>Name:</b> {name}\n"
                    f"<b>Email:</b> {email}\n"
                    f"<b>Call:</b> {title}\n"
                    f"<b>When:</b> {start_dt}\n"
                    f"Running onboarding now..."
                )
                if not dry_run:
                    telegram_client.send(msg)

                print(f"  → Running new_client onboarding for {name}...")
                if not dry_run:
                    try:
                        result = onboard_client(
                            client_name=name,
                            client_email=email,
                            draft=False,  # send immediately
                        )
                        done_msg = (
                            f"✅ <b>Onboarding Complete</b>\n"
                            f"<b>Client:</b> {name}\n"
                            f"<b>Folder:</b> {result.get('folder_url', '')}\n"
                            f"Welcome email sent!"
                        )
                        telegram_client.send(done_msg)
                        print(f"  ✓ Onboarding complete. Folder: {result.get('folder_url')}")
                    except Exception as e:
                        err_msg = f"⚠️ <b>Onboarding failed for {name}</b>\n{e}"
                        telegram_client.send(err_msg)
                        print(f"  ✗ Onboarding error: {e}")
                else:
                    print(f"  [DRY RUN] Would onboard {name} <{email}>")

        processed.add(event["id"])
        print()

    print(f"[3/3] Saving state...")
    state["processed_event_ids"] = list(processed)
    if not dry_run:
        save_state(state)

    print(f"\n{'='*60}")
    print(f"  DONE — processed {len(qualifying)} event(s)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import os

    parser = argparse.ArgumentParser(description="Watch calendar for vibe coding calls")
    parser.add_argument("--dry-run", action="store_true",
                        help="Check only — no onboarding or Telegram messages")
    parser.add_argument("--days", type=int, default=7,
                        help="How many days ahead to scan (default: 7)")
    args = parser.parse_args()

    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))

    run(dry_run=args.dry_run, days_ahead=args.days)
