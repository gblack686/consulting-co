# Langfuse Agent 🔍

*Words and numbers dance in structured light*
*Each conversation leaves a glowing trace*

---

## Purpose

Capture the voice of Claude. Record every question asked, every answer given. Measure tokens, count cost, trace the flow of thought through execution.

---

## Core Mission

Transform conversations into queryable traces. Bridge the gap between human intent and machine response. Make invisible costs visible.

---

## Primary Files

### Main Hook Script
**`.claude/hooks/log_to_langfuse.py`** (uv run)
```
Trigger: Stop hook (session end)
Action: Read transcript → structure trace → send to Langfuse
Timeout: 10 seconds
```

### Configuration Manager
**`.claude/hooks/utils/langfuse_config.py`** (Python utility)
```
Project discovery by directory name
Multi-repo support
API credential management
```

---

## Hook Logic (The Poetry of Traces)

### Trace Structure

```
Trace: {project}-conversation
├── Input: User message
├── Output: Assistant response
│
├── Generation: claude-response
│   ├── Model: claude-sonnet-4-5-20250929
│   ├── Tokens: input, output, cache, thinking
│   └── Latency: conversation duration
│
└── Spans: tool-{name}
    ├── Read, Bash, Task, etc.
    ├── Latency per tool
    └── Input/output snippets
```

---

## Configuration Files

### Project Mapping
**`.claude/config/langfuse.yaml`**
```yaml
langfuse:
  base_url: http://localhost:3000
  organization: gbautomation

  projects:
    consulting-co: cmi19k90n000atd0713m9maij
    # Add more repos here
```

### Environment Variables
**`.env`**
```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=http://localhost:3000
LANGFUSE_PROJECT_ID=cmi19k90n000atd0713m9maij
PROJECT_NAME=consulting-co
ENABLE_LANGFUSE=true
```

---

## How It Works

### On Session End (Stop Hook)

1. **Read Transcript**
   - Parse JSONL format
   - Find last user message
   - Find following assistant response
   - Extract tool calls

2. **Extract Data**
   - User input text
   - Assistant response text
   - Model name (claude-sonnet-4-5-20250929)
   - Token usage (input, output, cache, thinking)
   - Start/end timestamps

3. **Get Tool Timings**
   - Call `utils/tool_timing.py`
   - Retrieve latency_ms per tool
   - Calculate total_tool_latency_ms

4. **Structure Trace**
   - Create top-level trace with project name
   - Add generation child observation
   - Add tool span for each tool invocation
   - Include all metadata

5. **Send to Langfuse**
   - POST to http://localhost:3000
   - Use Langfuse SDK v3
   - Auto-calculate token costs
   - Flush to ensure delivery

---

## Key Features

### Token Tracking
```python
# From log_to_langfuse.py
usage_details = {
    "input": input_tokens,
    "output": output_tokens,
    "cache_read_input_tokens": cache_read_tokens,      # 90% discount
    "cache_creation_input_tokens": cache_creation_tokens,
    "thinking_tokens": thinking_tokens
}
```

### Multi-Repo Support
```python
# From langfuse_config.py
project_id = config.get_current_project_id()
# Checks: LANGFUSE_PROJECT_ID env var
#         PROJECT_NAME env var
#         Current directory name
```

### Latency Measurement
```python
# Calculates:
conversation_latency_ms = (end_timestamp - start_timestamp) * 1000
llm_time_ms = max(0, conversation_latency_ms - total_tool_latency_ms)
tool_breakdown = {tool: latency_ms for tool in tools}
```

---

## Documentation

### Setup & Configuration
**`.claude/context/langfuse/LANGFUSE_SETUP.md`**
- Complete setup guide (400+ lines)
- Multi-repo configuration
- Troubleshooting

### Quick Reference
**`.claude/context/langfuse/QUICK_REFERENCE.md`**
- 5-minute verification
- Common commands
- Project mapping

### Implementation Details
**`.claude/context/langfuse/SETUP_COMPLETE.md`**
- What was configured
- Integration diagram
- Next steps

---

## Viewing Traces

1. Go to http://localhost:3000
2. Select gbautomation organization
3. Choose consulting-co project
4. Click Tracing → Traces
5. See your trace with full breakdown

---

## Debug Logging

**`.claude/langfuse_hook_debug.log`**
```
Logs every hook execution:
- Hook called at [timestamp]
- Session ID, event type
- Messages extracted
- Tool calls found
- Tokens counted
- Success/failure status
```

Check for errors:
```bash
tail -20 .claude/langfuse_hook_debug.log
```

---

## Integration Points

**With Observability** (`.claude/hooks/send_event.py`)
- Receives real-time events from observability system
- Uses latency data for tool spans

**With Obsidian** (`.claude/scripts/obsidian_exporter.py`)
- Session metrics flow to markdown notes
- Performance tiers (Fast/Medium/Slow)

**With Neo4j** (`.claude/hooks/log_to_graphiti.py`)
- Both hooks fire on Stop event
- Independent but complementary

---

## Philosophy

> *Every conversation is valuable.*
> *Make costs visible. Measure impact.*
> *Let tokens tell their story.*

---

**Status**: ✅ Configured
**Organization**: gbautomation
**Current Project**: consulting-co
**Dashboard**: http://localhost:3000
**Integration**: Full (Observability + Obsidian + Neo4j)
