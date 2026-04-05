---
name: monitor-feeds
description: "Trading: Monitor Feeds - Watch volume spikes and indicator alerts; fire Telegram alerts on threshold crossings"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY", "TELEGRAM_BOT_TOKEN"]}}}
---

# Monitor Feeds

Watch configured data feeds for volume spikes and indicator conditions. Fire Telegram alerts when thresholds are crossed. Runs every 15 minutes via heartbeat.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Check Volume Feeds
1. Read configured alert rules from `memory/feed-rules.json`
2. For each monitored ticker: fetch latest 15m volume from Hyper Liquid API
3. Compare to rolling average volume (last 20 periods)
4. Flag if current volume > average × volume_spike_multiplier (default: 3x)

### Phase 2: Check Indicator Conditions
1. For each configured indicator alert:
   - Fetch latest price/indicator data
   - Evaluate condition: RSI > {threshold}, price crosses MA, etc.
   - Flag if condition met and not already triggered in last {cooldown_minutes}

### Phase 3: Fire Alerts
1. For each triggered condition:
   - Log to `memory/feed-alerts/{YYYY-MM-DD}.json`
   - Send Telegram alert: `⚡ Alert: {condition_name} on {ticker} | {details} | {timestamp}`
   - Optionally: queue a chart generation task for the triggered ticker
2. Update `memory/feed-state.json` with last trigger timestamps (prevent duplicate alerts)
3. During quiet hours (00:00–06:00 PST): log only, no Telegram alerts

## Output Format
```
Feed check complete: {ticker_count} tickers scanned
Alerts fired: {alert_count}
Volume spikes detected: {spike_count}
```

## Error Handling
- API timeout → skip this cycle, log; don't fire false alerts
- All conditions quiet → log HEARTBEAT_OK
