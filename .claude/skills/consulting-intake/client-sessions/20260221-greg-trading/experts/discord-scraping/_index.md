---
type: expert
name: "discord-scraping"
domain: [discord-scraping, trading, signals, news, data-feeds]
specialty: "Discord trade signal monitoring, news aggregation, volume-spike alerts, and data pipeline management"
status: active
created: 2026-02-21
updated: 2026-02-21
tags: [expert, domain-expertise, discord-scraping, openclaw, trading]
---

# Discord & Scraping Expert

## Domain Overview

The Discord & Scraping domain is Greg's intelligence layer. It monitors Discord trade channels every 15 minutes for signals, scrapes YouTube daily for strategy content, watches data feeds for volume spikes and indicator triggers, and assembles the morning brief. This domain never executes trades — it's pure signal intelligence and delivery.

## Expert Type

**Domain Expert** — Trade signal intelligence and information pipeline management specific to Greg's Discord channels, data feeds, and Hyper Liquid market data.

## Core Insight

> Signal quality > signal quantity. A well-filtered Discord scrape with 2 high-quality signals is worth more than 50 noisy ones. Build filtering first; volume of alerts is a UX problem.

## Key Capabilities

- Monitor Discord channels every 15 minutes for structured trade signals
- Parse and score signal quality (entry + TP + SL = complete signal)
- Fire Telegram alerts for high-quality signals (score ≥ 7)
- Daily YouTube scrape for strategy insights and market content
- Volume spike detection and indicator-condition alerts
- Compose and deliver daily morning brief at 7 AM PST
- News aggregation from relevant crypto/trading sources

## Expert Files

| File | Purpose |
|------|---------|
| expertise | Complete Discord & Scraping workflow mental model |
| question | Query signal pipeline without changes |
| plan | Plan new scraping workflows or alert rules |
| plan_build_improve | Full ACT-LEARN-REUSE cycle |
| self-improve | Update expertise after runs |
| scrape-discord | Run or debug the Discord scraper |
| monitor-feeds | Manage volume spike + indicator alert rules |
| schedule-morning-brief | Configure or test the morning brief |

## OpenClaw Skills (deployed)

| Skill | Trigger | Delivery |
|-------|---------|----------|
| scrape-discord | Cron every 15m | Telegram (high-quality signals only) |
| morning-brief | Cron 7:00 AM PST daily | Telegram announce |
| monitor-feeds | Heartbeat every 15m | Telegram (alerts) |

## Tools & APIs

| Tool | API | Auth | Status |
|------|-----|------|--------|
| Discord | REST API v10 | Bot token | Pending key |
| Hyper Liquid | REST + WebSocket | API key + secret | Pending key |
| YouTube Data API v3 | REST | API key | Pending key |
| News source | WebSearch / TBD | N/A | TBD |

## Related

- [[portfolio-manager/_index]] — receives signals from this domain for trade proposal context
- [[back-tester/_index]] — uses overnight scrapes for strategy research
- [[charting/_index]] — volume spike alerts can trigger chart generation

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-21 | Initial expert system from consulting intake |
