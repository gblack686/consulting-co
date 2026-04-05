# Phase 3 Implementation: Subagent Support

## Overview

Phase 3 adds full subagent support with parent-child relationship tracking and hierarchy depth detection. The system can now detect when an agent spawns subagents and create linked traces for complete agent orchestration visibility.

**Status**: ✅ COMPLETE - Ready for Testing

---

## What Was Implemented

### Subagent Detection

**In `trace_builder.py`:**

1. **`_detect_parent_session()`** - Identifies if current session is a subagent
   ```python
   parent_session_id = self._detect_parent_session()
   # Returns: session ID of parent if this is a subagent, None otherwise
   ```

2. **`_detect_subagent_calls()`** - Extracts all subagent invocations
   ```python
   subagent_calls = self._detect_subagent_calls()
   # Returns: List of subagent call details with purpose, outcome, errors
   ```

3. **`_calculate_hierarchy_depth()`** - Tracks nesting level
   ```python
   hierarchy_depth = self._calculate_hierarchy_depth()
   # Returns: 0 (root), 1+ (subagent nesting)
   ```

### Hierarchy Tracking

Every trace now includes hierarchy information:

```json
{
  "is_subagent": false,
  "parent_session_id": null,
  "hierarchy_depth": 0,
  "subagent_count": 1
}
```

### Trace Linking

Subagent observations include parent-child links:

```json
{
  "type": "SPAN",
  "name": "subagent-session_def456",
  "metadata": {
    "event_type": "SubagentExecution",
    "subagent_session_id": "session_def456",
    "parent_session_id": "session_abc123",
    "child_trace_id": "session_def456",
    "hierarchy_depth": 1,
    "purpose": "Search codebase for patterns",
    "outcome": "Found 3 matching files"
  }
}
```

---

## Architecture: Parent-Child Linking

### Trace Relationship Model

```
Parent Trace (session_abc123)
└─ SPAN: subagent-session_def456
    metadata.child_trace_id: session_def456  ← Links to child

Child Trace (session_def456)
metadata:
  parent_session_id: session_abc123  ← Links back to parent
  hierarchy_depth: 1
```

### Query Pattern

To retrieve subagent hierarchy:

```python
# 1. Load parent trace
parent_trace = langfuse.get_trace("session_abc123")

# 2. Find subagent spans
subagent_spans = [
  obs for obs in parent_trace.observations
  if obs.metadata.get("event_type") == "SubagentExecution"
]

# 3. Load child traces
for span in subagent_spans:
  child_trace_id = span.metadata["child_trace_id"]
  child_trace = langfuse.get_trace(child_trace_id)

  # Verify linking
  assert child_trace.metadata["parent_session_id"] == "session_abc123"
```

---

## Event Detection

### SubagentStop Event

When a subagent completes, a `SubagentStop` event is captured:

```json
{
  "hook_event_type": "SubagentStop",
  "session_id": "session_abc123",
  "timestamp": "2025-11-16T10:00:15Z",
  "hook_data": {
    "subagent_session_id": "session_def456",
    "purpose": "Search codebase for authentication patterns",
    "outcome": "Found 3 files with auth logic",
    "status": "completed",
    "duration_ms": 5230,
    "error": null
  }
}
```

### Event Buffering for Subagents

Each session (parent or subagent) maintains its own event buffer:

```
~/.claude/logs/
├── event_buffer_session_abc123.json     (parent session)
│   └─ Contains: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, SubagentStop, Stop
└── event_buffer_session_def456.json     (subagent session)
    └─ Contains: SessionStart, PreToolUse, PostToolUse, Stop
```

---

## Phase 3 Metadata Schema

### Trace-Level Metadata

```json
{
  "organization": "consulting-co",
  "project": "consulting-co",
  "project_id": "cmi19k90n000atd0713m9maij",

  // Phase 1: Event tracking
  "total_events_buffered": 7,
  "event_types_captured": {
    "PreToolUse": 2,
    "PostToolUse": 2,
    "SubagentStop": 1,
    "Stop": 1
  },

  // Phase 3: Subagent hierarchy
  "is_subagent": false,
  "parent_session_id": null,
  "hierarchy_depth": 0,
  "subagent_count": 1
}
```

