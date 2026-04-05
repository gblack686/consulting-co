---
name: client-personal-intel
description: "Deep personal intelligence research for GBAutomation consulting. Goes beyond LinkedIn — reads actual Instagram post captions (in native language), Facebook, Twitter/X, TikTok, and web search for personal life. Produces 2 focused slides and a deep-research markdown file grounded in real captions with source URLs cited. Invoke with 'personal intel', 'dig into them', 'instagram research', 'social media research', 'personal research', 'find out about them personally'."
model: opus
color: purple
---

# Client Personal Intel Skill

Deep personal reconnaissance. This skill does what no LinkedIn can — it reads who someone actually IS: the events they attend every year, the languages they code-switch into, the crew they roll with, the places they keep going back to, the values they signal through captions.

The goal: **surface information that only a close friend would know.** Make the consulting call feel personal, not transactional.

## When to Use

- After `/client-linkedin` when you want the full picture
- When user says "personal intel", "dig into them", "instagram research", "social deep dive"
- Before high-stakes sessions where rapport is everything

## What You Produce

1. **Screenshots** — Instagram grid, recent posts → saved to `.claude/context/clients/{slug}/`
2. **Deep research markdown** — `.claude/context/clients/{slug}/personal-intel.md`
3. **PowerPoint slides (2)** — personal intelligence slides grounded in actual captions with source URLs

---

## Prerequisites

- **Chrome DevTools MCP** must be connected (headed browser)
- **Instagram** must be logged in in the MCP Chrome profile (`C:\Users\gblac\.cache\chrome-devtools-mcp\chrome-profile`)
- **Facebook** (optional) — only researchable if logged in on MCP Chrome
- If MCP errors with "browser already running" → ask user to close the Chrome window for that profile, then retry
- **Do not attempt automated Instagram login** — 2FA blocks it. The session must already be active.

---

## Pipeline

### Phase 1: Inputs

Collect from user:
- **Name** (required)
- **Instagram handle** (if known) — otherwise search for it
- **Other social handles** — Twitter/X, TikTok, Facebook
- **Known personal details** — city, interests, anything already known

### Phase 2: Instagram Research

This is the highest-signal source. Go deep.

#### Step 1 — Find the Handle

If not provided:
1. WebSearch: `"{full name}" site:instagram.com` or `"{full name}" "{company}" instagram`
2. Or navigate to `https://www.instagram.com/web/search/topsearch/?query={name}` and parse results

#### Step 2 — Navigate to Profile

1. Navigate to `https://www.instagram.com/{handle}/`
2. Screenshot viewport → `instagram-profile.png`

#### Step 3 — Extract Profile Metadata

Read from screenshot or DOM:

| Field | Extract |
|---|---|
| Handle | @username |
| Display name | Full name on profile |
| Bio | Full bio text (verbatim, including language) |
| Follower count | Number |
| Following count | Number |
| Post count | Number |
| Link in bio | URL if present |
| Threads follower count | Ⓣ icon count if shown |
| Story highlights | All highlight reel names |
| Verified | Blue/gray check |
| Secondary accounts | Any @mentions in bio |

**Note the bio language** — Spanish, French, Italian, etc. signals cultural identity.

#### Step 4 — Capture the Grid

1. Screenshot the post grid → `instagram-grid-1.png`
2. Scroll down: `document.querySelector('main').scrollBy(0, 800)`
3. Screenshot again → `instagram-grid-2.png`
4. Note the visual themes (travel, nightlife, nature, events, people, food, etc.)

#### Step 5 — Read Actual Post Captions (THE MOST IMPORTANT STEP)

Do NOT skip this. Generic stats mean nothing. The captions are the intelligence.

**Method:**
1. Extract post URLs from the grid using JS:
   ```javascript
   Array.from(document.querySelectorAll('a[href*="/p/"]')).map(a => a.href)
   ```
2. Navigate to each post URL individually (most recent 6-10 posts)
3. For each post:
   - Screenshot → `instagram-post-{n}.png`
   - Read the caption **verbatim** (do NOT translate yet — preserve the original language)
   - Note: date, likes, comments, top comments
   - Note: who is tagged, any accounts mentioned

4. After reading all captions, **analyze and translate** non-English captions with cultural context

**What to extract from captions:**
- **Events they attend repeatedly** (annual festivals, parties, club nights)
- **Places they keep returning to** (cities, countries, venues)
- **Languages they use** (reveals cultural identity, not just nationality)
- **People they reference** (their inner circle)
- **Emotional tone** — grateful, nostalgic, celebratory, wistful?
- **Values signaled** — community, travel, art, music, family?
- **Inside references** — named events, recurring nicknames, private jokes that made it public

#### Step 6 — Engagement Analysis

- **Engagement rate** = (avg likes + avg comments) / followers × 100
- **Comment quality** — real friends? fans? bots? (check commenter handles)
- **Post frequency** — dates on recent posts
- **Platform asymmetry** — Instagram vs Threads vs other platforms (huge differences = strategic insight)

#### Step 7 — Story Highlights

Navigate each story highlight if accessible. Note what they chose to permanently archive — this is curated identity.

Save to → `personal-intel.md` under "Instagram" section

---

### Phase 3: Facebook Research (if logged in)

Only attempt if MCP Chrome is logged into Facebook.

1. Search: `https://www.facebook.com/search/people/?q={full name}`
2. Or try direct: `https://www.facebook.com/{username}`
3. If found: screenshot profile, extract bio, city, job listed, life events visible
4. Read recent public posts — same caption-reading discipline as Instagram

Save findings to `personal-intel.md` under "Facebook" section. Mark as "unverified" if profile match is uncertain.

---

### Phase 4: Twitter/X Research (if handle known or findable)

