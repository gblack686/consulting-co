---
type: expert-file
parent: "[[bowser/_index]]"
file-type: expertise
human_reviewed: false
source: hands-on-session-20260219 + browser-automation-justfile + bowser-commands
last_validated: 2026-02-19
tags: [expert-file, mental-model, bowser, browser-automation, mcp, youtube]
---

# Bowser Expertise (Complete Mental Model)

> **Sources**: Hands-on browser automation sessions, `.claude/skills/browser-automation/justfile`, bowser commands, MCP Chrome DevTools usage

---

## Part 1: The Two Browser Backends

Bowser supports two browser backends, each with distinct capabilities and trade-offs.

### Backend Reference

| Backend | Agent Type | Chrome Instance | Auth | Parallelism | Best For |
|---------|-----------|----------------|------|-------------|----------|
| **claude-bowser** | `bowser-agent` | MCP Chrome DevTools (separate profile) | Not signed in | Single instance only | Pages needing interaction, JS evaluation |
| **playwright-bowser** | `bowser-agent` | Playwright Chromium (headless by default) | No auth | Multiple parallel instances | Scraping, testing, screenshots |

### MCP Chrome DevTools (claude-bowser)

The MCP Chrome DevTools server opens its **own Chrome profile** — not incognito, but a separate profile that is not signed into any Google/web services. This has major implications:

| Feature | Status | Impact |
|---------|--------|--------|
| Google sign-in | Not available | YouTube transcripts, Gmail, Google Docs inaccessible |
| Cookie state | Separate profile | No access to user's daily browsing cookies |
| Storage quota | ~571GB (not incognito) | Full local storage available |
| Parallelism | Single instance | Cannot run multiple claude-bowser agents simultaneously |
| JS evaluation | Full access | Can run arbitrary JS via `evaluate_script` |

**Key tools**: `navigate_page`, `take_snapshot`, `take_screenshot`, `click`, `fill`, `evaluate_script`, `press_key`, `hover`, `wait_for`

### Playwright Bowser

Playwright uses its own Chromium binary. Supports headed/headless mode and parallel instances.

| Feature | Status | Impact |
|---------|--------|--------|
| Auth | None | Clean browser, no cookies |
| Parallelism | Multiple instances | Can run QA stories in parallel |
| Headed mode | Optional | Set via `headed` keyword |
| Screenshots | Built-in | Save to configurable path |

---

## Part 2: The 5 Bowser Commands

### Command Reference

| Command | Skill | Backend | Purpose |
|---------|-------|---------|---------|
| `/bowser:youtube-transcript` | Browser extraction | claude-bowser | Extract YouTube transcript + description |
| `/bowser:ui-review` | Parallel QA | bowser-agent (QA mode) | Fan out user story validation |
| `/bowser:hop-automate` | Workflow runner | configurable | Run saved browser workflows |
| `/bowser:amazon-add-to-cart` | Shopping | claude-bowser | Add items to Amazon cart |
| `/bowser:blog-summarizer` | Content | playwright-bowser | Summarize latest blog post |

### Command Details

#### youtube-transcript
- **Input**: `<video-id-or-url> [output-dir]`
- **Output**: `{VIDEO_ID}_transcript.txt`, `{VIDEO_ID}_description.txt`, `{VIDEO_ID}_metadata.json`
- **Default output dir**: `.claude/context/tac-scan`
- **Critical limitation**: Transcript panel requires Google sign-in (see Part 3)

#### ui-review
- **Input**: `[headed] [filename-filter] [vision]`
- **Output**: Aggregated pass/fail report with screenshots
- **Stories dir**: `ai_review/user_stories/*.yaml`
- **Agent**: `bowser-agent (QA mode)` (parallel instances)

#### hop-automate
- **Input**: `<workflow-name> [prompt] [playwright|claude] [headed|headless] [vision]`
- **Output**: Workflow execution results
- **Runs any saved `.md` workflow** from `.claude/commands/bowser/`

#### amazon-add-to-cart
- **Input**: `<item to search for>`
- **Backend**: claude-bowser (needs real Chrome for Amazon auth)
- **Stops at checkout** — never submits order

