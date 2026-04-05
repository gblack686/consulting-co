---
model: opus
description: Main orchestrator - syncs new Disler/IndyDevDan repos to TAC ecosystem (clone, process, vectorize, graph, report)
argument-hint: [--check | --sync | --full <repo-name>]
---

# Sync TAC Repos

## Purpose

Orchestrate the complete TAC repository synchronization workflow by detecting new repositories from github.com/disler (IndyDevDan), cloning them to Desktop/tac/, processing components into the knowledge ecosystem (Obsidian, Supabase vectors, Graphiti graph), and generating TAC agent summaries.

## Variables

MODE: $1 (--check | --sync | --full)
REPO_NAME: $2 (optional - specific repo for --full mode)
TAC_ROOT: C:/Users/gblac/OneDrive/Desktop/tac
OBSIDIAN_KB: C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB
GITHUB_USER: disler
SUPABASE_PROJECT: unickqnwfheaczccvgbw
MIN_DATE: 2025-11-01 (only repos created/updated after Nov 2025)

## Instructions

- **--check**: Only list new repositories and repos with updates, don't clone or process
- **--sync**: Clone new repos, pull updates for existing repos, run full processing pipeline
- **--full <repo>**: Run complete processing on a specific existing repo
- **--update**: Only pull updates for existing repos (no new clones)
- **FILTER**: Only process repos with `pushedAt` >= 2025-11-01 (Nov 2025+)
- Chain through each step sequentially - do NOT proceed if current step fails
- All agents receive the repo directory path as context
- Report progress after each step completes
- Use TAC agent for knowledge retrieval and question answering

## Workflow

### Mode: --check (Discovery Only)

```bash
# List all public repos from disler, compare with local TAC_ROOT
gh repo list disler --public --json name,description,url,pushedAt --limit 100
```

Compare with:
```bash
ls -d TAC_ROOT/*/
```

Output: Table of new repos not yet cloned.

---

### Mode: --sync (Full Sync Pipeline)

Execute Steps 1-8 for each NEW repository detected.

---

### Mode: --full <repo-name> (Process Existing Repo)

Execute Steps 2-8 for the specified repository.

---

## Step 0.5: Pull Updates for Existing Repos

For repos that exist locally but have remote updates:

```bash
cd TAC_ROOT/{REPO_NAME}
git fetch origin
git pull origin main --ff-only
```

Check for updates by comparing local HEAD with remote:
```bash
git rev-parse HEAD  # local
git rev-parse origin/main  # remote (after fetch)
```

If different, pull and re-process (Steps 2-8).

---

## Step 1: Clone New Repository

```bash
cd TAC_ROOT
gh repo clone disler/{REPO_NAME}
```

Verify:
- README.md exists
- .claude/ directory structure (if present)

---

## Step 2: Scan Repository Components

Use `/tac-process-directory {REPO_NAME}` to extract:

| Component Type | Location | Action |
|----------------|----------|--------|
| Agents | `.claude/agents/*.md` | Inventory |
| Commands | `.claude/commands/*.md` | Inventory |
| Skills | `.claude/skills/*/SKILL.md` | Inventory |
| Hooks | `.claude/hooks/*.py` | Inventory |
| ADWs | `adws/*.md` or `.claude/adws/` | Inventory |

Output: Component inventory JSON

---

## Step 3: Generate TAC Agent Summary

Invoke the TAC agent to analyze the repository:

```
Task(
  subagent_type: "tac",
  model: "haiku",
  prompt: "Analyze the repository at TAC_ROOT/{REPO_NAME}. Read the README.md and CLAUDE.md (if present). Answer these questions:

  1. What TAC tactic or lesson does this repository primarily demonstrate?
  2. What are the key components (agents, commands, hooks, skills)?
  3. What patterns from building-specialized-agents does it implement (Pong, Echo, Calculator)?
  4. What frameworks are applied (PITER, R&D, ACT-LEARN-REUSE, Core Four)?
  5. What is the recommended use case for this repository?

  Format as structured markdown with ## headers for each question."
)
```

Save output to: `TAC_ROOT/{REPO_NAME}/tac-agent-summary.md`

