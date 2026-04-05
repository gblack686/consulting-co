# Langfuse Python SDK v3 - Span Timing Research

## Executive Summary

Based on research of the Langfuse Python SDK v3 (OTEL-based, released June 2025), here are the key findings regarding span timing and the `span.end()` method:

**TL;DR:**
1. `span.end()` does NOT accept any parameters (including `end_time`)
2. Timing is set at span creation, not at end
3. Custom latency/duration can be set via OpenTelemetry span attributes during creation
4. REST API DOES support custom `startTime` and `endTime` parameters
5. Use `start_as_current_observation()` or `start_span()` with OpenTelemetry context for custom timing

---

## 1. Does `span.end(end_time=...)` Accept an `end_time` Parameter?

**Answer: NO**

The `span.end()` method does NOT accept any parameters. According to the official Langfuse Python SDK v3 documentation:

```python
# Correct usage
span.end()

# WRONG - this will fail
span.end(end_time=some_datetime)
```

This is consistent with OpenTelemetry's span lifecycle, where timing is determined at span creation, not at end.

---

## 2. What Parameters Does `span.end()` Accept?

**Answer: No parameters**

The `span.end()` method signature is:
```python
def end(self) -> None:
    """End the span."""
    pass
```

The method simply marks the span as complete and closes it. It takes no arguments.

---

## 3. Is There Any Way to Set Custom Latency/Duration After Creation?

**Answer: NO (by design)**

In Langfuse v3, you **cannot** modify timing after a span is created. However, you have options:

### Option A: Use `.update()` Method (For Non-Timing Attributes)

You CAN update span attributes like input, output, metadata, etc.:

```python
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_observation(as_type="span", name="my-span") as span:
    # Do work...
    span.update(
        output="result",
        metadata={"key": "value"}
    )
    # Timing is auto-captured, you cannot change it
```

**`LangfuseSpan.update()` Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | `Optional[Any]` | Input data |
| `output` | `Optional[Any]` | Output data |
| `metadata` | `Optional[Any]` | JSON-serializable metadata |
| `version` | `Optional[str]` | Version identifier |
| `level` | `Optional[SpanLevel]` | Severity level (DEBUG, DEFAULT, WARNING, ERROR) |
| `status_message` | `Optional[str]` | Status description |
| `completion_start_time` | `Optional[datetime]` | **Only for Generations**: TTFT tracking |

Note: `completion_start_time` is only available for generations, not regular spans.

### Option B: Set Timing at Creation Time (OpenTelemetry Attributes)

Since Langfuse v3 is OTEL-based, you can set timing via OpenTelemetry span attributes. The timing is captured when the span is created:

```python
from langfuse import get_client
import datetime

langfuse = get_client()

# Timing is automatic from span creation
with langfuse.start_as_current_observation(as_type="span", name="my-operation") as span:
    # Span automatically records start time here
    # ... do work ...
    # Span automatically records end time when exiting context
```

---

## 4. Can You Use the REST API to Create Spans with Custom Start/End Times?

**Answer: YES**

The Langfuse REST API **DOES support custom timestamps** for spans and generations.

### REST API Parameters for Observations (Spans/Generations)

According to Langfuse's GitHub issue #1157 (implemented Feb 2024):

**Available timestamp parameters:**
- `startTime` - Custom start time (ISO 8601 format)
- `endTime` - Custom end time (ISO 8601 format)

### Example REST API Call

```bash
POST https://api.langfuse.com/api/public/observations

{
  "type": "span",
  "name": "my-span",
  "startTime": "2024-01-01T10:00:00Z",
  "endTime": "2024-01-01T10:05:00Z",
  "input": {"key": "value"},
  "output": {"result": "success"},
  "traceId": "trace_id_here"
}
```

### When to Use REST API for Custom Timing

This is useful for:
- Data migration from other observability platforms
- Ingesting historical trace data
- Reconstructing past execution timelines
- Preserving original timestamps when moving to Langfuse

---

## 5. Recommended Approach for Custom Timing

**Best Practice: Use OpenTelemetry Attributes at Span Creation**

Since Langfuse v3 is built on OpenTelemetry, the recommended approach is to set timing information when creating the span:

### For Regular Spans (Automatic Timing)

```python
from langfuse import get_client

langfuse = get_client()

# Timing is automatically captured from creation to .end()
with langfuse.start_as_current_observation(as_type="span", name="process-data") as span:
    # Start time recorded here
    result = process_large_dataset()
    span.update(output=result)
    # End time recorded when exiting context
```

### For Generations (TTFT Tracking)

If you need to track time-to-first-token (TTFT) for LLM calls:

```python
from langfuse import get_client
import datetime
import time

langfuse = get_client()

with langfuse.start_as_current_observation(
    as_type="generation",
    name="llm-call",
    model="gpt-4"
) as generation:
    # Simulate time to first token
    time.sleep(3)

    # This is the ONLY timing parameter you can set during update
    generation.update(
        completion_start_time=datetime.datetime.now(),
        output="generated text",
        usage_details={"input_tokens": 10, "output_tokens": 50}
    )
```

### For Historical/Imported Data (Use REST API)

