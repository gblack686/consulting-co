# OpenTelemetry Telemetry - Quick Reference

## What Was Implemented

A proper OpenTelemetry-based distributed tracing system for Claude Code that:
- Creates parent-child trace relationships in Langfuse
- Stores trace context in JSON files for cross-hook communication
- Tracks tool execution times and metadata
- Provides comprehensive session summaries
- Never breaks Claude Code execution (graceful degradation)

## Files Created (13 total, 87.6 KB)

### Core Hooks (4 files)
- `~/.claude/hooks/session_start.py` - Creates root trace
- `~/.claude/hooks/session_end.py` - Finalizes trace with summary
- `~/.claude/hooks/pre_tool_use.py` - Creates child spans (ENHANCED)
- `~/.claude/hooks/post_tool_use.py` - Updates child spans (ENHANCED)

### Utilities (2 files)
- `~/.claude/hooks/utils/trace_context.py` - Core trace management (NEW)
- `~/.claude/hooks/utils/tool_timing.py` - Tool timing (EXISTING)

### Configuration (1 file)
- `~/.claude/hooks/.env.example` - Langfuse config template

### Documentation (5 files)
- `~/.claude/hooks/TELEMETRY_SETUP.md` - Full setup guide
- `~/.claude/hooks/QUICK_START.md` - Quick start guide
- `~/.claude/hooks/TEST_COMMANDS.txt` - Test commands
- `.claude/context/telemetry/TELEMETRY_IMPLEMENTATION_SUMMARY.md` - Summary
- `.claude/context/telemetry/ARCHITECTURE_DIAGRAM.md` - Architecture

### Testing (1 file)
- `~/.claude/hooks/test_trace_flow.py` - Automated test script

## How Trace Context Flows

```
Session Start
  ↓
session_start.py
  - Generates: trace_id (32-char hex UUID)
  - Generates: root_span_id (16-char hex UUID)
  - Creates: Root trace in Langfuse
  - Saves: ~/.claude/trace_context/{session_id}.json
  ↓
pre_tool_use.py (for each tool)
  - Reads: Parent trace context from file
  - Creates: Child observation span
  - Links: parent_observation_id → root_span_id
  - Saves: Span reference in {session_id}_spans.json
  ↓
[Tool Executes]
  ↓
post_tool_use.py (for each tool)
  - Reads: Parent trace context
  - Finds: Matching pending child span
  - Updates: Span with output and latency_ms
  - Marks: Span as completed
  ↓
session_end.py
  - Reads: All child observations
  - Calculates: Summary statistics
  - Updates: Root trace with metadata
  - Cleans: Session files
```

## Setup (5 minutes)

```bash
# 1. Install dependencies
pip install langfuse python-dotenv

# 2. Configure Langfuse
cd ~/.claude/hooks
cp .env.example .env
# Edit .env with your API keys from https://cloud.langfuse.com/settings

# 3. Test
python test_trace_flow.py

# 4. Verify
# Go to https://cloud.langfuse.com/traces
# Look for traces starting with "claude-session-"
```

## Quick Test

```bash
# Manual session simulation
echo '{"session_id":"test-001"}' | python ~/.claude/hooks/session_start.py
cat ~/.claude/trace_context/test-001.json

echo '{"session_id":"test-001","tool_name":"Read","tool_input":{"file_path":"/tmp/test"}}' | \
  python ~/.claude/hooks/pre_tool_use.py

echo '{"session_id":"test-001","tool_name":"Read","tool_output":"content"}' | \
  python ~/.claude/hooks/post_tool_use.py

echo '{"session_id":"test-001"}' | python ~/.claude/hooks/session_end.py

# Check debug log
tail -20 ~/.claude/hooks/trace_debug.log
```

## Key Features

- **OpenTelemetry Compliance**: Proper 32-char trace IDs, 16-char span IDs
- **Parent-Child Relationships**: Uses parent_observation_id
- **File-Based Persistence**: JSON files survive across hook invocations
- **Graceful Degradation**: Never breaks Claude Code execution
- **No Transcript Parsing**: Uses real-time hook data only
- **Rich Metadata**: Tool names, inputs, outputs, latencies
- **Summary Statistics**: Tool counts, total latency, per-tool breakdown
- **Debug Logging**: Troubleshooting support

## Troubleshooting

### No traces in Langfuse?
```bash
# Check credentials
cat ~/.claude/hooks/.env | grep LANGFUSE

# Check debug log
tail -100 ~/.claude/hooks/trace_debug.log

# Verify SDK
python -c "import langfuse; print('OK')"
```

### Enable debug logging
```bash
echo "DEBUG_TRACE_LOGGING=true" >> ~/.claude/hooks/.env
tail -f ~/.claude/hooks/trace_debug.log
```

## File Locations

```
~/.claude/
├── hooks/
│   ├── session_start.py         # Creates root trace
│   ├── session_end.py           # Finalizes trace
│   ├── pre_tool_use.py          # Creates child spans
│   ├── post_tool_use.py         # Updates child spans
│   ├── .env                     # Your config
│   ├── trace_debug.log          # Debug output
│   └── utils/
│       └── trace_context.py     # Core utilities
│
├── trace_context/               # Session trace data
│   ├── {session_id}.json        # Root trace context
│   └── {session_id}_spans.json  # Child spans
│
└── tool_timings/                # Tool timing data
    └── {session_id}.json
```

## Environment Variables

```bash
LANGFUSE_PUBLIC_KEY      # Required - from Langfuse settings
LANGFUSE_SECRET_KEY      # Required - from Langfuse settings
LANGFUSE_HOST            # Optional - default: cloud.langfuse.com
DEBUG_TRACE_LOGGING      # Optional - default: false
DEBUG_TOOL_TIMING        # Optional - default: false
```

## What You'll See in Langfuse

Navigate to: https://cloud.langfuse.com/traces

Each trace shows:
- **Trace Name**: `claude-session-{session_id}`
- **Root Span**: `claude-session-root`
- **Child Spans**: One per tool execution
  - Tool name, input, output (truncated to 1KB)
  - Execution latency in milliseconds
- **Summary Metadata**:
  - Total tool count
  - Total latency
  - Per-tool breakdown (counts + latencies)

## Next Steps

1. Set up Langfuse account: https://cloud.langfuse.com
2. Get API keys: Settings → API Keys
3. Configure .env: `cp .env.example .env` && edit
4. Test: `python test_trace_flow.py`
5. Use Claude Code normally - traces appear automatically!

## Full Documentation

- Quick Start: `~/.claude/hooks/QUICK_START.md`
- Full Setup: `~/.claude/hooks/TELEMETRY_SETUP.md`
- Architecture: `.claude/context/telemetry/ARCHITECTURE_DIAGRAM.md`
- Summary: `.claude/context/telemetry/TELEMETRY_IMPLEMENTATION_SUMMARY.md`
