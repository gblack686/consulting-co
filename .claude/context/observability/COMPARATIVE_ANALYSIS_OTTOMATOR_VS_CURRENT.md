# Comparative Analysis: Ottomator Pydantic AI vs Current Claude Code Implementation
**Date:** November 16, 2025
**Analysis:** Trace Structure & Event Capture Differences

---

## Visual Reference: What's Missing

**Screenshot shows:** brave_agent_run with nested observations:
```
brave_agent_run (root)
├─ preparing model request params
├─ chat gpt-4.1-mini (1.16s, 323 → 28 tokens)
├─ running tools: brave_web_search (1.05s)
├─ preparing model request params
└─ chat gpt-4.1-mini (5.30s, 1513 → 300 tokens)
```

This shows **multiple generations and intermediate steps** within a single agent run.

---

## Architecture Comparison

### Ottomator's Approach: Framework-Level Integration

**Stack:**
- Pydantic AI agents with `instrument=True` flag
- Logfire for automatic OpenTelemetry instrumentation
- `@observe()` decorators for tracing
- Direct SDK integration (Langfuse + OpenAI)

**How it works:**
```python
brave_agent = Agent(
    get_model(),
    system_prompt="...",
    mcp_servers=[brave_server],
    instrument=True  # ← Automatic instrumentation!
)

@observe()  # ← Decorator-based tracing
async def run_agent():
    result = await brave_agent.run(query)
```

**Result:** Framework automatically generates:
- Nested observations for each generation
- Model call tracing with token counts
- Tool execution tracking
- Automatic timing/latency capture

### Your Approach: Hook-Level Manual Integration

**Stack:**
- Claude Code hooks (pre_tool_use, post_tool_use, stop, session_end)
- Manual event buffering to SQLite
- Turn-level trace aggregation
- Custom trace building (log_to_langfuse.py)

**How it works:**
```python
# stop.py fires after Claude response
def send_turn_trace_to_langfuse(session_id):
    all_events = buffer.get_events(session_id)
    # All events from this turn get sent as ONE trace
    trace_to_langfuse(all_events)
```

**Result:** Manual control but:
- ❌ No intermediate observations captured
- ❌ No token counts per generation
- ❌ No model reasoning steps
- ❌ No tool timing breakdown
- ❌ Flat structure (one generation per turn, no nesting)

---

## What's Different: Event Capture

### Ottomator: Rich Hierarchical Events

**What gets captured:**

1. **Agent Run (Root Trace)**
   - Session ID, user ID
   - Agent name and system prompt
   - Input/output

2. **Generation Events (Nested)**
   - Model name (gpt-4.1-mini)
   - Prompt content
   - Completion content
   - **Token counts:** input → output (323 → 28)
   - Duration (1.16s)
   - Stop reason

3. **Tool Execution Events (Nested)**
   - Tool name (brave_web_search)
   - Tool input
   - Tool output
   - Duration (1.05s)

4. **Planning/Reasoning Steps (Nested)**
   - "preparing model request params" (0.0s)
   - Shows agent deliberation

**Total events per trace:** 5-10+ depending on iterations

### Your Current System: Flat Single-Level Events

**What gets captured:**

1. **User Prompt Event**
   - User input message

2. **Tool Use Events** (if any)
   - Pre: Tool name, input
   - Post: Tool output

3. **Stop Event**
   - Assistant message

**Total events per turn:** 2-4 (flat structure, no nesting)

**Missing:**
- ❌ Token counts per generation
- ❌ Model name/version tracking
- ❌ Generation duration breakdown
- ❌ Multiple generations in one turn
- ❌ Agent reasoning/planning steps
- ❌ Intermediate observations

---

## Key Missing Features

### 1. Token Counting & Cost Tracking ⭐⭐⭐

**Ottomator shows:**
```
chat gpt-4.1-mini: 323 → 28 (1.16s)
```
- Input tokens: 323
- Output tokens: 28
- Duration: 1.16s
- Cost calculable: (323 * input_price) + (28 * output_price)

**Your current system:**
- ❌ No token counts
- ❌ No cost tracking
- ❌ Can't optimize for cost

**To fix:** Extract token counts from Claude's responses and include in trace metadata

### 2. Multiple Generations Per Turn ⭐⭐⭐

