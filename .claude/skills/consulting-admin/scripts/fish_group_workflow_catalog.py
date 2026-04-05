"""
One-off script: Fish Group Workflow Catalog
- Task 1: Create Google Doc in GBAutomation Clients / Fish Group / Fish Group — Session 2026-03-12 / deliverables/
- Task 2: Share doc with mike@piermontbrands.com (editor)
- Task 3: Draft Gmail to mike@piermontbrands.com with doc link inserted
"""
import sys
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Auth (inline, no module import needed) ---
import boto3
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SECRET_ID = "gbautomation/google/workspace-god-token"
REGION = "us-east-1"


def get_credentials():
    client = boto3.client("secretsmanager", region_name=REGION)
    resp = client.get_secret_value(SecretId=SECRET_ID)
    secret = json.loads(resp["SecretString"])
    creds = Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        token_uri=secret["token_uri"],
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=secret["scopes"],
    )
    creds.refresh(Request())
    return creds


def get_or_create_folder(drive, name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = drive.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def build_doc_requests(content: str):
    """
    Convert markdown content into Google Docs API batchUpdate requests.
    Handles headings, bold, checkboxes, horizontal rules, and paragraph structure.
    Returns a list of requests to insert styled text.
    """
    import re

    requests = []
    lines = content.split("\n")

    # We'll insert all text first as plain text, then apply formatting
    # Build the full plain text with newlines, tracking line positions
    # for styling. Use a two-pass approach: insert all text, then style.

    # First, build plain text and a map of (start_index, end_index, style)
    full_text = ""
    style_map = []  # list of (start, end, style_type, extra)

    STYLES = {
        "h1": "HEADING_1",
        "h2": "HEADING_2",
        "h3": "HEADING_3",
        "h4": "HEADING_4",
    }

    current_pos = 1  # Google Docs starts at index 1

    for i, line in enumerate(lines):
        raw_line = line

        # Detect heading level
        heading_match = re.match(r"^(#{1,4})\s+(.*)", line)
        hr_match = re.match(r"^---+$", line.strip())
        checkbox_match = re.match(r"^(\s*)- \[([ x])\] (.*)", line)

        if hr_match:
            # Replace HR with a visual separator line
            text = "─" * 60 + "\n"
            style_map.append((current_pos, current_pos + len(text), "normal", None))
            full_text += text
            current_pos += len(text)
        elif heading_match:
            hashes = heading_match.group(1)
            heading_text = heading_match.group(2)
            h_level = f"h{len(hashes)}"
            text = heading_text + "\n"
            style_map.append((current_pos, current_pos + len(text), h_level, None))
            full_text += text
            current_pos += len(text)
        elif checkbox_match:
            indent = checkbox_match.group(1)
            checked = checkbox_match.group(2)
            label = checkbox_match.group(3)
            # Render checkbox as unicode
            box = "☑" if checked == "x" else "☐"
            text = f"{indent}{box} {label}\n"
            style_map.append((current_pos, current_pos + len(text), "normal", None))
            full_text += text
            current_pos += len(text)
        else:
            text = line + "\n"
            style_map.append((current_pos, current_pos + len(text), "normal", None))
            full_text += text
            current_pos += len(text)

    # Request 1: Insert all text at index 1
    requests.append({
        "insertText": {
            "location": {"index": 1},
            "text": full_text
        }
    })

    # Request 2+: Apply paragraph styles for headings
    heading_style_map = {
        "h1": "HEADING_1",
        "h2": "HEADING_2",
        "h3": "HEADING_3",
        "h4": "HEADING_4",
    }

    for start, end, style_type, extra in style_map:
        if style_type in heading_style_map:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {"namedStyleType": heading_style_map[style_type]},
                    "fields": "namedStyleType"
                }
            })

    return requests


