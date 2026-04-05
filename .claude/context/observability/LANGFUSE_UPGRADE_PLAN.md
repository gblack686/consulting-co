# Langfuse Observability Upgrade Plan

## Executive Summary

This document provides a comprehensive plan to enhance the current Langfuse observability logging system to support full multi-agent execution tracking, observability dashboard integration, and enhanced metadata capture based on the existing observability platform architecture.

**Current State**: Single-turn conversation logging with basic token/cost tracking
**Target State**: Multi-agent hierarchical trace logging with tool execution chains, subagent tracking, and dashboard-ready metadata

---

## 1. Current State Analysis

### 1.1 What We're Logging Now

Based on `log_to_langfuse.py` and `TRACE_EXAMPLE.json`:

**Trace Structure:**
```
Trace (consulting-co-conversation)
└── SPAN (consulting-co-conversation)
    └── GENERATION (claude-response)
```

**Current Metadata Captured:**

| Category | Fields | Source |
|----------|--------|--------|
| **Organization** | organization, project, project_id | `langfuse_config.py` auto-detection |
| **Timing** | conversation_latency_ms, conversation_latency_seconds, llm_time_ms | Calculated from timestamps |
| **Messages** | user_message_length, assistant_message_length | Message string lengths |
| **Tools** | tool_count, total_tool_latency_ms, tool_breakdown | From `tool_timing.py` (if exists) |
| **Tokens** | input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens | Claude API usage |
| **Costs** | Automatic calculation by Langfuse based on model + tokens | Langfuse built-in |

**Current Capabilities:**
- ✅ Multi-org routing (consulting-co vs RevStar)
- ✅ Project auto-detection from working directory
- ✅ Auto project creation for RevStar quickstarts
- ✅ Token usage with cache tracking (90% discount on cache reads)
- ✅ Tool execution timing (if tool_timing utility exists)
- ✅ Session ID tracking for conversation threads
- ✅ Model parameter tracking (max_tokens, temperature)

---

## 2. Gap Analysis

### 2.1 Missing from Current Traces

| What's Missing | Why It Matters | Dashboard Impact |
|----------------|----------------|------------------|
| **PreToolUse/PostToolUse events** | No tool execution details | Can't show tool timeline |
| **Tool input/output** | No visibility into what tools did | Can't debug tool failures |
| **Tool error tracking** | Can't identify which tools failed | Missing error analysis |
| **Subagent hierarchy** | No parent-child relationships | Can't visualize agent coordination |
| **SubagentStop events** | Can't track subagent completion | Missing subagent metrics |
| **Session start time** | Only capture end time | Can't calculate true session duration |
| **User prompt content** | Only log assistant response | Missing full conversation context |
| **Tool sequence order** | Tools logged in bulk | Can't recreate execution timeline |
| **Event timestamps** | Only session-level timing | Can't track event-by-event flow |

### 2.2 Desired Enhanced Structure

```
Trace (session_abc123)
├── SPAN (user-prompt)
├── GENERATION (llm-response)
├── SPAN (tool-bash-1)
├── SPAN (tool-read-2)
├── SPAN (subagent-session_def456)  ← NEW
│   ├── GENERATION (subagent-llm-response)
│   └── SPAN (subagent-tool-glob)
└── SPAN (tool-write-3)
```

---

## 3. Enhanced Data Model

### 3.1 New Trace-Level Metadata

