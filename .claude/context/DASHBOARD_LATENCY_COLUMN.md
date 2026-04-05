# Adding Latency Column to Langfuse Dashboard

## The Confusion Explained

You were right to be confused about `latency: 0`. Here's what's happening:

### Why `trace.latency = 0.002ms`

```
Hook runs fast:
  start_span() ─────────┐
     [0.002ms]          │ ← Langfuse measures this
  end_span() ──────────┘

Result: latency = 0.002ms (hook execution time, not conversation time)
```

### But We HAVE the Real Time

In the metadata we store:
```json
{
  "conversation_latency_ms": 8468,
  "conversation_latency_seconds": 8.468
}
```

This is the ACTUAL conversation time (user message → assistant response = 8.468 seconds).

---

## Dashboard Column Mapping

Use this in your Langfuse dashboard to display latency:

### Column Configuration

```json
{
  "column_name": "Conversation Latency",
  "data_source": "trace.metadata.conversation_latency_seconds",
  "format": "{value} sec",
  "sort_order": "ascending",
  "example_values": ["2.5 sec", "8.468 sec", "1.234 sec"]
}
```

### Why This Works

- ✅ Shows actual conversation time
- ✅ Stored in metadata (searchable)
- ✅ In seconds (human-readable)
- ✅ Available in every trace

### Why NOT `trace.latency`

- ❌ Shows hook execution time (~0.002ms)
- ❌ Not relevant to conversation performance
- ❌ Misleading for analysis

---

## Complete Dashboard Schema

```json
{
  "columns": [
    {
      "name": "Session ID",
      "source": "trace.sessionId",
      "width": "15%"
    },
    {
      "name": "Model",
      "source": "trace.observations[0].model",
      "width": "12%"
    },
    {
      "name": "Input",
      "source": "trace.input",
      "truncate": 50,
      "width": "20%"
    },
    {
      "name": "Output",
      "source": "trace.output",
      "truncate": 50,
      "width": "20%"
    },
    {
      "name": "Latency",
      "source": "trace.metadata.conversation_latency_seconds",
      "unit": "sec",
      "format": "decimal(2)",
      "sort": "ascending",
      "width": "10%"
    },
    {
      "name": "Tokens",
      "source": "trace.observations[0].usageDetails.total",
      "width": "8%"
    },
    {
      "name": "Cost",
      "source": "trace.observations[0].costDetails.total",
      "format": "currency",
      "width": "8%"
    },
    {
      "name": "Timestamp",
      "source": "trace.timestamp",
      "format": "datetime",
      "width": "12%"
    }
  ]
}
```

---

## Example Dashboard View

| Session | Model | Input | Output | Latency | Tokens | Cost | Time |
|---------|-------|-------|--------|---------|--------|------|------|
| d23d5ebd | haiku | What is Claude... | Claude is... | **8.468 sec** | 122,855 | $0.018 | 2025-11-14T22:15:35Z |
| test-latency | haiku | Test message... | Test response... | **3.0 sec** | 5,135 | $0.001 | 2025-11-14T22:15:21Z |
| test-latency | haiku | Test message... | This response took... | **2.5 sec** | 5,135 | $0.001 | 2025-11-14T22:15:15Z |

---

## API Query for Dashboard

If building a custom dashboard, query the Langfuse API:

```python
import requests

def get_traces_for_dashboard(limit=50):
    """Get trace data formatted for dashboard."""

    response = requests.get(
        f"{LANGFUSE_BASE_URL}/api/public/traces?limit={limit}",
        auth=(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    )

    traces = response.json()["data"]

    dashboard_data = []
    for trace in traces:
        row = {
            "session_id": trace["sessionId"],
            "model": trace["observations"][0]["model"] if trace["observations"] else "—",
            "input": trace["input"][:50] + "..." if trace["input"] else "—",
            "output": trace["output"][:50] + "..." if trace["output"] else "—",
            "latency_seconds": trace["metadata"].get("conversation_latency_seconds", 0),
            "total_tokens": trace["observations"][0]["usageDetails"]["total"] if trace["observations"] else 0,
            "total_cost": trace["observations"][0]["costDetails"]["total"] if trace["observations"] else 0,
            "timestamp": trace["timestamp"]
        }
        dashboard_data.append(row)

    return dashboard_data
```

---

## Summary

| Field | Value | Use in Dashboard |
|-------|-------|------------------|
| `trace.latency` | 0.002ms | ❌ NO - Hook time |
| `trace.metadata.conversation_latency_seconds` | 8.468 sec | ✅ YES - Use this! |
| `trace.metadata.conversation_latency_ms` | 8468 ms | ✅ Also good |

**For your latency column, use:**
```
trace.metadata.conversation_latency_seconds
```

This gives you the real, actual conversation time that matters for performance analysis.

---

**Date:** 2025-11-14
**Status:** ✅ READY TO ADD TO DASHBOARD
**Verified:** Yes - Data available in all recent traces
