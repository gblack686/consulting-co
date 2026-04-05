# Turn-Level Logging - Testing Checklist
**Phase 6 Verification**

---

## Pre-Test Setup

Before running a test conversation, verify:

- [ ] `ENABLE_LANGFUSE=true` in .env file
- [ ] `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set
- [ ] Can access Langfuse dashboard
- [ ] `.claude/logs` directory exists
- [ ] `stop.py` file modified (contains `send_turn_trace_to_langfuse` function)

---

## Test Conversation (3+ Turns Recommended)

**Goal:** Run a multi-turn conversation to test turn-level logging

### Turn 1: Simple Query (No Tools)
```
You:    "what is the capital of France?"
Claude: [responds without tools]
```

**Expected:** One trace sent after this turn

### Turn 2: Tool Usage
```
You:    "list files in the current directory"
Claude: [calls bash/ls command]
        [shows results]
```

**Expected:** Second trace sent with bash tool tagged

### Turn 3: Multiple Tools (Optional)
```
You:    "create and run a test script"
Claude: [writes file, runs bash]
```

**Expected:** Third trace with multiple tools

### Exit Session
```
/exit
```

---

## Verification Steps

### IMMEDIATELY After Session Ends

#### Step 1: Check Stop Debug Log
```bash
tail -50 ~/.claude/logs/stop_send_turn_debug.log
```

**What you should see:**

For Turn 1:
```
[2025-11-16T15:30:45.123456] === Sending turn trace for session: abc123...xyz ===
[2025-11-16T15:30:45.124567] ✓ Langfuse enabled with credentials
[2025-11-16T15:30:45.127890] ✓ Imported event_buffer
[2025-11-16T15:30:45.129123] Retrieved 2 events for turn     ← UserPromptSubmit, Stop
[2025-11-16T15:30:45.145678] ✓ Imported log_to_langfuse
[2025-11-16T15:30:45.145789] Extracted metadata: tools=[]  ← No tools used
[2025-11-16T15:30:45.234567] Sending turn trace to Langfuse: consulting-co/consulting-co (ts:153045)
[2025-11-16T15:30:45.567890] ✓ Turn trace sent and buffer cleared for next turn
```

For Turn 2:
```
[2025-11-16T15:30:52.123456] === Sending turn trace for session: abc123...xyz ===
[2025-11-16T15:30:52.127890] ✓ Langfuse enabled with credentials
[2025-11-16T15:30:52.129123] Retrieved 4 events for turn     ← UserPromptSubmit, PreToolUse, PostToolUse, Stop
[2025-11-16T15:30:52.145678] ✓ Imported log_to_langfuse
[2025-11-16T15:30:52.145789] Extracted metadata: tools=['bash']  ← Tool used!
[2025-11-16T15:30:52.234567] Sending turn trace to Langfuse: consulting-co/consulting-co (ts:153052)
[2025-11-16T15:30:52.567890] ✓ Turn trace sent and buffer cleared for next turn
```

**Success Indicators:**
- [ ] Multiple "=== Sending turn trace ===" sections (one per turn)
- [ ] Each turn shows "Retrieved X events" (X should be 2-6)
- [ ] Each turn shows "✓ Turn trace sent and buffer cleared"
- [ ] No "✗ Exception" or "Error" messages

#### Step 2: Check Session End Log
```bash
tail -10 ~/.claude/logs/session_end_debug.log
```

**What you should see:**
```
[2025-11-16T15:31:10.123456] === session_end.py called for session: abc123...xyz ===
[2025-11-16T15:31:10.124567] (Note: Turn-level logging now sends traces via stop.py, not session_end.py)
[2025-11-16T15:31:10.234567] ✓ Buffer is clean (as expected for turn-level logging)
```

**Success Indicators:**
- [ ] Shows session_end was called
- [ ] Shows "✓ Buffer is clean" (expected behavior)
- [ ] No warnings about "events still in buffer"

#### Step 3: Check Langfuse Dashboard
Go to your Langfuse project dashboard

**What you should see:**

3 traces (one per turn):

**Trace 1:**
- [ ] Name: Something like "consulting-co-capital-france" (from Turn 1 prompt)
- [ ] Tags: Should include "model:sonnet" (or haiku/opus), "status:success"
- [ ] Events: 2 total (UserPromptSubmit, Stop)
- [ ] No tool observations (no tools used)

**Trace 2:**
- [ ] Name: Something like "consulting-co-list-files" (from Turn 2 prompt)
- [ ] Tags: Should include "model:sonnet", "tool:bash", "status:success"
- [ ] Events: 4 total (UserPromptSubmit, PreToolUse, PostToolUse, Stop)
- [ ] Has tool observation for bash call

**Trace 3 (if applicable):**
- [ ] Name: Something like "consulting-co-create-run-test" (from Turn 3 prompt)
- [ ] Tags: Should include "model:sonnet", "tool:...", "status:success"
- [ ] Events: 4-6 total
- [ ] Has tool observations

---

## Comparison: Old vs New

### OLD (Session-Level) ❌
```
Langfuse shows:
└─ Trace: "consulting-co-conversation"  (generic, same for all sessions)
   ├─ Events: 100+ (from all 3 turns mixed together)
   ├─ Tags: [claude-code, consulting-co, conversation]
   └─ Hard to see what happened in each turn
