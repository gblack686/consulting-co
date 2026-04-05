---
name: generate-chart
description: "Trading: Generate Chart - Create price/indicator chart for a ticker on demand and send via Telegram"
user-invocable: true
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY", "TELEGRAM_BOT_TOKEN"]}}}
---

# Generate Chart

Generate a candlestick chart with indicator overlays for any ticker on demand. Send chart image to Greg via Telegram. User-invocable with `/generate-chart`.

## Allowed Tools
`Bash, Read, Write`

## Usage
```
/generate-chart BTC-PERP 1h
/generate-chart ETH-PERP 4h indicators=RSI,MACD
/generate-chart HYPE-PERP 15m days=3
```

## Workflow

### Phase 1: Parse Request
1. Extract from command: ticker, timeframe, optional indicators, optional date range
2. Default: last 100 candles, indicators: 20 EMA, 50 EMA, volume

### Phase 2: Fetch Data
1. Call Hyper Liquid API for OHLCV candles
2. Calculate requested indicators:
   - MA/EMA: standard calculation
   - RSI: 14-period default
   - MACD: 12/26/9 default
   - Volume: included by default

### Phase 3: Render Chart
1. Use mplfinance (or equivalent) to render:
   - Candlestick chart (main panel)
   - Volume bars (sub-panel)
   - Requested indicators overlaid
2. Style: dark background, clean lines — Greg prefers visual clarity
3. Add title: `{ticker} | {timeframe} | {date_range}`
4. Save to `~/.openclaw/workspace/charts/{ticker}-{timeframe}-{timestamp}.png`

### Phase 4: Deliver
1. Send chart image via Telegram to Greg
2. Include 1-line market context: `Current: ${price} | 24h: {change}% | Volume: {vol_rank} vs avg`

## Output Format
Chart image delivered via Telegram with brief context line.

## Error Handling
- Ticker not found → "Ticker {ticker} not found on Hyper Liquid — check symbol"
- Charting library error → report error with traceback summary
- Telegram upload fails → save chart to local file, report path to Greg
