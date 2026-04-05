---
description: Scan a .claude folder and discover all ecosystem components (agents, commands, hooks, skills)
argument-hint: <claude-folder-path>
---

# Scan Claude Folder

## Purpose

Discover and catalog all Claude ecosystem components in a target `.claude` folder.

## Variables

TARGET_FOLDER: $ARGUMENTS (path to .claude folder)
TAC_DIR: C:/Users/gblac/OneDrive/Desktop/tac

## Instructions

1. Validate TARGET_FOLDER exists and is a `.claude` directory
2. **Detect TAC Origin**:
   - Check if TARGET_FOLDER path contains `/tac/` or `\tac\`
   - Set `is_tac_origin: true` if from TAC directory, `false` otherwise
   - This flag will be inherited by all components in the folder
3. Scan each component type and build inventory:

### Scan Agents
```bash
# Find all agent definitions
glob .claude/agents/*.md
glob .claude/agents/*.yaml
```

For each agent file:
- Extract name from filename or frontmatter `name:` field
- Extract description from frontmatter or first paragraph
- Extract model, tools from frontmatter
- Note any hooks defined

### Scan Commands
```bash
# Find all command files (including nested)
glob .claude/commands/**/*.md
```

For each command file:
- Extract name from filename (without .md)
- Extract description from frontmatter
- Check if it references agents (Agentic Prompt indicator)
- Check if it has hooks defined
- Note argument-hint

### Scan Hooks
```bash
# Find all hook scripts
glob .claude/hooks/*.py
glob .claude/hooks/**/*.py
```

For each hook file:
- Extract name from filename
- Read docstring for purpose
- Identify hook type from code (Stop, PreToolUse, etc.)
- Extract dependencies from script header

### Scan Skills
```bash
# Find all skill definitions
glob .claude/skills/*/SKILL.md
glob .claude/skills/*/skill.md
```

For each skill:
- Extract name from folder or frontmatter
- Extract description
- List scripts in scripts/ subfolder
- Note dependencies

## Output Format

Create a JSON inventory and report:

```json
{
  "source_folder": "TARGET_FOLDER",
  "scan_date": "YYYY-MM-DD",
  "is_tac_origin": true,  // true if TARGET_FOLDER path contains "/tac/" or "\tac\"
  "components": {
    "agents": [
      {
        "name": "agent-name",
        "file": "relative/path/to/file.md",
        "description": "...",
        "model": "opus",
        "tools": ["Read", "Write"],
        "hooks": [],
        "tac_original": true  // inherited from is_tac_origin
      }
    ],
    "commands": [
      {
        "name": "command-name",
        "file": "relative/path/to/file.md",
        "description": "...",
        "is_agentic_prompt": false,
        "referenced_agents": [],
        "hooks": [],
        "tac_original": true  // inherited from is_tac_origin
      }
    ],
    "hooks": [
      {
        "name": "hook-name",
        "file": "relative/path/to/file.py",
        "hook_type": "Stop",
        "description": "...",
        "tac_original": true  // inherited from is_tac_origin
      }
    ],
    "skills": [
      {
        "name": "skill-name",
        "folder": "relative/path/to/skill/",
        "description": "...",
        "scripts": ["script1.py", "script2.py"],
        "tac_original": true  // inherited from is_tac_origin
      }
    ]
  },
  "summary": {
    "total_agents": 0,
    "total_commands": 0,
    "total_hooks": 0,
    "total_skills": 0,
    "agentic_prompts_detected": 0,
    "is_tac_origin": true  // folder-level TAC detection
  }
}
```

## Report

```
## Claude Folder Scan: TARGET_FOLDER

### Source Origin
- **TAC Origin**: {Yes/No} (based on path containing /tac/)

### Components Found
- Agents: {count}
- Commands: {count}
- Hooks: {count}
- Skills: {count}

### Agentic Prompts Detected
Commands that orchestrate multiple agents:
- {command-name}: references {agents}

### Inventory saved to:
- JSON: TARGET_FOLDER/ecosystem-inventory.json
```




