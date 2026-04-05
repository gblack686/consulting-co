---
type: workflow
title: Daily Cash Position
tags: [workflow, cash, quickbooks, finance]
created: 2026-03-26
updated: 2026-03-26
status: planned
priority: high
phase: 1
agent: Data & Airtable Agent
trigger: schedule
---

# Daily Cash Position

> Morning cash position summary per client. Feeds into Finn's 8am morning brief.

## Trigger

**Schedule**: Weekdays at 7:45am EST

## Steps

1. For each active client:
   - Pull bank account balances from QuickBooks
   - Pull total outstanding AR (unpaid invoices)
   - Pull total outstanding AP (unpaid bills)
2. Calculate net cash position
3. Flag if balance < threshold (configurable per client)
4. Format and send to [[../agents/finn|Finn]] for inclusion in morning brief

## Output

```
Cash Position — {date}

Piermont Brands:
  Bank: $42,300
  AR Outstanding: $18,500
  AP Outstanding: $9,200
  Net: $51,600

Gary's:
  Bank: $12,100
  AR Outstanding: $4,400
  AP Outstanding: $6,800
  Net: $9,700 (below $10k threshold)
```

## Prerequisites

- [ ] QuickBooks API credentials
- [ ] Per-client balance thresholds configured in Airtable

## Related

- [[../agents/finn|Finn (Morning Brief)]]
- [[../agents/data-airtable|Data & Airtable Agent]]
