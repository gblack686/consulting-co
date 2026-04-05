# OpenTelemetry-Based Telemetry Implementation Summary

## Overview

Implemented a proper OpenTelemetry-compliant distributed tracing system for Claude Code that uses Langfuse for observability. The system creates parent-child trace relationships and stores context in JSON files for reliable cross-hook communication.

## Files Created/Modified

### New Files Created

1. **~/.claude/hooks/session_start.py** (4.6 KB)
   - Creates root trace span with UUID-based trace_id and root_span_id
   - Stores trace context in ~/.claude/trace_context/{session_id}.json
   - Initializes Langfuse trace and root span

2. **~/.claude/hooks/session_end.py** (4.6 KB)
   - Reads all child observations from session
   - Calculates summary metadata (tool_count, total_latency, breakdown)
   - Updates root trace with summary
   - Cleans up session files

3. **~/.claude/hooks/utils/trace_context.py** (11.9 KB)
   - Core utility module for trace context management
   - Functions: generate_trace_id(), generate_span_id()
   - Context persistence: save/get session trace context
   - Span management: create/update/track child spans
   - Summary calculation: tool counts and latencies
   - Debug logging support

4. **~/.claude/hooks/.env.example** (0.6 KB)
   - Template for Langfuse configuration
   - Documents all environment variables

5. **~/.claude/hooks/TELEMETRY_SETUP.md** (11.2 KB)
   - Comprehensive setup and usage documentation
   - Architecture diagrams and flow explanations
   - Testing procedures
   - Troubleshooting guide

6. **~/.claude/hooks/test_trace_flow.py** (6.7 KB)
   - Automated test script for full trace flow
   - Simulates session with multiple tool executions
   - Verifies file creation and cleanup

### Files Modified

7. **~/.claude/hooks/pre_tool_use.py** (Enhanced)
   - Added: Read parent trace context from file
   - Added: Create child observation span in Langfuse
   - Added: Store span reference with parent_span_id linkage
   - Maintains: Existing tool timing functionality

8. **~/.claude/hooks/post_tool_use.py** (Enhanced)
   - Added: Read parent trace context
   - Added: Find matching pending child span
   - Added: Update span with output and latency
   - Maintains: Existing tool timing functionality

## How Trace Context Flows Through the System

