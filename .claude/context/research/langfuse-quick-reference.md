# Langfuse Python SDK v3 - Quick Reference Guide

## TL;DR

| Question | Answer |
|----------|--------|
| **How do I set start_time?** | Automatic via context manager - no manual parameter needed |
| **How do I set end_time?** | Automatic when context manager exits - no manual parameter needed |
| **Is latency automatic?** | YES - calculated as (end_time - start_time) in milliseconds |
| **Latency parameter name?** | Query via Metrics API as `"measure": "latency"` |
| **Timestamp format?** | ISO 8601 - use Python `datetime.datetime` objects |
| **Can I set custom latency?** | YES - store in `metadata` dict |
| **TTFT parameter?** | `completion_start_time` (datetime object) |
| **When should I use TTFT?** | For generation observations tracking time to first token |

---

## Automatic Timing (No Parameters Needed)

```python
# ✓ CORRECT - Timing is automatic
with langfuse.start_as_current_span(name="operation") as span:
    do_work()
    # Start: recorded automatically
    # End: recorded automatically
    # Latency: calculated automatically

# ✗ WRONG - These parameters don't exist
with langfuse.start_as_current_span(
    name="operation",
    start_time="2025-05-13T14:00:00Z",  # ERROR: Not a valid parameter
    end_time="2025-05-13T14:01:00Z"     # ERROR: Not a valid parameter
):
    pass
```

---

## Method Parameters Reference

### Span/Generation Methods

```python
langfuse.start_as_current_span(
    name: str,                    # Required
    input: Any = None,
    output: Any = None,
    metadata: Dict = None,        # Custom metrics go here
    version: str = None,
    level: str = None,            # DEBUG, DEFAULT, WARNING, ERROR
    status_message: str = None,
    trace_context: Dict = None,
    as_type: str = None
)

langfuse.start_as_current_generation(
    name: str,                    # Required
    model: str = None,            # e.g., "gpt-4"
    input: Any = None,
    output: Any = None,
    metadata: Dict = None,
    version: str = None,
    level: str = None,
    status_message: str = None,
    trace_context: Dict = None,
    as_type: str = None
)

langfuse.start_as_current_observation(
    name: str,                    # Required
    as_type: str = None,          # IMPORTANT: 'generation', 'span', 'tool', etc.
    input: Any = None,
    output: Any = None,
    metadata: Dict = None,
    version: str = None,
    level: str = None,
    status_message: str = None,
    trace_context: Dict = None,
    model: str = None             # For type='generation'
)
```

### Update Methods

```python
span.update(
    input: Any = None,
    output: Any = None,
    metadata: Dict = None,        # Update custom metrics
    version: str = None,
    level: str = None,
    status_message: str = None,
    completion_start_time: datetime = None,  # TTFT for generations
    model: str = None,
    model_parameters: Dict = None,
    usage_details: Dict = None,   # {"input_tokens": 10, "output_tokens": 20}
    cost_details: Dict = None,    # {"total_cost": 0.0023}
    prompt: PromptClient = None
)
```

---

## 5-Minute Integration Example

```python
from langfuse import get_client
import datetime

langfuse = get_client()

# Process a transcript with timing
transcript = {
    "user": "What is machine learning?",
    "response": "Machine learning is...",
    "response_time": "2025-05-13T14:30:45.123Z"
}

# Create trace (automatic timing)
with langfuse.start_as_current_span(name="transcript-processing") as root:

    # Create generation with TTFT from transcript
    with langfuse.start_as_current_generation(
        name="llm-response",
        model="gpt-4"
    ) as gen:

        # Parse transcript timestamp
        ttft = datetime.datetime.fromisoformat(
            transcript["response_time"].replace("Z", "+00:00")
        )

        # Update with transcript data
        gen.update(
            input={"prompt": transcript["user"]},
            output=transcript["response"],
            completion_start_time=ttft,  # Enables TTFT metric
            metadata={
                "source": "transcript",
                "confidence": 0.95
            }
        )

    # Root span automatically times full operation
    root.update(output={"status": "complete"})

# Send data
langfuse.flush()
```

---

## Timestamp Handling

### Create Timestamps

```python
import datetime

# Current time (recommended)
now = datetime.datetime.now(datetime.timezone.utc)

# From ISO string
parsed = datetime.datetime.fromisoformat(
    "2025-05-13T14:30:45.123456+00:00"
)

# From transcript (remove Z)
from_transcript = datetime.datetime.fromisoformat(
    "2025-05-13T14:30:45.123Z".replace("Z", "+00:00")
)

# From Unix timestamp
from_unix = datetime.datetime.fromtimestamp(
    1715599845.123456,
    tz=datetime.timezone.utc
)
```

