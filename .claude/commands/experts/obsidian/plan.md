---
type: expert-file
parent: "[[obsidian/_index]]"
file-type: command
command-name: "plan"
human_reviewed: false
tags: [expert-file, command, planning, obsidian]
---

# Obsidian Expert - Plan Mode

> Create implementation plans for Obsidian vault work: archiving, schema design, Playwright testing, or new entity types.

## Purpose
Plan Obsidian vault operations using the expertise mental model. Produces a spec file with exact file paths, frontmatter templates, and implementation steps.

## Usage
```
/experts:obsidian:plan [user_request]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Task`, `Write`

---

## Planning Framework

### Step 1: Identify Operation Type

| Request | Operation |
|---------|-----------|
| "Archive X into Obsidian" | Archiving Workflow (Part 7) |
| "Add new agent/skill/expert" | Entity Creation (Part 2) |
| "Create a base view for X" | Bases Design (Part 3) |
| "Test my vault / screenshot" | Playwright Testing (Part 8) |
| "Generate vault schema" | Schema Analysis (Part 6) |
| "Update CSS / theme" | Theme Work (Part 4) |
| "Sync / hook integration" | Hooks Integration (Part 9) |

### Step 2: Determine Entity Details

For new entities:
- **Type**: agent / skill / adw / expert / hook / command / agentic-prompt
- **Target folder**: use entity type → folder mapping
- **Template**: pick from `obsidian-agent-archiver/templates/`
- **MTG card**: check registry, assign unique card

### Step 3: Resolve Paths

Always use absolute vault paths:
```
Vault root:   C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation
AI-Agent-KB:  ...\Gbautomation\AI-Agent-KB
Agents:       ...\AI-Agent-KB\agents\
MTG images:   ...\AI-Agent-KB\_assets\mtg-cards\
CSS:          ...\Gbautomation\.obsidian\snippets\
```

### Step 4: Playwright Validation Strategy

For any vault changes that affect visual output:
- [ ] Does a `.base` file need updating?
- [ ] Should we screenshot the result?
- [ ] Do frontmatter fields need completeness validation?
- [ ] Visual regression test needed?

---

## Plan Output Format

```markdown
# Obsidian Plan: {Title}

## Operation Type
{Archiving | Entity Creation | Bases Design | Testing | Schema | Theme | Hooks}

## Entity Details (if applicable)
- **Type**: {entity type}
- **Name**: {name}
- **Target folder**: {path}
- **Template**: {template file}
- **MTG Card**: {card name} ({color})

## Frontmatter Template
```yaml
---
name: {name}
status: active
{type-specific fields}
mtg_card: "{Card Name}"
mtg_color: {U/W/R/G/B/Colorless}
banner: "[[_assets/mtg-cards/{card-slug}.jpg]]"
tags: [{entity-type}]
updated: {YYYY-MM-DD}
---
```

## Files to Create/Modify
| File | Action |
|------|--------|
| `{path}` | Create/Edit/Archive |

## Implementation Steps
1. {Step 1}
2. {Step 2}
3. {Step 3}

## Playwright Validation
- [ ] {screenshot check}
- [ ] {frontmatter completeness}
- [ ] {visual regression}

## Notes
{Edge cases, dependencies, registry updates needed}
```

---

## Examples

### Example 1: "Archive the playwright-validator agent to Obsidian"
**Type**: Entity Creation → agent
**Folder**: `AI-Agent-KB/agents/playwright-validator.md`
**Template**: `agent-template.md`
**Plan**: Create note with frontmatter, assign MTG card, verify banner image exists

### Example 2: "Create a Bases view for Experts"
**Type**: Bases Design
**File**: `AI-Agent-KB/07-Experts/Experts.base`
**Plan**: Define filter `file.hasTag("expert")`, properties, cards + table views

### Example 3: "Screenshot all .base views for review"
**Type**: Playwright Testing
**Plan**: Run `test-obsidian-playwright.py` render pattern, one HTML per base, full-page screenshots

### Example 4: "Add the new obsidian expert to the KB"
**Type**: Entity Creation → expert
**Folder**: `AI-Agent-KB/07-Experts/obsidian/`
**Template**: `expert-template.md`
**Plan**: Create index + expertise note, assign MTG card from registry
