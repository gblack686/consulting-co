# Testing Tool Extraction Integration

**Date:** November 16, 2025
**Status:** Ready to Test
**Plan:** Run a simple bash command and verify tool extraction works end-to-end

---

## Quick Test Steps

### Step 1: Clear Old Debug Logs
```bash
# Remove old logs to see fresh output
rm -f ~/.claude/logs/pre_tool_debug.log
rm -f ~/.claude/logs/post_tool_debug.log
rm -f ~/.claude/logs/extraction_debug.log
```

### Step 2: Run a Simple Test Command
```bash
# In Claude Code, run a simple command like:
# "List my home directory"
# or "Check the current time"
```

This will trigger:
1. UserPromptSubmit hook
2. Claude generates a bash call
3. PreToolUse hook fires (writes debug log)
4. Bash executes
5. PostToolUse hook fires (writes debug log)
6. Stop hook fires (calls extract_metadata_from_events with verbose logging)

### Step 3: Check Pre-Tool Debug Log
```bash
tail -200 ~/.claude/logs/pre_tool_debug.log
```

**Expected output:**
```
============================================================
[2025-11-16T20:10:45.123456] PreToolUse Hook Fired
============================================================
Session ID: abc123def456...
Input data keys: ['tool_name', 'tool_input', 'session_id', ...]
Full input_data:
{
  "tool_name": "Bash",    ← CRITICAL: This should NOT be 'unknown'
  "tool_input": {
    "command": "ls ~"
  },
  ...
}
============================================================
[EXTRACTED] tool_name='Bash', input_len=50
============================================================
```

**Key things to check:**
- ✅ Input data keys include 'tool_name'
- ✅ tool_name value is 'Bash' (or other tool name, not 'unknown')
- ✅ tool_input.command contains the actual command being run

### Step 4: Check Post-Tool Debug Log
```bash
tail -150 ~/.claude/logs/post_tool_debug.log
```

**Expected output:**
```
============================================================
[2025-11-16T20:10:45.234567] PostToolUse Hook Fired
============================================================
Session ID: abc123def456...
Input data keys: ['tool_name', 'output', 'exit_code', ...]
tool_name: Bash
exit_code: 0
error: None
output length: 245 chars
============================================================
[EXTRACTED] tool_name='Bash', exit_code=0
============================================================
```

**Key things to check:**
- ✅ tool_name is properly extracted (not 'unknown')
- ✅ exit_code is 0 for successful commands
- ✅ output contains the actual command result

### Step 5: Check Extraction Debug Log
```bash
tail -300 ~/.claude/logs/extraction_debug.log
```

**Expected output:**
```
============================================================
[2025-11-16T20:10:45.500000] 🔍 EXTRACTION STARTED
============================================================
[2025-11-16T20:10:45.500001] Total events to process: 4
[2025-11-16T20:10:45.500002] Event types present: {'UserPromptSubmit': 1, 'PreToolUse': 1, 'PostToolUse': 1, 'Stop': 1}

[2025-11-16T20:10:45.500003] ✓ Found UserPromptSubmit: 'List my home directory'
[2025-11-16T20:10:45.500004] ✓ Found PreToolUse: tool_name='Bash', timestamp=2025-11-16T20:10:45.100000
[2025-11-16T20:10:45.500005] ✓ Found PostToolUse: tool_name='Bash', exit_code=0

[2025-11-16T20:10:45.500006] Grouped events: 1 PreToolUse, 1 PostToolUse, 1 UserPrompt

[2025-11-16T20:10:45.500007]
📍 Starting tool call matching...

[2025-11-16T20:10:45.500008]   Processing PreToolUse #1: Bash
[2025-11-16T20:10:45.500009]     Timestamp: 2025-11-16T20:10:45.100000
[2025-11-16T20:10:45.500010]     Candidate PostToolUse: time_diff=0.134s
[2025-11-16T20:10:45.500011]     → Selected as best match
[2025-11-16T20:10:45.500012]     ✅ MATCHED: status=success, latency=134ms

============================================================
[2025-11-16T20:10:45.500013] 📊 EXTRACTION COMPLETE
============================================================
[2025-11-16T20:10:45.500014] Extracted 1 tool calls
[2025-11-16T20:10:45.500015] Unique tools: ['Bash']
[2025-11-16T20:10:45.500016] Total latency: 134ms
```