### Use in Langfuse

```python
# All correct
generation.update(completion_start_time=now)
generation.update(completion_start_time=parsed)
generation.update(completion_start_time=from_transcript)

# SDK automatically serializes to ISO 8601
# No manual string conversion needed
```

---

## Storing Custom Metrics

### In Metadata (Flexible)

```python
span.update(
    metadata={
        "preprocessing_time_ms": 100,
        "inference_time_ms": 500,
        "postprocessing_time_ms": 50,
        "queue_depth": 3,
        "cache_hit": True,
        "custom_score": 0.92
    }
)
```

### For Token/Cost Tracking

```python
generation.update(
    usage_details={
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150
    },
    cost_details={
        "total_cost": 0.0023,
        "input_cost": 0.001,
        "output_cost": 0.0013
    }
)
```

### Querying Custom Metrics

```python
# Filter by metadata
query = """{
  "view": "observations",
  "metrics": [{"measure": "count", "aggregation": "count"}],
  "filters": [
    {
      "column": "metadata",
      "operator": "contains",
      "key": "cache_hit",
      "value": "true",
      "type": "stringObject"
    }
  ],
  "fromTimestamp": "2025-05-01T00:00:00Z",
  "toTimestamp": "2025-05-13T23:59:59Z"
}"""

results = langfuse.api.metrics.metrics(query=query)
```

---

## Automatic Metrics Available

### For All Observations

- `latency` - Duration in milliseconds
- `count` - Number of observations
- Aggregations: `avg`, `min`, `max`, `p50`, `p75`, `p90`, `p95`, `p99`

### For Generations Only

- `timeToFirstToken` - TTFT in ms (when `completion_start_time` is set)
- `totalTokens` - Total tokens used
- `totalCost` - Cost if cost_details provided

### Query Example

```python
query = """{
  "view": "observations",
  "metrics": [
    {"measure": "latency", "aggregation": "p95"},
    {"measure": "latency", "aggregation": "avg"},
    {"measure": "timeToFirstToken", "aggregation": "p95"}
  ],
  "dimensions": [{"field": "name"}],
  "fromTimestamp": "2025-05-01T00:00:00Z",
  "toTimestamp": "2025-05-13T23:59:59Z"
}"""

results = langfuse.api.metrics.metrics(query=query)
```

---

## Common Patterns

### Pattern 1: Trace with Automatic Timing

```python
with langfuse.start_as_current_span(name="operation") as span:
    # Timing automatic
    result = do_work()
    span.update(output=result)
# Latency automatically available in UI
```

### Pattern 2: Generation with TTFT

```python
with langfuse.start_as_current_generation(
    name="llm",
    model="gpt-4"
) as gen:
    time.sleep(2)  # Simulate TTFT
    ttft_time = datetime.datetime.now(datetime.timezone.utc)

    response = stream_response()  # Get full response

    gen.update(
        output=response,
        completion_start_time=ttft_time
    )
# Both latency and TTFT automatically available
```

### Pattern 3: Nested Operations

```python
with langfuse.start_as_current_span(name="parent") as parent:
    with langfuse.start_as_current_span(name="child") as child:
        do_work()
    # child latency available
# parent latency includes child time
```

### Pattern 4: Transcript Processing

```python
with langfuse.start_as_current_span(name="transcript") as root:
    root.update_trace(user_id=transcript["user_id"])

    for msg in transcript["messages"]:
        if msg["role"] == "assistant":
            with langfuse.start_as_current_generation(
                name="response",
                model=transcript["model"]
            ) as gen:
                ttft = parse_timestamp(msg["ttft"])
                gen.update(
                    output=msg["content"],
                    completion_start_time=ttft
                )
```

---

## Error Prevention Checklist

- [ ] Using context managers (`with` statement)?
- [ ] Using Python `datetime.datetime` objects (not strings)?
- [ ] Timezone-aware datetimes (with `.timezone.utc`)?
- [ ] Using `completion_start_time` only for generations?
- [ ] Calling `.flush()` before exit?
- [ ] Custom metrics in `metadata` dict?
- [ ] No manual `start_time`/`end_time` parameters?

---

## Key Differences from v2

| Feature | v2 | v3 |
|---------|----|----|
| Timing | Manual setup | Automatic |
| Context | Manual management | Automatic via context manager |
| Nesting | Manual parent_id | Automatic context propagation |
| API | Dedicated methods | Low-level + high-level |

---

## Resources

- Docs: https://langfuse.com/docs/observability/sdk/python/overview
- Advanced: https://langfuse.com/docs/observability/sdk/python/advanced-usage
- Metrics: https://langfuse.com/docs/metrics/features/metrics-api
- API Reference: https://api.reference.langfuse.com/
