---
type: expert-file
parent: "[[back-tester/_index]]"
file-type: command
command-name: run-backtest-session
tags: [expert-file, command, back-tester]
---

# Run Backtest Session — Interactive Backtest Execution

> Run a backtest interactively with Greg, reviewing results and drilling into details.

## Purpose

When Greg wants to run a specific backtest with discussion — not just the automated nightly run, but an interactive session where they review the strategy, run it, and discuss the results together.

## Allowed Tools
`Read, Write, Bash`

## Workflow

### Phase 1: Define the Backtest
Ask Greg (or take from command input):
1. Strategy name: which strategy to test?
2. Asset: BTC-PERP, ETH-PERP, HYPE-PERP, or other?
3. Timeframe: 15m, 1h, 4h, 1d?
4. Date range: last 3 months? 6 months? 1 year?
5. Parameters: any custom values to override defaults?

If strategy is new: confirm it exists in `~/.openclaw/strategies/` before running.

### Phase 2: Pre-flight Check
1. Verify historical data availability for requested range + asset + timeframe
2. If data missing or stale (> 24h): fetch fresh from Hyper Liquid
3. Confirm strategy file interface is correct (`generate_signals` function)
4. Estimate runtime for sanity check

### Phase 3: Execute Backtest
Run the backtest as specified in `run-backtest/SKILL.md`.
Show progress for long runs (> 30 seconds).

### Phase 4: Present Results — Interactive
Don't just dump metrics. Walk Greg through the results:

```
📈 Backtest Complete: {strategy_name}
Asset: {asset} | Timeframe: {tf} | Period: {start} → {end}

HEADLINE NUMBERS:
• Total Return: {return_pct}%  (benchmark: {market_return_pct}%)
• Sharpe Ratio: {sharpe}       (target: > 1.0)
• Max Drawdown: {max_dd_pct}%  (limit: 20%)
• Win Rate: {win_rate}%
• Profit Factor: {profit_factor}
• Total Trades: {trade_count}

Verdict: {PROMISING 🟢 | NEEDS_WORK 🟡 | AVOID 🔴}

Key insight: {1 sentence on what drives the performance}
```

5. Offer drill-down options:
   - "View equity curve chart" → trigger generate-equity-curve
   - "Show trade-by-trade breakdown" → list top 5 wins and worst 5 losses
   - "Compare to buy-and-hold" → compute simple B&H return for same period

### Phase 5: Next Steps
Based on verdict:
- **PROMISING**: "Want me to run optimization to find best parameters?"
- **NEEDS_WORK**: "I see {issue} as the main problem — want to try adjusting {parameter}?"
- **AVOID**: "This strategy has fundamental issues: {reason}. Want to shelve it or try a different approach?"

## Output Format
Interactive session via Telegram + backtest archived in `memory/backtests/`.
