---
name: expert-scheduler
description: "Trading: Expert Scheduler - Start, stop, check status, or run individual expert system jobs"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]}}}
---

# Expert Scheduler Control

Manages the 12-job expert system scheduler that orchestrates all trading automation on the Mac Mini.

## Allowed Tools
`Bash, Read`

## Jobs Available

| Job | Schedule | Purpose |
|-----|----------|---------|
| `kscript_screener` | Every 30 min | kiyotaka gRPC coin screener (score 0-100) |
| `signal_scout_scan` | Every 15 min | Discord + Whale Room signal aggregation |
| `risk_guard_audit` | Every 15 min | Position audit: SL check, drawdown, funding |
| `whale_room_scrape` | Every 30 min | Whale Room signal extraction |
| `indicator_stream_watchdog` | Every 5 min | Restart indicator stream if down |
| `auto_bracket_watchdog` | Every 5 min | Restart auto-bracket daemon if down |
| `daily_lesson` | 08:00 UTC | TA mentor lesson delivery |
| `morning_brief_assembly` | 04:00 UTC | Assemble morning brief |
| `morning_brief_delivery` | 10:00 UTC | Deliver morning brief to Telegram + Discord |
| `trade_journal_nightly` | 23:30 UTC | Grade fills, update trade journal |
| `supabase_maintenance` | 02:00 UTC | Prune old rows, check vault secrets |
| `weekly_backtest_report` | Sun 01:00 UTC | GeneticAlpha weekly backtest |

## Workflow

### Check Scheduler Status
```bash
python ~/hyperliquid-python-sdk/scripts/expert_scheduler.py --status
```
Lists all jobs and their next scheduled run time.

### Run a Specific Job Now
```bash
python ~/hyperliquid-python-sdk/scripts/expert_scheduler.py --once --job <job_id>
```

### Dry Run (test without side effects)
```bash
python ~/hyperliquid-python-sdk/scripts/expert_scheduler.py --once --dry-run
```

### Start Scheduler (continuous)
The scheduler should be running as a launchd daemon. To manually start:
```bash
launchctl start ai.hyperliquid.expert-scheduler
```

### Check Daemon Health
```bash
launchctl list | grep expert-scheduler
tail -50 ~/hyperliquid-python-sdk/logs/expert_scheduler.log
```

### Restart Daemon
```bash
launchctl stop ai.hyperliquid.expert-scheduler
launchctl start ai.hyperliquid.expert-scheduler
```

## Output Format
Reports job status, next run times, and any recent errors from the log file.
