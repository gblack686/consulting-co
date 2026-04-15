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


def build_welcome_email_html(client_name: str, folder_url: str, doc_urls: dict,
                              booking_url: str = "https://calendar.app.google/X4SN26PYLgvVYPRp8",
                              intro_html: str = None,
                              ps_text: str = None,
                              signature_url: str = None) -> str:
    """Build the branded HTML welcome email with GBAutomation styling.

    Args:
        client_name: First name of the client.
        folder_url: Google Drive folder URL for the client workspace.
        doc_urls: Dict of {doc_title: google_doc_url} for workspace docs.
        booking_url: Calendar booking link for CTA button.
        intro_html: Optional personalized intro HTML inserted between greeting
                     and workspace section. Should contain styled <p>, <h3>,
                     <table> blocks matching the email's inline styles.
                     If None, uses generic "I'm excited to get started" intro.
        ps_text: Optional P.S. line (plain text, no HTML needed).
        signature_url: Optional signature image URL.
    """
    # --- Reusable style tokens ---
    P = 'style="color: #2D2D2D; font-size: 15px; line-height: 1.6; margin: 0 0 16px 0;"'
    H3 = 'style="color: #2D2D2D; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #D97757; padding-bottom: 8px; margin: 0 0 12px 0;"'

    # --- Doc links table rows ---
    doc_links = ""
    for doc_name, url in doc_urls.items():
        doc_links += (
            f'<tr><td style="padding: 8px 12px; border-bottom: 1px solid #E8E5DA;">'
            f'<a href="{url}" style="color: #D97757; text-decoration: none; font-weight: 500;">{doc_name}</a>'
            f'</td></tr>\n'
        )

    # --- Intro section ---
    if intro_html:
        intro_block = intro_html
    else:
        intro_block = f"""
              <p {P}>I'm excited to get started on your custom AI agent system. I've set up your client workspace in Google Drive with everything you need for our session.</p>
"""

    # --- P.S. section ---
    ps_block = ""
    if ps_text:
        ps_block = f"""
              <hr style="border: none; border-top: 1px solid #E8E5DA; margin: 24px 0 16px 0;" />
              <p style="color: #888; font-size: 13px; font-style: italic; line-height: 1.5; margin: 0;">{ps_text}</p>
"""

    return f"""
<html>
<body style="margin: 0; padding: 0; background-color: #F3F1E7; font-family: Arial, Helvetica, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #F3F1E7; padding: 24px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px;">

          <!-- Header -->
          <tr>
            <td style="background-color: #FFFFFF; padding: 24px 32px; border-radius: 8px 8px 0 0; border-bottom: 3px solid #D97757; text-align: center;">
              <img src="https://drive.google.com/uc?export=view&id=1q_1Q2nX_PcB15P0DtcJ5BxFc8Q9ojGIR" alt="GBAutomation" style="height: 60px; margin-bottom: 8px;" />
              <br/>
              <span style="color: #D97757; font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">AI-Powered Automation Systems</span>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background-color: #FFFFFF; padding: 32px; border-left: 1px solid #E8E5DA; border-right: 1px solid #E8E5DA;">

              <h2 style="color: #D97757; font-size: 20px; margin: 0 0 20px 0;">Welcome, {client_name} — Let's Build Your Agent</h2>

              <p {P}>Hi {client_name},</p>

              <!-- Personalized intro -->
{intro_block}

              <!-- Workspace Section -->
              <h3 {H3}>Your Client Workspace</h3>
              <table cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0;">
                <tr>
                  <td style="background-color: #F3F1E7; padding: 12px 20px; border-radius: 6px; border-left: 4px solid #D97757;">
                    <a href="{folder_url}" style="color: #D97757; text-decoration: none; font-weight: 600; font-size: 15px;">Open Your GBAutomation Workspace</a>
                  </td>
                </tr>
              </table>

              <!-- Documents -->
              <h3 {H3}>Documents Inside</h3>
              <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0;">
{doc_links}
              </table>

              <!-- Next Steps -->
              <h3 {H3}>Next Steps</h3>
              <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0;">
                <tr>
                  <td style="padding: 8px 0; color: #2D2D2D; font-size: 15px; line-height: 1.6;">
                    <strong>1.</strong> <strong>Review the Service Agreement</strong> — sign and return before our session
                  </td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; color: #2D2D2D; font-size: 15px; line-height: 1.6;">
                    <strong>2.</strong> <strong>Complete the Pre-Session Prep Guide</strong> — takes ~15 min, makes the session much more productive
                  </td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; color: #2D2D2D; font-size: 15px; line-height: 1.6;">
                    <strong>3.</strong> <strong>Review the Session Agenda</strong> — so you know what to expect
                  </td>
                </tr>
              </table>

              <!-- Booking CTA -->
              <table cellpadding="0" cellspacing="0" style="margin: 0 auto 24px auto;">
                <tr>
                  <td align="center" style="background-color: #D97757; border-radius: 6px;">
                    <a href="{booking_url}" style="display: inline-block; padding: 14px 32px; color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 15px; letter-spacing: 0.5px;">Book Your 30-Min Discovery Call</a>
                  </td>
                </tr>
              </table>

              <p style="color: #2D2D2D; font-size: 15px; line-height: 1.6; margin: 0 0 8px 0;">If you have any questions before our call, just reply to this email.</p>

              <p style="color: #2D2D2D; font-size: 15px; line-height: 1.6; margin: 0 0 0 0;">Looking forward to building with you,</p>
{ps_block}

              <!-- Signature -->
              <table cellpadding="0" cellspacing="0" style="margin-top: 24px;">
                <tr>
                  <td style="border-left: 3px solid #D97757; padding-left: 12px;">
                    <strong style="color: #2D2D2D; font-size: 15px;">Greg Black</strong><br/>
                    <span style="color: #D97757; font-size: 13px; font-weight: 600;">GBAutomation</span><br/>
                    <a href="mailto:greg@gbautomation.xyz" style="color: #888; font-size: 13px; text-decoration: none;">greg@gbautomation.xyz</a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #2D2D2D; padding: 16px 32px; border-radius: 0 0 8px 8px; text-align: center;">
              <span style="color: #D97757; font-size: 12px; font-weight: 700; letter-spacing: 1px;">GBAUTOMATION</span>
              <span style="color: rgba(255,255,255,0.4); font-size: 11px;">&nbsp;&nbsp;&bull;&nbsp;&nbsp;</span>
              <a href="https://gbautomation.xyz" style="color: rgba(255,255,255,0.6); font-size: 11px; text-decoration: none;">gbautomation.xyz</a>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