def main():
    print("Authenticating with Google Workspace...")
    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)
    gmail = build("gmail", "v1", credentials=creds)

    # --- Task 1: Create folder structure and Google Doc ---
    print("\nTask 1: Setting up Drive folder structure...")

    root_id = get_or_create_folder(drive, "GBAutomation Clients")
    print(f"  Root folder ID: {root_id}")

    client_id = get_or_create_folder(drive, "Fish Group", parent_id=root_id)
    print(f"  Fish Group folder ID: {client_id}")

    session_id = get_or_create_folder(drive, "Fish Group — Session 2026-03-12", parent_id=client_id)
    print(f"  Session folder ID: {session_id}")

    deliverables_id = get_or_create_folder(drive, "deliverables", parent_id=session_id)
    print(f"  Deliverables folder ID: {deliverables_id}")

    # Read the workflow catalog markdown
    catalog_path = r"C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\consulting-intake\client-sessions\20260305-michael-fisch\session_output\workflow-catalog.md"
    with open(catalog_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("\nCreating Google Doc...")
    doc_title = "Fish Group — Workflow Catalog (27 AI-Generated Workflows)"

    # Create the doc
    doc_metadata = {
        "name": doc_title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [deliverables_id],
    }
    doc = drive.files().create(body=doc_metadata, fields="id, webViewLink").execute()
    doc_id = doc["id"]
    doc_url = doc["webViewLink"]
    print(f"  Doc created: {doc_url}")

    # Build and apply content
    print("  Populating doc content...")
    requests = build_doc_requests(content)
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()
    print("  Content applied successfully.")

    # --- Task 2: Share with mike@piermontbrands.com as editor ---
    print("\nTask 2: Sharing Google Doc...")
    try:
        drive.permissions().create(
            fileId=doc_id,
            body={
                "type": "user",
                "role": "writer",
                "emailAddress": "mike@piermontbrands.com",
            },
            sendNotificationEmail=False,
            fields="id"
        ).execute()
        print("  Shared with mike@piermontbrands.com (editor) — no notification email.")
    except Exception as e:
        print(f"  First attempt failed ({e}), retrying with notification email...")
        drive.permissions().create(
            fileId=doc_id,
            body={
                "type": "user",
                "role": "writer",
                "emailAddress": "mike@piermontbrands.com",
            },
            sendNotificationEmail=True,
            fields="id"
        ).execute()
        print("  Shared with mike@piermontbrands.com (editor) — notification sent.")

    # --- Task 3: Draft Gmail ---
    print("\nTask 3: Creating Gmail draft...")

    subject = "Fish Group — AI Workflow Catalog (27 Workflows Identified)"

    body_html = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; line-height: 1.6;">

<p>Hey Michael,</p>

<p>Following up on our session today &mdash; I put together a comprehensive workflow catalog based on everything we discussed. It includes 27 potential workflows across your business, organized by priority:</p>

<ul>
  <li><strong>5 Quick Wins</strong> &mdash; buildable in 1-2 hours each (AR Aging Follow-Up is #1, as you requested)</li>
  <li><strong>10 Medium Effort</strong> &mdash; high-impact workflows like vendor payments, bank reconciliation, inventory alerts</li>
  <li><strong>5 Strategic</strong> &mdash; bigger builds like the Gary's CS Agent and full client onboarding automation</li>
  <li><strong>7 Nice-to-Have</strong> &mdash; LinkedIn prospecting, meeting prep, compliance checklists</li>
</ul>

<p>Each workflow includes which APIs are needed, human-in-the-loop checkpoints, validation gates, and build time estimates.</p>

<p>I've also included a recommended 4-phase build order starting with the AR follow-up and cash position summary in our next sessions.</p>

<p><strong>The doc is shared with you as an editor</strong> &mdash; feel free to mark which workflows are most important to you, add comments, or reorder priorities. The Prerequisites Checklist at the bottom has checkboxes you can tick off as we get API keys and credentials set up.</p>

<p>Here's the link: <a href="{doc_url}" style="color: #D97757;">{doc_url}</a></p>

<p>Once I have Emil's email I'll share it with him too.</p>

<p>Talk soon,</p>

<p>
  <strong>Greg Black</strong><br/>
  GBAutomation<br/>
  <a href="mailto:greg@gbautomation.xyz">greg@gbautomation.xyz</a>
</p>

</body>
</html>"""

    body_text = f"""Hey Michael,

Following up on our session today — I put together a comprehensive workflow catalog based on everything we discussed. It includes 27 potential workflows across your business, organized by priority:

• 5 Quick Wins — buildable in 1-2 hours each (AR Aging Follow-Up is #1, as you requested)
• 10 Medium Effort — high-impact workflows like vendor payments, bank reconciliation, inventory alerts
• 5 Strategic — bigger builds like the Gary's CS Agent and full client onboarding automation
• 7 Nice-to-Have — LinkedIn prospecting, meeting prep, compliance checklists

Each workflow includes which APIs are needed, human-in-the-loop checkpoints, validation gates, and build time estimates.

I've also included a recommended 4-phase build order starting with the AR follow-up and cash position summary in our next sessions.

The doc is shared with you as an editor — feel free to mark which workflows are most important to you, add comments, or reorder priorities. The Prerequisites Checklist at the bottom has checkboxes you can tick off as we get API keys and credentials set up.

Here's the link: {doc_url}

Once I have Emil's email I'll share it with him too.

Talk soon,
Greg Black
GBAutomation
greg@gbautomation.xyz"""

    message = MIMEMultipart("alternative")
    message["to"] = "mike@piermontbrands.com"
    message["from"] = "Greg Black | GBAutomation <greg@gbautomation.xyz>"
    message["subject"] = subject
    message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = gmail.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()
    draft_id = draft["id"]
    print(f"  Draft created. Draft ID: {draft_id}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("ALL TASKS COMPLETE")
    print("=" * 60)
    print(f"Google Doc URL : {doc_url}")
    print(f"Gmail Draft ID : {draft_id}")
    print(f"Draft review   : https://mail.google.com/mail/#drafts")
    print("=" * 60)

    return doc_url, draft_id


if __name__ == "__main__":
    main()
