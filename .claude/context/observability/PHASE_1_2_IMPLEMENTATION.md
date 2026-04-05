# Phase 1 & 2 Implementation: Enhanced Langfuse Tracing

## Overview

Phases 1 and 2 of the Langfuse upgrade plan have been implemented. The system now captures all hook events and constructs multi-event traces with tool invocations, user prompts, and subagent executions.

**Status**: ✅ COMPLETE - Ready for Testing

---

## Phase 1: Enhanced Event Capture

### What Was Implemented

**New File**: `.claude/hooks/utils/event_buffer.py`
- In-memory event buffering per session
- Automatic disk persistence to `~/.claude/logs/event_buffer_*.json`
- CLI tools for debugging and inspection
- Automatic cleanup after trace sent

**Modified**: `.claude/hooks/log_to_langfuse.py`
- Now captures ALL hook events (not just Stop)
- Buffers events until Stop event received
- Passes all buffered events to trace construction
- Clears buffer after successful Langfuse send

### Event Types Captured

```
SessionStart
├─ UserPromptSubmit
├─ PreToolUse
├─ PostToolUse (paired with PreToolUse)
├─ SubagentStop
└─ Stop (trigger for trace send)
```

### Phase 1 Metadata Added to Trace

```json
{
  "total_events_buffered": 7,
  "event_types_captured": {
    "PreToolUse": 2,
    "PostToolUse": 2,
    "Stop": 1
  }
}
```

### Event Buffer Persistence

Events are saved to disk immediately upon receipt:

```
~/.claude/logs/
├── event_buffer_session_abc123.json
├── event_buffer_session_def456.json
└── event_buffer_session_xyz789.json
```

Each file contains:
```json
[
  {
    "hook_event_type": "PreToolUse",
    "session_id": "session_abc123",
    "timestamp": "2025-11-16T10:00:05Z",
    "hook_data": { ... }
  },
  { ... }
]
```

### Phase 1 CLI Tools

**List all buffered sessions:**
```bash
python3 .claude/hooks/utils/event_buffer.py list
```

**View session summary:**
```bash
python3 .claude/hooks/utils/event_buffer.py summary --session-id <id>
```

**Export events to file:**
```bash
python3 .claude/hooks/utils/event_buffer.py export --session-id <id> --output events.json
```

**Clear session buffer:**
```bash
python3 .claude/hooks/utils/event_buffer.py clear --session-id <id>
```

---

## Phase 2: Multi-Event Trace Construction

### What Was Implemented

**New File**: `.claude/hooks/utils/trace_builder.py`
- Parses buffered events into structured observations
- Matches PreToolUse/PostToolUse pairs
- Extracts user prompts and subagent executions
- Generates Langfuse-compatible observations

**Modified**: `.claude/hooks/log_to_langfuse.py`
- Integrates TraceBuilder when `ENABLE_ENHANCED_TRACING=true`
- Creates observations from matched events
- Falls back to old trace structure if flag disabled

### Event-to-Observation Mapping

#### User Prompts
```
UserPromptSubmit event
    ↓
SPAN: "user-prompt"
  input: user message text
  metadata:
    event_type: UserPromptSubmit
    timestamp: event timestamp
```

#### Tool Invocations
```
PreToolUse + PostToolUse (matched pair)
    ↓
SPAN: "tool-{tool_name}-{sequence}"
  input: tool input (JSON)
  output: tool output (truncated)
  metadata:
    event_type: ToolInvocation
    tool_name: Bash
    sequence_number: 1
    latency_ms: 234
    status: success
    error_message: null
```

#### Subagent Executions
```
SubagentStop event
    ↓
SPAN: "subagent-{session_id[:12]}"
  metadata:
    event_type: SubagentExecution
    subagent_session_id: session_def456
    parent_session_id: session_abc123
    child_trace_id: session_def456  (links to child trace)
    hierarchy_depth: 1
    purpose: reason for subagent call
    outcome: result of execution
```

### Trace Structure (Phase 2)

```
Trace: consulting-co-conversation
├── SPAN: user-prompt
│   input: "List files and read README"
├── GENERATION: claude-response
│   output: "I found the following files..."
├── SPAN: tool-Bash-1
│   input: { "command": "ls -la" }
│   output: "file1.py\nfile2.py\n..."
├── SPAN: tool-Read-2
│   input: { "file_path": "README.md" }
│   output: "# Project\nThis is a readme..."
└── SPAN: subagent-session_def456
    metadata.child_trace_id: session_def456
```

