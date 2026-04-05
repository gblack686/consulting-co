# Greg Trading — OpenClaw Workspace Package
**Built**: 2026-02-21
**Agent Name**: Sebastian 📊
**Client**: Greg (Los Angeles, PST)
**Validation Score**: 94/100 ✅

---

## What Was Built

Complete OpenClaw workspace for a professional trading AI assistant covering 4 domains, 11 skills, 7 cron jobs, and 4 domain expert systems.

---

## Package Structure

```
client-sessions/greg-trading/
├── session_output/                     ← Parsed transcript data
│   ├── client_profile.json
│   ├── soul_draft.md
│   ├── identity.json
│   ├── mission_statement.md
│   ├── tool_inventory.json
│   ├── autonomy.json
│   └── domains/
│       ├── discord-scraping.json
│       ├── portfolio-manager.json
│       ├── back-tester.json
│       └── charting.json
│
├── workspace/                          ← Deploy to OpenClaw server
│   ├── USER.md                         Greg's profile
│   ├── SOUL.md                         Sebastian's constitution
│   ├── IDENTITY.md                     Sebastian 📊, sharp trading AI
│   ├── MEMORY.md                       Mission + 90-day goals
│   ├── AGENTS.md                       Session behavior + memory arch
│   ├── TOOLS.md                        Hyper Liquid, Discord, Telegram, YouTube
│   ├── HEARTBEAT.md                    15m trading checks + 30m general
│   ├── openclaw.json                   Multi-agent config (Pattern B)
│   ├── cron-setup.sh                   Install 7 cron jobs
│   └── skills/
│       ├── discord-scraping/
│       │   ├── scrape-discord/SKILL.md
│       │   ├── morning-brief/SKILL.md
│       │   └── monitor-feeds/SKILL.md
│       ├── portfolio-manager/
│       │   ├── monitor-positions/SKILL.md
│       │   ├── manage-risk/SKILL.md
│       │   └── trade-journal/SKILL.md
│       ├── back-tester/
│       │   ├── run-backtest/SKILL.md
│       │   ├── optimize-strategy/SKILL.md
│       │   └── scout-datasets/SKILL.md
│       └── charting/
│           ├── generate-chart/SKILL.md    (user-invocable: /generate-chart)
│           └── generate-equity-curve/SKILL.md
│
└── experts/                            ← Claude Code expert systems
    ├── discord-scraping/               8 files
    ├── portfolio-manager/              8 files
    ├── back-tester/                    8 files
    └── charting/                       8 files
```

---

## Agents Deployed

| Agent ID | Name | Model | Purpose |
|----------|------|-------|---------|
| main | Sebastian | glm47 | Primary orchestrator |
| discord-scraping | Signal Scout | glm47-lite | Discord + feeds |
| portfolio-manager | Risk Guard | glm47 | Position monitoring |
| back-tester | Quant | glm47 | Strategy testing |
| charting | Chart Maker | glm47-lite | Chart generation |

---

## Cron Schedule

| Job | Schedule | Skill | Note |
|-----|----------|-------|------|
| Morning Brief | 7:00 AM PST daily | morning-brief | Greg's daily read |
| Discord Scrape | Every 15 min | scrape-discord | Signal intelligence |
| Feed Monitor | Every 15 min | monitor-feeds | Volume + indicators |
| Position Monitor | Every 15 min | monitor-positions | Stop-loss guardian |
| Nightly Backtest | 2:00 AM PST daily | run-backtest | Overnight testing |
| Dataset Scout | Sunday 10 PM PST | scout-datasets | Weekly data search |
| Trade Journal Weekly | Monday 7 AM PST | trade-journal | Performance review |

---

## Key Design Decisions

### 1. Trade Execution is Manual (For Now)
All portfolio management skills have `[APPROVAL GATE]` markers. Sebastian monitors, alerts, and proposes — Greg executes. This is Greg's explicit requirement and matches his risk comfort level.

### 2. Multi-Agent Pattern B (Domain-Specific Agents)
4 domain agents route from the main Sebastian agent. This allows domain experts to operate in isolated contexts (especially important for charting and backtesting which have different context needs than risk monitoring).

### 3. Memory: Long-Term by Default, Clean on Demand
Greg wants to "remember everything forever" but needs clean sessions for trade decisions to prevent bias. Solution: long-term memory by default, `/clean` or `/reset` available for unbiased trade analysis sessions.

### 4. glm47 Brain / glm47-lite Muscle
Greg specified two-tier model routing. Brain (glm47) for Sebastian main, portfolio manager, and back-tester (all require reasoning). Muscle (glm47-lite) for signal scout and charting (mechanical tasks). **Action required**: verify glm47 model ID with Greg before deployment.

### 5. Runs Locally on Greg's Laptop
OpenClaw runs on Greg's Lenovo Windows machine — not a cloud server. Ensure the laptop stays on for overnight cron jobs. Paper trading is the first validation step before live capital is deployed.

---

## 90-Day Roadmap (Greg's Goals)

| Target | Milestone |
|--------|-----------|
| **Day 3** | Trade execution monitoring ready (monitor-positions live on testnet) |
| **Week 1** | Paper trading live + morning brief + Discord signal pipeline |
| **2 Weeks** | Validated paper trading strategy with back-test confirmation |
| **30 Days** | Full Discord + dashboard system operational |
| **90 Days** | Consistent profitability on validated live strategy |

---

## Pre-Deployment Checklist

- [ ] Greg provides: Hyper Liquid API key + secret
- [ ] Greg provides: Discord bot token + channel IDs to monitor
- [ ] Greg provides: Telegram bot token + Greg's Telegram user ID
- [ ] Greg provides: YouTube Data API key
- [ ] Greg confirms: glm47 model provider and API key
- [ ] Replace `GREG_TELEGRAM_ID` placeholder in `openclaw.json`
- [ ] Run `cron-setup.sh` on OpenClaw server
- [ ] First test: generate a test morning brief (on-demand)
- [ ] First test: generate a chart for BTC 1h
- [ ] First test: run monitor-positions on testnet
- [ ] Confirm quiet hours with Greg (default: 00:00–06:00 PST)

---

## Files Requiring Greg's Input

| File | What to Fill In |
|------|----------------|
| `workspace/openclaw.json` | Replace `GREG_TELEGRAM_ID` |
| `workspace/TOOLS.md` | Confirm working hours |
| `workspace/MEMORY.md` | Monthly budget ceiling |
| `memory/feed-rules.json` (create on deploy) | Discord channel IDs |
| `~/.openclaw/strategies/` (create on deploy) | First strategy Python file |
