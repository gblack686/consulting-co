"""
Create Google Calendar Appointment Schedule (Booking Page)
===========================================================
Creates a "60 Min Agent Build with Greg" booking page on the
gblack686@gmail.com calendar using the Calendar API v3.

Requires a separate OAuth token for gblack686@gmail.com stored in:
  AWS Secret: gbautomation/google/personal-calendar-token
  Fields: refresh_token, token_uri, client_id, client_secret, scopes

Usage:
    python -m scripts.create_booking_page
    python -m scripts.create_booking_page --dry-run
"""
import argparse
import boto3
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent

PERSONAL_SECRET_ID = "gbautomation/google/personal-calendar-token"


def get_personal_calendar_service():
    """Build a Calendar service for gblack686@gmail.com."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    sm = boto3.client("secretsmanager", region_name="us-east-1")
    secret = json.loads(sm.get_secret_value(SecretId=PERSONAL_SECRET_ID)["SecretString"])

    creds = Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        token_uri=secret["token_uri"],
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=secret["scopes"],
    )
    creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)


def create_booking_page(dry_run: bool = False) -> str:
    """
    Create the 60 Min Agent Build with Greg appointment schedule.
    Returns the booking URL.
    """
    cal = get_personal_calendar_service()

    body = {
        "name": "60 Min Agent Build with Greg",
        "description": (
            "Book a 60-minute hands-on AI agent build session with Greg Black at GBAutomation. "
            "We'll scope your use case, map out your workflows, and start building your custom AI system."
        ),
        "duration": "3600s",  # 60 minutes
        "schedulingWindow": {
            "startTime": {"hours": 9, "minutes": 0},
            "endTime": {"hours": 17, "minutes": 0},
        },
        "weeklySchedule": {
            "daysOfWeek": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
        },
        "bookingType": "BOOKING_WITH_FORM",
        "guestFields": [
            {"field": "FIRST_NAME", "required": True},
            {"field": "LAST_NAME", "required": True},
            {"field": "EMAIL", "required": True},
        ],
        "organizerBio": "Greg Black — AI Automation Consultant at GBAutomation",
    }

    if dry_run:
        print("  [DRY RUN] Would create appointment schedule:")
        print(json.dumps(body, indent=2))
        return "(dry run — no URL created)"

    result = cal.appointmentSchedules().create(
        calendarId="primary",
        body=body,
    ).execute()

    booking_url = result.get("bookingUrl") or result.get("selfLink", "")
    schedule_id = result.get("id", "")

    print(f"  ✓ Appointment schedule created")
    print(f"  ID:  {schedule_id}")
    print(f"  URL: {booking_url}")

    return booking_url


if __name__ == "__main__":
    import os

    parser = argparse.ArgumentParser(description="Create GBAutomation booking page")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))

    url = create_booking_page(dry_run=args.dry_run)
    print(f"\nBooking URL: {url}")
