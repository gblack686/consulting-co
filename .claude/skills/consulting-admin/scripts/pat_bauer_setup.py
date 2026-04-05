"""
One-shot setup for Pat Bauer discovery call.
Tasks:
1. Search Gmail + Contacts for Pat Bauer / acquisition.com / acquisition.ai
2. Create Google Meet / Calendar event (March 8 2026, 12pm PT / 3pm ET, 60 min)
3. Create Drive folders: GBAutomation Clients / Pat Bauer - Acquisition.com / Pat Bauer — Session 2026-03-08
4. Draft welcome email (or fill placeholder if email not found)
"""

import sys
import json
from datetime import datetime, timezone, timedelta

# Ensure the package root is on the path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import google_client
from scripts.drive_manager import get_or_create_folder, get_root_folder_id, get_folder_url


# ── 1. Gmail search ──────────────────────────────────────────────────────────

def search_gmail_for_pat():
    gmail = google_client.gmail_service()
    queries = [
        "Pat Bauer",
        "acquisition.com",
        "acquisition.ai",
        "patbauer",
        "pat.bauer",
    ]
    found = {}
    for q in queries:
        for scope in [f'from:({q})', f'to:({q})']:
            results = gmail.users().messages().list(
                userId="me", q=scope, maxResults=10
            ).execute()
            msgs = results.get("messages", [])
            if msgs:
                for m in msgs[:3]:
                    msg = gmail.users().messages().get(
                        userId="me", id=m["id"], format="metadata",
                        metadataHeaders=["From", "To", "Subject", "Date"]
                    ).execute()
                    headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
                    key = headers.get("From", "") + headers.get("To", "")
                    if key not in found:
                        found[key] = {
                            "from": headers.get("From", ""),
                            "to": headers.get("To", ""),
                            "subject": headers.get("Subject", ""),
                            "date": headers.get("Date", ""),
                            "query": q,
                        }
    return list(found.values())


# ── 2. Contacts search ───────────────────────────────────────────────────────

def search_contacts_for_pat():
    from googleapiclient.discovery import build
    creds = google_client.get_credentials()
    people = build("people", "v1", credentials=creds)
    results = people.people().searchContacts(
        query="Pat Bauer",
        readMask="names,emailAddresses,organizations",
        pageSize=10,
    ).execute()
    contacts = []
    for r in results.get("results", []):
        p = r.get("person", {})
        names = [n.get("displayName", "") for n in p.get("names", [])]
        emails = [e.get("value", "") for e in p.get("emailAddresses", [])]
        orgs = [o.get("name", "") for o in p.get("organizations", [])]
        contacts.append({"names": names, "emails": emails, "orgs": orgs})
    # Also search acquisition.com
    results2 = people.people().searchContacts(
        query="acquisition",
        readMask="names,emailAddresses,organizations",
        pageSize=20,
    ).execute()
    for r in results2.get("results", []):
        p = r.get("person", {})
        emails = [e.get("value", "") for e in p.get("emailAddresses", [])]
        orgs = [o.get("name", "") for o in p.get("organizations", [])]
        # Only include if email or org mentions acquisition
        if any("acquisition" in e.lower() for e in emails + orgs):
            names = [n.get("displayName", "") for n in p.get("names", [])]
            contacts.append({"names": names, "emails": emails, "orgs": orgs})
    return contacts


# ── 3. Calendar event with Meet ──────────────────────────────────────────────

def create_calendar_event():
    cal = google_client.calendar_service()

    # March 8 2026 12:00 PM PT = UTC-8 (PST)
    start_pt = "2026-03-08T12:00:00-08:00"
    end_pt   = "2026-03-08T13:00:00-08:00"

    event_body = {
        "summary": "AI Discovery Call - Pat Bauer x GBAutomation",
        "description": (
            "60-minute AI discovery call with Pat Bauer from Acquisition.com.\n\n"
            "Agenda: Discuss how AI can streamline prospect research workflows — "
            "sourcing and personalizing insights from LinkedIn, Instagram, and social media "
            "to enhance client experiences at acquisition.com's day-long sales intensives."
        ),
        "start": {
            "dateTime": start_pt,
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": end_pt,
            "timeZone": "America/Los_Angeles",
        },
        "attendees": [
            {"email": "greg@gbautomation.xyz", "organizer": True},
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": "pat-bauer-20260308",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 60},
                {"method": "popup", "minutes": 15},
            ],
        },
    }

    event = cal.events().insert(
        calendarId="primary",
        body=event_body,
        conferenceDataVersion=1,
        sendUpdates="none",
    ).execute()

    meet_link = ""
    conf = event.get("conferenceData", {})
    for ep in conf.get("entryPoints", []):
        if ep.get("entryPointType") == "video":
            meet_link = ep.get("uri", "")
            break

    return {
        "event_id": event["id"],
        "event_link": event.get("htmlLink", ""),
        "meet_link": meet_link,
        "start": event["start"]["dateTime"],
        "end": event["end"]["dateTime"],
    }


# ── 4. Drive folders ─────────────────────────────────────────────────────────

