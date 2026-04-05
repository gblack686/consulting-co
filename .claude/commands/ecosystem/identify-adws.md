---
description: Identify ADWs and Agentic Prompts by analyzing component relationships and patterns
argument-hint: <inventory-json-path>
---

# Identify ADWs

## Purpose

Analyze the Claude ecosystem inventory to identify ADWs (Agentic Design Workflows) and Agentic Prompts based on their composition patterns.

## Variables

INVENTORY_FILE: $ARGUMENTS (path to ecosystem-inventory.json)

## Classification: Command vs Agentic Prompt vs ADW

### Command (Simple)
- **< 3 steps** in workflow
- Single-purpose, straightforward task
- No complex orchestration
- Examples: `github-scrape.md`, `note-create.md`

### Agentic Prompt
- **>= 3 steps** in workflow
- Pure markdown file in `commands/`
- References multiple agents with "Use the X-agent"
- Has Step 1, Step 2, Step 3... workflow pattern
- Chains commands with `/command-name`
- **No** backend infrastructure
- Examples: `sync-claude-ecosystem.md`, `review-finances.md`

### ADW (Agentic Design Workflow)
- Has Python orchestrator in `adws/adw_workflows/`
- Uses `Task()` with `run_in_background: true`
- Has session tracking, logging infrastructure
- Has `logs/` or `output/` directories
- Persists state between runs
- Labeled with "ADW" in name or description
- Examples: `plan-build-review-adw/`

## Instructions

1. Read INVENTORY_FILE
2. Analyze commands for orchestration patterns:

### Pattern Detection

For each command in inventory:

```
1. COUNT STEPS in the markdown:
   - Look for: "Step 1", "Phase 1", "### 1.", numbered lists
   - Look for: workflow/instructions sections with sequential actions
   - Count distinct workflow steps

2. Check for ADW indicators (classify as ADW if ANY match):
   - Has corresponding folder in skills/ with Python files
   - Has corresponding file in adws/adw_workflows/
   - Uses Task() tool with run_in_background
   - Has logs/ or output/ directories
   - Name contains "adw" or description mentions "ADW"

3. If NOT ADW, classify by step count:
   - < 3 steps → COMMAND (simple)
   - >= 3 steps → AGENTIC PROMPT

4. Additional Agentic Prompt indicators:
   - Contains "Use the X-agent" phrases
   - References other /commands in workflow
   - Has hooks: section in frontmatter
```

### Extract Relationships

For each identified workflow:

```
1. Parse markdown for agent references:
   - Regex: "Use the ([a-z-]+)-agent"
   - Regex: "([A-Z][a-z]+Agent)"

2. Parse for command references:
   - Regex: "/([a-z-]+)"
   - Regex: "Invoke: `/([a-z-]+)`"

3. Parse frontmatter for hooks:
   - hooks.Stop[].command paths
   - Extract validator script names

4. Build relationship map
```

## Output Format

```json
{
  "inventory_file": "path/to/inventory.json",
  "analysis_date": "YYYY-MM-DD",
  "workflows": {
    "adws": [
      {
        "name": "plan-build-review-adw",
        "type": "ADW",
        "step_count": 3,
        "indicators": ["has Python orchestrator", "uses Task()", "has logs/ directory"],
        "orchestrator_file": "skills/plan-build-review-adw/",
        "components": {
          "agents": ["plan-agent", "build-agent", "review-agent"],
          "commands": ["/plan-build-review"],
          "hooks": ["code-validator.py"]
        }
      }
    ],
    "agentic_prompts": [
      {
        "name": "sync-claude-ecosystem",
        "type": "Agentic Prompt",
        "step_count": 6,
        "indicators": [">=3 steps", "chains commands", "no backend infra"],
        "orchestrator_file": "commands/sync-claude-ecosystem.md",
        "components": {
          "sub_commands": ["/scan-claude-folder", "/check-obsidian-exists", "/copy-to-obsidian"],
          "agents_referenced": []
        }
      }
    ],
    "commands": [
      {
        "name": "github-scrape",
        "type": "Command",
        "step_count": 2,
        "description": "Simple command with <3 steps"
      }
    ]
  },
  "component_usage": {
    "agents": {
      "normalize-csv-agent": {
        "used_by": ["review-finances"],
        "workflow_type": "agentic-prompt"
      }
    },
    "commands": {...},
    "hooks": {...}
  },
  "summary": {
    "total_adws": 1,
    "total_agentic_prompts": 4,
    "total_simple_commands": 8,
    "classification_criteria": {
      "command": "< 3 steps",
      "agentic_prompt": ">= 3 steps, no backend",
      "adw": "has infra artifacts (Python, logs/, adws/)"
    },
    "orphan_agents": [],
    "orphan_commands": [],
    "orphan_hooks": []
  }
}
```

## Report

```
## Workflow Identification Report

### Classification Criteria
| Type | Criteria |
|------|----------|
| Command | < 3 steps, simple single-purpose |
| Agentic Prompt | >= 3 steps, pure markdown orchestration |
| ADW | Has infra artifacts (Python, logs/, adws/ folder) |

### ADWs Found
| Name | Steps | Orchestrator | Agents | Hooks |
|------|-------|--------------|--------|-------|
| plan-build-review-adw | 3 | skills/plan-build-review-adw/ | 3 | 1 |

### Agentic Prompts Found (>= 3 steps)
| Name | Steps | Sub-Commands | Agents |
|------|-------|--------------|--------|
| sync-claude-ecosystem | 6 | 6 | 0 |
| codebase-knowledge-extract | 8 | 8 | 0 |

### Simple Commands Found (< 3 steps)
| Name | Steps | Description |
|------|-------|-------------|
| github-scrape | 2 | Run GitHub watchlist scraper |
| note-create | 1 | Create Obsidian note |

### Component Diagram: review-finances
```
┌─────────────────────────────────────┐
│     Agentic Prompt: review-finances │
├─────────────────────────────────────┤
│ Agents:                             │
│  ├── normalize-csv-agent            │
│  ├── categorize-csv-agent           │
│  ├── merge-accounts-agent           │
│  ├── graph-agent                    │
│  └── generative-ui-agent            │
├─────────────────────────────────────┤
│ Commands:                           │
│  ├── /accumulate-csvs               │
│  └── /normalize-csv                 │
├─────────────────────────────────────┤
│ Hooks:                              │
│  ├── html-validator.py              │
│  └── csv-validator.py               │
└─────────────────────────────────────┘
```

### Orphan Components (not part of any workflow)
- Agents: {list}
- Commands: {list}
- Hooks: {list}

### Results saved to:
- JSON: TARGET_FOLDER/workflow-analysis.json
```




