"""
Scan Client Skill
==================
Scans all documents a client shared with us (Drive + email attachments),
uses Claude to fill out their intake form assumptions, then drafts an
approval email to the client.

Usage:
    python -m scripts.scan_client --name "Jason Diaz" --email "jid5274@gmail.com"
    python -m scripts.scan_client --name "Jason Diaz" --email "jid5274@gmail.com" --draft
    python -m scripts.scan_client --name "Jason Diaz" --email "jid5274@gmail.com" --send
"""
import argparse
import os
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent


def run(client_name: str, client_email: str, draft: bool = True):
    from . import drive_manager, gmail_client
    from .intake_filler import fill_intake, format_assumptions_markdown

    first_name = client_name.split()[0]

    print(f"\n{'='*60}")
    print(f"  INTAKE SCAN: {client_name}")
    print(f"  Email: {client_email}")
    print(f"  Mode: {'DRAFT' if draft else 'SEND'}")
    print(f"{'='*60}\n")

    # ── Step 1: Find Drive files shared by client ──────────────────
    print("[1/5] Scanning Drive for files shared by client...")
    shared_files = drive_manager.get_files_shared_by(client_email)
    print(f"      Found {len(shared_files)} shared file(s):")
    for f in shared_files:
        print(f"      • {f['name']} ({f['mimeType'].split('.')[-1]})")

    # ── Step 2: Find emails from client ────────────────────────────
    print(f"\n[2/5] Scanning Gmail for emails from {client_email}...")
    emails = gmail_client.get_emails_from(client_email, max_results=10)
    print(f"      Found {len(emails)} email(s)")

    # Collect Drive links mentioned in emails
    email_drive_links = []
    for e in emails:
        if e["drive_links"]:
            print(f"      • Drive links in '{e['subject']}': {e['drive_links']}")
            email_drive_links.extend(e["drive_links"])

    # ── Step 3: Extract text from all Drive files ───────────────────
    print(f"\n[3/5] Extracting text from {len(shared_files)} Drive file(s)...")
    documents = {}

    for f in shared_files:
        print(f"      Extracting: {f['name']}...")
        text = drive_manager.export_doc_text(f["id"], f["mimeType"])
        if text and not text.startswith("["):  # skip unsupported format notes
            documents[f["name"]] = text
            print(f"      ✓ {len(text):,} chars extracted")
        else:
            documents[f["name"]] = text  # keep the note anyway
            print(f"      ⚠ {text[:60]}")

    # Add email bodies as documents too
    for e in emails:
        if e["body"].strip():
            key = f"Email: {e['subject']} ({e['date'][:16]})"
            documents[key] = e["body"]

    if not documents:
        print("      ⚠ No readable documents found. Intake analysis will be low-confidence.")

    # ── Step 4: Copy shared files into client's Drive folder ────────
    print(f"\n[4/5] Copying shared files into client Drive folder...")
    client_folder_id, onboarding_folder_id = drive_manager.create_onboarding_folder(client_name)
    for f in shared_files:
        # Skip folders — can't copy them, just note the link
        if f["mimeType"] == "application/vnd.google-apps.folder":
            print(f"      ⏭ Skipped (folder): {f['name']} — link: {f.get('webViewLink','')}")
            continue
        try:
            copy_name = f"[From {first_name}] {f['name']}"
            url = drive_manager.copy_file_to_folder(f["id"], copy_name, onboarding_folder_id)
            print(f"      ✓ Copied: {copy_name}")
        except Exception as e:
            print(f"      ⚠ Could not copy '{f['name']}': {e}")

    # ── Step 5: Run Claude intake analysis ─────────────────────────
    print(f"\n[5/5] Running intake analysis with Claude...")
    if documents:
        assumptions = fill_intake(client_name, documents)
        print(f"      ✓ Analysis complete")
    else:
        assumptions = {
            "tools": [], "departments": [], "annoying_task": {}, "morning_briefing": {},
            "agent_personality": {},
            "confidence_notes": {k: "No documents found" for k in
                ["tools", "departments", "annoying_task", "morning_briefing", "agent_personality"]},
        }

    # Save analysis as Google Doc in Onboarding folder
    source_names = list(documents.keys())
    markdown = format_assumptions_markdown(client_name, assumptions, source_names)
    analysis_url = drive_manager.create_google_doc(
        title=f"Intake Analysis — {client_name}",
        content_markdown=markdown,
        parent_folder_id=onboarding_folder_id,
    )
    print(f"      ✓ Analysis doc created: {analysis_url}")

    # ── Step 6: Draft/send approval email ──────────────────────────
    print(f"\n[6/6] {'Drafting' if draft else 'Sending'} approval email to {client_email}...")
    subject = f"I reviewed your files — here are my assumptions for your setup, {first_name}"
    body_html = _build_approval_email(
        first_name=first_name,
        assumptions=assumptions,
        source_files=source_names,
        analysis_url=analysis_url,
    )

    if draft:
        from . import gmail_client as gc
        draft_id = gc.create_draft(to=client_email, subject=subject, body_html=body_html)
        print(f"      ✓ Draft created (ID: {draft_id})")
        print(f"        Review at: https://mail.google.com/mail/#drafts")
    else:
        from . import gmail_client as gc
        msg_id = gc.send_email(to=client_email, subject=subject, body_html=body_html)
        print(f"      ✓ Email sent (ID: {msg_id})")

    print(f"\n{'='*60}")
    print(f"  DONE — Intake scan complete for {client_name}")
    print(f"  Files scanned: {len(shared_files)} Drive + {len(emails)} email(s)")
    print(f"  Analysis doc: {analysis_url}")
    print(f"{'='*60}\n")

    return {
        "client_name": client_name,
        "shared_files": shared_files,
        "emails_found": len(emails),
        "documents_extracted": len(documents),
        "analysis_url": analysis_url,
        "assumptions": assumptions,
    }


