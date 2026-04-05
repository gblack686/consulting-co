"""
Setup OAuth token for gblack686@gmail.com personal calendar
=============================================================
One-time script. Reuses the same Google Cloud OAuth client credentials
stored in the workspace god token, but authenticates as gblack686@gmail.com.

Uses InstalledAppFlow.run_local_server() — opens browser, spins up a local
HTTP server on a random port to catch the redirect, no manual code needed.

Stores result to:
  AWS Secret: gbautomation/google/personal-calendar-token

Usage:
    python -m scripts.setup_personal_calendar_auth
"""
import boto3
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
GOD_TOKEN_SECRET = "gbautomation/google/workspace-god-token"
PERSONAL_TOKEN_SECRET = "gbautomation/google/personal-calendar-token"
REGION = "us-east-1"

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]


def run():
    from google_auth_oauthlib.flow import InstalledAppFlow

    sm = boto3.client("secretsmanager", region_name=REGION)
    god = json.loads(sm.get_secret_value(SecretId=GOD_TOKEN_SECRET)["SecretString"])

    client_config = {
        "installed": {
            "client_id": god["client_id"],
            "client_secret": god["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": god.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": ["http://localhost"],
        }
    }

    print("\n" + "="*60)
    print("  Personal Calendar OAuth Setup")
    print("  Account: gblack686@gmail.com")
    print("  → Browser will open. Log in as gblack686@gmail.com and allow access.")
    print("="*60 + "\n")

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(
        port=0,  # pick a random free port
        authorization_prompt_message="Opening browser...\n",
        success_message="Auth complete! You can close this tab.",
        open_browser=True,
    )

    print(f"\n  ✓ Token obtained")
    print(f"  Refresh token: {creds.refresh_token[:20]}...")

    payload = {
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    }

    try:
        sm.create_secret(
            Name=PERSONAL_TOKEN_SECRET,
            Description="OAuth refresh token for gblack686@gmail.com personal calendar",
            SecretString=json.dumps(payload),
        )
        print(f"  ✓ Secret created: {PERSONAL_TOKEN_SECRET}")
    except sm.exceptions.ResourceExistsException:
        sm.put_secret_value(
            SecretId=PERSONAL_TOKEN_SECRET,
            SecretString=json.dumps(payload),
        )
        print(f"  ✓ Secret updated: {PERSONAL_TOKEN_SECRET}")

    print("\n  Done! Running create_booking_page.py now...\n")
    return True


if __name__ == "__main__":
    import os
    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))
    run()
