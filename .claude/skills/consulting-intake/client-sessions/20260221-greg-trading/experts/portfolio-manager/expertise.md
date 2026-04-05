---
type: expert-file
parent: "[[portfolio-manager/_index]]"
file-type: expertise
human_reviewed: false
tags: [expert-file, mental-model, portfolio-manager, trading]
last_updated: 2026-02-21
---

# Portfolio Manager Expert - Complete Mental Model

## Part 1: Domain Architecture

### Overview
The Portfolio Manager domain is Greg's always-on risk guardian for his Hyper Liquid account. It checks every open position every 15 minutes, enforces a mandatory stop-loss policy, monitors drawdown thresholds, generates risk recommendations, and logs all trades for learning. The core constraint: this domain NEVER executes trades. All actions are monitoring, alerting, and proposing.

### Tool Connections
```
Hyper Liquid REST API
    ↓
Position Monitor (every 15m)
    ↓
Risk Checks:
  ├── Missing stop-loss? → 🚨 CRITICAL alert → Telegram → Greg
  ├── Drawdown > 5%?    → ⚠️ WARNING alert → Telegram → Greg
  └── Drawdown > 15%?   → 🔴 CRITICAL alert → Telegram → Greg

Closed Position Detected
    ↓
Trade Journal Logger
    ↓
memory/trade-journal/trades.json

On-Demand Risk Analysis
    ↓
Risk Manager
    ↓
Recommendations (proposals only) → Telegram → Greg
```

### Key File Locations
| File | Purpose |
|------|---------|
| `memory/portfolio-snapshots/{YYYY-MM-DD-HHmm}.json` | Every-15m position snapshot |
| `memory/trade-journal/trades.json` | All closed trades log |
| `memory/trade-journal/fills-state.json` | Last checked fill IDs (dedup) |
| `memory/trade-journal/stats.json` | Running performance stats |

### Data Flows
- Hyper Liquid API → positions → risk checks → alert if triggered
- Hyper Liquid fills → detect closed trades → log to trade journal
- Trade journal → weekly stats → weekly summary to Greg

---

## Part 2: Primary Workflow — Position Monitor (Every 15 Minutes)

### Trigger
- Type: cron / heartbeat
- Schedule: `*/15 * * * *`
- Timezone: UTC (server time)

### Steps
1. `POST https://api.hyperliquid.xyz/info` with `{"type": "clearinghouseState", "user": "{wallet_address}"}`
2. Parse positions: `assetPositions[]` array
3. For each position:
   a. Extract: coin, side (long/short), size, entryPx, unrealizedPnl, leverage
   b. Fetch current open orders: `POST /info` with `{"type": "openOrders", "user": "{wallet}"}`
   c. Check if a stop-loss order exists for this position
   d. Calculate drawdown %: `unrealizedPnl / (entryPx × size)` in percent
4. Calculate portfolio-level unrealized P&L
5. Log snapshot to `memory/portfolio-snapshots/{timestamp}.json`
6. Fire alerts for any issues (see thresholds below)

### Alert Thresholds
| Condition | Level | Message |
|-----------|-------|---------|
| No stop-loss on any position | CRITICAL | 🚨 MISSING STOP-LOSS: {ticker} — Set one NOW |
| Position drawdown > 5% | WARNING | ⚠️ Drawdown warning: {ticker} at {pct}% |
| Position drawdown > 10% | HIGH | 🔴 High drawdown: {ticker} at {pct}% |
| Portfolio total drawdown > 15% | CRITICAL | 🔴 CRITICAL: Portfolio down {pct}% |
| Position leverage > 10x | WARNING | ⚠️ High leverage: {ticker} at {leverage}x |

### API Endpoints Used
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.hyperliquid.xyz/info` | POST | Get clearinghouse state (positions) |
| `https://api.hyperliquid.xyz/info` | POST | Get open orders (stop-loss check) |

### Expected Inputs
- Hyper Liquid API key + wallet address (env: `HYPERLIQUID_API_KEY`, `HYPERLIQUID_WALLET`)

### Expected Outputs
- Position snapshot JSON in memory
- Telegram alerts for any threshold violations

### Approval Gates
CRITICAL (trade execution): None taken — monitoring only. Greg acts manually on alerts.

---

## Part 3: Secondary Workflows

