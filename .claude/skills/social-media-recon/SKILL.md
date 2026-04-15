---
name: social-media-recon
description: "Browser-native social media research skill for Sebastian (Mac Mini). Uses Steer GUI automation to research Instagram + Facebook profiles with authenticated Safari sessions. Produces personal-intel.md, screenshots, and conversation starters. Invoke with 'social recon', 'instagram research', 'facebook research', 'social media deep dive', 'research their socials'."
model: opus
color: purple
---

# Social Media Recon — Sebastian (Mac Mini)

Browser-native social media research using **Steer** (macOS GUI automation) instead of Chrome DevTools MCP. Runs on the Mac Mini where Safari stays permanently logged into Instagram and Facebook — no profile conflicts, no 2FA interruptions, no MCP "browser already running" errors.

## When to Use

- Research a client's Instagram and/or Facebook before a consulting session
- After `/client-linkedin` when you want the personal layer
- User says "social recon", "instagram research", "facebook research", "dig into their socials"
- Triggered remotely via Listen job: `just send "social recon: {name} @{handle}"`

## What You Produce

1. **Screenshots** — profile, grid, individual posts → `~/.openclaw/workspace/gbauto/pbauer/{slug}/`
2. **personal-intel.md** — deep research markdown with verbatim captions, engagement analysis, conversation starters
3. **Summary message** — sent back via Telegram/Discord with key findings

---

## Prerequisites

- **Safari** must be logged into Instagram and Facebook (one-time manual setup)
- **Steer** CLI installed and working (`steer see --app Safari` returns screenshot)
- **Drive** CLI for terminal commands if needed
- macOS Accessibility + Screen Recording permissions granted to Terminal

### One-Time Safari Auth Setup

Do this manually on the Mac Mini:

```bash
# Open Safari
open -a Safari

# Navigate and log in manually:
# 1. https://www.instagram.com — log in, approve 2FA, check "Remember me"
# 2. https://www.facebook.com — log in, approve 2FA, check "Remember me"
# 3. Verify both stay logged in after closing/reopening Safari
```

---

## Pipeline

### Phase 1: Inputs

Required:
- **Name** — full name of the person
- **Platform handles** — at least one of: Instagram handle, Facebook URL/name

Optional:
- **Known details** — city, company, interests (helps verify correct profile)
- **Slug** — folder name override (default: kebab-case of name)

### Phase 2: Setup

```bash
# gbauto = GitHub org with one repo per GBAutomation client
# pbauer = Patrick Bauer's repo — this skill researches people FOR pbauer
# SLUG = the person being researched (pbauer's client/prospect)
SLUG="aidan-pinter"  # kebab-case of research target
BASE=~/.openclaw/workspace/gbauto/pbauer/$SLUG
mkdir -p $BASE/instagram
mkdir -p $BASE/linkedin
mkdir -p $BASE/facebook

# Ensure Safari is frontmost
steer focus --app Safari
```

> **First-time setup**: Clone all GBAutomation client repos from the gbauto GitHub org:
> ```bash
> cd ~/.openclaw/workspace
> gh repo list gbauto --limit 100 --json name -q '.[].name' | xargs -I{} gh repo clone gbauto/{} gbauto/{}
> ```

---

### Phase 3: Instagram Research

#### Step 1 — Navigate to Profile

```bash
# Open Instagram profile in Safari
steer focus --app Safari
steer hotkey cmd+l                          # Focus address bar
steer type "https://www.instagram.com/{handle}/"
steer hotkey enter
sleep 3                                      # Wait for page load

# Verify we landed on the right page
steer see --app Safari --json > /tmp/ig-profile-check.json
# Read screenshot to confirm profile loaded (not login wall)
```

If login wall appears: **STOP** — tell the user to manually log into Instagram on Safari on the Mac Mini.

#### Step 2 — Screenshot Profile Header

```bash
steer see --app Safari --path $BASE/instagram/instagram-profile.png
```

#### Step 3 — Extract Profile Metadata via OCR

```bash
steer ocr --app Safari --store > /tmp/ig-profile-ocr.json
```

Parse OCR output for:

| Field | What to Find |
|---|---|
| Handle | @username text |
| Display name | Name above bio |
| Bio | Text block below name (preserve original language!) |
| Posts / Followers / Following | Number triplet near top |
| Link in bio | URL if visible |
| Verified | Blue checkmark icon |
| Story highlights | Circular icons with labels below bio |

**Critical: Note the bio language.** Spanish, French, Portuguese = cultural identity signal.

#### Step 4 — Capture the Post Grid

