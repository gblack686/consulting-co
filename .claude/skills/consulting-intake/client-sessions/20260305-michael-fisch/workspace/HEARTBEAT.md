# Heartbeat — Finn 🐟

## Cron Schedule

```bash
# Morning ops brief — daily 8am EST (Mon-Fri only)
openclaw cron add "morning-brief" "0 8 * * 1-5"

# Weekly Airtable audit — Monday 9am EST
openclaw cron add "airtable-sync-check" "0 9 * * 1"

# Permissions audit — Friday 4pm EST (weekly)
openclaw cron add "access-audit" "0 16 * * 5"
```

## Morning Brief Format

```
=== Fish Group Ops Brief — {date} ===

NEW EMAILS (priority)
  • {N} unread — {summary of flagged items}

AIRTABLE ACTIVITY
  • Piermont: {N} new records, {N} pending shipments
  • {Other clients}: {summary}

WORKFLOW STATUS
  • {list of last 24h workflow runs — pass/fail}

TODAY'S SCHEDULE
  • {Google Calendar events for Michael}

ACTION ITEMS
  • {anything requiring approval or attention}
===
```

## Trigger Words (Claude Code commands)

- `/brief` — run morning brief on demand
- `/onboard {client}` — trigger client onboarding workflow
- `/shipment {client}` — trigger shipment request workflow
- `/audit` — run permissions audit
- `/status` — check all workflow run statuses
