---
name: monitor-positions
description: "Trading: Monitor Positions - Check Hyper Liquid positions for missing stop-losses and drawdown thresholds"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY", "TELEGRAM_BOT_TOKEN"]}}}
---

# Monitor Positions

Check all open Hyper Liquid positions for risk conditions. Ensures stop-losses are always set and drawdown thresholds aren't breached. Runs every 15 minutes via heartbeat.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Fetch Positions
1. Call Hyper Liquid API: `GET /info` with `{"type": "openOrders"}` and `{"type": "clearinghouseState"}`
2. Parse all open positions: ticker, side, size, entry_price, current_price, unrealized_pnl, leverage

### Phase 2: Risk Checks
1. **Stop-loss check**: For each position, verify an open stop-loss order exists
   - No stop-loss → HIGH PRIORITY alert
2. **Drawdown check**: Calculate unrealized P&L % for each position and portfolio total
   - Position drawdown > 5% → WARNING alert
   - Position drawdown > 10% → HIGH PRIORITY alert
   - Portfolio total drawdown > 15% → CRITICAL alert
3. **Leverage check**: Flag positions with leverage > {max_leverage_threshold} (default: 10x)

### Phase 3: Log and Alert
1. Write portfolio snapshot to `memory/portfolio-snapshots/{YYYY-MM-DD-HHmm}.json`
2. For each issue found:
   - **Missing SL**: `🚨 MISSING STOP-LOSS: {ticker} {side} — Set one NOW`
   - **Warning drawdown**: `⚠️ Drawdown warning: {ticker} is at {pnl_pct}%`
   - **Critical drawdown**: `🔴 CRITICAL: Portfolio down {portfolio_pnl_pct}% — review all positions`
3. During quiet hours: still send CRITICAL alerts; suppress WARNING and INFO

## IMPORTANT
This skill only monitors and alerts. It NEVER executes trades or modifies positions.
All action requires Greg's manual decision.

## Output Format
```
Position check: {position_count} open positions
Issues found: {issue_count} ({critical_count} critical, {warning_count} warnings)
Portfolio P&L: {portfolio_pnl_pct}%
```

## Error Handling
- API auth failure → alert Greg: "Cannot access Hyper Liquid — check API key"
- API timeout → retry once; if fails, note in log; don't suppress future checks
