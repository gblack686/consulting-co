---
name: graphify-sync
description: "Scan all client repos on Mac Mini, diff files since last graphify run, and re-run graphify --update on repos with changes. Keeps knowledge graphs fresh."
triggers:
  - graphify sync
  - sync graphs
  - update knowledge graphs
  - client graph scan
model: haiku
---

# graphify-sync

Scans every client repo on Mac Mini, compares file trees against last snapshot, and runs `graphify . --update` on repos that changed. Keeps GRAPH_REPORT.md and graph.json current for agents like Finn.

## Usage

```bash
# Scan all repos, update changed ones
python scripts/graphify_sync.py

# Single repo
python scripts/graphify_sync.py --repo fisch-group

# Force re-graphify all repos
python scripts/graphify_sync.py --force

# Dry run — show what changed without running graphify
python scripts/graphify_sync.py --dry-run

# Show registry and last-run status
python scripts/graphify_sync.py --list
```

## Config

Edit `config/repos.json` to add/remove repos. Each repo needs:
- `path`: Mac Mini path (e.g., `~/repos/fisch-group`)
- `display_name`: Human label
- `graphify_flags`: Extra flags (e.g., `--wiki` for wiki article generation)
- `auto_update`: Set `false` to skip unless `--force`

## How it works

1. SSH to Mac Mini, `find` all files (excluding .git, node_modules, graphify-out)
2. Compare `{path: mtime}` against last snapshot in `state/{repo}.json`
3. If files added/modified/deleted → run `claude -p '/graphify . --update'` via Meridian pipeline
4. Save new snapshot for next run

## Scheduling

Run daily alongside `daily-client-logs`:

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "C:\...\graphify-sync\scripts\graphify_sync.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -TaskName "GBAutomation-Graphify-Sync" -Action $action -Trigger $trigger
```

## Dependencies

- Python 3.9+ (stdlib only, runs on Windows)
- SSH access to Mac Mini (`greg@100.88.4.114`)
- `graphify` installed on Mac Mini (`pip3.11 install graphifyy`)
- Claude Code + Meridian pipeline on Mac Mini for `--update` runs