1. WebSearch: `"{full name}" site:twitter.com OR site:x.com`
2. If found and public: navigate, screenshot, read recent tweets
3. Extract: tone, topics, who they reply to, viral moments

---

### Phase 5: TikTok Research (if relevant)

1. WebSearch: `"{full name}" site:tiktok.com`
2. If found: note content themes, follower count, viral videos

---

### Phase 6: Deep Web Personal Research

Run WebSearch for personal life signals that complement the social data:

```
"{full name}" wedding OR married OR spouse OR partner
"{full name}" "{city}" event OR concert OR festival
"{full name}" volunteer OR nonprofit OR cause
"{full name}" podcast guest OR interview (personal interest topics)
"{full name}" marathon OR sport OR team OR club
```

Save findings to `personal-intel.md` under "Web Research" section.

---

### Phase 7: Generate Outputs

#### Personal Intel Markdown

Save to `.claude/context/clients/{slug}/personal-intel.md`:

```markdown
# Personal Intelligence: {Full Name}

**Researched**: {date}
**Instagram**: @{handle}

---

## Instagram Profile

| Field | Value |
|---|---|
| Handle | @{handle} |
| Display Name | {name} |
| Bio | "{bio verbatim}" |
| Posts | {count} |
| Followers | {count} |
| Following | {count} |
| Threads | {count if shown} |
| Link in Bio | {url} |
| Highlights | {list} |

## Posts Reviewed

| # | Date | Caption (verbatim) | Likes | Comments | URL |
|---|---|---|---|---|---|
| 1 | {date} | "{caption}" | {n} | {n} | {url} |
[... all posts reviewed ...]

## Engagement Analysis

- **Engagement rate**: {rate}% ({calculation})
- **Post frequency**: {cadence}
- **Comment quality**: {assessment}
- **Platform asymmetry**: {IG count} IG vs {Threads count} Threads — {insight}

## Content Themes

{paragraph analysis of what dominates the grid and what it signals}

## Caption Intelligence

### Annual Events
{events they attend every year based on recurring date/caption patterns}

### Places & Travel
{cities, countries, venues that appear repeatedly}

### Inner Circle
{people who appear in photos or comments, what that signals}

### Language & Cultural Identity
{what languages appear and what that reveals}

### Values & Causes
{what they signal caring about}

---

## Facebook

{findings or "Not found / not logged in"}

## Twitter/X

{findings or "Not found"}

## Web Research

{web search findings on personal life}

---

## Conversation Starters (Personal)

1. {specific opener referencing a post or caption with URL context}
2. {event they attend — "I saw you went to Lightning in a Bottle — do you go every year?"}
3. {language/cultural — "Your bio is in Spanish — were you based in Chile?"}
4. {travel — "Torino looked incredible — what brought you there?"}
5. {community — "Who's the crew in those photos?"}
```

#### PowerPoint Slides (2 slides)

Add to the client deck or generate standalone. GBAutomation colors: cream `#F3F1E7`, terracotta `#D97757`.

**Slide A: Personal Footprint**
- Bio verbatim
- Platform counts with asymmetry callout
- Story highlight names
- Content theme summary
- Top insight from captions

**Slide B: Caption Intelligence** (THE MONEY SLIDE)
- 4-6 direct caption quotes (verbatim, in original language with translation if non-English)
- Each quote: caption → what it reveals
- Source URLs listed at bottom
- Engagement rate callout

**Design rules for Caption Intelligence slide:**
- Use actual quote marks, not paraphrase
- Preserve original language — add translation in italics
- Each caption entry: `"[caption]"` → [what this reveals about the person]
- Footer: source URLs for each quoted post

Save as `.claude/context/clients/{slug}/{Name} - Personal Intel.pptx` (or append slides to existing deck)

---

## Lessons Learned (from Gregory Black session, 2026-03-08)

These lessons were hard-won — incorporate them:

1. **Caption screenshots beat JS extraction** — Instagram's React DOM doesn't expose captions reliably via `querySelector`. Navigate to each post URL and read the screenshot visually.

2. **Preserve original language** — "Agradecido" (grateful) hits differently than "Grateful." "Buscame aqui" (find me here) is a personal signature, not a generic caption. Don't flatten culture through translation.

3. **Annual events are gold** — "Dia de los muertos 2023 — excelente papito — nos vemos a la proxima" reveals an annual tradition (Day of the Dead), Spanish-speaking community, and a recurring attendee relationship.

4. **Platform asymmetry is a strategic insight** — 1.4K Instagram vs ~3M Threads = Instagram is personal/private, Threads is the distribution engine. That asymmetry tells you where their real audience is and how they think about audience separation.

5. **Highlights as curated identity** — Someone who highlights "Valpo" and "Studio" is telling you what they consider defining. Not random — intentional.

6. **Bio language = first signal** — A Spanish bio from someone with an English LinkedIn is a deliberate choice. Lead with that cultural bridge.

7. **Comment quality > comment count** — Five comments from real named friends who say "miss you!" is infinitely higher signal than 50 generic emoji from unknown accounts.

8. **Facebook requires login** — Don't attempt without confirmed session in MCP Chrome. Note the gap and move on.

---

## Error Handling

- **Instagram not logged in** → Tell user to open Chrome, log into Instagram manually, then retry (2FA blocks automation)
- **Chrome conflict** → Ask user to close the MCP Chrome window, retry
- **Caption not readable in screenshot** → Navigate directly to the post URL for a clean view
- **Rate limited** → Wait 30s, retry once; if still blocked, move to next post
- **Private account** → Note in output, extract what's visible from profile page only

---

## Usage Examples

```
/client-personal-intel Patrick Bauer — @patrickbauer on instagram
/client-personal-intel Gregory Black — @gregorablack
dig into Michael Fisch personally before his session
```
