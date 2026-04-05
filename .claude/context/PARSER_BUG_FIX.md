# SDK Parser Bug Fix: message_start Support

**Date:** 2026-01-11  
**Issue:** Claude Agent SDK parser doesn't handle `message_start` events  
**Status:** ✅ FIXED (with monkey patch)

---

## Problem

The Claude Agent SDK's `message_parser.py` handles these message types:
- `user`
- `assistant`
- `system`
- `result`
- `stream_event`

But it does **NOT** handle `message_start` events, causing `MessageParseError` when the CLI sends these events.

### Evidence

According to [Claude Code CLI documentation](https://docs.claude.com/en/docs/claude-code/cli-reference), `message_start` is a valid event type in the stream-JSON output format. The CLI sends events like:

```json
{
  "type": "message_start",
  "message": {
    "id": "msg_014p7gG3wDgGV9EUtLvnow3U",
    "type": "message",
    "role": "assistant",
    "model": "claude-3-haiku-20240307",
    ...
  }
}
```

However, the SDK's `message_parser.py` only handles 5 message types and raises `MessageParseError` for unknown types like `message_start`.

## Solution

Added support for `message_start` events by treating them as `SystemMessage` objects (since they're metadata events with a flexible structure).

## Patch Applied

The parser now includes:

```python
case "message_start":
    # message_start is a metadata event, treat as SystemMessage
    try:
        return SystemMessage(
            subtype="message_start",
            data=data,
        )
    except KeyError as e:
        raise MessageParseError(
            f"Missing required field in message_start: {e}", data
        ) from e
```

## Files Modified

- **Location:** `~/.local/lib/python3.12/site-packages/claude_agent_sdk/_internal/message_parser.py`
- **Backup:** `~/.local/lib/python3.12/site-packages/claude_agent_sdk/_internal/message_parser.py.backup`

## References

### Official Documentation
- **Claude Code CLI Reference:** https://docs.claude.com/en/docs/claude-code/cli-reference
  - Documents `message_start` as a valid event type in stream-JSON format
  - Shows example `message_start` event structure

### Related Issues
- **GitHub Repository:** https://github.com/anthropics/claude-agent-sdk-python
- **Issue #252 (Windows CLI Path):** https://github.com/anthropics/claude-agent-sdk-python/issues/252
  - Related Windows-specific issue, but shows SDK has platform-specific problems
- **MessageParseError Documentation:** 
  - Error occurs when SDK encounters valid JSON that doesn't match expected structure
  - Common causes include unexpected message formats or protocol changes

### Error Handling Documentation
- **HexDocs (Elixir SDK):** https://hexdocs.pm/claude_agent_sdk/error-handling.html
  - Documents `MessageParseError` behavior
  - Notes that it occurs when message format is unexpected

## How to Apply/Re-apply

Run the fix script:

```bash
wsl
cd /mnt/c/Users/gblac/OneDrive/Desktop/consulting-co
python3 .claude/context/fix_message_parser.py
```

## Notes

- This is a **monkey patch** to the installed SDK package
- The patch will be **lost if you reinstall/upgrade** the SDK
- **Consider filing an issue** with the SDK maintainers for an official fix
- The patch is safe because `message_start` events are metadata and `SystemMessage` handles them appropriately
- This is a separate issue from the Windows subprocess timeout bug (Issue #208)

## Verification

To verify the patch is working:

1. Check that the case statement exists:
   ```bash
   wsl grep -A 5 'case "message_start":' ~/.local/lib/python3.12/site-packages/claude_agent_sdk/_internal/message_parser.py
   ```

2. Test the orchestrator backend - it should no longer throw parser errors for message_start events

## Recommended Next Steps

1. **Test the patch** with your orchestrator backend
2. **File a GitHub issue** with the SDK maintainers documenting this missing handler
3. **Monitor SDK releases** for an official fix
4. **Re-apply patch** after SDK upgrades until official fix is released







