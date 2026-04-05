# MEMORY.md — Greg Trading
# Private: loaded ONLY in direct/private sessions. Never in group chats.

## Mission

Sebastian is a sharp, professional trading AI that manages Greg's entire trading intelligence operation across Hyper Liquid, Discord signal pipelines, backtesting, and market research — so that Greg can focus on high-quality trade decisions while Sebastian handles the grind of monitoring, scanning, and optimization. Sebastian operates with near-full autonomy, checking in only on critical architecture calls and trade execution, with the goal of making Greg consistently profitable within 90 days.

## 90-Day Goals

| Milestone | Target | Status |
|-----------|--------|--------|
| Paper trading live with data pipelines | Week 1 | ✅ Live — position_monitor.py running |
| Trade monitoring + proposal system | Day 3 | ✅ Done — 5-min Telegram position updates |
| Daily TA education system | Week 1 | ✅ Done — 30-day Kiyotaka curriculum, 08:00 UTC daily |
| Discord signal pipeline + morning brief | 30 days | 🔨 Stub jobs built, need implementation |
| Paper trading validated (backtested edge) | 2 weeks | ⏳ Pending |
| Consistent profitability (validated strategy) | 90 days | ⏳ Pending |

## Key Decisions

- **Primary autonomous overnight task**: Backtest new strategies + scrape information pipelines + scout datasets
- **Model routing**: Claude Haiku (lessons/analysis), Claude Sonnet (heavy reasoning), GLM-4.7 via OpenRouter (cheap tasks)
- **Trade execution**: MANUAL until explicitly unlocked by Greg. Sebastian proposes, Greg executes.
- **Memory mode**: Long-term (remember everything). Use `/new` or `/reset` for clean sessions on trade decisions.
- **Compute**: Mac Mini (Gregs-Mac-mini.local) — always-on, runs launchd daemons

## What's Built and Running (as of 2026-03-19)

### Expert Scheduler Daemon
- **13 jobs** running via APScheduler on Mac Mini
- Plist: `~/Library/LaunchAgents/ai.hyperliquid.expert-scheduler.plist`
- Log: `~/hyperliquid-python-sdk/logs/expert_scheduler.log`
- **Fully working**: `position_monitor` (5-min), `daily_lesson` (08:00 UTC)
- **Stubs needing implementation**: signal_scout_scan, risk_guard_audit, kscript_screener, whale_room_scrape, morning_brief_assembly, morning_brief_delivery, trade_journal_nightly, weekly_backtest_report

### Daily Lesson System
- `~/hyperliquid-python-sdk/scripts/daily_lesson.py`
- 30-day Kiyotaka curriculum (Days 1-7 Foundations, 8-11 Heatmaps, 12-16 Footprints, 17-23 VWAP/Derivatives, 24-28 Market Profile, 29-30 Integration)
- Delivers to Telegram (chat 6777263736) + Discord #morning-brief
- Academy source files: `~/hyperliquid-python-sdk/.claude/commands/experts/kiyotaka/academy/`
- Currently on Day 1 (progress tracked in `outputs/mentor/progress.json`)
- OpenClaw cron also triggers at 08:00 UTC via system event to main session

### Position Monitor
- `~/hyperliquid-python-sdk/scripts/position_monitor.py`
- Fires every 5 min via scheduler
- Reads live positions from Hyperliquid REST (`Info.user_state(ACCOUNT_ADDRESS)`)
- Sends Telegram update only when positions exist
- Live tested 2026-03-19 — confirmed working with real position data

### Expert Knowledge Base
- All expert files at: `~/hyperliquid-python-sdk/.claude/commands/experts/`
- Directories: kiyotaka, discord, telegram, websocket-hyperliquid, quant, scalping, whale-room, supabase, tac
- **Always read relevant expert files before building a skill or script in that domain**

## Established Strategies

*(Populated as strategies are backtested and validated)*

## Known Preferences

- Always propose stop-losses with any trade idea
- Charts > tables for trend data
- Morning brief = first thing Greg reads — make it sharp
- If a signal is weak or a strategy looks bad, say so directly
- Telegram is the primary delivery channel — Discord secondary
- Position updates every 5 minutes when trade is open

## Long-Term Context

- Greg started at Hyper Liquid; wants to expand to other markets over time
- Wants broader market opportunity scouting as the system matures
- Underlying goal: build a reliable income stream from trading, not just a side project
- Greg values observability and visual reporting highly — always include charts/summaries with key outputs
- Account address: `0x109A42c3eAD059b041560Cb6Da71058516e7Ba3e`

## Next Priorities for Sebastian

1. **Discord channel IDs** — Greg needs to provide the signal feed + whale room channel IDs so Sebastian can start scraping
2. **DISCORD_WEBHOOK_MORNING_BRIEF** — get webhook URL from Greg for #morning-brief delivery
3. **Implement signal_scout_scan** — read expert files at `experts/discord/` and `experts/whale-room/` then build the scanner
4. **Implement risk_guard_audit** — check open positions for SL/drawdown/funding issues every 15 min
5. **Implement morning_brief_assembly** — pull signals, screener results, overnight moves, assemble brief
6. **Kiyotaka gRPC screener** — read `experts/kiyotaka/expertise.md` and `experts/kiyotaka/kscript.md` to build the screener job
