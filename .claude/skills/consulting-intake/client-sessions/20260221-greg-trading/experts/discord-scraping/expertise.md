---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: expertise
human_reviewed: false
tags: [expert-file, mental-model, discord-scraping, trading]
last_updated: 2026-02-21
---

# Discord & Scraping Expert - Complete Mental Model

## Part 1: Domain Architecture

### Overview
The Discord & Scraping domain operates as Greg's signal intelligence layer. It runs continuously in the background, checking three data streams: Discord channels (every 15 minutes), data feeds for volume/indicator events (every 15 minutes), and YouTube (daily overnight). The primary output is structured signal records, alerts, and the daily morning brief.

### Tool Connections
```
Discord API (bot read access)
    ↓
Signal Parser (quality scoring)
    ↓ High-quality signals (score ≥ 7)
Telegram Bot → Greg

Hyper Liquid API (price/volume feeds)
    ↓
Feed Monitor (threshold checking)
    ↓ Threshold crossed
Telegram Bot → Greg
         ↓ (optional)
Charting Agent → generate-chart

YouTube Data API
    ↓
Transcript Summarizer (nightly)
    ↓
Memory: youtube-insights/

All streams → Morning Brief Compiler → Telegram → Greg (7 AM PST)
```

### Key File Locations
| File | Purpose |
|------|---------|
| `memory/discord-signals/{YYYY-MM-DD}.json` | Daily signal log |
| `memory/discord-state.json` | Last checked message IDs per channel |
| `memory/youtube-insights/{YYYY-MM-DD}.json` | Daily YouTube summaries |
| `memory/feed-alerts/{YYYY-MM-DD}.json` | Feed alert log |
| `memory/feed-state.json` | Last trigger timestamps (dedup) |
| `memory/feed-rules.json` | Alert rule configuration |
| `memory/morning-briefs/{YYYY-MM-DD}.md` | Archived morning briefs |

### Data Flows
- Discord → parsed signals → memory log → Telegram (if high-quality)
- Hyper Liquid feeds → threshold check → memory log → Telegram alert + optional chart
- YouTube API → transcript → summarized insight → memory → morning brief
- All memory → morning brief compiler → Telegram

---

## Part 2: Primary Workflow — Discord Signal Scrape (Every 15 Minutes)

### Trigger
- Type: cron
- Schedule: `*/15 * * * *`
- Timezone: UTC (server time); quiet hours check in America/Los_Angeles

### Steps
1. Load `memory/discord-state.json` for last message IDs per channel
2. For each configured channel ID: `GET /channels/{id}/messages?after={last_id}&limit=100`
3. Filter messages since last check timestamp
4. Parse each message for signal patterns:
   - Ticker: regex for known Hyper Liquid tickers (BTC-PERP, ETH-PERP, HYPE-PERP, etc.)
   - Direction: keywords LONG, SHORT, BUY, SELL (case-insensitive)
   - Entry: price or "entry at {price}"
   - TP (Take Profit): "TP {price}", "target {price}"
   - SL (Stop Loss): "SL {price}", "stop {price}", "stop loss {price}"
5. Score signal (0–10):
   - Ticker present: +2
   - Direction present: +2
   - Entry present: +2
   - TP present: +2
   - SL present: +2
6. Write all signals (score ≥ 3) to `memory/discord-signals/{date}.json`
7. Update `memory/discord-state.json` with latest message IDs
8. For score ≥ 7: send Telegram alert
9. Check quiet hours (00:00–06:00 PST); suppress Telegram if in quiet window

### API Endpoints Used
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://discord.com/api/v10/channels/{id}/messages` | GET | Fetch new messages |

### Expected Inputs
- Channel IDs to monitor (configured in `memory/feed-rules.json`)
- Discord bot token (env: `DISCORD_BOT_TOKEN`)

### Expected Outputs
- Structured signal records in `memory/discord-signals/{date}.json`
- Telegram alerts for signals with score ≥ 7

### Approval Gates
None — fully autonomous monitoring. Greg reviews signals at his discretion.

---

## Part 3: Secondary Workflows

### YouTube Daily Scrape

**Trigger**: Cron nightly (configurable, default 1:00 AM PST)
**Steps**:
1. Query YouTube Data API for new videos on tracked channels/search terms
2. Fetch transcripts for new videos (yt-dlp or YouTube Data API captions)
3. Summarize: 3 key points per video using Claude
4. Tag: strategy, market-analysis, risk-management, fundamentals
5. Write to `memory/youtube-insights/{date}.json`
6. Top 1–2 insights queued for morning brief

