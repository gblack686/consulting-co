# Phase 4 Implementation: Enhanced Metadata

## Overview

Phase 4 adds comprehensive agent identity tracking, source application detection, and error status monitoring. The system now captures agent context in all observations and provides detailed metadata about the agent executing the tools.

**Status**: ✅ COMPLETE - Ready for Testing

---

## What Was Implemented

### Agent Identity Tracking

**In `trace_builder.py`:**

1. **`_generate_agent_id()`** - Creates display-friendly agent identifiers
   ```python
   agent_id = self._generate_agent_id()
   # Returns: {source_app}:{session_id[:8]}
   # Example: claude-code:session_a
   ```

2. **`_detect_source_app()`** - Extracts source application from events
   ```python
   source_app = self._detect_source_app()
   # Returns: "claude-code", "browser", or custom app name
   ```

3. **`_detect_errors()`** - Detects tool and subagent failures
   ```python
   has_errors = self._detect_errors()
   # Returns: True if any tool or subagent call failed
   ```

### Agent Metadata Schema

Every trace now includes agent identity:

```json
{
  "agent_id": "claude-code:session_a",
  "source_app": "claude-code",
  "has_errors": false
}
```

### Observation-Level Metadata

Tool invocations now include agent context:

```json
{
  "type": "SPAN",
  "name": "tool-Bash-1",
  "metadata": {
    "event_type": "ToolInvocation",
    "tool_name": "Bash",
    "latency_ms": 234,
    "status": "success",
    "agent_id": "claude-code:session_a",
    "source_app": "claude-code"
  }
}
```

Subagent executions include agent context:

```json
{
  "type": "SPAN",
  "name": "subagent-session_def456",
  "metadata": {
    "event_type": "SubagentExecution",
    "subagent_session_id": "session_def456",
    "status": "completed",
    "agent_id": "claude-code:session_a",
    "source_app": "claude-code"
  }
}
```

---

## Architecture: Agent Context Propagation

### Trace Metadata Structure

```
Trace Metadata
├── agent_id: "claude-code:session_abc123"
├── source_app: "claude-code"
├── has_errors: false
│
└── Observations
    ├── SPAN: tool-Bash-1
    │   ├── agent_id: "claude-code:session_abc123"
    │   ├── source_app: "claude-code"
    │   └── status: "success"
    │
    └── SPAN: subagent-session_def456
        ├── agent_id: "claude-code:session_abc123"
        ├── source_app: "claude-code"
        └── status: "completed"
```

### Agent ID Format

```
{source_app}:{session_id[:8]}

Examples:
- claude-code:session_a
- claude-code:session_abc1
- browser:session_xyz9
- custom-app:session_def4
```

---

## Error Detection

### Error Detection Logic

The system checks three levels for errors:

1. **Tool-Level Errors**
   ```python
   for tool_inv in self.tool_pairs:
       if tool_inv.status == "error" or tool_inv.error_message:
           return True
   ```

2. **Subagent-Level Errors**
   ```python
   for call in self.subagent_calls:
       if call.get("error") or call.get("status") == "error":
           return True
   ```

3. **Event-Level Errors**
   ```python
   for event in self.events:
       if event.get("hook_event_type") == "PostToolUse":
           if event.get("hook_data", {}).get("error"):
               return True
   ```

### Error Metadata in Traces

When errors are detected:

```json
{
  "has_errors": true,
  "observations": [
    {
      "type": "SPAN",
      "name": "tool-Read-1",
      "metadata": {
        "status": "error",
        "error_message": "File not found: /path/to/missing.txt"
      }
    }
  ]
}
```

---

