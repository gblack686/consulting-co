---
type: expert-file
parent: "[[portfolio-manager/_index]]"
file-type: command
command-name: self-improve
tags: [expert-file, command, learning, portfolio-manager]
---

# Portfolio Manager Expert - Self-Improve

> Update expertise after portfolio management runs. This is how Sebastian becomes a better risk manager.

## Purpose

After a workflow execution, analyze the outcome and update expertise.md with new risk patterns and learnings.

## Allowed Tools
`Read, Edit, Glob, Grep, Bash`

## Workflow

### Step 1: Gather Results
1. Read latest position snapshots from `memory/portfolio-snapshots/`
2. Read `memory/trade-journal/trades.json` for recent closed trades
3. Read `memory/trade-journal/stats.json` for current stats
4. Check `memory/` for any alert history files
5. Read current `expertise.md` Part 7

### Step 2: Analyze Outcome

| Check | Question |
|-------|----------|
| **Alert accuracy** | Were stop-loss alerts correct? Any false positives? |
| **Missed positions** | Any positions that should have been flagged but weren't? |
| **Risk rule effectiveness** | Did the drawdown thresholds fire at the right times? |
| **Trade journal quality** | Were all closed trades captured correctly? |
| **Recommendation quality** | Did Greg find the risk recommendations useful? |
| **API reliability** | Any Hyper Liquid API failures or stale data issues? |

### Step 3: Update expertise.md Part 7

Edit `expertise.md` to add new entries:

#### Patterns That Work
```markdown
- {date}: {risk pattern} — {why it works}
```

#### Patterns To Avoid
```markdown
- {date}: {risk pattern} — {what went wrong}
```

#### Known Issues
```markdown
- {date}: {issue} — {workaround}
```

#### Tips
```markdown
- {date}: {risk management tip}
```

### Step 4: Update Timestamp
Set `last_updated` in expertise.md frontmatter to today's date.

### Step 5: Threshold Review
If risk thresholds need adjustment based on Greg's feedback:
1. Document current vs. proposed thresholds in Part 7 Tips
2. Update thresholds in monitor-positions SKILL.md
3. Note the rationale for the change

## Report Format

```markdown
## Self-Improve: Portfolio Manager

### Run Analyzed
- Command: {command_name}
- Date: {date}
- Outcome: {success|partial|failed}

### Expertise Updates
- Part 7 Patterns That Work: +{N} entries
- Part 7 Patterns To Avoid: +{N} entries
- Part 7 Known Issues: +{N} entries

### Threshold Changes
- {threshold}: {old} → {new} ({reason})

### Cross-Domain Notes
- back-tester: {any trade outcome patterns worth backtesting}
```
