---
type: expert-file
parent: "[[trade-executor/_index]]"
file-type: expertise
human_reviewed: false
tags: [expert-file, mental-model, trade-executor, trading]
last_updated: 2026-03-18
---

# Trade Executor Expert — Complete Mental Model

## Part 1: Domain Architecture

### Overview

Apex manages trade execution on Hyperliquid from proposal to close. It maintains a live `execution_plan` object in Supabase that tracks every tranche, fill, stop-loss order, and TP target. A background WebSocket daemon streams fills in real-time so Apex never misses an event. The hard rule: every fill triggers an immediate SL update covering 100% of position before any other action.

### Tool Connections

```
WF-017 Trade Proposal (Telegram card)
        ↓
[APPROVAL GATE: Greg approves]
        ↓
Apex: parse-proposal
        ↓
Build Execution Plan → Supabase (execution_plans table)
        ↓
Execute Tranche 1 (market/limit)
    ↓
WebSocket stream (userEvents) detects fill
    ↓
IMMEDIATE: Place SL covering 100% of filled size
    ↓
Alert: "✅ Tranche 1 filled @ {price} | SL set @ {sl_price}"
        ↓
Monitor: Wait for price to hit Tranche 2 level
        ↓
Execute Tranche 2 → Fill → Cancel old SL → Place new SL (full position)
        ↓
Monitor: Price action vs TP targets
        ↓
Scale-Out: Partial exit at TP1 → Update SL (trail to breakeven+)
        ↓
Scale-Out: Full exit at TP2 → Plan closed → Supabase updated
        ↓
Alert: "🏁 Position closed | P&L: +{pct}% | Avg slippage: {bps} bps"
```

### Key File Locations

| File | Purpose |
|------|---------|
| `memory/execution-plans/{plan_id}.json` | Local plan cache (Supabase is source of truth) |
| `memory/fills/{YYYY-MM-DD}.json` | Daily fill log |
| `memory/slippage-log.json` | Slippage per tranche over time |
| `memory/ws-stream.log` | WebSocket event log (last 500 events) |

### Data Flows

```
Supabase (execution_plans) ←→ Apex plan state
Hyperliquid WS (userEvents) → fill detection → SL update → Telegram alert
Hyperliquid WS (l2Book)     → orderbook depth → pre-trade slippage estimate
Hyperliquid /info           → position verification after each fill
Telegram Bot                ← all execution alerts and status updates
```

### Supabase Tables

