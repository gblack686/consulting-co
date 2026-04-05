---
type: expert-file
parent: "[[charting/_index]]"
file-type: command
command-name: self-improve
tags: [expert-file, command, learning, charting]
---

# Charting Expert - Self-Improve

> Update expertise after chart generation runs. This is how Chart Maker gets better at visualizing data.

## Purpose

After chart generation runs, analyze the outcome and update expertise.md with rendering patterns and delivery learnings.

## Allowed Tools
`Read, Edit, Glob, Grep, Bash`

## Workflow

### Step 1: Gather Results
1. Read `memory/chart-requests.json` for recent chart requests
2. Note which chart types Greg requests most often
3. Check for any errors in recent chart generation runs
4. Read current `expertise.md` Part 7

### Step 2: Analyze Outcome

| Check | Question |
|-------|----------|
| **Rendering quality** | Did charts render clearly? Good enough for trade decisions? |
| **Request patterns** | What tickers and timeframes does Greg request most? |
| **Delivery reliability** | Any Telegram delivery failures? Image size issues? |
| **Speed** | How long does chart generation take? Acceptable? |
| **Integration quality** | Did equity curves from back-tester render correctly? |
| **Indicator accuracy** | Did indicators calculate correctly vs. manual check? |

### Step 3: Update expertise.md Part 7

#### Patterns That Work
```markdown
- {date}: {rendering pattern} — {why it works}
```

#### Patterns To Avoid
```markdown
- {date}: {rendering issue} — {what went wrong}
```

#### Known Issues
```markdown
- {date}: {issue} — {workaround}
```

#### Tips
```markdown
- {date}: {chart generation tip}
```

### Step 4: Update Timestamp
Set `last_updated` in expertise.md frontmatter to today's date.

### Step 5: Cache Optimization
If the same tickers/timeframes are requested repeatedly:
1. Note hot tickers in expertise.md Part 7 Tips
2. Consider pre-caching data for frequently requested charts
3. Document cache strategy

## Report Format

```markdown
## Self-Improve: Charting

### Charts Analyzed
- Total generated: {count}
- Most requested: {ticker} {timeframe}
- Error rate: {pct}%

### Expertise Updates
- Part 7 Patterns That Work: +{N} entries
- Part 7 Tips: +{N} entries

### Delivery Issues
- {any Telegram or rendering issues}

### Cross-Domain Notes
- back-tester: {equity curve quality feedback}
- discord-scraping: {chart quality on volume spike alerts}
```
