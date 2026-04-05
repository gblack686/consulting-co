# Turn-Based Review System - Quick Start 🚀

Get started with automatic session reviews in 2 minutes.

---

## TL;DR

After each turn:
- 📝 **Mini-Doc Agent** (Haiku) writes a quick summary
- 🔄 **Turn Counter** increments in SQLite

Every 10 turns:
- 🔍 **Trace Review Agent** (Sonnet) analyzes the session
- 📊 Generates comprehensive review with insights

---

## Setup (One-Time)

### 1. Environment Variables

Add to `.env`:

```bash
ENABLE_MINI_DOC=true
ENABLE_TRACE_REVIEW=true
REVIEW_INTERVAL=10
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Verify Installation

```bash
cd .claude/tests
uv run test_turn_review_system.py
```

Expected: `🎉 All tests passed!`

---

## Usage

### It Just Works™

The system runs automatically. No action needed!

Every turn:
```
Your conversation → Stop hook → Turn counter → Mini-doc summary
```

Every 10th turn:
```
Turn 10 reached → Trace review triggered → Analysis generated
```

---

## View Your Data

### Session Log (All Turns)

```bash
# View your session log
cat ~/.claude/data/session_docs/YOUR_SESSION_ID/session_log.md
```

### Reviews (Every 10 Turns)

```bash
# View reviews
ls ~/.claude/data/reviews/YOUR_SESSION_ID/

# Read a specific review
cat ~/.claude/data/reviews/YOUR_SESSION_ID/review_turn_10.md
```

### Turn Statistics

```bash
# Query the database
sqlite3 ~/.claude/data/turn_counter.db "
  SELECT session_id, turn_count, last_review_turn
  FROM session_turns
  ORDER BY last_turn_timestamp DESC
  LIMIT 5;
"
```

---

## Debug

### Check Logs

```bash
# Mini-doc agent log
tail -f ~/.claude/logs/mini_doc_debug.log

# Trace review agent log
tail -f ~/.claude/logs/trace_review_debug.log

# Turn counter log
tail -f ~/.claude/logs/stop_send_turn_debug.log
```

### Verify Turn Count

```bash
sqlite3 ~/.claude/data/turn_counter.db "
  SELECT * FROM session_turns WHERE session_id='YOUR_SESSION_ID';
"
```

---

## Configuration

### Change Review Interval

```bash
# Review every 5 turns instead of 10
echo "REVIEW_INTERVAL=5" >> .env
```

### Disable Features

```bash
# Disable mini-doc summaries
echo "ENABLE_MINI_DOC=false" >> .env

# Disable trace reviews
echo "ENABLE_TRACE_REVIEW=false" >> .env
```

---

## What Gets Created

```
~/.claude/data/
├── turn_counter.db              # SQLite database
├── session_docs/
│   └── {session_id}/
│       └── session_log.md       # All turn summaries
└── reviews/
    └── {session_id}/
        ├── review_turn_10.md    # First review
        ├── review_turn_20.md    # Second review
        └── review_turn_30.md    # Third review
```

---

## Example Output

### Mini-Doc Summary (Every Turn)

```markdown
## 2025-12-13 14:23:45
User requested file cleanup. Assistant organized files into
archive directories and removed temporary files. Tools: Bash,
Read, Write.
```

### Trace Review (Every 10 Turns)

```markdown
# Session Review - Turn 10

## Summary
Session focused on implementing observability systems including
turn tracking, documentation agents, and review automation.

## Key Patterns
- Iterative development with testing
- Documentation-first approach
- Tool-heavy workflow (Read, Write, Edit, Bash)

## Recommendations
1. Continue systematic testing approach
2. Add error handling for edge cases
```

---

## Performance

| What | When | Speed | Cost |
|------|------|-------|------|
| Turn Counter | Every turn | 5ms | Free |
| Mini-Doc | Every turn | 1s | $0.0001 |
| Trace Review | Every 10th | 4s | $0.003 |

Average cost: **~$0.0004 per turn**

---

## Troubleshooting

### No summaries appearing?

Check mini-doc is enabled:
```bash
grep ENABLE_MINI_DOC .env
# Should show: ENABLE_MINI_DOC=true
```

### No reviews at turn 10?

Check review is enabled and logs:
```bash
grep ENABLE_TRACE_REVIEW .env
tail ~/.claude/logs/trace_review_debug.log
```

### Database errors?

Reinitialize database:
```bash
rm ~/.claude/data/turn_counter.db
# System will recreate on next turn
```

---

## Full Documentation

- **Complete Guide**: `.claude/context/observability/TURN_BASED_REVIEW_SYSTEM.md`
- **Implementation Summary**: `.claude/context/observability/TURN_REVIEW_SYSTEM_SUMMARY.md`
- **Agent Spec**: `.claude/agents/TRACE_REVIEW_AGENT.md`

---

## Support

Check debug logs first:
```bash
tail ~/.claude/logs/*.log
```

Test the system:
```bash
cd .claude/tests && uv run test_turn_review_system.py
```

---

**Status**: ✅ Active and Running
**Last Updated**: 2025-12-13