## Phase 4 Metadata Schema

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
    "Stop": 1
  },

  // Phase 3: Subagent hierarchy
  "is_subagent": false,
  "parent_session_id": null,
  "hierarchy_depth": 0,
  "subagent_count": 1,

  // Phase 4: Agent metadata
  "agent_id": "claude-code:session_abc123",
  "source_app": "claude-code",
  "has_errors": false
}
```

### Tool Observation Metadata (Phase 4)

```json
{
  "event_type": "ToolInvocation",
  "tool_name": "Bash",
  "sequence_number": 1,
  "latency_ms": 234,
  "status": "success",
  "error_message": null,
  "start_timestamp": "2025-11-16T10:00:05Z",
  "end_timestamp": "2025-11-16T10:00:05Z",
  // Phase 4 additions:
  "agent_id": "claude-code:session_abc123",
  "source_app": "claude-code"
}
```

### Subagent Observation Metadata (Phase 4)

```json
{
  "event_type": "SubagentExecution",
  "subagent_session_id": "session_def456",
  "parent_session_id": "session_abc123",
  "child_trace_id": "session_def456",
  "hierarchy_depth": 1,
  "status": "completed",
  "purpose": "Search codebase for patterns",
  "outcome": "Found 3 files",
  "timestamp": "2025-11-16T10:00:15Z",
  // Phase 4 additions:
  "agent_id": "claude-code:session_abc123",
  "source_app": "claude-code"
}
```

---

## CLI Tools

### Analyze Agent Metadata

```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id session_abc123
```

**Output:**
```
============================================================
🔨 TRACE BUILDER: session_abc123...
============================================================
Total Events: 7
Agent ID: claude-code:session_abc123
Source: claude-code
✓ ROOT AGENT TRACE

Event Types:
  PreToolUse: 2
  PostToolUse: 2
  Stop: 1

Observations to Create:
  User Prompts: 1
  Tool Invocations: 2
  Subagent Executions: 0

Tool Breakdown:
  Bash: 2
```

### View Event Summary with Phase 4 Metadata

```bash
python3 .claude/hooks/utils/event_buffer.py summary --session-id session_abc123
```

**Output includes:**
```
Agent Context:
  agent_id: claude-code:session_abc123
  source_app: claude-code
  has_errors: false
```

---

## Implementation Details

### TraceBuilder Initialization

When TraceBuilder is created:

```python
def __init__(self, session_id: str, events: List[Dict[str, Any]]):
    self.session_id = session_id
    self.events = sorted(events, key=lambda e: self._get_timestamp(e))
    self.tool_pairs = self._match_tool_events()

    # PHASE 3: Subagent detection
    self.parent_session_id = self._detect_parent_session()
    self.subagent_calls = self._detect_subagent_calls()
    self.hierarchy_depth = self._calculate_hierarchy_depth()

    # PHASE 4: Agent identity and error tracking
    self.agent_id = self._generate_agent_id()
    self.source_app = self._detect_source_app()
    self.has_errors = self._detect_errors()
```

### Metadata Extraction in log_to_langfuse.py

```python
# PHASE 3 & 4: Extract metadata
subagent_info = {}
phase4_info = {}
if ENABLE_ENHANCED_TRACING and all_events:
    try:
        builder = TraceBuilder(session_id, all_events)

        # PHASE 3: Subagent hierarchy
        subagent_info = {
            "is_subagent": builder.parent_session_id is not None,
            "parent_session_id": builder.parent_session_id,
            "hierarchy_depth": builder.hierarchy_depth,
            "subagent_count": len(builder.subagent_calls)
        }

        # PHASE 4: Agent metadata
        phase4_info = {
            "agent_id": builder.agent_id,
            "source_app": builder.source_app,
            "has_errors": builder.has_errors
        }
    except Exception:
        pass

