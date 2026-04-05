# ADW Status Skill

Monitor running ADWs across local and GitHub Actions with cost tracking.

## Invocation

```
/adw-status
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `github_repo` | `gblack686/consulting-co` | GitHub repository |
| `poll_interval` | `10` | Polling interval in seconds |
| `max_runs` | `10` | Max workflow runs to show |

## Core Capabilities

| Capability | Command | Description |
|------------|---------|-------------|
| List All | `python scripts/list_running.py` | All running ADWs |
| GitHub Status | `python scripts/get_github_status.py` | GitHub Actions status |
| Local Status | `python scripts/get_local_status.py` | Local task status |
| Cost Summary | `python scripts/cost_summary.py` | Token/cost breakdown |

## Quick Start

```bash
# List all running ADWs
python .claude/skills/adw-status/scripts/list_running.py

# Check GitHub Actions runs
python .claude/skills/adw-status/scripts/get_github_status.py

# Get cost summary
python .claude/skills/adw-status/scripts/cost_summary.py
```

## Output Format

```
ADW Status Report
================

LOCAL TASKS (1 running):
  [haiku] Fix typo - running (2m 15s)
    Tokens: 1,234 | Cost: $0.003

GITHUB ACTIONS (2 running):
  [opus] Implement auth - in_progress
    URL: https://github.com/.../actions/runs/123
    Started: 5 minutes ago

  [opus] Add API tests - queued
    URL: https://github.com/.../actions/runs/124
    Queued: 1 minute ago

COST SUMMARY:
  Today: $0.12 / $1.00 (12%)
  Local: $0.12 | GitHub: $0.00
```

## Source Files

- `scripts/list_running.py` - List all ADWs
- `scripts/get_github_status.py` - GitHub Actions status
- `scripts/get_local_status.py` - Local task status
- `scripts/cost_summary.py` - Cost breakdown
- `scripts/status_ops.py` - Core operations
- `config/settings.json` - Configuration
