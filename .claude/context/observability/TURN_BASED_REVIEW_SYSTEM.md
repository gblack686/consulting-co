# Turn-Based Review System 🔄

*Automatic session analysis every 10 turns with mini-documentation*

---

## Overview

The Turn-Based Review System automatically tracks conversation turns, generates periodic session reviews using Claude Sonnet, and maintains lightweight documentation using Claude Haiku after each turn.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         User Turn Complete (Stop Hook)      │
└──────────────────┬──────────────────────────┘
                   ↓
        ┌──────────────────────┐
        │  Turn Counter         │
        │  (SQLite DB)          │
        │  - Increment count    │
        │  - Track history      │
        └──────────┬─────────────┘
                   ↓
        ┌──────────────────────┐
        │  Mini-Doc Agent       │
        │  (Haiku)              │
        │  - Quick summary      │
        │  - Append to log      │
        └──────────┬─────────────┘
                   ↓
        ┌──────────────────────┐
        │  Check Turn Count     │
        │  (Every 10 turns?)    │
        └──────────┬─────────────┘
                   ↓ (if turn % 10 == 0)
        ┌──────────────────────────────┐
        │  Trace Review Agent          │
        │  (Sonnet)                    │
        │  - Analyze 10 turns          │
        │  - Extract patterns          │
        │  - Generate insights         │
        │  - Call mini-doc-agent       │
        └──────────────────────────────┘
```

---

## Components

### 1. Turn Counter (SQLite)

**File**: `.claude/hooks/utils/turn_counter.py`

**Database**: `~/.claude/data/turn_counter.db`

**Tables**:
- `session_turns`: Session-level turn counts and review tracking
- `turn_history`: Individual turn records with messages

**Functions**:
- `increment_turn(session_id, user_message, assistant_message)` → Returns turn count
- `should_review(session_id, interval=10)` → Boolean
- `mark_reviewed(session_id)` → Updates last_review_turn
- `get_session_stats(session_id)` → Dict with turn count, timestamps
- `get_recent_turns(session_id, count=10)` → List of recent turns

---

### 2. Mini-Doc Agent (Haiku)

**File**: `.claude/hooks/mini_doc_agent.py`

**Model**: `claude-3-5-haiku-20241022` (fast + cost-effective)

**Purpose**: Generate quick 2-3 sentence summaries after each turn

**Output**: `~/.claude/data/session_docs/{session_id}/session_log.md`

**Process**:
1. Extract user message, assistant response, tools used
2. Call Claude Haiku with summary prompt
3. Append to session markdown log
4. Link to review files if applicable

**Environment Variables**:
- `ENABLE_MINI_DOC`: Enable/disable (default: true)

---

### 3. Trace Review Agent (Sonnet)

**File**: `.claude/hooks/trace_review_agent.py`

**Model**: `claude-3-5-sonnet-20241022` (analysis + insights)

**Purpose**: Deep analysis every 10 turns

**Output**: `~/.claude/data/reviews/{session_id}/review_turn_{N}.md`

**Process**:
1. Fetch last 10 turns from transcript
2. Extract patterns (tool usage, token consumption, themes)
3. Use Claude Sonnet to generate comprehensive analysis
4. Save review markdown file
5. Trigger mini-doc-agent to record review completion

**Environment Variables**:
- `ENABLE_TRACE_REVIEW`: Enable/disable (default: true)
- `REVIEW_INTERVAL`: Turns between reviews (default: 10)
- `REVIEW_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)

---

### 4. Stop Hook Integration

**File**: `.claude/hooks/stop.py`

**New Logic** (executed after each turn):

```python
# 1. Increment turn counter
counter = get_default_counter()
turn_count = counter.increment_turn(session_id, user_msg, assistant_msg)

# 2. Call mini-doc-agent (Haiku) for quick summary
call_mini_doc_agent(session_id, input_data)

# 3. Check if review needed (every 10 turns)
if counter.should_review(session_id, interval=10):
    # Trigger trace review agent (Sonnet)
    trace_review_agent(session_id, transcript_path, turn_count)
    counter.mark_reviewed(session_id)
```

---

## Data Flow

### Every Turn (1-10)

```
User Turn → Stop Hook
    ↓
Turn Counter: Increment (turn 1, 2, 3... 10)
    ↓
Mini-Doc Agent (Haiku): Quick 2-3 sentence summary
    ↓
Session Log: Append to session_log.md
```

### Every 10th Turn

```
User Turn → Stop Hook
    ↓
Turn Counter: Increment (turn 10)
    ↓
Mini-Doc Agent (Haiku): Quick summary
    ↓
Trace Review Agent (Sonnet): Triggered!
    ├─ Analyze last 10 turns
    ├─ Extract patterns & insights
    ├─ Generate review_turn_10.md
    └─ Call mini-doc-agent to record review
    ↓
Turn Counter: Mark reviewed (last_review_turn = 10)
```

---

## File Outputs

