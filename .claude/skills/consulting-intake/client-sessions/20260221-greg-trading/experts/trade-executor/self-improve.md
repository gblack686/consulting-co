---
type: expert-file
parent: "[[trade-executor/_index]]"
file-type: command
command-name: self-improve
model: sonnet
tags: [expert-file, command, self-improve, trade-executor]
---

# Trade Executor Expert — Self-Improve Mode

> Update expertise after live runs. Learn from fills, slippage, and execution patterns.

## Purpose

After each real execution (testnet or mainnet), update the trade executor expert with observed patterns, slippage benchmarks, and edge cases encountered.

## Allowed Tools
`Read, Write, Edit, Glob, Grep, Bash(read-only)`

## Trigger

Run after:
- First live execution of a new ticker
- Any execution with slippage > 20 bps
- Any SL-related incident (failed placement, gap-through, etc.)
- Weekly review of `memory/slippage-log.json`

## Workflow

### Step 1: Gather Evidence

Read:
- `memory/fills/{YYYY-MM-DD}.json` — fills from recent runs
- `memory/slippage-log.json` — all slippage records
- `memory/ws-stream.log` — WebSocket events (last 500)
- Supabase `execution_plans` — closed plans with P&L
- Any Telegram messages from Apex during the run (check memory)

### Step 2: Analyze

Questions to answer:
1. What was the average slippage per tranche? Per order type (market vs limit)?
2. Was the WebSocket fill detection fast enough? Any delays?
3. Did SL always get placed before the next event? Any gaps?
4. Did any tranche fail to fill? Why?
5. Were TP levels hit? What was the outcome?
6. Any edge cases encountered not covered in expertise.md?

### Step 3: Update expertise.md

Update **Part 7: Patterns & Learnings**:
- Move verified patterns from "pending" to "Patterns That Work"
- Add new "Patterns To Avoid" from any failures
- Update "Known Issues" with new edge cases
- Update "Tips" with new practical knowledge

**Specific metrics to record:**
```
Slippage benchmarks (add after first 10 trades):
- Average slippage by order type: market={bps}, limit={bps}
- 95th percentile slippage: {bps}
- Best time of day for entry (low slippage): {time UTC}
- Worst time (high slippage, low liquidity): {time UTC}
```

### Step 4: Update Thresholds (if warranted)

If observed slippage consistently differs from defaults:
- Update `max_slippage_bps` recommendation in expertise.md Part 2
- Note which tickers need higher/lower thresholds (BTC = tight market, alt = wider)

### Step 5: Validate expertise.md Still Complete

Confirm all 7 parts present and up to date:
- [ ] Part 1: Architecture current
- [ ] Part 2: Primary workflow unchanged or updated
- [ ] Part 3: Edge cases reflect observed issues
- [ ] Part 4: Tool config current (SDK version, API URLs)
- [ ] Part 5: Cron/heartbeat schedule correct
- [ ] Part 6: Integration points still valid
- [ ] Part 7: Patterns updated with new learnings

## Output

```
✅ Self-improve complete

Learnings added:
- Patterns That Work: {N new}
- Patterns To Avoid: {N new}
- Known Issues: {N new}
- Slippage benchmarks: {updated|first run}

expertise.md last_updated: {today}
```
