# Greg Trading — Workflow Catalog
**Client:** Greg | **Domain:** Algorithmic Trading / Crypto (Hyper Liquid)
**Generated:** 2026-03-18 | **Total Workflows:** 18

---

> **⚠️ Critical Rule:** The agent NEVER executes live trades. All trade proposals require Greg's explicit manual approval. Every workflow with trade-related output is notification/proposal only.

---

## Priority Matrix

| ID | Workflow | Complexity | Impact | Score | Phase |
|----|----------|-----------|--------|-------|-------|
| WF-001 | Morning Brief | Low | High | 10 | 1 |
| WF-003 | Position Monitor & Stop-Loss Guard | Low | High | 10 | 1 |
| WF-002 | Discord Signal Scraper | Low | High | 9 | 1 |
| WF-004 | Trade Journal & Performance Tracker | Low | High | 9 | 2 |
| WF-005 | Run Backtest | Medium | High | 9 | 3 |
| WF-018 | OpenClaw Setup & Health Check | Low | Medium | 9 | 1 |
| WF-006 | Strategy Optimizer | Medium | High | 8 | 3 |
| WF-007 | Generate Chart | Low | Medium | 8 | 2 |
| WF-009 | Paper Trading System | Medium | High | 8 | 3 |
| WF-011 | Risk Management Report | Medium | High | 8 | 4 |
| WF-015 | Weekly Performance Review | Low | High | 8 | 4 |
| WF-017 | Trade Proposal Builder | High | High | 8 | 4 |
| WF-008 | YouTube Trading Intelligence Scraper | Low | Medium | 7 | 2 |
| WF-010 | Volume Spike & Indicator Alert | Low | Medium | 7 | 2 |
| WF-013 | Signal Quality Scorer | Medium | High | 7 | 4 |
| WF-014 | Equity Curve Generator | Low | Medium | 7 | 3 |
| WF-016 | Strategy Live-Ready Validator | Medium | High | 7 | 4 |
| WF-012 | Dataset Scout | Low | Medium | 6 | 3 |

---

## Build Phases

### Phase 1 — Foundation: Eyes Open (Sessions 1–2)
> Get the agent observing. No trade execution. Greg gets daily intel with zero manual work.

- **WF-001** Morning Brief
- **WF-002** Discord Signal Scraper
- **WF-003** Position Monitor & Stop-Loss Guard
- **WF-018** OpenClaw Setup & Health Check

### Phase 2 — Memory: Learn From Every Trade (Sessions 3–4)
> Agent starts logging and learning. Trade journal builds the data foundation for everything downstream.

- **WF-004** Trade Journal & Performance Tracker
- **WF-007** Generate Chart
- **WF-008** YouTube Trading Intelligence Scraper
- **WF-010** Volume Spike & Indicator Alert

### Phase 3 — Edge: Backtesting & Validation (Sessions 5–6)
> Quant agent comes online. Strategies get tested, optimized, and validated before any live capital.

- **WF-005** Run Backtest
- **WF-006** Strategy Optimizer
- **WF-009** Paper Trading System
- **WF-014** Equity Curve Generator

### Phase 4 — Intelligence: Synthesis & Proposals (Sessions 7+)
> Agent synthesizes signals, scores sources, validates strategies, and generates trade proposals. Greg still pulls the trigger but the agent does all the pre-work.

- **WF-011** Risk Management Report
- **WF-012** Dataset Scout
- **WF-013** Signal Quality Scorer
- **WF-015** Weekly Performance Review
- **WF-016** Strategy Live-Ready Validator
- **WF-017** Trade Proposal Builder

---

## Workflow Details

### WF-001 — Morning Brief
**Agent:** main (Sebastian) | **Trigger:** Daily 7am PST | **APIs:** Hyper Liquid, Discord, YouTube, Telegram

Every morning: pull overnight Discord signals, Hyper Liquid portfolio snapshot, market volume metrics, YouTube insights from last 24h, and news digest. Send consolidated daily letter to Greg via Telegram.

**Estimated:** 2.5h | **Prerequisites:** hyperliquid_api_key, discord_bot_token, telegram_bot_token, youtube_api_key

---

### WF-002 — Discord Signal Scraper
**Agent:** discord-scraping (Signal Scout) | **Trigger:** Every 15 minutes | **APIs:** Discord, Telegram

