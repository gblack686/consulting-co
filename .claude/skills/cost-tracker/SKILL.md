# Cost Tracker Skill

Track API costs against daily budget with alerts.

## Invocation

```
/cost-tracker
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `daily_budget` | `1.00` | Daily budget in USD |
| `alert_threshold` | `0.80` | Alert at 80% of budget |
| `haiku_input_cost` | `0.001` | $ per 1K input tokens |
| `haiku_output_cost` | `0.005` | $ per 1K output tokens |

## Core Capabilities

| Capability | Command | Description |
|------------|---------|-------------|
| Check Budget | `python scripts/check_budget.py` | Current budget status |
| Log Usage | `python scripts/log_usage.py <tokens> <model>` | Log API call |
| Daily Report | `python scripts/daily_report.py` | Full daily breakdown |
| Alert Check | `python scripts/alert_threshold.py` | Check against limits |

## Quick Start

```bash
# Check current budget status
python .claude/skills/cost-tracker/scripts/check_budget.py

# Log an API call
python .claude/skills/cost-tracker/scripts/log_usage.py 1500 2000 haiku

# Get daily report
python .claude/skills/cost-tracker/scripts/daily_report.py

# Check if near alert threshold
python .claude/skills/cost-tracker/scripts/alert_threshold.py
```

## Pricing Reference

| Model | Input (per 1K) | Output (per 1K) |
|-------|---------------|-----------------|
| Haiku | $0.001 | $0.005 |
| Sonnet | $0.003 | $0.015 |
| Opus | $0.015 | $0.075 |

## Budget Display

```
Daily Budget: $1.00
Used Today:   $0.42
[████████████░░░░░░░░░░░░░░░░░░] 42%

Breakdown:
  Local Haiku:     $0.42
  GitHub Actions:  $0.00 (free with Max)

Remaining: $0.58
Est. Tasks: ~116 (at ~$0.005/task)
```

## Data Storage

Usage data is stored in `data/usage_log.json`:
```json
{
  "entries": {
    "2026-01-17": [
      {"timestamp": "...", "tokens": 1500, "cost": 0.0045, "model": "haiku"},
      ...
    ]
  },
  "daily_totals": {
    "2026-01-17": 0.42
  }
}
```

## Source Files

- `scripts/check_budget.py` - Budget status
- `scripts/log_usage.py` - Log API call
- `scripts/daily_report.py` - Daily breakdown
- `scripts/alert_threshold.py` - Alert checks
- `scripts/cost_ops.py` - Core operations
- `config/settings.json` - Configuration
- `data/usage_log.json` - Usage tracking
