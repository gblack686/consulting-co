# OpenTelemetry Multi-Process Context Propagation Architecture

## Executive Summary

This document provides comprehensive guidance on implementing OpenTelemetry span nesting and context propagation across multiple processes, specifically for PreToolUse, PostToolUse, and Stop hooks that run in separate processes. It includes architecture diagrams, code patterns, and best practices for real-time span creation with Langfuse SDK v3.

---

## 1. Core Concepts

### 1.1 OpenTelemetry Context Propagation

**Context Propagation** is the mechanism that moves trace context (trace_id, span_id, trace_flags) between services and processes, enabling distributed tracing across process boundaries.

**Key Components:**
- **Trace ID**: 32-character lowercase hexadecimal string (128 bits) - Identifies the entire trace
- **Span ID**: 16-character lowercase hexadecimal string (64 bits) - Identifies a specific span
- **Parent Span ID**: The span_id of the parent span (used to establish hierarchy)
- **Trace Flags**: 2-character hex string indicating sampling decisions (01 = sampled, 00 = not sampled)

### 1.2 W3C Trace Context Standard

The `traceparent` header format:
```
{version}-{trace-id}-{parent-id}-{trace-flags}
Example: 00-a9c3b99a95cc045e573e163c3ac80a77-d99d251a8caecd06-01
```

### 1.3 Langfuse SDK v3 and OpenTelemetry

Langfuse SDK v3 is built on OpenTelemetry and uses:
- **OTel Trace** = **Langfuse Trace** (same ID)
- **OTel Span** = **Langfuse Observation** (spans, generations, events)
- **Context Propagation**: Automatic parent-child relationships via OpenTelemetry context
- **Attribute Propagation**: Langfuse-specific attributes (user_id, session_id, metadata) can be propagated via `propagate_attributes()`

---

