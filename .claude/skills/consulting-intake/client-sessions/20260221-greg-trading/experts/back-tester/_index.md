---
type: expert
name: "back-tester"
domain: [back-tester, quantitative-analysis, strategy, backtesting, optimization]
specialty: "Strategy backtesting, parameter optimization, dataset scouting, and quantitative analysis on Hyper Liquid"
status: active
created: 2026-02-21
updated: 2026-02-21
tags: [expert, domain-expertise, back-tester, openclaw, trading, quant]
---

# Back Tester / Quantitative Analyst Expert

## Domain Overview

The Back Tester domain is Greg's strategy validation engine. It runs overnight backtests on historical Hyper Liquid data, optimizes strategy parameters with overfitting protection, scouts for new datasets that could provide trading edge, and maintains a library of validated strategies. This domain works primarily at night and on-demand, providing the quantitative backbone for live trading decisions.

## Expert Type

**Domain Expert** — Strategy backtesting and quantitative analysis on Hyper Liquid perpetuals, specific to Greg's strategy library and risk parameters.

## Core Insight

> A strategy is not a strategy until it's been tested on out-of-sample data. In-sample performance is a lie. Always validate on holdout data before touching live capital.

## Key Capabilities

- Fetch historical OHLCV data from Hyper Liquid
- Execute strategy backtests with realistic fee simulation (0.045% taker)
- Calculate comprehensive metrics: Sharpe, max drawdown, profit factor, win rate
- Run parameter optimization sweeps with out-of-sample validation
- Detect overfitting: flag configs with > 30% in-sample/OOS performance degradation
- Scout overnight for new alternative data sources (on-chain, sentiment, options flow)
- Maintain strategy performance library in memory

## Expert Files

| File | Purpose |
|------|---------|
| expertise | Complete backtesting workflow mental model |
| question | Query strategy results or dataset library |
| plan | Plan new backtest campaigns or strategy ideas |
| plan_build_improve | Full ACT-LEARN-REUSE cycle |
| self-improve | Update expertise after runs |
| run-backtest | Execute a specific backtest |
| optimize-strategy | Run parameter sweep for a strategy |
| scout-datasets | Research new data sources overnight |

## OpenClaw Skills (deployed)

| Skill | Trigger | Delivery |
|-------|---------|----------|
| run-backtest | Cron 2:00 AM PST + on-demand | Telegram announce |
| optimize-strategy | On-demand | Telegram announce |
| scout-datasets | Cron Sunday 10 PM PST | Telegram announce (weekly) |

## Tools & APIs

| Tool | API | Auth | Status |
|------|-----|------|--------|
| Hyper Liquid Historical | REST POST /info | API key | Pending key |
| GitHub | REST API | PAT | Pending key |
| WebSearch | OpenClaw built-in | N/A | Available |

## Related

- [[portfolio-manager/_index]] — backtested strategies inform live position management
- [[charting/_index]] — equity curves generated after backtests
- [[discord-scraping/_index]] — overnight research feeds into strategy ideas

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-21 | Initial expert system from consulting intake |
