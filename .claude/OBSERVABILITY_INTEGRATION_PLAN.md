# Observability Integration Plan for consulting-co

## Overview
Integrating the multi-agent observability system (from `/observability`) into the main `consulting-co` project's `.claude` directory.

## Integration Strategy

### Current State (consulting-co)
- **Existing hooks**: `log_to_langfuse.py`, `log_to_graphiti.py`, `pre_tool_use.py`, `post_tool_use.py`
- **Hook type**: Only `Stop` hook registered in `settings.local.json`
- **Limitation**: Batch logging only at end of conversation, no real-time visibility

### Target State
- **Add observability hooks**: `send_event.py`, `session_start.py`, `session_end.py`, `pre_tool_use.py`, `post_tool_use.py`, `user_prompt_submit.py`, `notification.py`, `subagent_stop.py`, `pre_compact.py`
- **Add hook utilities**: `utils/` directory with summarizer, model extractor, etc.
- **Update settings.json**: Register PreToolUse, PostToolUse, SessionStart, SessionEnd, SubagentStop hooks
- **Benefit**: Real-time event streaming, per-tool latency tracking, subagent observability

## Files to Copy from `/observability/.claude/hooks/`

### Core Hooks (NEW - Real-time tracking)
- `send_event.py` - Universal event sender to observability server
- `pre_tool_use.py` - REPLACE existing with security checks + event sending
- `post_tool_use.py` - REPLACE existing with result logging + event sending
- `session_start.py` - Track session initialization
- `session_end.py` - Track session completion and aggregates
- `user_prompt_submit.py` - Capture user prompts
- `notification.py` - Capture system notifications
- `subagent_stop.py` - Track subagent execution and completion

### Supporting Files
- `utils/` directory with:
  - `constants.py` - Session directory management
  - `summarizer.py` - Event summary generation (uses Claude API)
  - `model_extractor.py` - Extract model name from transcript

### Backup Existing Hooks (SAFETY)
Before integration, backup existing hooks:
- `.claude/hooks/pre_tool_use.py` → `.claude/hooks/pre_tool_use.py.bak`
- `.claude/hooks/post_tool_use.py` → `.claude/hooks/post_tool_use.py.bak`

## Integration Steps

### 1. Copy Hook Scripts
Copy all hooks from `/observability/.claude/hooks/` to `.claude/hooks/`

### 2. Copy Utils Directory
Copy `/observability/.claude/hooks/utils/` to `.claude/hooks/utils/`

### 3. Update settings.local.json
Add new hook registrations for:
- PreToolUse (with security + event sending)
- PostToolUse (with event sending)
- SessionStart (new)
- SessionEnd (new)
- UserPromptSubmit (new)
- Notification (new)
- SubagentStop (new)

### 4. Configuration
Set environment variables in settings.local.json:
```json
{
  "env": {
    "ENABLE_LANGFUSE": "true",
    "OBSERVABILITY_SERVER": "http://localhost:4000",
    "SOURCE_APP": "consulting-co",
    "PROJECT_NAME": "consulting-co"
  }
}
```

### 5. Server Setup (EXTERNAL)
The observability server must be running separately:
```bash
cd observability/apps/server
bun install
bun run dev
# Server runs on http://localhost:4000
```

### 6. Dashboard (EXTERNAL)
Optionally run the dashboard:
```bash
cd observability/apps/client
npm install
npm run dev
# Dashboard runs on http://localhost:5173
```

## Benefits of This Integration

### Real-Time Observability
- ✅ PreToolUse fires BEFORE tool execution (capture start)
- ✅ PostToolUse fires AFTER tool execution (capture latency)
- ✅ Events stream to server as they happen
- ✅ Dashboard updates live

### Per-Tool Metrics
- ✅ Tool name, input, output captured
- ✅ Start/end timestamps recorded
- ✅ Latency calculated automatically (end_time - start_time)
- ✅ Tool breakdown in dashboard

### Subagent Tracking
- ✅ SubagentStop hook fires when Task tool spawns subagent
- ✅ Subagent execution tracked in separate session
- ✅ Parent → child session linking via source_app:session_id

### Security
- ✅ pre_tool_use.py blocks dangerous `rm -rf` commands
- ✅ Blocks .env file access (can whitelist)
- ✅ Validates bash commands before execution

## Compatibility Notes

### Coexistence with Existing Hooks
- `log_to_langfuse.py` - KEEP (Stop hook for batch logging)
- `log_to_graphiti.py` - KEEP (Stop hook for Graphiti integration)
- `pre_tool_use.py` - REPLACE with observability version (security + real-time)
- `post_tool_use.py` - REPLACE with observability version (event streaming)

### Hook Execution Flow
```
Claude Code → MultiHook Execution:
├─ Pre/PostToolUse: pre_tool_use.py → send_event.py → Server
└─ Stop: log_to_langfuse.py + log_to_graphiti.py → Cloud services
```

## Rollback Plan

If integration causes issues:
1. Restore backed up hooks: `cp .claude/hooks/*.bak .claude/hooks/`
2. Revert settings.local.json: Remove PreToolUse/PostToolUse entries
3. Keep only Stop hook registered
4. Restart Claude Code

## Next Steps

1. Execute integration plan
2. Start observability server
3. Run test command in Claude Code
4. Verify events in dashboard/database
5. Enable additional hooks as needed

## Server Requirements

- **Observability Server**: Must be running at `http://localhost:4000`
  - Receives events at `/events` endpoint
  - Stores in SQLite database
  - Broadcasts via WebSocket

- **Optional Dashboard**: `http://localhost:5173`
  - Real-time event visualization
  - Filtering and aggregation
  - Chat transcript viewer
