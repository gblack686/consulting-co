---
type: expert-file
parent: "[[obsidian/_index]]"
file-type: command
command-name: "question"
human_reviewed: false
tags: [expert-file, command, read-only, obsidian]
---

# Obsidian Expert - Question Mode

> Read-only command to query Obsidian vault architecture, schemas, CSS, Bases, and Playwright testing patterns.

## Purpose
Answer questions about the Gbautomation Obsidian vault — entity types, frontmatter, CSS themes, Datacore bases, MTG card system, schema generation, and Playwright-based vault testing — **without making any changes**.

## Usage
```
/experts:obsidian:question [question]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Task`

---

## Workflow

1. **Receive question** from user
2. **Read expertise.md** for the Obsidian mental model
3. **Route to source files** based on question category
4. **Answer** with accurate information from live vault files

---

## Question Categories

### Category 1: Schema / Taxonomy
"What entity type is X?", "Where does a skill go?", "What fields are required?"

**Route to**: `expertise.md` Part 2, then `_TAXONOMY.md`, `_SCHEMA.md`

### Category 2: Bases / Datacore
"How does Agents.base work?", "How do I filter a base?", "What views exist?"

**Route to**: `expertise.md` Part 3, then actual `*.base` files in vault

### Category 3: CSS / Themes
"What colors does the dark theme use?", "How do I style cards?"

**Route to**: `expertise.md` Part 4, then `.obsidian/snippets/*.css`

### Category 4: MTG Card System
"Is this card already used?", "How do I assign a new card?"

**Route to**: `expertise.md` Part 5, then `_MTG-CARD-REGISTRY.md`

### Category 5: Schema / Analysis
"How do I generate a vault schema?", "What output formats exist?"

**Route to**: `expertise.md` Part 6, `obsidian-schema-generator/skill.md`

### Category 6: Archiving Workflow
"How do I add a new agent to the KB?", "Which template should I use?"

**Route to**: `expertise.md` Part 7, `obsidian-agent-archiver/SKILL.md`

### Category 7: Playwright Testing
"How do I screenshot a .base view?", "Can Playwright test Obsidian?"

**Route to**: `expertise.md` Part 8, `.claude/context/testing/test-obsidian-playwright.py`

### Category 8: Hooks Integration
"How does session sync work?", "What hooks write to Obsidian?"

**Route to**: `expertise.md` Part 9, `.claude/hooks/obsidian_ecosystem_sync.py`

---

## Source File Paths

| Resource | Path |
|----------|------|
| Vault root | `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation` |
| AI-Agent-KB | `...\Gbautomation\AI-Agent-KB` |
| Schema | `...\AI-Agent-KB\_SCHEMA.md` |
| Taxonomy | `...\AI-Agent-KB\_TAXONOMY.md` |
| MTG Registry | `...\AI-Agent-KB\_MTG-CARD-REGISTRY.md` |
| CSS snippets | `...\Gbautomation\.obsidian\snippets\` |
| Agents folder | `...\AI-Agent-KB\agents\` |
| MTG card images | `...\AI-Agent-KB\_assets\mtg-cards\` |
| Archiver skill | `.claude/skills/obsidian-agent-archiver/SKILL.md` |
| Schema skill | `.claude/skills/obsidian-schema-generator/skill.md` |
| Playwright tests | `.claude/context/testing/test-obsidian-playwright.py` |

---

## Report Format

```markdown
## Answer

{Direct answer with specifics from source material}

## Details

{Field names, file paths, code examples from actual vault}

## Source

- File: `{absolute path}`
- Section: `{relevant section}`
```
