---
type: expert-file
parent: "[[back-tester/_index]]"
file-type: command
command-name: self-improve
tags: [expert-file, command, learning, back-tester]
---

# Back Tester Expert - Self-Improve

> Update expertise after backtesting runs. This is how Quant gets smarter.

## Purpose

After a backtest or optimization run, analyze the outcome and update expertise.md with new quantitative patterns and learnings.

## Allowed Tools
`Read, Edit, Glob, Grep, Bash`

## Workflow

### Step 1: Gather Results
1. Read latest backtest results from `memory/backtests/`
2. Read optimization results if applicable
3. Read `memory/dataset-scout/` for recent finds
4. Check if live trades match backtested expectations
5. Read current `expertise.md` Part 7

### Step 2: Analyze Outcome

| Check | Question |
|-------|----------|
| **Backtest accuracy** | Did live paper/live trading match backtest expectations? |
| **Overfitting** | Did PROMISING backtests underperform in live trading? |
| **Data quality** | Were there gaps or anomalies in historical data? |
| **Fee accuracy** | Were fee estimates realistic? |
| **Verdict calibration** | Are PROMISING verdicts actually finding good strategies? |
| **Overnight efficiency** | Did nightly backtests complete within the 2 AM window? |

### Step 3: Update expertise.md Part 7

Add new entries with date tags:

#### Patterns That Work
```markdown
- {date}: {quantitative pattern} — {why it works}
```

#### Patterns To Avoid
```markdown
- {date}: {quantitative pattern} — {what went wrong}
```

#### Known Issues
```markdown
- {date}: {data or API issue} — {workaround}
```

#### Tips
```markdown
- {date}: {backtesting tip from experience}
```

### Step 4: Update Verdict Thresholds (if needed)
If backtest verdicts are miscalibrated:
1. Document current vs. proposed thresholds
2. Update in `run-backtest` SKILL.md
3. Note rationale in expertise.md Part 7

### Step 5: Update Timestamp
Set `last_updated` in expertise.md frontmatter to today's date.

## Report Format

```markdown
## Self-Improve: Back Tester

### Run Analyzed
- Strategy: {name}
- Date: {date}
- Outcome: {success|partial|failed}

### Backtest vs. Reality
- Backtest Sharpe: {value}
- Live paper trading Sharpe: {value} (if available)
- Verdict: {calibrated|needs_adjustment}

### Expertise Updates
- Part 7 Patterns That Work: +{N} entries
- Part 7 Patterns To Avoid: +{N} entries
- Part 7 Tips: +{N} entries

### Cross-Domain Notes
- portfolio-manager: {any live trading patterns to monitor}
- charting: {any visualization improvements needed}
```
