"""
Re-authorize the GBAutomation workspace god token with expanded scopes.
=======================================================================
Opens browser for OAuth consent, then updates the AWS secret with
the new refresh token covering all scopes.

Usage:
    python -m scripts.reauth_god_token

Account: greg@gbautomation.xyz
"""
import boto3
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
GOD_TOKEN_SECRET = "gbautomation/google/workspace-god-token"
REGION = "us-east-1"

# Comprehensive scopes for all GBAutomation Google Workspace skills
SCOPES = [
    # Gmail
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    # Drive
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    # Sheets
    "https://www.googleapis.com/auth/spreadsheets",
    # Docs
    "https://www.googleapis.com/auth/documents",
    # Slides
    "https://www.googleapis.com/auth/presentations",
    # Calendar
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    # Contacts / People
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/directory.readonly",
    # Tasks
    "https://www.googleapis.com/auth/tasks",
    # Admin
    "https://www.googleapis.com/auth/admin.directory.customer.readonly",
    "https://www.googleapis.com/auth/admin.directory.domain.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
    "https://www.googleapis.com/auth/admin.reports.usage.readonly",
    # Meet
    "https://www.googleapis.com/auth/meetings.space.readonly",
    "https://www.googleapis.com/auth/meetings.space.created",
    # Forms
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    # Chat
    "https://www.googleapis.com/auth/chat.messages",
    "https://www.googleapis.com/auth/chat.spaces.readonly",
    # Apps Script
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/script.deployments",
]


def run():
    from google_auth_oauthlib.flow import InstalledAppFlow

    sm = boto3.client("secretsmanager", region_name=REGION)
    god = json.loads(sm.get_secret_value(SecretId=GOD_TOKEN_SECRET)["SecretString"])

    print("\n" + "=" * 60)
    print("  GBAutomation God Token Re-Authorization")
    print("  Account: greg@gbautomation.xyz")
    print(f"  Scopes: {len(SCOPES)} (was {len(god.get('scopes', []))})")
    print()
    print("  NEW scopes being added:")
    existing = set(god.get("scopes", []))
    for s in sorted(SCOPES):
        if s not in existing:
            print(f"    + {s}")
    print()
    print("  → Browser will open. Log in as greg@gbautomation.xyz")
    print("=" * 60 + "\n")

    client_config = {
        "installed": {
            "client_id": god["client_id"],
            "client_secret": god["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": god.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(
        port=0,
        authorization_prompt_message="Opening browser...\n",
        success_message="Auth complete! You can close this tab.",
        open_browser=True,
    )

    print(f"\n  Token obtained")
    print(f"  Refresh token: {creds.refresh_token[:20]}...")
    print(f"  Scopes granted: {len(creds.scopes) if creds.scopes else len(SCOPES)}")

    payload = {
        "account": "greg@gbautomation.xyz",
        "type": "authorized_user",
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    }

    sm.put_secret_value(
        SecretId=GOD_TOKEN_SECRET,
        SecretString=json.dumps(payload),
    )
    print(f"  Secret updated: {GOD_TOKEN_SECRET}")
    print("\n  Done! All GWS skills now have full access.\n")
    return True


if __name__ == "__main__":
    import os
    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))
    run()