## 2. Architecture Diagram: Hook-Based Multi-Process Tracing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Main Process (Session)                           │
│                                                                         │
│  SessionStart Hook                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 1. Create root span (SessionStartSpan)                           │  │
│  │    trace_id: a9c3b99a95cc045e573e163c3ac80a77                    │  │
│  │    span_id:  d99d251a8caecd06                                    │  │
│  │                                                                  │  │
│  │ 2. Store in session state:                                       │  │
│  │    - trace_id                                                    │  │
│  │    - span_id (becomes parent_span_id for child spans)            │  │
│  │                                                                  │  │
│  │ 3. Inject context into carrier dict                              │  │
│  │    carrier = {'traceparent': '00-a9c3...77-d99d...06-01'}        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Context passed to subprocess
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Subprocess 1 (PreToolUse Hook)                        │
│                                                                         │
│  1. Receive context from main process                                   │
│     - Via function arguments: trace_id, parent_span_id                  │
│     - Or via carrier dict: {'traceparent': '00-...'}                    │
│                                                                         │
│  2. Extract context from carrier OR construct manually                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ from opentelemetry.trace.propagation.tracecontext import \       │  │
│  │     TraceContextTextMapPropagator                                │  │
│  │                                                                  │  │
│  │ # Method A: Extract from carrier                                │  │
│  │ ctx = TraceContextTextMapPropagator().extract(carrier=carrier)   │  │
│  │                                                                  │  │
│  │ # Method B: Use Langfuse trace_context                           │  │
│  │ langfuse.start_as_current_span(                                  │  │
│  │     name="PreToolUse",                                           │  │
│  │     trace_context={                                              │  │
│  │         "trace_id": "a9c3b99a95cc045e573e163c3ac80a77",          │  │
│  │         "parent_span_id": "d99d251a8caecd06"                     │  │
│  │     }                                                            │  │
│  │ )                                                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  3. Create child span (PreToolUseSpan)                                  │
│     trace_id:        a9c3b99a95cc045e573e163c3ac80a77 (inherited)       │
│     span_id:         e12f456b9cde7890 (new)                             │
│     parent_span_id:  d99d251a8caecd06 (from SessionStartSpan)           │
│                                                                         │
│  4. Update span with tool metadata                                      │
│     - tool_name                                                         │
│     - tool_input                                                        │
│     - validation results                                                │
│                                                                         │
│  5. End span and flush                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Tool execution happens
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Subprocess 2 (PostToolUse Hook)                       │
│                                                                         │
│  1. Receive same trace_id, but different parent_span_id                 │
│     - trace_id: a9c3b99a95cc045e573e163c3ac80a77 (same)                 │
│     - parent_span_id: d99d251a8caecd06 (SessionStartSpan)               │
│                                                                         │
│  2. Create child span (PostToolUseSpan)                                 │
│     trace_id:        a9c3b99a95cc045e573e163c3ac80a77 (inherited)       │
│     span_id:         f34g678h0ijk1234 (new)                             │
│     parent_span_id:  d99d251a8caecd06 (from SessionStartSpan)           │
│                                                                         │
│  3. Update span with tool results                                       │
│     - tool_output                                                       │
│     - execution_time                                                    │
│     - error_info (if any)                                               │
│                                                                         │
│  4. End span and flush                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ More tools execute...
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Subprocess 3 (Task Tool - Subagent)                   │
│                                                                         │
│  1. Receive parent context from Task tool invocation                    │
│     - trace_id: a9c3b99a95cc045e573e163c3ac80a77 (same)                 │
│     - parent_span_id: g56h890i2jkl5678 (from Task tool span)            │
│                                                                         │
│  2. Create NEW child span for subagent work                             │
│     trace_id:        a9c3b99a95cc045e573e163c3ac80a77 (inherited)       │
│     span_id:         h78i901j3klm6789 (new)                             │
│     parent_span_id:  g56h890i2jkl5678 (from Task tool)                  │
│                                                                         │
│  3. Subagent creates its own child spans                                │
│     - Each subagent tool call creates child spans                       │
│     - All share same trace_id                                           │
│     - Parent-child relationships preserved                              │
│                                                                         │
│  4. End all subagent spans and flush                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Session ends
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Subprocess 4 (Stop Hook)                            │
│                                                                         │
│  1. Receive root trace_id and span_id                                   │
│     - trace_id: a9c3b99a95cc045e573e163c3ac80a77                        │
│     - parent_span_id: d99d251a8caecd06 (root span)                      │
│                                                                         │
│  2. Create final summary span (StopSpan)                                │
│     trace_id:        a9c3b99a95cc045e573e163c3ac80a77 (inherited)       │
│     span_id:         i89j012k4lmn7890 (new)                             │
│     parent_span_id:  d99d251a8caecd06 (from SessionStartSpan)           │
│                                                                         │
│  3. Update with session summary                                         │
│     - total_tools_used                                                  │
│     - total_tokens                                                      │
│     - session_duration                                                  │
│     - errors_encountered                                                │
│                                                                         │
│  4. Update trace-level attributes                                       │
│     langfuse.update_current_trace(                                      │
│         output={"session_summary": {...}},                              │
│         metadata={"final_stats": {...}}                                 │
│     )                                                                   │
│                                                                         │
│  5. End span, flush, and shutdown                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

FINAL TRACE STRUCTURE IN LANGFUSE:
═══════════════════════════════════

Trace: a9c3b99a95cc045e573e163c3ac80a77
├── SessionStartSpan (d99d251a8caecd06)
│   ├── PreToolUseSpan (e12f456b9cde7890)
│   ├── PostToolUseSpan (f34g678h0ijk1234)
│   ├── TaskToolSpan (g56h890i2jkl5678)
│   │   └── SubagentSpan (h78i901j3klm6789)
│   │       ├── SubagentTool1Span
│   │       └── SubagentTool2Span
│   └── StopSpan (i89j012k4lmn7890)
```

---

## 3. Code Patterns for Context Propagation

### 3.1 Pattern A: Using TraceContextTextMapPropagator (Standard OpenTelemetry)

**In Parent Process (SessionStart Hook):**
```python
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from langfuse import get_client

langfuse = get_client()

# Create root span
with langfuse.start_as_current_span(name="SessionStart") as session_span:
    # Get trace_id and span_id
    trace_id = session_span.trace_id
    span_id = session_span.id

    # Inject context into carrier
    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)

    # carrier now contains: {'traceparent': '00-{trace_id}-{span_id}-01'}

    # Store carrier in session state for hooks to use
    session_state['trace_carrier'] = carrier
    session_state['trace_id'] = trace_id
    session_state['root_span_id'] = span_id
```

**In Child Process (PreToolUse Hook):**
```python
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry import context
from langfuse import get_client

langfuse = get_client()

