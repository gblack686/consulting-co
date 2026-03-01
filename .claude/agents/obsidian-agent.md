# Obsidian Agent 📝

*From chaos of execution, birth of order*
*Markdown becomes memory, memory becomes wisdom*

---

## Purpose

Transform agent sessions into living documents. Generate markdown notes that grow like knowledge, linked across time and space.

---

## Core Mission

Auto-generate comprehensive session documentation. Create daily summaries. Link related sessions. Make agent behavior visible and searchable.

---

## Primary Files

### Main Exporter Script
**`.claude/scripts/obsidian_exporter.py`** (uv run)
```
Trigger: Stop hook (via settings.local.json)
Action: Read Neo4j → format markdown → write to vault
Timeout: 10 seconds
```

### Configuration
**`.claude/config/obsidian.yaml`**
```yaml
vault:
  path: "./observability/notes"

directories:
  sessions: "sessions"
  daily: "daily"

export:
  frequency: "per-session"
  include_metrics: true
  include_entities: true
  include_timeline: true
```

---

## How It Works

### On Session End (Stop Hook)

1. **Query Neo4j**
   - Fetch session node from database
   - Get all tool execution spans
   - Retrieve extracted entities
   - Calculate metrics

2. **Format Session Note**
   ```markdown
   ---
   session_id: d23d5ebd
   source_app: consulting-co
   model: claude-sonnet-4-5
   date: 2025-11-16
   status: completed
   tags: [agent-session]
   ---

   # Session Summary
   ## Timeline (tool execution)
   ## Entities Discovered
   ## Performance Metrics
   ## Tool Breakdown
   ```

3. **Generate Daily Summary**
   - Aggregate all sessions today
   - Sum metrics
   - Create entity index
   - Link to session notes

4. **Write to Vault**
   ```
   observability/notes/
   ├── sessions/
   │   └── consulting-co_d23d5ebd.md
   └── 2025-11-16.md
   ```

---

## Output Structure

### Session Notes
**`observability/notes/sessions/consulting-co_<id>.md`**

```markdown
---
session_id: d23d5ebd
source_app: consulting-co
model: claude-sonnet-4-5-20250929
date: 2025-11-16
status: completed
tags: [agent-session]
---

# Session d23d5ebd Summary

## Timeline
- 09:13:11 Read (250ms) - file.py
- 09:13:15 Bash (2000ms) - git status
- 09:13:20 Task (850ms) - explore codebase

## Entities Discovered
- file.py (File)
- git (Tool)
- codebase (Concept)

## Performance
- Total tools: 3
- Total latency: 3100ms
- Average per tool: 1033ms
- Performance tier: Medium 🔄

## Tool Breakdown
- Read: 250ms (8%)
- Bash: 2000ms (65%)
- Task: 850ms (27%)

## Related Sessions
- Parent: none
- Children: 2
```

### Daily Summary
**`observability/notes/YYYY-MM-DD.md`**

```markdown
# Daily Summary - 2025-11-16

## Overview
- Sessions: 5
- Total tools: 12
- Avg latency: 1200ms
- Performance: Fast ⚡

## Sessions Today
1. d23d5ebd (completed, 3100ms)
2. a4b2c1ef (completed, 2400ms)
...

## Entities Index
- Files: consulting-co, server.py, config.yaml
- Tools: Read, Bash, Task, Grep
- Concepts: refactoring, optimization
```

---

## Features

### Metrics Calculation
```python
# From obsidian_exporter.py
metrics = {
    "tool_count": len(tools),
    "total_latency_ms": sum(tool.latency_ms),
    "avg_latency_ms": sum / len(tools),
    "performance_tier": "Fast" if avg < 1000 else "Medium"
}
```

### Entity Extraction
```python
# Entities discovered during session
entities = {
    "files": ["path/to/file.py"],
    "functions": ["def my_func"],
    "concepts": ["optimization", "refactoring"]
}
```

### Backlinks
```markdown
# Automatic links created
- [[consulting-co_a4b2c1ef|parent session]]
- [[file.py|entity: File]]
- [[2025-11-16|daily summary]]
```

### Timeline Formatting
```markdown
## Timeline
- HH:MM:SS Tool Name (XXXms) - description
- Grouped by execution order
- Shows performance tiers with emoji
```

---

## Integration with Other Systems

### From Neo4j
- Session node with metrics
- Tool execution spans
- Entities and relationships

### From Langfuse
- Token counts (for context)
- Performance percentiles
- Model information

### From Observability
- Raw event timeline
- Tool success/failure
- Execution order

---

## Customization

### Enable Tool Details
**`.claude/config/obsidian.yaml`**
```yaml
export:
  limits:
    include_tool_output: true  # Show input/output
```

### Change Daily Format
```yaml
vault:
  daily_notes_format: "YYYY-MM-DD"  # or "YYYY/MM/DD"
```

### Disable Auto-Refresh
```yaml
auto_refresh:
  enabled: false  # true to watch for changes
```

---

## Documentation

### Configuration Guide
**`.claude/context/obsidian/CONFIG.md`**
- All configuration options
- Customization examples

### Integration Guide
**`.claude/context/observability/OBSIDIAN_INTEGRATION.md`**
- How it connects to other systems
- Data flow diagram

---

## Hook Registration

**`.claude/settings.local.json`**
```json
{
  "hooks": {
    "Stop": [
      {
        "command": "uv run \".claude/scripts/obsidian_exporter.py\"",
        "timeout": 10
      }
    ]
  }
}
```

---

## Viewing Notes

```bash
# List all session notes
ls observability/notes/sessions/

# View today's summary
cat observability/notes/$(date +%Y-%m-%d).md

# View specific session
cat observability/notes/sessions/consulting-co_d23d5ebd.md

# Watch for updates
tail -f observability/notes/$(date +%Y-%m-%d).md
```

---

## Philosophy

> *Every session is a story.*
> *Let markdown be the memory.*
> *Let links be the understanding.*

---

**Status**: ✅ Active
**Vault**: ./observability/notes/
**Generation**: Per-session + daily
**Format**: Obsidian markdown
**Integration**: Neo4j, Langfuse, Observability