### Observation-Level Metadata (Subagent)

```json
{
  "event_type": "SubagentExecution",
  "subagent_session_id": "session_def456",
  "parent_session_id": "session_abc123",
  "child_trace_id": "session_def456",
  "hierarchy_depth": 1,
  "purpose": "Search codebase for authentication patterns",
  "outcome": "Found 3 files: auth.py, login.py, oauth.py",
  "status": "completed",
  "duration_ms": 5230,
  "timestamp": "2025-11-16T10:00:15Z"
}
```

---

## CLI Tools

### Analyze Subagent Relationships

```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id session_abc123
```

**Output:**
```
============================================================
🔨 TRACE BUILDER: session_abc123...
============================================================
Total Events: 7
✓ ROOT AGENT TRACE

Event Types:
  PreToolUse: 2
  PostToolUse: 2
  SubagentStop: 1
  Stop: 1

Observations to Create:
  User Prompts: 1
  Tool Invocations: 2
  Subagent Executions: 1

Tool Breakdown:
  Bash: 2

Subagent Calls: 1
  1. session_def456...
     Purpose: Search codebase for authentication patterns
```

### Analyze Subagent Trace

```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id session_def456
```

**Output:**
```
============================================================
🔨 TRACE BUILDER: session_def456...
============================================================
Total Events: 5
⚠️  SUBAGENT TRACE (depth=1)
   Parent: session_abc123...

Event Types:
  PreToolUse: 2
  PostToolUse: 2
  Stop: 1

Observations to Create:
  User Prompts: 0
  Tool Invocations: 2
  Subagent Executions: 0
```

---

## Implementation Details

### Session Initialization

When a new session starts (parent or subagent):

1. Create new `EventBuffer` for session
2. Start buffering all events
3. Detect parent_session_id if subagent

### During Execution

For each hook event:

1. Buffer event to disk
2. If `SubagentStop`: Record subagent call details
3. Wait for `Stop` event

### Trace Construction (Stop Event)

1. Load all buffered events
2. Initialize `TraceBuilder`
3. Detect relationships:
   - Is this a subagent? → Set `is_subagent=true`
   - How many subagents called? → Count `SubagentStop` events
   - What's the depth? → Set `hierarchy_depth`
4. Create linked observations
5. Send trace to Langfuse
6. Clear event buffer

---

## Example: Multi-Agent Execution

### Scenario

```
User: "Search codebase for auth patterns and analyze security"

Main Agent:
├─ Parse request
├─ Spawn Search Subagent (session_search_123)
│  └─ Use Glob to find files
│  └─ Use Grep to search content
├─ Spawn Analysis Subagent (session_analysis_456)
│  └─ Use Read to examine files
│  └─ Use Bash to run security checks
└─ Synthesize results
```

### Resulting Traces

**Main Agent Trace** (session_main_789):
```json
{
  "trace": {
    "name": "consulting-co-conversation",
    "metadata": {
      "is_subagent": false,
      "hierarchy_depth": 0,
      "subagent_count": 2,
      "parent_session_id": null
    },
    "observations": [
      {
        "type": "SPAN",
        "name": "user-prompt",
        "input": "Search codebase for auth patterns..."
      },
      {
        "type": "SPAN",
        "name": "subagent-session_search_123",
        "metadata": {
          "child_trace_id": "session_search_123",
          "hierarchy_depth": 1,
          "purpose": "Search for authentication patterns",
          "outcome": "Found 5 files with auth logic"
        }
      },
      {
        "type": "SPAN",
        "name": "subagent-session_analysis_456",
        "metadata": {
          "child_trace_id": "session_analysis_456",
          "hierarchy_depth": 1,
          "purpose": "Analyze security implications",
          "outcome": "Identified 3 security issues"
        }
      }
    ]
  }
}
```