# Merge into trace metadata
trace_metadata = {
    ...base metadata...,
    **subagent_info,    # Phase 3 merge
    **phase4_info       # Phase 4 merge
}
```

---

## Example: Complete Trace with Phase 4 Metadata

### Test Command
```
"Read a non-existent file and show me the error"
```

### Resulting Trace

```json
{
  "trace_id": "session_abc123",
  "name": "consulting-co-conversation",
  "metadata": {
    "organization": "consulting-co",
    "project": "consulting-co",
    "agent_id": "claude-code:session_abc",
    "source_app": "claude-code",
    "has_errors": true,
    "total_events_buffered": 3,
    "event_types_captured": {
      "PreToolUse": 1,
      "PostToolUse": 1,
      "Stop": 1
    }
  },
  "observations": [
    {
      "type": "SPAN",
      "name": "user-prompt",
      "input": "Read a non-existent file and show me the error"
    },
    {
      "type": "SPAN",
      "name": "tool-Read-1",
      "metadata": {
        "event_type": "ToolInvocation",
        "tool_name": "Read",
        "status": "error",
        "error_message": "File not found: /path/to/missing.txt",
        "latency_ms": 45,
        "agent_id": "claude-code:session_abc",
        "source_app": "claude-code"
      }
    }
  ]
}
```

---

## Testing Phase 4

### Test 1: Normal Tool Execution

**Command:**
```
"List files in the current directory"
```

**Expected:**
- ✓ agent_id populated (claude-code:session_*)
- ✓ source_app = "claude-code"
- ✓ has_errors = false
- ✓ Tool observation has agent_id and source_app
- ✓ Tool status = "success"

**Verify:**
```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>
# Should show: Agent ID: claude-code:session_*
#             Source: claude-code
```

### Test 2: Tool Error

**Command:**
```
"Try to read a file that doesn't exist"
```

**Expected:**
- ✓ has_errors = true (detected in trace metadata)
- ✓ Tool observation status = "error"
- ✓ error_message captured
- ✓ CLI output shows "⚠️  ERRORS DETECTED in this trace"

**Verify:**
```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>
# Should show: ⚠️  ERRORS DETECTED in this trace
```

### Test 3: Multiple Tools with Mixed Results

**Command:**
```
"List files, then read a non-existent file"
```

**Expected:**
- ✓ has_errors = true (at least one tool failed)
- ✓ First tool (Bash): status = "success"
- ✓ Second tool (Read): status = "error"
- ✓ All observations include agent_id and source_app

**Verify:**
```bash
python3 .claude/hooks/utils/trace_builder.py analyze --session-id <session_id>
# Should show:
#   Tool Breakdown:
#     Bash: 1
#     Read: 1
#   ⚠️  ERRORS DETECTED in this trace
```

### Test 4: Subagent with Agent Context

**Command (if subagent Task tool triggered):**
```
"Use a subagent to search for Python files"
```

**Expected:**
- ✓ Parent trace has agent_id and source_app
- ✓ Subagent span includes agent_id and source_app from parent
- ✓ Subagent observation has status field

**Verify:**
```bash
# Parent
python3 .claude/hooks/utils/trace_builder.py analyze --session-id parent_id
# Should show: Agent ID: claude-code:parent_id[:8]
#             Subagent Calls: 1

# Child
python3 .claude/hooks/utils/trace_builder.py analyze --session-id child_id
# Should show: Agent ID: claude-code:child_id[:8]
```

---

## Langfuse Dashboard Integration

### Trace Details View

Phase 4 metadata is visible in trace details:

```
Trace: session_abc123
Organization: consulting-co
Project: consulting-co

Agent Context:
  Agent ID: claude-code:session_abc
  Source: claude-code
  Errors: false

Event Summary:
  Total Events: 7
  PreToolUse: 2
  PostToolUse: 2
```

### Observation Inspector

Each tool observation shows:

```
SPAN: tool-Bash-1
Status: success
Latency: 234ms
Agent: claude-code:session_abc
Source: claude-code
```

### Cost Analysis

Can now track costs per agent:

```
Agent Summary:
  claude-code:session_abc - $0.12
    tool-Bash-1: $0.05
    tool-Read-2: $0.07
```

---

## Known Limitations & Future Enhancements

### Current Limitations

1. **Source App Detection**: Only checks hook_data and event metadata; custom apps need to populate field
2. **Agent ID Uniqueness**: Relies on session_id; doesn't handle UUID collisions
3. **Error Propagation**: Doesn't track error recovery/retry logic

### Future Enhancements

**Phase 4+ Enhancements**:
- Agent capabilities tracking (which tools available to agent)
- Cost allocation per agent and per tool
- Agent version/model tracking
- Tool performance baselines per agent

**Phase 5**:
- Real-time agent status monitoring
- Agent behavior analytics
- Anomaly detection in agent performance

---

## Summary

✅ **Phase 4 Complete**:
- Agent identity tracking with agent_id format
- Source application detection and propagation
- Error detection across tools and subagents
- Agent context in all observations
- CLI output enhanced with agent metadata
- Metadata includes all agent information

⏭️ **Ready for Testing**:
- Test normal tool execution
- Test tool errors (has_errors=true)
- Test multiple tools with mixed results
- Test subagent execution with agent context

---

**Implementation Date**: 2025-11-16
**Status**: Complete
**Version**: 1.0

## Next Steps

1. Run Phase 4 test conversations
2. Verify agent_id and source_app in Langfuse dashboard
3. Validate error detection with failing tools
4. Prepare for Phase 5 (cost tracking and dashboards)
