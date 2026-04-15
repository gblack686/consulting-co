---
allowed-tools: Read, Glob, Grep, Edit, Bash
description: Self-improve library expertise by auditing catalog against actual skills, agents, and Obsidian notes
---

# Library Expert - Self-Improve Mode

Validate and update library expertise by comparing library.yaml against actual consulting-co contents, Obsidian vault state, and upstream the-library repo.

## Variables

EXPERTISE_PATH: .claude/commands/experts/library/expertise.yaml
LIBRARY_YAML: C:/Users/gblac/OneDrive/Desktop/tac/the-library/library.yaml
SKILLS_DIR: C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills
AGENTS_DIR: C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/agents
VAULT_PATH: C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB

## Workflow

### Step 1: Load Current State
- Read `EXPERTISE_PATH` and `LIBRARY_YAML`
- Count entries: skills, agents, prompts

### Step 2: Audit Skills
```bash
# Find all SKILL.md files in consulting-co
find "$SKILLS_DIR" -name "SKILL.md" -o -name "skill.md" | sort
```
- Compare against library.yaml skill entries
- Flag: skills present locally but missing from catalog (orphans)
- Flag: catalog entries pointing to deleted/moved sources

### Step 3: Audit Agents
```bash
ls "$AGENTS_DIR"/*.md
```
- Compare against library.yaml agent entries
- Flag orphans and stale entries

### Step 4: Audit Obsidian Notes
- Glob `VAULT_PATH/skills/**/*.md`, `VAULT_PATH/agents/*.md`, `VAULT_PATH/commands/*.md`
- Check each library entry has a corresponding Obsidian note with `library-synced` tag
- Flag missing Obsidian notes

### Step 5: Update
- Add missing entries to library.yaml
- Update expertise.yaml catalog_stats
- Run `python scripts/generate_obsidian_notes.py` for missing Obsidian notes if needed

### Step 6: Report

```markdown
## Library Self-Improve Report

### Catalog State
- Skills: {count} | Agents: {count} | Prompts: {count}

### Gaps Found
| Type | Name | Issue |
|------|------|-------|
| {type} | {name} | orphan / missing note / stale source |

### Updates Made
- {change 1}
- {change 2}
```
