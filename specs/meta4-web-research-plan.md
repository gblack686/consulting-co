# META-4: Web Research / Market Intelligence Agent — Build Plan
**Date:** 2026-03-18
**Build location:** `.claude/skills/consulting-intake/templates/agents/research/`

---

## What to Build

A general-purpose research agent that ships with every OpenClaw workspace. Handles competitive intel, trend tracking, API documentation discovery, and signal enrichment via web search, page fetching, and scheduled market scans.

---

## Files to Create

```
templates/agents/research/
├── SOUL.md
├── IDENTITY.md
├── AGENTS.md
└── skills/
    ├── web-search/SKILL.md
    ├── fetch-page/SKILL.md
    └── market-scan/SKILL.md

references/research-agent.md
```

---

## SOUL.md Spec

```
Name: Scout 🔍 (or {research_agent_name} from client profile)

Core Truths:
1. Cite everything — no claim without a source URL
2. Structured output only — JSON or markdown tables, not prose dumps
3. Recency matters — prefer sources from last 90 days
4. Signal over noise — summarize insights, not raw content

Boundaries:
- Never post or interact with external sites
- Never store credentials found during research
- Flag paywalled content rather than trying to bypass it
```

---

## IDENTITY.md Spec

```
Role: Market Intelligence Agent
Domain: {client_industry}
Topics: {research_topics}  ← from session_output/client_profile.json
Output format: Structured markdown → Telegram summary → Obsidian archive
Frequency: Weekly competitive scan (cron) + on-demand searches
```

---

## web-search/SKILL.md Spec

**Backends (in priority order):**
1. Brave Search API (via `badlogic/pi-skills` or direct API)
2. Perplexity API (via OpenRouter)
3. `oh-my-pi` web search extension

**Input:** Query string + optional `recency` (day/week/month)

**Output:**
```json
[
  {"title": "...", "url": "...", "snippet": "...", "date": "..."},
  ...
]
```

**Workflow:**
1. Run search query
2. Filter to results from last `recency` period
3. Rank by relevance (title keyword match)
4. Return top 10 as JSON

---

## fetch-page/SKILL.md Spec

Clean page content extraction.

**Backends:**
1. Jina Reader: `https://r.jina.ai/{url}` — returns clean markdown
2. Readability fallback via headless Chrome

**Input:** URL

**Output:** Clean markdown of page content + extracted links

**Use cases:**
- Fetch competitor pricing pages
- Extract API documentation
- Read blog posts for morning brief

---

## market-scan/SKILL.md Spec

Scheduled weekly competitive intelligence scan.

**Trigger:** Weekly cron (Sunday night) + on-demand

**Config (from `workspace/data/research-config.json`):**
```json
{
  "topics": ["{topic1}", "{topic2}"],
  "competitors": ["{competitor1}", "{competitor2}"],
  "subreddits": ["{subreddit1}"],
  "sources": ["web", "youtube", "reddit"]
}
```

**Workflow:**
1. For each topic: run web-search (last 7 days)
2. For each competitor: check their website for new content
3. Fetch top results with fetch-page
4. Summarize top 3-5 insights per topic
5. Write to Obsidian: `Research/Market Scan/{YYYY-MM-DD}.md`
6. Send Telegram summary: "This week in {client_industry}: [3 bullets]"

---

## references/research-agent.md Spec

Document:
- Brave Search API setup (key in Secrets Manager: `{client}/brave-search-api-key`)
- Jina Reader usage (no auth required)
- Perplexity via OpenRouter (model: `perplexity/sonar`)
- How `research-config.json` is populated during consulting-intake Step 1
- Reddit monitoring option (no auth needed for public subreddits via old.reddit.com)
- Obsidian output folder convention
- How to add new topics without redeploying

---

## Acceptance Criteria

- [ ] All 3 SKILL.md files pass `skill-format-spec.md` validation
- [ ] `web-search` skill works with at least one backend (Brave or Perplexity)
- [ ] `fetch-page` skill returns clean markdown from a test URL
- [ ] `market-scan` generates a valid Obsidian note
- [ ] `references/research-agent.md` documents all setup steps
- [ ] `consulting-intake/SKILL.md` Step 2b references research agent as universal template
- [ ] `{research_topics}` placeholder is populated from `client_profile.json` during intake

---

## Prompt for OpenClaw

> "Build the Web Research agent from the spec at `specs/meta4-web-research-plan.md`. Create all files under `templates/agents/research/`: SOUL.md, IDENTITY.md, and 3 skills (web-search, fetch-page, market-scan). Create `references/research-agent.md`. Primary search backend: Brave Search API via OpenRouter. Page fetcher: Jina Reader at `https://r.jina.ai/{url}`. All outputs should write to Obsidian and send Telegram summaries."