**Output**: Summarized insights in memory, surfaced in morning brief

### Morning Brief

**Trigger**: Cron `0 7 * * *` America/Los_Angeles
**Steps**: (See SKILL.md for full detail)
1. Pull overnight Discord signals (top 3–5 by quality)
2. Pull Hyper Liquid portfolio snapshot
3. Market overview (BTC/ETH/HYPE prices + 24h change + volume)
4. News digest (WebSearch, last 12 hours)
5. YouTube insights (last 24h)
6. Compose structured brief
7. Deliver via Telegram

**Output**: Daily brief delivered via Telegram, archived in memory

### Edge Cases & Variations
- Discord bot rate limited: back off for 1 minute, retry once; log failure if still failing
- YouTube quota exhausted (10,000 units/day): fall back to WebSearch for video discovery; note in morning brief
- No new Discord messages: log HEARTBEAT_OK — not an error
- Discord channel removed or access revoked: alert Greg, mark channel as inactive in feed-rules.json

---

## Part 4: Tool Configuration

| Tool | Base URL | Auth Header | Key Endpoints |
|------|----------|-------------|---------------|
| Discord API v10 | `https://discord.com/api/v10` | `Authorization: Bot {DISCORD_BOT_TOKEN}` | `/channels/{id}/messages` |
| YouTube Data API v3 | `https://www.googleapis.com/youtube/v3` | `key={YOUTUBE_API_KEY}` (query param) | `/search`, `/videos`, `/captions` |
| Hyper Liquid | `https://api.hyperliquid.xyz` | None (public endpoints) | `/info` (POST with type field) |

### MCP Server Availability
- Discord MCP: not confirmed — use direct REST API calls via Bash/curl
- YouTube MCP: not confirmed — use direct API calls
- Check ClawHub for updates

### ClawHub Plugin Availability
- Search ClawHub for "discord" and "youtube" before deploying — may save implementation time

---

## Part 5: Scheduling & Automation

### Cron Jobs

| Name | Schedule | Skill | Mode | Delivery |
|------|----------|-------|------|----------|
| Discord Scrape | `*/15 * * * *` | scrape-discord | isolated | none (alerts via skill) |
| Feed Monitor | `*/15 * * * *` | monitor-feeds | isolated | none (alerts via skill) |
| Morning Brief | `0 7 * * *` PST | morning-brief | main | announce |
| YouTube Scrape | `0 1 * * *` PST | (inline in morning-brief) | isolated | none |

### Heartbeat Tasks
- Check Discord channels every 15m heartbeat (same as cron — dedup logic in discord-state.json)
- Volume spike checks on data feeds every 15m

### Trigger Patterns
- Discord: time-driven (every 15m poll) — WebSocket ideal long-term but requires persistent connection
- Volume alerts: threshold-driven on polled data — move to WebSocket feed when available
- Morning brief: cron-driven, hard daily delivery

---

## Part 6: Integration Points

### Cross-Domain Connections
- **→ Portfolio Manager**: High-quality Discord signals surface context for trade proposals
- **→ Back Tester**: Overnight research (YouTube insights, news) informs strategy ideas for backtesting
- **→ Charting**: Volume spike alerts can queue chart generation on the triggered ticker

### Shared Tools or Data Sources
- Hyper Liquid API used by: this domain (feed monitoring), Portfolio Manager (position data), Back Tester (historical data), Charting (price data)
- Telegram Bot used by: all domains for delivery

### Workflow Handoffs
1. Discord scrape detects high-quality signal → portfolio manager context includes signal for trade proposal
2. Volume spike alert fires → charting agent generates 15m chart of ticker and attaches to alert
3. YouTube insights → morning brief includes top 1–2 insights + links to back-tester for strategy ideas

---

## Part 7: Patterns & Learnings

### Patterns That Work
- (Populated after first self-improve cycle)

### Patterns To Avoid
- (Populated after first self-improve cycle)

### Known Issues
- Discord rate limits: 50 req/s per bot globally, 5 req/s per channel — stagger multi-channel fetches
- YouTube quota: 10,000 units/day; search costs 100 units, video details cost 1 unit — budget carefully

### Tips
- Start with 1–2 Discord channels for testing before expanding to many
- Signal scoring thresholds (≥ 7 for alert) may need tuning based on Greg's channel noise levels
- YouTube: track channels by ID not by name to survive channel renames
