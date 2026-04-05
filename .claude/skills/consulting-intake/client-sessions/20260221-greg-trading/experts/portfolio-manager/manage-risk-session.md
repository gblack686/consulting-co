---
type: expert-file
parent: "[[portfolio-manager/_index]]"
file-type: command
command-name: manage-risk-session
tags: [expert-file, command, portfolio-manager, risk]
---

# Manage Risk Session — Full Portfolio Risk Review

> Run a comprehensive risk analysis on all open positions and get actionable recommendations.

## Purpose

When Greg wants a deep risk review — not just the automated alerts, but a full analysis of every position with specific stop-loss and TP recommendations.

## Allowed Tools
`Read, Write, Bash`

## Workflow

### Phase 1: Fetch All Open Positions
1. Get full position state from Hyper Liquid API
2. Get all open orders (stops, TPs, limits)
3. Get last 24h price action for each position's ticker

### Phase 2: Position-Level Analysis
For each position:

| Metric | Calculate |
|--------|-----------|
| Entry vs. Current | Distance from entry in % |
| Distance to SL | % loss if stop-loss hit |
| Distance to TP | % gain if target hit |
| R/R Ratio | TP distance / SL distance |
| Time in trade | Hours since entry |
| 1h momentum | % change last hour |
| 4h momentum | % change last 4 hours |
| Volume context | Current volume vs. 20-period average |

### Phase 3: Recommendation Engine
Apply rules to each position:

1. **No SL**: Generate emergency SL at entry × (1 - 3%) — must fix NOW
2. **SL too loose (> 5% from current)**: Recommend tightening
3. **Winning position (> 3%)**: Recommend trailing SL to lock in partial gains
4. **Near TP (< 1% away)**: Recommend partial take + hold remainder
5. **Poor R/R (< 1.0)**: Flag for review — risk more than potential gain
6. **Correlation risk**: If 3+ positions are in same direction/asset class, flag concentration

### Phase 4: Portfolio-Level Risk
1. Calculate total open risk (dollar amount at risk if all SLs hit)
2. Calculate max drawdown scenario
3. Assign overall risk score: GREEN (<5% total at risk) / YELLOW (5-10%) / RED (>10%)

### Phase 5: Report

**[APPROVAL GATE]** All recommendations are proposals. Greg executes manually.

Format: Send via Telegram with full position table + recommendations.

Include action priority:
- 🚨 URGENT (missing SL, critical drawdown)
- ⚠️ RECOMMENDED (SL tightening, TP adjustment)
- 💡 OPTIONAL (R/R improvements)

## Output Format
Full risk analysis report via Telegram + archived in `memory/risk-reviews/{YYYY-MM-DD}.md`.