### Phase 2 CLI Tools

**Analyze session events:**
```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <id>
```

**Export observations:**
```bash
python3 .claude/hooks/utils/trace_builder.py export --session-id <id> --output observations.json
```

---

## Configuration

### Enable Enhanced Tracing

In `.env`:
```bash
ENABLE_ENHANCED_TRACING=true    # Enable Phase 2 trace building
ENABLE_LANGFUSE=true            # Enable Langfuse logging
```

### Disable for Backward Compatibility

```bash
ENABLE_ENHANCED_TRACING=false   # Uses old simple trace structure
ENABLE_LANGFUSE=true            # Still captures but simpler format
```

---

## How It Works: Complete Flow

### Step 1: Event Buffering (Phase 1)

```
Hook triggered (ANY event type)
    ↓
log_to_langfuse.py receives event
    ↓
Buffer event in memory + save to disk
    ↓
If event type != Stop → Return (wait for more events)
If event type == Stop → Proceed to Step 2
```

**Debug output:**
```
🔔 Hook called at 2025-11-16T10:00:05Z
📥 Hook data received:
  - Session ID: session_abc123
  - Event: PreToolUse
  - Transcript: /path/to/transcript.jsonl
📌 Buffered event: PreToolUse
   Total events in session: 1
⏭️  Buffering for later trace construction
```

### Step 2: Trace Construction (Phase 2)

```
Stop event received
    ↓
Load ALL buffered events for session
    ↓
If ENABLE_ENHANCED_TRACING == true:
    ├─ Create TraceBuilder
    ├─ Match PreToolUse/PostToolUse pairs
    ├─ Extract user prompts
    ├─ Extract subagent executions
    └─ Generate observations
Else:
    └─ Use simple trace (backward compatible)
    ↓
Create Langfuse trace with observations
    ↓
Clear event buffer from disk
```

**Debug output:**
```
🛑 Stop event received - building trace from buffered events
📋 Buffered events: 7
🔨 PHASE 2: Building enhanced trace from 7 events
📊 Generated 3 observations from events
  ✓ Created SPAN: user-prompt
  ✓ Created SPAN: tool-Bash-1
  ✓ Created SPAN: tool-Read-2
✅ Successfully logged to Langfuse
🗑️  Clearing event buffer for session
```

### Step 3: Langfuse Trace

Trace appears in Langfuse with structure:
```
Trace ID: session_abc123
Name: consulting-co-conversation
Tags: [consulting-co, claude-code, conversation]
Metadata:
  organization: consulting-co
  project: consulting-co
  total_events_buffered: 7
  event_types_captured: {PreToolUse: 2, PostToolUse: 2, ...}

Observations:
  1. SPAN: user-prompt
  2. GENERATION: claude-response
  3. SPAN: tool-Bash-1
  4. SPAN: tool-Read-2
```

---

## Testing Phase 1 & 2

### Prerequisites

- Langfuse running at http://localhost:3000
- `.env` configured with `ENABLE_LANGFUSE=true` and `ENABLE_ENHANCED_TRACING=true`
- Event buffer directory exists: `~/.claude/logs/`

### Test 1: Simple Conversation (No Tools)

**Command:**
```
"What is 2+2?"
```

**Expected:**
- ✓ Event buffer created
- ✓ Trace sent to Langfuse
- ✓ Trace includes user-prompt and claude-response
- ✓ total_events_buffered = 1 (Stop event)

**Verify:**
```bash
# Check event buffer
python3 .claude/hooks/utils/event_buffer.py list

# View trace in Langfuse
http://localhost:3000/project/cmi19k90n000atd0713m9maij/traces
```

### Test 2: Tool Usage

**Command:**
```
"List files in the current directory"
```

**Expected:**
- ✓ Multiple events buffered (PreToolUse, PostToolUse, etc.)
- ✓ Tool span created with:
  - tool_name: Bash
  - latency_ms: execution time
  - status: success/error
  - input/output captured
- ✓ Trace in Langfuse shows tool invocation

**Verify:**
```bash
# Analyze events
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>

# View in Langfuse - should see tool-Bash-1 span
```

