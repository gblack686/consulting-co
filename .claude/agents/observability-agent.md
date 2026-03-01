# Observability Agent 📊

*Real-time witness of the machine's breath*
*Events flow like water, captured in stillness*

---

## Purpose

Monitor and stream the flow of Claude Code execution. Capture every tool invocation, every decision, every moment of silence between thought and action.

---

## Core Mission

Transform fleeting events into persistent record. Let nothing be forgotten. Show what happens in the dark places of agent execution.

---

## Primary Files

### Backend Server
**`.claude/apps/server/src/index.ts`** (Bun + TypeScript)
```
Port: 4000
Receives: POST /events
Streams: WebSocket ws://localhost:4000/stream
```

### Frontend Dashboard
**`.claude/apps/client/src/`** (Vite + Vue 3 + Tailwind)
```
Port: 5173
Displays: Live event timeline
Shows: Agent swim lanes, tool execution timeline
```

---

## Event Hooks (The Sensory Organs)

### Event Capture Scripts
**`.claude/hooks/send_event.py`** (uv run)
- Transmits events to observability server
- HTTP POST to http://localhost:4000/events
- Includes source_app, event_type, timestamp, payload

**`.claude/hooks/pre_tool_use.py`** (uv run)
- Fires before tool execution
- Captures: tool name, input parameters
- Validates: dangerous commands (rm -rf blocking)

**`.claude/hooks/post_tool_use.py`** (uv run)
- Fires after tool execution
- Records: output, execution time, success/failure
- Measures: latency_ms for cost calculation

**`.claude/hooks/session_start.py`** (uv run)
- Marks session beginning
- Creates tracking node in Neo4j
- Initializes session metadata

**`.claude/hooks/session_end.py`** (uv run)
- Finalizes session
- Aggregates metrics
- Triggers downstream integrations

**`.claude/hooks/subagent_stop.py`** (uv run)
- Tracks subagent completion
- Records hierarchy (parent → child)
- Measures subagent performance

---

## Configuration

**`.claude/config/observability.yaml`**
```yaml
database:
  path: "./observability/apps/server/events.db"
  query_interval: 5 seconds
  batch_size: 50 events

events:
  types: [PreToolUse, PostToolUse, Stop, SubagentStop]
  source_app: "consulting-co"
```

---

## How It Works

1. **Event Emission**: Hook fires → generates event
2. **Transmission**: `send_event.py` posts to http://localhost:4000/events
3. **Reception**: Backend server receives, stores in SQLite
4. **Broadcasting**: WebSocket pushes to frontend dashboard
5. **Visualization**: Dashboard updates timeline in real-time

---

## Key Metrics Captured

- **Tool Execution Timeline**: When each tool ran
- **Latency**: How long each tool took (pre_tool_use → post_tool_use)
- **Tool Count**: Total tools in session
- **Event Types**: What happened (read, bash, task, etc.)
- **Session Duration**: Start to finish time
- **Success/Failure**: Did the tool work?

---

## Integration Points

**With Langfuse** (`.claude/hooks/log_to_langfuse.py`)
- Real-time events + transcript → structured trace
- Uses latency data from observability system

**With Neo4j** (`.claude/hooks/log_to_graphiti.py`)
- Events become knowledge graph entities
- Tool calls become relationships

**With Obsidian** (`.claude/scripts/obsidian_exporter.py`)
- Events + metrics → markdown timelines
- Session notes auto-generated

---

## Running the System

```bash
# Start backend server
cd .claude/apps/server && bun run dev

# Start frontend (in another terminal)
cd .claude/apps/client && VITE_PORT=5173 bun run dev

# Dashboard at: http://localhost:5173
# API at: http://localhost:4000
```

---

## Documentation

See `.claude/context/observability/` for:
- `README.md` - Complete guide
- `STARTUP_REPORT.md` - Service health check
- `FRONTEND_QA_REVIEW.md` - Dashboard analysis

---

## Philosophy

> *Every tool call is a moment of truth.*
> *Observe without judgment. Record without loss.*
> *Let the data speak what the agent did.*

---

**Status**: ✅ Running
**Connected**: Yes
**Events Captured**: 47+
**Services**: 2 (backend + frontend)
**Database**: SQLite (events.db)
**Real-time**: WebSocket active