**Ottomator shows:**
- First generation: "preparing model request params" → "chat gpt-4.1-mini"
- Tool execution: "running tools: brave_web_search"
- Second generation: "preparing model request params" → "chat gpt-4.1-mini"

This shows **agent iteration** - trying, using tools, then responding again.

**Your current system:**
- One trace per turn
- But a turn might have multiple Claude generations (if using tools)
- Currently only captures final response

**To fix:** Create separate observations for each generation/tool call within a turn, not aggregate them

### 3. Intermediate Observations / Reasoning Steps ⭐⭐⭐

**Ottomator shows:**
- "preparing model request params" (0.0s) - agent preparation
- "chat gpt-4.1-mini" - actual generation
- "running tools" - tool execution
- Repeat...

**Your current system:**
- ❌ No preparation/reasoning steps
- ❌ No breakdown of what Claude is doing
- ❌ Black box - just input → output

**To fix:** Log each major step (thinking, planning, tool prep) as separate observations

### 4. Hierarchical/Nested Structure ⭐⭐

**Ottomator:**
```
Root Trace (agent_run)
├─ Span (preparing params)
├─ Generation (LLM call)
├─ Tool (tool execution)
└─ Generation (LLM call again)
```

**Your system:**
```
Trace (turn)
├─ Event (user prompt)
├─ Event (tool call)
└─ Event (stop)
```

Ottomator's nesting allows:
- Clear parent-child relationships
- Understanding which observations belong to which phase
- Better visualization in UI

**To fix:** Use nested observations instead of flat events

### 5. Tool Timing Breakdown ⭐

**Ottomator shows:**
- "running tools: brave_web_search (1.05s)"

Tool execution time is tracked separately, allowing:
- Identifying slow tools
- Optimizing tool selection
- Understanding latency sources

**Your current system:**
- Tool execution bundled with rest of turn
- No individual tool timing

**To fix:** Track tool execution as separate observation with start/end times

---

## Architecture Insights from Ottomator

### 1. Using Framework Instrumentation

Ottomator leverages **Pydantic AI's built-in instrumentation**:
```python
Agent(..., instrument=True)
```

This means:
- Every model call is automatically traced
- Every tool call is automatically tracked
- Token counts automatically captured
- Timing automatically recorded

**Your challenge:** Claude Code hooks are at the CLI level, not framework level
- Can't directly hook into Claude's internal generation
- Must manually capture what you can observe

### 2. Decorator-Based Observation

```python
@observe()
def main():
    result = brave_agent.run(query)
    return result
```

Decorators automatically create trace/span boundaries.

**Your equivalent:** session_id + turn_id as natural boundaries

### 3. Logfire + OpenTelemetry Integration

