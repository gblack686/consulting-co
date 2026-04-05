---
type: expert-file
parent: "[[charting/_index]]"
file-type: command
command-name: plan
tags: [expert-file, command, planning]
---

# Charting Expert - Plan Mode

> Create TAC-informed implementation plans for chart generation changes.

## Purpose

Analyze a requested change or addition to charting workflows and produce an implementation plan.

## Allowed Tools
`Read, Write, Glob, Grep, Bash`

## Workflow

### Step 1: Load Context
1. Read `expertise.md` for current charting state
2. Read `_index.md` for available commands
3. Check `memory/chart-requests.json` for patterns in what Greg requests

### Step 2: Analyze Request
1. What new chart type or indicator is needed?
2. Does this require new data sources or new Python libraries?
3. Is delivery changing? (Telegram → dashboard? file output?)
4. Are there dependencies on other domains?

### Step 3: Classify by TAC Pattern

| If the request involves... | Use TAC Pattern |
|---------------------------|-----------------|
| A new repeatable chart type | TAC-6: One Agent One Purpose |
| Chart automatically attached to alerts | TAC-5: Feedback Loops |
| Multi-chart comparison report | TAC-3: Template Engineering |
| Dynamic chart based on portfolio state | TAC-5 + TAC-9: Context Engineering |

### Step 4: Research (if needed)
- **Chart library research**:
  ```
  Task(subagent_type: "playwright-bowser-agent",
       prompt: "Research mplfinance or plotly for candlestick charts with {specific_feature}. Find examples and configuration options.")
  ```

### Step 5: Output Plan
Write to `specs/charting-{feature}.md`:

```markdown
# Plan: {feature_name}

## TAC Pattern: {pattern_name}
## Affected Files: {file_list}
## New Libraries: {library_list}

## Implementation Steps
1. {step}
2. {step}

## Validation Criteria
- Chart renders without errors
- Image size < 10 MB for Telegram
- Correct indicators displayed
- Dark theme applied

## Estimated Complexity: {low|medium|high}
```