# Receive carrier from parent process
carrier = hook_context.get('trace_carrier')  # {'traceparent': '00-...'}

# Extract context from carrier
ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

# Method 1: Pass context parameter directly
with langfuse.start_as_current_span(
    name="PreToolUse",
    context=ctx  # Uses extracted context
) as span:
    span.update(
        input={"tool_name": tool_name, "tool_input": tool_input},
        metadata={"hook": "PreToolUse"}
    )
    # Span automatically becomes child of SessionStartSpan

# Method 2: Attach context to make it current
token = context.attach(ctx)
try:
    with langfuse.start_as_current_span(name="PreToolUse") as span:
        span.update(input={"tool_name": tool_name})
        # Span automatically uses attached context
finally:
    context.detach(token)
```

### 3.2 Pattern B: Using Langfuse trace_context Parameter (Simplified)

**In Parent Process (SessionStart Hook):**
```python
from langfuse import get_client

langfuse = get_client()

# Create root span
with langfuse.start_as_current_span(name="SessionStart") as session_span:
    # Store IDs in session state
    session_state['trace_id'] = session_span.trace_id
    session_state['root_span_id'] = session_span.id

    # Set trace-level attributes
    session_span.update_trace(
        user_id="user_123",
        session_id="session_456",
        metadata={"environment": "production"}
    )
```

**In Child Process (PreToolUse Hook):**
```python
from langfuse import get_client

langfuse = get_client()

# Receive IDs from parent process
trace_id = hook_context.get('trace_id')
parent_span_id = hook_context.get('root_span_id')

# Create child span with explicit trace_context
with langfuse.start_as_current_span(
    name="PreToolUse",
    trace_context={
        "trace_id": trace_id,  # 32 hex chars
        "parent_span_id": parent_span_id  # 16 hex chars
    }
) as span:
    span.update(
        input={
            "tool_name": tool_name,
            "tool_input": tool_input,
            "timestamp": datetime.now().isoformat()
        },
        metadata={"hook": "PreToolUse", "process_id": os.getpid()}
    )

    # This span is now a child of SessionStartSpan in the same trace
```

### 3.3 Pattern C: Manual Span Context Construction (Advanced)

**When you only have trace_id and span_id as integers or need full control:**

```python
from opentelemetry import trace
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
from langfuse import get_client

langfuse = get_client()

# Construct SpanContext manually
span_context = SpanContext(
    trace_id=int(trace_id_hex, 16),  # Convert hex string to int
    span_id=int(parent_span_id_hex, 16),  # Convert hex string to int
    is_remote=True,  # Indicates this came from another process
    trace_flags=TraceFlags(0x01)  # 01 = sampled
)

# Create context with this span
ctx = trace.set_span_in_context(NonRecordingSpan(span_context))

# Use context when creating span
with langfuse.start_as_current_span(
    name="PreToolUse",
    context=ctx
) as span:
    span.update(input={"tool_name": tool_name})
```

---

## 4. Real-Time Span Creation in Hooks

### 4.1 Best Practices

1. **Create spans IMMEDIATELY when hooks fire** - Don't wait until completion
2. **Use context managers (`with` statements)** for automatic span lifecycle
3. **Update spans progressively** as information becomes available
4. **Always flush before subprocess exits**
5. **Set `is_remote=True`** when constructing contexts from another process

### 4.2 PreToolUse Hook Pattern

```python
from langfuse import get_client
from datetime import datetime

def pre_tool_use_hook(tool_name: str, tool_input: dict, hook_context: dict):
    """
    Called BEFORE tool executes - creates span in real-time.
    Runs in separate subprocess.
    """
    langfuse = get_client()

    # Get parent context
    trace_id = hook_context.get('trace_id')
    parent_span_id = hook_context.get('root_span_id')

    # Create span immediately
    with langfuse.start_as_current_span(
        name=f"PreToolUse-{tool_name}",
        trace_context={
            "trace_id": trace_id,
            "parent_span_id": parent_span_id
        }
    ) as span:
        # Update with initial data
        span.update(
            input={
                "tool_name": tool_name,
                "tool_input": tool_input,
                "invocation_time": datetime.now().isoformat()
            },
            metadata={
                "hook": "PreToolUse",
                "process_id": os.getpid(),
                "thread_id": threading.get_ident()
            }
        )

        # Perform pre-tool validation/logging
        validation_result = validate_tool_input(tool_input)

        # Update span with validation result
        span.update(
            metadata={
                "validation_passed": validation_result.is_valid,
                "validation_errors": validation_result.errors
            }
        )

        # Span automatically ends when exiting context manager

    # Flush to ensure data is sent before subprocess exits
    langfuse.flush()
