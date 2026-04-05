---
type: expert
name: "portfolio-manager"
domain: [portfolio-manager, trading, risk, hyperliquid, positions]
specialty: "Hyper Liquid position monitoring, risk management, stop-loss enforcement, and trade journaling"
status: active
created: 2026-02-21
updated: 2026-02-21
tags: [expert, domain-expertise, portfolio-manager, openclaw, trading]
---

# Portfolio Manager Expert

## Domain Overview

The Portfolio Manager domain is Greg's risk guardian. It watches all open Hyper Liquid positions every 15 minutes, enforces the rule that every position must have a stop-loss, monitors drawdown thresholds, generates risk-adjusted TP/SL recommendations, and logs every trade to a journal for performance learning. It NEVER executes trades — all recommendations require Greg's manual execution.

## Expert Type

**Domain Expert** — Hyper Liquid portfolio risk management, position monitoring, and trade performance analytics specific to Greg's account and risk tolerance.

## Core Insight

> The only unforgivable portfolio management error is a position without a stop-loss. Every other mistake is recoverable. Build the stop-loss guardian first and make it loud.

## Key Capabilities

- Monitor all open positions every 15 minutes
- Fire immediate alerts for positions missing stop-losses
- Calculate and report portfolio drawdown in real-time
- Generate concrete stop-loss and TP adjustment recommendations (proposals only)
- Log all closed trades with full context
- Calculate running performance stats: win rate, P&L, profit factor
- Weekly trade journal summary with pattern analysis

## Expert Files

| File | Purpose |
|------|---------|
| expertise | Complete portfolio management workflow mental model |
| question | Query position status or trade history |
| plan | Plan new risk rules or monitoring logic |
| plan_build_improve | Full ACT-LEARN-REUSE cycle |
| self-improve | Update expertise after runs |
| monitor-positions | Run or debug the position monitor |
| manage-risk | Execute a full risk analysis session |
| trade-journal | Query or update trade logs |

## OpenClaw Skills (deployed)

| Skill | Trigger | Delivery |
|-------|---------|----------|
| monitor-positions | Heartbeat every 15m | Telegram (alerts only) |
| manage-risk | On-demand | Telegram announce |
| trade-journal | On position close + Monday 7 AM | Telegram announce (weekly) |

## Tools & APIs

| Tool | API | Auth | Status |
|------|-----|------|--------|
| Hyper Liquid | REST API + WebSocket | API key + secret | Pending key |
| Telegram | Bot API | Bot token | Pending key |

## Related

- [[discord-scraping/_index]] — Discord signals inform trade context
- [[back-tester/_index]] — backtests validate strategies used in live positions
- [[charting/_index]] — position analysis can trigger chart generation

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-21 | Initial expert system from consulting intake |
