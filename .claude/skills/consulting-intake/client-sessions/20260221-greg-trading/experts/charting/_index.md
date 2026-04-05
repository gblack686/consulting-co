---
type: expert
name: "charting"
domain: [charting, visualization, trading-charts, technical-analysis]
specialty: "On-demand candlestick chart generation with indicator overlays and equity curve visualization"
status: active
created: 2026-02-21
updated: 2026-02-21
tags: [expert, domain-expertise, charting, openclaw, trading, visualization]
---

# Charting Expert

## Domain Overview

The Charting domain generates visual analysis on demand. Greg does not want charts generated automatically on a schedule — he wants a button. Sebastian generates charts when Greg asks, when a trade proposal is attached to a signal, or when a backtest equity curve needs visualization. Fast, clean, and always delivered via Telegram.

## Expert Type

**Domain Expert** — On-demand chart generation and technical visualization for Hyper Liquid markets, specific to Greg's preferred indicators and visual style.

## Core Insight

> Charts are decisions aids, not decorations. Every chart should surface one clear signal: whether to act, wait, or pass. Lead with the interpretation, not just the image.

## Key Capabilities

- Generate candlestick charts for any Hyper Liquid ticker and timeframe on demand
- Apply technical indicators: EMA, MA, RSI, MACD, volume
- Render equity curve charts with drawdown overlay from backtest data
- User-invocable via `/generate-chart {ticker} {timeframe}`
- Deliver chart images via Telegram instantly

## Expert Files

| File | Purpose |
|------|---------|
| expertise | Complete charting workflow mental model |
| question | Query chart config or available indicators |
| plan | Plan new chart types or custom indicator overlays |
| plan_build_improve | Full ACT-LEARN-REUSE cycle |
| self-improve | Update expertise after runs |
| generate-chart | Generate and deliver a price chart on demand |
| generate-equity-curve | Render equity curve from backtest data |

## OpenClaw Skills (deployed)

| Skill | Trigger | Delivery |
|-------|---------|----------|
| generate-chart | On-demand (user `/generate-chart` or agent) | Telegram image |
| generate-equity-curve | On-demand (called by back-tester) | Telegram image |

## Tools & APIs

| Tool | API | Auth | Status |
|------|-----|------|--------|
| Hyper Liquid | REST POST /info (candleSnapshot) | API key | Pending key |
| mplfinance / charting lib | Python library | N/A | Install on server |
| Telegram | Bot API (sendPhoto) | Bot token | Pending key |

## Related

- [[discord-scraping/_index]] — volume spike alerts can trigger chart requests
- [[portfolio-manager/_index]] — position analysis may request charts
- [[back-tester/_index]] — equity curves generated after backtests

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-21 | Initial expert system from consulting intake |
