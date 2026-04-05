---
type: expert-file
parent: "[[trade-executor/_index]]"
file-type: command
command-name: plan
model: sonnet
tags: [expert-file, command, planning, trade-executor]
---

# Trade Executor Expert — Plan Mode

> Create an implementation plan for a trade executor change without building yet.

## Purpose

Design and document a change to execution logic, SL rules, scale-in strategy, or Supabase schema. Produces a spec file for review before any code is written.

## Allowed Tools
`Read, Write, Glob, Grep, Bash(read-only)`

## Critical Constraint

This domain places real orders on Hyperliquid with real capital. Every plan must specify:
1. **Testnet validation steps** — before any mainnet change
2. **Rollback procedure** — how to undo if something breaks
3. **SL coverage impact** — does this change ever leave a position without a SL?

## Workflow

### Step 1: Load Context
1. Read `expertise.md` — current execution state
2. Read `_index.md` — active skills and their status
3. If the plan involves new API calls: fetch current Hyperliquid docs from `https://hyperliquid.gitbook.io/hyperliquid-docs/`
4. Read existing related SKILL.md files in Greg's workspace

### Step 2: Analyze Request
- What is changing? (new skill / modify existing / new config)
- Which tranches or order types are affected?
- Does this touch SL placement logic? (highest risk — extra scrutiny)
- Does this change Supabase schema? (migration needed?)
- What is the testnet test scenario?

### Step 3: Write Plan

Save to `specs/trade-executor-{feature}-plan.md`:

```markdown
## Trade Executor Plan: {feature}

### Objective
{what this plan achieves}

### Files to Create/Modify
| File | Action | Why |
|------|--------|-----|
| {path} | create/modify | {reason} |

### SL Coverage Impact
{does this change affect stop-loss placement? how?}

### Supabase Schema Changes
{any new tables or columns? migration SQL}

### Testnet Test Scenario
1. {step}
2. {step}
Confirm: {what must be true after test}

### Rollback
{how to revert if something goes wrong}

### Acceptance Criteria
- [ ] {criterion}
```

### Step 4: Review Checkpoint

**STOP before building if**:
- SL placement order changes in any way
- New order types are introduced
- Position sizing calculations are modified
- Supabase schema breaks existing data

For any of the above: write plan → present to Greg → explicit approval before building.

## Output

```
✅ Plan complete: specs/trade-executor-{feature}-plan.md
   Impact: {summary of what changes}
   SL risk: {none|low|medium|high}
   Testnet steps: {count}
   Ready to build? {yes|needs review}
```
