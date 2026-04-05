---
name: daily-lesson
description: "Trading: Daily TA Lesson - Deliver today's technical analysis lesson from the 30-day Kiyotaka curriculum"
metadata: {"openclaw": {"requires": {"env": ["ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]}}}
---

# Daily TA Lesson

Deliver today's technical analysis lesson sourced from the Kiyotaka academy guides. Progresses through a 30-day curriculum covering candlesticks, orderbook heatmaps, volume footprints, VWAP, OI/CVD/funding, and Market Profile/TPO.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Check Progress
```bash
python ~/hyperliquid-python-sdk/scripts/daily_lesson.py --status
```
Report current day number and topic.

### Phase 2: Deliver Lesson
```bash
python ~/hyperliquid-python-sdk/scripts/daily_lesson.py
```
Fetches live BTC context, loads kiyotaka academy source material, generates lesson via Claude, delivers to Telegram + Discord.

### Phase 3: Confirm Delivery
Check exit code. Log result. If delivery failed, report error to Greg.

## CLI Options

| Option | Effect |
|--------|--------|
| `--day N` | Override lesson day (1-30) |
| `--dry-run` | Generate + print, no Telegram/Discord delivery |
| `--force` | Re-deliver today's lesson even if already sent |
| `--reset` | Restart curriculum at Day 1 |

## Output Format
Lesson delivered to Telegram (primary) + Discord #morning-brief. Saved to `~/hyperliquid-python-sdk/outputs/mentor/day_NN_YYYY-MM-DD.md`.

## Error Handling
- Claude API unavailable → fallback template lesson delivered
- Telegram send fails → lesson still saved to file, error reported
- BTC data fetch fails → lesson generated without live price context (noted in lesson)
