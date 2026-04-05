---
description: Send personalized InMails to non-connected high-value prospects — burns InMail credits
argument-hint: <prospect-list-file> [max-inmails] [subject-template] [body-template]
---

# LinkedIn InMail Campaign

Send personalized InMails to high-value prospects who are NOT in your network. This is the primary credit-burning skill.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser |
| OUTPUT_DIR | `.claude/context/linkedin` | Where outreach log is saved |
| MAX_INMAILS | 10 | Default max InMails per session (conservative) |

## Blocklist (MANDATORY — CRITICAL FOR THIS SKILL)

Before sending ANY InMail:
- If prospect company contains "Accenture Federal" (case-insensitive) → **SKIP silently**
- If prospect company is "Accenture" AND title contains "Federal" → **SKIP silently**
- InMails cost credits. Wasting one on a blocklisted contact is both a compliance violation AND a waste.

## Workflow

1. Read the prospect JSON file specified in {PROMPT}
2. Filter to prospects with:
   - status NOT "connected" (InMails are for non-connections)
   - fit_score >= 7 (only high-value targets — credits are precious)
   - status NOT "inmail_sent" (no duplicates)
3. Sort by fit_score descending
4. For each prospect (up to MAX_INMAILS):
   a. **Run blocklist check** — if blocked, skip and log
   b. Navigate to their LinkedIn profile
   c. Wait 5-8 seconds
   d. Take a snapshot to verify correct profile and confirm InMail button exists
   e. Click the "Message" button (InMail)
   f. Wait 2-3 seconds for the message dialog to open
   g. Fill the **Subject** field (≤200 chars) — personalized using prospect data
   h. Fill the **Message body** (≤1900 chars) — personalized, value-first, clear CTA
   i. Take a screenshot as evidence before sending
   j. Click "Send"
   k. Wait 2-3 seconds to confirm send success
   l. Log: name, company, subject, message preview, timestamp, credit estimate
   m. Wait 8-15 seconds (randomized) before next InMail

5. Save outreach log to `{OUTPUT_DIR}/{date}_inmail_log.json`
6. Update prospect status to "inmail_sent" in the source file
7. Report: total sent, credits used, credits estimated remaining, blocklisted count

## InMail Subject Templates (≤200 chars)

### Subject A — Question Hook
```
Quick question about {company}'s approach to {topic}
```

### Subject B — Value Proposition
```
Idea to help {company} automate {pain_point} — worth a quick chat?
```

### Subject C — Mutual Reference
```
{mutual_name} mentioned you'd be the right person to talk to
```

### Subject D — Content Reference
```
Your take on {post_topic} sparked an idea
```

## InMail Body Template (≤1900 chars)

```
Hi {first_name},

{personalized_hook — 1 sentence referencing something specific: their post, company news, mutual connection, or shared interest}

I run GBAutomation, where we help {industry} companies build AI-powered workflow automation — the kind that turns 2-week deployment cycles into 2-day ones.

{value_proposition — 1-2 sentences about a specific result you've achieved for a similar company, or a specific insight relevant to their situation}

Would a 15-minute call to explore whether something like this could work for {company} be worth your time? Happy to share a case study first if that's easier.

Best,
Greg
```

## Pacing Rules

- Wait 8-15 seconds between InMails (randomized — these are high-scrutiny)
- Max 10-15 InMails per session
- After every 5 InMails, pause for 2 minutes
- NEVER send more than 15 InMails in a single day
- Best times to send: Tue-Thu, 8-10am recipient's local timezone
- If CAPTCHA or "unusual activity" appears → STOP immediately

## Output Format

```json
{
  "session_date": "2026-03-02",
  "total_sent": 8,
  "credits_used": 8,
  "credits_remaining_estimate": 42,
  "total_blocklisted": 0,
  "inmails": [
    {
      "name": "...",
      "company": "...",
      "title": "...",
      "linkedin_url": "...",
      "subject": "Quick question about Acme's approach to CI/CD automation",
      "body_preview": "Hi Jane, your post about scaling...",
      "template_used": "A",
      "status": "inmail_sent",
      "timestamp": "2026-03-02T09:15:00Z",
      "screenshot": "screenshots/inmail_jane_smith_2026-03-02.png"
    }
  ],
  "blocklisted": []
}
```
