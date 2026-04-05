---
type: expert-file
parent: "[[back-tester/_index]]"
file-type: command
command-name: plan_build_improve
model: sonnet
tags: [expert-file, command, workflow, back-tester]
---

# Back Tester Expert - Plan Build Improve

> Full ACT-LEARN-REUSE workflow for backtesting and quantitative analysis changes.

## Purpose

Execute the complete plan-build-improve cycle for a back-tester change or addition.

## Allowed Tools
`Task, TaskOutput, Read, Write, Edit, Glob, Grep, Bash`

## Workflow

```
ACT → LEARN → REUSE

Step 1: Plan (ACT)  — Create TAC-informed implementation plan
Step 2: Build (ACT) — Execute the implementation
Step 3: Self-Improve (LEARN) — Update expertise with new patterns
```

### Phase 1: PLAN (ACT)

1. Load `expertise.md` for current backtesting state
2. Analyze request — is this a new strategy, a new data source, or a workflow improvement?
3. Classify by TAC pattern (see plan.md)
4. If research needed:
   - Dispatch browser agent for data source API docs
   - Dispatch YouTube agent for strategy research
5. Write plan to `specs/back-tester-{feature}.md`
6. **[CHECKPOINT]**: Review before building — especially for new strategies going to paper trading

### Phase 2: BUILD (ACT)

1. Create or modify strategy files in `~/.openclaw/strategies/{name}/strategy.py`
   - Implement `generate_signals(df, params)` interface
   - Include parameter validation
2. Create or modify SKILL.md files if new workflow needed
3. For new data sources:
   - Test API connection
   - Validate data quality (gaps? format issues?)
   - Cache to parquet
4. Run a test backtest on 3 months of data — verify no errors
5. Verify equity curve flows to charting agent correctly
6. Update data cache paths in TOOLS.md if new sources added

### Phase 3: SELF-IMPROVE (LEARN)

After successful build:

1. Read backtest results from `memory/backtests/`
2. Note strategy performance characteristics
3. Update `expertise.md` Part 7 with new patterns
4. If new data source added: update Part 4 with API details
5. Update `last_updated` timestamp

### Quality Gate

Before marking complete:
- [ ] Strategy file implements correct interface (`generate_signals`)
- [ ] Backtest ran without errors on test period
- [ ] Out-of-sample validation included
- [ ] Equity curve data format compatible with charting agent
- [ ] No hardcoded API keys
- [ ] expertise.md updated with new strategy info

## Report Format

```markdown
## Back Tester PBI Complete

### Strategy/Feature Built
- Name: {name}
- Type: {trend-following|mean-reversion|momentum|other}

### Backtest Results (Preview)
- Sharpe: {value}
- Max DD: {value}%
- Verdict: {PROMISING|NEEDS_WORK|AVOID}

### Data Sources Added
- {source}: {data_type}

### Expertise Updated
- Part {N}: {what was added}

### Score: {score}/100
```
