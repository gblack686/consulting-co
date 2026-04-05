---
name: consulting-admin
description: Consulting admin agent for GBAutomation workspace operations — client onboarding, Google Drive setup, email drafting, calendar events. Uses greg@gbautomation.xyz via permanent workspace OAuth token.
triggers:
  - new client
  - onboard client
  - consulting admin
  - client folder
  - send welcome email
  - create drive folder
model: sonnet
---

# Consulting Admin Skill

Manages GBAutomation consulting operations using Google Workspace (Gmail, Drive, Calendar) for `greg@gbautomation.xyz`.

## Credentials

Uses the permanent workspace god token stored in AWS Secrets Manager:
- **Secret**: `gbautomation/google/workspace-god-token`
- **Scopes**: Gmail, Drive, Calendar, Contacts
- **Never expires** (Internal Google Workspace app)

## Skills

### `new-client` — Onboard a New Client

Creates the full client workspace in one command:

```bash
cd .claude/skills/consulting-admin
pip install -r requirements.txt   # first time only

# Draft mode (review email before sending)
python -m scripts.new_client --name "Jason Diaz" --email "jid5274@gmail.com" --draft

# Live mode (sends immediately)
python -m scripts.new_client --name "Jason Diaz" --email "jid5274@gmail.com"
```

**What it does:**
1. Creates `GBAutomation Clients / {Client Name} / Onboarding/` folder in Drive
2. Creates 5 branded Google Docs inside `Onboarding/` (filled templates):
   - Welcome Email & Overview
   - Service Agreement
   - Pre-Session Prep Guide
   - Session Agenda
   - Key Terms Glossary
3. Shares folder with client (viewer) + personal/workspace accounts (editor)
4. Sends welcome email from greg@gbautomation.xyz with folder link
5. Generates 17-slide onboarding deck (PPTX) and uploads to `Onboarding/`

**Templates source**: `../consulting-intake/client-facing/`
**Branding**: `assets/gb-logo.png` inserted at top of each doc; cream/terracotta brand colors in deck

---

### `generate-deck` — Generate Branded Onboarding Deck

Creates a 17-slide PPTX onboarding presentation for a client. Called automatically by `new-client` (step 5), but can also be run standalone.

```bash
cd .claude/skills/consulting-admin

# Standalone (override defaults)
python -m scripts.generate_client_deck \
  --name "Erica Cruz" \
  --email "artbycruzcreations@gmail.com" \
  --session-date "Thursday, March 5, 2026" \
  --session-time "4:00 PM" \
  --timezone "PST" \
  --meet-link "https://meet.google.com/vjk-dvpq-nfe"
```

**Output**: `output/{kebab-name}-onboarding.pptx`

**Slides:**
1. Title — client name, session date/time, Meet link
2. What to Expect
3. Deliverables
4. Pre-Session Checklist (with Meet link)
5. Voice Intake Option (Meet link for verbal onboarding)
6. Tool Inventory (fillable)
7. Departments & Team
8. Most Annoying Recurring Task
9. Morning Briefing preference
10. Agent Personality Style
11. Session Agenda Overview
12. After Session — Delivery Timeline
13. Key Terms — Agent Concepts
14. Key Terms — Autonomy & Control
15. Models Reference
16. Pricing Tiers
17. Next Steps

**Brand**: Cream (`#F3F1E7`) / Terracotta (`#D97757`) — matches gb-automation-landing design system.

---

### `scan-client` — Scan Client Documents & Pre-Fill Intake

After a client shares files or sends emails, this scans everything and generates
intake assumptions for Greg's review, then drafts an approval email.

```bash
cd .claude/skills/consulting-admin

# Scan and create draft email (default)
python -m scripts.scan_client --name "Jason Diaz" --email "jid5274@gmail.com"

# Scan and send immediately
python -m scripts.scan_client --name "Jason Diaz" --email "jid5274@gmail.com" --send
```

**What it does:**
1. Scans Drive for all files Jason shared with greg@gbautomation.xyz
2. Scans Gmail for emails from Jason + extracts any Drive links in them
3. Exports text from Google Docs, Sheets, plain text files
4. Copies all client files into `Jason Diaz / Onboarding/` folder
5. Runs Claude (claude-sonnet-4-6) to fill out all 5 intake form questions as assumptions
6. Creates `Intake Analysis — Jason Diaz` Google Doc in Onboarding folder
7. Drafts (or sends) approval email to Jason with assumptions table + analysis link

**Approval email subject**: `I reviewed your files — here are my assumptions for your setup, Jason`

---

## File Structure

```
consulting-admin/
├── SKILL.md                     ← this file
├── config.yaml                  ← company info, pricing, delivery windows
├── requirements.txt             ← includes anthropic SDK
├── assets/
│   ├── gb-logo.png              ← header logo for branded docs
│   └── gb-signature.png         ← email signature image
├── output/                      ← generated PPTX decks (gitignored)
│   └── {client-name}-onboarding.pptx
└── scripts/
    ├── __init__.py
    ├── google_client.py         ← auth: loads god token from AWS Secrets
    ├── drive_manager.py         ← Drive folder/doc/sharing/upload operations
    ├── gmail_client.py          ← send/draft/scan emails as greg@gbautomation.xyz
    ├── intake_filler.py         ← Claude-powered intake form analyzer
    ├── new_client.py            ← onboarding: creates {Client}/Onboarding/ + 5 docs + deck
    ├── generate_client_deck.py  ← 17-slide PPTX generator (cream/terracotta brand)
    └── scan_client.py           ← scans client files, fills intake, drafts email
```

**Drive folder structure** (per client):
```
GBAutomation Clients/
└── {Client Name}/
    └── Onboarding/
        ├── Welcome Email & Overview
        ├── Service Agreement
        ├── Pre-Session Prep Guide
        ├── Session Agenda
        ├── Key Terms Glossary
        ├── [From {Client}] {shared file 1}   ← copied from client's Drive
        ├── [From {Client}] {shared file 2}
        └── Intake Analysis — {Client Name}   ← auto-generated by scan_client
```

## Google Meet Intake (Active)

The Pre-Session Prep Guide includes an **optional voice intake** section — clients can hop on Meet instead of filling out the written exercises. They talk through their tools, workflows, departments, and preferences for 10–20 minutes, and the session is auto-transcribed via Google Workspace Business Plus.

**Admin settings configured:**
- Recording: ON (manual — host presses record)
- Meeting transcripts: ON
- Automatic transcription: **ON** (transcription starts the moment the meeting begins)

The `{video_call_link}` placeholder in the prep guide is filled by the `new_client.py` script (currently set to "TBD"). To make this fully automated, wire `new_client.py` to create a Calendar event with a Meet link per client and pass the URL as `{video_call_link}`.

---

## Roadmap / Future Skills

- `draft-email` — AI-draft any email for review before sending
- `schedule-call` — Create calendar event + send invite
- `client-status` — Check where a client is in the pipeline
- `followup` — Draft a follow-up based on email thread context
