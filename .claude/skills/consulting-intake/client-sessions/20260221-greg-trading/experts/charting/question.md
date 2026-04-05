---
type: expert-file
parent: "[[charting/_index]]"
file-type: command
command-name: question
tags: [expert-file, command, read-only]
---

# Charting Expert - Question Mode

> Answer questions about chart generation workflows without making any changes.

## Purpose

Query chart generation processes, indicator configuration, and delivery setup without modifying any files.

## Allowed Tools
`Read, Glob, Grep, Bash(read-only)`

## Question Categories

### 1. Chart Generation Questions
**Examples**:
- "How do I generate a chart for BTC on the 4-hour?"
- "What indicators are available?"
- "How long does chart generation take?"

**Resolution**: Read expertise.md Part 2

### 2. Equity Curve Questions
**Examples**:
- "How is the equity curve chart triggered?"
- "What does the drawdown overlay show?"
- "Which backtest data format does generate-equity-curve expect?"

**Resolution**: Read expertise.md Part 3

### 3. Scheduling Questions
**Examples**:
- "Can charts be generated automatically?"
- "How do I trigger a chart from a volume spike alert?"

**Resolution**: Read expertise.md Part 5

### 4. Tool/API Questions
**Examples**:
- "What libraries are needed for chart generation?"
- "What's the Telegram sendPhoto endpoint?"
- "What's the Hyper Liquid candleSnapshot format?"

**Resolution**: Read expertise.md Part 4

### 5. Integration Questions
**Examples**:
- "How does the back-tester trigger equity curves?"
- "How does monitor-feeds attach charts to alerts?"

**Resolution**: Read expertise.md Part 6

### 6. Troubleshooting Questions
**Examples**:
- "Why did chart generation fail?"
- "What if the image is too large for Telegram?"
- "Why is the ticker not found?"

**Resolution**: Read expertise.md Part 7
