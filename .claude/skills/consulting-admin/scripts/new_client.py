"""
New Client Onboarding Skill
=============================
Given a client name and email:
1. Creates a Google Drive folder under GBAutomation Clients/
2. Uploads all client-facing docs as branded Google Docs
3. Shares the folder with the client
4. Sends a welcome email from greg@gbautomation.xyz

Usage:
    python -m scripts.new_client --name "Jason Diaz" --email "jid5274@gmail.com"
    python -m scripts.new_client --name "Jason Diaz" --email "jid5274@gmail.com" --draft
"""
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# Template paths (relative to skill root)
SKILL_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_ROOT.parent / "consulting-intake" / "client-facing"
LOGO_PATH = SKILL_ROOT / "assets" / "gb-logo.png"

# Map of doc title -> template file
DOCS_TO_CREATE = {
    "Welcome Email & Overview":     "welcome-email.md",
    "Service Agreement":            "service-agreement.md",
    "Pre-Session Prep Guide":       "pre-session-prep.md",
    "Session Agenda":               "session-agenda.md",
    "Key Terms Glossary":           "key-terms.md",
}

# Template variables (extend as needed)
def get_template_vars(client_name: str, client_email: str) -> dict:
    return {
        "{client_name}":        client_name,
        "{client_email}":       client_email,
        "{company_name}":       "GBAutomation",
        "{consultant_name}":    "Greg Black",
        "{support_email}":      "greg@gbautomation.xyz",
        "{support_channel}":    "greg@gbautomation.xyz",
        "{agreement_date}":     datetime.today().strftime("%B %d, %Y"),
        "{session_date}":       "TBD — we'll schedule shortly",
        "{session_time}":       "TBD",
        "{timezone}":           "your local time",
        "{delivery_window}":    "5 business days",
        "{video_call_link}":    "https://calendar.app.google/esY5F8R6YUckRGWB9",
        "{foundation_price}":   "$1,500",
        "{standard_price}":     "$2,500",
        "{premium_price}":      "$4,000",
        "{payment_schedule}":   "50% upfront, 50% on delivery",
        "{stripe_payment_link}": "https://gbautomation.xyz/pay",
        "{company_address}":    "Remote",
        "{arbitration_body}":   "AAA",
        "{jurisdiction}":       "State of New York",
    }


def fill_template(content: str, vars: dict) -> str:
    for key, val in vars.items():
        content = content.replace(key, val)
    return content


def load_template(filename: str) -> str:
    path = TEMPLATES_DIR / filename
    if not path.exists():
        print(f"  WARNING: Template not found: {path}")
        return f"[Template {filename} not found]"
    return path.read_text(encoding="utf-8")


