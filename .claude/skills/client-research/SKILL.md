---
name: client-research
description: "DEPRECATED — split into client-linkedin and client-personal-intel. Kept for reference. Use /client-linkedin for quick professional overview or /client-personal-intel for deep social media + personal intelligence."
model: opus
color: gray
---

# Client Research Skill — DEPRECATED

> **This skill has been split into two focused skills:**
>
> - **`/client-linkedin`** — Quick professional overview: LinkedIn profile, career timeline, education, recommendations. Fast (< 5 min). Produces markdown + 3-slide deck.
> - **`/client-personal-intel`** — Deep personal intelligence: Instagram caption reading (verbatim, multilingual), Facebook, Twitter/X, web research. Produces 2 focused slides grounded in actual post captions with source URLs cited.
>
> The original monolithic pipeline below is preserved for reference only.

---

# Original Client Research Skill (Reference)

Pre-session research agent for GBAutomation consulting. Performs deep reconnaissance on a prospective or booked client, producing a PowerPoint deck and structured markdown profile Greg can review before the session.

## When to Use

- Before a consulting session — "research Patrick Bauer"
- When onboarding a new client — "build a deck on this person"
- User says "client research", "research client", "client intel", "pre-session prep"

## What You Produce

1. **Screenshots** — saved to `.claude/context/clients/{slug}/`
2. **Markdown profile** — `.claude/context/clients/{slug}/profile.md`
3. **PowerPoint deck** — `.claude/context/clients/{slug}/{Name} - Client Research.pptx`

## Prerequisites

- **Chrome DevTools MCP** must be connected (headed browser, not headless)
- **LinkedIn** must be logged in — stored in MCP Chrome profile session (no automated login — 2FA blocks it)
- **Instagram** must be logged in — same MCP Chrome profile (`C:\Users\gblac\.cache\chrome-devtools-mcp\chrome-profile`)
- If MCP tools error with "browser already running" → ask user to close the Chrome window for that profile, then retry

## Research Pipeline

### Phase 1: Inputs

Collect from user:
- **Name** (required) — full name of the person
- **Identifiers** (at least one) — company, school, LinkedIn URL, email, location
- **Session info** (optional) — date, type, Meet link

If a LinkedIn URL is provided, skip search and go directly to the profile.

### Phase 2: LinkedIn Research

#### Step 1 — Find the Profile

If no direct LinkedIn URL:
1. Navigate to LinkedIn search: `https://www.linkedin.com/search/results/all/?keywords={name}+{company}+{school}`
2. Take a screenshot of search results → `search-results.png`
3. Take a11y snapshot to find the correct profile link
4. Confirm with user if multiple matches (or auto-select if only one strong match)

#### Step 2 — Extract Profile Data

1. Navigate to the profile URL
2. Take a **full viewport screenshot** → `profile-header.png`
3. Take a11y snapshot and extract:

| Field | Source |
|---|---|
| Full name | Profile heading |
| Headline | Below name |
| Location | Location line |
| Current company | First experience entry |
| Current title | First experience entry |
| Connection degree | "1st", "2nd", "3rd" |
| Mutual connections | Mutual connection count + names |
| Services offered | Services section |
| Profile URL | Current page URL |

4. Extract **Experience** — all roles with company, title, dates, duration, location, description
5. Extract **Education** — schools, degrees, fields, dates
6. Extract **Skills** — listed skills
7. Extract **Languages** — listed languages
8. Extract **Publications** — if any
9. Extract **Highlights** — recent position changes, mutual schools, etc.

#### Step 3 — Scroll and Capture More

1. Scroll down to experience section → screenshot `experience.png`
2. If there's a "Show all" for experience, click it and capture the full list
3. Scroll to education → screenshot `education.png`
4. Scroll to skills → screenshot `skills.png`

#### Step 4 — Activity/Posts (Optional)

If time permits:
1. Navigate to `{profile_url}/recent-activity/all/`
2. Screenshot recent posts → `recent-activity.png`
3. Note topics they post about (reveals interests and expertise)

### Phase 3: Deep Web Research (The Dossier)

Run a general-purpose agent with WebSearch to find EVERYTHING. This is what separates a basic LinkedIn scrape from a real dossier. Search for ALL of the following categories:

#### 3a. Company Deep Dive
- All current and past companies — what they do, size, revenue, key people, exits
- Company websites — scrape homepage, about, team, services, pricing
- Company logos (Brandfetch CDN or direct)
- Company social media accounts

#### 3b. Podcast & Speaking Appearances
```
"{full name}" podcast guest OR interview OR episode OR speaker
"{full name}" "{company}" podcast
"{full name}" keynote OR panel OR conference
```

#### 3c. Viral Moments & Video Content
```
"{full name}" "{company}" youtube OR video OR testimonial
"{full name}" viral OR trending
```

#### 3d. News & Press Features
```
"{full name}" "{company}" news OR press OR feature OR article OR profile
"{full name}" "{company}" interview OR quoted
```

