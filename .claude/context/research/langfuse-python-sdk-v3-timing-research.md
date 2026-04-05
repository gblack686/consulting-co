# Langfuse Python SDK v3 - Timing & Latency Research

## Research Summary
Based on official Langfuse documentation, here's what I found about timing, latency, and metrics in Langfuse Python SDK v3.

---

## 1. START_TIME AND END_TIME FOR SPANS AND OBSERVATIONS

### Key Finding: Automatic Timing via Context Managers
**Langfuse SDK v3 automatically handles start and end times** when you use context managers or the `@observe` decorator. You do NOT need to manually set `start_time` and `end_time` parameters.

### How It Works
When using context managers, Langfuse captures timing automatically:

```python
from langfuse import get_client

langfuse = get_client()

# Timing is automatically captured
with langfuse.start_as_current_span(name="my-operation") as span:
    # Your code here
    # Start time: captured when context manager enters
    # End time: captured when context manager exits
    pass
# Span automatically ended and timed
```

When using the `@observe` decorator, timing is also automatic:

```python
from langfuse import observe

@observe
def my_function(data):
    # Timing automatically captured
    return {"processed": data}
```

---

## 2. LATENCY CALCULATION

### Is Latency Automatic?
**YES - Latency is automatically calculated** from the span's start and end times.

### How Latency Is Computed
- **Source**: Difference between span end time and span start time
- **Unit**: Milliseconds (ms)
- **Availability**: Via the Metrics API as `"latency"` measure
- **Automatic**: No manual configuration needed

### Metrics API Access
You can query latency via the Metrics API:

```python
query = """
{
  "view": "observations",
  "metrics": [{"measure": "latency", "aggregation": "p95"}],
  "dimensions": [{"field": "name"}],
  "fromTimestamp": "2025-05-01T00:00:00Z",
  "toTimestamp": "2025-05-13T00:00:00Z"
}
"""

langfuse.api.metrics.metrics(query=query)
```

Available latency aggregations:
- `avg` - Average latency
- `min` - Minimum latency
- `max` - Maximum latency
- `p50`, `p75`, `p90`, `p95`, `p99` - Percentile latencies

---

## 3. PARAMETERS FOR SPAN AND OBSERVATION METHODS

### `start_as_current_span()` Parameters

From the documentation, here are the main parameters:

```python
langfuse.start_as_current_span(
    name: str,                          # Required: Name of the span
    input: Optional[Any] = None,        # Input data
    output: Optional[Any] = None,       # Output data
    metadata: Optional[Any] = None,     # Additional metadata (JSON-serializable)
    version: Optional[str] = None,      # Version identifier
    level: Optional[str] = None,        # Log level: DEBUG, DEFAULT, WARNING, ERROR
    status_message: Optional[str] = None, # Status description
    trace_context: Optional[Dict] = None, # For linking to existing traces
    as_type: Optional[str] = None       # Observation type (e.g., "span", "chain")
)
```

### `start_as_current_generation()` Parameters

```python
langfuse.start_as_current_generation(
    name: str,                          # Required: Name of the generation
    model: Optional[str] = None,        # Model name (e.g., "gpt-4")
    input: Optional[Any] = None,        # Input/prompt
    output: Optional[Any] = None,       # LLM output
    metadata: Optional[Any] = None,     # Additional metadata
    version: Optional[str] = None,      # Version identifier
    level: Optional[str] = None,        # Log level
    status_message: Optional[str] = None, # Status description
    trace_context: Optional[Dict] = None, # For linking to existing traces
    as_type: Optional[str] = None       # Observation type
)
```

### `start_as_current_observation()` Parameters

This is a generic method that can create any observation type:

```python
langfuse.start_as_current_observation(
    name: str,                          # Required: Name
    input: Optional[Any] = None,        # Input data
    output: Optional[Any] = None,       # Output data
    metadata: Optional[Any] = None,     # Metadata
    version: Optional[str] = None,      # Version
    level: Optional[str] = None,        # Log level
    status_message: Optional[str] = None, # Status description
    as_type: Optional[str] = None,      # IMPORTANT: Specify type (e.g., "generation", "span", "tool")
    trace_context: Optional[Dict] = None, # For linking traces
    model: Optional[str] = None,        # For generation type only
)
```