def run(client_name: str, client_email: str, draft_mode: bool = False):
    from . import drive_manager, gmail_client

    print(f"\n{'='*50}")
    print(f"  NEW CLIENT ONBOARDING: {client_name}")
    print(f"  Email: {client_email}")
    print(f"  Mode: {'DRAFT (no send)' if draft_mode else 'LIVE'}")
    print(f"{'='*50}\n")

    template_vars = get_template_vars(client_name, client_email)

    # Step 1: Create Drive folder + Onboarding subfolder
    print(f"[1/4] Creating Drive folder for {client_name}...")
    folder_id, onboarding_folder_id = drive_manager.create_onboarding_folder(client_name)
    folder_url = drive_manager.get_folder_url(folder_id)
    onboarding_url = drive_manager.get_folder_url(onboarding_folder_id)
    print(f"      Client folder:    {folder_url}")
    print(f"      Onboarding folder: {onboarding_url}")

    # Step 2: Upload all docs as branded Google Docs inside Onboarding/
    print(f"\n[2/4] Creating branded Google Docs (in Onboarding/)...")
    doc_urls = {}
    for doc_title, template_file in DOCS_TO_CREATE.items():
        print(f"      Creating: {doc_title}...")
        raw_content = load_template(template_file)
        filled_content = fill_template(raw_content, template_vars)
        url = drive_manager.create_google_doc(
            title=doc_title,
            content_markdown=filled_content,
            parent_folder_id=onboarding_folder_id,
            logo_path=str(LOGO_PATH) if LOGO_PATH.exists() else None,
        )
        doc_urls[doc_title] = url
        print(f"      ✓ {doc_title}: {url}")

    # Step 3: Share folder with client + internal accounts
    print(f"\n[3/4] Sharing folder...")
    shares = [
        (client_email,          "writer"),   # client: full edit
        ("gblack686@gmail.com", "writer"),   # personal account: full edit
        ("greg@gbautomation.xyz", "writer"), # workspace account: full edit
    ]
    for email, role in shares:
        drive_manager.share_folder(folder_id, email, role=role)
        print(f"      ✓ {email} → {role}")

    # Step 4: Send or draft welcome email
    print(f"\n[4/4] {'Creating draft' if draft_mode else 'Sending'} welcome email...")
    subject = f"Your GBAutomation Agent Setup — Welcome, {client_name.split()[0]}!"
    body_html = gmail_client.build_welcome_email_html(
        client_name=client_name.split()[0],
        folder_url=folder_url,
        doc_urls=doc_urls,
    )

    if draft_mode:
        draft_id = gmail_client.create_draft(
            to=client_email,
            subject=subject,
            body_html=body_html,
        )
        print(f"      ✓ Draft created (ID: {draft_id})")
        print(f"        Review at: https://mail.google.com/mail/#drafts")
    else:
        msg_id = gmail_client.send_email(
            to=client_email,
            subject=subject,
            body_html=body_html,
        )
        print(f"      ✓ Email sent (ID: {msg_id})")

    # Step 5: Generate onboarding deck and upload to Drive
    print(f"\n[5/5] Generating onboarding deck...")
    deck_url = None
    try:
        import types
        from . import generate_client_deck
        deck_args = types.SimpleNamespace(
            name=client_name,
            email=client_email,
            session_date="TBD",
            session_time="TBD",
            timezone="",
            meet_link="TBD",
            output=f"{client_name.lower().replace(' ', '-')}-onboarding.pptx",
        )
        deck_path = generate_client_deck.generate(deck_args)
        deck_filename = f"{client_name} — Onboarding Deck.pptx"
        deck_url = drive_manager.upload_file_to_folder(
            local_path=str(deck_path),
            filename=deck_filename,
            folder_id=onboarding_folder_id,
        )
        print(f"      ✓ Deck uploaded: {deck_url}")
    except Exception as e:
        print(f"      WARNING: Deck generation failed — {e}")

    # Summary
    print(f"\n{'='*50}")
    print(f"  DONE — {client_name} onboarded successfully")
    print(f"\n  Drive folder:      {folder_url}")
    print(f"  Onboarding folder: {onboarding_url}")
    print(f"  Documents: {len(doc_urls)} created")
    if deck_url:
        print(f"  Deck:              {deck_url}")
    print(f"  Email: {'Draft saved' if draft_mode else 'Sent to ' + client_email}")
    print(f"{'='*50}\n")

    return {
        "client_name": client_name,
        "client_email": client_email,
        "folder_id": folder_id,
        "onboarding_folder_id": onboarding_folder_id,
        "folder_url": folder_url,
        "onboarding_url": onboarding_url,
        "doc_urls": doc_urls,
        "deck_url": deck_url,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Onboard a new GBAutomation consulting client")
    parser.add_argument("--name",  required=True, help="Client full name (e.g. 'Jason Diaz')")
    parser.add_argument("--email", required=True, help="Client email address")
    parser.add_argument("--draft", action="store_true", help="Create email draft instead of sending")
    args = parser.parse_args()

    # Run from skill root so relative paths work
    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))

    run(client_name=args.name, client_email=args.email, draft_mode=args.draft)