#### 3e. Awards & Recognition
```
"{full name}" award OR recognition OR "30 under 30" OR honor OR "best of"
"{full name}" "{company}" award
```

#### 3f. Books Written
```
"{full name}" author book OR published
site:amazon.com "{full name}" book
```

#### 3g. Amazon Products
```
site:amazon.com "{company}" OR "{full name}"
```

#### 3h. Community & Board Involvement
```
"{full name}" volunteer OR community OR nonprofit OR "board member" OR "board of directors"
"{full name}" "{city}" community OR nonprofit
```

#### 3i. Sports (Professional, College, or Recreational)
```
"{full name}" "{school}" athletics OR sports OR varsity OR club OR team
"{full name}" marathon OR triathlon OR crossfit OR ironman
```

#### 3j. Charity & Philanthropy
```
"{full name}" charity OR foundation OR philanthropy OR donate OR fundraiser
```

#### 3k. IMDB Credits
```
site:imdb.com "{full name}"
```

#### 3l. Family & Personal Life
```
"{full name}" wife OR husband OR married OR family OR children
"{full name}" "{city}" wedding OR engaged
```
Note: Only include publicly available information. Mark any speculation.

#### 3m. Proprietary Systems & Named Methodologies
- Extract from LinkedIn descriptions — what systems/frameworks did they build?
- Named processes, branded methodologies, internal tools they've created
- CRM, dashboard, workflow, or platform names

#### 3n. Unique Service Offerings
- What makes their business different from competitors?
- Proprietary pricing models, unique delivery formats
- Niche market positions

#### 3o. Social Media Deep Scan & Personal Intelligence
If they have Instagram, Facebook, Twitter/X, TikTok — scroll through their feed (past 2 years) and extract:

**Communication Style:**
- How they write captions, replies, comments
- Tone: formal, casual, irreverent, motivational, sarcastic
- Emoji usage, hashtag patterns, posting frequency
- Do they engage in comment threads? How do they respond to criticism?

**Personal Interests & Lifestyle:**
- Hobbies (golf, fishing, cooking, gaming, music, etc.)
- Cars they drive or post about
- Pets (breed, name, how often featured)
- Travel destinations and frequency
- Food/restaurant preferences
- Fashion/style choices
- Home/real estate (neighborhood, style)

**People & Influences:**
- People they look up to, tag, or quote
- Idols, mentors, inspirations
- Celebrity interests (who they follow, repost, or reference)
- Business figures they admire
- Authors, podcasters, thought leaders they engage with

**Family & Relationships:**
- Spouse/partner (name, profession, how they met if shared)
- Children (names, ages if shared)
- Parents, siblings (if featured)
- Wedding, engagement, anniversary posts
- Family traditions or recurring events

**Viral Moments & Highlights:**
- Posts with unusually high engagement (likes, comments, shares)
- Content that went viral or was reshared widely
- Controversial takes or public disagreements
- Milestone posts (exits, launches, awards, personal achievements)

**Causes & Values:**
- Charities, nonprofits, or causes they support
- Political leanings (if publicly expressed)
- Social issues they speak on
- Community involvement posts

**Goal:** Surface information that only a close friend would know — the kind of details that make a consulting call feel personal and connected, not transactional.

Save all findings to `{slug}/deep-research.md` and `{slug}/site-research.md`.

### Phase 4: Generate Outputs

#### Markdown Profile

Save to `.claude/context/clients/{slug}/profile.md`:

```markdown
# Client Profile: {Full Name}

**Researched**: {date}
**LinkedIn**: {url}
**Session**: {type} — {date} (if known)

---

## Summary

| Field | Value |
|---|---|
| Name | {name} |
| Headline | {headline} |
| Location | {location} |
| Current Role | {title} at {company} |
| Connection | {degree} ({mutual_count} mutual) |

## Services Offered
{list from LinkedIn services section}

## Experience
{chronological list with descriptions}

## Education
{schools and degrees}

## Skills
{list}

## Languages
{list}

## Key Takeaways for Consulting
1. {insight 1 — what they're good at}
2. {insight 2 — what they might need}
3. {insight 3 — connection points with Greg}
4. {insight 4 — automation/AI opportunities based on their work}

## Screenshots
- `search-results.png` — LinkedIn search
- `profile-header.png` — Profile header
- `experience.png` — Experience section
- `education.png` — Education section
```

#### PowerPoint Deck

Generate using `python-pptx` via the script at `scripts/build_deck.py`.

**Slide layout (16 slides):**

