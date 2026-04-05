---
type: expert-file
parent: "[[linkedin/_index]]"
file-type: expertise
human_reviewed: false
source: linkedin-premium-features + agent-browser-wsl + chrome-devtools-mcp
last_validated: 2026-03-02
tags: [expert-file, mental-model, linkedin, browser-automation, lead-gen, networking]
---

# LinkedIn Expertise (Complete Mental Model)

> **Sources**: LinkedIn Premium/Sales Navigator feature set, MCP Chrome DevTools browser automation, agent-browser WSL patterns, consulting outreach workflows

---

## Part 1: The LinkedIn Credit System

LinkedIn gates outreach and discovery behind several credit types. The goal is to **burn every credit before the monthly reset** to maximize ROI on the Premium subscription.

### Credit Types

| Credit Type | Subscription | Monthly Allocation | Rollover | Purpose |
|-------------|-------------|-------------------|----------|---------|
| **InMail credits** | Premium Business | 15/month | Up to 90 banked | Direct message anyone (even non-connections) |
| **InMail credits** | Sales Navigator Core | 50/month | Up to 150 banked | Same, higher volume |
| **Profile views** | Premium | Unlimited | N/A | See who viewed you + view anyone |
| **Search filters** | Premium | Advanced | N/A | Company size, seniority, function |
| **Sales Navigator credits** | Sales Nav | 25 saved leads/week | N/A | Save leads to lists |
| **Search appearances** | Premium | Enhanced | N/A | Appear higher in recruiter search |

### Credit Recovery Rules

- InMails that get a **reply within 90 days** are **refunded** — so good targeting = infinite InMails
- Withdrawn/declined connection requests do NOT return credits
- Accepted InMails refund the credit even if reply is negative

### Monthly Credit Burn Strategy

| Week | Focus | Actions |
|------|-------|---------|
| Week 1 | Targeting | Build prospect lists, save leads, research profiles |
| Week 2 | Warm outreach | Send connection requests to warm leads (mutual connections, engaged with your content) |
| Week 3 | InMail campaign | Send InMails to high-value prospects not in network |
| Week 4 | Follow-up + cleanup | Follow up on pending InMails, exhaust remaining credits |

---

## Part 2: Browser Automation Strategy

### Why Agent Browser WSL

LinkedIn aggressively detects automation. The strategy uses **claude-bowser** (MCP Chrome DevTools) connected to the user's **real Chrome profile** where LinkedIn is already authenticated.

| Approach | Auth | Detection Risk | Speed | Verdict |
|----------|------|----------------|-------|---------|
| LinkedIn API (official) | OAuth | None | Fast | Limited to approved apps only |
| Playwright headless | No cookies | Very high — instant ban | Fast | Do NOT use |
| Puppeteer/Selenium | Injected cookies | High | Medium | Fragile, ban risk |
| **MCP Chrome DevTools** | Real Chrome profile | Low — real browser, human-like | Slow-deliberate | **Best approach** |
| Agent Browser WSL | WSL Playwright | Medium | Medium | Fallback for non-auth pages |

### Key Principle: Human-Speed Automation

LinkedIn monitors:
- Click velocity (too fast = bot)
- Scroll patterns (linear scrolling = bot)
- Time between page loads (< 3s between pages = suspicious)
- Number of profile views per hour (> 80 = throttled)
- Search result pagination speed