---

## Step 4: Index Components to Supabase (Vector Tier)

For each component discovered in Step 2, add to the vector index:

```bash
python .claude/scripts/kb_search.py --index --source TAC_ROOT/{REPO_NAME}
```

Or manually via Supabase:

```sql
INSERT INTO kb_index (id, file_path, folder, type, name, summary, tags, embedding)
VALUES (
  '{repo}_{component_type}_{name}',
  '{file_path}',
  '{folder}',
  '{type}',
  '{name}',
  '{summary}',
  ARRAY['{tags}'],
  {embedding_vector}
);
```

Target table: `kb_index` with pgvector embeddings

---

## Step 5: Add to Knowledge Graph (Graphiti Tier)

Add repository episode to Graphiti:

```python
mcp__graphiti__add_memory(
  name="TAC Repository: {REPO_NAME}",
  episode_body="""
Repository: {REPO_NAME}
URL: https://github.com/disler/{REPO_NAME}
Author: IndyDevDan

Summary: {from README}

Components:
- Agents: {count} ({list})
- Commands: {count} ({list})
- Hooks: {count} ({list})
- Skills: {count} ({list})
- ADWs: {count} ({list})

Patterns: {detected patterns}
Frameworks: {detected frameworks}
TAC Lesson: {lesson number if applicable}
""",
  source="json",
  source_description="TAC repository documentation",
  group_id="ai-agent-kb"
)
```

---

## Step 6: Create Obsidian Repository Note

Create note at: `OBSIDIAN_KB/repositories/{REPO_NAME}.md`

Use template:

```markdown
---
type: repository
name: "{REPO_NAME}"
url: "https://github.com/disler/{REPO_NAME}"
author: "IndyDevDan"
description: "{description from README}"
youtube: ""
themes: [{detected themes}]
status: active
created: {today}
updated: {today}
human_reviewed: false
tac_original: true
tags: [repository, tac-course]
cssclasses: [ai-agent-kb]
banner: "[[_assets/mtg-cards/{mtg-card-kebab}.jpg]]"
mtg_card: "{MTG Card Name}"
---

![[_assets/mtg-cards/{mtg-card-kebab}.jpg]]

# {REPO_NAME}

> {One-line description}

## Overview

{2-3 sentences from README or TAC agent summary}

## Components

### Agents
{list from inventory}

### Commands
{list from inventory}

### Hooks
{list from inventory}

### Skills
{list from inventory}

### ADWs
{list from inventory}

## Patterns Demonstrated

{from TAC agent analysis}

## Key Insights

{from TAC agent summary}

---

## Related

### See Also
{similar repos}

### External Links
- [GitHub Repository](https://github.com/disler/{REPO_NAME})
```

---

## Step 6.5: Create Claude Component Notes

For each component found in the `.claude/` folder, create a corresponding Obsidian note using the templates.

### Templates by Component Type

| Component | Template | Destination |
|-----------|----------|-------------|
| Agent | `agents/_agent-template.md` | `OBSIDIAN_KB/agents/{agent-name}.md` |
| Command | `commands/_command-template.md` | `OBSIDIAN_KB/commands/{command-name}.md` |
| Hook | `hooks/_hook-template.md` | `OBSIDIAN_KB/hooks/{hook-name}.md` |
| Skill | `skills/_skill-template.md` | `OBSIDIAN_KB/skills/{skill-name}/{skill-name}.md` |
| ADW | `adws/_adw-template.md` | `OBSIDIAN_KB/adws/{adw-name}.md` |

### Process for Each Component

1. **Read the source file** from `TAC_ROOT/{REPO_NAME}/.claude/{type}/{name}.md`
2. **Extract key information**:
   - For agents: Purpose, tools, model, system prompt
   - For commands: Arguments, workflow, examples
   - For hooks: Event type, matcher, input/output format
   - For skills: Capabilities, component files
   - For ADWs: Workflow steps, agents involved
3. **Generate note** using template structure
4. **Add source reference**: `source_repo: {REPO_NAME}`, `source_path: {path}`
5. **Link to repository note**: Add `[[{REPO_NAME}]]` in Related section