```
┌─────────────────────────────────────────────────────────────────┐
│ SESSION START                                                   │
│ ─────────────────                                               │
│ 1. Generate trace_id (32-char hex) and root_span_id (16-char)  │
│ 2. Create root trace in Langfuse                               │
│ 3. Save to: ~/.claude/trace_context/{session_id}.json         │
│                                                                 │
│ Stored Context:                                                │
│ {                                                              │
│   "trace_id": "a1b2c3d4e5f6789012345678901234ab",            │
│   "root_span_id": "1234567890abcdef",                         │
│   "root_span_name": "claude-session-root",                    │
│   "session_id": "abc123",                                     │
│   "created_at": "2025-01-15T10:30:00Z"                        │
│ }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PRE-TOOL-USE (for each tool)                                   │
│ ─────────────────────────────                                  │
│ 1. Read parent trace context from file                         │
│ 2. Extract: trace_id, root_span_id                            │
│ 3. Generate new span_id for this observation                  │
│ 4. Create child span in Langfuse:                             │
│    - trace_id: from parent                                    │
│    - parent_observation_id: root_span_id                      │
│    - id: new span_id                                          │
│    - start_time: now()                                        │
│    - metadata: tool_name, tool_input                          │
│ 5. Store span reference in {session_id}_spans.json           │
│                                                                │
│ Span Reference:                                               │
│ {                                                             │
│   "Read_2025-01-15T10:30:15.123Z": {                         │
│     "span_id": "abc123def4567890",                           │
│     "tool_name": "Read",                                     │
│     "start_time": "2025-01-15T10:30:15.123Z",               │
│     "end_time": null,                                        │
│     "status": "pending"                                      │
│   }                                                           │
│ }                                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [TOOL EXECUTES]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ POST-TOOL-USE                                                   │
│ ──────────────                                                  │
│ 1. Read parent trace context                                   │
│ 2. Find most recent pending span for tool_name                 │
│ 3. Calculate latency: now() - start_time                       │
│ 4. Update span in Langfuse:                                    │
│    - trace_id: from context                                   │
│    - id: span_id from pending span                            │
│    - end_time: now()                                          │
│    - metadata: tool_output, latency_ms                        │
│ 5. Update span status to "completed"                          │
│ 6. Flush to Langfuse                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
              [Repeat for each tool execution]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ SESSION END                                                     │
│ ────────────                                                    │
│ 1. Read all child spans from {session_id}_spans.json          │
│ 2. Calculate summary:                                          │
│    - tool_count: total number of tools                        │
│    - total_tool_latency_ms: sum of all latencies              │
│    - tool_breakdown: per-tool counts and latencies            │
│ 3. Update root span with summary metadata                     │
│ 4. Update trace with final metadata                           │
│ 5. Flush to Langfuse                                          │
│ 6. Clean up session files:                                    │
│    - Delete {session_id}.json                                 │
│    - Delete {session_id}_spans.json                           │
│    - Delete {session_id} timing data                          │
│                                                                │
│ Summary Example:                                               │
│ {                                                              │
│   "tool_count": 5,                                            │
│   "total_tool_latency_ms": 1250,                             │
│   "tool_breakdown": {                                         │
│     "Read": {"count": 2, "total_latency_ms": 800},           │
│     "Bash": {"count": 2, "total_latency_ms": 350},           │
│     "Grep": {"count": 1, "total_latency_ms": 100}            │
│   }                                                            │
│ }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **OpenTelemetry Compliance**
   - Proper 32-char hex trace IDs (UUID-based)
   - Proper 16-char hex span IDs (UUID-based)
   - Parent-child relationships via parent_observation_id

2. **File-Based Context Persistence**
   - JSON files in ~/.claude/trace_context/
   - Survives across hook invocations
   - Easy to inspect and debug

3. **Graceful Degradation**
   - Never breaks Claude Code execution
   - Handles missing context files
   - Handles missing Langfuse credentials
   - Handles SDK not installed
   - Logs all errors for debugging

4. **No Transcript Parsing**
   - Only uses real-time hook data
   - No fragile text extraction
   - Reliable and maintainable

5. **Comprehensive Metadata**
   - Tool names, inputs (truncated to 1KB)
   - Tool outputs (truncated to 1KB)
   - Latencies in milliseconds
   - Session summaries and per-tool breakdowns

## Testing Commands

### 1. Basic Setup Verification

```bash
# Check all files exist
ls -la ~/.claude/hooks/session_start.py
ls -la ~/.claude/hooks/session_end.py
ls -la ~/.claude/hooks/pre_tool_use.py
ls -la ~/.claude/hooks/post_tool_use.py
ls -la ~/.claude/hooks/utils/trace_context.py

# Check configuration
ls -la ~/.claude/hooks/.env.example
```

### 2. Install Dependencies

```bash
pip install langfuse python-dotenv
```

### 3. Configure Langfuse

```bash
cd ~/.claude/hooks
cp .env.example .env
# Edit .env with your Langfuse credentials
```

### 4. Run Automated Test

```bash
cd ~/.claude/hooks
python test_trace_flow.py
```

Expected output:
```
================================================================================
Testing OpenTelemetry-Based Telemetry System
================================================================================

Session ID: test-1736950800

