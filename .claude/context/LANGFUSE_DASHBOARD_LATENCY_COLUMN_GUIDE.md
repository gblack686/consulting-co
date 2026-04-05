# Adding Conversation Latency Column to Langfuse Dashboard

## Status: ✅ Data Captured & Ready to Display

The conversation latency is **being captured correctly** in every trace. We verified this via API calls showing:
- Trace 1: 10,373 ms (10.373 seconds)
- Trace 2: 3,000 ms (3 seconds)
- Trace 3: 8,468 ms (8.468 seconds)

## How to Add the Column in Langfuse UI

### Step 1: Navigate to Traces View
1. Go to: http://localhost:3000/project/cmhv9lrqh0006p007jyz1n96i/traces

### Step 2: Open Column Customizer
1. Click **"Columns 14/26"** button (top right of traces table)
2. This opens the column visibility/customization modal

### Step 3: Expand Metadata Section
1. In the filter panel on the left, find **"Metadata"** button
2. Click to expand the Metadata section
3. Look for: **`conversation_latency_seconds`**

### Step 4: Enable the Column
1. Check the checkbox next to `conversation_latency_seconds`
2. The column should appear in the traces table
3. You can drag to reorder columns as needed

## What You'll See

Once enabled, the column will show values like:
```
Conversation Latency (seconds)
─────────────────────────────
10.373
3.0
8.468
2.5
5.2
```

## Alternative: If Metadata Field Not Showing

If `conversation_latency_seconds` doesn't appear in the Metadata dropdown:

### Option 1: Use the Metadata Column
Add the generic "Metadata" column and expand it to see all custom fields:
1. Enable the "Metadata" column
2. Click on a trace to view full metadata details
3. You'll see:
   ```json
   {
     "conversation_latency_ms": 10373,
     "conversation_latency_seconds": 10.373,
     "project": "consulting-co",
     "user_message_length": 330,
     ...
   }
   ```

### Option 2: Create a Custom Dashboard
Create a dashboard query using the Langfuse REST API:

```python
import requests

def get_traces_with_latency():
    """Get traces with conversation latency column."""

    response = requests.get(
        "http://localhost:3000/api/public/traces?limit=50",
        auth=(PUBLIC_KEY, SECRET_KEY)
    )

    traces = response.json()["data"]

    dashboard_rows = []
    for trace in traces:
        row = {
            "session_id": trace.get("sessionId"),
            "trace_name": trace.get("name"),
            "model": trace["observations"][0].get("model") if trace["observations"] else "—",
            "input": trace.get("input", "—")[:50],
            "output": trace.get("output", "—")[:50],
            "conversation_latency_sec": trace["metadata"].get("conversation_latency_seconds", "—"),
            "total_tokens": trace["observations"][0]["usageDetails"]["total"] if trace["observations"] else 0,
            "total_cost": trace["observations"][0]["costDetails"]["total"] if trace["observations"] else 0,
            "timestamp": trace.get("timestamp")
        }
        dashboard_rows.append(row)

    return dashboard_rows

# Display in table format
for row in get_traces_with_latency():
    print(f"{row['session_id']:12} | {row['conversation_latency_sec']:6} | ${row['total_cost']:.6f}")
```

## Field Reference

**Field Name in Metadata:** `conversation_latency_seconds`
**Data Type:** Float (seconds, e.g., 10.373)
**Alternative Format:** `conversation_latency_ms` (Integer milliseconds, e.g., 10373)
**Always Present:** Yes - in every trace created after the fix

## Complete Dashboard Schema

Here's what a complete dashboard with latency should look like:

| Column | Source | Format |
|--------|--------|--------|
| **Timestamp** | `trace.timestamp` | ISO 8601 |
| **Session ID** | `trace.sessionId` | Text |
| **Trace Name** | `trace.name` | Text |
| **Model** | `trace.observations[0].model` | Text (claude-haiku-4-5-20251001) |
| **Input Preview** | `trace.input` | Text (truncate to 50 chars) |
| **Output Preview** | `trace.output` | Text (truncate to 50 chars) |
| **Conversation Latency** | `trace.metadata.conversation_latency_seconds` | Number with "sec" unit |
| **Total Tokens** | `trace.observations[0].usageDetails.total` | Integer |
| **Total Cost** | `trace.observations[0].costDetails.total` | Currency ($) |
| **Tags** | `trace.tags` | List |
| **Environment** | `trace.environment` | Text |

## Verification

To verify the field exists in your traces:

```bash
curl -s http://localhost:3000/api/public/traces?limit=1 \
  -u $LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY \
  | jq '.data[0].metadata.conversation_latency_seconds'

# Should output: 10.373 (or whatever the value is)
```

## Notes

- ✅ The field is captured in **every trace** created by our hook
- ✅ Data is **persistent and searchable** in Langfuse
- ✅ You can **filter and sort** by this field once added to dashboard
- ✅ **Backward compatible** - doesn't affect existing traces
- ⚠️ May need to **refresh Langfuse UI** to see column options update

## Troubleshooting

### Problem: "Columns" button not responding
**Solution:** Try refreshing the page or clearing browser cache

### Problem: conversation_latency_seconds doesn't appear in metadata filter
**Solution:** Use the generic "Metadata" column instead - it will show all custom fields

### Problem: Authorization errors when viewing traces
**Solution:** Check Langfuse project permissions and API key configuration

## Next Steps

1. ✅ Data is being captured correctly (verified via API)
2. ⏳ Add the `conversation_latency_seconds` field as a column in the dashboard
3. ⏳ Create alerts based on latency (e.g., alert if latency > 30 seconds)
4. ⏳ Build latency trend visualizations (P50, P95, P99)

---

**Status:** ✅ Ready to add to dashboard
**Data Availability:** All recent traces have this field
**Last Verified:** 2025-11-14
