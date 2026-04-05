---
name: optimize-strategy
description: "Trading: Optimize Strategy - Run parameter sweep to find optimal strategy configuration"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY"]}}}
---

# Optimize Strategy

Run a parameter sweep (grid search or walk-forward) to find optimal settings for a trading strategy, with overfitting checks.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Define Search Space
1. Receive: strategy name + parameter ranges
   - Example: `{"ma_fast": [5, 10, 20], "ma_slow": [50, 100, 200], "rsi_threshold": [30, 35, 40]}`
2. Validate: total combinations < 500 (cap to prevent runaway compute)
3. Split date range: 70% in-sample, 30% out-of-sample (holdout)

### Phase 2: Grid Search (In-Sample)
1. For each parameter combination:
   - Run backtest on in-sample period
   - Collect Sharpe ratio, max drawdown, win rate, profit factor
2. Rank combinations by Sharpe ratio (primary) and max drawdown (secondary)
3. Select top 10 candidates

### Phase 3: Out-of-Sample Validation
1. For each top-10 candidate:
   - Run backtest on holdout (out-of-sample) period
   - Compare in-sample vs. out-of-sample Sharpe: degradation > 30% = overfitting flag
2. Identify top 3 configurations that generalize well

### Phase 4: Report

**[APPROVAL GATE]** Greg reviews and selects which configuration to use going forward.

```
🔬 Optimization: {strategy_name}
Parameters tested: {total_combinations}
In-sample period: {start} → {end}
Out-of-sample period: {start} → {end}

TOP 3 CONFIGURATIONS:
1. Params: {params} | Sharpe: {sharpe} | DD: {dd_pct}% | OOS degradation: {deg_pct}%
2. Params: {params} | Sharpe: {sharpe} | DD: {dd_pct}% | OOS degradation: {deg_pct}%
3. Params: {params} | Sharpe: {sharpe} | DD: {dd_pct}% | OOS degradation: {deg_pct}%

⚠️ Overfitting flags: {count} configurations flagged
Recommendation: {config #N} — best balance of performance and generalization
```

## Output Format
Optimization report JSON + Telegram summary with top 3 configs.

## Error Handling
- Too many combinations → cap at 500, warn Greg and proceed
- All configs perform poorly (Sharpe < 0.5) → report honestly, suggest strategy revision
