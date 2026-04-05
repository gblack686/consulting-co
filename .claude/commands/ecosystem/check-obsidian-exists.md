---
description: Check which Claude ecosystem components already exist in Obsidian AI-Agent-KB
argument-hint: <inventory-json-path>
---

# Check Obsidian Exists

## Purpose

Compare discovered Claude components against existing Obsidian AI-Agent-KB notes to identify what needs to be synced.

## Variables

INVENTORY_FILE: $ARGUMENTS (path to ecosystem-inventory.json from scan)
OBSIDIAN_VAULT: CLAUDE.md: OBSIDIAN_VAULT
AI_AGENT_KB: OBSIDIAN_VAULT/AI-Agent-KB

## Folder Mapping

| Component Type | Obsidian Folder |
|----------------|-----------------|
| Agent | `AI_AGENT_KB/02-Agents/` |
| Command | `AI_AGENT_KB/08-Commands/` |
| Hook | `AI_AGENT_KB/09-Hooks/` |
| Skill | `AI_AGENT_KB/03-Skills/` |
| ADW | `AI_AGENT_KB/01-ADWs/` |
| Agentic Prompt | `AI_AGENT_KB/10-Agentic-Prompts/` |

## Instructions

1. Read INVENTORY_FILE
2. For each component, check if corresponding Obsidian note exists:

### Check Logic

```
For each agent in inventory.agents:
  obsidian_path = AI_AGENT_KB/02-Agents/{agent.name}.md
  if file_exists(obsidian_path):
    mark as "synced"
    record existing note path
  else:
    mark as "needs_sync"
    add to sync_queue
```

Repeat for commands, hooks, skills.

### Fuzzy Matching

If exact match not found, check for:
- Case variations: `Build-Agent.md` vs `build-agent.md`
- Underscore/hyphen: `build_agent.md` vs `build-agent.md`
- With/without suffix: `build-agent.md` vs `build-agent-agent.md`

## Output Format

```json
{
  "inventory_file": "path/to/inventory.json",
  "obsidian_vault": "AI_AGENT_KB path",
  "check_date": "YYYY-MM-DD",
  "results": {
    "agents": {
      "synced": [
        {"name": "agent-name", "source": "...", "obsidian": "..."}
      ],
      "needs_sync": [
        {"name": "agent-name", "source": "...", "target": "..."}
      ]
    },
    "commands": {...},
    "hooks": {...},
    "skills": {...}
  },
  "sync_queue": [
    {
      "type": "agent",
      "name": "agent-name",
      "source_file": "path/to/source.md",
      "target_file": "AI_AGENT_KB/02-Agents/agent-name.md",
      "template": "agent-template.md"
    }
  ],
  "summary": {
    "already_synced": 0,
    "needs_sync": 0,
    "total_checked": 0
  }
}
```

## Report

```
## Obsidian Sync Check

### Already in Obsidian
| Type | Name | Obsidian Path |
|------|------|---------------|
| Agent | name | path |

### Needs Sync (sync_queue)
| Type | Name | Source | Target |
|------|------|--------|--------|
| Agent | name | source | target |

### Summary
- Already synced: {count}
- Needs sync: {count}

### Sync queue saved to:
- JSON: TARGET_FOLDER/sync-queue.json
```




