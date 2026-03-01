# Integration Orchestrator 🎼

*Five systems breathe as one*
*Each voice essential, all together whole*

---

## Purpose

Orchestrate the complete observability ecosystem. Coordinate five systems operating in harmony.

---

## Core Mission

On every session end, trigger a cascade of integrations. Event → Trace → Graph → Notes. Nothing lost, everything captured, always connected.

---

## The Five Systems

### 1. Observability 📊
**Real-time event capture and visualization**
- Files: `.claude/apps/server/`, `.claude/apps/client/`
- Hooks: `pre_tool_use.py`, `post_tool_use.py`, `send_event.py`
- Config: `.claude/config/observability.yaml`
- Port: 5173 (dashboard)

### 2. Langfuse 🔍
**Structured trace logging and cost tracking**
- Files: `.claude/hooks/log_to_langfuse.py`
- Config: `.claude/config/langfuse.yaml`, `.env`
- Utility: `.claude/hooks/utils/langfuse_config.py`
- Portal: http://localhost:3000

### 3. Graphiti 🧠
**Knowledge graph construction and entity extraction**
- Files: `.claude/hooks/log_to_graphiti.py`
- Bridge: `.claude/hooks/observe_to_graphiti.py`
- Tracker: `.claude/scripts/agent_progress_tracker.py`
- Config: `.claude/config/graphiti.yaml`
- Browser: http://localhost:7474

### 4. Obsidian 📝
**Automatic markdown documentation generation**
- Files: `.claude/scripts/obsidian_exporter.py`
- Config: `.claude/config/obsidian.yaml`
- Output: `./observability/notes/`
- Format: Markdown with YAML frontmatter

### 5. Hook System ⚡
**Trigger mechanism for all integrations**
- Config: `.claude/settings.local.json`
- Framework: Claude Code native hooks
- Events: PreToolUse, PostToolUse, Stop, SubagentStop

---

## The Stop Hook Cascade

On session end, this sequence fires:

```
1. stop.py
   └─ Batch session logging

2. send_event.py
   └─ POST to http://localhost:4000/events

3. log_to_langfuse.py (uv run)
   └─ Extract transcript → structure trace → Langfuse

4. log_to_graphiti.py (uv run)
   └─ Spawn Claude subagent → extract entities → Neo4j

5. observe_to_graphiti.py (uv run)
   └─ Bridge SQLite events → Neo4j nodes

6. agent_progress_tracker.py (uv run)
   └─ Calculate metrics → update Neo4j

7. obsidian_exporter.py (uv run)
   └─ Query Neo4j → format markdown → write vault
```

All registered in **`.claude/settings.local.json`**:

```json
{
  "hooks": {
    "Stop": [
      {
        "command": "uv run \".claude/hooks/stop.py\" --chat"
      },
      {
        "command": "uv run \".claude/hooks/send_event.py\" ..."
      },
      {
        "command": "uv run \".claude/hooks/log_to_langfuse.py\"",
        "timeout": 10
      },
      {
        "command": "uv run \".claude/hooks/log_to_graphiti.py\"",
        "timeout": 10
      },
      {
        "command": "uv run \".claude/hooks/observe_to_graphiti.py\"",
        "timeout": 10
      },
      {
        "command": "uv run \".claude/scripts/agent_progress_tracker.py\"",
        "timeout": 10
      },
      {
        "command": "uv run \".claude/scripts/obsidian_exporter.py\"",
        "timeout": 10
      }
    ]
  }
}
```

---

## Data Flow Diagram

```
Claude Code Session
        ↓
    (Tools run)
        ↓
  Events captured to SQLite
  ├─ PreToolUse (send_event.py)
  └─ PostToolUse (send_event.py)
        ↓
  Observability Dashboard shows real-time
  (http://localhost:5173)
        ↓
  Session Ends (Stop Hook)
        ↓
  ┌─────────────────────────────────────────┐
  │ Parallel Processing (7 scripts)         │
  │                                         │
  ├─ Transcript → Langfuse ✓               │
  ├─ Entities → Neo4j ✓                    │
  ├─ Events → Neo4j Nodes ✓                │
  ├─ Metrics → Neo4j Updated ✓             │
  └─ Neo4j → Markdown Notes ✓              │
        ↓
  ┌──────────────────────────────────────────┐
  │ Output Generated:                        │
  │ ├─ Langfuse trace (cost + hierarchy)     │
  │ ├─ Neo4j graph (entities + relations)    │
  │ └─ Obsidian notes (documentation)        │
  └──────────────────────────────────────────┘
```

