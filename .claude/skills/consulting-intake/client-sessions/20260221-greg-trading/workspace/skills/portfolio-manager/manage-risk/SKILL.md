---
name: manage-risk
description: "Trading: Manage Risk - Analyze positions and generate stop-loss / TP adjustment recommendations"
metadata: {"openclaw": {"requires": {"env": ["HYPERLIQUID_API_KEY"]}}}
---

# Manage Risk

Proactive risk analysis: review all open positions, evaluate risk/reward, and generate concrete stop-loss and TP adjustment recommendations. On-demand or scheduled.

## Allowed Tools
`Bash, Read, Write`

## Workflow

### Phase 1: Fetch & Analyze Positions
1. Get all open positions from Hyper Liquid API
2. For each position:
   - Current price vs. entry: distance to TP, distance to SL
   - Risk/reward ratio: (TP distance) / (SL distance)
   - Time in trade: entry timestamp
   - Momentum: 1h and 4h price change

### Phase 2: Generate Recommendations
For each position, apply rules:
- **Trail stop-loss**: If price moved in favor by > {trail_threshold}%, suggest moving SL to breakeven or better
- **Tighten TP**: If momentum slowing and position near TP, suggest locking in earlier
- **Emergency SL**: If no SL set, generate recommended SL at entry × (1 - max_loss_pct)
- **Correlation risk**: If multiple positions are in same direction on correlated assets, flag concentration risk

### Phase 3: Portfolio Risk Summary
1. Calculate portfolio metrics:
   - Total open risk (sum of distances to all stop-losses in dollar terms)
   - Max drawdown scenario (if all stop-losses hit)
   - Correlation matrix for open positions
2. Output risk score: GREEN / YELLOW / RED based on total exposure

### Phase 4: Present Recommendations

**[APPROVAL GATE]** All recommendations are proposals only. Greg must execute manually.

Send formatted recommendations via Telegram:
```
📋 Risk Review — {date}

Portfolio Risk: {GREEN/YELLOW/RED}
Max drawdown if all SLs hit: ${max_drawdown_usd}

POSITION RECOMMENDATIONS:
{For each position with a recommendation:}
• {ticker} {side}: {recommendation}
  Current: {current_price} | SL: {sl_price} | TP: {tp_price}
  Suggested: {specific adjustment}
```

## Output Format
Risk review report + Telegram message with recommendations.

## Error Handling
- Position fetch fails → report error, do not proceed
- No open positions → respond "No open positions to review"