### Manual Methods (without context manager)

```python
span = langfuse.start_span(name="my-span")
# ... do work ...
span.end()

generation = langfuse.start_generation(name="llm-call", model="gpt-4")
# ... do work ...
generation.end()
```

---

## 4. PASSING TIMING INFORMATION FROM TRANSCRIPTS

### Method 1: Using `completion_start_time` for TTFT (Time To First Token)

If you're manually creating generations and have timing data (e.g., from a transcript), use `completion_start_time`:

```python
from langfuse import get_client
import datetime

langfuse = get_client()

# Create generation with transcript data
with langfuse.start_as_current_observation(
    as_type="generation",
    name="llm-call",
    model="gpt-4"
) as generation:

    # Update with transcript timing information
    generation.update(
        completion_start_time=datetime.datetime.fromisoformat(
            transcript_data["llm_start_time"]  # ISO 8601 format
        ),
        output=transcript_data["response"],
        input=transcript_data["prompt"]
    )

langfuse.flush()
```

### Parameters for `update()` method

When updating observations with timing info:

```python
generation.update(
    input: Optional[Any] = None,        # Input/prompt from transcript
    output: Optional[Any] = None,       # Response from transcript
    metadata: Optional[Any] = None,     # Custom metadata
    version: Optional[str] = None,      # Version info
    level: Optional[str] = None,        # Log level
    status_message: Optional[str] = None, # Error message if failed
    completion_start_time: Optional[datetime] = None, # TTFT timing
    model: Optional[str] = None,        # Model name
    model_parameters: Optional[Dict] = None, # Temperature, etc.
    usage_details: Optional[Dict] = None, # Token counts
    cost_details: Optional[Dict] = None, # Cost information
    prompt: Optional[PromptClient] = None # Associated prompt
)
```

**Important:** `completion_start_time` parameter format is **ISO 8601 datetime object** (Python `datetime.datetime`)

---

## 5. CUSTOM METRICS AND SEPARATE LATENCY FIELDS

### How to Store Custom Metrics

Langfuse supports storing custom metrics in two ways:

#### Method 1: Using Metadata (Flexible)

```python
with langfuse.start_as_current_span(name="my-operation") as span:
    # ... do work ...
    span.update(
        metadata={
            "custom_latency_ms": 1234,  # Custom timing metric
            "processing_time": 5.67,     # Any custom metric
            "queue_wait_time": 234,      # Your custom fields
            "actual_tokens": 150,
            "estimated_tokens": 140,
            "confidence_score": 0.92
        }
    )
```

#### Method 2: Using Cost Details (For Cost/Token Info)

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

#### Method 3: Using the Metrics API (For Querying)

Query custom metrics stored in metadata:

```python
# Query observations and extract metadata
query = """
{
  "view": "observations",
  "metrics": [{"measure": "count", "aggregation": "count"}],
  "dimensions": [{"field": "name"}],
  "filters": [
    {
      "column": "metadata",
      "operator": "contains",
      "key": "custom_latency_ms",
      "value": 1000,
      "type": "stringObject"
    }
  ],
  "fromTimestamp": "2025-05-01T00:00:00Z",
  "toTimestamp": "2025-05-13T00:00:00Z"
}
"""

langfuse.api.metrics.metrics(query=query)
```

---

## 6. TIMESTAMP FORMAT SPECIFICATIONS

### ISO 8601 Format (REQUIRED)

All timestamps must be in **ISO 8601 format**:

```python
import datetime

# Correct ISO 8601 format
timestamp = datetime.datetime.now(datetime.timezone.utc)
# Output: 2025-05-13T14:30:45.123456+00:00

# Or parse from string
timestamp = datetime.datetime.fromisoformat("2025-05-13T14:30:45.123456+00:00")

# For completion_start_time
generation.update(
    completion_start_time=timestamp
)
```

