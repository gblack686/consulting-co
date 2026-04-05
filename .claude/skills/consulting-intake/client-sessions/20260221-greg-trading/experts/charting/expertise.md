---
type: expert-file
parent: "[[charting/_index]]"
file-type: expertise
human_reviewed: false
tags: [expert-file, mental-model, charting, trading, visualization]
last_updated: 2026-02-21
---

# Charting Expert - Complete Mental Model

## Part 1: Domain Architecture

### Overview
The Charting domain is Greg's visual analysis layer. Every chart is on-demand — Greg uses it like a button: ask for a chart, get a chart in Telegram within seconds. Charts are also triggered programmatically when the back-tester completes a backtest (equity curves) or when a volume spike alert fires. The domain is deliberately simple: fetch data, render chart, deliver via Telegram.

### Tool Connections
```
Greg's Telegram command: /generate-chart BTC-PERP 1h
    ↓
Hyper Liquid API (price data)
    ↓
Indicator Calculator (EMA, RSI, MACD, Volume)
    ↓
mplfinance Chart Renderer
    ↓ PNG image
Telegram Bot → Greg

Back Tester (equity_curve data)
    ↓
generate-equity-curve
    ↓ equity + drawdown chart PNG
Telegram Bot → Greg
```

### Key File Locations
| File | Purpose |
|------|---------|
| `~/.openclaw/workspace/charts/` | Generated chart PNGs |
| `memory/chart-requests.json` | Log of all chart requests |

### Data Flows
- Hyper Liquid → OHLCV candles → indicator calc → mplfinance render → Telegram delivery

---

## Part 2: Primary Workflow — Generate Chart (On-Demand)

### Trigger
- Type: on-demand (user-invocable)
- Command: `/generate-chart {ticker} {timeframe} [indicators=X,Y] [days=N]`
- Also triggered by: volume spike alerts (via monitor-feeds), trade proposals

### Steps
1. Parse command: extract ticker, timeframe, optional indicators, optional date range
   - Defaults: last 100 candles, indicators: 20 EMA + 50 EMA + volume
2. Fetch OHLCV from Hyper Liquid: `POST /info` with `candleSnapshot` for the ticker + timeframe
3. Calculate indicators:
   - EMA/MA: `ta.ema(close, period)`
   - RSI: `ta.rsi(close, 14)` by default
   - MACD: `ta.macd(close, 12, 26, 9)` by default
   - Volume: raw from OHLCV
4. Render chart using mplfinance:
   - Main panel: OHLCV candlesticks + EMA overlays
   - Sub-panel 1: Volume bars
   - Sub-panel 2 (if RSI requested): RSI with overbought/oversold lines at 70/30
   - Sub-panel 3 (if MACD requested): MACD histogram + signal line
5. Style: dark background (#1a1a2e), clean gridlines, minimal decoration
6. Save to `~/.openclaw/workspace/charts/{ticker}-{tf}-{timestamp}.png`
7. Send image via Telegram with context line: `Current: ${price} | 24h: {change}% | Vol: {vol_rank} vs avg`
8. Log request to `memory/chart-requests.json`

### API Endpoints Used
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.hyperliquid.xyz/info` | POST | OHLCV candle data |
| Telegram Bot API `sendPhoto` | POST | Deliver chart image |

### Expected Inputs
- Ticker symbol (e.g., BTC, ETH, HYPE — Hyper Liquid coin names without "-PERP" suffix in API)
- Timeframe (e.g., 1h, 4h, 15m)
- Optional: indicator list, date range, number of candles

### Expected Outputs
- Chart PNG file
- Telegram message with image + 1-line context

### Approval Gates
None — fully on-demand, Greg-initiated (or agent-triggered).

---

## Part 3: Secondary Workflows

### Generate Equity Curve

**Trigger**: Called by back-tester after backtest completion
**Input**: Equity curve data from backtest JSON
**Steps**:
1. Parse equity_curve: list of `{timestamp, equity}` points
2. Calculate drawdown series: `(equity - rolling_max) / rolling_max`
3. Render two-panel chart:
   - Main panel: equity line chart (base 100)
   - Sub-panel: drawdown area chart (filled red)
4. Annotate: max drawdown point, final equity value
5. Save and send via Telegram

**Output**: Equity curve + drawdown PNG → Telegram

### Edge Cases
- Ticker not found on Hyper Liquid: return error message, list available tickers
- Charting library unavailable (import error): report with install command `pip install mplfinance pandas ta`
- Telegram image upload fails (> 10 MB): compress to JPEG, reduce resolution; if still fails, save path locally
- Very few data points (< 20 candles): warn but still render — don't refuse

---

## Part 4: Tool Configuration

| Tool | Base URL | Auth Header | Key Endpoints |
|------|----------|-------------|---------------|
| Hyper Liquid | `https://api.hyperliquid.xyz` | None | `/info` (POST, candleSnapshot) |
| Telegram Bot API | `https://api.telegram.org/bot{TOKEN}` | N/A | `/sendPhoto` (multipart) |

### Python Libraries Required
```bash
pip install mplfinance pandas numpy ta pillow
```

### Chart Rendering Config
```python
import mplfinance as mpf

style = mpf.make_mpf_style(
    base_mpl_style='dark_background',
    rc={'axes.facecolor': '#1a1a2e', 'figure.facecolor': '#1a1a2e'},
    gridstyle='--',
    gridcolor='#333355',
    y_on_right=True
)

mpf.plot(df, type='candle', style=style, volume=True,
         addplot=additional_plots, savefig='chart.png')
```

---

## Part 5: Scheduling & Automation

### Cron Jobs
None — charting is fully on-demand.

### Heartbeat Tasks
None — responds to requests only.

### Trigger Patterns
- User-invocable: `/generate-chart` command
- Agent-triggered: Back-tester calls generate-equity-curve after backtest
- Alert-triggered: Monitor-feeds fires alert, optionally attaches chart

---

## Part 6: Integration Points

### Cross-Domain Connections
- **← Back Tester**: Equity curve data passed after backtest → generate-equity-curve
- **← Discord & Scraping**: Volume spike alert → chart of triggered ticker
- **← Portfolio Manager**: Position review may request chart for open position ticker

### Shared Tools or Data Sources
- Hyper Liquid API: shared with all domains
- Telegram Bot: shared delivery layer across all domains

### Workflow Handoffs
1. `run-backtest` completes → passes `equity_curve` data → `generate-equity-curve` renders and delivers
2. `monitor-feeds` fires volume spike alert → sends alert + optionally queues `generate-chart` call

---

## Part 7: Patterns & Learnings

### Patterns That Work
- (Populated after first self-improve cycle)

### Patterns To Avoid
- (Populated after first self-improve cycle)

### Known Issues
- Hyper Liquid coin names in API use "BTC" not "BTC-PERP" — strip suffix before API call
- mplfinance requires DataFrame with DatetimeIndex and specific column names (Open, High, Low, Close, Volume)

### Tips
- Dark background charts read better on mobile (where Greg likely views Telegram)
- Include the context line (price, 24h change) with every chart — Greg values data density
- For equity curves: always show drawdown — it's the honest view of strategy performance
- Keep chart files cleaned up: delete charts older than 7 days from the charts/ directory
