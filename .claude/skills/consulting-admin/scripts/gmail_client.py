"""
Gmail operations for consulting admin — sends as greg@gbautomation.xyz.
"""
import base64
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import google_client

SENDER = "greg@gbautomation.xyz"
SENDER_NAME = "Greg Black | GBAutomation"


def send_email(to: str, subject: str, body_html: str, body_text: str = None, cc: str = None) -> str:
    """Send an email. Returns Gmail message ID."""
    gmail = google_client.gmail_service()

    message = MIMEMultipart("alternative")
    message["to"] = to
    message["from"] = f"{SENDER_NAME} <{SENDER}>"
    message["subject"] = subject
    if cc:
        message["cc"] = cc

    if body_text:
        message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
    return result["id"]


def create_draft(to: str, subject: str, body_html: str, body_text: str = None,
                  reply_to_message_id: str = None) -> str:
    """Create a draft. If reply_to_message_id is given, thread it as a reply."""
    gmail = google_client.gmail_service()

    # If replying, fetch original message headers for threading
    thread_id = None
    if reply_to_message_id:
        orig = gmail.users().messages().get(
            userId="me", id=reply_to_message_id, format="metadata",
            metadataHeaders=["From", "To", "Subject", "Message-ID", "References"],
        ).execute()
        orig_headers = {h["name"]: h["value"] for h in orig["payload"].get("headers", [])}
        thread_id = orig.get("threadId")

        # Use original recipient as To if not specified
        if not to:
            to = orig_headers.get("From", "")
        # Prefix subject with Re: if not already
        if not subject:
            orig_subj = orig_headers.get("Subject", "")
            subject = orig_subj if orig_subj.lower().startswith("re:") else f"Re: {orig_subj}"

    message = MIMEMultipart("alternative")
    message["to"] = to
    message["from"] = f"{SENDER_NAME} <{SENDER}>"
    message["subject"] = subject

    # Threading headers
    if reply_to_message_id and orig_headers:
        msg_id = orig_headers.get("Message-ID", "")
        refs = orig_headers.get("References", "")
        if msg_id:
            message["In-Reply-To"] = msg_id
            message["References"] = f"{refs} {msg_id}".strip()

    if body_text:
        message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    draft = gmail.users().drafts().create(
        userId="me", body=draft_body
    ).execute()
    return draft["id"]


def get_emails_from(sender_email: str, max_results: int = 20) -> list[dict]:
    """
    Fetch emails received from sender_email.
    Returns list of dicts: {id, subject, date, snippet, body, drive_links}.
    """
    gmail = google_client.gmail_service()

    results = gmail.users().messages().list(
        userId="me",
        q=f"from:{sender_email}",
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg_meta in messages:
        msg = gmail.users().messages().get(
            userId="me",
            id=msg_meta["id"],
            format="full",
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        body = _extract_body(msg["payload"])

        emails.append({
            "id": msg_meta["id"],
            "subject": headers.get("Subject", "(no subject)"),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
            "body": body,
            "drive_links": extract_drive_links(body),
        })

    return emails


def _extract_body(payload: dict) -> str:
    """Recursively extract plain text body from Gmail message payload."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""

    if payload.get("mimeType") == "text/html":
        data = payload.get("body", {}).get("data", "")
        html = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""
        # Strip HTML tags for plain text
        return re.sub(r"<[^>]+>", " ", html)

    # Multipart — recurse into parts
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text.strip():
            return text

    return ""


def extract_drive_links(text: str) -> list[str]:
    """Extract Google Drive/Docs/Sheets links from text."""
    pattern = r"https://(?:docs|drive)\.google\.com/[^\s\"\'>]+"
    return list(set(re.findall(pattern, text)))


def build_welcome_email_html(client_name: str, folder_url: str, doc_urls: dict, signature_url: str = None) -> str:
    """Build the branded HTML welcome email."""
    doc_links = ""
    for doc_name, url in doc_urls.items():
        doc_links += f'<li><a href="{url}">{doc_name}</a></li>\n'

    return f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">

  <img src="https://gbautomation.xyz/gb-logo.png" alt="GBAutomation" style="height:50px; margin-bottom:20px;" />

  <h2 style="color: #D97757;">Welcome, {client_name} — Let's Build Your Agent</h2>

  <p>Hi {client_name},</p>

  <p>I'm excited to get started on your custom AI agent system. I've set up your client workspace in Google Drive with everything you need for our session.</p>

  <h3>Your Client Folder</h3>
  <p><a href="{folder_url}" style="color: #D97757;">📁 Open Your GBAutomation Workspace</a></p>

  <h3>Documents Inside</h3>
  <ul>
{doc_links}
  </ul>

  <h3>Next Steps</h3>
  <ol>
    <li><strong>Review the Service Agreement</strong> — sign and return before our session</li>
    <li><strong>Complete the Pre-Session Prep Guide</strong> — takes ~15 min, makes the session much more productive</li>
    <li><strong>Review the Session Agenda</strong> — so you know what to expect</li>
  </ol>

  <p>If you have any questions before our call, just reply to this email.</p>

  <p>Looking forward to working with you,</p>

  <p>
    <strong>Greg Black</strong><br/>
    GBAutomation<br/>
    <a href="mailto:greg@gbautomation.xyz">greg@gbautomation.xyz</a>
  </p>

</body>
</html>
"""