```

### 4.3 PostToolUse Hook Pattern

```python
from langfuse import get_client
from datetime import datetime

def post_tool_use_hook(
    tool_name: str,
    tool_input: dict,
    tool_output: any,
    error: Exception | None,
    hook_context: dict
):
    """
    Called AFTER tool executes - creates span with results.
    Runs in separate subprocess.
    """
    langfuse = get_client()

    # Get parent context
    trace_id = hook_context.get('trace_id')
    parent_span_id = hook_context.get('root_span_id')

    # Create span immediately
    with langfuse.start_as_current_span(
        name=f"PostToolUse-{tool_name}",
        trace_context={
            "trace_id": trace_id,
            "parent_span_id": parent_span_id
        }
    ) as span:
        # Determine span level based on error
        level = "ERROR" if error else "DEFAULT"

        # Update with tool results
        span.update(
            input={
                "tool_name": tool_name,
                "tool_input": tool_input
            },
            output={
                "tool_output": tool_output if not error else None,
                "error": str(error) if error else None,
                "completion_time": datetime.now().isoformat()
            },
            level=level,
            status_message=str(error) if error else "Success",
            metadata={
                "hook": "PostToolUse",
                "has_error": bool(error)
            }
        )

        # Additional processing...

    langfuse.flush()
```

### 4.4 Stop Hook Pattern

```python
from langfuse import get_client
from datetime import datetime

def stop_hook(session_summary: dict, hook_context: dict):
    """
    Called when session ends - creates final summary span.
    Runs in separate subprocess.
    """
    langfuse = get_client()

    # Get parent context
    trace_id = hook_context.get('trace_id')
    root_span_id = hook_context.get('root_span_id')

    # Create final span
    with langfuse.start_as_current_span(
        name="SessionStop",
        trace_context={
            "trace_id": trace_id,
            "parent_span_id": root_span_id
        }
    ) as span:
        # Update span with session summary
        span.update(
            input={"trigger": "session_end"},
            output={
                "session_summary": session_summary,
                "end_time": datetime.now().isoformat()
            },
            metadata={
                "hook": "Stop",
                "total_tools": session_summary.get('tool_count', 0),
                "total_errors": session_summary.get('error_count', 0)
            }
        )

        # Update TRACE-LEVEL attributes (applies to entire trace)
        span.update_trace(
            output={
                "final_summary": session_summary,
                "session_duration_seconds": session_summary.get('duration', 0)
            },
            metadata={
                "total_tokens_used": session_summary.get('total_tokens', 0),
                "session_success": session_summary.get('error_count', 0) == 0
            }
        )

    # Critical: Flush and shutdown before subprocess exits
    langfuse.flush()
    langfuse.shutdown()
```

---

## 5. Task Tool and Subagent Context Propagation

### 5.1 Task Tool Pattern

When the main agent uses the Task tool to spawn a subagent, the context should flow:

```
Main Agent Trace
├── SessionStartSpan
│   ├── MainAgentTool1Span
│   ├── TaskToolSpan  ← Task tool invocation
│   │   └── SubagentRootSpan  ← Subagent work (CHILD of TaskToolSpan)
│   │       ├── SubagentTool1Span
│   │       └── SubagentTool2Span
│   └── MainAgentTool2Span
```

### 5.2 Implementation

**In Task Tool Invocation (Main Agent):**
```python
from langfuse import get_client

langfuse = get_client()

# Main agent creates span for Task tool
with langfuse.start_as_current_span(
    name="Task-Tool",
    as_type="span"
) as task_span:
    # Get current trace and span IDs
    trace_id = task_span.trace_id
    task_span_id = task_span.id  # This becomes parent for subagent

    # Update with task details
    task_span.update(
        input={
            "task_description": "Analyze data and generate report",
            "subagent_config": {...}
        }
    )

    # Pass context to subagent
    subagent_result = invoke_subagent(
        task_description="...",
        trace_id=trace_id,
        parent_span_id=task_span_id  # Subagent becomes child
    )

    task_span.update(
        output={"subagent_result": subagent_result}
    )
