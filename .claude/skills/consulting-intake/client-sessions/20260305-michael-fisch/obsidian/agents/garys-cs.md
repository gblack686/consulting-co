---
type: agent
title: Gary's CS Agent
tags: [agent, customer-service, garys, voice-ai]
created: 2026-03-26
updated: 2026-03-26
role: Customer Service Automation
phase: 2
status: planned
---

# Gary's CS Agent

> Phase 2 agent. Replaces Gary's 5-person Philippines customer service team (~$90k/year) with AI-powered email triage and eventually voice AI.

## Status: Phase 2 — Not Yet Building

Waiting for Phase 1 (Fish Group internals) to stabilize first.

## Savings Potential

| Scenario | Annual Savings |
|----------|----------------|
| Full CS replacement (5 reps) | ~$90k/year |
| Keep 1 human oversight + AI handles 80% | ~$72k/year |
| Estimated realistic savings | **~$80k/year** |

## Phase 1 — Email Triage

- Inbound email classification: returns / order status / general inquiry / escalate
- Auto-draft responses for common queries (requires human approval to send)
- Escalation routing for edge cases

## Phase 2 — Voice AI

| Tool | Role |
|------|------|
| **Twilio** | Phone number, call routing, SMS |
| **ElevenLabs** | Voice synthesis |
| **Gary's POS** | Order lookup, return processing (TBD) |

## Open Questions

- [ ] What POS system does Gary's use?
- [ ] Are emails handled in Gmail or a helpdesk tool?
- [ ] What % of CS volume is returns vs. order status vs. other?
- [ ] Is there an existing KB / FAQ we can train on?

## Related

- [[../contacts/clients/garys|Gary's Client Page]]
- [[finn|Finn (Orchestrator)]]
