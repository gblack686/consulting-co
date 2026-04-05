---
model: opus
description: Main orchestrator - scans .claude folder, syncs to Obsidian, identifies ADWs/Agentic Prompts, assigns MTG cards
argument-hint: <claude-folder-path> [--dry-run] [--skip-mtg]
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run .claude/hooks/validators/obsidian-sync-validator.py"
---

# Sync Claude Ecosystem

## Purpose

Orchestrate the complete Claude ecosystem → Obsidian archival workflow by chaining multiple specialized sub-commands to discover components, sync to Obsidian, identify workflows, and assign MTG cards.

> **Note**: This is an **Agentic Prompt**, not an ADW. It orchestrates through pure markdown without backend infrastructure.

## Variables

SOURCE_FOLDER: $1 (path to .claude folder to scan)
OUTPUT_DIR: SOURCE_FOLDER/sync-claude-ecosystem (all output files go here)
DRY_RUN: Check if $ARGUMENTS contains "--dry-run"
SKIP_MTG: Check if $ARGUMENTS contains "--skip-mtg"
OBSIDIAN_VAULT: CLAUDE.md: OBSIDIAN_VAULT
AI_AGENT_KB: OBSIDIAN_VAULT/AI-Agent-KB
TEMPLATES_DIR: .claude/skills/obsidian-agent-archiver/templates

## Instructions

- First, validate SOURCE_FOLDER exists and contains expected subfolders (agents/, commands/, hooks/, skills/)
- Chain through each phase in sequential order - do NOT proceed if a phase fails
- Wait for each phase to complete before proceeding
- If DRY_RUN is set, only report what would be done without making changes
- If SKIP_MTG is set, skip Phase 4 (MTG card assignment)
- Report progress after each phase completes

## Workflow

1. Parse arguments: SOURCE_FOLDER and flags
2. Validate SOURCE_FOLDER path
3. Execute the phase chain in order:

### Phase 0: Setup & Validation

1. Check SOURCE_FOLDER exists
2. Create OUTPUT_DIR if it doesn't exist (SOURCE_FOLDER/sync-claude-ecosystem/)
3. Verify it has expected structure:
   ```
   SOURCE_FOLDER/
   ├── agents/      (optional)
   ├── commands/    (optional)
   ├── hooks/       (optional)
   └── skills/      (optional)
   ```
4. Verify OBSIDIAN_VAULT and AI_AGENT_KB paths exist
5. Verify TEMPLATES_DIR has required templates:
   - agent-template.md
   - command-template.md
   - hook-template.md
   - skill-template.md
   - adw-template.md
   - agentic-prompt-template.md

### Phase Chain

#### Phase 1: Discovery
Invoke: `Use the /ecosystem/scan-claude-folder command with SOURCE_FOLDER`
- **Input**: SOURCE_FOLDER path
- **Output**: OUTPUT_DIR/ecosystem-inventory.json

Verify output file created before proceeding.

#### Phase 2: Obsidian Diff Check
Invoke: `Use the /ecosystem/check-obsidian-exists command with the inventory file`
- **Input**: OUTPUT_DIR/ecosystem-inventory.json
- **Output**: OUTPUT_DIR/sync-queue.json

Verify output file created before proceeding.

#### Phase 3: Copy to Obsidian
**Skip if DRY_RUN is set** - just report what would be copied.

Invoke: `Use the /ecosystem/copy-to-obsidian command with the sync queue`
- **Input**: OUTPUT_DIR/sync-queue.json
- **Output**: New notes in AI_AGENT_KB folders
- **Output**: OUTPUT_DIR/copy-results.json

Stop hook validates notes were created correctly.

#### Phase 3.5: Update Frontmatter Keys
Ensure all Obsidian notes have required frontmatter fields (`human_reviewed`, `tac_original`).

Run the frontmatter update scripts:
```bash
# Add missing frontmatter keys to all notes
python "AI_AGENT_KB/_assets/scripts/add_frontmatter_keys.py" --apply

# Detect and mark TAC-originated files
python "AI_AGENT_KB/_assets/scripts/detect_tac_origin.py" --apply
```

- **Input**: All notes in AI_AGENT_KB component folders
- **Output**: Updated frontmatter in existing notes
- **Output**: AI_AGENT_KB/_tac_origin_report.json

**Note**: Phase 3 (Copy) auto-sets `tac_original` for newly copied files based on source path. This phase ensures existing notes also have the fields.

#### Phase 4: Identify Workflows
Invoke: `Use the /ecosystem/identify-adws command with the inventory`
- **Input**: OUTPUT_DIR/ecosystem-inventory.json
- **Output**: OUTPUT_DIR/workflow-analysis.json

This classifies commands by complexity:

| Type | Criteria |
|------|----------|
| **Command** | < 3 steps, simple single-purpose |
| **Agentic Prompt** | >= 3 steps, pure markdown orchestration |
| **ADW** | Has infra artifacts (Python orchestrator, logs/, adws/ folder) |

#### Phase 5: Link Components
**Skip if DRY_RUN is set** - just report what would be linked.

Invoke: `Use the /ecosystem/link-adw-components command with the workflow analysis`
- **Input**: OUTPUT_DIR/workflow-analysis.json
- **Output**: Updated Obsidian notes with cross-references
- **Output**: OUTPUT_DIR/link-results.json