**Search Subagent Trace** (session_search_123):
```json
{
  "trace": {
    "name": "consulting-co-conversation",
    "metadata": {
      "is_subagent": true,
      "hierarchy_depth": 1,
      "parent_session_id": "session_main_789",
      "subagent_count": 0
    },
    "observations": [
      {
        "type": "SPAN",
        "name": "tool-Glob-1",
        "metadata": {
          "tool_name": "Glob",
          "latency_ms": 123,
          "status": "success"
        }
      },
      {
        "type": "SPAN",
        "name": "tool-Grep-2",
        "metadata": {
          "tool_name": "Grep",
          "latency_ms": 456,
          "status": "success"
        }
      }
    ]
  }
}
```

---

## Testing Phase 3

### Test 1: Root Agent Only (No Subagents)

**Command:**
```
"What is 2+2?"
```

**Expected:**
- ✓ is_subagent = false
- ✓ hierarchy_depth = 0
- ✓ parent_session_id = null
- ✓ subagent_count = 0

**Verify:**
```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>
# Should show: ✓ ROOT AGENT TRACE
```

### Test 2: Agent with Tool Usage

**Command:**
```
"List files and read the README"
```

**Expected:**
- ✓ is_subagent = false
- ✓ Tool spans created (tool-Bash-1, tool-Read-2)
- ✓ hierarchy_depth = 0

### Test 3: Subagent Spawned

**Command (if subagent Task tool is triggered):**
```
"Use a subagent to search for Python files"
```

**Expected:**
- ✓ Parent trace: is_subagent=false, subagent_count=1
- ✓ Subagent span with child_trace_id link
- ✓ Child trace: is_subagent=true, hierarchy_depth=1, parent_session_id=parent_id

**Verify:**
```bash
# Parent
python3 .claude/hooks/utils/trace_builder.py analyze --session-id parent_id
# Should show: Subagent Calls: 1

# Child
python3 .claude/hooks/utils/trace_builder.py analyze --session-id child_id
# Should show: ⚠️  SUBAGENT TRACE (depth=1)
```

---

## Known Limitations & Future Enhancements

### Current Limitations

1. **Depth calculation**: Currently returns 0 or 1; doesn't recursively check parent's parent
2. **Error handling**: If subagent fails, still creates SPAN (status field not used yet)
3. **Async subagents**: Assumes synchronous execution; may need adjustment for parallel subagents

### Future Enhancements

**Phase 4**:
- Add error tracking (status field: success/error/blocked)
- Add agent_id and source_app to all traces
- Capture full tool input/output for debugging

**Phase 5**:
- Real-time subagent streaming
- WebSocket updates for parent-child relationships
- Visual tree representation in dashboard

---

## Integration with Observability Dashboard

### Dashboard Usage

The parent-child linking enables:

1. **Hierarchy Visualization**: Show agent trees
   ```
   Main Agent (consulting-co)
   ├─ Search Subagent (depth=1)
   │  └─ Tools: Glob, Grep
   └─ Analysis Subagent (depth=1)
      └─ Tools: Read, Bash
   ```

2. **Cost Tracking**: Sum costs across hierarchy
   ```
   Main Agent: $0.10
   ├─ Search Subagent: $0.02
   └─ Analysis Subagent: $0.05
   Total: $0.17
   ```

3. **Performance Analysis**: Track latencies
   ```
   Main Agent: 5.5s
   ├─ Search Subagent: 1.2s
   └─ Analysis Subagent: 2.8s
   ```

---

## Summary

✅ **Phase 3 Complete**:
- Parent-child session detection working
- Hierarchy depth tracking implemented
- Trace linking enabled via metadata
- CLI tools enhanced with subagent info
- Metadata includes all hierarchy info

⏭️ **Ready for Phase 4**:
- Enhanced metadata (agent_id, source_app)
- Error tracking and status fields
- Tool input/output summaries

---

**Implementation Date**: 2025-11-16
**Status**: Complete
**Version**: 1.0
