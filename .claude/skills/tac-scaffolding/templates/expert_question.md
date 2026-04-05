---
type: expert-file
file-type: command
command-name: "question"
domain: "{{DOMAIN}}"
human_reviewed: false
tags: [expert-file, command, read-only, {{DOMAIN}}]
---

# {{DOMAIN}} Expert - Question Mode

> Read-only command to query {{DOMAIN}} **without making any changes**.

## Purpose

Answer questions about {{DOMAIN}} without making any code changes.

## Question Categories

### Status & Health
- "Is {{DOMAIN}} running?"
- "What's the current state of {{DOMAIN}}?"

### Configuration
- "How is {{DOMAIN}} configured?"
- "What settings does {{DOMAIN}} use?"

### How-To
- "How do I set up {{DOMAIN}}?"
- "How do I troubleshoot {{DOMAIN}}?"

## Workflow

1. Parse the user's question
2. Load expertise from `expertise.md`
3. Search relevant code and config files
4. Synthesize answer from expertise + live state
5. Return structured response

## Report Format

```
## {{DOMAIN}} Answer

**Question**: {user's question}
**Confidence**: High / Medium / Low

### Answer
{Clear, actionable answer}

### Sources
- {File or doc referenced}
```