Every 15 minutes: fetch new messages from monitored trade-signal channels, parse for structured signals (ticker, direction, entry, TP, SL), filter noise, log to daily file. High-quality signals (score >0.7) fire an immediate Telegram alert.

**Human gates:** Greg specifies which channels to monitor
**Estimated:** 3h | **Prerequisites:** discord_bot_token, monitored_channel_list

---

### WF-003 — Position Monitor & Stop-Loss Guard
**Agent:** portfolio-manager (Risk Guard) | **Trigger:** Every 15 minutes | **APIs:** Hyper Liquid, Telegram

Every 15 minutes: fetch all open positions, verify each has a stop-loss, calculate drawdown vs threshold, log portfolio snapshot. **Immediate Telegram alert** if any position is missing a stop-loss or portfolio drawdown exceeds threshold.

**Human gates:** Greg manually executes any action — agent never trades
**Estimated:** 2h | **Prerequisites:** hyperliquid_api_key, telegram_bot_token, drawdown_threshold_defined

---

### WF-004 — Trade Journal & Performance Tracker
**Agent:** portfolio-manager (Risk Guard) | **Trigger:** On position close | **APIs:** Hyper Liquid

On every position close: log entry, exit, P&L, duration, SL used, TP used, outcome (target_hit / stopped_out / manual_close). Update running win rate and avg P&L. Weekly: performance summary with pattern analysis.

**Human gates:** Greg reviews weekly summary and adds context
**Estimated:** 2h | **Prerequisites:** hyperliquid_api_key

---

### WF-005 — Run Backtest
**Agent:** back-tester (Quant) | **Trigger:** On-demand + nightly | **APIs:** Hyper Liquid

Execute a backtest for a named strategy: fetch OHLCV data, apply rules, calculate metrics (total return, Sharpe, max drawdown, win rate, avg P&L). Report top 5 metrics + strengths/weaknesses.

**Human gates:** Greg provides strategy spec; reviews results
**Estimated:** 4h | **Prerequisites:** hyperliquid_api_key, strategy_code_in_github

---

### WF-006 — Strategy Optimizer
**Agent:** back-tester (Quant) | **Trigger:** On-demand | **APIs:** Hyper Liquid

Run parameter sweeps (grid or Bayesian) to find optimal strategy settings. Validate top 3 configs on holdout period for overfitting. Report: best params, in-sample vs out-of-sample performance, overfitting risk flag.

**Human gates:** Greg defines ranges; selects config to deploy
**Estimated:** 4.5h | **Prerequisites:** WF-005

---

### WF-007 — Generate Chart
**Agent:** charting (Chart Maker) | **Trigger:** On-demand | **APIs:** Hyper Liquid, Telegram
**User-invocable: yes**

On demand: fetch OHLCV data, render chart with requested indicators (MA, RSI, MACD, volume, etc.) as PNG, deliver via Telegram. Not automatically generated — Greg requests it.

**Estimated:** 2h | **Prerequisites:** hyperliquid_api_key, telegram_bot_token

---

### WF-008 — YouTube Trading Intelligence Scraper
**Agent:** discord-scraping (Signal Scout) | **Trigger:** Daily overnight | **APIs:** YouTube

Query tracked trading channels for new videos. Download transcripts. Summarize key insights. Top 2-3 insights included in morning brief.

**Human gates:** Greg specifies tracked channel list
**Estimated:** 2.5h | **Prerequisites:** youtube_api_key, tracked_channel_list

---

### WF-009 — Paper Trading System
**Agent:** portfolio-manager (Risk Guard) | **Trigger:** Event | **APIs:** Hyper Liquid

Simulate trades using real-time data without capital at risk. Track paper P&L vs live performance. Use to validate new strategies before going live.

**Human gates:** Greg approves which strategies run in paper mode; makes go-live decision
**Estimated:** 5h | **Prerequisites:** hyperliquid_api_key, WF-004

---

### WF-010 — Volume Spike & Indicator Alert
**Agent:** discord-scraping (Signal Scout) | **Trigger:** Every 15 minutes | **APIs:** Hyper Liquid, Telegram

Poll tickers for volume anomalies and indicator threshold crossings (RSI, MACD, etc.). On trigger: Telegram alert with context. Queue chart generation if significant.

**Human gates:** Greg defines watched tickers and alert thresholds
**Estimated:** 2.5h | **Prerequisites:** hyperliquid_api_key, telegram_bot_token, alert_conditions_defined

