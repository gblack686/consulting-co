---
name: intake-session-processor
description: "Post-session transcript processor for GBAutomation consulting. Triggered after any client session (AI discovery call or agent build). Pulls transcript from Google Drive, parses into structured session data, continues filling the OpenClaw workspace config, web searches answers to open questions, and generates Excalidraw architecture diagrams. Use when: new Google Meet transcript saved to Drive, client asks 'what are next steps', processing a post-session follow-up. Trigger keywords: 'process transcript', 'new transcript', 'session just ended', 'post-session', 'update openclaw config'."
---

# Session Processor Skill

## Purpose

Process any client session transcript into actionable outputs:
1. **Parse** the transcript from Google Drive
2. **Update** the OpenClaw `openclaw.json` config with new context
3. **Research** any open questions raised in the session (web search)
4. **Diagram** the agent architecture in Excalidraw (if architecture was discussed)
5. **Save** everything to the client's session folder

## When This Skill Fires

- A new Google Meet transcript appears in Drive (Google automatically saves "60 Minute Agent Build w Greg" and similar transcripts)
- User says "new transcript just saved", "we just had a session with X", "process Erica's transcript"
- Triggered after any consulting call — discovery, build, or follow-up

## Session Types

| Type | Google Meet Title Pattern | What to Update |
|------|--------------------------|----------------|
| Discovery / Intake | "AI Discovery Call w Greg ({Client})" | Full openclaw.json build from scratch |
| Agent Build | "60 Minute Agent Build w Greg ({Client})" | Flesh out existing config, add domains |
| Follow-up / Check-in | "Check-in w Greg ({Client})" | Append to MEMORY.md, update HEARTBEAT.md |

## Pipeline

### Step 1 — Find & Pull Transcript

Search Google Drive for transcripts modified in the last 24 hours:
```python
drive.files().list(
  q="name contains 'Transcript' and modifiedTime > '...' and trashed=false",
  orderBy="modifiedTime desc"
)
```
Export as plain text. Identify the client name from the file title.

### Step 2 — Locate or Create Session Folder

```
client-sessions/
└── YYYYMMDD-{client-slug}/
    ├── session_output/          ← parsed data (internal)
    │   ├── client_profile.json
    │   ├── soul_draft.md
    │   ├── identity.json
    │   ├── mission_statement.md
    │   ├── tool_inventory.json
    │   ├── autonomy.json
    │   ├── domains/             ← one JSON per domain
    │   └── research/            ← web search answers
    ├── workspace/               ← deliverable OpenClaw files
    │   ├── SOUL.md
    │   ├── USER.md
    │   ├── IDENTITY.md
    │   ├── MEMORY.md
    │   ├── AGENTS.md
    │   ├── TOOLS.md
    │   ├── HEARTBEAT.md
    │   ├── openclaw.json
    │   └── skills/
    └── diagrams/                ← Excalidraw files
        └── {client}-architecture.excalidraw
```

If the folder already exists (follow-up session), merge new info.

### Step 3 — Parse Transcript

Extract from the transcript:
- **Client profile**: name, email, business, timezone, device (phone/laptop)
- **Business context**: what they do, pain points, goals
- **Domains/workflows**: each automation or agent use case discussed
- **Tool inventory**: all apps, platforms, APIs mentioned
- **Channel preference**: how they want to talk to the agent
- **Budget**: monthly AI spend they're comfortable with
- **Open questions**: anything Greg said "I'll find out" or "Claude will figure that out"
- **Diagram triggers**: any time architecture, workflows, or system design was sketched out verbally

### Step 4 — Web Search Open Questions

For each open question from the transcript, run a `WebSearch` and save results to `session_output/research/questions-answered.md`.

Format:
```markdown
## Q: {question from transcript}
**Asked by**: Greg / Client
**Answer**: {summary}
**Sources**: {links}
**Action**: {what to do with this answer}
```

### Step 5 — Update OpenClaw Config

If `workspace/openclaw.json` does NOT exist: generate from scratch using the `consulting-intake` templates.
If it DOES exist: merge new information into the existing config.

