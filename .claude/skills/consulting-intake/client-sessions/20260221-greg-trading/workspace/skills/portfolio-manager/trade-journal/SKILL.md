---
name: trade-journal
description: "Trading: Trade Journal - Log closed trades and generate performance analysis"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY"]}}}
---

# Trade Journal

Detect closed positions, log them with full context, and build running performance analytics. Also generates weekly trade review summaries.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Detect Closed Trades
1. Fetch trade history from Hyper Liquid API: `GET /userFills`
2. Compare to previously logged fills in `memory/trade-journal/fills-state.json`
3. Identify new closed trades since last check

### Phase 2: Log Trade
For each new closed trade:
1. Build trade record:
   ```json
   {
     "ticker": "BTC-PERP",
     "side": "LONG",
     "entry_price": 95000,
     "exit_price": 97500,
     "size": 0.1,
     "pnl_usd": 250,
     "pnl_pct": 2.63,
     "duration_hours": 4.5,
     "sl_used": true,
     "tp_hit": true,
     "exit_reason": "take_profit",
     "timestamp_open": "2026-02-21T10:00:00Z",
     "timestamp_close": "2026-02-21T14:30:00Z"
   }
   ```
2. Append to `memory/trade-journal/trades.json`
3. Update running stats: win_rate, avg_pnl, total_pnl, streak

### Phase 3: Weekly Summary (runs every Monday 7 AM PST)
1. Pull all trades from the past 7 days
2. Calculate:
   - Win rate, avg win, avg loss, profit factor
   - Best trade, worst trade
   - Most traded ticker
   - Strategy performance breakdown (if tagged)
3. Identify patterns: any repeated mistakes? What worked?
4. Send summary via Telegram to Greg

## Output Format
```
Trade logged: {ticker} {side} | P&L: {pnl_usd} ({pnl_pct}%)
Running stats: Win rate: {win_rate}% | Total P&L: ${total_pnl}
```

## Error Handling
- API returns no new fills → log "No new closed trades"
- Duplicate fill detected → skip, already logged
