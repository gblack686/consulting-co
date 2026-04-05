---
name: scrape-discord
description: "Trading: Scrape Discord - Monitor trade signal channels for new tips every 15 minutes"
metadata: {"openclaw": {"requires": {"env": ["DISCORD_BOT_TOKEN"]}}}
---

# Scrape Discord

Monitor Greg's configured Discord trading channels for new trade signals. Run every 15 minutes via cron.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Fetch New Messages
1. Read `TOOLS.md` for Discord bot token and channel IDs to monitor
2. Call Discord API: `GET /channels/{channel_id}/messages?after={last_message_id}&limit=100`
3. Load `last_checked_message_id` from `memory/discord-state.json` (or use timestamp if not set)
4. Fetch all new messages across all monitored channels

### Phase 2: Parse Signals
1. For each new message: check for trade signal patterns
   - Look for: ticker symbols (e.g., BTC, ETH, HYPE), direction keywords (LONG, SHORT, BUY, SELL), price levels
   - Structure signal: `{ticker, direction, entry, tp, sl, source_channel, author, timestamp, raw_text}`
2. Filter noise: skip messages without clear ticker + direction
3. Score signal quality (0-10): higher score for signals with explicit entry + TP + SL

### Phase 3: Log and Alert
1. Write all parsed signals to `memory/discord-signals/{YYYY-MM-DD}.json`
2. Update `memory/discord-state.json` with latest message IDs
3. For signals with quality_score >= 7: send Telegram alert to Greg
   - Format: `📡 Signal: {direction} {ticker} | Entry: {entry} | TP: {tp} | SL: {sl} | Source: {channel}`
4. During quiet hours (00:00–06:00 PST): log only, no Telegram alert

## Output Format
```
Scrape complete: {channel_count} channels checked
New signals: {signal_count} ({high_quality_count} high-quality)
Alerts sent: {alert_count}
```

## Error Handling
- Discord API rate limited → wait 1 minute, retry once; log failure if still failing
- Bot token invalid → alert Greg via Telegram with error details
- No new messages → log HEARTBEAT_OK quietly
