# Conversation Latency Tracking Fix

## Problem Identified

Traces were showing `latency: 0` at the trace level, which didn't reflect the actual time the Claude Code conversation took.

**Example from trace `90714775b1f7c2ad49d5cdefe6763997`:**
```json
{
  "latency": 0.002,
  "observations": [
    {
      "name": "claude-response",
      "latency": 0
    }
  ]
}
```

The latency was measuring the hook execution time (~2ms), not the actual conversation time.

## Root Cause

1. **Hook execution is fast** (~1-5ms) - The hook processes the transcript and sends to Langfuse almost instantly
2. **Timestamps were extracted but not used** - The code parsed `start_timestamp` and `end_timestamp` from the transcript but never calculated the latency
3. **Latency not stored anywhere** - Even if calculated, it wasn't stored in metadata or as a custom metric

## Solution

### 1. Calculate Conversation Latency from Transcript Timestamps

```python
# Calculate timestamps and conversation latency
conversation_latency_ms = 0

if start_timestamp and end_timestamp:
    try:
        start_time = date_parser.parse(start_timestamp)
        end_time = date_parser.parse(end_timestamp)
        # Calculate actual conversation latency in milliseconds
        latency_delta = end_time - start_time
        conversation_latency_ms = int(latency_delta.total_seconds() * 1000)
    except Exception as e:
        pass
```

### 2. Store Latency in Custom Metrics

Added `conversation_latency_ms` and `conversation_latency_seconds` to metadata at both trace and generation levels:

```python
trace_metadata = {
    "project": project_name,
    "timestamp": datetime.now().isoformat(),
    "user_message_length": len(user_message),
    "assistant_message_length": len(assistant_message),
    "tool_count": len(tool_calls)
}

# Add conversation latency as custom metric if calculated
if conversation_latency_ms > 0:
    trace_metadata["conversation_latency_ms"] = conversation_latency_ms
    trace_metadata["conversation_latency_seconds"] = round(conversation_latency_ms / 1000, 3)
```

## Verification Results

### Test Case
- **Created trace:** `e8ef3f4d08b547ad14bd2befc5c65f89`
- **Session:** `test-latency-141532`
- **Expected latency:** 2.5 seconds (from timestamps 2.5 seconds apart)
- **Actual latency tracked:** 2500 ms / 2.5 sec ✅

### Trace-Level Metadata
```json
{
  "conversation_latency_ms": 2500,
  "conversation_latency_seconds": 2.5,
  "user_message_length": 33,
  "assistant_message_length": 44,
  "tool_count": 0
}
```

### How It Works

The latency is calculated from two timestamp fields automatically captured in every Claude Code transcript:

1. **Start Timestamp** - When the user message was processed
2. **End Timestamp** - When the assistant response was received

These are extracted from the JSONL transcript and used to calculate the actual wall-clock time of the conversation.

## Benefits

### 1. Accurate Performance Metrics
- Tracks actual conversation time, not hook execution time
- Visible at trace level immediately (no drilling into observations)
- Stored as searchable metadata

### 2. Performance Insights
- Identify slow conversations
- Monitor average latency over time
- Detect outliers and anomalies
- Compare different model/prompt combinations

### 3. Cost Correlation
- Correlate latency with token usage
- Identify if longer conversations are more expensive
- Monitor efficiency over time

## Files Modified

**`.claude/hooks/log_to_langfuse.py`** (3 changes):
1. Lines 216-229: Calculate conversation latency from timestamps
2. Lines 235-246: Add latency to trace-level metadata
3. Lines 291-302: Add latency to generation observation metadata

## Langfuse UI Visibility

The latency is now visible in:
1. **Trace metadata section** - Shows `conversation_latency_ms` and `conversation_latency_seconds`
2. **Generation metadata section** - Same fields in nested observation
3. **Search/filter** - Can search for "conversation_latency_ms" in metadata

## Custom Metrics Format

The metrics are stored as:
- **`conversation_latency_ms`** - Integer milliseconds (e.g., 2500)
- **`conversation_latency_seconds`** - Float seconds (e.g., 2.5)

Both formats are stored for flexibility:
- Use milliseconds for precise timing
- Use seconds for human readability

## No Impact on Existing Features

✅ Token tracking - Unchanged
✅ Cost calculation - Unchanged
✅ Model identification - Unchanged
✅ Cache token tracking - Unchanged
✅ Hook backwards compatibility - Maintained

## Future Enhancement Ideas

### 1. Latency Breakdown Tracking
Could add finer-grained metrics:
```python
metadata = {
    "prompt_preparation_ms": 100,
    "model_inference_ms": 1500,
    "token_processing_ms": 900
}
```

### 2. Latency Alerts
Create Langfuse alerts for:
- Conversations taking > 30 seconds
- Average latency trending upward
- Specific models consistently slow

### 3. Latency Dashboard
Create Langfuse dashboard showing:
- P50, P95, P99 latencies
- Latency by model
- Latency by project
- Latency trends over time

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Latency tracking | ❌ Hook execution time | ✅ Actual conversation time |
| Visibility | Hidden in buried metrics | Visible in trace metadata |
| Accuracy | ~0-5ms | Actual wall-clock time (100s to 1000s ms) |
| Searchability | N/A | ✅ Via custom metadata |
| Trend analysis | Not possible | ✅ Now trackable over time |

---

**Fix Applied:** 2025-11-14
**Test Status:** ✅ VERIFIED AND TESTED
**Production Ready:** ✅ YES

Example: 2500ms conversation latency now properly tracked and visible in Langfuse traces!
