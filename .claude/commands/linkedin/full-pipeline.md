---
model: opus
description: Full LinkedIn outreach pipeline — research, engage, connect, InMail in sequence with pacing breaks
argument-hint: <search-keywords> [title-filter] [max-prospects]
---

# LinkedIn Full Pipeline

Orchestrates the complete LinkedIn outreach funnel in a single session with mandatory pacing breaks between phases.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser |
| OUTPUT_DIR | `.claude/context/linkedin` | Where all data is saved |

## Blocklist (MANDATORY — ENFORCED AT EVERY PHASE)

Before ANY interaction with ANY prospect at ANY phase:
- If company contains "Accenture Federal" (case-insensitive) → **SKIP silently**
- If company is "Accenture" AND title contains "Federal" → **SKIP silently**

## Pipeline Phases

### Phase 1: Credit Check (2 min)
Run `/linkedin:credit-check` workflow steps to assess budget.
- Record: InMail credits available, pending connections
- Determine campaign intensity based on credits remaining

### Phase 2: Profile Views Harvest (5 min)
Run `/linkedin:profile-views-harvest` workflow steps.
- Extract warm leads from profile viewers
- Add fit prospects to today's target list

### Phase 3: Prospect Search (15-20 min)
Run `/linkedin:prospect-search` workflow steps with {PROMPT} keywords.
- Search and extract up to 20 profiles
- Save to `{date}_prospect_research.json`
- **Mandatory break: pause 5 minutes after this phase**

### Phase 4: Engagement Farming (10-15 min)
Run `/linkedin:engagement-farm` workflow steps on top 10 prospects by fit_score.
- Like 1-2 posts per prospect
- Comment on 3-5 posts total (only where you have genuine insight)
- **Mandatory break: pause 3 minutes after this phase**

### Phase 5: Connection Requests (10-15 min)
Run `/linkedin:connection-blast` workflow steps.
- Send connection requests to "engaged" prospects first, then "researched"
- Max 15 connections in full pipeline mode (save some weekly budget)
- Use personalized notes referencing engagement where applicable
- **Mandatory break: pause 5 minutes after this phase**

### Phase 6: InMail Campaign (10-15 min)
Run `/linkedin:inmail-campaign` workflow steps.
- Target: non-connected prospects with fit_score >= 8
- Max 8 InMails in full pipeline mode (save some monthly budget)
- Prioritize prospects where connection was unavailable

### Phase 7: Session Report
Run `/linkedin:session-report` workflow steps.
- Aggregate all activity
- Save report
- Display summary

## Total Session Time: ~60-75 minutes

## Session Limits (Full Pipeline Mode)

| Action | Pipeline Max | Rationale |
|--------|-------------|-----------|
| Profile views | 25 | Leave room for manual browsing |
| Engagements | 12 | Focus on quality over quantity |
| Connection requests | 15 | ~75% of daily conservative limit |
| InMails | 8 | ~50% of daily conservative limit |

These are intentionally lower than standalone skill limits to avoid overloading LinkedIn in a single concentrated session.

## Abort Conditions

At ANY point during the pipeline:
- CAPTCHA or "unusual activity" → STOP all phases, save progress, generate partial report
- Rate limit warning → Pause for 15 minutes, then decide whether to continue
- Account restriction → STOP immediately, do NOT continue, generate incident report

## Output

All individual phase outputs are saved to `{OUTPUT_DIR}/` with today's date prefix, plus a final session report at `{OUTPUT_DIR}/{date}_session_report.md`.
