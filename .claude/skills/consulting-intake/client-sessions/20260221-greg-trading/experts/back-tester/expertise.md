---
type: expert-file
parent: "[[back-tester/_index]]"
file-type: expertise
human_reviewed: false
tags: [expert-file, mental-model, back-tester, trading, quant]
last_updated: 2026-02-21
---

# Back Tester / Quant Expert - Complete Mental Model

## Part 1: Domain Architecture

### Overview
The Back Tester domain validates every strategy before live capital is deployed. It fetches historical Hyper Liquid data, runs strategy backtests with realistic fee simulation, optimizes parameters with out-of-sample validation, and scouts nightly for new data sources. This is the quantitative foundation for Greg's profitability goal — no strategy goes live without a backtest.

### Tool Connections
```
Hyper Liquid Historical API
    ↓ OHLCV candles
Data Cache (parquet files)
    ↓
Strategy Code (~/.openclaw/strategies/{name}/)
    ↓
Backtest Engine
    ↓
Metrics Calculator
    ↓
Results Memory (backtests/{name}-{date}.json)
    ↓
Telegram → Greg (summary)
    ↓ (equity curve data)
Charting Agent → generate-equity-curve

Optimization Engine (parameter sweep)
    ↓ top 3 configs
Telegram → Greg

WebSearch + YouTube
    ↓
Dataset Scout
    ↓
memory/dataset-scout/{YYYY-WW}.md
    ↓
Telegram → Greg (weekly)
```

### Key File Locations
| File | Purpose |
|------|---------|
| `memory/backtests/{strategy}-{date}.json` | Backtest result records |
| `memory/dataset-scout/{YYYY-WW}.md` | Weekly dataset scouting reports |
| `~/.openclaw/data/market-history/{asset}-{tf}.parquet` | Historical OHLCV cache |
| `~/.openclaw/strategies/{name}/` | Strategy Python files |

### Data Flows
- Hyper Liquid API → raw OHLCV → parquet cache → strategy engine → metrics → memory → Telegram

---

## Part 2: Primary Workflow — Run Backtest (Nightly + On-Demand)

### Trigger
- Type: cron (nightly) + on-demand
- Schedule: `0 2 * * *` America/Los_Angeles (nightly)
- Timezone: America/Los_Angeles

### Steps
1. Receive strategy spec: name, params, asset, timeframe, date range
2. Check cache: `~/.openclaw/data/market-history/{asset}-{timeframe}.parquet`
   - If cache is fresh (< 24h): use cached data
   - Else: fetch from Hyper Liquid historical API
3. Fetch data: `POST https://api.hyperliquid.xyz/info` with `{"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1h", "startTime": {ts}, "endTime": {ts}}}`
4. Run strategy Python code against OHLCV data
5. Simulate trades: entry/exit signals → position tracking → P&L
6. Apply fees: 0.045% taker × 2 (entry + exit) = 0.09% round-trip minimum
7. Calculate metrics (see table below)
8. Write results to `memory/backtests/{name}-{date}.json`
9. Send Telegram summary
10. Trigger generate-equity-curve with equity_curve data

### Performance Metric Calculations

| Metric | Formula | Good Threshold |
|--------|---------|----------------|
| Total Return | (final_equity / initial_equity) - 1 | > 10% per period |
| Sharpe Ratio | mean_return / std_return × sqrt(periods/year) | > 1.0 |
| Max Drawdown | max((peak - trough) / peak) | < 20% |
| Win Rate | winning_trades / total_trades | > 50% (trend) / > 35% (mean-rev) |
| Profit Factor | gross_profit / gross_loss | > 1.5 |
| Avg Trade | total_pnl / trade_count | > fee × 5 (must beat friction) |

### Verdict Thresholds
| Verdict | Condition |
|---------|-----------|
| PROMISING | Sharpe > 1.0 AND MaxDD < 20% AND Win Rate > 40% |
| NEEDS_WORK | Sharpe 0.5–1.0 OR MaxDD 20–35% |
| AVOID | Sharpe < 0.5 OR MaxDD > 35% OR avg_trade < fees |