Ottomator uses **Logfire** (Pydantic's observability tool) which:
- Automatically instruments Python code
- Sends to OpenTelemetry endpoint
- Langfuse consumes OpenTelemetry data

This is **framework-aware** - understands Pydantic AI natively.

**Your approach:** Manual SDK calls to Langfuse (more manual, more control)

---

## What You CAN Improve Without Framework Access

### 1. Extract & Track Token Counts ✅

**Add to your traces:**
```python
from your_response_parsing import extract_tokens

metadata = {
    "input_tokens": 250,
    "output_tokens": 75,
    "total_tokens": 325,
    "estimated_cost": "0.0012"
}
```

**Source:** Claude's response object should include token counts

### 2. Create Nested Observations Instead of Flat Events ✅

**Instead of:**
```
Trace: consulting-co-search-python
├─ Event: UserPromptSubmit
├─ Event: PreToolUse
└─ Event: Stop
```

**Do:**
```
Trace: consulting-co-search-python
├─ Span: "Preparing request" (0.0s)
├─ Generation: "LLM Call" (1.2s, 250 → 75 tokens)
├─ Tool: "bash search" (0.8s)
└─ Generation: "Final response" (0.5s, 125 → 50 tokens)
```

### 3. Track Multiple Generations Per Turn ✅

If Claude response includes:
1. Initial generation
2. Tool calls
3. Tool results
4. Final generation

Log each as separate observations in the same trace:

```
Turn: "search for Python files"
├─ Gen #1: Initial thinking (prompt: "...", output: "I'll search...")
├─ Tool: bash (input: "find *.py", output: [...files])
├─ Gen #2: Format results (prompt: "Format these...", output: "Here are the files:")
```

### 4. Add Intermediate Steps ✅

Log decision points:
```
├─ Span: "Analyzing user request"
├─ Span: "Determining tools needed"
├─ Generation: "Actual LLM call"
├─ Span: "Processing tool results"
└─ Generation: "Formatting response"
```

### 5. Use Langfuse's Observation Types ✅

Instead of generic "Event", use:
- **Span:** Duration-based operations (preparing, analyzing, formatting)
- **Generation:** LLM calls (include prompt, output, model, tokens)
- **Tool:** Tool calls (include input, output, duration)
- **Chain:** Links between operations

---

## Recommended Immediate Changes

### Priority 1: Token Counting
```python
# In stop.py's send_turn_trace_to_langfuse()
metadata = extract_metadata_from_events(all_events)
metadata['tokens'] = {
    'input': get_token_count(user_message),
    'output': get_token_count(assistant_message)
}
```

### Priority 2: Nested Observations
```python
# Use Langfuse SDK's nested observation support
trace = langfuse_client.trace(name="...", session_id=session_id)

# Create nested observations instead of flat events
with trace.span(name="preparing_request") as span:
    # ... preparation

with trace.generation(name="llm_call", model="...", tokens=...) as gen:
    gen.input = user_prompt
    gen.output = response
```

### Priority 3: Track Multiple Generations
```python
# If turn has tool calls, create separate generations
for tool_call in tool_calls:
    with trace.span(name=f"tool_{tool_call.name}"):
        # Log tool execution
```

### Priority 4: Use Better Observation Types
```python
# Instead of:
add_event("PreToolUse", ...)

# Do:
trace.span(name="tool_preparation", input={...})
trace.tool(name="bash", input=..., output=...)
trace.generation(name="format_results", ...)
```

---

## Architecture Decision: Turn-Level vs Multi-Generation

### Your Current Choice: Turn-Level (One Trace Per Turn)
- ✅ Simple, clean separation
- ✅ Easy to understand turn boundaries
- ✅ Good for conversation threads
- ❌ Loses intermediate observations
- ❌ Can't see tool iteration

### Ottomator's Choice: Agent-Run Level (Multiple Generations Per Trace)
- ✅ Shows agent reasoning process
- ✅ Captures tool iteration
- ✅ Hierarchical visibility
- ❌ Larger traces
- ❌ Harder to separate distinct steps

**Recommendation:** Keep turn-level, but add **nested observations** within each turn:
```
Turn: "search for Python files"  ← Trace
├─ Span: Prepare request
├─ Generation: First LLM call
├─ Tool: Execute bash
├─ Generation: Process results
└─ Generation: Final response
```

This gives you:
- Clean turn boundaries (good for Claude Code context)
- Rich nesting (good for visibility)
- Token tracking (good for cost)
- Multiple generations (good for iteration)

---

## Summary of Gaps

| Feature | Ottomator | You | Priority |
|---------|-----------|-----|----------|
| Token counts | ✅ Per generation | ❌ | ⭐⭐⭐ |
| Multiple generations per turn | ✅ Yes | ❌ Single | ⭐⭐⭐ |
| Nested observations | ✅ Full hierarchy | ❌ Flat | ⭐⭐ |
| Tool timing breakdown | ✅ Yes | ❌ | ⭐⭐ |
| Intermediate steps | ✅ Yes | ❌ | ⭐⭐ |
| Observation types | ✅ All types | ⚠️ Mixed | ⭐ |
| Automatic instrumentation | ✅ Framework | ❌ Manual | N/A |
| Cost tracking | ✅ Yes | ❌ | ⭐⭐⭐ |

---

## Next Steps

### Short Term (Quick Wins)
1. Add token counting to traces
2. Add observation type specification (generation vs span vs tool)
3. Improve metadata extraction (add model info, timestamps)

### Medium Term (Better Structure)
4. Implement nested observations within turn
5. Track tool execution separately
6. Add cost calculation

### Long Term (Full Parity)
7. Consider multi-generation traces if needed
8. Add agent reasoning visualization
9. Implement sampling/cost optimization

---

**Key Takeaway:** Your turn-level approach is good, but you need **richer observations within each turn** - more granular event types, nested structure, and metadata (especially token counts). Ottomator's framework-level integration gives them these automatically; you'll need to add them manually via the Langfuse SDK.

*Last Updated: 2025-11-16 17:35 UTC*
