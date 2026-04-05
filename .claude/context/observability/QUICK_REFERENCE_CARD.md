# Langfuse Integration - Quick Reference Card
**Keep this handy for the next session!**

---

## What to Do Now

1. **Run a normal conversation** (multiple turns, use some tools)
2. **End the session** (`/exit` or close CLI)
3. **Check the logs** (see below)
4. **Verify Langfuse** (see below)

---

## Quick Log Check (After Session Ends)

### Command to View Logs
```bash
tail -30 ~/.claude/logs/session_end_debug.log
```

### What You Should See ✅
```
=== session_end.py send_trace_to_langfuse called for session: abc123... ===
Sessions in buffer: 2 total
  - abc123... (8 events)    ← Your session here
Attempt 1: Retrieved 8 events
✓ Trace sent and buffer cleared
```

### What Means Success ✅
- [ ] "Retrieved X events" (X > 0, not 0)
- [ ] "✓ Trace sent and buffer cleared"
- [ ] No error messages

### What Means Problem ❌
- [ ] "Retrieved 0 events" on all 3 attempts
- [ ] Session IDs in buffer don't match log
- [ ] "Exception:" or "Error:" in log

---

## Quick Langfuse Check

### Where to Check
- Langfuse Dashboard → Traces
- Or check if LANGFUSE_EXPORT_PATH is set:
  ```bash
  ls -l $(dirname $LANGFUSE_EXPORT_PATH)
  ```

### What You Should See ✅
**Trace Name:** NOT "consulting-co-conversation" but something like:
- `consulting-co-search-obsidian-tools2`
- `consulting-co-analyze-code-bash-read`
- `consulting-co-list-files-tools3`

**Tags:** Should include:
- `model:sonnet` (or haiku/opus)
- `tool:bash`, `tool:read` (whatever tools used)
- `status:success` (or error if failed)
- `complexity:medium` (or low/high)

**Events:** Should show:
- 10-100+ events (NOT just 3)
- Tool observations with latencies
- User messages and prompts

### If You See Old Behavior ❌
- Trace name: "consulting-co-conversation" (generic)
- Tags: only ["claude-code", "consulting-co", "conversation"]
- Events: only 3 (SessionStart, UserPromptSubmit, Stop)

---

## File Locations (for reference)

```
Logs Directory:
  ~/.claude/logs/

Main Files:
  session_end_debug.log           ← Primary debug output
  session_end_called.txt          ← When hook fires
  events.db                       ← SQLite database
  *_buffer_called.txt             ← When hooks add events

Hook Scripts:
  ~/.claude/hooks/session_end.py  ← MODIFIED in Phase 5C
  ~/.claude/hooks/utils/event_buffer.py
  ~/.claude/hooks/utils/log_to_langfuse.py
```

---

## Interpretation Cheat Sheet

| Log Entry | Meaning | Status |
|-----------|---------|--------|
| `Retrieved 0 events` then `Retrieved 8 events` | Race condition but recovered | ✅ Good |
| `Retrieved 0 events` (all 3 times) | Session ID mismatch or timing issue | ❌ Problem |
| `Attempt 1: Retrieved X events` (X > 0) | Immediate success | ✅ Good |
| `Sessions in buffer: 2 total` + `abc123...` | Your session in buffer | ✅ Good |
| `✓ Trace sent and buffer cleared` | Success! | ✅ Good |
| `PUBLIC_KEY set: False` | Credentials missing | ❌ Problem |
| `ENABLE_LANGFUSE=False` | Feature disabled | ⚠️ Disabled |

---

## Expected Session Flow

```
15:30:00 - User starts conversation
15:30:05 - user_prompt_submit hook fires → ✓ event added
15:30:10 - Claude responds
15:30:15 - stop hook fires → ✓ event added
15:30:20 - User asks next question
15:30:25 - user_prompt_submit hook fires → ✓ event added
15:30:30 - Tools used (pre_tool_use, post_tool_use hooks)
          → ✓ events added
15:30:45 - stop hook fires → ✓ event added
15:30:50 - User hits /exit or closes CLI
15:30:51 - session_end.py called
          → Retrieves all buffered events
          → Sends to Langfuse
          → Creates trace with proper name & tags
```

---

## Troubleshooting Quick Guide

**No events retrieved?**
→ Check if session_id in log matches sessions in buffer list

**No trace in Langfuse?**
→ Check "✓ Trace sent" message in log

**Langfuse trace still generic?**
→ Check Langfuse API credentials in .env file

**Less than 10 events?**
→ Normal for short sessions, should increase with longer conversations

**Still only 3 events?**
→ Phase 5C didn't work, check log for error messages

---

## Copy-Paste Commands

### Check Debug Log
```bash
tail -50 ~/.claude/logs/session_end_debug.log
```

### Check When Hook Was Called
```bash
tail ~/.claude/logs/session_end_called.txt
```

### Check Event Buffer Status
```bash
ls -lah ~/.claude/logs/events.db
```

### Verify All Marker Files Updated
```bash
ls -l ~/.claude/logs/*_buffer_called.txt | tail -3
```

### Print Last 3 Entries from Debug Log
```bash
tail -3 ~/.claude/logs/session_end_debug.log | grep "Retrieved\|Trace sent\|No events"
```

---

## What Changed in Phase 5C

**Only one file was modified:**
- `~/.claude/hooks/session_end.py`

**Changes:**
1. Added session_id logging to marker file (line 74)
2. Added session_id to debug logs (line 79)
3. Added buffer diagnostics (lines 106-114):
   - List all sessions in buffer
   - Show event count for each
   - Helps identify session_id mismatch

**What DIDN'T change:**
- Event buffering (still working)
- SQLite database (still working)
- Retry mechanism (already there from Phase 5B)
- Langfuse integration (ready to test)

---

## Success Criteria

✅ You'll know it worked when:
1. Debug log shows "Retrieved X events" (X > 0)
2. Debug log shows "✓ Trace sent and buffer cleared"
3. Langfuse trace has descriptive name
4. Langfuse trace has meaningful tags
5. Langfuse trace shows 10-100+ events

❌ You'll know there's an issue when:
1. Debug log shows "Retrieved 0 events" even after retries
2. No trace appears in Langfuse
3. Trace name is still "consulting-co-conversation"
4. Trace only has 3 events

---

**TL;DR:** Run next conversation, end session, check log for "Retrieved X events" + "✓ Trace sent", verify in Langfuse that trace has good name and tags.

*Last Updated: 2025-11-16 15:18 UTC*
