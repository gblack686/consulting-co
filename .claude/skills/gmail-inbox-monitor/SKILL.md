---
name: gmail-inbox-monitor
description: "Monitor greg@gbautomation.xyz inbox every 5 minutes. Classifies emails (client/spam/vendor/admin), auto-labels, and sends Telegram notifications."
triggers:
  - gmail
  - inbox
  - email monitor
  - check email
model: haiku
---

# Gmail Inbox Monitor

Polls Gmail inbox every 5 minutes via launchd on the Mac Mini.

## What it does

1. Fetches up to 50 unread inbox messages
2. Skips already-seen messages (state tracked in `state.json`)
3. Fast spam check (regex patterns, List-Unsubscribe header)
4. Known client matching (domain/email lookup)
5. Claude Haiku classification for unknown senders
6. Auto-labels in Gmail (Clients/{name}, Vendors, Spam-Auto)
7. Telegram notifications for client/prospect/vendor emails
8. Marks spam and admin emails as read

## Dependencies

- `google-api-python-client`, `google-auth`, `google-auth-httplib2`
- `boto3` (for AWS Secrets Manager)
- `anthropic` (for Haiku classification)

## Secrets (from AWS Secrets Manager)

- `gbautomation/google/workspace-god-token` — Gmail OAuth
- `gbautomation/telegram/bot` — Telegram bot_token + chat_id
- `gbautomation/core/anthropic-api-key` — Claude API key

## Schedule

launchd plist: `~/Library/LaunchAgents/com.gbautomation.gmail-monitor.plist`
Runs every 300 seconds (5 minutes).

## Manual run

```bash
cd ~/.openclaw/workspace/skills/gmail-inbox-monitor
python3 scripts/monitor.py
python3 scripts/monitor.py --dry-run
```
