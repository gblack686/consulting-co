"""
Build Client Lifecycle Sheet
=============================
Creates a comprehensive multi-tab Google Sheet for the client lifecycle:
intake → pre-session → session → workflows/APIs → payment → delivery →
review → sign-off → 1-week support.

Pre-fills known data from intake analysis.

Usage:
    python -m scripts.build_client_sheet --name "Jason Diaz" --email "jid5274@gmail.com"
"""
import argparse
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# Sheet definition helpers
# ─────────────────────────────────────────────────────────────────────────────

def _header_row(cells: list) -> dict:
    return {
        "values": [
            {
                "userEnteredValue": {"stringValue": c},
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.851, "green": 0.467, "blue": 0.337},  # terracotta
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                }
            }
            for c in cells
        ]
    }


def _row(cells: list) -> dict:
    """Plain row — each cell can be str, bool, or None."""
    values = []
    for c in cells:
        if c is None:
            values.append({"userEnteredValue": {"stringValue": ""}})
        elif isinstance(c, bool):
            values.append({"userEnteredValue": {"boolValue": c}})
        else:
            values.append({"userEnteredValue": {"stringValue": str(c)}})
    return {"values": values}


def _checkbox_row(label: str, status: str = "⬜ Pending", notes: str = "") -> dict:
    return _row([label, status, notes])


def _section_label(text: str) -> dict:
    return {
        "values": [
            {
                "userEnteredValue": {"stringValue": text},
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                    "textFormat": {"bold": True, "italic": True},
                }
            },
            {"userEnteredValue": {"stringValue": ""}},
            {"userEnteredValue": {"stringValue": ""}},
        ]
    }


def _blank() -> dict:
    return _row(["", "", ""])


# ─────────────────────────────────────────────────────────────────────────────
# Tab builders
# ─────────────────────────────────────────────────────────────────────────────

