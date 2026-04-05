---
type: workflow
title: Data Discrepancy Checker
tags: [workflow, data-quality, airtable, quickbooks]
created: 2026-03-26
updated: 2026-03-26
status: planned
priority: medium
phase: 1
agent: Data & Airtable Agent
trigger: schedule
---

# Data Discrepancy Checker

> Compares QuickBooks and Airtable records to find mismatches before they become reconciliation nightmares.

## Trigger

**Schedule**: Every Wednesday at 10am EST

## Steps

1. Pull all invoices + payments from QuickBooks (past 30 days)
2. Pull corresponding records from Airtable
3. Compare on: invoice amounts, payment status, due dates, client names (fuzzy match)
4. Flag all mismatches
5. Generate discrepancy report
6. Send to Michael + Emil for review

## Discrepancy Types

| Type | Example | Severity |
|------|---------|----------|
| Amount mismatch | QB: $1,200 / Airtable: $1,000 | High |
| Status mismatch | QB: Paid / Airtable: Outstanding | High |
| Missing record | Invoice in QB not in Airtable | Medium |
| Date mismatch | Due date differs by >3 days | Medium |
| Name variant | "Gary's Inc" vs "Garys" | Low |

## Output

```
Data Discrepancy Report — {date}

Found 4 discrepancies:

HIGH — Amount mismatch
  QB Invoice #1042 (Piermont): $4,200
  Airtable row #82: $4,000
  Difference: $200

MEDIUM — Missing in Airtable
  QB Invoice #1051 (Gary's): $1,800 — not found in Airtable

Action required: review and correct before month-end close.
```

## Prerequisites

- [ ] QuickBooks API credentials
- [ ] Airtable base IDs per client configured

## Related

- [[../agents/data-airtable|Data & Airtable Agent]]