```sql
-- Active and historical execution plans
CREATE TABLE execution_plans (
  plan_id       TEXT PRIMARY KEY,          -- e.g. APEX-20260318-001
  ticker        TEXT NOT NULL,
  direction     TEXT NOT NULL,             -- 'long' | 'short'
  total_size    NUMERIC NOT NULL,
  tranches      JSONB NOT NULL,            -- array of tranche objects
  stop_loss     JSONB NOT NULL,            -- {price, order_id, status}
  take_profits  JSONB NOT NULL,            -- array of {pct, price, order_id}
  status        TEXT NOT NULL,             -- pending|active|partial|closed|cancelled
  approved_by   TEXT DEFAULT 'greg',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  closed_at     TIMESTAMPTZ,
  realized_pnl  NUMERIC,
  avg_slippage_bps NUMERIC
);

-- Per-tranche fill records
CREATE TABLE fills (
  fill_id       TEXT PRIMARY KEY,
  plan_id       TEXT REFERENCES execution_plans(plan_id),
  tranche_id    INT,
  ticker        TEXT,
  side          TEXT,                      -- 'buy' | 'sell'
  size          NUMERIC,
  expected_px   NUMERIC,                   -- mid price at order time
  fill_px       NUMERIC,                   -- actual fill price
  slippage_bps  NUMERIC,                   -- abs(fill-expected)/expected*10000
  filled_at     TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Part 2: Primary Workflow — Execute Approved Trade Proposal

### Trigger

- Type: On-demand (Greg approval via Telegram or direct command to Apex)
- Input: Approved trade proposal JSON from WF-017 or structured command
- Prerequisite: Greg has explicitly approved — Apex never self-initiates

### Proposal Format (input from WF-017)

```json
{
  "ticker": "BTC",
  "direction": "long",
  "entry_zone": {"low": 49000, "high": 49500},
  "stop_loss": 48000,
  "take_profits": [{"pct": 50, "price": 52000}, {"pct": 50, "price": 55000}],
  "rr_ratio": 2.5,
  "position_size_pct": 5,
  "supporting_signals": ["Discord signal: @trader123", "RSI oversold 4H"],
  "proposal_id": "WF017-20260318-001",
  "approved": true
}
```

### Steps

**1. Parse and validate proposal**
- Confirm `approved: true` — hard stop if not
- Validate: SL defined, TP defined, position_size_pct within Greg's limits (max 10% per trade)
- Calculate absolute size from account equity: `size = equity × (position_size_pct / 100) / entry_price`

**2. Build execution plan**
- Default tranche split: 40% / 35% / 25%
- Tranche 1: market order (entry immediately at market)
- Tranche 2: limit order at entry_zone.low
- Tranche 3: limit order at entry_zone.low × 0.995 (1 tick below zone)
- Custom splits accepted if provided in proposal

```json
{
  "plan_id": "APEX-20260318-001",
  "ticker": "BTC",
  "direction": "long",
  "total_size": 0.1,
  "tranches": [
    {"id": 1, "pct": 40, "size": 0.04, "type": "market",  "target_px": null,  "order_id": null, "status": "pending"},
    {"id": 2, "pct": 35, "size": 0.035,"type": "limit",   "target_px": 49000, "order_id": null, "status": "pending"},
    {"id": 3, "pct": 25, "size": 0.025,"type": "limit",   "target_px": 48755, "order_id": null, "status": "pending"}
  ],
  "stop_loss": {"price": 48000, "order_id": null, "covers_size": 0, "status": "not_placed"},
  "take_profits": [
    {"id": 1, "pct": 50, "price": 52000, "order_id": null, "status": "pending"},
    {"id": 2, "pct": 50, "price": 55000, "order_id": null, "status": "pending"}
  ],
  "max_slippage_bps": 20,
  "status": "pending"
}
```

**3. Save plan to Supabase + local cache**

**4. Pre-trade slippage estimate**
- Fetch L2 orderbook: `POST /info {"type": "l2Book", "coin": "BTC", "nSigFigs": 4}`
- Walk the book for the full tranche 1 size
- Calculate price impact: if market impact > max_slippage_bps → alert Greg, await confirmation

**5. Execute Tranche 1**
```python
# Market buy via hyperliquid-python-sdk
result = exchange.order(
    "BTC",
    is_buy=True,
    sz=0.04,
    limit_px=None,        # market = Ioc with high limit
    order_type={"limit": {"tif": "Ioc"}},
    slippage=0.002        # 0.2% slippage tolerance
)
```
- Record `order_id` to plan
- Telegram: "📋 Execution plan active: BTC Long | Tranche 1 @ market"

**6. Start WebSocket stream (if not already running)**
- Subscribe to `userEvents` on `wss://api.hyperliquid.xyz/ws`
- Filter for fills on BTC

**7. On Tranche 1 fill detected (via WebSocket)**
- Calculate slippage: `(fill_px - mid_px) / mid_px * 10000`
- **IMMEDIATELY place SL for 100% of filled size**:
  ```python
  exchange.order("BTC", is_buy=False, sz=0.04, limit_px=None,
      order_type={"trigger": {"isMarket": True, "tpsl": "sl", "triggerPx": str(sl_price)}},
      reduce_only=True)
  ```
- Update Supabase: tranche 1 → `filled`, sl → `{order_id, covers_size: 0.04, status: "active"}`
- Place Tranche 2 and 3 limit orders
- Telegram: "✅ T1 filled @ 49,420 (slippage: 4 bps) | SL active @ 48,000 | T2/T3 limit orders placed"

**8. On Tranche 2 fill**
- Cancel existing SL order
- Place new SL covering total position (T1 + T2 size = 0.075)
- Update Supabase
- Telegram: "✅ T2 filled @ 49,105 | SL updated: now covers 0.075 BTC @ 48,000"

**9. On Tranche 3 fill**
- Cancel SL, place new covering full 0.1 BTC
- Place TP1 limit order (sell 50% at 52,000)
- Update plan status → `active` (all tranches filled)
- Telegram: "✅ Full position loaded | 0.1 BTC long avg @ 49,227 | SL: 48,000 | TP1: 52,000"

**10. On TP1 hit**
- Exit 50% (0.05 BTC)
- Cancel full-position SL
- Place new SL at breakeven (avg entry price) for remaining 0.05 BTC
- Place TP2 limit for remaining
- Telegram: "🟢 TP1 hit @ 52,000 | +5.6% on 50% | SL moved to breakeven | Riding remaining to 55k"

**11. On TP2 hit (or Greg closes manually)**
- Full exit
- Mark plan `closed`
- Update Supabase with realized P&L + avg slippage
- Telegram: "🏁 CLOSED: BTC Long | P&L: +8.2% | Avg slippage: 6 bps | Duration: 4h 22m"

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.hyperliquid.xyz/info` | POST | L2 orderbook (pre-trade estimate) |
| `https://api.hyperliquid.xyz/info` | POST | `clearinghouseState` (position verify) |
| `https://api.hyperliquid.xyz/exchange` | POST | Place order (signed EIP-712) |
| `https://api.hyperliquid.xyz/exchange` | POST | Cancel order |
| `wss://api.hyperliquid.xyz/ws` | WS | `userEvents` — real-time fills |
| `wss://api.hyperliquid.xyz/ws` | WS | `l2Book` — orderbook depth |