---

### WF-011 — Risk Management Report
**Agent:** portfolio-manager (Risk Guard) | **Trigger:** On-demand + weekly | **APIs:** Hyper Liquid, Telegram

Analyze all open positions: risk/reward ratios, SL recommendations, TP adjustments, correlation risk, portfolio max drawdown scenario. Delivered as Telegram message.

**Human gates:** Greg manually executes all recommendations
**Estimated:** 3h | **Prerequisites:** hyperliquid_api_key, drawdown_threshold_defined

---

### WF-012 — Dataset Scout
**Agent:** back-tester (Quant) | **Trigger:** Nightly

Search for new data sources (on-chain data, social sentiment, options flow, funding rates, whale wallets, etc.). Flag 1-3 promising sources per week in morning brief.

**Human gates:** Greg decides whether to integrate a flagged dataset
**Estimated:** 2h | **Prerequisites:** none

---

### WF-013 — Signal Quality Scorer
**Agent:** discord-scraping (Signal Scout) | **Trigger:** Event | **APIs:** Discord

After trade data accumulates: score incoming Discord signals against historical source quality. Weight signals from higher-win-rate sources. Flag consistently underperforming sources for removal.

**Human gates:** Greg approves removal of underperforming sources
**Estimated:** 4h | **Prerequisites:** WF-002, WF-004 (min 20 historical signals)

---

### WF-014 — Equity Curve Generator
**Agent:** charting (Chart Maker) | **Trigger:** Post-backtest | **APIs:** Telegram

Called automatically after every backtest: render equity curve with drawdown overlay. Send via Telegram. Attach to backtest report in memory.

**Estimated:** 1.5h | **Prerequisites:** WF-005, telegram_bot_token

---

### WF-015 — Weekly Performance Review
**Agent:** portfolio-manager (Risk Guard) | **Trigger:** Weekly Sunday | **APIs:** Telegram

Compile weekly trading performance: total P&L, win rate, best/worst trade, avg hold time, drawdown vs account peak. Pattern analysis: recurring mistakes, what's working. Delivered via Telegram.

**Human gates:** Greg can add notes/context to the weekly log
**Estimated:** 2h | **Prerequisites:** WF-004

---

### WF-016 — Strategy Live-Ready Validator
**Agent:** back-tester (Quant) | **Trigger:** On-demand | **APIs:** Hyper Liquid

Before any new strategy goes live: run full checklist — backtest (>30 trades, Sharpe >1.0), paper trading (>20 trades), drawdown within tolerance, SL logic present, position sizing defined. Generate go/no-go report.

**Human gates:** Greg reviews report and makes final go-live decision
**Estimated:** 3h | **Prerequisites:** WF-005, WF-009

---

### WF-017 — Trade Proposal Builder
**Agent:** main (Sebastian) | **Trigger:** Event | **APIs:** Hyper Liquid, Discord, Telegram

When high-confidence setup detected (Discord signal + indicator alignment): generate structured proposal — ticker, direction, entry zone, TP, SL, R:R ratio, supporting signals, recommended position size (% of account). Sent via Telegram card. Minimum 2:1 R:R required to fire.

**Human gates:** Greg approves or skips every proposal — agent NEVER executes
**Estimated:** 6h | **Prerequisites:** WF-002, WF-010, WF-003

---

### WF-018 — OpenClaw Setup & Health Check
**Agent:** main (Sebastian) | **Trigger:** On-demand + weekly | **APIs:** All
**User-invocable: yes**

Verify all API connections, agent heartbeats, secrets loaded, signal pipeline end-to-end. Run on first deploy and weekly thereafter. Delivers health report via Telegram.

**Estimated:** 1.5h | **Prerequisites:** all API keys configured

---

## Prerequisites Checklist

### Critical (must have before Phase 1)
- [ ] `hyperliquid_api_key`
- [ ] `telegram_bot_token`
- [ ] `discord_bot_token`

### Important (needed by Phase 2)
- [ ] `youtube_api_key`
- [ ] `openrouter_api_key`
- [ ] Monitored Discord channel list from Greg
- [ ] Drawdown threshold defined (e.g. 10%)

### Nice to Have
- [ ] Tracked YouTube channel list
- [ ] Charting library selected (mplfinance, lightweight-charts, etc.)
- [ ] Alert conditions defined (RSI levels, volume spike %)