### Session Documentation
```
~/.claude/data/session_docs/{session_id}/
└── session_log.md                    # Continuous log of all turns
```

**Example Content**:
```markdown
# Session Documentation: abc123

## 2025-12-13 14:23:45
User asked about file cleanup. Assistant organized files into
archive directories and cleaned up the root directory.

---

## 2025-12-13 14:25:12
User requested turn-based review system. Assistant created
turn counter, mini-doc-agent, and trace review agent.

---
```

### Review Analysis
```
~/.claude/data/reviews/{session_id}/
├── review_turn_10.md
├── review_turn_20.md
└── review_turn_30.md
```

**Example Content**:
```markdown
# Session Review - Turn 10
**Session ID**: abc123
**Timestamp**: 2025-12-13T14:30:00
**Review Generated By**: Trace Review Agent

---

## Summary
This session focused on implementing observability and
documentation systems...

## Key Patterns
- Heavy use of file operations (Read, Write, Edit)
- Iterative development with testing
- Documentation-first approach

## Issues Detected
- None identified

## Recommendations
1. Consider adding error handling tests
2. Document environment variable requirements
```

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Turn-Based Review System
ENABLE_MINI_DOC=true                 # Enable mini-doc-agent
ENABLE_TRACE_REVIEW=true             # Enable trace review agent
REVIEW_INTERVAL=10                   # Turns between reviews
REVIEW_MODEL=claude-3-5-sonnet-20241022  # Model for reviews

# Required
ANTHROPIC_API_KEY=sk-ant-...         # For Haiku and Sonnet calls
```

---

## Integration with Existing Systems

### Works With

- ✅ **Langfuse**: Review data includes token counts from traces
- ✅ **Neo4j/Graphiti**: Can query knowledge graph for context
- ✅ **Observability Dashboard**: Can pull tool timing data
- ✅ **Session Logs**: Reads from existing transcript files

### Standalone

- ⚡ Runs independently of other hooks
- 💾 Uses separate SQLite database
- 📁 Outputs to dedicated directories

---

## Usage

### Automatic (Default)

System runs automatically after every turn when enabled:

```bash
# In .env
ENABLE_MINI_DOC=true
ENABLE_TRACE_REVIEW=true
```

### Manual Testing

Test turn counter:
```bash
uv run .claude/hooks/utils/turn_counter.py
```

Test mini-doc-agent:
```bash
echo '{"session_id":"test123","user_message":"test"}' | \
  uv run .claude/hooks/mini_doc_agent.py --session-id test123
```

Test trace review agent:
```bash
uv run .claude/hooks/trace_review_agent.py \
  --session-id test123 \
  --transcript-path ~/.claude/data/sessions/test123.jsonl \
  --turn-count 10
```

---

## Logs and Debugging

### Debug Logs

- **Turn Counter**: `~/.claude/logs/stop_send_turn_debug.log`
- **Mini-Doc Agent**: `~/.claude/logs/mini_doc_debug.log`
- **Trace Review**: `~/.claude/logs/trace_review_debug.log`

### Database Inspection

```bash
# View turn counts
sqlite3 ~/.claude/data/turn_counter.db \
  "SELECT * FROM session_turns ORDER BY last_turn_timestamp DESC LIMIT 10;"

# View turn history
sqlite3 ~/.claude/data/turn_counter.db \
  "SELECT * FROM turn_history WHERE session_id='abc123' ORDER BY turn_number DESC LIMIT 10;"
```

---

## Performance

### Per Turn Overhead

- **Turn Counter**: ~5ms (SQLite write)
- **Mini-Doc Agent**: ~500-1000ms (Haiku API call)
- **Total**: ~1 second per turn

### Review Overhead (Every 10 turns)

- **Trace Review Agent**: ~3-5 seconds (Sonnet API call + analysis)
- **Total**: ~4-6 seconds every 10th turn

### Cost

- **Mini-Doc Agent**: ~$0.0001 per turn (Haiku)
- **Trace Review**: ~$0.003 per review (Sonnet)
- **Average**: ~$0.0004 per turn

---

## Benefits

1. **Continuous Documentation**: Every turn summarized automatically
2. **Pattern Detection**: Identifies trends across 10-turn windows
3. **Issue Spotting**: Catches problems before they compound
4. **Session Insights**: Understand what you accomplished
5. **Cost-Effective**: Uses Haiku for frequent summaries, Sonnet for deep analysis

---

## Agent Documentation

- **Trace Review Agent**: `.claude/agents/TRACE_REVIEW_AGENT.md`
- **Mini-Doc Agent**: Lightweight, documented inline
- **Turn Counter**: Utility library with inline docs

---

## Status

✅ **Active** - Integrated into stop hook
📊 **Tracking**: Turn counts, session logs, periodic reviews
🤖 **Models**: Haiku (summaries) + Sonnet (analysis)

---

**Created**: 2025-12-13
**Author**: AI-Assisted Development