```python
{
  # Identity
  "agent_id": "consulting-co:abc12345",
  "source_app": "consulting-co",
  "session_id": "session_abc123...",
  "parent_session_id": "session_xyz...",  # If subagent

  # Organization & Project
  "organization": "consulting-co",
  "project": "consulting-co",
  "project_id": "cmi19k90n000atd0713m9maij",

  # Hierarchy
  "hierarchy_depth": 0,
  "is_subagent": false,

  # Status & Timing
  "status": "completed",
  "session_start_time": "2025-11-16T10:00:00Z",
  "session_end_time": "2025-11-16T10:05:23Z",
  "session_duration_ms": 323000,

  # Metrics
  "total_events": 15,
  "tool_count": 5,
  "subagent_count": 1,
  "user_prompts": 1,
  "llm_generations": 1,

  # Performance
  "total_tool_latency_ms": 1234,
  "total_llm_latency_ms": 5678,
  "total_session_latency_ms": 6912,

  # Tool breakdown
  "tool_breakdown": {
    "Bash": { "count": 2, "total_ms": 400 },
    "Read": { "count": 2, "total_ms": 234 },
    "Write": { "count": 1, "total_ms": 600 }
  }
}
```

### 3.2 New Observation-Level Metadata

**Tool Invocations:**
```python
{
  "event_type": "ToolInvocation",
  "tool_name": "Bash",
  "sequence_number": 1,
  "latency_ms": 234,
  "status": "success",
  "start_timestamp": "2025-11-16T10:00:05.123Z",
  "end_timestamp": "2025-11-16T10:00:05.357Z",
  "input_summary": "{ command: 'ls -la' }",
  "output_summary": "file1\nfile2\n..."
}
```

**Subagent Executions:**
```python
{
  "event_type": "SubagentExecution",
  "subagent_session_id": "session_def456",
  "parent_session_id": "session_abc123",
  "hierarchy_depth": 1,
  "child_trace_id": "session_def456",
  "purpose": "Search codebase for authentication patterns",
  "outcome": "Found 3 files with auth logic"
}
```

---

## 4. Implementation Plan (6 Phases)

### Phase 1: Enhanced Event Capture (Week 1)
- Capture all hook events (not just Stop)
- Build event state machine per session
- Store events in memory buffer for trace construction
- **Key Files**: `log_to_langfuse.py`, `event_buffer.py` (NEW)

### Phase 2: Multi-Event Trace Construction (Week 1-2)
- Transform event sequences into Langfuse observations
- Implement tool invocation spans
- Add user prompt spans
- **Key Files**: `trace_builder.py` (NEW)

### Phase 3: Subagent Support (Week 2)
- Detect parent-child relationships
- Create linked traces for subagents
- Track hierarchy depth
- **Key Files**: `trace_builder.py`, `send_event.py`

### Phase 4: Enhanced Metadata (Week 2-3)
- Add agent_id, source_app to all traces
- Capture tool input/output (truncated)
- Track error states and status
- **Key Files**: `trace_builder.py`

### Phase 5: Dashboard Integration (Week 3)
- Test with observability dashboard
- Validate WebSocket event flow
- Ensure SQLite → Langfuse sync works

### Phase 6: Testing & Optimization (Week 4)
- Load testing with multiple agents
- Performance optimization
- Documentation

---

## 5. Multi-Agent Architecture

### 5.1 Trace Relationships (Option A: RECOMMENDED)

Each agent session gets its own trace, linked via metadata:

```
Trace: session_abc123 (main)
  metadata.hierarchy_depth: 0
  observations:
    - SPAN: subagent-session_def456
        metadata.child_trace_id: "session_def456"

Trace: session_def456 (subagent)
  metadata.parent_session_id: "session_abc123"
  metadata.hierarchy_depth: 1
  observations:
    - GENERATION: ...
    - SPAN: tool-glob-1
```

**Advantages:**
- Clean separation of concerns
- Each agent has full trace structure
- Scalable to deep nesting
- Easy to filter by parent/child

### 5.2 Event-to-Observation Mapping

| Hook Event | Langfuse Observation Type | Metadata |
|------------|--------------------------|----------|
| `SessionStart` | SPAN | event_type, session_start_time |
| `UserPromptSubmit` | SPAN | event_type, user_input |
| `PreToolUse` + `PostToolUse` | SPAN | event_type, tool_name, latency_ms, status |
| `Stop` (LLM response) | GENERATION | model, usage, costs |
| `SubagentStop` | SPAN | event_type, child_trace_id, purpose |
| `SessionEnd` | SPAN | event_type, session_end_time |