```python
import requests
import json

headers = {
    "Authorization": f"Bearer {secret_key}",
    "Content-Type": "application/json"
}

# Create span with custom times for historical data
observation_data = {
    "type": "span",
    "name": "imported-operation",
    "startTime": "2024-01-01T10:00:00Z",
    "endTime": "2024-01-01T10:05:00Z",
    "input": {"source": "historical_data"},
    "output": {"status": "complete"},
    "traceId": "your_trace_id"
}

response = requests.post(
    "https://api.langfuse.com/api/public/observations",
    headers=headers,
    json=observation_data
)
```

---

## Method Signatures - Complete Reference

### `LangfuseSpan.end()`
```python
def end(self) -> None:
    """
    End the span.

    No parameters accepted.
    No return value.
    """
```

### `LangfuseSpan.update()`
```python
def update(
    self,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    metadata: Optional[Any] = None,
    version: Optional[str] = None,
    level: Optional[SpanLevel] = None,  # "DEBUG", "DEFAULT", "WARNING", "ERROR"
    status_message: Optional[str] = None,
) -> "LangfuseSpan":
    """
    Update span attributes.

    Does NOT accept timing parameters (startTime, endTime, duration).
    Returns self for method chaining.
    """
```

### `LangfuseGeneration.update()` (Extends LangfuseSpan)
```python
def update(
    self,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    metadata: Optional[Any] = None,
    version: Optional[str] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    completion_start_time: Optional[datetime] = None,  # For TTFT tracking
    model: Optional[str] = None,
    model_parameters: Optional[Dict[str, Any]] = None,
    usage_details: Optional[Dict[str, int]] = None,
    cost_details: Optional[Dict[str, float]] = None,
    prompt: Optional[PromptClient] = None,
) -> "LangfuseGeneration":
    """
    Update generation attributes.

    completion_start_time: The timestamp when LLM started generating (for TTFT).
    Returns self for method chaining.
    """
```

### `Langfuse.start_span()`
```python
def start_span(
    self,
    name: str,
    input: Optional[Any] = None,
    metadata: Optional[Any] = None,
    # Note: No startTime parameter in Python SDK v3
) -> LangfuseSpan:
    """
    Create a span.

    Timing begins at this call.
    Must call .end() when complete.
    """
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Passing Parameters to `.end()`
```python
# WRONG
span.end(end_time=datetime.now())
span.end(status="complete")
span.end(output="result")
```

### ❌ Mistake 2: Using `.update()` for Timing
```python
# WRONG - .update() doesn't accept timing parameters
span.update(end_time=datetime.now())
```

### ❌ Mistake 3: Trying to Set Timing on Regular Spans
```python
# WRONG - completion_start_time only works on generations
span.update(completion_start_time=datetime.now())
```

### ✅ Correct Approach: Set Timing at Creation
```python
# CORRECT - Let Langfuse auto-capture timing
with langfuse.start_as_current_observation(as_type="span", name="work") as span:
    do_work()
    span.update(output="done")  # Only update non-timing attributes

# For custom timing via REST API only
requests.post(url, json={
    "startTime": "2024-01-01T10:00:00Z",
    "endTime": "2024-01-01T10:05:00Z"
})
```

---

## Why This Design?

Langfuse v3 uses OpenTelemetry as its foundation, which follows these principles:

1. **Span timing is immutable** - Set at creation, recorded at end
2. **No retroactive timing changes** - Maintains trace integrity
3. **Automatic time capture** - Reduces user error
4. **REST API flexibility** - For data migration and legacy imports

This design prevents:
- Incorrect latency metrics
- Trace data corruption
- Timeline inconsistencies

---

## Summary Table

| Feature | Python SDK v3 | REST API |
|---------|---------------|----------|
| Auto-capture timing | ✅ Yes | ❌ No (must provide) |
| Set startTime | ❌ No in SDK | ✅ Yes |
| Set endTime | ❌ No in SDK | ✅ Yes |
| Modify timing after creation | ❌ No | ❌ No |
| `span.end(end_time=...)` | ❌ Not supported | N/A |
| TTFT tracking (generations only) | ✅ via `completion_start_time` | ✅ via parameter |
| Update input/output/metadata | ✅ via `.update()` | ✅ via API |

---

## References

- Langfuse Python SDK v3 Documentation: https://langfuse.com/docs/sdk/python/sdk-v3
- Instrumentation Guide: https://langfuse.com/docs/observability/sdk/python/instrumentation
- Advanced Usage: https://langfuse.com/docs/observability/sdk/python/advanced-usage
- GitHub Issue #1157 (Custom Timestamps): https://github.com/langfuse/langfuse/issues/1157
- OpenTelemetry Concepts: https://opentelemetry.io/docs/concepts/

---

## Conclusion

**The short answer to your original question:**

1. **NO** - `span.end()` does not accept `end_time` parameter
2. `span.end()` accepts **NO parameters**
3. **NO** - Cannot set custom latency/duration after creation in SDK
4. **YES** - REST API supports custom `startTime` and `endTime`
5. **Recommended**: Use OpenTelemetry automatic timing at creation; use REST API for historical data imports

If you need custom timing for historical data, use the REST API. For real-time tracing, rely on Langfuse's automatic timing capture.
