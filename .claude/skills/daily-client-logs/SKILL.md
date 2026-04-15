---
name: daily-client-logs
description: "Diff files across all client workspace roots, detect added/modified/deleted files since last scan, and append a dated activity log to each client's second brain vault (obsidian/daily/YYYY-MM-DD.md)."
triggers:
  - daily client log
  - client diff
  - second brain sync
  - workspace diff
model: haiku
---

# daily-client-logs

Scans every configured client workspace, compares the current file tree against
the last snapshot, and writes a dated markdown note into that client's second
brain. Each client can have **multiple workspace roots** (consulting-intake
session folder, gbauto client repo, Obsidian vault, etc.) — the skill walks all
of them and produces a single unified log.

## What it does

1. Loads `config/clients.json` — the registry of clients and their workspace roots
2. For each client:
   - Walks every workspace root (honors `ignore` globs)
   - Computes `(path, size, mtime, sha1)` for every file
   - Loads last snapshot from `state/{client}.json`
   - Diffs against current state → `added`, `modified`, `deleted`, `unchanged`
   - Writes `obsidian/daily/YYYY-MM-DD.md` to the client's `second_brain` path
   - Saves new snapshot to `state/{client}.json`
3. Prints a summary table per client

## Client registry (`config/clients.json`)

```json
{
  "fisch-group": {
    "display_name": "Fish Group",
    "workspaces": [
      "C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills/consulting-intake/client-sessions/20260305-michael-fisch",
      "C:/Users/gblac/OneDrive/Desktop/gbauto/fisch-group"
    ],
    "second_brain": "C:/Users/gblac/OneDrive/Desktop/gbauto/fisch-group/second-brain/obsidian",
    "ignore": [".git", "__pycache__", "node_modules", "*.pyc", "*.log", ".obsidian/workspace.json", "state/*"]
  }
}
```

Add new clients by adding a new top-level key. The skill picks them up on the
next run — no code changes.

## Daily log format

Written to `{second_brain}/daily/YYYY-MM-DD.md`:

```markdown
---
type: daily
title: Fish Group — 2026-04-09
date: 2026-04-09
tags: [daily, fisch-group, auto]
generated_by: daily-client-logs
---

# Fish Group — 2026-04-09

**Workspaces scanned:** 2
**Files tracked:** 77
**Changes since last scan:** 3 added · 5 modified · 0 deleted

## Added (3)
- `second-brain/workspace/MEMORY.md` (4.2 KB)
- `second-brain/sessions/2026-03-05/workflow-catalog.md` (18 KB)
- ...

## Modified (5)
- `second-brain/obsidian/tasks/blockers.md` — was 412 B, now 589 B
- ...

## Deleted (0)
_none_

## Unchanged
67 files unchanged since last scan.
```

If nothing changed, a minimal note is still written (so the daily/ log is
continuous).

## Usage

```bash
# Run all clients
python scripts/daily_client_logs.py

# Single client
python scripts/daily_client_logs.py --client fisch-group

# Dry run (no writes)
python scripts/daily_client_logs.py --dry-run

# Show current registry
python scripts/daily_client_logs.py --list
```

## Dependencies

Stdlib only — no third-party packages. Safe to run on any Python 3.9+.

## State

- `state/{client}.json` — last file snapshot per client
- Keyed by absolute path → `{size, mtime, sha1}`

## Scheduling

Intended to run once daily (e.g. 8am local) via Windows Task Scheduler:

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\daily-client-logs\scripts\daily_client_logs.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "GBAutomation-Daily-Client-Logs" -Action $action -Trigger $trigger
```

Or add to an existing cron/just recipe.

## Extending

- **More clients**: edit `config/clients.json`
- **More workspace roots per client**: add to the `workspaces` list
- **Custom ignores**: extend the `ignore` list (fnmatch globs on relative path)
- **Non-obsidian second brains**: the `second_brain` path can be any folder —
  the skill just writes `daily/YYYY-MM-DD.md` inside it