### Format Details
- Pattern: `YYYY-MM-DDTHH:MM:SS.ffffffZ` or `YYYY-MM-DDTHH:MM:SS.ffffff+00:00`
- Timezone: Always include timezone (UTC recommended)
- Python: Use `datetime.datetime` objects (SDK handles serialization)

---

## COMPLETE EXAMPLE: PROCESSING TRANSCRIPT DATA

Here's a comprehensive example showing how to use all the timing features together:

```python
from langfuse import get_client
import datetime

langfuse = get_client()

# Transcript data with timing
transcript = {
    "trace_name": "conversation",
    "start_time": "2025-05-13T14:00:00Z",
    "end_time": "2025-05-13T14:02:30Z",
    "messages": [
        {
            "role": "user",
            "content": "What is machine learning?",
            "timestamp": "2025-05-13T14:00:05Z"
        },
        {
            "role": "assistant",
            "content": "Machine learning is...",
            "timestamp": "2025-05-13T14:00:08Z",  # TTFT
            "completion_time": "2025-05-13T14:00:15Z",  # Full response time
            "tokens": 150
        }
    ]
}

# Create trace with transcript times
with langfuse.start_as_current_span(
    name=transcript["trace_name"],
    input={"user_message": transcript["messages"][0]["content"]}
) as root_span:

    # Set trace metadata
    root_span.update_trace(
        user_id="transcript_123",
        metadata={
            "source": "transcript",
            "transcript_duration_sec": 150
        }
    )

    # Create generation with timing from transcript
    with langfuse.start_as_current_generation(
        name="llm-response",
        model="gpt-4"
    ) as generation:
        msg = transcript["messages"][1]

        # Parse timestamps from transcript
        ttft = datetime.datetime.fromisoformat(
            msg["timestamp"].replace("Z", "+00:00")
        )
        completion_time = datetime.datetime.fromisoformat(
            msg["completion_time"].replace("Z", "+00:00")
        )

        # Update with timing and token info
        generation.update(
            input={"prompt": transcript["messages"][0]["content"]},
            output=msg["content"],
            completion_start_time=ttft,  # Time to first token
            usage_details={
                "output_tokens": msg["tokens"]
            },
            metadata={
                "ttft_ms": int((ttft - datetime.datetime.fromisoformat(
                    msg["timestamp"].replace("Z", "+00:00")
                )).total_seconds() * 1000),
                "total_latency_ms": int((completion_time - ttft).total_seconds() * 1000),
                "source": "transcript"
            }
        )

    # Span automatically ends and captures latency
    root_span.update(
        output={"response": transcript["messages"][1]["content"]},
        metadata={
            "total_conversation_latency_sec": 150,
            "message_count": len(transcript["messages"])
        }
    )

# Ensure all data is sent
langfuse.flush()
```

---

## KEY TAKEAWAYS

1. **Start/End Times**: Automatic - don't manually set unless using manual span API
2. **Latency**: Auto-calculated from start/end times in milliseconds
3. **TTFT Tracking**: Use `completion_start_time` parameter with ISO 8601 datetime
4. **Timestamp Format**: ISO 8601 (Python `datetime.datetime` objects)
5. **Custom Metrics**: Store in `metadata` dict or use `cost_details` / `usage_details`
6. **Querying**: Use Metrics API with `latency` measure for standard latency, or filter by metadata for custom fields
7. **Context Manager**: Always preferred - ensures proper timing and nesting

---

## REFERENCES

- Langfuse Python SDK v3 Documentation: https://langfuse.com/docs/observability/sdk/python/overview
- Advanced Usage (TTFT): https://langfuse.com/docs/observability/sdk/python/advanced-usage#passing-completion_start_time-for-ttft-tracking
- Metrics API: https://langfuse.com/docs/metrics/features/metrics-api
- Instrumentation Guide: https://langfuse.com/docs/observability/sdk/python/instrumentation