#### Phase 6: Assign MTG Cards
**Skip if DRY_RUN or SKIP_MTG is set**

Invoke: `Use the /ecosystem/assign-mtg-cards command with the inventory`
- **Input**: OUTPUT_DIR/ecosystem-inventory.json
- **Output**: Updated Obsidian note frontmatter with MTG cards
- **Output**: OUTPUT_DIR/mtg-assignments.json

Stop hook validates all components have cards assigned.

4. Now follow the `Report` section to summarize the completed work

## Report

Present progress and completion in this format:

```
## Claude Ecosystem Sync: SOURCE_FOLDER

### Setup
- Source: SOURCE_FOLDER
- Obsidian Vault: OBSIDIAN_VAULT
- AI-Agent-KB: AI_AGENT_KB
- Dry Run: {yes/no}
- Skip MTG: {yes/no}

### Progress
- [x] Phase 0: Setup validated
- [x] Phase 1: Discovery - {count} components found (TAC origin: {yes/no})
- [x] Phase 2: Diff Check - {count} need sync, {count} already synced
- [x] Phase 3: Copy - {count} notes created
- [x] Phase 3.5: Frontmatter - {count} notes updated with human_reviewed/tac_original
- [x] Phase 4: Workflows - {count} ADWs, {count} Agentic Prompts, {count} Simple Commands
- [x] Phase 5: Links - {count} cross-references created
- [x] Phase 6: MTG Cards - {count} cards assigned

### Discovery Summary
| Type | Found | Already Synced | Newly Added |
|------|-------|----------------|-------------|
| Agents | {n} | {n} | {n} |
| Commands | {n} | {n} | {n} |
| Hooks | {n} | {n} | {n} |
| Skills | {n} | {n} | {n} |

### TAC Origin & Review Status
| Type | TAC Originals | Human Reviewed | Missing TAC Field |
|------|---------------|----------------|-------------------|
| Agents | {n} | {n} | {n} |
| Commands | {n} | {n} | {n} |
| Hooks | {n} | {n} | {n} |
| Skills | {n} | {n} | {n} |

> **TAC Origin**: Components from `C:/Users/gblac/OneDrive/Desktop/tac/` (IndyDevDan courses)
> **Human Reviewed**: Components verified by a human (must be set manually)

### Workflows Identified

#### Classification Criteria
| Type | Criteria |
|------|----------|
| Command | < 3 steps, simple single-purpose |
| Agentic Prompt | >= 3 steps, pure markdown orchestration |
| ADW | Has infra artifacts (Python, logs/, adws/) |

#### ADWs (with backend infrastructure)
| Name | Steps | Orchestrator |
|------|-------|--------------|
| {name} | {n} | {path} |

#### Agentic Prompts (>= 3 steps, pure markdown)
| Name | Steps | Sub-Commands |
|------|-------|--------------|
| {name} | {n} | {n} |

#### Simple Commands (< 3 steps)
| Name | Steps | Description |
|------|-------|-------------|
| {name} | {n} | {desc} |

### MTG Card Distribution
| Color | Count | Components |
|-------|-------|------------|
| Blue | {n} | agent-1, agent-2 |
| Red | {n} | cmd-1, hook-1 |
| ... | | |

### Output Files (in OUTPUT_DIR)
1. `ecosystem-inventory.json` - Component discovery (includes is_tac_origin flag)
2. `sync-queue.json` - Items needing sync
3. `copy-results.json` - Copy operation results
4. `workflow-analysis.json` - ADW/Agentic Prompt identification
5. `link-results.json` - Cross-reference results
6. `mtg-assignments.json` - MTG card assignments
7. `ecosystem-classification.json` - Quality classification (official/needs_review/deletable)
8. `ecosystem-sync-history.json` - Sync history and timestamps
9. `obsidian-validation.json` - TAC stats, review stats, MTG coverage (in OUTPUT_DIR)
10. `_tac_origin_report.json` - TAC origin detection results (in AI_AGENT_KB)

### Obsidian Notes Created/Updated
- Agents: AI_AGENT_KB/02-Agents/
- Commands: AI_AGENT_KB/08-Commands/
- Hooks: AI_AGENT_KB/09-Hooks/
- Skills: AI_AGENT_KB/03-Skills/
- ADWs: AI_AGENT_KB/01-ADWs/
- Agentic Prompts: AI_AGENT_KB/10-Agentic-Prompts/
```

## Examples

```bash
# Full sync of current project's .claude folder
/sync-claude-ecosystem .claude/

# Sync another project's Claude ecosystem
/sync-claude-ecosystem C:/Users/gblac/OneDrive/Desktop/tac/agentic-finance-review/.claude

# Dry run - see what would be synced without making changes
/sync-claude-ecosystem .claude/ --dry-run

# Skip MTG card assignment
/sync-claude-ecosystem .claude/ --skip-mtg

# Both flags
/sync-claude-ecosystem .claude/ --dry-run --skip-mtg
```

## Error Handling

If any phase fails:
1. Report the error with phase context
2. Show what succeeded before the failure
3. Provide recovery instructions:
   - How to re-run from a specific phase
   - How to manually fix the issue
4. Save partial results to output files for debugging

