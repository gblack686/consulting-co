---
allowed-tools: Read, Grep, Glob, Bash
description: Answer questions about the-library catalog, skills, distribution, and Obsidian integration
argument-hint: [question]
---

# Library Expert - Question Mode

Answer questions about the-library by referencing the expertise knowledge base and the live library.yaml catalog.

## Variables

USER_QUESTION: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/library/expertise.yaml
LIBRARY_YAML: C:/Users/gblac/OneDrive/Desktop/tac/the-library/library.yaml
VAULT_PATH: C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB

## Instructions

- IMPORTANT: This is a question-answering task only — DO NOT modify files
- Focus on library catalog, skill distribution, Obsidian integration, and MTG card assignments
- If the question requires changes, explain the approach without implementing

## Workflow

1. **Load Expertise** — Read `EXPERTISE_PATH` for architecture and patterns
2. **Check Catalog** — Read `LIBRARY_YAML` if question is about specific skills/agents
3. **Check Obsidian** — Glob/Read vault notes if question is about Obsidian integration
4. **Answer** — Direct answer with commands/paths as needed

## Report Format

```markdown
## Answer
{Direct answer}

## Details
{Supporting info with paths/commands}

## Source
- Expertise: `EXPERTISE_PATH` section: {section}
```
