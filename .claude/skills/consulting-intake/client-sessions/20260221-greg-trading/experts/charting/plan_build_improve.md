---
type: expert-file
parent: "[[charting/_index]]"
file-type: command
command-name: plan_build_improve
model: sonnet
tags: [expert-file, command, workflow, charting]
---

# Charting Expert - Plan Build Improve

> Full ACT-LEARN-REUSE workflow for charting changes.

## Purpose

Execute the complete plan-build-improve cycle for a charting change or addition.

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

1. Load `expertise.md` for current charting state
2. Analyze request — new indicator? new chart type? new trigger? new delivery?
3. Classify by TAC pattern (see plan.md)
4. If research needed: dispatch browser agent for charting library docs
5. Write plan to `specs/charting-{feature}.md`
6. **[CHECKPOINT]**: Review plan — charting is low-blast-radius but user-facing (Greg sees results)

### Phase 2: BUILD (ACT)

1. Modify `generate-chart/SKILL.md` or `generate-equity-curve/SKILL.md` as needed
2. For new indicators:
   - Add to indicator calculation section
   - Document formula in expertise.md Part 2
3. For new chart types:
   - Create new SKILL.md with clear trigger syntax
   - Document usage in _index.md OpenClaw Skills table
4. Test chart generation:
   - Generate test chart with BTC 1h (last 50 candles)
   - Verify image renders correctly
   - Verify image < 10 MB (Telegram limit)
   - Verify Telegram delivery (send to test channel if available)
5. Update `_index.md` OpenClaw Skills table with new skill

### Phase 3: SELF-IMPROVE (LEARN)

After successful build:

1. Review generated chart quality
2. Check if Greg's visual preferences are reflected (dark theme, clean layout)
3. Update `expertise.md` Part 7 with rendering patterns
4. Update `last_updated` timestamp

### Quality Gate

Before marking complete:
- [ ] Chart renders without Python errors
- [ ] Image size < 10 MB
- [ ] Dark theme applied
- [ ] Correct indicators shown
- [ ] Ticker context line included
- [ ] expertise.md still has all 7 parts

## Report Format

```markdown
## Charting PBI Complete

### Changes Made
- {file}: {what changed}

### Chart Types Available
- {chart_type}: triggered by {trigger}

### Test Chart Generated
- Ticker: {ticker}
- Timeframe: {tf}
- Result: {success|failed}
- Image size: {size}

### Expertise Updated
- Part {N}: {what was added}

### Score: {score}/100
```