### Expected Inputs
- Approved trade proposal JSON (from WF-017 or direct)
- `HYPERLIQUID_PRIVATE_KEY` env (for signing)
- `HYPERLIQUID_WALLET_ADDRESS` env
- `SUPABASE_URL` + `SUPABASE_KEY` env

### Expected Outputs
- Active `execution_plan` in Supabase
- SL order on Hyperliquid covering 100% of position at all times
- Telegram messages at every state transition
- `fills` records in Supabase for every tranche

### Approval Gates

**[APPROVAL GATE — HARD STOP]**: Before any order placement:
1. `proposal.approved == True` — must be set by Greg
2. `position_size_pct <= 10` — never exceed Greg's single-position limit
3. `stop_loss defined` — no SL in proposal = reject, alert Greg
4. If slippage estimate > 20 bps: pause, alert Greg for confirmation

---

## Part 3: Secondary Workflows

### Stream Monitor (Background Daemon)

**Trigger**: Runs continuously while any execution plan is active
**Steps**:
1. Connect to `wss://api.hyperliquid.xyz/ws`
2. Subscribe to `userEvents` (fills, liquidations)
3. Subscribe to `l2Book` for active tickers (orderbook depth monitoring)
4. On fill event: route to active plan's fill handler
5. On liquidation warning: immediate Telegram: "🚨 LIQUIDATION WARNING — {ticker}"
6. Reconnect on disconnect (exponential backoff, max 30s)
7. Log all events to `memory/ws-stream.log`

**Output**: Real-time fill detection feeding execution workflow

### Close Position (Emergency / Greg Command)

**Trigger**: Greg command: "close BTC" or "emergency close all"
**Steps**:
1. Fetch all open positions via `/info clearinghouseState`
2. For each position to close: market sell (or buy for shorts) entire size
3. Cancel all open orders for that ticker (SL, TP, pending tranches)
4. Update Supabase: plan status → `cancelled`
5. Calculate realized P&L from fills
6. Telegram: "🔴 Closed {ticker} @ {price} | P&L: {result}"

**[APPROVAL GATE]**: Greg's explicit "close" command. For "emergency close all" — no confirmation needed, execute immediately.

### Slippage Report

**Trigger**: After every tranche fill; daily summary
**Steps**:
1. Calculate: `slippage_bps = abs(fill_px - mid_px_at_order) / mid_px * 10000`
2. Classify: < 5 bps = excellent, 5-20 = normal, > 20 = alert, > 50 = investigate
3. Log to Supabase `fills` table
4. If > `max_slippage_bps`: Telegram alert immediately
5. Daily summary (midnight): avg slippage across all fills, worst fill, best fill

**Output**: Slippage log + alerts + daily summary

### Scale In / Scale Out Manual Override

**Trigger**: Greg command mid-execution ("add 25% to BTC at 48,800")
**Steps**:
1. Parse: ticker, size or %, price (market or limit)
2. Add new tranche to existing plan
3. Recalculate average entry, update SL if needed
4. Execute order
5. Update Supabase plan

**Output**: Updated execution plan + new fill

### Edge Cases

- **Partial fill**: Tranche fills partially → place SL for filled amount immediately, wait for remainder, update SL when rest fills
- **SL order rejected** (insufficient margin): Telegram critical alert, retry with market SL, then alert Greg
- **WebSocket disconnects during active trade**: immediately fall back to polling `/info` every 30s until WS reconnects
- **Greg cancels mid-execution**: gracefully cancel all pending tranche orders, keep SL on filled portion, mark plan `partial`
- **Price gaps through SL**: log slippage, alert Greg with actual fill price vs SL trigger
- **Testnet vs mainnet**: env var `HYPERLIQUID_ENV=testnet|mainnet` controls base URL — ALWAYS start new skills on testnet

---

## Part 4: Tool Configuration

### Hyperliquid Python SDK

```bash
pip install hyperliquid-python-sdk
```

```python
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from eth_account import Account

# Setup
account = Account.from_key(os.environ["HYPERLIQUID_PRIVATE_KEY"])
info = Info(base_url="https://api.hyperliquid.xyz")
exchange = Exchange(account, base_url="https://api.hyperliquid.xyz")

# Place SL order
exchange.order(
    coin="BTC",
    is_buy=False,           # sell to close long
    sz=position_size,
    limit_px=None,
    order_type={"trigger": {"isMarket": True, "tpsl": "sl", "triggerPx": str(sl_price)}},
    reduce_only=True
)

# Cancel order
exchange.cancel(coin="BTC", oid=order_id)
```

