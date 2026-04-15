#!/usr/bin/env python3
"""
Gmail Inbox Monitor for Sebastian (Mac Mini OpenClaw Agent)
============================================================
Polls greg@gbautomation.xyz inbox, classifies emails, auto-labels,
and sends Telegram notifications.

State: ~/.openclaw/workspace/skills/gmail-inbox-monitor/state.json

Usage:
    python3 monitor.py
    python3 monitor.py --dry-run
"""
import base64
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SKILL_DIR = Path(__file__).parent.parent
STATE_FILE = SKILL_DIR / "state.json"
CACHE_FILE = SKILL_DIR / ".secret_cache.json"
CACHE_TTL = 3600  # 1 hour

AWS_REGION = "us-east-1"
GMAIL_SECRET = "gbautomation/google/workspace-god-token"
TELEGRAM_SECRET = "gbautomation/telegram/bot"
ANTHROPIC_SECRET = "gbautomation/core/anthropic-api-key"

KNOWN_CLIENTS = {
    "fischgroup.com": "Clients/Fisch Group",
    "piermontbrands.com": "Clients/Fisch Group",
    "ecaplow@fischgroup.com": "Clients/Fisch Group",
    "mike@piermontbrands.com": "Clients/Fisch Group",
}

SPAM_PATTERNS = [
    r"unsubscribe", r"no-?reply@", r"noreply@", r"marketing@",
    r"promotions?@", r"newsletter", r"@linkedin\.com", r"@quora\.com",
    r"@medium\.com", r"do-not-reply@", r"mailer-daemon@",
]

# ---------------------------------------------------------------------------
# Secret cache (self-contained, no relative imports)
# ---------------------------------------------------------------------------
def get_secret(secret_id: str) -> dict:
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            pass

    entry = cache.get(secret_id)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL:
        return entry["value"]

    import boto3
    sm = boto3.client("secretsmanager", region_name=AWS_REGION)
    value = json.loads(sm.get_secret_value(SecretId=secret_id)["SecretString"])
    cache[secret_id] = {"ts": time.time(), "value": value}
    CACHE_FILE.write_text(json.dumps(cache))
    return value


# ---------------------------------------------------------------------------
# Gmail auth
# ---------------------------------------------------------------------------
def gmail_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    secret = get_secret(GMAIL_SECRET)
    creds = Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        token_uri=secret["token_uri"],
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=secret["scopes"],
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
def telegram_send(message: str):
    import urllib.request
    cfg = get_secret(TELEGRAM_SECRET)
    url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
    payload = json.dumps({
        "chat_id": cfg["chat_id"],
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  Telegram error: {e}")


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
def is_spam_by_pattern(sender: str, subject: str, headers: dict) -> bool:
    text = f"{sender} {subject}".lower()
    for pat in SPAM_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    if headers.get("List-Unsubscribe"):
        return True
    return False


def match_known_client(sender: str):
    sender_lower = sender.lower()
    for pattern, label in KNOWN_CLIENTS.items():
        if pattern.lower() in sender_lower:
            return label
    return None


def classify_email(sender: str, subject: str, snippet: str) -> dict:
    prompt = f"""Classify this email to greg@gbautomation.xyz (AI consulting firm GBAutomation).

From: {sender}
Subject: {subject}
Preview: {snippet}

Return ONLY a JSON object:
- "category": one of "client", "prospect", "vendor", "admin", "spam", "other"
- "client_name": company/person name (title case) if client/prospect, null otherwise
- "confidence": float 0-1

Rules:
- "client" = existing client or someone we have meetings with
- "prospect" = new business inquiry or potential client
- "vendor" = SaaS tools, services, invoices from providers
- "admin" = internal, calendar, system notifications (Google, GitHub, etc.)
- "spam" = marketing, newsletters, unsolicited outreach
"""
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY") or get_secret(ANTHROPIC_SECRET)
        if isinstance(api_key, dict):
            api_key = api_key.get("api_key", api_key.get("key", ""))

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


# ---------------------------------------------------------------------------
# Gmail helpers
# ---------------------------------------------------------------------------
def get_or_create_label(gmail, label_name: str, label_cache: dict) -> str:
    if label_name in label_cache:
        return label_cache[label_name]

    results = gmail.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        if label["name"] == label_name:
            label_cache[label_name] = label["id"]
            return label["id"]

    if "/" in label_name:
        parent = label_name.rsplit("/", 1)[0]
        get_or_create_label(gmail, parent, label_cache)

    body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    created = gmail.users().labels().create(userId="me", body=body).execute()
    label_cache[label_name] = created["id"]
    return created["id"]


def apply_label(gmail, msg_id: str, label_id: str):
    gmail.users().messages().modify(
        userId="me", id=msg_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def mark_as_read(gmail, msg_id: str):
    gmail.users().messages().modify(
        userId="me", id=msg_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(dry_run: bool = False):
    # Load state
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    seen_ids = set(state.get("seen_ids", []))
    label_cache = state.get("label_ids", {})

    gmail = gmail_service()

    results = gmail.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=50,
    ).execute()

    new_count = spam_count = labeled_count = 0

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

        # Skip our own emails
        if "greg@gbautomation.xyz" in sender.lower():
            seen_ids.add(meta["id"])
            continue

        # 1. Fast spam check
        if is_spam_by_pattern(sender, subject, headers):
            if not dry_run:
                spam_label_id = get_or_create_label(gmail, "Spam-Auto", label_cache)
                apply_label(gmail, meta["id"], spam_label_id)
                mark_as_read(gmail, meta["id"])
            spam_count += 1
            seen_ids.add(meta["id"])
            new_count += 1
            continue

        # 2. Known client match
        known_label = match_known_client(sender)
        if known_label:
            if not dry_run:
                label_id = get_or_create_label(gmail, known_label, label_cache)
                apply_label(gmail, meta["id"], label_id)
            labeled_count += 1
            telegram_send(
                f"📬 <b>{html.escape(known_label)}</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )
            seen_ids.add(meta["id"])
            new_count += 1
            continue

        # 3. Claude classification
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
            telegram_send(
                f"📬 <b>{html.escape(label_name)}</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )

        elif category == "vendor":
            if not dry_run:
                label_id = get_or_create_label(gmail, "Vendors", label_cache)
                apply_label(gmail, meta["id"], label_id)
            telegram_send(
                f"🏷️ <b>Vendor</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )

        elif category == "admin":
            if not dry_run:
                mark_as_read(gmail, meta["id"])

        else:
            telegram_send(
                f"📬 <b>New Email</b>\n"
                f"<b>From:</b> {html.escape(sender)}\n"
                f"<b>Subject:</b> {html.escape(subject)}\n"
                f"<i>{html.escape(snippet)}</i>"
            )

        seen_ids.add(meta["id"])
        new_count += 1

    # Save state
    state["seen_ids"] = list(seen_ids)[-500:]  # Keep last 500 to prevent unbounded growth
    state["label_ids"] = label_cache
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {new_count} new — {spam_count} spam, {labeled_count} labeled")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run(dry_run=dry)
