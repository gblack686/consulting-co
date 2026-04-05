# System Architecture Clarification

## Current State: Two Systems Need Integration

You have identified correctly that there's confusion about which system is being used. Let me clarify:

### System 1: Multi-Agent Observability Dashboard (UPSTREAM/PRIMARY)
**Location**: `./observability/`
**Purpose**: Real-time event capture and visualization
**Architecture**:
```
Claude Code Hooks → send_event.py → HTTP POST → Bun Server → SQLite → WebSocket → Vue Dashboard
```

**Data Model**:
- `source_app` - Application/project name
- `session_id` - Unique session identifier
- `hook_event_type` - PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, etc.
- `payload` - Event-specific data (tool_name, input, output, etc.)
- Display ID: `source_app:session_id[:8]`

**Status**: Working, real-time, event-based

### System 2: Langfuse Integration (NEW/COMPLEMENTARY)
**Location**: `.claude/hooks/log_to_langfuse.py` + Phase 1-4 infrastructure
**Purpose**: Cost tracking, performance analytics, trace analysis
**Architecture**:
```
Hook Events → Buffer → TraceBuilder → Langfuse Cloud → Dashboards/Analytics
```

**Data Model**:
- Traces with metadata (org, project, agent_id, source_app, hierarchy_depth, has_errors, etc.)
- Observations (tool calls, subagent calls, LLM generations)
- Cost and performance metrics
- Historical analytics and projections

**Status**: Partially integrated (missing hook integration)

---

## The Problem

### Issue 1: Hooks Don't Call log_to_langfuse.py
The session_end.py hook doesn't call `log_to_langfuse.py`, so:
- ❌ Traces aren't being sent to Langfuse
- ❌ Event buffering isn't working (buffer only lives in process memory)
- ❌ Only "Stop" event is captured, not intermediate events
- ❌ Subagent counts show 0

### Issue 2: Trace Naming Is Generic
Current: `consulting-co-conversation`
- Not descriptive
- Doesn't include user prompt summary
- Doesn't include tools used
- Doesn't include model type

Should be: `consulting-co-[short-prompt]-tools[count]`
- Example: `consulting-co-search-obsidian-tools2`
- Example: `consulting-co-bash-ls-tools1`

### Issue 3: Tags Are Not Useful
Current tags:
- `claude-code`
- `consulting-co`
- `conversation`

Should include:
- Tool types: `tool:bash`, `tool:read`, `tool:task`
- Model: `model:sonnet`, `model:haiku`
- Outcome: `status:success`, `status:error`
- Has subagents: `has:subagents`

### Issue 4: Event Count Is Low (Only 3)
Current: Shows total_events_buffered = 3 (SessionStart, UserPromptSubmit, Stop)

Should show: All intermediate events
- PreToolUse events
- PostToolUse events
- Multiple tool calls in long conversations

**Root Cause**: Event buffer doesn't persist between hook calls because it's in-process memory

---

## Solution: Unified Integration

### Architecture We Need
```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Hooks                         │
│  (PreToolUse, PostToolUse, UserPromptSubmit, SessionEnd)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ↓                             ↓
  ┌──────────────┐          ┌──────────────────┐
  │ send_event.py│          │ Langfuse Hook    │
  │ (Real-time)  │          │ Integration      │
  └──────┬───────┘          └────────┬─────────┘
         │                           │
         ↓                           ↓
  ┌──────────────┐          ┌──────────────────┐
  │ Observability│          │ Event Buffer     │
  │ Dashboard    │          │ (SQLite)         │
  │ (Upstream)   │          │ (Session-level)  │
  └──────────────┘          └────────┬─────────┘
                                     │
                            ┌────────┴─────────┐
                            ↓                  ↓
                      ┌──────────┐      ┌─────────────┐
                      │TraceBuilder    │Langfuse      │
                      │(Events→Trace)  │Cloud API     │
                      └──────────┘      └─────────────┘
```

### Step 1: Persist Event Buffer to SQLite
**File**: `.claude/hooks/utils/event_buffer.py`

