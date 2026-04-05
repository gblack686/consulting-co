---
type: expert-file
parent: "[[back-tester/_index]]"
file-type: command
command-name: question
tags: [expert-file, command, read-only]
---

# Back Tester Expert - Question Mode

> Answer questions about backtesting workflows and quantitative analysis without making any changes.

## Purpose

Query backtesting processes, strategy configuration, and dataset library without modifying any files.

## Allowed Tools
`Read, Glob, Grep, Bash(read-only)`

## Question Categories

### 1. Backtest Workflow Questions
**Examples**:
- "How does the backtest engine work?"
- "What fees are simulated in the backtest?"
- "What metrics does a backtest report include?"

**Resolution**: Read expertise.md Part 2

### 2. Optimization / Dataset Questions
**Examples**:
- "How does the parameter optimizer work?"
- "What's the out-of-sample validation process?"
- "What data sources has the dataset scout found?"

**Resolution**: Read expertise.md Part 3 + `memory/dataset-scout/`

### 3. Scheduling Questions
**Examples**:
- "When does the nightly backtest run?"
- "How often does the dataset scout run?"
- "Can I run a backtest on-demand?"

**Resolution**: Read expertise.md Part 5

### 4. Tool/API Questions
**Examples**:
- "What Hyper Liquid endpoint provides historical candles?"
- "What's the candleSnapshot request format?"
- "What timeframes are available?"

**Resolution**: Read expertise.md Part 4

### 5. Integration Questions
**Examples**:
- "How do backtests flow into the charting domain?"
- "How do I add a new strategy file?"
- "How does the trade journal feed back-tester?"

**Resolution**: Read expertise.md Part 6

### 6. Troubleshooting Questions
**Examples**:
- "Why did a backtest return 0 trades?"
- "What does 'AVOID' verdict mean?"
- "How do I handle overfitting warnings?"

**Resolution**: Read expertise.md Part 7
