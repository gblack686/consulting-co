"""
Email Watcher
==============
Checks greg@gbautomation.xyz for new emails since the last run.
Classifies each email (client, spam, vendor, admin, transcript).
Auto-creates Gmail labels per client, marks spam as read, and notifies via Telegram.

State file: state/email_watcher.json  (tracks seen message IDs + label cache)

Usage:
    python -m scripts.email_watcher
    python -m scripts.email_watcher --dry-run
"""
import base64
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
STATE_FILE = SKILL_ROOT / "state" / "email_watcher.json"

# Known clients: domain/email patterns -> label name
# Add new clients here or let the classifier auto-detect them
KNOWN_CLIENTS = {
    "fischgroup.com": "Clients/Fisch Group",
    "piermontbrands.com": "Clients/Fisch Group",
    "ecaplow@fischgroup.com": "Clients/Fisch Group",
    "mike@piermontbrands.com": "Clients/Fisch Group",
}

# Spam patterns — emails matching these are marked read + labeled Spam immediately
SPAM_PATTERNS = [
    r"unsubscribe",
    r"no-?reply@",
    r"noreply@",
    r"marketing@",
    r"promotions?@",
    r"newsletter",
    r"@linkedin\.com",       # LinkedIn notification noise
    r"@quora\.com",
    r"@medium\.com",
    r"do-not-reply@",
    r"mailer-daemon@",
]


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"seen_ids": [], "label_ids": {}}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_or_create_label(gmail, label_name: str, label_cache: dict) -> str:
    """Get a Gmail label ID by name, creating it (and parent) if needed."""
    if label_name in label_cache:
        return label_cache[label_name]

    # Check if label already exists
    results = gmail.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        if label["name"] == label_name:
            label_cache[label_name] = label["id"]
            return label["id"]

    # Create parent label if nested (e.g. "Clients" for "Clients/Fisch Group")
    if "/" in label_name:
        parent = label_name.rsplit("/", 1)[0]
        get_or_create_label(gmail, parent, label_cache)

    # Create the label
    body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    created = gmail.users().labels().create(userId="me", body=body).execute()
    label_cache[label_name] = created["id"]
    return created["id"]


