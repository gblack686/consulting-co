"""
Scope counter for Fisch Group engagement pull.
Counts Gmail threads, Drive files, and Calendar events before committing to full pull.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import google_client

QUERIES = [
    "from:mike@piermontbrands.com OR to:mike@piermontbrands.com",
    "from:ecaplow@fischgroup.com OR to:ecaplow@fischgroup.com",
    'subject:"Fish Group" OR subject:"Fisch Group" OR subject:"Piermont"',
    '"Fisch Group" OR "Fish Group" OR "Piermont Brands" OR "Chica Cheetah" OR "Drop Fitness" OR "clientflow-dashboard" OR "Finn" agent',
]

COMBINED_QUERY = (
    "after:2026/02/15 before:2026/04/10 "
    "("
    "from:mike@piermontbrands.com OR to:mike@piermontbrands.com OR "
    "from:ecaplow@fischgroup.com OR to:ecaplow@fischgroup.com OR "
    'subject:"Fisch Group" OR subject:"Fish Group" OR subject:"Piermont" OR '
    '"Fisch Group" OR "Fish Group" OR "Piermont Brands" OR "Chica Cheetah" OR "Drop Fitness" OR "clientflow" OR "Emilfisch"'
    ")"
)

DRIVE_QUERIES = [
    "fullText contains 'Fisch Group' or fullText contains 'Fish Group' or fullText contains 'Piermont'",
    "name contains 'Fisch' or name contains 'Fish Group' or name contains 'Piermont'",
    "sharedWith='mike@piermontbrands.com'",
    "sharedWith='ecaplow@fischgroup.com'",
]

CALENDAR_QUERY_EMAILS = ["mike@piermontbrands.com", "ecaplow@fischgroup.com"]


def count_gmail_threads():
    gmail = google_client.gmail_service()
    result = gmail.users().threads().list(
        userId="me",
        q=COMBINED_QUERY,
        maxResults=500,
    ).execute()
    threads = result.get("threads", [])
    next_page = result.get("nextPageToken")
    count = len(threads)
    # get a second page if there is one
    if next_page:
        result2 = gmail.users().threads().list(
            userId="me",
            q=COMBINED_QUERY,
            maxResults=500,
            pageToken=next_page,
        ).execute()
        count += len(result2.get("threads", []))
        if result2.get("nextPageToken"):
            count = f"{count}+ (more pages exist)"
    return count, threads[:20]  # return first 20 thread snippets for preview


def count_drive_files():
    drive = google_client.drive_service()
    counts = {}

    # Search by name patterns
    name_queries = [
        ("name:fisch/fish/piermont", "name contains 'Fisch' or name contains 'Fish' or name contains 'Piermont' or name contains 'Finn'"),
    ]
    for label, q in name_queries:
        r = drive.files().list(
            q=q + " and trashed=false",
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            pageSize=100,
            corpora="user",
            includeItemsFromAllDrives=False,
        ).execute()
        counts[label] = r.get("files", [])

    # Search Meet Recordings folder
    # First find "Meet Recordings" folder
    meet_folder = drive.files().list(
        q="name = 'Meet Recordings' and mimeType = 'application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)",
        pageSize=10,
    ).execute()
    meet_folders = meet_folder.get("files", [])
    counts["meet_recording_folders"] = meet_folders

    meet_files = []
    for mf in meet_folders:
        r = drive.files().list(
            q=f"'{mf['id']}' in parents and trashed=false",
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            pageSize=200,
            orderBy="modifiedTime desc",
        ).execute()
        meet_files.extend(r.get("files", []))
    counts["meet_recording_files_total"] = len(meet_files)
    # Filter for fish group related
    fish_meet_files = [
        f for f in meet_files
        if any(kw in f["name"].lower() for kw in ["fisch", "fish", "piermont", "michael", "mike", "emil"])
    ]
    counts["meet_files_fish_filtered"] = fish_meet_files

    # Also check all files modified in date range with Meet/transcript keywords
    transcript_q = (
        "mimeType = 'application/vnd.google-apps.document' and "
        "name contains 'Transcript' and trashed=false and "
        "modifiedTime > '2026-02-15T00:00:00' and modifiedTime < '2026-04-10T00:00:00'"
    )
    tr = drive.files().list(
        q=transcript_q,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        pageSize=200,
        orderBy="modifiedTime desc",
    ).execute()
    counts["transcript_docs_in_range"] = tr.get("files", [])

    return counts


def count_calendar_events():
    cal = google_client.calendar_service()
    # List all events in range
    events_result = cal.events().list(
        calendarId="primary",
        timeMin="2026-02-15T00:00:00Z",
        timeMax="2026-04-10T00:00:00Z",
        maxResults=500,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    all_events = events_result.get("items", [])

    # Filter for fish group attendees or keywords
    fish_events = []
    for ev in all_events:
        attendees = [a.get("email", "").lower() for a in ev.get("attendees", [])]
        title = ev.get("summary", "").lower()
        desc = ev.get("description", "").lower() if ev.get("description") else ""
        is_fish = (
            "mike@piermontbrands.com" in attendees
            or "ecaplow@fischgroup.com" in attendees
            or any(kw in attendees_str for kw in ["fischgroup", "piermontbrands"] for attendees_str in attendees)
            or any(kw in title for kw in ["fisch", "fish", "piermont", "michael fisch"])
            or any(kw in desc for kw in ["fisch", "fish", "piermont", "michael fisch"])
        )
        if is_fish:
            fish_events.append(ev)

    return fish_events, len(all_events)


def main():
    print("=" * 60)
    print("FISCH GROUP ENGAGEMENT — SCOPE COUNT")
    print("=" * 60)

    print("\n--- Gmail ---")
    try:
        thread_count, sample_threads = count_gmail_threads()
        print(f"Matching threads: {thread_count}")
        print("Sample thread subjects:")
        for t in sample_threads[:10]:
            snippet = t.get("snippet", "")[:80]
            print(f"  [{t['id']}] {snippet}")
    except Exception as e:
        print(f"Gmail error: {e}")
        thread_count = "ERROR"

    print("\n--- Google Drive ---")
    try:
        drive_counts = count_drive_files()
        print(f"Files matching name (Fisch/Fish/Piermont/Finn): {len(drive_counts.get('name:fisch/fish/piermont', []))}")
        for f in drive_counts.get("name:fisch/fish/piermont", []):
            print(f"  {f['name']}  ({f['mimeType'].split('.')[-1]})  {f.get('modifiedTime', '')[:10]}")

        print(f"\nMeet Recordings folders found: {len(drive_counts.get('meet_recording_folders', []))}")
        for mf in drive_counts.get("meet_recording_folders", []):
            print(f"  Folder: {mf['name']} ({mf['id']})")
        print(f"Total files in Meet Recordings: {drive_counts.get('meet_recording_files_total', 0)}")
        print(f"Meet files matching Fish Group keywords: {len(drive_counts.get('meet_files_fish_filtered', []))}")
        for f in drive_counts.get("meet_files_fish_filtered", []):
            print(f"  {f['name']}  {f.get('modifiedTime', '')[:10]}  {f.get('webViewLink', '')}")

        print(f"\nTranscript docs in date range (all): {len(drive_counts.get('transcript_docs_in_range', []))}")
        for f in drive_counts.get("transcript_docs_in_range", []):
            print(f"  {f['name']}  {f.get('modifiedTime', '')[:10]}  {f.get('webViewLink', '')}")
    except Exception as e:
        print(f"Drive error: {e}")
        import traceback; traceback.print_exc()

    print("\n--- Google Calendar ---")
    try:
        fish_events, total_events = count_calendar_events()
        print(f"Total events in range (Feb 15 - Apr 9): {total_events}")
        print(f"Fish Group / Piermont events: {len(fish_events)}")
        for ev in fish_events:
            start = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))[:16]
            title = ev.get("summary", "(no title)")
            attendees = [a.get("email", "") for a in ev.get("attendees", [])]
            meet_link = ev.get("hangoutLink", "")
            print(f"  {start}  |  {title}")
            print(f"    Attendees: {', '.join(attendees)}")
            if meet_link:
                print(f"    Meet: {meet_link}")
    except Exception as e:
        print(f"Calendar error: {e}")
        import traceback; traceback.print_exc()

    print("\n" + "=" * 60)
    print("SCOPE SUMMARY")
    print("=" * 60)


if __name__ == "__main__":
    main()
