---
description: Search LinkedIn with filters, extract prospect profiles to JSON
argument-hint: <search keywords> [title filter] [company size] [location]
---

# LinkedIn Prospect Search

Search LinkedIn for prospects matching filters, extract profile data, and save to a structured JSON file.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser — must see LinkedIn activity |
| OUTPUT_DIR | `.claude/context/linkedin` | Where prospect data is saved |

## Blocklist (MANDATORY)

Before viewing or extracting ANY profile, check the company field:
- If company contains "Accenture Federal" (case-insensitive) → **SKIP silently**
- If company is "Accenture" AND title contains "Federal" → **SKIP silently**
- Log skipped prospects as `"status": "blocklisted", "rule": "accenture-federal"`

## Workflow

1. Navigate to `https://www.linkedin.com/search/results/people/` with search keywords from {PROMPT}
2. Wait for search results to load (look for "results" text)
3. Apply any additional filters if specified (title, company size, location, industry)
4. Take a snapshot of the search results page
5. For each result on the current page (max 10 per page):
   a. Extract name, title, company, location from the search card
   b. **Run blocklist check** — if blocked, skip and log
   c. Click into the profile link
   d. Wait 4-6 seconds (randomized)
   e. Take a snapshot of the profile page
   f. Extract: full name, headline, company, location, mutual connections count, mutual connection names, About section summary, recent activity (last post topic)
   g. Navigate back to search results
   h. Wait 3-5 seconds before next profile
6. After processing the page, check if there are more pages (max 3 pages per session = ~30 profiles)
7. Save results to `{OUTPUT_DIR}/{date}_prospect_research.json`
8. Report: number of profiles researched, number blocklisted, number saved

## Pacing Rules

- Wait 4-6 seconds between profile views (randomized)
- Wait 3-5 seconds after returning to search results
- Max 30 profiles per session (3 pages of 10)
- After every 10 profiles, pause for 60 seconds
- If CAPTCHA or "unusual activity" appears → STOP immediately and report

## Output Format

```json
{
  "session_date": "2026-03-02",
  "search_query": "CTO SaaS",
  "filters": { "title": "CTO", "location": "United States" },
  "total_found": 30,
  "total_blocklisted": 2,
  "prospects": [
    {
      "name": "...",
      "title": "...",
      "company": "...",
      "location": "...",
      "linkedin_url": "...",
      "mutual_connections": 3,
      "mutual_names": ["..."],
      "headline": "...",
      "about_summary": "...",
      "recent_activity": "...",
      "fit_score": null,
      "status": "researched"
    }
  ],
  "blocklisted": [
    { "name": "...", "company": "Accenture Federal Services", "rule": "accenture-federal" }
  ]
}
```