```

**In Subagent Process:**
```python
from langfuse import get_client

def run_subagent(task: str, trace_id: str, parent_span_id: str):
    """
    Subagent runs in its own process but maintains trace lineage.
    """
    langfuse = get_client()

    # Create subagent root span as child of Task tool span
    with langfuse.start_as_current_span(
        name="Subagent-Execution",
        trace_context={
            "trace_id": trace_id,  # Same trace as main agent
            "parent_span_id": parent_span_id  # Task tool span
        }
    ) as subagent_span:
        subagent_span.update(
            input={"task": task},
            metadata={"subagent": True, "process_id": os.getpid()}
        )

        # Subagent's tool calls automatically become children
        # because subagent_span is current in context
        result = execute_subagent_task(task)

        subagent_span.update(output={"result": result})

    langfuse.flush()
    return result

def execute_subagent_task(task: str):
    """
    Individual subagent operations create child spans automatically.
    """
    langfuse = get_client()

    # This span automatically becomes child of subagent_span
    with langfuse.start_as_current_span(name="Subagent-Tool-1") as span:
        span.update(input={"operation": "data_analysis"})
        # ... work ...
        span.update(output={"analysis_result": "..."})

    # Another child span
    with langfuse.start_as_current_span(name="Subagent-Tool-2") as span:
        span.update(input={"operation": "report_generation"})
        # ... work ...
        span.update(output={"report": "..."})

    return "task_complete"
```

---

## 6. Storage and Passing Recommendations

### 6.1 What to Store in Session State

```python
# In SessionStart Hook
session_state = {
    # REQUIRED for child processes
    'trace_id': 'a9c3b99a95cc045e573e163c3ac80a77',  # 32 hex chars
    'root_span_id': 'd99d251a8caecd06',  # 16 hex chars

    # OPTIONAL: Full carrier for OpenTelemetry compatibility
    'trace_carrier': {
        'traceparent': '00-a9c3b99a95cc045e573e163c3ac80a77-d99d251a8caecd06-01'
    },

    # OPTIONAL: Additional context
    'user_id': 'user_123',
    'session_id': 'session_456',
    'environment': 'production'
}
```

### 6.2 How to Pass to Subprocess Hooks

**Option 1: Function Arguments (Recommended)**
```python
def invoke_hook_subprocess(hook_fn, hook_context):
    """
    Pass context as function arguments.
    Most reliable for multiprocessing.
    """
    return hook_fn(
        trace_id=hook_context['trace_id'],
        parent_span_id=hook_context['root_span_id'],
        # ... other args
    )
```

**Option 2: Environment Variables (For Subprocesses)**
```python
import os
import subprocess

# Set environment variable
env = os.environ.copy()
env['TRACEPARENT'] = f"00-{trace_id}-{span_id}-01"

# Subprocess can read TRACEPARENT
result = subprocess.run(
    ['python', 'hook_script.py'],
    env=env
)

# In hook_script.py:
traceparent = os.environ.get('TRACEPARENT')
ctx = TraceContextTextMapPropagator().extract({'traceparent': traceparent})
```

**Option 3: Shared Memory/IPC (For Complex Data)**
```python
from multiprocessing import Manager

# In parent process
manager = Manager()
shared_state = manager.dict()
shared_state['trace_id'] = trace_id
shared_state['root_span_id'] = root_span_id

# In subprocess
trace_id = shared_state['trace_id']
parent_span_id = shared_state['root_span_id']
```

### 6.3 Data Format Requirements

**Trace ID:**
- Format: 32-character lowercase hexadecimal string
- Example: `a9c3b99a95cc045e573e163c3ac80a77`
- Validation: `^[0-9a-f]{32}$`

**Span ID:**
- Format: 16-character lowercase hexadecimal string
- Example: `d99d251a8caecd06`
- Validation: `^[0-9a-f]{16}$`

**Traceparent Header:**
- Format: `{version}-{trace-id}-{span-id}-{flags}`
- Example: `00-a9c3b99a95cc045e573e163c3ac80a77-d99d251a8caecd06-01`
- Validation: `^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$`

---

## 7. Common Pitfalls and Solutions

### 7.1 Pitfall: Forgetting to Flush

**Problem:**
```python
def hook_subprocess():
    langfuse = get_client()
    with langfuse.start_as_current_span(name="Hook") as span:
        span.update(output="done")
    # Process exits - data lost!