Key fields to fill/update from session:
- `agents.list[]` — one entry per domain discussed
- `bindings[]` — route keywords to domain agents
- `channels` — set based on client's chosen messaging app
- `env` — add API key placeholders for tools mentioned
- `skills.entries{}` — one skill entry per workflow
- `cron` — enable if any scheduled tasks were discussed

### Step 6 — Generate Excalidraw Diagram

**Always create an architecture diagram** in proper Obsidian `.excalidraw.md` format:
- Save to `diagrams/{client-slug}-architecture.excalidraw.md`
- **Also save a PNG export** to `diagrams/{client-slug}-architecture.png` — every `.excalidraw.md` must have a matching `.png` alongside it
- Generate the PNG using matplotlib or a dedicated render script; never leave an `.excalidraw.md` without its paired `.png`
- Dark canvas `#1a1a1a`, `fillStyle: "hachure"` (never solid), `roughness: 1`
- Follow `excalidraw-agent.md` spec (YAML frontmatter + `# Text Elements` + `%%` Drawing block)

**Color convention:**
- Purple `#6a0dad` border / `#1a0533` fill: agent nodes
- Blue `#1e90ff` border / `#001a33` fill: external tools/APIs
- Green `#00cc66` border / `#003311` fill: channels/delivery
- Orange `#ff8c00` border / `#1a0e00` fill: client/human
- Dashed border: services with no API (browser automation)

### Step 7 — Upload to Google Drive

After all files are generated, upload the entire session folder to Drive using `upload_session_to_drive.py`:

```python
# From consulting-admin:
python -m scripts.upload_session_to_drive <local_session_path> --parent-name "GBAutomation Clients" --client-name "{Client Full Name}"
```

This creates (or reuses):
```
GBAutomation Clients/
└── {Client Full Name}/              ← one folder per client
    └── {Client} — Session {date}/  ← one folder per session
        ├── workspace/       ← OpenClaw config files
        ├── session_output/  ← JSON + research
        └── diagrams/        ← Excalidraw .excalidraw.md + matching .png
```

Pull `--client-name` from `session_output/client_profile.json` → `name` field.

Save the returned Drive folder URL and include it in the summary.

**Script location**: `consulting-admin/scripts/upload_session_to_drive.py`
**Auth**: uses god token via `google_client.drive_service()` — no OAuth prompt

### Step 8 — Output Summary

Print a clean summary:
```
=== SESSION PROCESSED: {Client Name} ===
Session: {date} ({type})
Folder:  client-sessions/{slug}/

WORKSPACE FILES:
  ✓ SOUL.md
  ✓ USER.md
  ✓ IDENTITY.md
  ✓ MEMORY.md
  ✓ AGENTS.md
  ✓ TOOLS.md
  ✓ HEARTBEAT.md
  ✓ openclaw.json  ({N} agents, {N} skills)

RESEARCH:
  ✓ {N} questions answered → research/questions-answered.md

DIAGRAMS:
  ✓ {client}-architecture.excalidraw.md  (Obsidian format, dark canvas)
  ✓ {client}-architecture.png            (paired PNG export)

DRIVE:
  ✓ {N} files uploaded → GBAutomation Clients / {Client Name} — Session {date}
  ✓ https://drive.google.com/drive/folders/{folder-id}

NEXT STEPS FOR GREG:
  1. {action item 1}
  2. {action item 2}
  ...

NEXT STEPS FOR CLIENT:
  1. {action item 1}
  ...
```

## Notes

- **Diagram = Excalidraw + PNG**: Any time the user mentions "diagram", build an `.excalidraw.md` file AND a matching `.png` in the same folder — always paired, never one without the other
- **Merge don't overwrite**: If a session folder already exists, append new info — don't clobber existing workspace files
- **Google Drive auth**: Use `consulting-admin/scripts/google_client.py` for Drive access (god token via AWS Secrets Manager)
- **Transcript location**: Google Meet auto-saves transcripts to the Drive root; search `name contains 'Transcript' and trashed=false`