---

## 6. Code Changes Summary

| File | Change Type | Purpose |
|------|-------------|---------|
| `.claude/hooks/log_to_langfuse.py` | **MODIFY** | Add event buffering, use TraceBuilder |
| `.claude/hooks/utils/event_buffer.py` | **NEW** | Event buffering per session |
| `.claude/hooks/utils/trace_builder.py` | **NEW** | Transform events → Langfuse trace |
| `.claude/hooks/send_event.py` | **MODIFY** | Capture parent_session_id for subagents |
| `.claude/hooks/utils/langfuse_config.py` | **MINOR** | Add agent_id helper |
| `.claude/hooks/sync_sqlite_to_langfuse.py` | **NEW (OPTIONAL)** | Backfill Langfuse from SQLite |

---

## 7. Backward Compatibility

Use feature flag to maintain backward compatibility:

```python
# In log_to_langfuse.py
if os.getenv("ENABLE_ENHANCED_TRACING", "false").lower() == "true":
    # Use new TraceBuilder
    builder = TraceBuilder(session_id, events)
    builder.build_trace(langfuse)
else:
    # Use existing simple trace
    trace_to_langfuse(session_id, user_message, assistant_message, ...)
```

**Environment Variable:**
```bash
# In .env
ENABLE_ENHANCED_TRACING=true  # Enable new multi-event tracing
```

---

## 8. Testing Strategy

### Unit Tests
- Event buffer operations
- Tool event matching (PreToolUse + PostToolUse)
- Hierarchy depth calculation
- Agent ID generation

### Integration Tests
- Full trace construction from event sequences
- Subagent linking and hierarchy
- Trace upload to Langfuse

### End-to-End Tests
- Simple tool usage ("list files")
- Multiple tools ("read and count lines")
- Subagent execution ("use search subagent")
- Error handling ("read non-existent file")

---

## 9. Success Metrics

### Technical Metrics
- **Event Capture Rate**: 100% of hook events buffered
- **Trace Completeness**: All observations present
- **Subagent Linking**: 100% linked to parent
- **Error Rate**: <1% trace construction failures
- **Performance**: <100ms overhead per event

### Dashboard Metrics
- **Real-time Updates**: Events appear within 1 second
- **Trace Visibility**: All traces queryable in Langfuse
- **Hierarchy Display**: Subagent trees visualized
- **Cost Tracking**: Accurate token/cost breakdown

---

## 10. Rollout Plan

### Development Environment (Week 1)
- Enable `ENABLE_ENHANCED_TRACING=true`
- Test with consulting-co project
- Verify traces in local Langfuse

### Staging Environment (Week 2)
- Deploy to RevStar quickstarts
- Test multi-org routing
- Verify project auto-creation

### Production Rollout (Week 3)
- Gradual rollout: 10% → 50% → 100%
- Monitor error rates
- Quick rollback if needed: Set flag to false

---

## 11. Future Enhancements

- **Real-Time Streaming**: WebSocket connection to Langfuse
- **Anomaly Detection**: Identify slow tools, high error rates
- **Cost Optimization**: Recommend cheaper models, cache opportunities
- **Custom Dashboards**: Project-specific tracking, team performance
- **Integration**: Neo4j (Graphiti) integration for entity discovery

---

## Summary

This upgrade plan enables:

1. **Multi-Event Capture**: All hook events tracked
2. **Hierarchical Traces**: Tools, user prompts, subagents
3. **Enhanced Metadata**: Agent IDs, source apps, hierarchy
4. **Dashboard Ready**: Full integration with observability platform
5. **Subagent Tracking**: Parent-child relationships, linked traces

**Next Steps**:
1. Review plan with team
2. Create implementation tasks
3. Begin Phase 1 (Event Capture)
4. Test with sample sessions
5. Iterate based on findings

---

**Status**: Ready for Implementation
**Version**: 1.0
