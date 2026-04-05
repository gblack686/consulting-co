---
type: workflow
title: Weekly Client Digest
tags: [workflow, digest, reporting, clients]
created: 2026-03-26
updated: 2026-03-26
status: planned
priority: medium
phase: 1
agent: Finn
trigger: schedule
---

# Weekly Client Digest

> Every Friday, Finn compiles a one-page summary per client: financials, open items, upcoming deadlines.

## Trigger

**Schedule**: Every Friday at 3pm EST

## Steps

1. For each active client, pull:
   - Cash position (from daily-cash-position data)
   - Outstanding AR (QuickBooks)
   - Open Airtable tasks
   - Any discrepancies flagged (from data-discrepancy-checker)
   - Upcoming deadlines (tax dates, contract renewals)
2. Compile into structured digest per client
3. Send summary to Michael + Emil
4. Archive digest in Airtable
5. Save copy to `/daily/` in vault

## Output

```
Weekly Client Digest — Week of {date}

PIERMONT BRANDS
  Cash: $51,600 (up from last week)
  AR Outstanding: $18,500 (3 invoices)
  Open items: 2 discrepancies flagged
  Next deadline: Q1 close — April 5

GARY'S
  Cash: $9,700 (below threshold)
  AR Outstanding: $4,400
  ...
```

## Prerequisites

- [ ] daily-cash-position workflow running
- [ ] Michael + Emil emails confirmed
- [ ] Gmail OAuth token for Finn

## Related

- [[../agents/finn|Finn (Orchestrator)]]
