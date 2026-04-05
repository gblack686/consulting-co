"""
One-off Gmail tasks:
1. Mark emails from specific senders as read.
2. Search for emails from "Grant" with PowerPoint attachments.

Run from consulting-admin/ as:
    python -m scripts.gmail_tasks
"""
import base64
import re
from . import google_client


# ─────────────────────────────────────────────────────────────────────────────
# 1. MARK AS READ
# ─────────────────────────────────────────────────────────────────────────────

MARK_READ_QUERIES = [
    ("Paramount+",
     "from:paramountplus.com OR from:paramount.com OR from:info.paramountplus.com"),
    ("Google Workspace Team",
     'from:workspace-noreply@google.com OR from:(google.com) subject:"Google Workspace"'),
    ("Max / founderpass.com",
     "from:max.com OR from:founderpass.com OR from:hbomax.com"),
    ("noreply-dmarc-support@google.com",
     "from:noreply-dmarc-support@google.com"),
    ("Google Pay notification",
     "from:googlepay-noreply@google.com OR from:pay-noreply@google.com"),
]


def mark_as_read_query(service, label: str, query: str) -> int:
    """
    Find ALL messages (unread) matching query and remove UNREAD label.
    Returns the count of messages marked read.
    """
    q_unread = f"({query}) is:unread"
    page_token = None
    total = 0

    while True:
        params = dict(userId="me", q=q_unread, maxResults=500)
        if page_token:
            params["pageToken"] = page_token
        result = service.users().messages().list(**params).execute()
        messages = result.get("messages", [])

        if messages:
            ids = [m["id"] for m in messages]
            service.users().messages().batchModify(
                userId="me",
                body={"ids": ids, "removeLabelIds": ["UNREAD"]},
            ).execute()
            total += len(ids)

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return total


# ─────────────────────────────────────────────────────────────────────────────
# 2. SEARCH FOR GRANT + PPT/PPTX ATTACHMENT
# ─────────────────────────────────────────────────────────────────────────────

def _decode(data: str) -> str:
    if not data:
        return ""
    padding = 4 - len(data) % 4
    return base64.urlsafe_b64decode(data + "=" * (padding % 4)).decode("utf-8", errors="replace")


def extract_body_and_attachments(payload: dict) -> tuple:
    """Return (plain_text_body, list_of_attachment_dicts)."""
    body_parts: list[str] = []
    attachments: list[dict] = []

    def walk(part):
        mime = part.get("mimeType", "")
        filename = part.get("filename", "")

        if filename:
            attachments.append({
                "filename": filename,
                "mimeType": mime,
                "size": part.get("body", {}).get("size", 0),
                "attachmentId": part.get("body", {}).get("attachmentId", ""),
            })
            return  # don't descend into attachment parts

        if mime == "text/plain":
            body_parts.append(_decode(part.get("body", {}).get("data", "")))
        elif mime == "text/html" and not body_parts:
            html = _decode(part.get("body", {}).get("data", ""))
            body_parts.append(re.sub(r"<[^>]+>", " ", html))

        for child in part.get("parts", []):
            walk(child)

    walk(payload)
    return "\n".join(body_parts).strip(), attachments


def search_grant_pptx(service) -> list[dict]:
    """
    Search for emails from someone named 'Grant' with a PowerPoint attachment.
    Returns full message details for matching emails.
    """
    queries = [
        "from:grant has:attachment filename:pptx",
        "from:grant has:attachment filename:ppt",
        "from:grant has:attachment",        # broader sweep — filter by attachment extension below
    ]

    seen_ids: set = set()
    candidate_ids: list[str] = []

    for q in queries:
        result = service.users().messages().list(
            userId="me", q=q, maxResults=50
        ).execute()
        for m in result.get("messages", []):
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                candidate_ids.append(m["id"])

    hits = []
    for msg_id in candidate_ids:
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        body, attachments = extract_body_and_attachments(msg["payload"])

        sender_from = headers.get("From", "")

        # Must be from someone whose display name or address contains "grant"
        if "grant" not in sender_from.lower():
            continue

        # Find PowerPoint attachments
        ppt_attachments = [
            a for a in attachments
            if (
                a["filename"].lower().endswith((".pptx", ".ppt"))
                or "presentation" in a["mimeType"].lower()
                or "powerpoint" in a["mimeType"].lower()
            )
        ]

        if not ppt_attachments:
            continue

        hits.append({
            "id": msg_id,
            "sender_raw": sender_from,
            "subject": headers.get("Subject", "(no subject)"),
            "date": headers.get("Date", ""),
            "body": body,
            "all_attachments": attachments,
            "ppt_attachments": ppt_attachments,
        })

    return hits


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    svc = google_client.gmail_service()

    print("=" * 64)
    print("TASK 1 — Marking emails as read")
    print("=" * 64)
    for label, query in MARK_READ_QUERIES:
        count = mark_as_read_query(svc, label, query)
        print(f"  {label:<45} {count} marked read")

    print()
    print("=" * 64)
    print("TASK 2 — Searching for emails from Grant with PPT attachment")
    print("=" * 64)

    hits = search_grant_pptx(svc)

    if not hits:
        print("  No emails found from 'Grant' with a PowerPoint attachment.")
    else:
        for i, h in enumerate(hits, 1):
            print(f"\n--- Match {i} ---")
            print(f"  Sender     : {h['sender_raw']}")
            print(f"  Subject    : {h['subject']}")
            print(f"  Date       : {h['date']}")
            print(f"  PPT files  : {[a['filename'] for a in h['ppt_attachments']]}")
            print("  All attachments:")
            for a in h["all_attachments"]:
                size_kb = round(a["size"] / 1024, 1) if a["size"] else 0
                print(f"    - {a['filename']}  ({a['mimeType']}, {size_kb} KB)")
            print(f"  Body:\n{'-'*40}\n{h['body'][:3000]}\n{'-'*40}")

    print("\nDone.")


if __name__ == "__main__":
    main()