```

**Solution:**
```python
def hook_subprocess():
    langfuse = get_client()
    with langfuse.start_as_current_span(name="Hook") as span:
        span.update(output="done")

    langfuse.flush()  # ✓ Ensures data is sent
    langfuse.shutdown()  # ✓ Clean shutdown
```

### 7.2 Pitfall: Using Wrong Parent Span ID

**Problem:**
```python
# In PostToolUse hook - using PreToolUse span_id as parent
trace_id = ctx['trace_id']
parent_span_id = ctx['pre_tool_span_id']  # ✗ WRONG!

# Results in incorrect hierarchy:
# SessionStart
#   └── PreToolUse
#       └── PostToolUse  # Should be sibling, not child!
```

**Solution:**
```python
# Always use ROOT span_id for hooks
trace_id = ctx['trace_id']
parent_span_id = ctx['root_span_id']  # ✓ CORRECT!

# Results in correct hierarchy:
# SessionStart
#   ├── PreToolUse
#   └── PostToolUse  # Siblings, both children of SessionStart
```

### 7.3 Pitfall: Not Setting is_remote=True

**Problem:**
```python
span_context = SpanContext(
    trace_id=int(trace_id, 16),
    span_id=int(span_id, 16),
    is_remote=False,  # ✗ Should be True for cross-process
    trace_flags=TraceFlags(0x01)
)
```

**Solution:**
```python
span_context = SpanContext(
    trace_id=int(trace_id, 16),
    span_id=int(span_id, 16),
    is_remote=True,  # ✓ Indicates cross-process span
    trace_flags=TraceFlags(0x01)
)
```

### 7.4 Pitfall: Creating Orphaned Traces

**Problem:**
```python
# Forgetting to pass trace_context
with langfuse.start_as_current_span(name="Hook") as span:
    # Creates NEW trace instead of joining existing one!
    pass
```

**Solution:**
```python
# Always pass trace_context in subprocess
with langfuse.start_as_current_span(
    name="Hook",
    trace_context={
        "trace_id": trace_id,
        "parent_span_id": parent_span_id
    }
) as span:
    # ✓ Joins existing trace
    pass
```

---

## 8. Complete Working Example

```python
# ============================================================================
# FILE: session_manager.py
# Main process - manages session and invokes hooks
# ============================================================================

from langfuse import get_client
from multiprocessing import Process
import hooks

def start_session(user_id: str, session_id: str):
    """Main session entry point"""
    langfuse = get_client()

    # Create root session span
    with langfuse.start_as_current_span(
        name="Claude-Code-Session",
        as_type="span"
    ) as session_span:
        # Set trace-level attributes
        session_span.update_trace(
            user_id=user_id,
            session_id=session_id,
            metadata={"environment": "production"}
        )

        # Extract context for hooks
        trace_id = session_span.trace_id
        root_span_id = session_span.id

        # Create hook context
        hook_context = {
            'trace_id': trace_id,
            'root_span_id': root_span_id,
            'user_id': user_id,
            'session_id': session_id
        }

        # Simulate tool execution
        tool_name = "Read"
        tool_input = {"file_path": "/path/to/file"}

        # PreToolUse Hook (subprocess)
        p1 = Process(
            target=hooks.pre_tool_use_hook,
            args=(tool_name, tool_input, hook_context)
        )
        p1.start()
        p1.join()

        # Tool execution
        tool_output = {"content": "file contents..."}

        # PostToolUse Hook (subprocess)
        p2 = Process(
            target=hooks.post_tool_use_hook,
            args=(tool_name, tool_input, tool_output, None, hook_context)
        )
        p2.start()
        p2.join()

        # Session end
        session_summary = {
            'tool_count': 1,
            'error_count': 0,
            'duration': 10.5
        }

        # Stop Hook (subprocess)
        p3 = Process(
            target=hooks.stop_hook,
            args=(session_summary, hook_context)
        )
        p3.start()
        p3.join()

    # Flush main process
    langfuse.flush()


# ============================================================================
# FILE: hooks.py
# Hook implementations running in subprocesses
# ============================================================================

from langfuse import get_client
from datetime import datetime
import os