### API Endpoints Used
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.hyperliquid.xyz/info` | POST | Historical OHLCV candles |

### Expected Inputs
- Strategy name, parameters, asset (e.g., BTC-PERP), timeframe, date range

### Expected Outputs
- Backtest JSON with full trade log + metrics
- Telegram summary with verdict
- Equity curve data passed to charting agent

### Approval Gates
None — fully autonomous analysis.

---

## Part 3: Secondary Workflows

### Optimize Strategy

**Trigger**: On-demand
**Steps**:
1. Define parameter grid (e.g., MA periods, RSI levels)
2. Split data: 70% in-sample, 30% out-of-sample holdout
3. Run backtest for each parameter combination (cap at 500 combinations)
4. Rank by Sharpe ratio on in-sample data → select top 10
5. Run top 10 on out-of-sample data
6. Flag overfitting: OOS Sharpe / in-sample Sharpe < 0.7 = overfit
7. Report top 3 generalized configurations

**[APPROVAL GATE]**: Greg selects configuration before it goes live

### Dataset Scout (Nightly)

**Trigger**: Cron Sunday 10 PM PST (weekly report)
**Steps**:
1. WebSearch for new data sources (on-chain, sentiment, options flow, alternative data)
2. Evaluate: quality, freshness, cost, API availability, trading relevance
3. Compile top 3 finds per week
4. Write to `memory/dataset-scout/{YYYY-WW}.md`
5. Send weekly summary via Telegram

**Output**: Weekly dataset opportunity report

### Edge Cases
- Insufficient historical data (< 100 candles): note limitation, proceed with available data, flag in report
- Strategy has no trades in backtest period: report "Strategy generated 0 trades — check logic/parameters"
- Backtest runtime > 60 seconds: log progress at 30s intervals; don't time out silently

---

## Part 4: Tool Configuration

| Tool | Base URL | Auth Header | Key Endpoints |
|------|----------|-------------|---------------|
| Hyper Liquid | `https://api.hyperliquid.xyz` | None (public) | `/info` (POST, type: candleSnapshot) |
| Hyper Liquid (testnet) | `https://api.hyperliquid-testnet.xyz` | None | `/info` (POST) |

### Hyper Liquid candleSnapshot Request Format
```json
{
  "type": "candleSnapshot",
  "req": {
    "coin": "BTC",
    "interval": "1h",
    "startTime": 1700000000000,
    "endTime": 1700100000000
  }
}
```

### Available Timeframes
`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`

### Python Strategy Interface
Strategies are Python files in `~/.openclaw/strategies/{name}/strategy.py`:
```python
def generate_signals(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Returns df with added 'signal' column: 1=long, -1=short, 0=flat"""
    pass
```

---

## Part 5: Scheduling & Automation

### Cron Jobs

| Name | Schedule | Skill | Mode | Delivery |
|------|----------|-------|------|----------|
| Nightly Backtest | `0 2 * * *` PST | run-backtest | isolated | announce |
| Dataset Scout | `0 22 * * 0` PST | scout-datasets | isolated | announce |

### Heartbeat Tasks
- Check if a backtest job is queued and idle → start it (every 30m general heartbeat)

### Trigger Patterns
- Primary: time-driven (nightly)
- On-demand: Greg requests via chat ("backtest the RSI strategy on BTC 1h")

---

## Part 6: Integration Points

### Cross-Domain Connections
- **→ Charting**: Equity curve data passed after every backtest for visualization
- **← Portfolio Manager**: Closed trade data informs which strategies to backtest/optimize
- **← Discord & Scraping**: YouTube/news insights trigger new strategy hypothesis testing

### Shared Tools or Data Sources
- Hyper Liquid API: shared with Portfolio Manager (live data) and Charting (price data)

### Workflow Handoffs
1. Backtest completes → equity_curve JSON passed to charting agent → equity curve delivered to Greg
2. Strategy validates well in backtest → Greg decides to paper trade → Portfolio Manager monitors

---

## Part 7: Patterns & Learnings

### Patterns That Work
- (Populated after first self-improve cycle)

### Patterns To Avoid
- (Populated after first self-improve cycle)

### Known Issues
- Hyper Liquid historical data may have gaps at market launch (pre-2024) — handle gracefully
- Fee simulation: 0.045% is taker fee; maker orders are cheaper — note in reports

### Tips
- Always validate strategy on out-of-sample before showing Greg "good" results
- Strategies with win rate < 40% aren't necessarily bad — check profit factor and R/R
- Cache OHLCV data to disk — refetching the same data repeatedly wastes quota
- Paper trading should be the mandatory step between "PROMISING" backtest and live capital
