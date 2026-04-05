---
type: expert-file
parent: "[[linkedin/_index]]"
file-type: command
command-name: "question"
human_reviewed: false
tags: [expert-file, command, read-only, linkedin]
---

# LinkedIn Expert - Question Mode

> Read-only command to query LinkedIn automation patterns without making changes.

## Purpose
Answer questions about LinkedIn credit optimization, InMail campaigns, browser automation for LinkedIn, prospect management, and outreach strategy **without making any code changes**.

## Usage
```
/experts:linkedin:question [question]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Task`

---

## Workflow

1. **Receive question** from user
2. **Read expertise.md** for LinkedIn mental model
3. **Search codebase** for existing LinkedIn automation files, prospect data, or outreach logs
4. **Answer** with pattern reference, code example, and source

---

## Question Categories

### Category 1: Credit Questions
"How many InMails do I have left?", "When do credits reset?", "How do I get InMail refunds?"

**Resolution**: Reference Part 1 (The LinkedIn Credit System) — credit types, allocations, recovery rules

### Category 2: Automation Questions
"How do I automate LinkedIn safely?", "What browser backend should I use?", "How fast can I go?"

**Resolution**: Reference Part 2 (Browser Automation Strategy) — pacing rules, session safety, detection avoidance

### Category 3: Workflow Questions
"How do I send InMails?", "How does connection outreach work?", "How do I research prospects?"

**Resolution**: Reference Part 3 (Core LinkedIn Workflows) — step-by-step workflow descriptions

### Category 4: InMail Questions
"What subject lines work?", "How do I write a good InMail?", "When should I send InMails?"

**Resolution**: Reference Part 5 (InMail Best Practices) — templates, timing, credit optimization

### Category 5: Safety Questions
"Will I get banned?", "What are the daily limits?", "What should I do if I see a CAPTCHA?"

**Resolution**: Reference Part 7 (Safety & Compliance) — risk tiers, red flags, abort triggers

### Category 6: Pipeline Questions
"How do prospects flow through the system?", "Where is prospect data stored?", "How do I track outreach?"

**Resolution**: Reference Part 6 (Prospect List Management) — data schema, status flow, output files

### Category 7: Integration Questions
"How does LinkedIn connect to consulting intake?", "What ICP filters should I use?"

**Resolution**: Reference Part 8 (Integration with Consulting Pipeline) — ICP filters, workflow stages

### Category 8: Technical Questions
"What MCP tools do I use for LinkedIn?", "How do I extract profile data?", "How do I fill InMail forms?"

**Resolution**: Reference Part 4 (MCP Chrome DevTools Patterns) and Part 10 (Quick Reference)

---

## Report Format

```markdown
## Answer

{Direct answer with code example if applicable}

## Relevant Pattern

**Part**: {Part name from expertise.md}
**Workflow**: {workflow name if applicable}
**Key Detail**:
```
{Relevant code snippet, template, or configuration}
```

## Source Reference

- Expertise: `Part {N}: {Section Name}`
- File: `{relevant file path}`
```