**Mandatory pacing rules**:
- Wait 3-8 seconds between page navigations
- Wait 1-3 seconds between clicks
- Limit profile views to 40-50 per session
- Limit InMails to 10-15 per session
- Limit connection requests to 20-25 per session
- Take breaks: 10-15 min pause every 30 min of activity
- Randomize wait times (don't use fixed intervals)

### Session Safety

| Guard | Implementation |
|-------|---------------|
| Rate limit | Track actions per session, hard-stop at limits |
| Cooldown | Minimum 3s between navigations via `evaluate_script` sleep |
| Session cap | Max 2 hours continuous automation per day |
| Detection check | After every 10 actions, check for CAPTCHA/challenge page |
| Abort trigger | If "unusual activity" or "verify identity" appears, stop immediately |

---

## Part 3: Core LinkedIn Workflows

### Workflow 1: Profile Research & Export

**Purpose**: View target profiles, extract key info for personalized outreach.

**Steps**:
1. Navigate to LinkedIn search with filters (title, company, location)
2. `take_snapshot` to capture search results
3. For each result: `click` profile link → wait 4s → `take_snapshot` → extract name, title, company, mutual connections, recent activity
4. Save to structured output (JSON/CSV)
5. Navigate back → next result

**Output**: `.claude/context/linkedin/{date}_prospect_research.json`

### Workflow 2: Connection Request Campaign

**Purpose**: Send personalized connection requests to researched prospects.

**Steps**:
1. Load prospect list from research output
2. For each prospect: navigate to profile → `click` Connect button
3. If "Add a note" option: `click` it → `fill` with personalized message (≤300 chars)
4. `click` Send
5. Log result (sent/pending/already_connected)
6. Wait 5-10s before next

**Pacing**: Max 20-25 per session, spread across the week.

**Message Template Variables**:
- `{first_name}` — prospect first name
- `{mutual_connection}` — shared connection name
- `{company}` — their company
- `{topic}` — relevant shared interest or industry topic

### Workflow 3: InMail Campaign

**Purpose**: Burn InMail credits on high-value prospects outside your network.

**Steps**:
1. Load high-priority prospects (not connected, high title, target company)
2. Navigate to profile → `click` "Message" (InMail button)
3. `fill` subject line (≤200 chars, personalized)
4. `fill` message body (≤1900 chars, value-first, clear CTA)
5. `click` Send
6. Log: prospect name, subject, timestamp, credit count remaining
7. Wait 8-15s before next (InMails are higher-scrutiny)

**Pacing**: Max 10-15 per session.

### Workflow 4: Engagement Farming

**Purpose**: Increase visibility by engaging with target prospects' content before outreach.

**Steps**:
1. Navigate to prospect's Activity/Posts tab
2. `click` Like on 2-3 recent posts
3. Optionally `click` Comment → `fill` with thoughtful 1-2 sentence comment
4. Wait 1-2 days, then send connection request (warm lead now)

**Pacing**: 15-20 engagements per session.

### Workflow 5: Who Viewed Your Profile Harvesting

**Purpose**: Identify warm leads who already showed interest.

**Steps**:
1. Navigate to `linkedin.com/me/profile-views/`
2. `take_snapshot` → extract viewer names, titles, companies
3. For each viewer: assess fit → add to prospect list if relevant
4. Send connection request with "I noticed you viewed my profile" angle

---

## Part 4: MCP Chrome DevTools Patterns for LinkedIn

### Navigation

```javascript
// Navigate to LinkedIn search
navigate_page({ url: "https://www.linkedin.com/search/results/people/?keywords=CTO%20SaaS&origin=GLOBAL_SEARCH_HEADER" })

// Wait for results to load
wait_for({ text: ["results"], timeout: 10000 })
```

### Snapshot & Data Extraction

```javascript
// Take snapshot to read page content
take_snapshot()  // Returns a11y tree with uid identifiers

// Extract via JS evaluation
evaluate_script({
  function: `() => {
    const cards = document.querySelectorAll('.reusable-search__result-container');
    return Array.from(cards).map(card => ({
      name: card.querySelector('.entity-result__title-text a span[aria-hidden="true"]')?.textContent?.trim(),
      title: card.querySelector('.entity-result__primary-subtitle')?.textContent?.trim(),
      location: card.querySelector('.entity-result__secondary-subtitle')?.textContent?.trim()
    }));
  }`
})
```

### Form Filling (Connection Notes, InMails)

```javascript
// Fill InMail subject
fill({ uid: "subject-input-uid", value: "Quick question about your AI strategy" })

// Fill InMail body
fill({ uid: "message-body-uid", value: "Hi {first_name}, I noticed..." })

// Click Send
click({ uid: "send-button-uid" })
```

### Anti-Detection Helpers

```javascript
// Random delay between actions (3-8 seconds)
evaluate_script({
  function: `() => new Promise(r => setTimeout(r, 3000 + Math.random() * 5000))`
})

// Simulate human-like scroll
evaluate_script({
  function: `() => {
    const scrollStep = () => {
      window.scrollBy(0, 100 + Math.random() * 200);
      if (window.scrollY < document.body.scrollHeight - window.innerHeight) {
        setTimeout(scrollStep, 500 + Math.random() * 1000);
      }
    };
    scrollStep();
    return 'scrolling';
  }`
})

// Check for CAPTCHA or challenge
evaluate_script({
  function: `() => {
    const body = document.body.innerText;
    if (body.includes('unusual activity') || body.includes('security verification') || body.includes('CAPTCHA')) {
      return 'BLOCKED';
    }
    return 'OK';
  }`
})
```

---

## Part 5: InMail Best Practices

### Subject Line Patterns (≤200 chars)

| Pattern | Example | When to Use |
|---------|---------|-------------|
| Question hook | "Quick question about {company}'s AI roadmap" | Decision makers |
| Mutual connection | "{mutual_name} suggested I reach out" | When you have a referral |
| Value-first | "Idea to cut {company}'s deployment time by 40%" | Technical leaders |
| Event-based | "Enjoyed your talk at {event}" | After conferences |
| Content-based | "Your post on {topic} resonated" | After engagement farming |

### Message Body Structure

```
Line 1: Personal hook (why them specifically)
Line 2: Credibility marker (brief — not a pitch)
Line 3: Value proposition (what's in it for them)
Line 4: Soft CTA (low commitment ask)
```

**Example**:
```
Hi {first_name},

Your post about scaling engineering teams at {company} caught my attention —
we solved a similar challenge for {reference_client} using AI-powered workflow
automation that reduced their deployment cycle from 2 weeks to 2 days.

Would a 15-minute call to explore if something similar could work for
{company} be worth your time?
```

### InMail Credit Optimization

- **Target reply rate > 25%** to maximize credit refunds
- Personalization is key — generic InMails get < 5% reply rate
- Best send times: Tue-Thu, 8-10am recipient's local time
- Avoid: Monday mornings, Friday afternoons, weekends
- Follow up once if no reply after 5-7 business days (use regular message if connected)

---

## Part 6: Prospect List Management

### Data Schema

```json
{
  "prospects": [
    {
      "name": "Jane Smith",
      "title": "CTO",
      "company": "Acme Corp",
      "location": "New York, NY",
      "linkedin_url": "https://www.linkedin.com/in/janesmith",
      "mutual_connections": 3,
      "mutual_names": ["John Doe"],
      "recent_activity": "Posted about AI governance",
      "fit_score": 8,
      "status": "researched",
      "outreach_type": "inmail",
      "outreach_date": null,
      "reply_date": null,
      "notes": "Spoke at AI Summit 2025"
    }
  ]
}
```

### Status Flow

```
researched → engaged → connection_sent → connected → inmail_sent → replied → meeting_booked → converted
                                       → declined
                                                    → no_reply → follow_up_sent → replied | archived
```

### Output Files

| File | Purpose |
|------|---------|
| `.claude/context/linkedin/{date}_prospect_research.json` | Raw research data |
| `.claude/context/linkedin/{date}_outreach_log.json` | Campaign send log |
| `.claude/context/linkedin/prospect_master.json` | Aggregated prospect database |
| `.claude/context/linkedin/{date}_profile_views.json` | Who viewed your profile |
| `.claude/context/linkedin/{date}_engagement_log.json` | Likes/comments tracked |

---

## Part 7: Safety & Compliance

### LinkedIn Terms of Service

LinkedIn prohibits automated access. These automations operate in a **gray area**. Risk mitigation:

| Rule | Implementation |
|------|---------------|
| Human-speed pacing | All delays randomized, never faster than a human |
| No mass scraping | Only view profiles you'd research manually |
| No data export for sale | Data used only for personal outreach |
| Respect opt-outs | If someone declines, mark as "do not contact" |
| Session limits | Hard caps on actions per session and per day |
| Real profile | Use your real account, real Chrome, real identity |

### Account Safety Tiers

| Risk Level | Daily Limits | Weekly Limits |
|------------|-------------|---------------|
| Conservative | 30 views, 10 connections, 5 InMails | 100 views, 40 connections, 20 InMails |
| Moderate | 50 views, 20 connections, 10 InMails | 200 views, 80 connections, 50 InMails |
| Aggressive | 80 views, 30 connections, 15 InMails | 350 views, 120 connections, 75 InMails |

**Recommended**: Start conservative for 2 weeks, then escalate to moderate.

### Blocklist — DO NOT CONTACT

**These organizations and their employees are strictly off-limits.** Every workflow MUST check prospects against this blocklist before any interaction (view, like, connect, InMail). If a match is found, skip the prospect silently and log it as `"status": "blocklisted"`.

| Organization | Reason | Match Rule |
|-------------|--------|------------|
| **Accenture Federal Services** | Employer conflict of interest | Company contains "Accenture Federal" (case-insensitive) |
| **Accenture** (federal division) | Parent org overlap | Company equals "Accenture" AND title contains "Federal" |

**Blocklist check implementation** (run before EVERY interaction):

```javascript
// Check if prospect is blocklisted
evaluate_script({
  function: `(el) => {
    const company = el?.company || '';
    const title = el?.title || '';
    const lc = company.toLowerCase();
    if (lc.includes('accenture federal')) return 'BLOCKED';
    if (lc === 'accenture' && title.toLowerCase().includes('federal')) return 'BLOCKED';
    return 'OK';
  }`
})
```

**Rules**:
- Do NOT view their profiles (leaves a footprint)
- Do NOT like or comment on their posts
- Do NOT send connection requests
- Do NOT send InMails
- If they appear in search results, skip to next result
- If they viewed YOUR profile, do NOT engage back
- Log all blocklist hits for audit: `{ "name": "...", "company": "...", "reason": "blocklisted", "rule": "accenture-federal" }`

### Red Flags (Abort Immediately)

- "We've restricted your account" message
- CAPTCHA or phone verification prompt
- Profile views suddenly show 0 (shadowban)
- Connection requests auto-withdrawn
- "Unusual activity detected" banner

---

## Part 8: Integration with Consulting Pipeline

### The 4-Step Outreach Funnel (STRICT — do NOT skip steps)

```
Step 1: CONNECT     → Link to website ONLY. No call ask. No booking link.
Step 2: WARM UP     → After they accept, start a conversation. Ask about their work.
                       Share a relevant insight. Point to website if they're curious.
                       DO NOT ask for a call yet.
Step 3: DISCOVERY   → Once they reply and show interest, propose a casual 15-min call.
                       "No pitch, just comparing notes." Low pressure.
Step 4: INTAKE      → After the 15-min discovery call, if qualified, book the
                       60-min consulting intake session via /consulting:quick-proposal.
```

**Rules**:
- NEVER send a booking link in a connection note
- NEVER ask for a call in the first message after they accept
- NEVER jump from connection to 60-min intake — always go through 15-min discovery first
- The website (https://gbautomation.xyz) is the bridge — let them self-educate before any call

### Workflow: LinkedIn → Consulting Intake

1. **Research phase**: Identify prospects matching ideal client profile (ICP)
2. **Engagement phase**: Like/comment on their content for 3-5 days
3. **Connection phase**: Send personalized connection request (website link only)
4. **Warm-up phase**: After acceptance, conversational follow-up (no call ask)
5. **Discovery phase**: Once they engage back, propose 15-min discovery call
6. **Intake phase**: After discovery call, if qualified, book 60-min intake via `/consulting:quick-proposal`
7. **Booking phase**: Use Google Workspace agent to schedule

### ICP Filters for GBAutomation

| Filter | Value |
|--------|-------|
| Title | CTO, VP Engineering, Head of AI, Director of Engineering |
| Company size | 50-500 employees |
| Industry | SaaS, FinTech, HealthTech, AI/ML |
| Location | US, Canada, UK |
| Keywords | "AI automation", "developer productivity", "workflow automation" |

---

## Part 9: Reporting & Analytics

### Session Report Format

```markdown
## LinkedIn Session Report — {date}

### Credits Used
| Type | Used | Remaining | Monthly Total |
|------|------|-----------|---------------|
| Profile views | {n} | {n} | {n} |
| Connection requests | {n} | {n} | {n} |
| InMails | {n} | {n} | {n} |

### Actions
- Profiles researched: {n}
- Connection requests sent: {n}
- InMails sent: {n}
- Posts liked: {n}
- Comments left: {n}

### Prospect Pipeline
| Status | Count |
|--------|-------|
| Researched | {n} |
| Engaged | {n} |
| Connection sent | {n} |
| Connected | {n} |
| InMail sent | {n} |
| Replied | {n} |
| Meeting booked | {n} |

### Issues
- {any CAPTCHA, throttling, or errors encountered}
```

---

## Part 10: Quick Reference — MCP Tool Mapping

| LinkedIn Action | MCP Tool | Notes |
|----------------|----------|-------|
| Open LinkedIn | `navigate_page` | Use real Chrome profile URL |
| Read page content | `take_snapshot` | Returns a11y tree |
| Click button | `click` | Use uid from snapshot |
| Fill text field | `fill` | For search, InMail, notes |
| Scroll page | `evaluate_script` | Human-like scroll function |
| Wait for load | `wait_for` | Wait for specific text |
| Check for blocks | `evaluate_script` | CAPTCHA/challenge detection |
| Take evidence | `take_screenshot` | Save key moments |
| Extract data | `evaluate_script` | DOM queries for structured data |
| Add delay | `evaluate_script` | Random setTimeout for pacing |