### Test 3: Multiple Tools

**Command:**
```
"Read the README.md file and count the lines"
```

**Expected:**
- ✓ PreToolUse, PostToolUse events buffered for multiple tools
- ✓ Tool pairs matched correctly:
  - tool-Bash-1 (read command)
  - tool-Read-1 (file read)
  - tool-Bash-2 (wc command)
- ✓ Sequence numbers increment correctly
- ✓ Each tool span has correct latency_ms

**Verify:**
```bash
# Check tool breakdown
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>
# Should show:
# Tool Breakdown:
#   Bash: 2
#   Read: 1
```

### Test 4: Error Handling

**Command:**
```
"Try to read a non-existent file"
```

**Expected:**
- ✓ PostToolUse event has error information
- ✓ Tool span created with:
  - status: "error"
  - error_message: reason for failure
- ✓ Trace in Langfuse shows error status

**Verify:**
```bash
# Export events and check for error
python3 .claude/hooks/utils/event_buffer.py export --session-id <session_id> --output events.json
# Check for error field in post_event
```

---

## Debug Log Format

Location: `.claude/langfuse_hook_debug.log`

### Phase 1 Entry
```
============================================================
🔔 Hook called at 2025-11-16T10:00:05Z
📥 Hook data received:
  - Session ID: session_abc123
  - Event: PreToolUse
  - Transcript: /path/to/transcript.jsonl
📌 Buffered event: PreToolUse
   Total events in session: 1
⏭️  Buffering for later trace construction
```

### Phase 2 Entry
```
============================================================
🔔 Hook called at 2025-11-16T10:00:10Z
📥 Hook data received:
  - Session ID: session_abc123
  - Event: Stop
  - Transcript: /path/to/transcript.jsonl
📌 Buffered event: Stop
   Total events in session: 7
🛑 Stop event received - building trace from buffered events
📋 Buffered events: 7
🔨 PHASE 2: Building enhanced trace from 7 events
📊 Generated 3 observations from events
  ✓ Created SPAN: user-prompt
  ✓ Created SPAN: tool-Bash-1
  ✓ Created SPAN: tool-Read-2
✅ Successfully logged to Langfuse
🗑️  Clearing event buffer for session
```

---

## Known Limitations & Next Steps

### Current Limitations

1. **Simple observation structure**: Observations are created as basic SPAN/GENERATION types
2. **No nested subagents**: Subagent support is planned but not yet capturing child execution details
3. **Event type detection**: Only recognizes standard hook events; custom events would need addition

### Future Phases

**Phase 3**: Subagent Support
- Create linked traces for parent-child relationships
- Track hierarchy depth
- Auto-create child traces for subagent sessions

**Phase 4**: Enhanced Metadata
- Add agent_id and source_app tracking
- Capture tool input/output summaries
- Track error states and recovery

**Phase 5**: Dashboard Integration
- Real-time event streaming via WebSocket
- Cost tracking and optimization
- Performance analytics

---

## Troubleshooting

### Events not being buffered

**Check:**
1. `ENABLE_LANGFUSE=true` in `.env`
2. Hook file exists: `.claude/hooks/log_to_langfuse.py`
3. Event buffer directory exists: `~/.claude/logs/`

**Fix:**
```bash
mkdir -p ~/.claude/logs/
```

### Trace not appearing in Langfuse

**Check:**
1. `LANGFUSE_BASE_URL` is correct (http://localhost:3000)
2. Langfuse is running: `curl http://localhost:3000`
3. API credentials are correct in `.env`

**Debug:**
```bash
tail -100 .claude/langfuse_hook_debug.log
```

### TraceBuilder errors

**Check:**
1. `ENABLE_ENHANCED_TRACING=true` in `.env`
2. `trace_builder.py` exists in `.claude/hooks/utils/`
3. Events buffer is valid JSON

**Debug:**
```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>
```

---

## Summary

✅ **Phase 1 Complete**: Event buffering and persistence working
✅ **Phase 2 Complete**: Multi-event trace construction implemented
✅ **Configuration**: Enhanced tracing enabled in .env
⏭️ **Ready for**: Testing and Phase 3 (Subagent Support)

**Next Action**: Run test conversations to validate Phase 1 & 2 implementation

---

**Implementation Date**: 2025-11-16
**Status**: Ready for Testing
**Version**: 1.0
