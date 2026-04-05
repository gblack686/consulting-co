---
type: decision
date: 2026-03-05
tags: [decision, architecture]
decided_by: [Michael Fisch, Greg Black]
---

# Architecture Decisions — Session 1

## Pattern B: Multi-Agent by Domain

**Decision**: Use Pattern B (multi-agent by domain) instead of a single monolithic agent.
**Rationale**: Fish Group has 5 distinct operational domains (orchestration, client ops, data/finance, permissions, customer service). Each domain has different APIs, triggers, and guardrails. Separating them ensures client isolation and allows phased rollout.
**Alternatives considered**: Pattern A (single agent), Pattern C (per-client agents)
**Outcome**: Implemented — 5 agents defined in Session 1

## Autonomy Level 2: Draft & Propose

**Decision**: All agents operate at Level 2 — they draft and propose actions but never execute without human approval.
**Rationale**: Financial operations (AR follow-ups, cash positions, access provisioning) carry real risk. Michael and Emil need to review before any external action.
**Outcome**: All workflows include human-in-the-loop gates

## AWS: One Account Per Client

**Decision**: Provision a separate AWS sub-account for each Fish Group client.
**Rationale**: Clean billing separation, security isolation, easy offboarding (delete account).
**Outcome**: Strategy confirmed, not yet provisioned

## Model Tier: Medium

**Decision**: Use medium-tier models (gemini-2.0-flash brain + claude-3-5-haiku muscle)
**Rationale**: Balances cost (~$100-200/mo) with capability. Financial data processing doesn't need frontier reasoning.
**Outcome**: Configured in openclaw.json

## QuickBooks Integration Path

**Decision**: Try Intuit MCP first, fall back to Python SDK.
**Rationale**: MCP is lower friction. Emil has developer access for fallback.
**Decided**: Session 2 (2026-03-12)
**Outcome**: Not yet evaluated
