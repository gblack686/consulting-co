---
description: Copy Claude ecosystem components to Obsidian using appropriate templates
argument-hint: <sync-queue-json-path>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run .claude/hooks/validators/obsidian-sync-validator.py"
---

# Copy to Obsidian

## Purpose

Create Obsidian notes for Claude ecosystem components using the appropriate templates from `obsidian-agent-archiver`.

## Variables

SYNC_QUEUE_FILE: $ARGUMENTS (path to sync-queue.json from check)
OBSIDIAN_VAULT: CLAUDE.md: OBSIDIAN_VAULT
AI_AGENT_KB: OBSIDIAN_VAULT/AI-Agent-KB
TEMPLATES_DIR: .claude/skills/obsidian-agent-archiver/templates
TAC_DIR: C:/Users/gblac/OneDrive/Desktop/tac

## Template Mapping

| Component Type | Template File |
|----------------|---------------|
| Agent | `agent-template.md` |
| Command | `command-template.md` |
| Hook | `hook-template.md` |
| Skill | `skill-template.md` |
| ADW | `adw-template.md` |
| Agentic Prompt | `agentic-prompt-template.md` |

## Instructions

1. Read SYNC_QUEUE_FILE
2. For each item in sync_queue:

### Process Each Component - VERBATIM COPY

**IMPORTANT**: Copy the source file content verbatim. Do NOT create metadata stubs or quality indicator sections.

```
For each item in sync_queue:
  1. Read the ENTIRE source file content
  2. Detect if source is from TAC directory:
     - Check if source path contains "/tac/" or "\tac\"
     - If yes: tac_original = true
     - If no: tac_original = false
  3. Check if source has frontmatter (between --- markers)
  4. If source has frontmatter:
     - Parse existing frontmatter
     - Add only these Obsidian-specific fields if missing:
       - type: {agent|command|hook|skill}
       - tags: [appropriate tags]
       - cssclasses: [ai-agent-kb]
       - source_repo: {repo name from path}
       - source_path: {original file path}
       - human_reviewed: false
       - tac_original: {true if from TAC_DIR, false otherwise}
     - Keep ALL existing frontmatter fields
     - Write the COMPLETE source content after frontmatter
  5. If source has NO frontmatter:
     - Create minimal frontmatter with fields above (including human_reviewed: false, tac_original: {detected value})
     - Write the COMPLETE source content after
  6. Write to target Obsidian path
  7. Log creation

DO NOT:
- Create "Quality Indicators" sections
- Add has_frontmatter, has_purpose, line_count fields
- Truncate or summarize the source content
- Use templates that replace the original content
```

### Handling Scripts (for Skills)

For skills with scripts:
- List all scripts in `scripts/` subfolder
- Create individual script notes if desired
- Reference scripts in skill note's ## Scripts section

### Handling Nested Commands

For commands in subfolders:
- Preserve folder context in note
- E.g., `commands/ecosystem/scan-claude-folder.md` → note title includes context

## Ensure Folders Exist

Before writing, create folders if needed:
```bash
mkdir -p "AI_AGENT_KB/02-Agents"
mkdir -p "AI_AGENT_KB/03-Skills"
mkdir -p "AI_AGENT_KB/08-Commands"
mkdir -p "AI_AGENT_KB/09-Hooks"
mkdir -p "AI_AGENT_KB/10-Agentic-Prompts"
```

## Output Format

```json
{
  "sync_queue_file": "path/to/sync-queue.json",
  "copy_date": "YYYY-MM-DD",
  "results": {
    "created": [
      {
        "type": "agent",
        "name": "agent-name",
        "obsidian_path": "AI_AGENT_KB/02-Agents/agent-name.md",
        "template_used": "agent-template.md"
      }
    ],
    "failed": [
      {
        "type": "agent",
        "name": "agent-name",
        "error": "Template not found"
      }
    ]
  },
  "summary": {
    "created": 0,
    "failed": 0
  }
}
```

## Report

```
## Obsidian Copy Report

### Created Notes
| Type | Name | Obsidian Path |
|------|------|---------------|
| Agent | name | path |

### Failed
| Type | Name | Error |
|------|------|-------|
| Agent | name | error |

### Summary
- Created: {count}
- Failed: {count}

### Results saved to:
- JSON: TARGET_FOLDER/copy-results.json
```




