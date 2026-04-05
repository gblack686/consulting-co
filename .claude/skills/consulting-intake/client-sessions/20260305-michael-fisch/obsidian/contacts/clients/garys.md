---
type: client
title: Gary's
tags: [client, garys, retail, customer-service]
created: 2026-03-26
updated: 2026-03-26
status: phase-2
industry: Family Retail
primary_contact: TBD
---

# Gary's

> Family-owned retail business. Primary automation opportunity: replace Philippines CS team with AI agent.

## Overview

| Field | Detail |
|-------|--------|
| **Type** | Family retail |
| **CS Team** | 5 reps in Philippines (~$90k/year) |
| **Primary Ask** | AI customer service agent to handle email + eventually phone |

## Savings Potential

| Scenario | Annual Savings |
|----------|----------------|
| Full CS replacement (5 reps) | ~$90k/year |
| Keep 1 human oversight + AI handles 80% | ~$72k/year |
| Estimated realistic savings | **~$80k/year** |

## Phase 1 — Email Triage

- Inbound email classification (returns, order status, general inquiries)
- Auto-draft responses for common queries
- Escalation to human for edge cases

## Phase 2 — Voice AI

| Tool | Purpose |
|------|------|
| **Twilio** | Phone/SMS |
| **ElevenLabs** | Voice AI |
| **Gary's POS** | Order lookup (TBD — may be proprietary) |

## Agent Coverage

- [[agents/garys-cs|Gary's CS Agent]] — Phase 2 build (after Piermont internal is stable)

## Open Questions

- [ ] What POS system does Gary's use?
- [ ] Are emails handled in Gmail or a helpdesk tool?
- [ ] What % of CS volume is returns vs. order status vs. other?
- [ ] Is there an existing KB / FAQ we can train on?