### Component Note Frontmatter

```yaml
---
type: {agent|command|hook|skill|adw}
name: "{component-name}"
source_repo: "{REPO_NAME}"
source_path: ".claude/{type}/{name}.md"
status: active
created: {today}
updated: {today}
tags: [{type}, {REPO_NAME}]
cssclasses: [ai-agent-kb]
banner: "[[_assets/mtg-cards/{card}.jpg]]"
mtg_card: "{card-name}"
---
```

### Skip Conditions

- Skip if component note already exists in Obsidian
- Skip template files (names starting with `_`)
- Skip index files

---

## Step 7: Assign MTG Card

Select an appropriate MTG card based on repository theme:

| Theme | Suggested Cards |
|-------|-----------------|
| Validation | Teferi, Who Slows the Sunset |
| Orchestration | Niv-Mizzet, Parun |
| Hooks/Events | Lightning Bolt |
| Memory | Jin-Gitaxias, Core Augur |
| Agents | Ancient Copper Dragon |
| Finance | Smothering Tithe |
| Security | Darksteel Colossus |

Download card image:
```bash
# Get card image URL from Scryfall
curl "https://api.scryfall.com/cards/named?fuzzy={card_name}" | jq -r '.image_uris.normal'

# Download to Obsidian assets
curl -o "OBSIDIAN_KB/_assets/mtg-cards/{card-kebab}.jpg" "{image_url}"
```

---

## Step 8: Update Indexes

1. **Repository Index**: Add entry to `OBSIDIAN_KB/repositories/_Repository-Index.md`
2. **TAC Processing Status**: Update `.claude/data/tac-processing-status.json`
3. **Component Indexes**: Update relevant component index files

---

## Report

Present progress and completion in this format:

```markdown
## TAC Repository Sync: {REPO_NAME}

### Discovery
- **GitHub URL**: https://github.com/disler/{REPO_NAME}
- **Description**: {description}
- **Last Push**: {date}

### Processing Status
- [x] Clone: Repository cloned to TAC_ROOT/{REPO_NAME}
- [x] Scan: {n} components discovered
- [x] TAC Summary: Generated tac-agent-summary.md
- [x] Vectors: {n} components indexed to Supabase
- [x] Graph: Episode added to Graphiti
- [x] Obsidian Repo: Repository note created
- [x] Obsidian Components: {n} component notes created
- [x] MTG Cards: {n} cards assigned
- [x] Indexes: Updated

### Component Inventory

| Type | Count | Components |
|------|-------|------------|
| Agents | {n} | {list} |
| Commands | {n} | {list} |
| Hooks | {n} | {list} |
| Skills | {n} | {list} |
| ADWs | {n} | {list} |

### TAC Analysis

**Primary Lesson**: {lesson}
**Patterns**: {patterns}
**Frameworks**: {frameworks}

### Files Created
1. `TAC_ROOT/{REPO_NAME}/tac-agent-summary.md`
2. `OBSIDIAN_KB/repositories/{REPO_NAME}.md`
3. `OBSIDIAN_KB/_assets/mtg-cards/{card}.jpg`
4. Component notes (for each .claude component):
   - `OBSIDIAN_KB/agents/{agent-name}.md`
   - `OBSIDIAN_KB/commands/{command-name}.md`
   - `OBSIDIAN_KB/hooks/{hook-name}.md`
   - `OBSIDIAN_KB/skills/{skill-name}/{skill-name}.md`
   - `OBSIDIAN_KB/adws/{adw-name}.md`

### Next Steps
- [ ] Human review of Obsidian note
- [ ] Verify Dataview queries pick up new repo
- [ ] Test TAC agent retrieval for this repo
```

---

## Examples

```bash
# Check for new repos without syncing
/sync-tac-repos --check

# Sync all new repos
/sync-tac-repos --sync

# Full reprocess of specific repo
/sync-tac-repos --full agentic-finance-review
```

---

## Dependencies

- `gh` CLI authenticated to GitHub
- Supabase connection via AWS secrets
- Graphiti MCP server running
- TAC agent configured in `.claude/agents/tac.md`
- OpenAI API key for embeddings
