---
name: morning-brief
description: "Trading: Morning Brief - Deliver daily market overview, portfolio status, signals, and news to Greg"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY", "TELEGRAM_BOT_TOKEN"]}}}
---

# Morning Brief

Compile and deliver Greg's daily morning brief via Telegram. Runs every morning at 7:00 AM PST.

## Allowed Tools
`Bash, Read, Write, WebSearch`

## Workflow

### Phase 1: Gather Data (run in parallel)
1. **Market Overview**: Fetch BTC/ETH/HYPE prices + 24h volume + market cap change
2. **Portfolio Overview**: Call Hyper Liquid API for open positions, unrealized P&L, account equity, margin ratio
3. **Overnight Discord Signals**: Read `memory/discord-signals/{YYYY-MM-DD}.json` — pull top 3-5 highest-quality signals
4. **Overnight YouTube Insights**: Read `memory/youtube-insights/{YYYY-MM-DD}.json` — pull 1-2 key insights
5. **News Digest**: WebSearch for top crypto/trading news from last 12 hours

### Phase 2: Compose Brief
Write a structured daily brief with these sections:

```
📊 Morning Brief — {date} | {time} PST

🌐 MARKET OVERVIEW
• BTC: ${price} ({24h_change}%) | Vol: ${volume}
• ETH: ${price} ({24h_change}%)
• HYPE: ${price} ({24h_change}%)
• Market Sentiment: {bullish/bearish/neutral based on data}

💼 YOUR PORTFOLIO
• Equity: ${equity} | P&L Today: ${pnl} ({pnl_pct}%)
• Open Positions: {count}
  {list of positions with current price and P&L}
• ⚠️ Missing stop-losses: {count} (list tickers if any)

📡 TOP SIGNALS (last 24h)
{top 3-5 signals from Discord with quality scores}

📰 KEY NEWS
{2-3 bullet points of relevant news}

💡 TODAY'S INSIGHT
{1 key insight from YouTube research or quant analysis}

📋 ACTION ITEMS
{any open items: missing SL, pending backtests, etc.}
```

### Phase 3: Deliver
1. Send completed brief via Telegram to Greg
2. Log brief to `memory/morning-briefs/{YYYY-MM-DD}.md`

## Output Format
Brief delivered via Telegram. Confirmation logged.

## Error Handling
- Hyper Liquid API down → use last known portfolio state, note staleness
- Discord signals missing → note "no signals overnight" — don't skip brief
- News search fails → omit news section, note error in brief
