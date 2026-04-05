# Observability Quick Start Guide

**Time Required:** 5 minutes

---

## Prerequisites

✅ **consulting-co** project has observability hooks integrated (Done!)
✅ **observability** repository cloned at `../observability/` (Exists!)

---

## Step 1: Start the Observability Server

```bash
# Terminal 1: Start the event server
cd observability/apps/server
npm install    # First time only
npm run dev

# You should see:
# ✓ Server running at http://localhost:4000
```

The server will:
- Listen for events at `http://localhost:4000/events`
- Store events in SQLite database
- Broadcast updates via WebSocket on port 4000

---

## Step 2 (Optional): Start the Dashboard

```bash
# Terminal 2: Start the visualization dashboard
cd observability/apps/client
npm install    # First time only
npm run dev

# You should see:
# ✓ Dashboard at http://localhost:5173
```

Open http://localhost:5173 in your browser to see real-time events.

---

## Step 3: Test the Integration

```bash
# Terminal 3: Use Claude Code in consulting-co project
cd consulting-co
claude code

# In Claude Code, run a command that uses tools:
# Example: Find and read a file
find . -name "*.md" -type f | head -5
```

---

## What You'll See

### Real-Time Events (Server Terminal)
```
✅ PreToolUse event received: {source_app: "consulting-co", event_type: "PreToolUse", ...}
✅ PostToolUse event received: {source_app: "consulting-co", event_type: "PostToolUse", latency_ms: 2667, ...}
```

### In Dashboard (Browser at http://localhost:5173)
```
Live Event Stream:
├─ [ConsultingCo:abc123ab] SessionStart
├─ [ConsultingCo:abc123ab] PreToolUse (Read)
├─ [ConsultingCo:abc123ab] PostToolUse (Read) - 2667ms
├─ [ConsultingCo:abc123ab] PreToolUse (Bash)
├─ [ConsultingCo:abc123ab] PostToolUse (Bash) - 2249ms
└─ [ConsultingCo:abc123ab] Stop
```

### Server Database (SQLite)
```bash
# Check stored events
cd observability/apps/server
sqlite3 events.db "SELECT source_app, hook_event_type, latency FROM events LIMIT 5;"

# Output:
# consulting-co|PreToolUse|...
# consulting-co|PostToolUse|2667
# consulting-co|PreToolUse|...
# consulting-co|PostToolUse|2249
```

---

## Key Metrics You Can Now Track

### Per-Tool Latency
- **When:** Every time a Claude Code tool executes (Read, Bash, Grep, Write, Task, etc.)
- **What:** Start time, end time, execution duration
- **Where:** Dashboard shows live; database stores historical

### Tool Breakdown
- **Session Total:** Sum of all tool latencies in a session
- **Tool Count:** Number of tools executed
- **By Tool:** Latency breakdown for each tool type

### Subagent Execution
- **When:** Task tool spawns a subagent
- **What:** Subagent session ID, completion status, output
- **Where:** SubagentStop events show parent-child relationship

### User Interactions
- **User Prompts:** Captured via UserPromptSubmit hook
- **System Events:** Notifications and status changes
- **Context Compaction:** When Claude compacts conversation history

---

## Understanding Event Payloads

### PreToolUse Event
```json
{
  "source_app": "consulting-co",
  "session_id": "abc123ab",
  "hook_event_type": "PreToolUse",
  "timestamp": 1731704400000,
  "payload": {
    "tool_name": "Read",
    "tool_input": {
      "file_path": "/path/to/file.txt"
    },
    "session_id": "abc123ab"
  }
}
```

### PostToolUse Event
```json
{
  "source_app": "consulting-co",
  "session_id": "abc123ab",
  "hook_event_type": "PostToolUse",
  "timestamp": 1731704402667,
  "payload": {
    "tool_name": "Read",
    "tool_output": {
      "status": "success",
      "lines_read": 50,
      "preview": "File contents..."
    },
    "latency_ms": 2667,
    "session_id": "abc123ab"
  }
}
```

### Stop Event (with Chat)
```json
{
  "source_app": "consulting-co",
  "session_id": "abc123ab",
  "hook_event_type": "Stop",
  "timestamp": 1731704410000,
  "summary": "User asked to read a file, then run a grep search",
  "chat": [
    {"role": "user", "content": "read the main file..."},
    {"role": "assistant", "content": "I'll read the file..."}
  ],
  "payload": {
    "tool_count": 2,
    "total_latency_ms": 4916,
    "tools_used": ["Read", "Bash"]
  }
}
```

---

## Filtering in Dashboard

The dashboard allows filtering by:

### Source App
- Shows only events from specific applications
- Example: "consulting-co" to see only this project's events

### Session ID
- Shows only events from a specific Claude Code session
- Format: "consulting-co:abc123ab" (first 8 chars of session)

### Event Type
- PreToolUse, PostToolUse, Stop, SessionStart, SubagentStop, etc.
- Filter to see only tool execution events

### Example Filters
```
View all tool executions:
  Source App: consulting-co
  Event Type: PreToolUse, PostToolUse

View subagent behavior:
  Source App: consulting-co
  Event Type: SubagentStop

View entire session:
  Session ID: abc123ab
  Event Type: All
```

---

## Querying the Database

```bash
# Connect to SQLite
cd observability/apps/server
sqlite3 events.db

# Get all events for a session
SELECT hook_event_type, timestamp, payload
FROM events
WHERE source_app = 'consulting-co'
ORDER BY timestamp;

# Get average tool latency
SELECT hook_event_type, AVG(json_extract(payload, '$.latency_ms')) as avg_latency
FROM events
WHERE hook_event_type = 'PostToolUse'
GROUP BY hook_event_type;

# Get slowest tools
SELECT hook_event_type,
       json_extract(payload, '$.tool_name') as tool_name,
       json_extract(payload, '$.latency_ms') as latency
FROM events
ORDER BY latency DESC
LIMIT 10;
```

---

## Common Issues & Solutions

### Server Not Receiving Events

**Problem:** Events not appearing in dashboard
**Solution:**
1. Verify server running: `curl http://localhost:4000/events`
2. Check Claude Code console for errors
3. Ensure hook files have execute permissions: `ls -la .claude/hooks/*.py`

### Dashboard Not Updating

**Problem:** Events in database but not showing in dashboard
**Solution:**
1. Check WebSocket connection: Open browser dev tools → Network tab
2. Verify client running on http://localhost:5173
3. Try refreshing dashboard (Cmd+R or Ctrl+Shift+R)

### Hook Scripts Failing

**Problem:** Hooks run but produce errors
**Solution:**
1. Check hook implementation in `.claude/hooks/`
2. Verify environment variables set in `settings.local.json`
3. Look for Python syntax errors: `python -m py_compile .claude/hooks/send_event.py`

---

## Next Steps

### Immediate
1. ✅ Start server: `npm run dev` in `observability/apps/server`
2. ✅ Start dashboard: `npm run dev` in `observability/apps/client`
3. ✅ Run a Claude Code tool and watch events stream

### Short Term (10 min)
- [ ] Test with different tool types (Read, Bash, Grep, Write)
- [ ] Check latency metrics for your workflow
- [ ] Verify Langfuse still receiving batch events

### Medium Term (1 hour)
- [ ] Set up automated performance monitoring
- [ ] Create alerts for slow tools (>5000ms)
- [ ] Analyze subagent execution patterns

### Long Term
- [ ] Integrate with your CI/CD for agent performance tracking
- [ ] Build custom dashboards for specific workflows
- [ ] Use event data for agent optimization

---

## Architecture Overview

```
Your Project (consulting-co)
    ↓ (runs with hooks)
Claude Code
    ↓ (executes)
Hooks (Python scripts)
    ├─ pre_tool_use.py → sends event
    ├─ post_tool_use.py → sends event + latency
    └─ send_event.py → HTTP POST
    ↓
Observability Server (Bun)
    ├─ Receives POST /events
    ├─ Stores in SQLite
    └─ Broadcasts via WebSocket
    ↓
Real-Time Dashboard (Vue 3)
    ├─ Connects via WebSocket
    ├─ Filters events
    └─ Shows live metrics
```

---

## Performance Tips

### Reduce Event Volume
If server is overwhelmed, modify `settings.local.json`:
```json
{
  "hooks": {
    "PreToolUse": [{
      "hooks": [
        {"type": "command", "command": "uv run .claude/hooks/pre_tool_use.py"}
        // Remove send_event.py to disable real-time posting
      ]
    }]
  }
}
```

### Batch Events
Stop hook still fires at end of session, batching all events:
```bash
# Only Stop hook fires (batch mode)
# Remove PreToolUse/PostToolUse hooks from settings
```

---

## Summary

You now have:
- ✅ Real-time event streaming for all Claude Code operations
- ✅ Per-tool latency measurement and tracking
- ✅ Live dashboard visualization
- ✅ Historical database of all events
- ✅ Backwards compatibility with Langfuse and Graphiti
- ✅ Subagent execution visibility
- ✅ Security validation of dangerous commands

**Start the server and run a tool to see it in action!**

```bash
npm run dev  # In observability/apps/server
```
