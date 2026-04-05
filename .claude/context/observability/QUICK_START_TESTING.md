# Turn-Level Logging - Quick Start Testing Guide
**What Changed:** Langfuse now logs one trace per conversation turn (not per session)

---

## TL;DR

### What to Do
1. Have a conversation with 3+ turns
2. End session (`/exit`)
3. Run: `tail -50 ~/.claude/logs/stop_send_turn_debug.log`
4. Look for multiple "✓ Turn trace sent" messages
5. Check Langfuse dashboard for 3+ independent traces

### What Success Looks Like
```
[15:30:45.123456] === Sending turn trace for session: abc123...xyz ===
[15:30:45.127890] ✓ Langfuse enabled with credentials
[15:30:45.129123] Retrieved 4 events for turn
[15:30:45.234567] ✓ Turn trace sent and buffer cleared for next turn

[15:30:52.123456] === Sending turn trace for session: abc123...xyz ===
[15:30:52.127890] ✓ Langfuse enabled with credentials
[15:30:52.129123] Retrieved 4 events for turn
[15:30:52.234567] ✓ Turn trace sent and buffer cleared for next turn

[15:31:03.123456] === Sending turn trace for session: abc123...xyz ===
[15:30:45.127890] ✓ Langfuse enabled with credentials
[15:30:45.129123] Retrieved 2 events for turn
[15:31:03.234567] ✓ Turn trace sent and buffer cleared for next turn
```

**That's it! 3 traces sent, one per turn** ✅

---

## What Actually Changed

### stop.py
- Added: `send_turn_trace_to_langfuse()` function
- Does: Sends trace immediately after each turn ends
- Result: Each turn gets its own trace in Langfuse

### session_end.py
- Removed: All trace sending logic
- Added: `check_session_cleanup()` function
- Does: Just verifies buffer is empty (sanity check)
- Result: No longer sends at /exit

### Everything Else
- No changes to event buffering
- No changes to trace building
- No changes to configuration

---

## Test Conversation Script

### Copy & Paste This Conversation:

```
# Turn 1 - Simple question (no tools)
What is the capital of France?

# Turn 2 - List files (uses bash tool)
List all Python files in the current directory

# Turn 3 - Read a file (uses read tool)
What is your name?

# Then exit
/exit
```

---

## Check Results (3 Checks)

### Check 1: Debug Log (Immediate)
```bash
tail -80 ~/.claude/logs/stop_send_turn_debug.log
```

**Look for:**
- ✅ "=== Sending turn trace ===" appears 3+ times
- ✅ Each has "Retrieved X events" (X > 0)
- ✅ Each has "✓ Turn trace sent and buffer cleared"
- ❌ No "✗ Exception" messages

### Check 2: Session End Log
```bash
tail -5 ~/.claude/logs/session_end_debug.log
```

**Look for:**
- ✅ Shows session_end was called
- ✅ Shows "✓ Buffer is clean"

### Check 3: Langfuse Dashboard
Open your Langfuse project

**Look for:**
- ✅ 3+ traces (not 1)
- ✅ Each has unique name (like "consulting-co-search-python", "consulting-co-list-files")
- ✅ Each has 2-10 events (not 100+)
- ✅ Each has proper tags (model:sonnet, tool:*, status:success)

---

## Before vs After

### Old (Session-Level)
```
Langfuse → 1 Trace: "consulting-co-conversation"
           ├─ 50+ events (all turns mixed)
           └─ Hard to parse
```

### New (Turn-Level) ✨
```
Langfuse → Trace 1: "consulting-co-capital-france"
           ├─ 2 events (clean & simple)

           → Trace 2: "consulting-co-list-files"
           ├─ 4 events (with bash tool)

           → Trace 3: "consulting-co-name"
           └─ 2 events (just response)
```

---

## Common Results

### ✅ Perfect Result
```
[15:30:45] === Sending turn trace for session: abc123...xyz ===
[15:30:45] ✓ Langfuse enabled with credentials
[15:30:45] Retrieved 2 events for turn
[15:30:45] ✓ Turn trace sent and buffer cleared for next turn

[15:30:52] === Sending turn trace for session: abc123...xyz ===
[15:30:52] ✓ Langfuse enabled with credentials
[15:30:52] Retrieved 4 events for turn
[15:30:52] ✓ Turn trace sent and buffer cleared for next turn

[15:31:03] === Sending turn trace for session: abc123...xyz ===
[15:31:03] ✓ Langfuse enabled with credentials
[15:31:03] Retrieved 4 events for turn
[15:31:03] ✓ Turn trace sent and buffer cleared for next turn
```
→ **You're done! 3 traces sent successfully** ✅

### ⚠️ All Turns Show 0 Events
```
[15:30:45] Retrieved 0 events for turn
[15:30:52] Retrieved 0 events for turn
[15:31:03] Retrieved 0 events for turn
```
→ **Issue:** Event buffering hooks not working
→ **Check:** tail -20 ~/.claude/logs/*_buffer_called.txt
→ **Should see:** Marker files updated recently

### ⚠️ Only First Turn Shows
```
[15:30:45] === Sending turn trace for session: abc123...xyz ===
[15:30:45] Retrieved 4 events for turn
[15:30:45] ✓ Turn trace sent and buffer cleared for next turn

(then silence - no more turn traces)
```
→ **Issue:** Only ran 1 turn, then /exit immediately
→ **Fix:** Run conversation with 3+ turns before /exit

### ❌ Exception Errors
```
[15:30:45] ✗ Exception sending turn trace: ImportError: No module named 'langfuse'
```
→ **Issue:** Module not installed
→ **Fix:** pip install langfuse

---

## Debugging (If Needed)

### Full error traceback:
```bash
grep -A 30 "Exception sending turn trace" ~/.claude/logs/stop_send_turn_debug.log
```

### Check event buffering is working:
```bash
tail -10 ~/.claude/logs/user_prompt_buffer_called.txt
tail -10 ~/.claude/logs/stop_buffer_called.txt
```

### Check credentials loaded:
```bash
grep "Langfuse enabled" ~/.claude/logs/stop_send_turn_debug.log
```

### Count how many turns sent:
```bash
grep -c "Turn trace sent" ~/.claude/logs/stop_send_turn_debug.log
```

---

## Success Criteria

You'll know it worked when:

1. ✅ **Stop debug log** shows multiple "Sending turn trace" sections
2. ✅ **Each turn** shows "Retrieved X events" (X > 0)
3. ✅ **Each turn** shows "✓ Turn trace sent and buffer cleared"
4. ✅ **Session end log** shows "✓ Buffer is clean"
5. ✅ **Langfuse dashboard** shows 3+ independent traces
6. ✅ **Trace names** are descriptive (not "consulting-co-conversation")
7. ✅ **Event counts** are 2-10 per trace (not 100+)

---

## Files Created

For reference documentation:
- `PHASE_6_TURN_LEVEL_LOGGING_ARCHITECTURE.md` - Full architecture guide
- `TURN_LEVEL_TESTING_CHECKLIST.md` - Detailed testing steps
- `PHASE_6_COMPLETION_SUMMARY.md` - Complete implementation summary
- `QUICK_START_TESTING.md` - This file (quick reference)

---

**Status:** Ready to test! Run your next multi-turn conversation and check the logs. 🚀

*Last Updated: 2025-11-16 15:50 UTC*