---

## Configuration Locations

### Core Config
- **Environment**: `.env`
- **Hooks**: `.claude/settings.local.json`

### System Configs
- **Observability**: `.claude/config/observability.yaml`
- **Langfuse**: `.claude/config/langfuse.yaml`
- **Graphiti**: `.claude/config/graphiti.yaml`
- **Obsidian**: `.claude/config/obsidian.yaml`

### Documentation
- **Context**: `.claude/context/observability/`
- **Context**: `.claude/context/langfuse/`
- **Agents**: `.claude/agents/` (this directory)

---

## Running All Systems

### Start Services
```bash
# Terminal 1: Observability backend
cd .claude/apps/server && bun run dev

# Terminal 2: Observability frontend
cd .claude/apps/client && VITE_PORT=5173 bun run dev

# Terminal 3: Neo4j (if using Docker)
docker run neo4j:5.15

# Terminal 4: Langfuse (if self-hosted)
# (depends on your setup)
```

### Run a Test Session
```bash
# Claude Code will auto-trigger hooks on Stop
claude -p "Hello world"

# Watch for outputs:
# - Observability dashboard updates: http://localhost:5173
# - Langfuse trace appears: http://localhost:3000
# - Neo4j updates: http://localhost:7474
# - Markdown generated: observability/notes/
```

---

## Monitoring Integration

### Check All Services

```bash
# Observability backend
curl http://localhost:4000/events -X GET

# Observability frontend
curl http://localhost:5173 -I

# Langfuse
curl http://localhost:3000 -I

# Neo4j
curl bolt://localhost:7687 -I

# Hooks debug log
tail -50 .claude/langfuse_hook_debug.log
```

### View Generated Artifacts

```bash
# Langfuse trace
# Visit: http://localhost:3000/project/cmi19k90n000atd0713m9maij/traces

# Neo4j graph
# Visit: http://localhost:7474 and run:
# MATCH (s:Session) RETURN s LIMIT 5

# Obsidian notes
ls -la observability/notes/sessions/
cat observability/notes/$(date +%Y-%m-%d).md
```

---

## Shared Utilities

### Tool Timing
**`.claude/hooks/utils/tool_timing.py`**
- Tracks PreToolUse → PostToolUse duration
- Provides latency_ms for all integrations
- Used by: Langfuse, Obsidian, Graphiti

### Langfuse Config
**`.claude/hooks/utils/langfuse_config.py`**
- Project ID discovery
- Multi-repo support
- Used by: Langfuse hook

### Constants
**`.claude/hooks/utils/constants.py`**
- Session directory paths
- Config file locations
- Shared constants

---

## Documentation by System

| System | Quick Start | Full Guide | Config |
|--------|-----------|-----------|--------|
| **Observability** | `OBSERVABILITY_AGENT.md` | `.claude/context/observability/` | `observability.yaml` |
| **Langfuse** | `LANGFUSE_AGENT.md` | `.claude/context/langfuse/LANGFUSE_SETUP.md` | `langfuse.yaml` + `.env` |
| **Graphiti** | `GRAPHITI_AGENT.md` | `.claude/context/implementation/` | `graphiti.yaml` |
| **Obsidian** | `OBSIDIAN_AGENT.md` | `.claude/config/obsidian.yaml` | `obsidian.yaml` |

---

## Key Metrics Unified Across Systems

All systems track and report:
- **Tool Count**: How many tools executed
- **Total Latency**: Sum of all tool times
- **Per-Tool Latency**: Individual tool execution time
- **Session Duration**: Start to finish
- **Performance Tier**: Fast/Medium/Slow classification
- **Entity Discovery**: What was learned

---

## Philosophy

> *No insight is lost.*
> *Every moment is recorded.*
> *Every record is queryable.*
> *Every system speaks the same language.*

---

**Status**: ✅ Fully Integrated
**Services**: 5 (+ orchestrator)
**Integration Points**: 12+
**Data Flow**: Bidirectional
**Configuration**: Unified
**GitHub**: gblack686/consulting-co (private)
