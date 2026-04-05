---
type: expert-file
parent: "[[trade-executor/_index]]"
file-type: command
command-name: plan_build_improve
model: sonnet
tags: [expert-file, command, workflow, trade-executor]
---

# Trade Executor Expert — Plan Build Improve

> Full ACT-LEARN-REUSE workflow for trade execution changes.

## Purpose

Execute the complete plan-build-improve cycle for any trade executor change: new skills, SL rule updates, scale-in strategy changes, Supabase schema migrations.

## Allowed Tools
`Task, TaskOutput, Read, Write, Edit, Glob, Grep, Bash`

## Hard Constraints

1. **ALWAYS start on testnet** (`https://api.hyperliquid-testnet.xyz`) — never test on mainnet first
2. **NEVER modify SL logic without explicit testnet validation** — a SL bug = real capital at risk
3. **ALWAYS use `reduce_only=True`** on SL and TP orders
4. **ALWAYS verify Supabase writes** before going live — a failed plan save means no execution state
5. **Rollback plan required** before building any schema migration

## Workflow

```
PLAN → BUILD → TESTNET VALIDATE → MAINNET APPLY → SELF-IMPROVE
```

### Phase 1: PLAN (ACT)

1. Read `expertise.md` for current state
2. Read any related SKILL.md files in Greg's workspace
3. Identify what's changing and blast radius
4. Classify: new-skill | modify-existing | schema-migration | config-change
5. If API uncertainty: fetch Hyperliquid docs
6. Write plan to `specs/trade-executor-{feature}-plan.md`
7. Document: files to change, SL impact, testnet steps, rollback

**[CHECKPOINT]**: Does this touch SL placement? If yes — plan must be reviewed by Greg before Phase 2.

### Phase 2: BUILD (ACT)

1. Create/modify SKILL.md files per plan
   - metadata: single-line JSON
   - never hardcode private keys, wallet addresses
   - "[APPROVAL GATE]" on any section that places orders
   - document env vars used
2. Update Supabase schema if needed (write migration SQL to `memory/migrations/`)
3. Update `_index.md` skill table with new skills

### Phase 3: TESTNET VALIDATE (ACT)

**Required for ALL changes that touch order logic:**

1. Set `HYPERLIQUID_ENV=testnet` in agent environment
2. Run the skill against testnet with a small test trade (e.g. 0.001 BTC)
3. Verify checklist:
   - [ ] Tranche 1 order placed successfully
   - [ ] Fill detected via WebSocket within 30s
   - [ ] SL placed immediately after fill
   - [ ] SL covers 100% of filled position
   - [ ] Slippage logged to Supabase
   - [ ] Telegram alert fired
   - [ ] Plan status updated in Supabase
4. If any check fails: debug and retest before proceeding

### Phase 4: MAINNET APPLY (ACT)

After testnet passes:
1. Set `HYPERLIQUID_ENV=mainnet`
2. Document mainnet activation in `expertise.md` Part 7
3. Update cron/heartbeat config if scheduling changed

### Phase 5: SELF-IMPROVE (LEARN)

1. Run skill in practice (or review testnet run)
2. Document what worked / what didn't in `expertise.md` Part 7
3. Update slippage benchmarks if new data
4. Note any edge cases encountered

### Quality Gate

- [ ] All planned files created/modified
- [ ] No hardcoded keys or wallet addresses
- [ ] Testnet validated: all 5 SL checks passed
- [ ] Supabase schema migration documented
- [ ] "[APPROVAL GATE]" present on all order-placing sections
- [ ] `expertise.md` updated with learnings
- [ ] `_index.md` skill table current

## Report Format

```markdown
## Trade Executor PBI Complete

### Changes Made
- {file}: {what changed}

### SL Coverage Verified
- Testnet SL test: {pass|fail}
- SL placed within: {N} ms of fill detection

### Testnet Validation
- Result: {pass|fail}
- Slippage observed: {bps} bps
- Fill detection latency: {ms}

### Expertise Updated
- Part {N}: {what was added}

### Score: {score}/100
```
