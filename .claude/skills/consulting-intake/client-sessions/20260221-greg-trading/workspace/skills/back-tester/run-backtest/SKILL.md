---
name: run-backtest
description: "Trading: Run Backtest - Execute a strategy backtest on Hyper Liquid historical data and report metrics"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY"]}}}
---

# Run Backtest

Execute a full backtest of a named strategy on historical Hyper Liquid data and return performance metrics. On-demand or nightly scheduled.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Load Strategy Spec
1. Receive strategy request with:
   - Strategy name / ID
   - Parameters (e.g., MA periods, RSI threshold, etc.)
   - Asset: e.g., BTC-PERP
   - Timeframe: 1m, 5m, 15m, 1h, 4h, 1d
   - Date range: start_date to end_date (default: last 6 months)
2. Load strategy code from `~/.openclaw/strategies/{strategy_name}/` (Python)

### Phase 2: Fetch Historical Data
1. Call Hyper Liquid historical API: `POST /info` with `{"type": "candleSnapshot", "req": {...}}`
2. Download OHLCV candles for the specified asset + timeframe + date range
3. Cache to `~/.openclaw/data/market-history/{asset}-{timeframe}.parquet`

### Phase 3: Execute Backtest
1. Run strategy code against historical data
2. Simulate trades: apply entry/exit rules, track positions
3. Apply realistic assumptions: slippage 0.05%, fees 0.045% (Hyper Liquid taker), no partial fills

### Phase 4: Calculate Metrics
| Metric | Formula |
|--------|---------|
| Total Return | (final_equity - initial_equity) / initial_equity |
| Sharpe Ratio | (mean_return / std_return) × sqrt(periods_per_year) |
| Max Drawdown | max(peak - trough) / peak |
| Win Rate | winning_trades / total_trades |
| Profit Factor | gross_profit / gross_loss |
| Avg Trade | total_pnl / total_trades |

### Phase 5: Report
1. Write results to `memory/backtests/{strategy_name}-{date}.json`
2. Generate equity curve data (for charting agent)
3. Send summary to Greg via Telegram:
   ```
   📈 Backtest: {strategy_name} | {asset} {timeframe}
   Period: {start} → {end} ({days} days)

   Total Return: {return_pct}%
   Sharpe: {sharpe}
   Max Drawdown: {max_dd_pct}%
   Win Rate: {win_rate}%
   Profit Factor: {profit_factor}
   Trades: {total_trades}

   Verdict: {PROMISING/NEEDS_WORK/AVOID based on thresholds}
   ```
4. Optionally trigger generate-equity-curve skill

## Output Format
Full backtest JSON + Telegram summary.

## Error Handling
- Strategy code not found → prompt Greg to add strategy file
- Insufficient historical data → note date range limitation, use what's available
- Backtest fails (error in strategy code) → report specific error with traceback summary
