---
description: Like and comment on prospects' recent posts to warm them up before outreach
argument-hint: <prospect-list-file OR linkedin-url> [max-engagements]
---

# LinkedIn Engagement Farm

Engage with target prospects' content (likes + comments) to build familiarity before sending connection requests or InMails.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser |
| OUTPUT_DIR | `.claude/context/linkedin` | Where engagement log is saved |
| MAX_ENGAGEMENTS | 15 | Default max engagements per session |

## Blocklist (MANDATORY)

Before engaging with ANY prospect's content:
- If their company contains "Accenture Federal" (case-insensitive) → **SKIP silently**
- If their company is "Accenture" AND title contains "Federal" → **SKIP silently**

## Workflow

### If given a prospect list file:
1. Read the prospect JSON file
2. Filter to prospects with status "researched" and fit_score >= 6
3. For each prospect (up to MAX_ENGAGEMENTS):
   a. **Run blocklist check** — if blocked, skip
   b. Navigate to their LinkedIn profile
   c. Wait 3-5 seconds
   d. Click "Activity" or "Posts" tab
   e. Wait 2-3 seconds for posts to load
   f. Find 1-2 recent posts (within last 30 days)
   g. Click "Like" on the first post
   h. Wait 2-4 seconds
   i. Optionally click "Comment" on a post → write a thoughtful 1-2 sentence comment relevant to the post content (NOT promotional — add genuine value)
   j. Wait 3-5 seconds
   k. Navigate back or to next prospect
   l. Log the engagement

### If given a single LinkedIn URL:
1. Navigate directly to that profile
2. Follow steps d-j above

4. Save engagement log to `{OUTPUT_DIR}/{date}_engagement_log.json`
5. Update prospect status to "engaged" in the source file if applicable
6. Report: total likes, total comments, prospects engaged

## Comment Guidelines

- Keep comments to 1-2 sentences
- Reference something specific from the post
- Add a genuine insight or ask a thoughtful question
- Do NOT pitch, promote, or mention GBAutomation
- Do NOT use generic comments like "Great post!" or "Thanks for sharing!"

**Good examples**:
- "Interesting point about the latency-throughput tradeoff — have you found that batching helps at scale?"
- "We ran into a similar challenge with our CI pipeline. The parallel test runner approach made a huge difference."

## Pacing Rules

- Wait 3-5 seconds between profile navigations
- Wait 2-4 seconds between like and comment actions
- Max 15-20 engagements per session
- After every 8 engagements, pause for 45-60 seconds
- If CAPTCHA or "unusual activity" appears → STOP immediately

## Output Format

```json
{
  "session_date": "2026-03-02",
  "total_engagements": 12,
  "likes": 12,
  "comments": 5,
  "blocklisted": 1,
  "engagements": [
    {
      "name": "...",
      "company": "...",
      "linkedin_url": "...",
      "action": "like",
      "post_topic": "AI governance frameworks",
      "comment_text": null,
      "timestamp": "2026-03-02T10:15:00Z"
    }
  ]
}
```
