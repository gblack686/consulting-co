"""
Poll the Social Media Recon Tracker sheet for NEW research jobs.

Diff-based: tracks previously seen slugs in a state file. Any new row
that appears in the sheet gets processed automatically — no Status column needed.

Run on a schedule (OpenClaw heartbeat, Task Scheduler, or cron):
    python poll_recon_sheet.py
    python poll_recon_sheet.py --dry-run

Architecture:
  Google Sheet (Greg adds a row)
    → This poller (detects new rows via diff)
      → POST to Sebastian Listen API (Tailscale)
        → Sebastian runs social-media-recon skill
          → Results saved to gbauto/pbauer/{slug}/
          → Telegram summary sent back
"""
import sys, os, json, argparse
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "consulting-admin"))
from scripts import google_client

# Mac Mini Listen API (Tailscale IP)
SEBASTIAN_URL = "http://100.88.4.114:7600"
DEFAULT_SHEET_ID = "1QnCKwahlaUV-gi31d4NZmKk7nxrtkJQA4rOs8paH-pA"

# State file — tracks which slugs have been processed
STATE_DIR = Path(__file__).parent / "state"
STATE_FILE = STATE_DIR / "processed_slugs.json"

# Sheet layout: A:Name B:Slug C:Instagram D:LinkedIn E:Facebook F:Status G:Updated H:Notes
SHEET_RANGE = "'Persona Reports'!A2:L100"
STATUS_RANGE_TEMPLATE = "'Persona Reports'!F{row}:G{row}"

COL_NAME = 0
COL_SLUG = 1
COL_INSTAGRAM = 2
COL_LINKEDIN = 3
COL_FACEBOOK = 4
COL_STATUS = 5
COL_UPDATED = 6
COL_NOTES = 7
COL_DRIVE_FOLDER = 11


def load_processed() -> dict:
    """Load set of already-processed slugs with metadata."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_processed(state: dict):
    """Persist processed slugs."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def read_all_rows(sheet_id: str) -> list[dict]:
    """Read all data rows from the sheet."""
    sheets = google_client.sheets_service()
    result = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=SHEET_RANGE,
    ).execute()

    rows = result.get("values", [])
    entries = []

    for i, row in enumerate(rows):
        while len(row) < 12:
            row.append("")

        name = row[COL_NAME].strip()
        slug = row[COL_SLUG].strip()
        if not name and not slug:
            continue  # skip empty rows

        # Auto-generate slug from name if missing
        if not slug:
            slug = name.lower().replace(" ", "-")

        entries.append({
            "row_num": i + 2,  # 1-indexed, skip header
            "name": name,
            "slug": slug,
            "instagram": row[COL_INSTAGRAM].strip(),
            "linkedin": row[COL_LINKEDIN].strip(),
            "facebook": row[COL_FACEBOOK].strip(),
            "status": row[COL_STATUS].strip(),
            "notes": row[COL_NOTES].strip(),
            "drive_folder": row[COL_DRIVE_FOLDER].strip(),
        })

    return entries


def find_new_rows(entries: list[dict], processed: dict) -> list[dict]:
    """Return rows that haven't been processed yet."""
    return [e for e in entries if e["slug"] not in processed]


def update_status(sheet_id: str, row_num: int, status: str):
    """Update the Status and Last Updated columns for a row."""
    sheets = google_client.sheets_service()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=STATUS_RANGE_TEMPLATE.format(row=row_num),
        valueInputOption="RAW",
        body={"values": [[status, now]]},
    ).execute()


def build_prompt(entry: dict) -> str:
    """Build the research prompt for Sebastian."""
    parts = [f"Run social media recon on {entry['name']}."]
    parts.append(f"Save all output to gbauto/pbauer/{entry['slug']}/.")

    platforms = []
    if entry["instagram"]:
        platforms.append(f"Instagram: {entry['instagram']}")
    if entry["facebook"]:
        platforms.append(f"Facebook: {entry['facebook']}")
    if entry["linkedin"]:
        platforms.append(f"LinkedIn: {entry['linkedin']}")

    if platforms:
        parts.append("Platforms to research: " + ", ".join(platforms))
    else:
        parts.append("No handles provided — search for their profiles by name.")

    if entry["drive_folder"]:
        parts.append(f"Upload all report PPTXs to the client's Drive Research folder: {entry['drive_folder']}")
        parts.append("Make each uploaded file publicly readable (anyone with link).")

    if entry["notes"]:
        parts.append(f"Notes: {entry['notes']}")

    parts.append("Use the social-media-recon skill.")
    parts.append("Send me a Telegram summary when done with public Drive links to each report.")

    return " ".join(parts)


def fire_job(prompt: str, dry_run: bool = False) -> str | None:
    """Send a research job to Sebastian via Listen API."""
    if dry_run:
        print(f"  [DRY RUN] Would POST to {SEBASTIAN_URL}/job")
        print(f"  Prompt: {prompt[:150]}...")
        return "dry-run"

    try:
        resp = requests.post(
            f"{SEBASTIAN_URL}/job",
            json={"prompt": prompt},
            timeout=10,
        )
        resp.raise_for_status()
        job = resp.json()
        job_id = job.get("id") or job.get("job_id", "unknown")
        print(f"  Job submitted: {job_id}")
        return job_id
    except requests.ConnectionError:
        print(f"  ERROR: Cannot reach Sebastian at {SEBASTIAN_URL}")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Poll recon sheet for new jobs")
    parser.add_argument("--sheet-id", default=DEFAULT_SHEET_ID, help="Google Spreadsheet ID")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen")
    parser.add_argument("--reset", action="store_true", help="Clear processed state and re-scan")
    args = parser.parse_args()

    if args.reset:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        print("State reset. All rows will be treated as new.")

    processed = load_processed()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Polling sheet ({len(processed)} previously processed)")

    entries = read_all_rows(args.sheet_id)
    new_rows = find_new_rows(entries, processed)

    if not new_rows:
        print("No new rows. Nothing to do.")
        return

    print(f"Found {len(new_rows)} new row(s):")

    for entry in new_rows:
        name = entry["name"]
        print(f"\n  [{entry['row_num']}] {name} ({entry['slug']})")

        has_handles = entry["instagram"] or entry["facebook"] or entry["linkedin"]
        if not has_handles and not entry["notes"]:
            print(f"  SKIP: No handles and no notes.")
            processed[entry["slug"]] = {
                "name": name,
                "skipped": True,
                "reason": "no handles",
                "seen_at": datetime.now().isoformat(),
            }
            continue

        prompt = build_prompt(entry)
        job_id = fire_job(prompt, dry_run=args.dry_run)

        if job_id:
            if not args.dry_run:
                update_status(args.sheet_id, entry["row_num"], "researching")
                print(f"  Status -> researching")
            processed[entry["slug"]] = {
                "name": name,
                "job_id": job_id,
                "fired_at": datetime.now().isoformat(),
            }
        else:
            if not args.dry_run:
                update_status(args.sheet_id, entry["row_num"], "error")
                print(f"  Status -> error")

    save_processed(processed)
    print(f"\nDone. State saved ({len(processed)} total processed).")


if __name__ == "__main__":
    main()
