---
name: scout-datasets
description: "Trading: Scout Datasets - Overnight search for new data sources that could provide trading edge"
---

# Scout Datasets

Overnight research task. Search for new publicly available data sources that could give Greg a trading edge. Runs nightly.

## Allowed Tools
`Bash, Read, Write, WebSearch`

## Workflow

### Phase 1: Search for New Data Sources
1. WebSearch for recent (last 7 days) developments in:
   - "Hyper Liquid on-chain data {current_year}"
   - "crypto trading alternative data free API {current_year}"
   - "DeFi sentiment data API"
   - "crypto options flow data"
   - "social sentiment trading data free"
2. Check known sources for new features: Glassnode, Dune Analytics, CryptoQuant, Santiment (free tiers)

### Phase 2: Evaluate Each Source
For each promising source found:
| Metric | Evaluate |
|--------|---------|
| Data quality | Recent? Reliable? Well-documented? |
| Update frequency | Real-time? Daily? |
| Cost | Free? Freemium? Paid? |
| API availability | REST/WebSocket available? |
| Trading relevance | Predictive signal potential? |

### Phase 3: Weekly Report
Compile top finds (max 3 per week) into a brief:
```
🔍 Dataset Scout — Week of {date}

NEW SOURCES FOUND: {count}

1. {source_name}
   Type: {on-chain/sentiment/options/other}
   URL: {url}
   Update frequency: {frequency}
   Cost: {free/paid}
   Potential: {HIGH/MEDIUM/LOW}
   Why it's interesting: {1 sentence}

{repeat for each}

RECOMMENDATION: {which to try first and why}
```

Only report weekly unless a HIGH-priority find warrants immediate alert.

## Output Format
Weekly dataset scouting report in `memory/dataset-scout/{YYYY-WW}.md` + Telegram summary.

## Error Handling
- No new sources found → report "No new sources this week" — always report