```bash
# Screenshot current grid view
steer see --app Safari --path $BASE/instagram/instagram-grid-1.png

# Scroll down to see more posts
steer scroll --app Safari --direction down --amount 5
sleep 1
steer see --app Safari --path $BASE/instagram/instagram-grid-2.png
```

Note visual themes from the grid: travel, nightlife, nature, food, people, events, etc.

#### Step 5 — Read Individual Post Captions (THE MOST IMPORTANT STEP)

This is what separates real intelligence from generic stats. Do NOT skip this.

For the **6-10 most recent posts**:

```bash
# Method: Click into each post from the grid, or navigate directly
steer hotkey cmd+l
steer type "https://www.instagram.com/p/{POST_SHORTCODE}/"
steer hotkey enter
sleep 2

# Screenshot the post
steer see --app Safari --path $BASE/instagram/instagram-post-{n}.png

# OCR to extract caption text
steer ocr --app Safari --store > /tmp/ig-post-{n}-ocr.json
```

For each post, extract:
- **Caption verbatim** — in original language, do NOT translate yet
- **Date** posted
- **Like count**
- **Comment count**
- **Tagged accounts**
- **Top comments** (names + text)

After reading all captions, analyze:
- **Events they attend repeatedly** (annual festivals, parties, traditions)
- **Places they return to** (cities, venues, countries)
- **Languages used** (code-switching = cultural identity)
- **Inner circle** (who appears in photos/comments/tags)
- **Emotional tone** (grateful, nostalgic, celebratory, wistful)
- **Values signaled** (community, travel, art, music, family)

#### Step 6 — Engagement Analysis

Calculate:
- **Engagement rate** = (avg likes + avg comments) / followers x 100
- **Post frequency** — cadence based on dates
- **Comment quality** — real friends vs bots vs generic emoji
- **Platform asymmetry** — if Threads/Twitter follower counts differ wildly from IG, note it (strategic insight for consulting)

#### Step 7 — Story Highlights (if accessible)

Click each highlight reel and screenshot. What someone permanently archives = curated identity.

```bash
# Click a highlight (use OCR coordinates from profile screenshot)
steer click --text "Travel"      # or whatever the highlight name is
sleep 2
steer see --app Safari --path $BASE/instagram/instagram-highlight-{name}.png
```

---

### Phase 4: Facebook Research

#### Step 1 — Navigate to Profile

```bash
steer focus --app Safari
steer hotkey cmd+l
steer type "https://www.facebook.com/{username_or_search}"
steer hotkey enter
sleep 3

# If searching by name:
steer hotkey cmd+l
steer type "https://www.facebook.com/search/people/?q={Full Name}"
steer hotkey enter
sleep 3
```

If login wall: **STOP** — tell user to log into Facebook on Safari.

#### Step 2 — Screenshot & OCR Profile

```bash
steer see --app Safari --path $BASE/facebook/facebook-profile.png
steer ocr --app Safari --store > /tmp/fb-profile-ocr.json
```

Extract:
- **Name** and profile headline
- **Location** (city)
- **Job/company** listed
- **Relationship status** (if public)
- **Life events** visible on timeline
- **Profile photo** context (what it reveals)

#### Step 3 — Read Recent Public Posts

Scroll through timeline, reading the most recent 5-10 public posts:

```bash
steer scroll --app Safari --direction down --amount 3
sleep 1
steer see --app Safari --path $BASE/facebook/facebook-timeline-{n}.png
steer ocr --app Safari --store > /tmp/fb-post-{n}-ocr.json
```

Same caption-reading discipline as Instagram:
- Verbatim text
- Engagement (reactions, comments, shares)
- Who comments (friends, family, colleagues)
- Topics and tone

#### Step 4 — About Section

Navigate to the About tab if accessible:

```bash
steer hotkey cmd+l
steer type "https://www.facebook.com/{username}/about"
steer hotkey enter
sleep 2
steer see --app Safari --path $BASE/facebook/facebook-about.png
steer ocr --app Safari --store > /tmp/fb-about-ocr.json
```

Extract: work history, education, family members, life events, places lived.

---

### Phase 5: Generate Outputs

#### personal-intel.md

Save to `~/.openclaw/workspace/gbauto/pbauer/{slug}/personal-intel.md`:

```markdown
# Personal Intelligence: {Full Name}

**Researched**: {date}
**Instagram**: @{handle}
**Facebook**: {url or "Not found"}
**Researcher**: Sebastian (Mac Mini)

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
- **Platform asymmetry**: {insight if applicable}

## Caption Intelligence

### Annual Events
{events they attend every year}

### Places & Travel
{recurring locations}

### Inner Circle
{people who appear}

### Language & Cultural Identity
{languages used and what they reveal}

### Values & Causes
{what they signal caring about}

---

## Facebook Profile

| Field | Value |
|---|---|
| Name | {name} |
| Location | {city} |
| Work | {job} |
| Relationship | {status if public} |

### Recent Posts
{post summaries with verbatim quotes}

### Life Events
{milestones visible}

### About Section
{education, work history, places lived}

---

## Conversation Starters (Personal)

1. {specific opener referencing a caption with URL}
2. {annual event — "I saw you went to X — do you go every year?"}
3. {language/cultural bridge — "Your bio is in Spanish — were you based in...?"}
4. {travel — "Torino looked incredible — what brought you there?"}
5. {community — "Who's the crew in those photos?"}
6. {Facebook life event — "Congrats on X — how's that going?"}

---

## Screenshots Index

- `instagram-profile.png` — IG profile header
- `instagram-grid-1.png` — Post grid (page 1)
- `instagram-grid-2.png` — Post grid (page 2)
- `instagram-post-{n}.png` — Individual posts
- `instagram-highlight-{name}.png` — Story highlights
- `facebook-profile.png` — FB profile
- `facebook-timeline-{n}.png` — FB timeline posts
- `facebook-about.png` — FB about section
```

#### Telegram Summary

After generating the markdown, send a summary back via Telegram:

```
Social Recon Complete: {Full Name}

Instagram (@{handle}):
- {followers} followers, {posts} posts
- Engagement rate: {rate}%
- Key themes: {2-3 themes}
- Languages: {languages found}

Facebook:
- {status — found/not found/private}
- {1-2 key findings if found}

Top conversation starters:
1. {best opener}
2. {second best}
3. {third best}

Full report: ~/.openclaw/workspace/gbauto/pbauer/{slug}/personal-intel.md
{count} screenshots captured.
```

---

## Lessons Learned (from prior research sessions)

1. **Caption screenshots beat JS extraction** — Instagram's React DOM doesn't expose captions reliably. Use Steer OCR on the rendered page.

2. **Preserve original language** — "Agradecido" hits differently than "Grateful." Don't flatten culture through translation.

3. **Annual events are gold** — recurring date/caption patterns reveal traditions and community ties.

4. **Platform asymmetry is strategic** — 1.4K IG vs 3M Threads tells you where their real audience is.

5. **Highlights = curated identity** — what someone permanently archives is intentional.

6. **Bio language = first signal** — Spanish bio + English LinkedIn = deliberate cultural choice.

7. **Comment quality > count** — 5 real friends > 50 bot emojis.

8. **Facebook requires confirmed login** — if not logged in, note the gap and move on. Don't waste time.

9. **Steer OCR is the equalizer** — when accessibility trees return nothing useful, `steer ocr --store` makes all text addressable.

10. **Scroll slowly** — Instagram lazy-loads content. `steer scroll --amount 3` then `sleep 1` before capturing.

---

## Error Handling

| Error | Solution |
|---|---|
| Login wall on Instagram | STOP — tell user to log into Safari on Mac Mini manually |
| Login wall on Facebook | STOP — same as above |
| Private account | Note in output, extract only what's visible from profile page |
| OCR returns garbage | Try `steer see` at higher resolution, or zoom in with cmd+ |
| Page won't load | Check Safari network — `steer see` and verify, retry once |
| Rate limited / blocked | Wait 60s, retry once. If still blocked, move to next platform |
| Wrong profile found | Show screenshot to user via Telegram, ask to confirm before proceeding |

---

## Remote Trigger Examples

From Windows (primary machine):

```bash
# Via Listen job server
curl -X POST http://192.168.4.94:7600/job \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Run social recon on Garrett Shuster. Instagram: @garrettshuster. Also check Facebook. Save to clients/garrett-shuster/"}'

# Via just (if devbox configured)
just send "social recon: Garrett Shuster @garrettshuster — check IG and FB"
```

Via Telegram to Sebastian:
```
Research Garrett Shuster on Instagram (@garrettshuster) and Facebook.
Use the social-media-recon skill. Save everything to clients/garrett-shuster/.
Send me the summary when done.
```

---

## Usage Examples

```
social recon: Patrick Bauer — no Instagram confirmed, check Facebook only
social recon: Garrett Shuster @garrettshuster — IG + FB deep dive
social recon: Loren Piretra @lorenpiretra — focus on podcast/activism captions
research their socials before the session tomorrow
```