```

### NEW (Turn-Level) ✅
```
Langfuse shows:
├─ Trace: "consulting-co-capital-france"
│  ├─ Events: 2
│  ├─ Tags: [model:sonnet, status:success, complexity:low]
│  └─ Clear: just answered a question, no tools
│
├─ Trace: "consulting-co-list-files"
│  ├─ Events: 4
│  ├─ Tags: [model:sonnet, tool:bash, status:success]
│  └─ Clear: ran a bash command to list files
│
└─ Trace: "consulting-co-create-run-test"
   ├─ Events: 4
   ├─ Tags: [model:sonnet, tool:write, tool:bash, status:success]
   └─ Clear: created and ran a test script
```

---

## Troubleshooting

### Issue: "Retrieved 0 events for turn"

**Cause:** Events not being buffered correctly

**Check:**
```bash
tail -20 ~/.claude/logs/user_prompt_buffer_called.txt
tail -20 ~/.claude/logs/stop_buffer_called.txt
```

**Fix:** Verify event buffering hooks are working
- Are marker files being created?
- Are timestamps recent?

### Issue: "Retrieved 2 events for turn" but expected 4+ (for a turn with tools)

**Cause:** Tool use hooks not firing

**Check:**
```bash
tail -20 ~/.claude/logs/*_buffer_called.txt
```

**Fix:** Verify pre_tool_use.py and post_tool_use.py are working

### Issue: Only one "Sending turn trace" message, expected 3

**Cause:** Session ended before all turns completed

**Fix:** Verify you actually typed 3+ turns (not just 1 turn then /exit)

### Issue: Traces not appearing in Langfuse

**Cause:** Credentials invalid or network issue

**Check:**
```bash
grep "✓ Turn trace sent" ~/.claude/logs/stop_send_turn_debug.log
```

If this appears, it means stop.py thought it sent successfully. Check:
- [ ] Langfuse credentials are correct
- [ ] Network connectivity to Langfuse API
- [ ] Check Langfuse status page for outages

### Issue: Trace name is still "consulting-co-conversation"

**Cause:** Old version of log_to_langfuse.py is running

**Fix:**
- [ ] Restart Claude Code (clear any cached imports)
- [ ] Verify ~/.claude/hooks/utils/log_to_langfuse.py has generate_trace_name() function

### Issue: "✗ Exception sending turn trace"

**Action:** Read the full error in stop_send_turn_debug.log
- [ ] Import error? Missing module?
- [ ] Permission error? Write to logs?
- [ ] API error? Langfuse connection?

**Get full traceback:**
```bash
grep -A 20 "Exception sending turn trace" ~/.claude/logs/stop_send_turn_debug.log
```

---

## Success Criteria

### ✅ Full Success
1. Multiple "Sending turn trace" entries in stop_send_turn_debug.log
2. Each turn shows "Retrieved X events" (X > 0)
3. Each turn shows "✓ Turn trace sent and buffer cleared"
4. Session end shows "✓ Buffer is clean"
5. Langfuse dashboard shows multiple traces (one per turn)
6. Each trace has a unique, descriptive name
7. Each trace has proper tags (model, tools, status)
8. Each trace has 2-10 events (not 100+)

### ⚠️ Partial Success (acceptable for debugging)
- Traces appear but with old naming ("consulting-co-conversation")
  → Still turn-level, but naming not updated yet
- Only first turn's trace appears
  → Subsequent turns buffering correctly, but send logic not working
- Events show as 0 for all turns
  → Buffering not working, but send logic is trying

---

## After Testing

### If Successful ✅
- [ ] Document results in PHASE_6_TESTING_RESULTS.md
- [ ] Note any issues that came up and how you fixed them
- [ ] Consider running a longer multi-turn session to stress test

### If Issues Found ❌
- [ ] Check logs as detailed above
- [ ] Document the specific error message
- [ ] Try to pinpoint which component failed:
  - User prompt buffering? (check user_prompt_buffer_called.txt)
  - Tool buffering? (check pre/post tool use markers)
  - Langfuse send? (check stop_send_turn_debug.log)
  - Session cleanup? (check session_end_debug.log)

---

## Quick Command Reference

Check all logs at once:
```bash
echo "=== STOP SEND (Turn-Level) ===" && \
tail -20 ~/.claude/logs/stop_send_turn_debug.log && \
echo -e "\n=== SESSION END ===" && \
tail -10 ~/.claude/logs/session_end_debug.log && \
echo -e "\n=== BUFFER MARKERS ===" && \
tail -5 ~/.claude/logs/user_prompt_buffer_called.txt && \
tail -5 ~/.claude/logs/stop_buffer_called.txt
```

Check for errors:
```bash
grep -i "error\|exception\|✗" ~/.claude/logs/stop_send_turn_debug.log
grep -i "error\|exception\|✗" ~/.claude/logs/session_end_debug.log
```

Count traces sent:
```bash
grep -c "Sending turn trace" ~/.claude/logs/stop_send_turn_debug.log
```

---

## Expected Timeline

```
15:30:45 - Turn 1 starts
15:30:50 - Turn 1 ends → stop.py sends trace → buffer cleared
15:30:52 - Turn 2 starts
15:30:59 - Turn 2 ends → stop.py sends trace → buffer cleared
15:31:01 - Turn 3 starts
15:31:08 - Turn 3 ends → stop.py sends trace → buffer cleared
15:31:10 - /exit typed
15:31:11 - session_end.py fires → checks buffer is clean
```

**All events in stop_send_turn_debug.log should have timestamps within this range**

---

**Test Date:** ________________
**Result:** [ ] Success  [ ] Partial  [ ] Failed
**Notes:** ________________________________________________

*Last Updated: 2025-11-16 15:45 UTC*