def create_drive_folders():
    root_id = get_root_folder_id()
    client_folder_id = get_or_create_folder("Pat Bauer - Acquisition.com", parent_id=root_id)
    session_folder_id = get_or_create_folder("Pat Bauer \u2014 Session 2026-03-08", parent_id=client_folder_id)
    return {
        "root_id": root_id,
        "client_folder_id": client_folder_id,
        "client_folder_url": get_folder_url(client_folder_id),
        "session_folder_id": session_folder_id,
        "session_folder_url": get_folder_url(session_folder_id),
    }


# ── 5. Draft email ───────────────────────────────────────────────────────────

def create_email_draft(pat_email: str, meet_link: str, session_folder_url: str):
    from scripts.gmail_client import create_draft

    subject = "AI Discovery Call - Tomorrow 12pm PT"

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; line-height: 1.6;">

  <p>Hey Pat,</p>

  <p>Really looking forward to our call tomorrow at <strong>12:00 PM Pacific (3:00 PM Eastern)</strong>.</p>

  <p>We'll be talking through how AI can help streamline your prospect research workflow — specifically pulling together and personalizing insights from LinkedIn, Instagram, and social media to enhance the client experience at your day-long sales intensives.</p>

  <p><strong>Join here:</strong><br/>
  <a href="{meet_link}" style="color: #D97757;">{meet_link}</a></p>

  <p>No prep needed — just bring your curiosity. If you want to think ahead of time, the main question I'll want to explore with you is: <em>what does the prospect research process currently look like before an intensive, and where does it feel manual or inconsistent?</em></p>

  <p>See you tomorrow,</p>

  <p>
    <strong>Greg Black</strong><br/>
    GBAutomation<br/>
    <a href="mailto:greg@gbautomation.xyz">greg@gbautomation.xyz</a><br/>
    <a href="https://gbautomation.xyz">gbautomation.xyz</a>
  </p>

</body>
</html>
"""

    text = f"""Hey Pat,

Really looking forward to our call tomorrow at 12:00 PM Pacific (3:00 PM Eastern).

We'll be talking through how AI can help streamline your prospect research workflow — specifically pulling together and personalizing insights from LinkedIn, Instagram, and social media to enhance the client experience at your day-long sales intensives.

Join here: {meet_link}

No prep needed — just bring your curiosity. If you want to think ahead of time, the main question I'll want to explore with you is: what does the prospect research process currently look like before an intensive, and where does it feel manual or inconsistent?

See you tomorrow,

Greg Black
GBAutomation
greg@gbautomation.xyz
gbautomation.xyz
"""

    draft_id = create_draft(
        to=pat_email,
        subject=subject,
        body_html=html,
        body_text=text,
    )
    return draft_id


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== Step 1: Searching Gmail for Pat Bauer / acquisition.com ===")
    gmail_hits = search_gmail_for_pat()
    if gmail_hits:
        print(f"  Found {len(gmail_hits)} email thread(s):")
        for h in gmail_hits:
            print(f"    FROM: {h['from']}")
            print(f"    TO:   {h['to']}")
            print(f"    SUBJ: {h['subject']}")
            print(f"    DATE: {h['date']}")
            print(f"    QUERY: {h['query']}")
            print()
    else:
        print("  No prior email correspondence found.")

    print("\n=== Step 2: Searching Contacts for Pat Bauer / acquisition ===")
    pat_email_found = None
    try:
        contacts = search_contacts_for_pat()
        if contacts:
            print(f"  Found {len(contacts)} contact(s):")
            for c in contacts:
                print(f"    Name(s):  {c['names']}")
                print(f"    Email(s): {c['emails']}")
                print(f"    Org(s):   {c['orgs']}")
                print()
                for name in c["names"]:
                    if "pat" in name.lower() or "bauer" in name.lower():
                        if c["emails"]:
                            pat_email_found = c["emails"][0]
        else:
            print("  No contacts found.")
    except Exception as e:
        contacts = []
        print(f"  Contacts search skipped (People API not enabled): {e}")

    print("\n=== Step 3: Creating Google Calendar event with Meet ===")
    cal_result = create_calendar_event()
    print(f"  Event created: {cal_result['event_link']}")
    print(f"  Google Meet:   {cal_result['meet_link']}")
    print(f"  Start:         {cal_result['start']}")

    print("\n=== Step 4: Creating Drive folders ===")
    drive_result = create_drive_folders()
    print(f"  Client folder:  {drive_result['client_folder_url']}")
    print(f"  Session folder: {drive_result['session_folder_url']}")

    print("\n=== Step 5: Drafting email ===")
    # Use found email or placeholder
    pat_email = pat_email_found or "PLACEHOLDER@acquisition.com"
    draft_id = create_email_draft(
        pat_email=pat_email,
        meet_link=cal_result["meet_link"],
        session_folder_url=drive_result["session_folder_url"],
    )
    print(f"  Draft created (ID: {draft_id})")
    print(f"  Draft to: {pat_email}")
    if not pat_email_found:
        print("  NOTE: Pat's email was NOT found — draft is addressed to placeholder. Update before sending.")

    print("\n=== SUMMARY ===")
    print(json.dumps({
        "gmail_hits": len(gmail_hits),
        "contacts_found": len(contacts),
        "pat_email_found": pat_email_found,
        "meet_link": cal_result["meet_link"],
        "calendar_event": cal_result["event_link"],
        "client_folder_url": drive_result["client_folder_url"],
        "session_folder_url": drive_result["session_folder_url"],
        "draft_id": draft_id,
        "draft_to": pat_email,
    }, indent=2))
