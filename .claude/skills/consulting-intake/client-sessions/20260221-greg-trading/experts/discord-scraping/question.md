---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: command
command-name: question
tags: [expert-file, command, read-only]
---

# Discord & Scraping Expert - Question Mode

> Answer questions about Discord scraping and signal pipeline workflows without making any changes.

## Purpose

Query signal pipeline production processes, tool configurations, and scheduling without modifying any files.

## Allowed Tools
`Read, Glob, Grep, Bash(read-only)`

## Question Categories

### 1. Signal Scraping Questions
**Examples**:
- "How does the Discord scrape work?"
- "What are the steps for parsing a trade signal?"
- "What's the signal quality scoring formula?"

**Resolution**: Read expertise.md Part 2

### 2. Feed Monitor / Alert Questions
**Examples**:
- "How does the volume spike alert work?"
- "What conditions trigger an indicator alert?"
- "Where are the alert rules configured?"

**Resolution**: Read expertise.md Part 3 + `memory/feed-rules.json`

### 3. Scheduling Questions
**Examples**:
- "When does the Discord scrape run?"
- "What time does the morning brief fire?"
- "How do I change the quiet hours?"

**Resolution**: Read expertise.md Part 5

### 4. Tool/API Questions
**Examples**:
- "What Discord API endpoint does the scraper use?"
- "How does YouTube authentication work?"
- "What's the Hyper Liquid market data endpoint?"

**Resolution**: Read expertise.md Part 4

### 5. Integration Questions
**Examples**:
- "How does Discord scraping connect to the portfolio manager?"
- "What happens after a volume spike is detected?"
- "How do signals flow into the morning brief?"

**Resolution**: Read expertise.md Part 6

### 6. Troubleshooting Questions
**Examples**:
- "Why are no signals being parsed from Discord?"
- "What happens when Discord rate limits us?"
- "Why did the morning brief fail to send?"

**Resolution**: Read expertise.md Part 7