#### blog-summarizer
- **Input**: `<blog-url>`
- **Backend**: playwright-bowser (headless, no auth needed)
- **Output**: 3-5 bullet summary + rating out of 10

---

## Part 3: YouTube Transcript Extraction

YouTube transcript extraction has a **primary path (browser)** and a **reliable fallback (Apify)**.

### Decision Tree

```
YouTube Video ID
    │
    ├─→ Try Browser (MCP Chrome DevTools)
    │       │
    │       ├─→ Navigate to video page
    │       ├─→ Click "...more" to expand description
    │       ├─→ Extract description text + URLs ✅ (always works)
    │       ├─→ Click "Show transcript"
    │       │       │
    │       │       ├─→ Segments load → Extract transcript ✅
    │       │       └─→ Spinner hangs (not signed in) → Fallback to Apify
    │       │
    │       └─→ Navigation timeout → IGNORE and proceed (see Part 4)
    │
    └─→ Apify Fallback (always works)
            │
            ├─→ Fetch token from AWS Secrets Manager
            ├─→ Call karamelo~youtube-transcripts actor
            ├─→ Poll for completion (~10-15s)
            └─→ Extract transcript from results ✅
```

### Apify Method (Preferred)

| Property | Value |
|----------|-------|
| **Actor** | `karamelo~youtube-transcripts` |
| **Cost** | $0.007/transcript |
| **Speed** | ~10-15 seconds |
| **Reliability** | 99.96% success rate |
| **Auth required** | Apify token only |
| **AWS Secret** | `gbautomation/core/apify-token` |
| **Output** | Clean plain text (no VTT rolling duplicates) |

### Apify Implementation Pattern

```python
import requests, json, time, boto3, re, html

def get_apify_token():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    secret = client.get_secret_value(SecretId='gbautomation/core/apify-token')
    return secret['SecretString']

def fetch_transcript(video_id):
    token = get_apify_token()
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    # Start run
    run_url = f'https://api.apify.com/v2/acts/karamelo~youtube-transcripts/runs?token={token}'
    response = requests.post(run_url, json={'urls': [video_url]})
    run_data = response.json()['data']
    run_id = run_data['id']
    dataset_id = run_data['defaultDatasetId']

    # Poll for completion
    status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={token}'
    while True:
        status = requests.get(status_url).json()['data']['status']
        if status == 'SUCCEEDED': break
        if status in ['FAILED', 'ABORTED', 'TIMED-OUT']: raise Exception(status)
        time.sleep(2)

    # Fetch results
    results_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}'
    results = requests.get(results_url).json()
    item = results[0]

    captions = item.get('captions', [])
    if isinstance(captions, list) and captions:
        if isinstance(captions[0], str):
            raw_text = ' '.join(captions)
        elif isinstance(captions[0], dict):
            raw_text = ' '.join([c.get('text', '') for c in captions])
    transcript = html.unescape(raw_text)

    return {
        'title': item.get('title', 'Unknown'),
        'channel': item.get('channelName', 'Unknown'),
        'published': item.get('datePublished', 'Unknown'),
        'transcript': transcript,
        'char_count': len(transcript)
    }
```

### Browser Method (Description-Only Reliable)

The browser can reliably extract **descriptions** but NOT transcripts (requires Google sign-in). Use browser for:
- Description text and URLs
- Following resource links (configs, gists) via WebFetch
- Extracting metadata (title, channel, views, likes, date)

### Output File Convention

```
{OUTPUT_DIR}/
├── {VIDEO_ID}_transcript.txt      # Full transcript with header
├── {VIDEO_ID}_description.txt     # YouTube description text
├── {VIDEO_ID}_metadata.json       # Video metadata + links
└── {VIDEO_ID}_config.json5        # Optional: extracted configs from description URLs
```

### Metadata JSON Schema

```json
{
  "video_id": "string",
  "title": "string",
  "channel": "string",
  "views": "string",
  "date": "ISO 8601 date string",
  "likes": "string",
  "description_file": "{VIDEO_ID}_description.txt",
  "transcript_file": "{VIDEO_ID}_transcript.txt",
  "transcript_available": true,
  "transcript_source": "apify | browser",
  "transcript_chars": 0,
  "github_links": ["url1", "url2"],
  "resource_links": ["url1", "url2"]
}
```

