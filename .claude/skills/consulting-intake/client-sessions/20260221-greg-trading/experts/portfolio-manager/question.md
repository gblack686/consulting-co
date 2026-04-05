---
type: expert-file
parent: "[[portfolio-manager/_index]]"
file-type: command
command-name: question
tags: [expert-file, command, read-only]
---

# Portfolio Manager Expert - Question Mode

> Answer questions about portfolio risk management and trade journaling without making any changes.

## Purpose

Query position monitoring, risk management logic, and trade journal without modifying any files.

## Allowed Tools
`Read, Glob, Grep, Bash(read-only)`

## Question Categories

### 1. Position Monitoring Questions
**Examples**:
- "How does the position monitor work?"
- "What triggers a stop-loss alert?"
- "What's the drawdown threshold for a critical alert?"

**Resolution**: Read expertise.md Part 2

### 2. Risk Management Questions
**Examples**:
- "How are stop-loss recommendations calculated?"
- "What is a trailing stop rule?"
- "How is portfolio-level risk assessed?"

**Resolution**: Read expertise.md Part 3

### 3. Scheduling Questions
**Examples**:
- "How often does position monitoring run?"
- "When does the weekly trade journal fire?"

**Resolution**: Read expertise.md Part 5

### 4. Tool/API Questions
**Examples**:
- "What Hyper Liquid API endpoint gets positions?"
- "How do I check open orders for stop-losses?"
- "What's the difference between mainnet and testnet URLs?"

**Resolution**: Read expertise.md Part 4

### 5. Integration Questions
**Examples**:
- "How does the portfolio manager connect to back-tester?"
- "How do Discord signals feed into trade context?"

**Resolution**: Read expertise.md Part 6

### 6. Troubleshooting Questions
**Examples**:
- "Why did the position monitor miss a stop-loss alert?"
- "What happens if Hyper Liquid API is down?"
- "How do I debug duplicate trade journal entries?"

**Resolution**: Read expertise.md Part 7
