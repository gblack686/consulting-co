---
name: generate-equity-curve
description: "Trading: Generate Equity Curve - Visualize backtest results as equity curve with drawdown overlay"
---

# Generate Equity Curve

Render a backtest equity curve chart with drawdown overlay. Typically invoked by the run-backtest skill after a completed backtest.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Load Backtest Data
1. Receive backtest results JSON (passed from run-backtest or loaded from `memory/backtests/`)
2. Extract: equity_curve (list of {timestamp, equity_value}), trade_log, max_drawdown periods

### Phase 2: Render Chart
1. Plot main panel: equity curve line (starting at 100)
2. Plot sub-panel: drawdown % over time (filled area, red)
3. Mark: trade entries (small triangles) and exits (small squares)
4. Annotate: max drawdown point, start/end equity
5. Title: `{strategy_name} | {asset} {timeframe} | {start} → {end}`

### Phase 3: Deliver
1. Save to `~/.openclaw/workspace/charts/equity-{strategy_name}-{timestamp}.png`
2. Send via Telegram to Greg
3. Link back to original backtest report in memory

## Output Format
Equity curve chart image sent via Telegram.

## Error Handling
- Insufficient data points (< 10 trades) → warn and still render
- Charting library error → report error
