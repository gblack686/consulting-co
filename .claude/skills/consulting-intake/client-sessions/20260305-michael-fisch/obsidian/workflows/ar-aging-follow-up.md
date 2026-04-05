---
type: workflow
title: AR Aging Follow-Up
tags: [workflow, ar, quickbooks, finance]
created: 2026-03-26
updated: 2026-03-26
status: planned
priority: high
phase: 1
agent: Data & Airtable Agent
trigger: schedule
---

# AR Aging Follow-Up

> Auto-generate follow-up drafts for overdue AR balances pulled from QuickBooks.

## Trigger

**Schedule**: Every Monday + Thursday at 9am EST

## Steps

1. Pull AR aging report from QuickBooks API
2. Filter invoices: 30+ days overdue
3. For each overdue invoice:
   - Look up client contact in Airtable
   - Generate personalized follow-up email draft
4. Present drafts to Michael for approval (never auto-send)
5. Log action in Airtable

## APIs Used

| API | Action |
|-----|--------|
| QuickBooks | `GET /v3/company/{id}/query` — overdue invoices |
| Airtable | `GET` client contact info |
| Gmail | Draft creation |

## Human-in-Loop Gate

**Required before sending**: Michael must approve each draft before email is sent.

## Output

```
AR Follow-Up Drafts — {date}

3 invoices overdue:

1. Piermont Brands — $4,200 (45 days)
   Draft: [View draft]

2. ...

Approve all? [Y/N] or review individually.
```

## Prerequisites

- [ ] QuickBooks API credentials set in OpenClaw secrets
- [ ] Gmail OAuth token set in OpenClaw secrets
- [ ] Client contact Airtable base configured

## Related

- [[../agents/data-airtable|Data & Airtable Agent]]