Change from in-process to SQLite persistence:
```python
class EventBuffer:
    def __init__(self):
        self.db_path = Path.home() / ".claude" / "logs" / "events.db"
        self._init_db()

    def add_event(self, session_id: str, event: Dict[str, Any]):
        # Insert into SQLite, not just memory
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO events (session_id, hook_event_type, data, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, event['hook_event_type'], json.dumps(event), datetime.now().isoformat()))

    def get_events(self, session_id: str) -> List[Dict]:
        # Retrieve from SQLite across process boundaries
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            ).fetchall()
        return [json.loads(row[2]) for row in rows]  # data column
```

### Step 2: Improve Trace Naming
**File**: `.claude/hooks/log_to_langfuse.py` (~line 376)

```python
def generate_trace_name(user_message: str, tool_names: List[str], model: str) -> str:
    """Generate descriptive trace name from execution context."""

    # Extract first significant words from user prompt (max 20 chars)
    words = user_message.split()
    prompt_summary = "-".join(words[:2]).lower()[:20]

    # Get unique tool names
    unique_tools = list(dict.fromkeys(tool_names))  # Preserve order, remove duplicates

    # If too many tools, show count instead
    if len(unique_tools) > 3:
        tools_str = f"tools{len(unique_tools)}"
    else:
        tools_str = "-".join(unique_tools).lower()[:30]

    # Return: project-prompt-tools
    return f"consulting-co-{prompt_summary}-{tools_str}"

# Usage
trace_name = generate_trace_name(
    user_message="Do a Google search for Obsidian plugins",
    tool_names=["Bash", "Read", "Task"],
    model="claude-3-5-sonnet"
)
# Result: consulting-co-do-a-bash-read-task
```

### Step 3: Improve Tags
**File**: `.claude/hooks/log_to_langfuse.py` (~line 449)

```python
def generate_tags(
    tool_names: List[str],
    model_name: str,
    has_errors: bool,
    is_subagent: bool,
    hierarchy_depth: int,
    organization: str,
    project: str
) -> List[str]:
    """Generate meaningful tags for filtering and analysis."""

    tags = [
        organization,
        project,
        "claude-code",
    ]

    # Add model tags
    if "sonnet" in model_name.lower():
        tags.append("model:sonnet")
    elif "haiku" in model_name.lower():
        tags.append("model:haiku")
    elif "opus" in model_name.lower():
        tags.append("model:opus")

    # Add tool tags
    for tool in set(tool_names):  # Unique tools
        tags.append(f"tool:{tool.lower()}")

    # Add status tags
    if has_errors:
        tags.append("status:error")
    else:
        tags.append("status:success")

    # Add hierarchy tags
    if is_subagent:
        tags.append("agent:subagent")
    else:
        tags.append("agent:root")

    if is_subagent and hierarchy_depth > 1:
        tags.append(f"depth:{hierarchy_depth}")

    # Add complexity tags
    if len(tool_names) > 5:
        tags.append("complexity:high")
    elif len(tool_names) > 2:
        tags.append("complexity:medium")
    else:
        tags.append("complexity:low")

    return tags

# Usage
tags = generate_tags(
    tool_names=["Bash", "Read", "Task"],
    model_name="claude-3-5-sonnet-20241022",
    has_errors=False,
    is_subagent=False,
    hierarchy_depth=0,
    organization="consulting-co",
    project="consulting-co"
)
# Result: ["consulting-co", "consulting-co", "claude-code", "model:sonnet",
#          "tool:bash", "tool:read", "tool:task", "status:success",
#          "agent:root", "complexity:medium"]
```

### Step 4: Fix Session End Hook Integration
**File**: `.claude/hooks/session_end.py`

Add call to Langfuse logging:

```python
import sys
from pathlib import Path

# Add hooks/utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))

# Existing imports...
from trace_context import get_session_trace_context, calculate_trace_summary

# NEW: Import Langfuse logger
try:
    from log_to_langfuse import trace_to_langfuse
except ImportError:
    trace_to_langfuse = None


def main():
    """Process session end event."""
    # Get hook data
    hook_data = json.loads(os.environ.get("HOOK_DATA", "{}"))

    # Extract session context
    session_id = hook_data.get("session_id")
    organization = os.getenv("ORGANIZATION", "consulting-co")
    project = os.getenv("PROJECT", "consulting-co")

    # Get buffered events for Langfuse (NEW)
    from event_buffer import get_default_buffer
    buffer = get_default_buffer()
    all_events = buffer.get_events(session_id)

    # Send to Langfuse (NEW)
    if trace_to_langfuse and os.getenv("ENABLE_LANGFUSE", "false").lower() == "true":
        try:
            trace_to_langfuse(
                session_id=session_id,
                organization=organization,
                project_name=project,
                user_message=extract_user_message(all_events),
                assistant_message=hook_data.get("assistant_message", ""),
                tool_calls=extract_tool_calls(all_events),
                tool_timings=extract_tool_timings(all_events),
                model_name=hook_data.get("model", "claude-3-5-sonnet"),
                all_events=all_events
            )
            debug_log("✓ Sent trace to Langfuse")
        except Exception as e:
            debug_log(f"✗ Failed to send to Langfuse: {e}")

    # Existing trace finalization logic...
    finalize_trace(session_id)

    # Clean up buffer after successful send (NEW)
    buffer.clear_session(session_id)
```

### Step 5: Fix Event Buffering for All Events
Currently only capturing SessionStart, UserPromptSubmit, Stop.

Need to ensure hooks call:
```bash
# Pre-tool-use hook should also log to buffer
python3 .claude/hooks/utils/event_buffer.py add-event \
  --session-id $SESSION_ID \
  --event-type PreToolUse \
  --data '{"tool_name": "Bash", ...}'

# Post-tool-use hook should also log to buffer
python3 .claude/hooks/utils/event_buffer.py add-event \
  --session-id $SESSION_ID \
  --event-type PostToolUse \
  --data '{"tool_name": "Bash", "status": "success", ...}'
```

---

## Action Items

### Priority 1: Fix Integration (CRITICAL)
- [ ] Modify `event_buffer.py` to use SQLite persistence instead of in-process
- [ ] Update `session_end.py` to call `log_to_langfuse.py`
- [ ] Update `.claude/settings.json` to ensure all hooks call event buffer
- [ ] Test: Run a conversation and verify all events are captured (not just 3)

### Priority 2: Improve Trace Quality (HIGH)
- [ ] Add `generate_trace_name()` function
- [ ] Add `generate_tags()` function
- [ ] Update `log_to_langfuse.py` to use these functions
- [ ] Test: Verify trace names are descriptive and tags are useful

### Priority 3: Fix Subagent Tracking (MEDIUM)
- [ ] Verify subagent events are being captured in event buffer
- [ ] Check that `subagent_count` is populated correctly in traces
- [ ] Test: Run a subagent task and verify count > 0

---

## Compatibility Matrix

| Feature | Observability Dashboard | Langfuse | Status |
|---------|------------------------|----------|--------|
| Real-time events | ✅ Primary | ❌ No | Events go to dashboard first |
| Event buffer | ✅ Implied | ❌ Memory only | Need SQLite persistence |
| Trace naming | ✅ Basic | ⚠️ Generic | Need improvement |
| Tags | ✅ Limited | ⚠️ Not useful | Need enhancement |
| Subagent tracking | ✅ Supported | ⚠️ Broken | Need integration |
| Cost tracking | ❌ No | ✅ Yes | Different purpose |
| Analytics | ❌ No | ✅ Yes | Different purpose |

---

## Summary

**The observability dashboard is your REAL-TIME system** (upstream, primary)
**Langfuse is your ANALYTICS system** (complementary, cost tracking)

Both should:
- ✅ Receive ALL events (not just Stop)
- ✅ Have descriptive trace names
- ✅ Have meaningful tags
- ✅ Track subagent calls properly

The solution requires:
1. Persistent event buffer (SQLite)
2. Hook integration with log_to_langfuse.py
3. Better trace naming and tags
4. Full event capture (all hook types)

---

**Status**: Documentation complete
**Next Step**: Implement fixes in order of priority