1. Testing session_start hook...
✓ Trace context file exists: /home/user/.claude/trace_context/test-1736950800.json
  Content preview: {
  "session_id": "test-1736950800",
  "trace_id": "a1b2c3d4e5f6789012345678901234ab",
  "root_span_id": "1234567890abcdef",
  ...

2. Testing pre_tool_use hook (Read)...
✓ Spans file exists: /home/user/.claude/trace_context/test-1736950800_spans.json
  ...

[... more test output ...]

================================================================================
✓ All tests completed successfully!
================================================================================
```

### 5. Manual Hook Testing

```bash
# Test session start
echo '{"session_id":"manual-test"}' | python ~/.claude/hooks/session_start.py

# Verify context created
cat ~/.claude/trace_context/manual-test.json

# Test pre-tool-use
echo '{"session_id":"manual-test","tool_name":"Read","tool_input":{"file_path":"/tmp/test"}}' | \
  python ~/.claude/hooks/pre_tool_use.py

# Test post-tool-use
echo '{"session_id":"manual-test","tool_name":"Read","tool_output":"content"}' | \
  python ~/.claude/hooks/post_tool_use.py

# Test session end
echo '{"session_id":"manual-test"}' | python ~/.claude/hooks/session_end.py

# Check debug logs
tail -50 ~/.claude/hooks/trace_debug.log
```

### 6. Verify in Langfuse UI

1. Go to https://cloud.langfuse.com
2. Navigate to "Traces"
3. Look for traces starting with `claude-session-`
4. Click on a trace to see:
   - Root span: `claude-session-root`
   - Child spans: One per tool execution
   - Metadata: Tool names, inputs, outputs, latencies
   - Summary: Tool counts and total latency

## File Structure

```
~/.claude/
├── hooks/
│   ├── session_start.py          # NEW: Creates root trace
│   ├── pre_tool_use.py            # ENHANCED: Creates child spans
│   ├── post_tool_use.py           # ENHANCED: Updates child spans
│   ├── session_end.py             # NEW: Finalizes trace
│   ├── .env                       # YOUR CONFIG (create from .env.example)
│   ├── .env.example               # NEW: Configuration template
│   ├── trace_debug.log            # NEW: Debug logging output
│   ├── TELEMETRY_SETUP.md         # NEW: Full documentation
│   ├── test_trace_flow.py         # NEW: Automated test script
│   └── utils/
│       ├── trace_context.py       # NEW: Core trace utilities
│       └── tool_timing.py         # EXISTING: Tool timing utilities
│
├── trace_context/                 # NEW: Trace context storage
│   ├── {session_id}.json          # Root trace context
│   └── {session_id}_spans.json    # Child span references
│
└── tool_timings/                  # EXISTING: Tool timing data
    └── {session_id}.json
```

## Troubleshooting

### Issue: No traces appearing in Langfuse

**Solution:**
```bash
# 1. Check credentials
cat ~/.claude/hooks/.env | grep LANGFUSE

# 2. Check debug log
tail -100 ~/.claude/hooks/trace_debug.log

# 3. Verify SDK installed
python -c "import langfuse; print(langfuse.__version__)"
```

### Issue: Spans not linked to parent

**Solution:**
```bash
# Check trace context file
cat ~/.claude/trace_context/{session_id}.json

# Verify parent_observation_id matches root_span_id in debug log
grep "parent_observation_id" ~/.claude/hooks/trace_debug.log
```

### Issue: Files not cleaning up

**Solution:**
```bash
# Manual cleanup
rm ~/.claude/trace_context/*.json
rm ~/.claude/tool_timings/*.json
```

## Next Steps

1. Set up Langfuse account at https://cloud.langfuse.com
2. Copy `.env.example` to `.env` and add your credentials
3. Run `python test_trace_flow.py` to verify setup
4. Use Claude Code normally - traces will appear in Langfuse
5. Monitor debug log for any issues: `tail -f ~/.claude/hooks/trace_debug.log`

## Benefits

- **Proper Observability**: Full distributed tracing with parent-child relationships
- **No Breaking Changes**: Graceful degradation ensures Claude Code always works
- **Easy Debugging**: JSON files + debug logs make troubleshooting simple
- **Rich Metadata**: Comprehensive tool execution data in Langfuse
- **Future-Proof**: OpenTelemetry-compliant design enables integration with other platforms