### Manage Risk (On-Demand)

**Trigger**: On-demand (Greg request or after position monitor flags issues)
**Steps**:
1. Fetch all open positions (same as monitor)
2. For each: calculate R/R ratio, distance to TP/SL, momentum (1h + 4h price change)
3. Apply recommendation rules: trail stop, tighten TP, emergency SL
4. Calculate portfolio-level correlation risk
5. Generate risk score: GREEN/YELLOW/RED
6. Send formatted recommendations via Telegram

**Output**: Recommendation report — all proposals, no execution

**[APPROVAL GATE]**: Greg executes manually

### Trade Journal (Continuous + Weekly Summary)

**Trigger**: Runs every 15m alongside position monitor to detect closed trades
**Steps**:
1. Fetch user fills from `POST /info` with `{"type": "userFills", "user": "{wallet}"}`
2. Compare to `memory/trade-journal/fills-state.json` for new fills
3. For each new fill: build trade record (entry, exit, P&L, duration, SL/TP used)
4. Append to `memory/trade-journal/trades.json`
5. Update running stats in `memory/trade-journal/stats.json`
6. On Monday 7 AM: generate weekly summary

**Output**: Trade log entries + weekly P&L summary

### Edge Cases
- Position shows no stop-loss but there's a conditional order: check all order types (trigger orders, not just limit stops)
- Position closed partially: log partial fill, update remaining position separately
- API returns stale data (cached): retry with `Cache-Control: no-cache` header

---

## Part 4: Tool Configuration

| Tool | Base URL | Auth Header | Key Endpoints |
|------|----------|-------------|---------------|
| Hyper Liquid | `https://api.hyperliquid.xyz` | `Authorization: Bearer {API_KEY}` (for write ops) | `/info` (POST) |
| Hyper Liquid (paper) | `https://api.hyperliquid-testnet.xyz` | Same | `/info` (POST) |

### Hyper Liquid API Key Endpoints (POST /info)
| Type Field | Returns |
|------------|---------|
| `clearinghouseState` | All open positions + account equity |
| `openOrders` | All open orders (including stops) |
| `userFills` | Historical fills / closed trades |
| `meta` | Available tokens + leverage limits |

### MCP Server Availability
- No known Hyper Liquid MCP server as of intake — use direct REST calls
- Check ClawHub for "hyperliquid" before deployment

---

## Part 5: Scheduling & Automation

### Cron Jobs

| Name | Schedule | Skill | Mode | Delivery |
|------|----------|-------|------|----------|
| Position Monitor | `*/15 * * * *` | monitor-positions | isolated | none (alerts via skill) |
| Trade Journal | `*/15 * * * *` | trade-journal | isolated | none |
| Weekly Trade Review | `0 7 * * 1` PST | trade-journal (weekly mode) | main | announce |

### Heartbeat Tasks
- Check positions every 15m heartbeat
- Detect closed trades on same cadence

### Trigger Patterns
- Monitoring: pure time-driven polling
- Future: WebSocket stream from Hyper Liquid for real-time position updates (more efficient)

---

## Part 6: Integration Points

### Cross-Domain Connections
- **← Discord & Scraping**: Signal context attached to trade proposals
- **→ Back Tester**: Closed trade data informs backtesting strategy selection
- **→ Charting**: Position analysis can request charts for open positions

### Shared Tools or Data Sources
- Hyper Liquid API: shared with Back Tester (historical data) and Charting (price data)

### Workflow Handoffs
1. Trade journal logs closed trades → back-tester can analyze patterns to improve strategies
2. Position missing SL alert → Greg manually sets SL → next 15m check confirms resolved

---

## Part 7: Patterns & Learnings

### Patterns That Work
- (Populated after first self-improve cycle)

### Patterns To Avoid
- (Populated after first self-improve cycle)

### Known Issues
- Hyper Liquid paper trading uses a different base URL (`https://api.hyperliquid-testnet.xyz`) — confirm which Greg is using at setup
- `clearinghouseState` returns leverage in asset-specific format — normalize before calculating drawdown

### Tips
- Start on paper trading testnet, validate all monitoring logic, then switch to mainnet
- Stop-loss detection: check both regular limit orders AND trigger/conditional orders
- Greg's rule: ALWAYS have a stop-loss — make this check loud and persistent until resolved