def _build_approval_email(first_name: str, assumptions: dict,
                           source_files: list, analysis_url: str) -> str:
    """Build the branded HTML approval request email."""

    # Tools section
    tools = assumptions.get("tools", [])
    tools_html = ""
    if tools:
        rows = ""
        for t in tools:
            if isinstance(t, dict):
                rows += f"<tr><td>{t.get('tool','')}</td><td>{t.get('purpose','')}</td></tr>"
        tools_html = f"""
        <h3>Your Tools</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px;">
          <tr style="background:#f5f5f5;"><th>Tool</th><th>What you use it for</th></tr>
          {rows}
        </table>"""
    else:
        tools_html = "<h3>Your Tools</h3><p><em>Couldn't determine from your files — we'll cover this on the call.</em></p>"

    # Departments section
    depts = assumptions.get("departments", [])
    depts_html = ""
    if depts:
        items = ""
        for i, d in enumerate(depts, 1):
            if isinstance(d, dict):
                items += f"<li><strong>{d.get('role_name','')}</strong> — {d.get('description','')}</li>"
        depts_html = f"<h3>Your Departments</h3><ol>{items}</ol>"
    else:
        depts_html = "<h3>Your Departments</h3><p><em>Couldn't determine from your files — we'll cover this on the call.</em></p>"

    # Annoying task
    task = assumptions.get("annoying_task", {})
    if isinstance(task, dict) and task.get("task"):
        steps = "".join(f"<li>{s}</li>" for s in task.get("steps", []))
        task_html = f"""
        <h3>Your Most Annoying Task (My Best Guess)</h3>
        <p><strong>Task:</strong> {task.get('task','')}</p>
        <p><strong>How often:</strong> {task.get('frequency','')}</p>
        <ol>{steps}</ol>"""
    else:
        task_html = "<h3>Your Most Annoying Task</h3><p><em>Couldn't determine — tell me what you'd most like automated.</em></p>"

    # Source files
    files_list = "".join(f"<li>{f}</li>" for f in source_files) if source_files else "<li>No files found</li>"

    return f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 620px; margin: 0 auto; padding: 20px;">

  <img src="https://gbautomation.xyz/gb-logo.png" alt="GBAutomation" style="height:45px; margin-bottom:24px;" />

  <h2 style="color: #D97757;">I scanned your files — here are my assumptions</h2>

  <p>Hi {first_name},</p>

  <p>I went through the documents you sent and put together my best assumptions for your intake answers.
  <strong>Please review these and let me know what's right, wrong, or missing</strong> — just reply to this email.</p>

  <p>I've also saved a full analysis doc to your Google Drive folder:
  <a href="{analysis_url}" style="color:#D97757;">View Intake Analysis →</a></p>

  <hr style="border:none; border-top:1px solid #eee; margin:24px 0;" />

  {tools_html}
  {depts_html}
  {task_html}

  <hr style="border:none; border-top:1px solid #eee; margin:24px 0;" />

  <h3>Files I Scanned</h3>
  <ul style="font-size:13px;">{files_list}</ul>

  <h3>What I Need From You</h3>
  <p>Just reply with anything that looks wrong or incomplete. For example:</p>
  <ul>
    <li>"Add Slack to tools — I use it daily"</li>
    <li>"Annoying task is actually my weekly reporting, not X"</li>
    <li>"Morning briefing should include revenue numbers"</li>
  </ul>

  <p>Once you approve, I'll lock in your setup and we're good to go for our session.</p>

  <p>
    <strong>Greg Black</strong><br/>
    GBAutomation<br/>
    <a href="mailto:greg@gbautomation.xyz">greg@gbautomation.xyz</a>
  </p>

</body>
</html>
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan client documents and pre-fill intake form")
    parser.add_argument("--name",  required=True, help="Client full name")
    parser.add_argument("--email", required=True, help="Client email address")
    parser.add_argument("--draft", action="store_true", default=True,
                        help="Create email draft instead of sending (default)")
    parser.add_argument("--send",  action="store_true",
                        help="Send the email immediately (overrides --draft)")
    args = parser.parse_args()

    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))

    run(client_name=args.name, client_email=args.email, draft=not args.send)
