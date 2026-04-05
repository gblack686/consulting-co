# Langfuse Integration - Diagnostic Log Guide
**Quick Reference for Interpreting Debug Output**

---

## Where to Check Logs

### Main Debug Log
```
~/.claude/logs/session_end_debug.log
```

### Marker Files (for hook confirmation)
```
~/.claude/logs/session_end_called.txt          # When session_end.py is called
~/.claude/logs/user_prompt_buffer_called.txt   # When user_prompt hook fires
~/.claude/logs/stop_buffer_called.txt          # When stop hook fires
~/.claude/logs/subagent_stop_buffer_called.txt # When subagent_stop hook fires
```

### Events Database
```
~/.claude/logs/events.db # SQLite database with buffered events
```

---

## Expected Log Output (Next Session)

### ✅ Success Scenario

```
[2025-11-16T15:30:45.123456] === session_end.py send_trace_to_langfuse called for session: abc123def-45f6-789g-hij0-123456789012 ===
[2025-11-16T15:30:45.124567] ENABLE_LANGFUSE=True
[2025-11-16T15:30:45.124567] PUBLIC_KEY set: True, SECRET_KEY set: True
[2025-11-16T15:30:45.127890] ✓ Imported event_buffer
[2025-11-16T15:30:45.129123] Getting events for session: abc123def-45f6-789g-hij0-123456789012
[2025-11-16T15:30:45.130234] Sessions in buffer: 3 total
[2025-11-16T15:30:45.130345]   - abc123de... (8 events)
[2025-11-16T15:30:45.130456]   - xyz789ab... (5 events)
[2025-11-16T15:30:45.130567]   - old12345... (2 events)
[2025-11-16T15:30:45.131234] Attempt 1: Retrieved 8 events
[2025-11-16T15:30:45.145678] ✓ Imported log_to_langfuse
[2025-11-16T15:30:45.145789] Extracted metadata: tools=['bash', 'read']
[2025-11-16T15:30:45.145890] Sending trace to Langfuse: consulting-co/consulting-co
[2025-11-16T15:30:45.234567] ✓ Trace sent and buffer cleared
```

**Key Indicators of Success:**
- ✅ Session ID matches the session that was running
- ✅ "Retrieved X events" (X > 0)
- ✅ "Attempt 1" shows immediate success
- ✅ "Trace sent and buffer cleared"

---

### ⚠️ Race Condition (Retry Mechanism) Scenario

```
[2025-11-16T15:30:45.123456] === session_end.py send_trace_to_langfuse called for session: abc123def-45f6-789g-hij0-123456789012 ===
[2025-11-16T15:30:45.124567] ENABLE_LANGFUSE=True
[2025-11-16T15:30:45.124567] PUBLIC_KEY set: True, SECRET_KEY set: True
[2025-11-16T15:30:45.127890] ✓ Imported event_buffer
[2025-11-16T15:30:45.129123] Getting events for session: abc123def-45f6-789g-hij0-123456789012
[2025-11-16T15:30:45.130234] Sessions in buffer: 1 total
[2025-11-16T15:30:45.130345]   - abc123de... (0 events)
[2025-11-16T15:30:45.131234] Attempt 1: Retrieved 0 events
[2025-11-16T15:30:45.131345] Waiting 0.5s for events to be written...
[2025-11-16T15:30:45.631567] Attempt 2: Retrieved 0 events
[2025-11-16T15:30:45.631678] Waiting 0.5s for events to be written...
[2025-11-16T15:30:46.131890] Attempt 3: Retrieved 0 events
[2025-11-16T15:30:46.131901] No events to send
```