**Key success indicators:**
- ✅ Event types present: Has PreToolUse and PostToolUse (not 0)
- ✅ "✓ Found PreToolUse: tool_name='Bash'" (not 'unknown')
- ✅ "✓ Found PostToolUse: tool_name='Bash'"
- ✅ "✅ MATCHED: status=success, latency=XXms"
- ✅ "Extracted 1 tool calls"
- ✅ "Unique tools: ['Bash']"

### Step 6: Verify in Langfuse
```bash
# Open Langfuse UI
open http://localhost:3000

# Navigate to project and look for newest trace
```

**Expected to see:**
- ✅ New trace appears
- ✅ Metadata shows: `tool_count: 1` (not 0!)
- ✅ Metadata shows: `unique_tools: ["Bash"]`
- ✅ Expand "Observations" to see nested tool span
- ✅ Tool span shows: input (command), output (result), latency

---

## Troubleshooting

### Problem: tool_name still shows 'unknown'
**Step 1:** Check pre_tool_debug.log to see what keys are in input_data
```bash
grep "Input data keys:" ~/.claude/logs/pre_tool_debug.log
```

**Possible solutions:**
- If keys show different names (e.g., 'name', 'tool', etc.): We need to update the field extraction logic
- The pre_tool_use.py already tries alternate names, but we may need to add more

### Problem: PreToolUse events not found (0 found)
**Cause:** The hooks might not be firing or buffering correctly
**Check:**
```bash
# Verify the hook is being called
grep "PreToolUse Hook Fired" ~/.claude/logs/pre_tool_debug.log | wc -l

# If 0 lines, the hook isn't firing. Check Claude Code hook configuration
# in .claude/settings.json
```

### Problem: PostToolUse not matching (shows ❌ NO MATCH)
**Cause:** Timestamps might be too far apart or tool names don't match exactly
**Check:**
```bash
# Look at the timestamps
grep "Timestamp:" ~/.claude/logs/extraction_debug.log
grep "Candidate PostToolUse:" ~/.claude/logs/extraction_debug.log

# If time difference > 60s, something went wrong
# If tool names don't match exactly, there might be a field naming issue
```

### Problem: tool_count is still 0 in Langfuse
**Cause:** Either:
1. Events not being extracted properly (check extraction_debug.log)
2. extract_metadata_from_events() not being called
3. Tool metadata not being added to trace

**Debug steps:**
```bash
# 1. Check if extraction is happening
tail ~/.claude/logs/extraction_debug.log | grep "Extracted.*tool calls"

# 2. Check if Langfuse is receiving data
tail ~/.claude/logs/langfuse_hook_debug.log | grep "tool"

# 3. Check Langfuse directly
curl http://localhost:3000/api/traces -H "Authorization: Bearer YOUR_KEY"
```

---

## Expected Success Criteria

All of the following should be true:

- [ ] ✅ pre_tool_debug.log shows tool_name='Bash' (not 'unknown')
- [ ] ✅ post_tool_debug.log shows tool_name='Bash'
- [ ] ✅ extraction_debug.log shows "Extracted 1 tool calls"
- [ ] ✅ extraction_debug.log shows "✅ MATCHED: status=success"
- [ ] ✅ Langfuse trace shows tool_count: 1 (not 0)
- [ ] ✅ Langfuse trace shows unique_tools: ["Bash"]
- [ ] ✅ Tool observation visible in Langfuse UI with input/output/latency

When all of these are true, the integration is working correctly! 🎉

---

## Next Steps

Once testing is complete and successful:

1. **Phase C:** Clean up debug logging (make it optional/configurable)
2. **Phase D:** Add tool metadata to Langfuse traces (tool_count, latency, etc.)
3. **Phase E:** Create tool span observations (nested observations in trace)
4. **Phase F:** Final E2E test with multiple bash calls in one turn

---

## Log File Locations

For quick reference:
- **Pre-tool debug:** `~/.claude/logs/pre_tool_debug.log`
- **Post-tool debug:** `~/.claude/logs/post_tool_debug.log`
- **Extraction debug:** `~/.claude/logs/extraction_debug.log`
- **Langfuse hook debug:** `~/.claude/langfuse_hook_debug.log`

All in `~/.claude/logs/` directory.