def pre_tool_use_hook(tool_name: str, tool_input: dict, hook_context: dict):
    """PreToolUse hook - runs in subprocess"""
    langfuse = get_client()

    trace_id = hook_context['trace_id']
    parent_span_id = hook_context['root_span_id']

    with langfuse.start_as_current_span(
        name=f"PreToolUse-{tool_name}",
        trace_context={
            "trace_id": trace_id,
            "parent_span_id": parent_span_id
        }
    ) as span:
        span.update(
            input={
                "tool_name": tool_name,
                "tool_input": tool_input,
                "timestamp": datetime.now().isoformat()
            },
            metadata={
                "hook": "PreToolUse",
                "process_id": os.getpid()
            }
        )

    langfuse.flush()


def post_tool_use_hook(
    tool_name: str,
    tool_input: dict,
    tool_output: any,
    error: Exception | None,
    hook_context: dict
):
    """PostToolUse hook - runs in subprocess"""
    langfuse = get_client()

    trace_id = hook_context['trace_id']
    parent_span_id = hook_context['root_span_id']

    with langfuse.start_as_current_span(
        name=f"PostToolUse-{tool_name}",
        trace_context={
            "trace_id": trace_id,
            "parent_span_id": parent_span_id
        }
    ) as span:
        level = "ERROR" if error else "DEFAULT"

        span.update(
            input={
                "tool_name": tool_name,
                "tool_input": tool_input
            },
            output={
                "tool_output": tool_output,
                "error": str(error) if error else None
            },
            level=level,
            metadata={
                "hook": "PostToolUse",
                "has_error": bool(error)
            }
        )

    langfuse.flush()


def stop_hook(session_summary: dict, hook_context: dict):
    """Stop hook - runs in subprocess"""
    langfuse = get_client()

    trace_id = hook_context['trace_id']
    root_span_id = hook_context['root_span_id']

    with langfuse.start_as_current_span(
        name="SessionStop",
        trace_context={
            "trace_id": trace_id,
            "parent_span_id": root_span_id
        }
    ) as span:
        span.update(
            input={"trigger": "session_end"},
            output={"session_summary": session_summary},
            metadata={
                "hook": "Stop",
                "total_tools": session_summary.get('tool_count', 0)
            }
        )

        # Update trace-level summary
        span.update_trace(
            output={"final_summary": session_summary},
            metadata={"session_success": session_summary.get('error_count', 0) == 0}
        )

    langfuse.flush()
    langfuse.shutdown()


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    start_session(user_id="user_123", session_id="session_456")
```

---

## 9. Key Takeaways

### 9.1 Essential Requirements

1. **Always pass `trace_id` and `parent_span_id`** to subprocess hooks
2. **Use `trace_context` parameter** in Langfuse SDK v3 for simplicity
3. **Flush before subprocess exits** to prevent data loss
4. **Use same `trace_id`** for entire session (all hooks, all processes)
5. **Use `root_span_id` as `parent_span_id`** for all hook spans

### 9.2 Architecture Decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Context Passing** | Function arguments + trace_context | Most reliable across processes |
| **Parent Span** | Always use root SessionStart span | Keeps hooks as siblings, not nested |
| **Storage Format** | Plain hex strings (trace_id, span_id) | Simple, compatible with Langfuse |
| **Propagation Method** | Langfuse trace_context parameter | Simpler than raw OpenTelemetry |
| **Flush Strategy** | Flush after each hook completes | Ensures data captured even if crash |

### 9.3 Performance Considerations

- **Flush overhead**: ~10-50ms per flush
- **Context extraction**: < 1ms
- **Span creation**: < 1ms
- **Recommendation**: Flush after each hook is acceptable for hooks that run infrequently

---

## 10. References

### Documentation
- [Langfuse SDK v3 Documentation](https://langfuse.com/docs/observability/sdk/python/sdk-v3)
- [OpenTelemetry Context Propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
- [OpenTelemetry Python Cookbook](https://opentelemetry.io/docs/languages/python/cookbook/)
- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/)

### Key Concepts
- [Langfuse Trace IDs & Distributed Tracing](https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing)
- [OpenTelemetry Spans](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Context Propagation Best Practices](https://betterstack.com/community/guides/observability/otel-context-propagation/)

---

**Last Updated**: 2025-01-14
**Version**: 1.0
**Author**: Claude Code Research Assistant
