---
type: expert-file
parent: "[[linkedin/_index]]"
file-type: command
command-name: "plan"
human_reviewed: false
tags: [expert-file, command, planning, linkedin]
---

# LinkedIn Expert - Plan Mode

> Create LinkedIn outreach and automation plans informed by credit budgets, pacing rules, and prospect targeting.

## Purpose
Plan LinkedIn automation campaigns using proven patterns from the LinkedIn expertise. Produces a spec with workflow selection, prospect targeting, pacing strategy, credit budget, and expected outputs.

## Usage
```
/experts:linkedin:plan [user_request]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Task`, `Write`

---

## Planning Framework

### Step 1: Campaign Type Selection

What kind of LinkedIn activity does the user need?

| Need | Workflow | Credit Cost |
|------|----------|-------------|
| Find prospects | Profile Research & Export | Profile views only |
| Warm up leads | Engagement Farming | No credits (likes/comments are free) |
| Grow network | Connection Request Campaign | Connection request limit (weekly) |
| Cold outreach to non-connections | InMail Campaign | InMail credits |
| Identify warm leads | Who Viewed Profile Harvesting | None |
| Full pipeline | Combined (research → engage → connect → InMail) | All credit types |

### Step 2: Prospect Targeting

Who are we targeting?

| Filter | Options |
|--------|---------|
| Title/Seniority | C-suite, VP, Director, Manager, IC |
| Company size | Startup (1-50), SMB (50-500), Enterprise (500+) |
| Industry | SaaS, FinTech, HealthTech, AI/ML, etc. |
| Location | US, Canada, UK, EU, APAC |
| Relationship | 1st, 2nd, 3rd+ degree |
| Keywords | Job title keywords, company keywords, skill keywords |

### Step 3: Credit Budget

How many credits will this campaign consume?

| Action | Per-Action Cost | Session Limit | Weekly Limit |
|--------|----------------|---------------|--------------|
| Profile view | 0 (Premium) | 40-50 | 200 |
| Connection request | 1 request | 20-25 | 80 |
| Connection w/ note | 1 request | 20-25 | 80 |
| InMail | 1 credit | 10-15 | 50 |
| Like/Comment | 0 | 15-20 | 100 |

### Step 4: Pacing Strategy

How will we stay under detection thresholds?

| Session Length | Actions | Breaks |
|---------------|---------|--------|
| Quick (15 min) | 10-15 profile views, 5 connections | None needed |
| Standard (45 min) | 30 views, 15 connections, 5 InMails | 5 min break at 25 min |
| Extended (90 min) | 50 views, 25 connections, 10 InMails | 10 min break every 30 min |

### Step 5: Message Personalization

What personalization variables are available?

| Variable | Source | Required |
|----------|--------|----------|
| `{first_name}` | Profile snapshot | Yes |
| `{company}` | Profile snapshot | Yes |
| `{title}` | Profile snapshot | Yes |
| `{mutual_connection}` | Profile snapshot | If available |
| `{recent_post_topic}` | Activity tab | For engagement-first approach |
| `{shared_interest}` | Profile skills/groups | Optional |
| `{event_name}` | Manual input | For event-based outreach |

### Step 6: Validation

How to verify the campaign is working:

- [ ] Chrome DevTools MCP connected to LinkedIn-authenticated Chrome profile
- [ ] Prospect list loaded with valid LinkedIn URLs
- [ ] Message templates personalized (no raw `{variables}` sent)
- [ ] Pacing delays implemented (3-8s between navigations)
- [ ] CAPTCHA detection active (abort on challenge)
- [ ] Credit tracking active (log remaining credits)
- [ ] Output files saving to `.claude/context/linkedin/`

---

## Plan Output Format

```markdown
# LinkedIn Campaign Plan: {Title}

## Campaign Analysis
| Property | Value |
|----------|-------|
| Campaign type | {Research / Engagement / Connection / InMail / Full Pipeline} |
| Target audience | {title + industry + company size} |
| Prospect count | {estimated number} |
| Credit budget | {InMails: N, Connections: N} |
| Timeline | {days/weeks} |
| Pacing | {conservative / moderate / aggressive} |

## Workflow Steps
1. {Step 1 — e.g., "Build prospect list from LinkedIn search"}
2. {Step 2 — e.g., "Engage with top 20 prospects' content"}
3. {Step 3 — e.g., "Send connection requests with personalized notes"}
4. {Step 4 — e.g., "Send InMails to remaining high-value non-connections"}

## Message Templates

### Connection Note (≤300 chars)
{template with variables}

### InMail Subject
{template with variables}

### InMail Body
{template with variables}

## Pacing Rules
| Action | Delay | Session Max | Daily Max |
|--------|-------|-------------|-----------|
| Profile view | 3-8s | {n} | {n} |
| Connection request | 5-10s | {n} | {n} |
| InMail | 8-15s | {n} | {n} |

## Safety
- Abort on: {CAPTCHA, unusual activity, verification prompt}
- Fallback: {pause for 24h, switch to manual}

## Output Files
| File | Purpose |
|------|---------|
| `.claude/context/linkedin/{date}_prospect_research.json` | Research data |
| `.claude/context/linkedin/{date}_outreach_log.json` | Send tracking |

## Success Metrics
- [ ] {N} prospects researched
- [ ] {N} connections sent (target: {X}% acceptance)
- [ ] {N} InMails sent (target: {X}% reply rate)
- [ ] {N} meetings booked
```

---

## Examples

### Example 1: "Burn all my InMail credits this month"
**Campaign type**: InMail Campaign
**Plan**: Load existing prospect list → prioritize by fit score → send personalized InMails → track credits → follow up non-replies

### Example 2: "Find CTOs at mid-size SaaS companies"
**Campaign type**: Profile Research & Export
**Plan**: Search with filters → snapshot each profile → extract data → save to prospect_master.json → score by fit

### Example 3: "Warm up 50 prospects before outreach"
**Campaign type**: Engagement Farming → Connection Request
**Plan**: Week 1-2: Like/comment on prospects' posts → Week 3: Send connection requests → Week 4: InMail remaining non-connected

### Example 4: "Full outreach campaign for AI consulting"
**Campaign type**: Full Pipeline
**Plan**: Research 100 prospects → engage top 50 → connect with 50 → InMail 20 non-connected → convert replies to discovery calls