---

## Part 4: Browser Quirks and Gotchas

### Critical: YouTube Navigation Timeout

YouTube's video player never fires the `load` event — the page stays in a perpetual loading state. The MCP `navigate_page` tool will report a timeout error.

**This is a red herring.** The page content is fully rendered despite the timeout. **Ignore the timeout and proceed** — all page elements (title, description, buttons) are available for interaction.

### MCP Chrome DevTools Profile

| Property | Value |
|----------|-------|
| Profile type | Separate Chrome profile (NOT incognito) |
| Google sign-in | Not signed in |
| Storage | Full local storage (~571GB quota) |
| Extensions | None |
| Cookies | Clean — no user session cookies |

This means any workflow that requires authentication (YouTube transcripts, Gmail, Google Docs, logged-in Amazon) will fail on the auth step.

### Nested Claude CLI Sessions

Running `claude --chrome` from within a Claude Code session is blocked by environment variables.

```
Error: "Cannot be launched inside another Claude Code session"
Fix:   unset CLAUDECODE

Error: "Invalid API key"
Fix:   unset ANTHROPIC_API_KEY && unset CLAUDE_CODE_OAUTH_TOKEN

Error: "Chrome browser extension isn't connected"
Fix:   Requires Claude browser extension active in Chrome — cannot be resolved from CLI
```

**Bottom line**: The justfile `youtube-transcript` recipe (`claude --chrome`) cannot work from within Claude Code. Use MCP Chrome DevTools or Apify directly instead.

### Browser MCP Wedging

The MCP Chrome DevTools server can occasionally become wedged between operations, returning errors. Usually resolves itself on the next call. If persistent, use `list_pages` and `select_page` to reset state.

### YouTube Description URL Truncation

YouTube truncates long URLs in the visible description text. To get full URLs, use JS evaluation:

```javascript
// Extract full href values from description links
const links = document.querySelectorAll('#description-inner a');
return Array.from(links).map(a => ({
  text: a.textContent.trim(),
  href: a.href
}));
```

---

## Part 5: Justfile Integration

### Browser Automation Justfile

Location: `.claude/skills/browser-automation/justfile`

| Recipe | Command | Notes |
|--------|---------|-------|
| `youtube-transcript <id>` | `claude --chrome "/bowser:youtube-transcript {id}"` | Requires Chrome extension (broken from CLI) |
| `youtube-transcript-to <id> <dir>` | `claude --chrome "/bowser:youtube-transcript {id} {dir}"` | Same limitation |
| `tac-scan <days>` | `claude --chrome "/youtube-tac-extract {days}"` | TAC channel scanning |
| `tac-scan-video <id>` | `claude --chrome "/youtube-tac-extract video {id}"` | Single video TAC scan |

### Practical Workaround

Since `--chrome` doesn't work from within Claude Code, the actual workflow is:

1. Use MCP Chrome DevTools for description/metadata extraction
2. Use Apify for transcript extraction
3. Use WebFetch for following resource links from descriptions
4. Combine all outputs into the standard file convention

---

## Part 6: QA and UI Review

### User Story Format (YAML)

```yaml
stories:
  - name: "Front page loads with posts"
    url: "https://news.ycombinator.com"
    workflow: |
      1. Navigate to the URL
      2. Verify the page loads with post titles visible
      3. Check that at least 10 posts are listed
      4. Verify each post has a title, points, and comment count
```

### QA Architecture

```
/bowser:ui-review
    │
    ├─→ Phase 1: Discover (Glob YAML files)
    ├─→ Phase 2: Spawn (one bowser-agent (QA mode) per story, parallel)
    ├─→ Phase 3: Collect (parse PASS/FAIL from each agent)
    └─→ Phase 4: Report (aggregated summary table)
```

### Screenshot Convention

```
screenshots/bowser-qa/{YYYYMMDD_HHMMSS}_{uuid}/
├── {file-stem}/
│   ├── {slugified-story-name}/
│   │   ├── step-1.png
│   │   ├── step-2.png
│   │   └── ...
```

---