def apply_label(gmail, msg_id: str, label_id: str):
    """Add a label to a message."""
    gmail.users().messages().modify(
        userId="me", id=msg_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def mark_as_read(gmail, msg_id: str):
    """Remove UNREAD label from a message."""
    gmail.users().messages().modify(
        userId="me", id=msg_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def is_spam_by_pattern(sender: str, subject: str, headers: dict) -> bool:
    """Quick check against known spam patterns before hitting Claude."""
    text = f"{sender} {subject}".lower()
    for pat in SPAM_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    # Check List-Unsubscribe header (bulk senders)
    if headers.get("List-Unsubscribe"):
        return True
    return False


def classify_email(sender: str, subject: str, snippet: str) -> dict:
    """Use Claude Haiku to classify an email. Returns {category, client_name, confidence}.

    Categories: client, prospect, vendor, admin, spam, other
    Uses the Anthropic API directly (key from AWS Secrets Manager).
    """
    prompt = f"""Classify this email to greg@gbautomation.xyz (AI consulting firm GBAutomation).

From: {sender}
Subject: {subject}
Preview: {snippet}

Return ONLY a JSON object with these fields:
- "category": one of "client", "prospect", "vendor", "admin", "spam", "other"
- "client_name": if category is "client" or "prospect", the company/person name (title case). null otherwise.
- "confidence": float 0-1

Rules:
- "client" = existing client or someone we have meetings with
- "prospect" = new business inquiry or potential client
- "vendor" = SaaS tools, services, invoices from providers
- "admin" = internal, calendar, system notifications (Google, GitHub, etc.)
- "spam" = marketing, newsletters, unsolicited outreach, mass emails
- For client_name, use the company name not the person name (e.g. "Fisch Group" not "Emil Caplow")
"""
    try:
        import os
        from .secret_cache import get_secret
        # OAuth token from AWS works with Anthropic SDK
        api_key = os.environ.get("ANTHROPIC_API_KEY") or get_secret(
            "gbautomation/core/anthropic-api-key", region="us-east-1"
        )

        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  Classification error: {e}")

    return {"category": "other", "client_name": None, "confidence": 0.0}


def match_known_client(sender: str) -> str | None:
    """Check if sender matches a known client domain/email."""
    sender_lower = sender.lower()
    for pattern, label in KNOWN_CLIENTS.items():
        if pattern.lower() in sender_lower:
            return label
    return None


def run(dry_run: bool = False):
    from . import google_client, telegram_client
    from .transcript_agent import is_transcript_email, handle_transcript_email

    state = load_state()
    seen_ids = set(state.get("seen_ids", []))
    label_cache = state.get("label_ids", {})

    gmail = google_client.gmail_service()

    # Fetch recent inbox messages
    results = gmail.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=50,
    ).execute()

    new_count = 0
    transcript_count = 0
    spam_count = 0
    labeled_count = 0

    for meta in results.get("messages", []):
        if meta["id"] in seen_ids:
            continue

        msg = gmail.users().messages().get(
            userId="me", id=meta["id"], format="full",
            metadataHeaders=["From", "Subject", "Date", "List-Unsubscribe"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        sender = headers.get("From", "Unknown")
        subject = headers.get("Subject", "(no subject)")
        snippet = msg.get("snippet", "")[:120]

        # Skip emails we sent
        if "greg@gbautomation.xyz" in sender.lower():
            seen_ids.add(meta["id"])
            continue

        # --- 1. Route transcript emails to the transcript agent ---
        if is_transcript_email(headers, snippet):
            body_text = snippet
            for part in msg["payload"].get("parts", []):
                if part.get("mimeType") == "text/plain":
                    data = part["body"].get("data", "")
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                        break

            try:
                handle_transcript_email(meta["id"], headers, body_text, dry_run=dry_run)
                transcript_count += 1
            except Exception as e:
                print(f"  Transcript agent error: {e}")
                telegram_client.send(
                    f"⚠️ <b>Transcript Processing Failed</b>\n"
                    f"<b>Subject:</b> {html.escape(subject)}\n"
                    f"<b>Error:</b> {html.escape(str(e)[:200])}"
                )
            seen_ids.add(meta["id"])
            new_count += 1
            continue

        # --- 2. Fast spam check (pattern-based, no API call) ---
        if is_spam_by_pattern(sender, subject, headers):
            if not dry_run:
                spam_label_id = get_or_create_label(gmail, "Spam-Auto", label_cache)
                apply_label(gmail, meta["id"], spam_label_id)
                mark_as_read(gmail, meta["id"])
            spam_count += 1
            seen_ids.add(meta["id"])
            new_count += 1
            continue

        # --- 3. Check known client list (fast, no API call) ---
        known_label = match_known_client(sender)
        if known_label:
            if not dry_run:
                label_id = get_or_create_label(gmail, known_label, label_cache)
                apply_label(gmail, meta["id"], label_id)
            labeled_count += 1
            telegram_client.send(
                f"📬 <b>{html.escape(known_label)}</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )
            seen_ids.add(meta["id"])
            new_count += 1
            continue

        # --- 4. Claude classification for unknown senders ---
        classification = classify_email(sender, subject, snippet)
        category = classification.get("category", "other")
        client_name = classification.get("client_name")

        if category == "spam":
            if not dry_run:
                spam_label_id = get_or_create_label(gmail, "Spam-Auto", label_cache)
                apply_label(gmail, meta["id"], spam_label_id)
                mark_as_read(gmail, meta["id"])
            spam_count += 1

        elif category in ("client", "prospect") and client_name:
            label_name = f"Clients/{client_name}"
            if not dry_run:
                label_id = get_or_create_label(gmail, label_name, label_cache)
                apply_label(gmail, meta["id"], label_id)
            labeled_count += 1
            telegram_client.send(
                f"📬 <b>{html.escape(label_name)}</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )

        elif category == "vendor":
            if not dry_run:
                label_id = get_or_create_label(gmail, "Vendors", label_cache)
                apply_label(gmail, meta["id"], label_id)
            telegram_client.send(
                f"🏷️ <b>Vendor</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )

        elif category == "admin":
            if not dry_run:
                mark_as_read(gmail, meta["id"])

        else:
            telegram_client.send(
                f"📬 <b>New Email</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )

        seen_ids.add(meta["id"])
        new_count += 1

    state["seen_ids"] = list(seen_ids)
    state["label_ids"] = label_cache
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {new_count} new — {transcript_count} transcript, {spam_count} spam, {labeled_count} labeled")


if __name__ == "__main__":
    import os
    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))
    dry = "--dry-run" in sys.argv
    run(dry_run=dry)
