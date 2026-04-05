---
type: expert-file
parent: "[[back-tester/_index]]"
file-type: command
command-name: plan
tags: [expert-file, command, planning]
---

# Back Tester Expert - Plan Mode

> Create TAC-informed implementation plans for backtesting and quantitative analysis changes.

## Purpose

Analyze a requested change or addition to backtesting workflows and produce an implementation plan.

## Allowed Tools
`Read, Write, Glob, Grep, Bash`

## Workflow

### Step 1: Load Context
1. Read `expertise.md` for current back-tester state
2. Read `_index.md` for available commands and tools
3. Check `memory/backtests/` for relevant prior backtest results

### Step 2: Analyze Request
1. What is being asked? (new strategy? new metric? new data source? optimization?)
2. Which existing workflows are affected?
3. Is new historical data needed?
4. Are there dependencies on other domains? (especially charting for equity curves)

### Step 3: Classify by TAC Pattern

| If the request involves... | Use TAC Pattern |
|---------------------------|-----------------|
| A new repeatable backtest run | TAC-6: One Agent One Purpose |
| Dataset integration pipeline | TAC-5: Feedback Loops |
| Strategy research from multiple sources | TAC-6 + TAC-9: Context Engineering |
| Multi-strategy comparison report | TAC-3: Template Engineering |
| Learning from live trade outcomes | TAC-10: Self-Improving Prompts |
| Automated nightly research cycle | TAC-7: Zero-Touch Engineering |

### Step 4: Research (if needed)
- **New data source API research**:
  ```
  Task(subagent_type: "playwright-bowser-agent",
       prompt: "Research the {data_source} API for trading data. Find: data types available, API endpoints, auth, rate limits, pricing/free tier.")
  ```
- **Strategy tutorial research**:
  ```
  Task(subagent_type: "youtube-transcript-agent",
       prompt: "Search for '{strategy_name} trading strategy backtest'. Extract: key parameters, entry/exit rules, typical performance metrics.")
  ```

### Step 5: Output Plan
Write to `specs/back-tester-{feature}.md`:

```markdown
# Plan: {feature_name}

## TAC Pattern: {pattern_name}
## Affected Files: {file_list}
## New Strategy Files: {strategy_list}
## New Data Sources: {data_source_list}

## Implementation Steps
1. {step}
2. {step}

## Validation Criteria
- Backtest produces metrics without errors
- Out-of-sample validation passes
- Equity curve generated successfully

## Estimated Complexity: {low|medium|high}
```
