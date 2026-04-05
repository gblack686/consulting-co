---
type: expert-file
parent: "[[bowser/_index]]"
file-type: command
command-name: "question"
human_reviewed: false
tags: [expert-file, command, read-only, bowser]
---

# Bowser Expert - Question Mode

> Read-only command to query browser automation patterns without making changes.

## Purpose
Answer questions about browser automation backends, YouTube extraction, QA workflows, and MCP Chrome DevTools **without making any code changes**.

## Usage
```
/experts:bowser:question [question]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Task`

---

## Workflow

1. **Receive question** from user
2. **Read expertise.md** for bowser mental model
3. **Search codebase** for existing bowser commands/workflows if relevant
4. **Answer** with pattern reference, code example, and source

---

## Question Categories

### Category 1: Backend Questions
"Which browser backend should I use?", "What's the difference between claude-bowser and playwright-bowser?"

**Resolution**: Reference Part 1 (Two Browser Backends) in expertise.md

### Category 2: YouTube Questions
"How do I extract a YouTube transcript?", "Why does the transcript panel hang?", "How does Apify work?"

**Resolution**: Reference Part 3 (YouTube Transcript Extraction) with decision tree and Apify pattern

### Category 3: QA and Testing Questions
"How do I run UI tests?", "How are user stories structured?", "How does parallel QA work?"

**Resolution**: Reference Part 6 (QA and UI Review) for YAML format and architecture

### Category 4: Browser Quirk Questions
"Why does YouTube navigation timeout?", "Why can't I use claude --chrome?", "How do I get full URLs from YouTube?"

**Resolution**: Reference Part 4 (Browser Quirks and Gotchas) with workarounds

### Category 5: Command Questions
"What bowser commands exist?", "How do I run a workflow?", "What does hop-automate do?"

**Resolution**: Reference Part 2 (5 Bowser Commands) with usage examples

### Category 6: Integration Questions
"How does the justfile work?", "What agent types are available?", "How do I add a new workflow?"

**Resolution**: Reference Part 5 (Justfile Integration) and Part 9 (Skill and Agent Types)

---

## Report Format

```markdown
## Answer

{Direct answer with code example if applicable}

## Relevant Pattern

**Part**: {Part name from expertise.md}
**Backend**: {claude-bowser | playwright-bowser | Apify | N/A}
**Key Detail**:
```
{Relevant code snippet or configuration}
```

## Source Reference

- Expertise: `Part {N}: {Section Name}`
- File: `{relevant file path}`
```
