---
name: skill-discovery
description: "Inventory all consulting pipeline skills, map to lifecycle phases, and generate capabilities indexes for any second brain vault."
argument-hint: "[--output <second-brain-path>] [--format table|json]"
---

# Skill Discovery

Scan all skills under `.claude/skills/`, parse their metadata, map them to consulting pipeline phases, and generate capability indexes.

## Invocation

```
/skill-discovery
```

## Parameters

- **`--output`** (optional) — Path to a second brain `capabilities/` folder. Defaults to stdout.
- **`--format`** (optional) — Output format: `table` (markdown) or `json`. Default: `table`.

## Workflow

1. **Scan** — Glob for all `SKILL.md` files under `.claude/skills/`
2. **Parse** — Extract YAML frontmatter (`name`, `description`) + detect trigger (`/skill-name`)
3. **Classify** — Match each skill to a pipeline phase using `references/pipeline-taxonomy.md` keywords
4. **Generate** — Produce two files:
   - `skills-index.md` — flat table of all skills with trigger, phase, description
   - `pipeline-map.md` — skills grouped by 7-phase lifecycle with cross-cutting section
5. **Write** — If `--output` given, write to that path. Otherwise print to console.

## Quick Start

```bash
# Print skill inventory to console
python .claude/skills/skill-discovery/scripts/discover.py

# Write to GBAutomation second brain
python .claude/skills/skill-discovery/scripts/discover.py --output C:/Users/gblac/OneDrive/Desktop/gbauto/gbautomation/second-brain/capabilities

# JSON output for programmatic use
python .claude/skills/skill-discovery/scripts/discover.py --format json
```

## Related

- **domain-discovery** — Scans GitHub repos and discovers project domains (broader scope, on Mac Mini OpenClaw)
- **obsidian-agent-archiver** — Archives agents/skills to Obsidian AI-Agent-KB