## Part 7: Best Practices

### Backend Selection

| Scenario | Backend | Reason |
|----------|---------|--------|
| Page requires auth | claude-bowser | Uses real Chrome (but separate profile) |
| Public page scraping | playwright-bowser | Headless, parallel, faster |
| UI testing | bowser-agent (QA mode) | Parallel instances, structured results |
| YouTube transcripts | Apify (not browser) | Browser transcript panel needs Google sign-in |
| YouTube descriptions | claude-bowser | Works without auth, full URL extraction |
| Blog reading | playwright-bowser | No auth needed, headless fine |

### Performance Rules

| Rule | Why |
|------|-----|
| Use Apify for YouTube transcripts | Browser method unreliable without sign-in |
| Ignore YouTube navigation timeouts | Page renders despite timeout error |
| Extract full URLs via JS evaluation | YouTube truncates URLs in display text |
| Use `take_snapshot` over `take_screenshot` | Faster, gives interactive element UIDs |
| Follow resource links with WebFetch | Don't navigate browser away from YouTube |

### Safety Rules

| Rule | Why |
|------|-----|
| Never submit Amazon orders | Stop at checkout page |
| Don't click "Buy Now" or "Place Order" | Financial transactions require human |
| Verify page state with `take_snapshot` | Ensure correct page before interacting |
| Use `wait_for` before extracting | Ensure dynamic content has loaded |
| Save screenshots at each step | Audit trail for QA workflows |

### Error Recovery

| Error | Fix |
|-------|-----|
| Navigation timeout on YouTube | Ignore and proceed — content is rendered |
| Transcript spinner hangs | Switch to Apify fallback |
| MCP server wedged | Call `list_pages` to reset, retry |
| "Cannot launch inside Claude Code" | Use MCP tools directly, not `claude --chrome` |
| Description URLs truncated | Use `evaluate_script` to get full `href` values |

---

## Part 8: Reference Implementations

### Key Files

| File | Purpose |
|------|---------|
| `.claude/commands/bowser/youtube-transcript.md` | Browser-based YouTube extraction workflow |
| `.claude/skills/youtube-transcript-apify.md` | Apify-based transcript extraction (reliable fallback) |
| `.claude/skills/browser-automation/justfile` | Just recipes for browser automation |
| `.claude/commands/bowser/ui-review.md` | Parallel QA with bowser-agent (QA mode)s |
| `.claude/commands/bowser/hop-automate.md` | Generic workflow runner |
| `.claude/commands/bowser/amazon-add-to-cart.md` | Amazon shopping automation |
| `.claude/commands/bowser/blog-summarizer.md` | Blog post summarization |
| `ai_review/user_stories/*.yaml` | QA user story definitions |

### Extracted Videos (tac-scan archive)

| Video ID | Title | Channel | Chars |
|----------|-------|---------|-------|
| `8kNv3rjQaVA` | 21 INSANE Use Cases for OpenClaw | Matthew Berman | 34,756 |
| `2HiHDIFStzg` | Anthropic just BANNED OpenClaw... | Matthew Berman | 9,390 |
| `fkT41ooKBuY` | I cut my OpenClaw API bill by 80% | VelvetShark | 7,409 |

---

## Part 9: Skill and Agent Types

### Agent Type Reference

All browser tasks now use the unified `bowser-agent` which auto-selects the right backend:

| Mode | Use Case | Parallel | Backend |
|------|----------|----------|---------|
| Browse (default) | General browsing, scraping, screenshots | Yes (Playwright) / No (Chrome DevTools) | Auto-selected |
| QA | User story validation | Yes | Playwright CLI |
| Plan | Workflow design and advisory | N/A | No browser execution |

The agent auto-selects Chrome DevTools (headed) vs Playwright (headless) based on whether auth is needed.

### Skill Invocation

```
/bowser:youtube-transcript <video-id>      # Browser-based YouTube extraction
/bowser:ui-review [headed] [filter]        # Parallel QA validation
/bowser:hop-automate <workflow> [options]   # Run saved workflow
/bowser:amazon-add-to-cart <item>           # Amazon shopping
/bowser:blog-summarizer <url>              # Blog summarization
```
