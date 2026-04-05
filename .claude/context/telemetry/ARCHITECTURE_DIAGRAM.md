# OpenTelemetry Telemetry Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE SESSION                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Session Start
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         session_start.py HOOK                                │
│                                                                              │
│  1. Generate trace_id (32-char hex UUID)                                   │
│  2. Generate root_span_id (16-char hex UUID)                               │
│  3. Create Langfuse trace & root span                                      │
│  4. Save to: ~/.claude/trace_context/{session_id}.json                     │
│                                                                              │
│  Context Saved:                                                             │
│  {                                                                           │
│    "trace_id": "a1b2c3d4...",                                              │
│    "root_span_id": "1234567890abcdef",                                     │
│    "session_id": "...",                                                    │
│    "created_at": "..."                                                     │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ User interacts with Claude
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TOOL EXECUTION LOOP                               │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              pre_tool_use.py HOOK                             │          │
│  │                                                                │          │
│  │  1. Read trace context from file                             │          │
│  │  2. Extract: trace_id, root_span_id                          │          │
│  │  3. Generate new span_id for this tool                       │          │
│  │  4. Create child span in Langfuse:                           │          │
│  │     - trace_id: from parent                                  │          │
│  │     - parent_observation_id: root_span_id                    │          │
│  │     - id: new span_id                                        │          │
│  │     - start_time: now()                                      │          │
│  │     - metadata: {tool_name, tool_input}                      │          │
│  │  5. Store span reference:                                    │          │
│  │     ~/.claude/trace_context/{session_id}_spans.json         │          │
│  │                                                               │          │
│  │  Span Reference:                                             │          │
│  │  {                                                            │          │
│  │    "Read_2025-01-15T10:30:15.123Z": {                       │          │
│  │      "span_id": "abc123def4567890",                         │          │
│  │      "tool_name": "Read",                                   │          │
│  │      "start_time": "2025-01-15T10:30:15.123Z",             │          │
│  │      "end_time": null,                                      │          │
│  │      "status": "pending"                                    │          │
│  │    }                                                         │          │
│  │  }                                                           │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                              ↓                                               │
│                    [TOOL EXECUTES]                                          │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │             post_tool_use.py HOOK                             │          │
│  │                                                                │          │
│  │  1. Read trace context                                       │          │
│  │  2. Find pending span for this tool                          │          │
│  │  3. Calculate latency: now() - start_time                    │          │
│  │  4. Update span in Langfuse:                                 │          │
│  │     - trace_id: from context                                 │          │
│  │     - id: span_id from pending span                          │          │
│  │     - end_time: now()                                        │          │
│  │     - metadata: {tool_output, latency_ms}                    │          │
│  │  5. Mark span as "completed"                                 │          │
│  │  6. Flush to Langfuse                                        │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                              ↓                                               │
│                  [Repeat for each tool]                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Session End
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          session_end.py HOOK                                 │
│                                                                              │
│  1. Read all child spans from {session_id}_spans.json                      │
│  2. Calculate summary:                                                      │
│     - tool_count: count(all spans)                                         │
│     - total_tool_latency_ms: sum(all latencies)                           │
│     - tool_breakdown: per-tool stats                                       │
│  3. Update root span with summary                                          │
│  4. Update trace with final metadata                                       │
│  5. Flush to Langfuse                                                      │
│  6. Clean up session files                                                 │
│                                                                             │
│  Summary Example:                                                           │
│  {                                                                          │
│    "tool_count": 5,                                                        │
│    "total_tool_latency_ms": 1250,                                         │
│    "tool_breakdown": {                                                     │
│      "Read": {"count": 2, "total_latency_ms": 800},                       │
│      "Bash": {"count": 2, "total_latency_ms": 350},                       │
│      "Grep": {"count": 1, "total_latency_ms": 100}                        │
│    }                                                                       │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LANGFUSE CLOUD UI                                    │
│                                                                              │
│  Trace: claude-session-{session_id}                                        │
│  ├─ Root Span: claude-session-root                                         │
│  │  ├─ metadata: {tool_count, total_latency, breakdown}                   │
│  │  └─ duration: session_end - session_start                              │
│  │                                                                          │
│  └─ Child Spans:                                                           │
│     ├─ tool-Read (span_id: abc...)                                        │
│     │  ├─ parent: root_span_id                                            │
│     │  ├─ metadata: {tool_input, tool_output, latency_ms}                │
│     │  └─ duration: 800ms                                                 │
│     │                                                                      │
│     ├─ tool-Bash (span_id: def...)                                        │
│     │  ├─ parent: root_span_id                                            │
│     │  ├─ metadata: {tool_input, tool_output, latency_ms}                │
│     │  └─ duration: 350ms                                                 │
│     │                                                                      │
│     └─ tool-Grep (span_id: ghi...)                                        │
│        ├─ parent: root_span_id                                            │
│        ├─ metadata: {tool_input, tool_output, latency_ms}                │
│        └─ duration: 100ms                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────┐
│  Claude Session  │
└────────┬─────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │                                                      │
         ↓                                                      ↓
┌──────────────────┐                              ┌────────────────────┐
│  Session Start   │                              │   Langfuse Cloud   │
│  Hook            │────── Create Trace ─────────→│                    │
└────────┬─────────┘                              │  - Root Trace      │
         │                                         │  - Root Span       │
         ↓                                         └────────────────────┘
┌──────────────────┐
│  Trace Context   │
│  File System     │
│                  │
│  {session}.json  │  ← Root trace context
│  {session}_      │  ← Child span references
│    spans.json    │
└────────┬─────────┘
         │
         │ Read Context
         ↓
┌──────────────────┐                              ┌────────────────────┐
│  Pre-Tool-Use    │                              │   Langfuse Cloud   │
│  Hook            │──── Create Child Span ──────→│                    │
└────────┬─────────┘                              │  - Links to parent │
         │                                         │  - Records input   │
         │ Store Span Ref                          │  - Starts timer    │
         ↓                                         └────────────────────┘
┌──────────────────┐
│  Trace Context   │
│  File System     │
│                  │
│  Span reference  │  ← New pending span
│  added           │
└────────┬─────────┘
         │
         │ [Tool Executes]
         │
         ↓
┌──────────────────┐
│  Post-Tool-Use   │                              ┌────────────────────┐
│  Hook            │                              │   Langfuse Cloud   │
│                  │──── Update Child Span ──────→│                    │
│  - Find pending  │                              │  - Records output  │
│    span          │                              │  - Ends timer      │
│  - Calculate     │                              │  - Saves latency   │
│    latency       │                              └────────────────────┘
└────────┬─────────┘
         │
         │ Update Status
         ↓
┌──────────────────┐
│  Trace Context   │
│  File System     │
│                  │
│  Span marked     │  ← Status: completed
│  completed       │
└────────┬─────────┘
         │
         │ [Repeat for each tool]
         │
         ↓
┌──────────────────┐                              ┌────────────────────┐
│  Session End     │                              │   Langfuse Cloud   │
│  Hook            │                              │                    │
│                  │──── Update Root Span ───────→│  - Summary stats   │
│  - Read all spans│                              │  - Tool breakdown  │
│  - Calculate     │                              │  - Final metadata  │
│    summary       │                              └────────────────────┘
│  - Clean up files│
└──────────────────┘
```

## Component Responsibilities

### session_start.py
- **Purpose**: Initialize distributed trace
- **Inputs**: session_id
- **Outputs**:
  - Langfuse trace & root span
  - ~/.claude/trace_context/{session_id}.json
- **Key Functions**:
  - generate_trace_id() → 32-char hex UUID
  - generate_span_id() → 16-char hex UUID
  - save_session_trace_context()

### pre_tool_use.py
- **Purpose**: Record tool execution start
- **Inputs**: session_id, tool_name, tool_input
- **Outputs**:
  - Langfuse child span (pending)
  - ~/.claude/trace_context/{session_id}_spans.json (append)
- **Key Functions**:
  - get_session_trace_context()
  - create_child_observation_span()
  - store_child_span_reference()

### post_tool_use.py
- **Purpose**: Record tool execution completion
- **Inputs**: session_id, tool_name, tool_output
- **Outputs**:
  - Updated Langfuse child span (completed)
  - Updated span status in file
- **Key Functions**:
  - get_pending_span()
  - update_span_status()
  - Langfuse span.update()

### session_end.py
- **Purpose**: Finalize trace with summary
- **Inputs**: session_id
- **Outputs**:
  - Updated Langfuse root span & trace
  - Cleaned up session files
- **Key Functions**:
  - calculate_trace_summary()
  - cleanup_session_files()
  - Langfuse trace/span.update()

### utils/trace_context.py
- **Purpose**: Core trace management utilities
- **Key Functions**:
  - generate_trace_id() / generate_span_id()
  - get/save_session_trace_context()
  - create_child_observation_span()
  - get_pending_span() / update_span_status()
  - calculate_trace_summary()
  - cleanup_session_files()
  - debug_log()

## File System State Machine

```
SESSION LIFECYCLE:

INITIAL STATE:
~/.claude/trace_context/               [empty]

↓ session_start.py

STATE AFTER SESSION START:
~/.claude/trace_context/
└── {session_id}.json                  [root trace context]

↓ pre_tool_use.py (first tool)

STATE AFTER FIRST PRE-TOOL:
~/.claude/trace_context/
├── {session_id}.json                  [root trace context]
└── {session_id}_spans.json            [1 pending span]

↓ post_tool_use.py (first tool)

STATE AFTER FIRST POST-TOOL:
~/.claude/trace_context/
├── {session_id}.json                  [root trace context]
└── {session_id}_spans.json            [1 completed span]

↓ pre/post for each subsequent tool

STATE DURING SESSION:
~/.claude/trace_context/
├── {session_id}.json                  [root trace context]
└── {session_id}_spans.json            [N completed spans]

↓ session_end.py

FINAL STATE:
~/.claude/trace_context/               [empty - cleaned up]
```

## Error Handling Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    GRACEFUL DEGRADATION                          │
└─────────────────────────────────────────────────────────────────┘

Each hook follows this pattern:

try:
    # 1. Read inputs
    hook_data = json.load(sys.stdin)

    # 2. Attempt telemetry operation
    if trace_context_exists():
        if langfuse_configured():
            if langfuse_available():
                # Do telemetry
                create_or_update_spans()
            else:
                debug_log("Langfuse unavailable")
                # Continue without telemetry
        else:
            debug_log("Langfuse not configured")
            # Continue without telemetry
    else:
        debug_log("No trace context")
        # Continue without telemetry

except Exception as e:
    debug_log(f"Error: {e}")
    # NEVER re-raise - silently fail

# Hook always exits cleanly
# Claude Code execution never interrupted
```

## Trace Context Schema

### Root Trace Context File
**Location**: `~/.claude/trace_context/{session_id}.json`

```json
{
  "session_id": "abc123",
  "trace_id": "a1b2c3d4e5f6789012345678901234ab",
  "root_span_id": "1234567890abcdef",
  "root_span_name": "claude-session-root",
  "created_at": "2025-01-15T10:30:00.000Z",
  "metadata": {
    "started_at": "2025-01-15T10:30:00.000Z",
    "platform": "darwin"
  }
}
```

### Child Spans File
**Location**: `~/.claude/trace_context/{session_id}_spans.json`

```json
{
  "Read_2025-01-15T10:30:15.123Z": {
    "span_id": "abc123def4567890",
    "tool_name": "Read",
    "start_time": "2025-01-15T10:30:15.123Z",
    "end_time": "2025-01-15T10:30:15.923Z",
    "status": "completed"
  },
  "Bash_2025-01-15T10:30:20.456Z": {
    "span_id": "def456ghi7890123",
    "tool_name": "Bash",
    "start_time": "2025-01-15T10:30:20.456Z",
    "end_time": "2025-01-15T10:30:20.806Z",
    "status": "completed"
  }
}
```

## Performance Characteristics

- **File I/O**: ~4 read/write operations per tool call
- **Network I/O**: Langfuse SDK batches and flushes asynchronously
- **Memory**: Minimal - only session context in memory
- **Latency Impact**: <10ms per hook invocation
- **Storage**: ~1KB per session + ~200 bytes per tool call

## Security Considerations

1. **API Keys**: Stored in ~/.claude/hooks/.env (not in git)
2. **Tool Input/Output**: Truncated to 1KB to avoid PII exposure
3. **File Permissions**: Standard user permissions on context files
4. **Network**: HTTPS to Langfuse cloud (or self-hosted)
5. **Cleanup**: Session files deleted on session_end