| Slide # | Content |
|---|---|
| 1 | **Title** — "{Name} — Client Research Dossier" + headline + date + "GBAutomation Consulting" |
| 2 | **Profile Overview** — name, headline, location, current role, connection info, mutual connections |
| 3 | **LinkedIn Screenshot** — profile-header.png embedded full-width |
| 4 | **Career Timeline** — all roles with company, title, dates, key achievements |
| 5 | **Company Deep Dive** — current + past companies with key facts |
| 6 | **Company Screenshot 1** — main company website homepage |
| 7 | **Company Screenshot 2** — secondary company/product website |
| 8 | **Proprietary Systems** — named methodologies, frameworks, tools they've built |
| 9 | **Services & Skills** — two-column: services offered + top skills |
| 10 | **Education & Languages** — degrees + languages |
| 11 | **Video & Media** — podcast appearances, testimonials, press features |
| 12 | **Personal & Digital Footprint** — social media presence, personal interests, family |
| 13 | **Key Takeaways (1/2)** — first 5 consulting angles |
| 14 | **Key Takeaways (2/2)** — remaining consulting angles |
| 15 | **Conversation Starters** — 5-7 specific things to bring up in the call |
| 16 | **Next Steps** — session info, prep questions, demo ideas |

**Design:**
- Use GBAutomation brand colors: cream background (#F3F1E7), terracotta accents (#D97757)
- Clean, minimal — no clip art, no filler
- Screenshots get full-slide treatment with thin border

### Phase 5: Instagram Research

**Prerequisites:** Chrome DevTools MCP must be connected and Instagram must be logged in. Instagram blocks automated login (2FA), so the session must already be active in the MCP-controlled Chrome profile (`C:\Users\gblac\.cache\chrome-devtools-mcp\chrome-profile`).

**Important — MCP Chrome conflict:** If Chrome is already open with the MCP profile, the MCP tools will throw a "browser already running" error. Ask the user to close that Chrome window, then the MCP will relaunch it and reconnect automatically.

#### Step 1 — Find the Handle

If not provided by user, search for it:
1. Use WebSearch: `"{full name}" site:instagram.com` or `"{full name}" "{company}" instagram`
2. Or navigate to `https://www.instagram.com/web/search/topsearch/?query={name}` and parse results

#### Step 2 — Navigate to Profile

1. Navigate to `https://www.instagram.com/{handle}/`
2. Take a full **viewport screenshot** → `instagram-profile.png`

#### Step 3 — Extract Profile Data

Use `evaluate_script` with a JS function to extract from the DOM, or read from the screenshot:

| Field | What to Extract |
|---|---|
| Handle | @username |
| Display name | Full name shown on profile |
| Bio | Full bio text |
| Follower count | Followers number |
| Following count | Following number |
| Post count | Number of posts |
| External link | Link in bio (booking link, website, etc.) |
| Threads count | Threads follower count if shown (Ⓣ icon) |
| Story highlights | Names of all highlight reels |
| Verified | Blue/gray check if present |
| Secondary account | Any @mentions in bio |

#### Step 4 — Scroll the Grid & Screenshot

1. Scroll down slowly using `evaluate_script` → `window.scrollBy(0, 800)`
2. Take **2-3 screenshots** of the post grid to capture ~12-24 posts
3. Save as `instagram-grid-1.png`, `instagram-grid-2.png`

#### Step 5 — Check Engagement on Recent Posts

1. Extract post URLs from the page using JS: `document.querySelectorAll('a[href*="/p/"]')`
2. Navigate to the **most recent post**
3. Take a screenshot → `instagram-post-recent.png`
4. Extract: **like count**, **comment count**, **post date**, **caption**, **top comments**
5. Navigate to 1-2 more recent posts to get an engagement average

#### Step 6 — Engagement Analysis

Calculate and note:
- **Engagement rate** = (avg likes + avg comments) / followers × 100
- **Avg likes per post**
- **Comment quality** — are they from real people? Friends? Fans? Bots?
- **Post frequency** — how often do they post (check dates on recent posts)
- **Content themes** — what topics/visuals dominate their feed

#### Step 7 — Cross-Platform Signal

Note the platform asymmetry if significant (e.g., 1.4K IG vs 3M Threads) — this reveals where their real audience lives and is a key consulting insight.

Save all findings to `{slug}/instagram-research.md`.

## Output Location

```
.claude/context/clients/
├── patrick-bauer/
│   ├── profile.md
│   ├── instagram-research.md
│   ├── Patrick Bauer - Client Research.pptx
│   ├── search-results.png
│   ├── profile-header.png
│   ├── experience.png
│   ├── education.png
│   ├── skills.png
│   ├── instagram-profile.png
│   ├── instagram-grid-1.png
│   ├── instagram-grid-2.png
│   └── instagram-post-recent.png
├── erica-cruz/
│   └── ...
```

## Usage Examples

```
/client-research Patrick Bauer — Acquisition.com, Penn State
/client-research https://www.linkedin.com/in/patrick-bauer-86a29527/
Research Jason Diaz before his session on March 10
```

## Error Handling

- **LinkedIn not logged in** → Tell user to open Chrome and log into LinkedIn manually, then retry
- **2FA triggered** → Wait for user to approve, then continue
- **Profile not found** → Show search results, ask user to pick the right one
- **Rate limited** → Back off, wait 30 seconds, retry once
- **Chrome not connected** → Tell user to ensure Chrome DevTools MCP is running