### WebSocket Connection

```python
import websocket, json

def on_message(ws, msg):
    data = json.loads(msg)
    if data.get("channel") == "userEvents":
        for event in data["data"]["fills"]:
            handle_fill(event)

ws = websocket.WebSocketApp(
    "wss://api.hyperliquid.xyz/ws",
    on_message=on_message
)
ws.run_forever()

# Subscribe after connect
ws.send(json.dumps({
    "method": "subscribe",
    "subscription": {"type": "userEvents", "user": WALLET_ADDRESS}
}))
```

### Supabase Client

```python
from supabase import create_client
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

# Upsert plan
sb.table("execution_plans").upsert(plan_dict).execute()

# Log fill
sb.table("fills").insert(fill_dict).execute()
```

### Tool Config Table

| Tool | Base URL | Auth | Notes |
|------|----------|------|-------|
| HL Exchange | `https://api.hyperliquid.xyz/exchange` | EIP-712 private key signing | Use SDK — don't hand-roll signing |
| HL Info | `https://api.hyperliquid.xyz/info` | None | Public REST |
| HL Testnet | `https://api.hyperliquid-testnet.xyz` | Same private key works | Use for testing |
| HL WebSocket | `wss://api.hyperliquid.xyz/ws` | WS auth frame for `userEvents` | Reconnect on close |
| Supabase | `$SUPABASE_URL` | `$SUPABASE_KEY` | Check if already provisioned |

### MCP Server Availability

- No known Hyperliquid MCP server as of 2026-03-18 — use SDK + REST directly
- Check ClawHub for "hyperliquid" before first deploy

---

## Part 5: Scheduling & Automation

### Cron Jobs

| Name | Schedule | Skill | Mode | Delivery |
|------|----------|-------|------|----------|
| Stream Monitor | Always-on daemon | stream-monitor | isolated | none (alerts via WS) |
| Slippage Daily Summary | `0 0 * * *` midnight UTC | slippage-report | isolated | Telegram announce |
| Execution Plan Cleanup | `0 8 * * *` 8 AM UTC | cleanup-closed-plans | isolated | none |

### Heartbeat Tasks
- During active execution: verify WS is still connected every 60s
- If no WS event in 5m during active trade: switch to polling mode + alert Greg

### Trigger Patterns
- Trade proposals arrive via Telegram → trigger `receive-proposal` skill
- Greg approval confirmation → trigger `execute-plan` skill
- WebSocket fill events → real-time (no polling during execution)

---

## Part 6: Integration Points

### Cross-Domain Connections

- **← WF-017 Trade Proposal Builder** (main Sebastian): sends approved proposals to Apex
- **→ Portfolio Manager (Risk Guard)**: Safety net — Risk Guard's 15m SL check catches if Apex's SL fails
- **→ Charting (Chart Maker)**: After plan closes, can auto-generate equity curve for the trade
- **→ Back Tester (Quant)**: Closed execution data (slippage, actual fills) feeds backtest calibration

### Shared Tools or Data Sources

- Hyperliquid API: shared with Portfolio Manager and Back Tester
- Supabase: Apex writes `execution_plans` + `fills`; Portfolio Manager can read for context
- Telegram: all domains deliver to same bot

### Workflow Handoffs

1. WF-017 generates proposal → Greg approves → Apex receives proposal → execution begins
2. Apex closes trade → writes to `fills` + Supabase → trade journal picks up via WF-004
3. Risk Guard checks positions every 15m — serves as backup SL verification layer
4. Closed trade data from Supabase → feeds WF-005 backtester for strategy calibration

---

## Part 7: Patterns & Learnings

### Patterns That Work
- (Populated after first live run)

### Patterns To Avoid
- NEVER place Tranche 1 without a plan to immediately SL on fill
- NEVER use `market` order type for large size without checking L2 depth first
- NEVER cancel a SL before the replacement is confirmed accepted by the exchange
- NEVER use leverage > Greg's defined limit without explicit confirmation
- NEVER execute on mainnet before testnet validation

### Known Issues
- Hyperliquid orders require coin index (integer), not symbol string — use `info.meta()` to resolve "BTC" → coin index
- `clearinghouseState` sizeInEther vs szDecimals: normalize carefully per asset
- WebSocket auth for `userEvents` requires sending a signed auth frame (different from REST signing)
- Partial fills from limit orders come as multiple `userEvents` messages — aggregate before logging

### Tips
- Start every new ticker on testnet (`https://api.hyperliquid-testnet.xyz`) — same keys work
- Use `reduce_only=True` on all SL and TP orders to prevent accidentally adding to position
- Supabase realtime subscriptions can mirror fill events to Mission Control dashboard (real-time position view)
- Keep WS connection alive with ping/pong — HL closes idle WS after 30s of no messages