def _overview_tab(client_name: str, client_email: str, intake_url: str) -> dict:
    first_name = client_name.split()[0]
    rows = [
        _header_row(["Phase", "Status", "Notes / Links"]),
        _checkbox_row("1. Client Intake (pre-session docs)", "✅ Complete",
                      f"Intake Analysis: {intake_url}"),
        _checkbox_row("2. Pre-Session Prep sent to client", "✅ Complete",
                      f"Email sent to {client_email}"),
        _checkbox_row("3. Pre-Session Prep reviewed by Greg", "⬜ Pending"),
        _checkbox_row("4. Intake assumptions approved by client", "⬜ Pending",
                      "Client replies with approvals/corrections"),
        _checkbox_row("5. 90-Min Consulting Session", "⬜ Pending",
                      "Schedule via Google Calendar"),
        _checkbox_row("6. Session transcript reviewed", "⬜ Pending"),
        _checkbox_row("7. Workflow requirements documented", "⬜ Pending",
                      "See 'Workflow Checklist' tab"),
        _checkbox_row("8. API keys collected from client", "⬜ Pending",
                      "See 'API Keys' tab"),
        _checkbox_row("9. Payment — 50% deposit received", "⬜ Pending"),
        _checkbox_row("10. Build started", "⬜ Pending"),
        _checkbox_row("11. Deliverables ready for review", "⬜ Pending",
                      "See 'Deliverables' tab"),
        _checkbox_row("12. Client review call / async review", "⬜ Pending"),
        _checkbox_row("13. Revisions complete", "⬜ Pending"),
        _checkbox_row("14. Payment — final 50% received", "⬜ Pending"),
        _checkbox_row("15. Go-live / handoff", "⬜ Pending"),
        _checkbox_row("16. 1-week support window open", "⬜ Pending",
                      "See 'Support Log' tab"),
        _checkbox_row("17. Support window closed", "⬜ Pending"),
        _checkbox_row("18. Client sign-off received", "⬜ Pending",
                      "See 'Sign-Off' tab"),
        _checkbox_row("19. Testimonial / referral requested", "⬜ Pending"),
    ]
    return {
        "properties": {"title": "📋 Overview", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _client_profile_tab(client_name: str, client_email: str) -> dict:
    rows = [
        _header_row(["Field", "Value", "Notes"]),
        _row(["Client Name", client_name]),
        _row(["Email", client_email]),
        _row(["Company", "Wellness Marketing LLC / PMC / EWC"]),
        _row(["Industry", "Wellness / Health Marketing"]),
        _row(["Role", "Owner / Operator"]),
        _row(["LinkedIn", ""]),
        _row(["Phone", ""]),
        _row(["Time Zone", ""]),
        _row(["Preferred Contact", "Email"]),
        _blank(),
        _section_label("Package"),
        _row(["Package Tier", "TBD (Custom)"]),
        _row(["Price", "$"]),
        _row(["Deposit (50%)", "$"]),
        _row(["Final Payment (50%)", "$"]),
        _row(["Payment Method", "Stripe"]),
        _row(["Stripe Invoice Link", ""]),
        _blank(),
        _section_label("Key Dates"),
        _row(["Intake Scan Date", "2026-02-28"]),
        _row(["Session Date", "TBD"]),
        _row(["Delivery Target", ""]),
        _row(["Support Window End", ""]),
    ]
    return {
        "properties": {"title": "👤 Client Profile", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _intake_tab(intake_url: str) -> dict:
    rows = [
        _header_row(["Question", "Assumed Answer", "Client Approved? (Y/N/Edit)", "Notes"]),
        {
            "values": [
                {"userEnteredValue": {"stringValue": "Q1: Tools used weekly"}},
                {"userEnteredValue": {"stringValue": "See Intake Analysis doc →"}},
                {"userEnteredValue": {"stringValue": ""}},
                {"userEnteredValue": {"stringValue": intake_url}},
            ]
        },
        _row(["Q2: 3–5 departments / roles if hired out", "See Intake Analysis doc →", "", intake_url]),
        _row(["Q3: Most annoying recurring task", "See Intake Analysis doc →", "", intake_url]),
        _row(["Q4: Perfect morning briefing", "See Intake Analysis doc →", "", intake_url]),
        _row(["Q5: Agent name / personality / nickname", "See Intake Analysis doc →", "", intake_url]),
        _blank(),
        _section_label("Known from PMC/EWC Drive documents"),
        _row(["Industry", "Wellness / Health Marketing", "✅ Confirmed from docs"]),
        _row(["Tools (confirmed)", "CRM (likely HubSpot or similar), Google Workspace, Email marketing platform", ""]),
        _row(["Primary workflows", "Client follow-up, marketing campaigns, wellness content scheduling", ""]),
        _row(["Pain points (inferred)", "Manual client follow-up, campaign reporting, content repurposing", ""]),
    ]
    return {
        "properties": {"title": "📝 Intake Answers", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _workflow_checklist_tab() -> dict:
    rows = [
        _header_row(["Workflow / Domain", "Description", "Status", "Complexity", "Notes"]),
        _section_label("Likely Workflows (based on intake)"),
        _row(["Client Follow-Up Automation", "Automated emails/texts after consultations or inquiries",
              "⬜ To spec", "Medium"]),
        _row(["Morning Briefing Agent", "Daily AI summary: appointments, leads, revenue, tasks",
              "⬜ To spec", "Medium"]),
        _row(["Content Repurposing", "Turn one piece of content into emails, social posts, newsletters",
              "⬜ To spec", "High"]),
        _row(["Lead Intake → CRM", "New inquiry → CRM entry → follow-up sequence triggered",
              "⬜ To spec", "High"]),
        _row(["Weekly Reporting", "Auto-pull KPIs from CRM/ads and generate summary report",
              "⬜ To spec", "Medium"]),
        _blank(),
        _section_label("Custom Workflows (to be determined in session)"),
        _row(["TBD #1", "", "⬜ TBD", ""]),
        _row(["TBD #2", "", "⬜ TBD", ""]),
        _row(["TBD #3", "", "⬜ TBD", ""]),
    ]
    return {
        "properties": {"title": "⚙️ Workflow Checklist", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _api_keys_tab() -> dict:
    rows = [
        _header_row(["Service / API", "Purpose", "Received?", "Key Name / Location", "Notes"]),
        _section_label("Google Workspace (client's account)"),
        _row(["Google OAuth (client)", "Access Gmail, Calendar, Drive on client's behalf",
              "⬜ Pending", "OAuth flow needed"]),
        _blank(),
        _section_label("CRM"),
        _row(["CRM API Key", "Read/write contacts, deals, pipeline",
              "⬜ Pending", "", "Confirm CRM name in session"]),
        _blank(),
        _section_label("Marketing / Email"),
        _row(["Email Marketing Platform", "Send campaigns, pull stats",
              "⬜ Pending", "", "Mailchimp / ActiveCampaign / Klaviyo TBD"]),
        _blank(),
        _section_label("Other (to confirm in session)"),
        _row(["Scheduling Tool", "Calendly / Acuity — booking data",
              "⬜ Pending"]),
        _row(["Ads Platform", "Meta / Google Ads spend + performance",
              "⬜ Pending"]),
        _row(["Analytics", "Google Analytics / website traffic",
              "⬜ Pending"]),
        _row(["Payment Processor", "Stripe / Square — revenue data",
              "⬜ Pending"]),
        _row(["Custom API #1", "", "⬜ Pending"]),
        _row(["Custom API #2", "", "⬜ Pending"]),
    ]
    return {
        "properties": {"title": "🔑 API Keys", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _deliverables_tab() -> dict:
    rows = [
        _header_row(["Deliverable", "Status", "Link / Location", "Notes"]),
        _section_label("Core Deliverables"),
        _row(["Agent system (OpenClaw deployment)", "⬜ Not started", ""]),
        _row(["Workflow automations (Make / n8n / custom)", "⬜ Not started", ""]),
        _row(["Morning briefing agent", "⬜ Not started", ""]),
        _row(["SOUL.md — agent personality spec", "⬜ Not started", "",
              "Built post-session based on call notes"]),
        _blank(),
        _section_label("Documentation"),
        _row(["Agent IDENTITY.md", "⬜ Not started", ""]),
        _row(["TOOLS.md — skill inventory", "⬜ Not started", ""]),
        _row(["User guide / how-to doc", "⬜ Not started", ""]),
        _blank(),
        _section_label("Optional / Add-ons"),
        _row(["Custom dashboard", "⬜ Not started", ""]),
        _row(["Slack / Discord integration", "⬜ Not started", ""]),
        _row(["Add-on workflow #1", "⬜ Not started", ""]),
        _row(["Add-on workflow #2", "⬜ Not started", ""]),
    ]
    return {
        "properties": {"title": "📦 Deliverables", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _payment_tab(client_name: str, client_email: str) -> dict:
    rows = [
        _header_row(["Item", "Amount", "Status", "Date", "Notes"]),
        _row(["Package (TBD)", "$", "⬜ Pending", "", "Confirm in session"]),
        _row(["Deposit — 50% (due before build)", "$", "⬜ Pending", "",
              "Stripe invoice to be sent"]),
        _row(["Final payment — 50% (due at delivery)", "$", "⬜ Pending", ""]),
        _blank(),
        _section_label("Stripe"),
        _row(["Stripe Customer", client_email]),
        _row(["Invoice Link", ""]),
        _row(["Payment Link", ""]),
        _blank(),
        _section_label("Refund / Cancellation Policy"),
        _row(["Deposit", "Non-refundable after build begins"]),
        _row(["Final payment", "Due within 3 business days of delivery"]),
        _row(["Dispute window", "7 days from delivery"]),
    ]
    return {
        "properties": {"title": "💳 Payment", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _review_signoff_tab(client_name: str) -> dict:
    first_name = client_name.split()[0]
    rows = [
        _header_row(["Item", "Status", "Date", "Notes"]),
        _section_label("Delivery Review"),
        _checkbox_row("Deliverables demo / walkthrough call scheduled"),
        _checkbox_row("Screen recording / Loom sent to client"),
        _checkbox_row(f"Client reviewed all deliverables"),
        _checkbox_row("Revision request #1 (if any)"),
        _checkbox_row("Revision request #2 (if any)"),
        _checkbox_row("All revisions complete"),
        _blank(),
        _section_label("Sign-Off"),
        _checkbox_row("Sign-off email sent to client"),
        _checkbox_row(f"{first_name} confirmed acceptance in writing"),
        _checkbox_row("Final 50% payment received"),
        _checkbox_row("Project marked COMPLETE"),
        _blank(),
        _section_label("Extras"),
        _checkbox_row("Testimonial / Google review requested"),
        _checkbox_row("Referral asked"),
        _checkbox_row("Case study permission obtained"),
    ]
    return {
        "properties": {"title": "✅ Review & Sign-Off", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


def _support_log_tab() -> dict:
    rows = [
        _header_row(["Date", "Issue / Request", "Resolution", "Time Spent", "Status"]),
        _row(["", "1-week support window open", "", "",  "⬜ Not started"]),
        _row(["", "", "", "", ""]),
        _row(["", "", "", "", ""]),
        _row(["", "", "", "", ""]),
        _row(["", "", "", "", ""]),
        _blank(),
        _section_label("Support Window Policy"),
        _row(["Duration", "7 calendar days from go-live", "", "", ""]),
        _row(["Scope", "Bug fixes only (not new features)", "", "", ""]),
        _row(["Contact", "greg@gbautomation.xyz", "", "", ""]),
    ]
    return {
        "properties": {"title": "🛠️ Support Log", "gridProperties": {"frozenRowCount": 1}},
        "data": [{"rowData": rows}],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main function
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet(client_name: str, client_email: str,
                onboarding_folder_id: str, intake_url: str) -> str:
    """
    Create the lifecycle Google Sheet, save to onboarding folder, share with client.
    Returns the spreadsheet URL.
    """
    from . import google_client, drive_manager

    sheets = google_client.sheets_service()
    drive = google_client.drive_service()

    title = f"Client Lifecycle — {client_name}"

    # Build sheet body
    body = {
        "properties": {"title": title},
        "sheets": [
            _overview_tab(client_name, client_email, intake_url),
            _client_profile_tab(client_name, client_email),
            _intake_tab(intake_url),
            _workflow_checklist_tab(),
            _api_keys_tab(),
            _deliverables_tab(),
            _payment_tab(client_name, client_email),
            _review_signoff_tab(client_name),
            _support_log_tab(),
        ],
    }

    # Create the spreadsheet
    spreadsheet = sheets.spreadsheets().create(
        body=body,
        fields="spreadsheetId,spreadsheetUrl"
    ).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    sheet_url = spreadsheet["spreadsheetUrl"]

    # Move spreadsheet into client's Onboarding folder
    file = drive.files().get(fileId=spreadsheet_id, fields="parents").execute()
    previous_parents = ",".join(file.get("parents", []))
    drive.files().update(
        fileId=spreadsheet_id,
        addParents=onboarding_folder_id,
        removeParents=previous_parents,
        fields="id, parents"
    ).execute()

    # Share with client as commenter (can comment but not edit core structure)
    drive_manager.share_folder(spreadsheet_id, client_email, role="commenter")

    print(f"      ✓ Sheet created: {sheet_url}")
    return sheet_url


def _get_onboarding_folder_id(client_name: str) -> str:
    """Look up or recreate the onboarding folder ID."""
    from . import drive_manager
    _, onboarding_id = drive_manager.create_onboarding_folder(client_name)
    return onboarding_id


def run(client_name: str, client_email: str,
        intake_url: str, onboarding_folder_id: str = None) -> dict:
    """
    Build the lifecycle sheet and send the email with both links.
    """
    from . import gmail_client

    print(f"\n{'='*60}")
    print(f"  BUILD CLIENT SHEET: {client_name}")
    print(f"{'='*60}\n")

    if not onboarding_folder_id:
        print("[1/3] Looking up onboarding folder...")
        onboarding_folder_id = _get_onboarding_folder_id(client_name)
        print(f"      Onboarding folder ID: {onboarding_folder_id}")

    print("[2/3] Creating lifecycle Google Sheet...")
    sheet_url = build_sheet(client_name, client_email, onboarding_folder_id, intake_url)

    print(f"\n[3/3] Sending email to {client_email}...")
    first_name = client_name.split()[0]
    subject = f"Your project checklist + intake assumptions, {first_name}"
    body_html = _build_email(first_name, client_email, intake_url, sheet_url)
    msg_id = gmail_client.send_email(to=client_email, subject=subject, body_html=body_html)
    print(f"      ✓ Email sent (ID: {msg_id})")

    print(f"\n{'='*60}")
    print(f"  DONE")
    print(f"  Sheet: {sheet_url}")
    print(f"  Intake doc: {intake_url}")
    print(f"{'='*60}\n")

    return {
        "client_name": client_name,
        "sheet_url": sheet_url,
        "intake_url": intake_url,
        "email_id": msg_id,
    }


def _build_email(first_name: str, client_email: str,
                 intake_url: str, sheet_url: str) -> str:
    return f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 640px; margin: 0 auto; padding: 20px;">

  <img src="https://gbautomation.xyz/gb-logo.png" alt="GBAutomation"
       style="height:45px; margin-bottom:24px;" />

  <h2 style="color: #D97757;">Here's your full project checklist, {first_name}</h2>

  <p>Hi {first_name},</p>

  <p>I went through everything you sent me — the PMC/EWC drive, your documents, the overview files — and put together two things for you:</p>

  <h3 style="color:#D97757;">1. My Intake Assumptions</h3>
  <p>I analyzed your documents and pre-filled what I think your answers are to the intake questions.
  <strong>Please review and reply with anything that looks wrong or incomplete.</strong></p>
  <p>
    <a href="{intake_url}" style="display:inline-block; background:#D97757; color:white;
       padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:bold;">
      View Intake Analysis →
    </a>
  </p>

  <h3 style="color:#D97757;">2. Your Full Project Lifecycle Checklist</h3>
  <p>I also created a master Google Sheet that tracks everything from here to completion —
  intake, session, API keys, payment, build, delivery, review, and your 1-week support window.</p>
  <p>
    <a href="{sheet_url}" style="display:inline-block; background:#D97757; color:white;
       padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:bold;">
      Open Project Checklist →
    </a>
  </p>

  <hr style="border:none; border-top:1px solid #eee; margin:24px 0;" />

  <h3>What I Need From You</h3>
  <ul>
    <li><strong>Review the intake assumptions</strong> — reply with any corrections</li>
    <li><strong>Check the workflow checklist tab</strong> — let me know if I'm missing anything</li>
    <li><strong>Confirm your preferred session date</strong> — I'll send a calendar invite</li>
  </ul>

  <p>Once you confirm the assumptions look right, we're ready to schedule our 90-minute session.</p>

  <p>
    <strong>Greg Black</strong><br/>
    GBAutomation<br/>
    <a href="mailto:greg@gbautomation.xyz">greg@gbautomation.xyz</a>
  </p>

</body>
</html>
"""


if __name__ == "__main__":
    import os

    parser = argparse.ArgumentParser(description="Build client lifecycle sheet and send email")
    parser.add_argument("--name", required=True, help="Client full name")
    parser.add_argument("--email", required=True, help="Client email address")
    parser.add_argument("--intake-url", required=True, help="URL of the intake analysis Google Doc")
    parser.add_argument("--onboarding-folder-id", default=None,
                        help="Onboarding folder ID (auto-detected if omitted)")
    args = parser.parse_args()

    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))

    run(
        client_name=args.name,
        client_email=args.email,
        intake_url=args.intake_url,
        onboarding_folder_id=args.onboarding_folder_id,
    )
