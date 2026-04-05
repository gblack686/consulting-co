---
description: Scrape "Who viewed your profile" into a prospect list of warm leads
argument-hint: [max-profiles]
---

# LinkedIn Profile Views Harvest

Extract people who viewed your LinkedIn profile — these are warm leads who already showed interest.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser |
| OUTPUT_DIR | `.claude/context/linkedin` | Where data is saved |

## Blocklist (MANDATORY)

Before recording ANY viewer, check company:
- If company contains "Accenture Federal" (case-insensitive) → **SKIP silently**
- If company is "Accenture" AND title contains "Federal" → **SKIP silently**

## Workflow

1. Navigate to `https://www.linkedin.com/me/profile-views/`
2. Wait for the page to load (look for "Who viewed your profile" or viewer cards)
3. Take a snapshot
4. For each viewer visible on the page:
   a. Extract: name, title/headline, company, time of view
   b. **Run blocklist check** — if blocked, skip
   c. Assess fit: does their title/company match GBAutomation ICP? (CTO, VP Eng, Head of AI at 50-500 employee SaaS/FinTech/HealthTech/AI companies)
   d. Assign fit_score (1-10 based on title seniority + company relevance)
5. Scroll down to load more viewers if available (max 50 viewers)
6. Wait 2-3 seconds between scrolls
7. Save to `{OUTPUT_DIR}/{date}_profile_views.json`
8. Report: total viewers, fit prospects found, blocklisted count

## Output Format

```json
{
  "session_date": "2026-03-02",
  "total_viewers": 25,
  "fit_prospects": 8,
  "blocklisted": 1,
  "viewers": [
    {
      "name": "...",
      "title": "...",
      "company": "...",
      "viewed_when": "2 days ago",
      "fit_score": 7,
      "status": "researched",
      "recommended_action": "connection_request"
    }
  ]
}
```
