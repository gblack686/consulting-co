# OpenClaw SKILL.md Format Specification

Source: https://docs.openclaw.ai/skills

## File Location

Skills live in the workspace skills directory:
```
~/.openclaw/workspace/skills/{domain}/{workflow}/SKILL.md
```

Loading precedence: workspace skills > ~/.openclaw/skills > bundled skills

## Required Format

```markdown
---
name: skill-name
description: "{category}: {Skill Name} - {what it does}"
---

# Skill Title

Instructions for the agent to follow when this skill is invoked.
```

## Frontmatter Fields

### Required
| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Kebab-case identifier (e.g., `write-newsletter`) |
| `description` | string | Format: `"{category}: {Name} - {purpose}"` |

### Optional
| Field | Type | Notes |
|-------|------|-------|
| `user-invocable` | boolean | If true, user can trigger via `/skill-name` |
| `disable-model-invocation` | boolean | If true, model cannot auto-invoke |
| `metadata` | JSON | **MUST BE SINGLE-LINE** — parser breaks on multiline |

## CRITICAL: metadata Format

The `metadata` field MUST be a single-line JSON string. This is the #1 deployment-breaking issue.

### Correct
```yaml
metadata: {"openclaw": {"requires": {"env": ["API_KEY"]}}}
```

### WRONG (breaks parser)
```yaml
metadata:
  openclaw:
    requires:
      env:
        - API_KEY
```

### metadata.openclaw.requires

Gating conditions — skill won't load unless all requirements are met:

| Key | Purpose | Example |
|-----|---------|---------|
| `bins` | Required CLI tools | `["ffmpeg", "yt-dlp"]` |
| `env` | Required env vars | `["CONVERTKIT_API_KEY"]` |
| `config` | Required config keys | `["channels.telegram"]` |
| `os` | Required OS | `["linux", "darwin"]` |

## Token Impact

Each loaded skill adds ~24 tokens to every agent turn. Keep skill count reasonable — 20 skills adds ~480 tokens of overhead per turn.

## Description Format Convention

Follow this pattern for consistency:
```
"{Category}: {Skill Name} - {one-line purpose}"
```

Examples:
- `"Content: Write Newsletter - Draft and send weekly newsletter via ConvertKit"`
- `"Business: Sync Pipeline - Update CRM pipeline from deal activity"`
- `"Personal: Morning Brief - Deliver personalized morning summary"`
- `"Analytics: Weekly Report - Generate and deliver KPI dashboard"`

## Skill Body Best Practices

1. **Start with purpose** — one sentence explaining what this skill does
2. **List allowed tools** — constrain what the agent can use
3. **Phased workflow** — numbered steps grouped into phases
4. **Approval gates** — mark human-in-the-loop points with `[APPROVAL GATE]`
5. **Output format** — specify what the result looks like
6. **Error handling** — what to do when steps fail
7. **Delivery** — where the output goes (announce, webhook, file)

## Cron Integration

Skills can be triggered by cron jobs. The cron definition is separate from the skill:

```bash
# One-shot (runs once)
openclaw cron add --name "Send report" \
  --at "2026-03-01T09:00:00" --tz "America/New_York" \
  --skill "weekly-report" --mode main --delivery announce

# Interval
openclaw cron add --name "Check inbox" \
  --every "30m" \
  --skill "check-inbox" --mode isolated --delivery none

# Cron expression
openclaw cron add --name "Morning brief" \
  --cron "0 7 * * *" --tz "America/New_York" \
  --skill "morning-brief" --mode main --delivery announce
```

### Schedule Types
| Type | Flag | Example |
|------|------|---------|
| One-shot | `--at` | `"2026-03-01T09:00:00"` |
| Interval | `--every` | `"30m"`, `"2h"`, `"1d"` |
| Cron | `--cron` | `"0 7 * * *"` (7am daily) |

### Execution Modes
| Mode | Behavior |
|------|----------|
| `main` | Runs in the user's main session (has memory context) |
| `isolated` | Runs in a fresh session (no memory bleed) |

### Delivery Modes
| Mode | Behavior |
|------|----------|
| `announce` | Sends result to configured channel (WhatsApp/Telegram/etc.) |
| `webhook` | POSTs result to a URL |
| `none` | Silent execution (logs only) |

## Example: Complete SKILL.md

```markdown
---
name: write-newsletter
description: "Content: Write Newsletter - Draft and send weekly newsletter via ConvertKit"
metadata: {"openclaw": {"requires": {"env": ["CONVERTKIT_API_KEY"]}}}
---

# Write Newsletter

Draft and publish a weekly newsletter for {client_name}.

## Allowed Tools
`Read, Write, Bash, WebSearch`

## Workflow

### Phase 1: Gather Content
1. Read recent content from memory (last 7 days)
2. Check {content_sources} for new material
3. Identify top 3 stories/updates

### Phase 2: Draft
1. Write newsletter following {client_name}'s style:
   - Tone: {vibe}
   - Length: {word_count} words
   - Structure: {template_structure}
2. Include links to full content where available

### Phase 3: Review
1. **[APPROVAL GATE]** Send draft to {delivery_channel} for review
2. Wait for approval or edits

### Phase 4: Publish
1. POST to ConvertKit API: `POST /v3/broadcasts`
2. Confirm send status
3. Log result to memory

## Output Format
```
Newsletter sent: "{subject_line}"
Subscribers: {count}
Status: {sent|scheduled|failed}
```

## Error Handling
- ConvertKit API down → save draft locally, retry in 30m
- No content found → notify user, skip this week
- Draft rejected → incorporate feedback, redraft (max 2 attempts)
```
