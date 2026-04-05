---
type: expert-file
parent: "[[trade-executor/_index]]"
file-type: command
command-name: question
tags: [expert-file, command, read-only]
---

# Trade Executor Expert — Question Mode

> Answer questions about trade execution, stop-loss management, WebSocket streaming, and execution plans without making any changes.

## Purpose

Query active execution plans, fill history, slippage data, and API logic without modifying any files or placing orders.

## Allowed Tools
`Read, Glob, Grep, Bash(read-only)`

## Question Categories

### 1. Execution Plan Questions
**Examples**:
- "What's the current execution plan for BTC?"
- "How does the tranche split work?"
- "What's the default scale-in split?"
- "How is average entry price calculated across tranches?"

**Resolution**: Read expertise.md Part 2 → Build Execution Plan section

### 2. Stop-Loss Coverage Questions
**Examples**:
- "When does the SL get placed after a fill?"
- "What happens to the SL when tranche 2 fills?"
- "How is the SL updated as position scales in?"
- "What's the SL order type on Hyperliquid?"

**Resolution**: Read expertise.md Part 2 Steps 7-9

### 3. Slippage Questions
**Examples**:
- "How is slippage calculated?"
- "What's the default slippage threshold?"
- "How do I read the slippage report?"
- "What happens if slippage exceeds the threshold before entry?"

**Resolution**: Read expertise.md Part 3 → Slippage Report section

### 4. WebSocket / Streaming Questions
**Examples**:
- "How does Apex detect fills in real-time?"
- "What happens if the WebSocket disconnects?"
- "What events does Apex subscribe to?"
- "How do I reconnect the stream?"

**Resolution**: Read expertise.md Part 2 Step 6 + Part 4 WebSocket section

### 5. API / SDK Questions
**Examples**:
- "How do I place a stop-loss on Hyperliquid?"
- "What's the difference between SL and trigger orders?"
- "How do I cancel an order?"
- "What does reduce_only do?"
- "How does EIP-712 signing work?"

**Resolution**: Read expertise.md Part 4 Tool Configuration

### 6. Supabase Questions
**Examples**:
- "What tables does Apex write to?"
- "How is the execution plan stored?"
- "What does a fill record look like?"

**Resolution**: Read expertise.md Part 1 → Supabase Tables section

### 7. Integration Questions
**Examples**:
- "How does a WF-017 proposal trigger Apex?"
- "What does Risk Guard check after Apex executes?"
- "How does trade data reach the back-tester?"

**Resolution**: Read expertise.md Part 6

### 8. Troubleshooting Questions
**Examples**:
- "SL order was rejected — what now?"
- "WebSocket disconnected during active trade — what happens?"
- "Tranche partially filled — how is SL handled?"
- "How do I test on Hyperliquid testnet?"

**Resolution**: Read expertise.md Part 3 Edge Cases + Part 7 Known Issues
