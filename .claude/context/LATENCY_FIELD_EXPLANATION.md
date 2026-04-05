# Langfuse Latency Field: The Real Issue & Solution

## The Problem You Discovered

You were right to be confused. **`latency: 0` doesn't make sense for a multi-second conversation.**

### Why Latency is 0

When we call `langfuse.start_span()` in the hook:
```
Hook execution start: 2025-11-14T22:15:35.000Z
  ├─ span.start() ─────────────────────┐
  ├─ [some processing] (~0.002ms)      │ latency = 0.002ms
  └─ span.end() ───────────────────────┘
Hook execution end: 2025-11-14T22:15:35.002Z
```

Langfuse measures the time between `span.start()` and `span.end()` - which is the hook execution time (~0.002ms), NOT the conversation time.

### Why We Can't Fix It with Python SDK

The Langfuse Python SDK doesn't support custom timing:
```python
# ❌ This doesn't work - span.end() accepts NO parameters
span.end(end_time=datetime(2025, 11, 14, 22, 15, 38))  # TypeError!

# ❌ This doesn't work either - update() has no timing parameters
span.update(latency=3000)  # Not supported
```

## Two Solutions

### Solution 1: Use REST API (Better Control)

The REST API **does** support custom `startTime` and `endTime`:

```python
import requests
from datetime import datetime

def log_to_langfuse_via_rest_api(
    session_id: str,
    user_message: str,
    assistant_message: str,
    start_timestamp: str,
    end_timestamp: str,
    token_usage: dict
):
    """Log trace with proper timing via REST API."""

    from dateutil import parser as date_parser

    # Parse conversation timestamps
    start_time = date_parser.parse(start_timestamp)
    end_time = date_parser.parse(end_timestamp)

    # Calculate latency
    latency_ms = int((end_time - start_time).total_seconds() * 1000)

    # Create trace via REST API with custom timing
    trace_data = {
        "id": f"trace-{session_id}-{int(datetime.now().timestamp())}",
        "name": "consulting-co-conversation",
        "sessionId": session_id,
        "input": user_message[:5000],
        "output": assistant_message[:5000],
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "metadata": {
            "user_message_length": len(user_message),
            "assistant_message_length": len(assistant_message),
            "conversation_latency_ms": latency_ms
        },
        "tags": ["claude-code", "conversation"]
    }

    # POST to Langfuse REST API
    response = requests.post(
        f"{LANGFUSE_BASE_URL}/api/public/traces",
        json=trace_data,
        auth=(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    )

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create trace: {response.text}")
```

**Advantages:**
- ✅ Latency field shows actual conversation time (~3000ms)
- ✅ Full control over timing
- ✅ No dependency on context managers
- ✅ Can backfill historical traces

**Disadvantages:**
- Slightly more code
- Direct API calls instead of SDK

### Solution 2: Accept SDK Limitation + Custom Metric

Keep using the Python SDK but **rely on the metadata field** we're already populating:

```python
# Python SDK approach (current)
trace_metadata = {
    "conversation_latency_ms": 3000,    # ← USE THIS
    "conversation_latency_seconds": 3.0  # ← USE THIS
}

# Langfuse will show:
# trace.latency: 0.002ms  (hook execution time)
# trace.metadata.conversation_latency_ms: 3000ms  (actual time)
```

**Advantages:**
- ✅ Simple, uses existing SDK
- ✅ Metadata is searchable and queryable
- ✅ Less code changes

**Disadvantages:**
- ❌ Latency field shows hook time, not conversation time
- Dashboard must use metadata field, not the native latency field

---

## What to Do

### Best Recommendation: Use REST API Approach

Modify the hook to use REST API directly for better control. This gives you:
1. **Correct latency field** (~3000ms)
2. **All the data we need** (input, output, tokens, cost)
3. **Same observability** as SDK approach
4. **Cleaner separation** between trace timing and hook execution

### Current Workaround: Use Metadata Field

If you prefer to stick with the SDK:
- Accept that `latency` field shows 0.002ms
- Use `metadata.conversation_latency_ms` field instead
- Dashboard should display this field as the "Conversation Latency"

---

## For Your Dashboard

Add a column that uses **`metadata.conversation_latency_ms`** instead of the native `latency` field:

```json
{
  "trace_name": "consulting-co-conversation",
  "conversation_latency_ms": 3000,  ← Display this
  "conversation_latency_seconds": 3.0,  ← Or this
  "model": "claude-haiku-4-5-20251001",
  "total_tokens": 5135,
  "cost": "$0.00072"
}
```

This gives you accurate conversation latency tracking without needing to rewrite the hook.

---

## Summary

| Metric | Python SDK | REST API |
|--------|-----------|----------|
| **trace.latency** | 0.002ms ❌ | 3000ms ✅ |
| **metadata.conversation_latency_ms** | 3000ms ✅ | 3000ms ✅ |
| **Code complexity** | Simple | Moderate |
| **Dashboard ready** | Yes (use metadata) | Yes (use latency field) |

**Recommendation:** Use metadata field in dashboard for now. If you want to use the native latency field, we can refactor to use REST API.

---

**Date:** 2025-11-14
**Issue:** Latency field limitation in Langfuse Python SDK v3
**Status:** Documented and workarounds provided