**Interpretation:**
- Session ID is correct (it's in the buffer list)
- But events show as 0
- Retry mechanism is working (shows Attempt 1, 2, 3)
- Even after waiting, no events found
- **Issue:** Events were written to buffer AFTER session_end hook fired
- **Root Cause:** Race condition still present despite retries

---

### ❌ Session ID Mismatch Scenario

```
[2025-11-16T15:30:45.123456] === session_end.py send_trace_to_langfuse called for session: OLD_SESSION_ID_12345 ===
[2025-11-16T15:30:45.124567] ENABLE_LANGFUSE=True
[2025-11-16T15:30:45.124567] PUBLIC_KEY set: True, SECRET_KEY set: True
[2025-11-16T15:30:45.127890] ✓ Imported event_buffer
[2025-11-16T15:30:45.129123] Getting events for session: OLD_SESSION_ID_12345
[2025-11-16T15:30:45.130234] Sessions in buffer: 2 total
[2025-11-16T15:30:45.130345]   - abc123de... (8 events)
[2025-11-16T15:30:45.130456]   - xyz789ab... (5 events)
[2025-11-16T15:30:45.131234] Attempt 1: Retrieved 0 events
[2025-11-16T15:30:45.131345] Waiting 0.5s for events to be written...
[2025-11-16T15:30:45.631567] Attempt 2: Retrieved 0 events
```

**Interpretation:**
- Session_end looking for: `OLD_SESSION_ID_12345`
- Sessions in buffer: `abc123de...`, `xyz789ab...`
- **Problem:** Wrong session_id being passed to session_end.py
- **Root Cause:** Claude Code not providing correct session_id to hook

---

### ❌ Langfuse Credentials Missing Scenario

```
[2025-11-16T15:30:45.123456] === session_end.py send_trace_to_langfuse called for session: abc123def-45f6-789g-hij0-123456789012 ===
[2025-11-16T15:30:45.124567] ENABLE_LANGFUSE=True
[2025-11-16T15:30:45.124567] PUBLIC_KEY set: False, SECRET_KEY set: False
[2025-11-16T15:30:45.124578] Missing Langfuse credentials
```

**Interpretation:**
- Langfuse is enabled (`ENABLE_LANGFUSE=True`)
- But credentials not loaded (`PUBLIC_KEY set: False`)
- **Fix:** Check `.env` file has LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY

---

## What to Check in Each Scenario

### For Session ID Mismatch
```bash
# Check what session_id Claude Code is passing
grep "session_id:" ~/.claude/logs/session_end_called.txt | tail -5

# Check what sessions have events
# (Would need to query events.db with sqlite3 or use event_buffer CLI)
```

### For Race Condition
```bash
# Check timing of events vs session_end call
ls -l ~/.claude/logs/session_end_called.txt
ls -l ~/.claude/logs/events.db

# Check if events were added AFTER session_end was called
grep "✓ event added" ~/.claude/logs/*_buffer_called.txt | tail -3
```

### For Langfuse Send Failure
```bash
# Check if error is logged after "Attempt 3"
tail -30 ~/.claude/logs/session_end_debug.log | grep -A5 "Attempt 3"

# Look for error message
tail -50 ~/.claude/logs/session_end_debug.log | grep "Exception\|Error\|Failed"
```

---

## Interpretation Guide

| Log Pattern | Meaning | Status | Action |
|---|---|---|---|
| `Sessions in buffer: N total` | N sessions have buffered events | INFO | Continue |
| `Attempt 1: Retrieved X events` (X > 0) | Events found immediately | ✅ SUCCESS | Continue to Langfuse send |
| `Attempt 1: Retrieved 0 events` → `Attempt 2/3` | Events found on retry | ⚠️ RACE CONDITION | Works but slow |
| `Attempt 3: Retrieved 0 events` | No events found after all retries | ❌ PROBLEM | Session ID mismatch or timing issue |
| `PUBLIC_KEY set: False` | Credentials not loaded | ❌ PROBLEM | Check .env file |
| `ENABLE_LANGFUSE=False` | Feature disabled | ⚠️ DISABLED | Enable in settings |
| `✓ Trace sent and buffer cleared` | Success! | ✅ SUCCESS | Check Langfuse dashboard |
| `Exception: ...` | Hook crashed | ❌ CRASH | Check error message, file may be corrupted |

---

## Timeline Analysis

### How to Check Event Timing

```bash
# Events added by hooks
grep "✓ event added" ~/.claude/logs/*_buffer_called.txt

# Session end called
grep "session_id:" ~/.claude/logs/session_end_called.txt

# Compare timestamps
# If session_end is called BEFORE events are added, that's the issue
```

Example interpretation:
```
15:30:44.100000 - session_end called (session_end_called.txt)
15:30:44.500000 - ✓ event added (user_prompt_buffer_called.txt)  ← Events AFTER session_end!
```
**Issue:** session_end hook fires before all events are buffered (race condition)

---

## Troubleshooting Decision Tree

```
START: Check session_end_debug.log

├─ Does file exist?
│  ├─ NO → Hooks not configured or file permissions issue
│  └─ YES → Continue
│
├─ Last timestamp > 15 min ago?
│  ├─ YES → No recent session ends, still in active session
│  └─ NO → Recent session, analyze below
│
├─ Does it show "Retrieved X events" (X > 0)?
│  ├─ YES ✅ → Events found! Check Langfuse for trace
│  └─ NO → Continue
│
├─ Does it show "Attempt 1", "Attempt 2", "Attempt 3"?
│  ├─ NO → Retry mechanism not running, old code? Check file timestamp
│  └─ YES → Retry ran but still got 0 events
│
├─ Do sessions in buffer match session_id in log?
│  ├─ NO → Session ID mismatch (Claude Code not passing correct ID)
│  └─ YES → Race condition (events added after session_end fired)
│
└─ Check marker files for timing mismatch
   (session_end_called vs *_buffer_called timestamps)
```

---

## Quick Checklist for Next Session

After running a conversation and ending the session:

- [ ] Check timestamp in `session_end_debug.log` (updated recently?)
- [ ] Look for "Sessions in buffer: X total"
- [ ] Note the session_ids shown in buffer
- [ ] Look for "Attempt 1: Retrieved X events"
- [ ] Check if X > 0 (events found)
- [ ] Look for "✓ Trace sent and buffer cleared" (success!)
- [ ] Check `~/.langfuse/` or Langfuse dashboard for new trace
- [ ] Verify trace name is descriptive (not "consulting-co-conversation")
- [ ] Verify tags include model type (model:sonnet/haiku/opus)
- [ ] Verify all events visible (10-100+ not just 3)

---

**Last Updated:** 2025-11-16 15:18 UTC
