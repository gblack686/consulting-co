---
description: Send personalized connection requests from a prospect list
argument-hint: <prospect-list-file> [max-connections] [message-template]
---

# LinkedIn Connection Blast

Send personalized connection requests to researched/engaged prospects with optional custom notes.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser |
| OUTPUT_DIR | `.claude/context/linkedin` | Where outreach log is saved |
| MAX_CONNECTIONS | 20 | Default max connection requests per session |

## Blocklist (MANDATORY — CRITICAL FOR THIS SKILL)

Before sending ANY connection request:
- If prospect company contains "Accenture Federal" (case-insensitive) → **SKIP silently**
- If prospect company is "Accenture" AND title contains "Federal" → **SKIP silently**
- This check is NON-NEGOTIABLE. A connection request cannot be unsent.

## Workflow

1. Read the prospect JSON file specified in {PROMPT}
2. Filter to prospects with status "researched" or "engaged" (prefer "engaged" first)
3. Sort by fit_score descending (highest value targets first)
4. For each prospect (up to MAX_CONNECTIONS):
   a. **Run blocklist check** — if blocked, skip and log
   b. Navigate to their LinkedIn profile
   c. Wait 4-6 seconds
   d. Take a snapshot to verify correct profile
   e. Look for the "Connect" button. If not found (already connected, or "Follow" only), skip and log as "already_connected" or "connect_unavailable"
   f. Click "Connect"
   g. If "Add a note" option appears, click it
   h. Fill the note field with a personalized message (≤300 characters):
      - Use the prospect's first name
      - Reference a mutual connection if available
      - Reference their recent post if status is "engaged"
      - Keep it conversational, NOT salesy
   i. Click "Send"
   j. Wait 5-10 seconds (randomized) before next prospect
   k. Log: name, company, note sent, timestamp

5. Save outreach log to `{OUTPUT_DIR}/{date}_outreach_log.json`
6. Update prospect status to "connection_sent" in the source file
7. Report: total sent, total skipped (already connected, unavailable, blocklisted)

## Connection Note Templates (≤300 chars)

### Template A — Mutual Connection
```
Hi {first_name}, I see we're both connected to {mutual_name}. I work in AI workflow automation and {company}'s work caught my eye. Would love to connect.
```

### Template B — Post Engagement
```
Hi {first_name}, enjoyed your recent post about {post_topic}. I'm working on similar challenges in the AI automation space. Would be great to connect.
```

### Template C — Industry Peer
```
Hi {first_name}, fellow {industry} practitioner here. Your work at {company} on {topic} is impressive. Always looking to connect with sharp minds in the space.
```

### Template D — No Note (if note option unavailable)
Just click Send without a note.

## Pacing Rules

- Wait 5-10 seconds between connection requests (randomized)
- Max 20-25 connections per session
- After every 10 requests, pause for 90 seconds
- If any request shows an error or unusual behavior → pause for 5 minutes
- If CAPTCHA or "unusual activity" appears → STOP immediately

## Output Format

```json
{
  "session_date": "2026-03-02",
  "total_sent": 18,
  "total_skipped": 4,
  "total_blocklisted": 1,
  "connections": [
    {
      "name": "...",
      "company": "...",
      "linkedin_url": "...",
      "note_sent": "Hi Jane, enjoyed your recent post about...",
      "template_used": "B",
      "status": "connection_sent",
      "timestamp": "2026-03-02T10:30:00Z"
    }
  ],
  "skipped": [
    { "name": "...", "reason": "already_connected" }
  ],
  "blocklisted": [
    { "name": "...", "company": "Accenture Federal Services", "rule": "accenture-federal" }
  ]
}
```
