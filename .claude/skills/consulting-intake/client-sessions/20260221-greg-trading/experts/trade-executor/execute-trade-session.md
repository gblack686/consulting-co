---
type: expert-file
parent: "[[trade-executor/_index]]"
file-type: session
command-name: execute-trade-session
model: sonnet
tags: [expert-file, session, trade-executor, execution]
---

# Trade Executor — Execute Trade Session

> Run or debug a trade execution. Load this when you need to actually execute a trade, monitor an active plan, or troubleshoot an execution issue.

## Purpose

Active execution session: receive an approved proposal, build the plan, execute tranches, maintain SL coverage, monitor fills.

## Allowed Tools
`Read, Write, Edit, Bash, Glob, Grep`

## Pre-Flight Checklist

Before running any execution:

```
[ ] HYPERLIQUID_PRIVATE_KEY set in environment
[ ] HYPERLIQUID_WALLET_ADDRESS set in environment
[ ] SUPABASE_URL + SUPABASE_KEY set in environment
[ ] TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID set
[ ] Testnet or mainnet? (HYPERLIQUID_ENV=testnet|mainnet)
[ ] hyperliquid-python-sdk installed (pip install hyperliquid-python-sdk)
[ ] Trade proposal has approved: true
```

## Session Modes

### Mode A: Execute New Proposal

**Input**: A trade proposal (from WF-017 or direct command)

1. Parse proposal → validate approval gate
2. Build execution plan (expertise.md Part 2, Steps 1-4)
3. Pre-trade slippage estimate (expertise.md Part 2, Step 4)
4. If slippage OK → execute Tranche 1
5. Start WebSocket stream monitor
6. Follow execution flow per expertise.md Part 2

### Mode B: Monitor Active Plan

**Input**: `plan_id` of active execution

1. Read plan from Supabase: `SELECT * FROM execution_plans WHERE plan_id = '{id}'`
2. Or read from `memory/execution-plans/{plan_id}.json`
3. Display current status: tranches filled, SL status, TP targets remaining
4. Verify SL order still active on Hyperliquid: `POST /info {"type": "openOrders", "user": "{wallet}"}`
5. If SL missing: immediately replace it (emergency SL placement)
6. Report status to Greg via Telegram

### Mode C: Emergency Close

**Input**: Greg command to close position

1. Fetch position: `POST /info {"type": "clearinghouseState", "user": "{wallet}"}`
2. For the specified ticker: note exact size
3. Cancel all open orders for ticker
4. Place market close order for full size (reduce_only=True)
5. Verify fill
6. Update Supabase plan status → cancelled
7. Alert Greg with P&L

## Key Code Snippets

### Place Market Order (Tranche 1)
```python
from hyperliquid.exchange import Exchange
from eth_account import Account
import os

account = Account.from_key(os.environ["HYPERLIQUID_PRIVATE_KEY"])
exchange = Exchange(account, base_url="https://api.hyperliquid.xyz")

# Market buy
result = exchange.market_open("BTC", is_buy=True, sz=0.04, slippage=0.002)
order_id = result["response"]["data"]["statuses"][0]["resting"]["oid"]
```

### Place Stop-Loss (after fill)
```python
# SL for long position (sell to exit)
result = exchange.order(
    "BTC",
    is_buy=False,
    sz=filled_size,           # 100% of position
    limit_px=None,
    order_type={"trigger": {"isMarket": True, "tpsl": "sl", "triggerPx": str(sl_price)}},
    reduce_only=True
)
sl_order_id = result["response"]["data"]["statuses"][0]["resting"]["oid"]
print(f"✅ SL placed: order {sl_order_id} @ {sl_price}")
```

### Cancel Existing SL (before placing updated one)
```python
cancel_result = exchange.cancel("BTC", sl_order_id)
assert cancel_result["status"] == "ok", f"Cancel failed: {cancel_result}"
```

### WebSocket Fill Detection
```python
import websocket, json, threading

WALLET = os.environ["HYPERLIQUID_WALLET_ADDRESS"]

def on_message(ws, msg):
    data = json.loads(msg)
    if data.get("channel") == "userEvents":
        fills = data.get("data", {}).get("fills", [])
        for fill in fills:
            if fill["coin"] == "BTC":
                handle_fill(fill)

def handle_fill(fill):
    fill_px = float(fill["px"])
    fill_sz = float(fill["sz"])
    print(f"Fill detected: {fill_sz} BTC @ {fill_px}")
    # IMMEDIATELY place SL
    place_sl(fill_sz, sl_price)

ws = websocket.WebSocketApp("wss://api.hyperliquid.xyz/ws", on_message=on_message)
thread = threading.Thread(target=ws.run_forever)
thread.daemon = True
thread.start()

# Subscribe after connect
import time; time.sleep(1)
ws.send(json.dumps({"method": "subscribe", "subscription": {"type": "userEvents", "user": WALLET}}))
```

### Supabase Plan Upsert
```python
from supabase import create_client
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

# Save/update plan
sb.table("execution_plans").upsert(plan_dict).execute()

# Log fill
sb.table("fills").insert({
    "fill_id": fill["tid"],
    "plan_id": plan_id,
    "tranche_id": tranche_id,
    "ticker": "BTC",
    "side": "buy",
    "size": float(fill["sz"]),
    "expected_px": mid_price_at_order,
    "fill_px": float(fill["px"]),
    "slippage_bps": abs(float(fill["px"]) - mid_price_at_order) / mid_price_at_order * 10000
}).execute()
```

## Status Report Format

After each tranche, Apex sends:

```
📋 APEX — BTC Long | Plan APEX-20260318-001

T1 ✅ 0.04 BTC @ 49,420 (4 bps slippage)
T2 ⏳ 0.035 BTC limit @ 49,000 [pending]
T3 ⏳ 0.025 BTC limit @ 48,755 [pending]

SL 🛡️ 0.04 BTC @ 48,000 [ACTIVE]
TP1 🎯 0.05 BTC @ 52,000 [pending]
TP2 🎯 0.05 BTC @ 55,000 [pending]

Avg entry: 49,420 | R:R remaining: 2.5
```

## Troubleshooting

| Problem | Check | Fix |
|---------|-------|-----|
| SL placement rejected | Account margin, position size | Reduce size, use market SL |
| WS no events after 5m | Connection alive? Auth frame sent? | Reconnect, resend subscribe |
| Fill not detected | WS subscribed to right ticker? | Check `userEvents` vs `userFills` |
| Order rejected "reduce only" | Position size mismatch | Refetch position size from `/info` |
| Supabase write fails | Check SUPABASE_URL and KEY | Fall back to local JSON cache |
| Wrong coin index | HL uses int index, not symbol | Fetch `info.meta()` to resolve "BTC" → index |
