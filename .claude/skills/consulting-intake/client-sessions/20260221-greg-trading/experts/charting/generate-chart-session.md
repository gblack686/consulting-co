---
type: expert-file
parent: "[[charting/_index]]"
file-type: command
command-name: generate-chart-session
tags: [expert-file, command, charting]
---

# Generate Chart Session — Interactive Chart Generation and Analysis

> Generate a chart and provide technical analysis interpretation alongside it.

## Purpose

When Greg wants not just a chart but also Sebastian's read on what it shows. Combines chart generation with brief technical commentary.

## Allowed Tools
`Read, Write, Bash`

## Workflow

### Phase 1: Get Chart Request
From Greg's command or message:
- Ticker (required)
- Timeframe (required: 1m, 5m, 15m, 1h, 4h, 1d)
- Indicators (optional; default: 20 EMA, 50 EMA, volume)
- Date range (optional; default: last 100 candles)

### Phase 2: Generate Chart
Follow `generate-chart/SKILL.md` workflow to:
1. Fetch OHLCV data from Hyper Liquid
2. Calculate indicators
3. Render chart PNG (dark theme)
4. Save to charts directory

### Phase 3: Technical Analysis Commentary
After generating the chart, provide a brief read (3-5 bullet points):

```
📊 {ticker} {timeframe} Analysis

Key observations:
• Trend: {uptrend/downtrend/ranging based on price + EMA relationship}
• Price vs. EMAs: {above/below/crossing 20 EMA and 50 EMA}
• Volume context: {expanding/contracting vs. average}
• {if RSI requested}: RSI at {value} — {overbought/neutral/oversold}
• {if MACD requested}: MACD {bullish/bearish} crossover / histogram {expanding/contracting}

Assessment: {1 sentence: bullish setup / bearish setup / no clear edge / wait for confirmation}
```

Note: This is analysis, not a trade recommendation. Greg makes all trade decisions.

### Phase 4: Deliver
1. Send chart image via Telegram
2. Send analysis text in same conversation thread
3. Log request to `memory/chart-requests.json`

### Offer Follow-Ups
- "Want me to generate this on a different timeframe?"
- "Want to see the equity curve for a strategy on this asset?"
- "Should I set an alert if price crosses the 20 EMA?"

## Output Format
Chart image + technical analysis commentary delivered via Telegram.
