# Langfuse Python SDK v3 - Timing Code Examples

## Quick Reference: Setting Start/End Times

### Example 1: Basic Span with Automatic Timing

```python
from langfuse import get_client

langfuse = get_client()

# Timing is AUTOMATICALLY captured
with langfuse.start_as_current_span(name="process-data") as span:
    # Start time recorded when context manager enters
    data = process_data()
    # End time recorded when context manager exits
    span.update(output=data)
```

**Result:**
- Start time: Automatically captured
- End time: Automatically captured
- Latency: Automatically calculated (end_time - start_time in ms)

---

### Example 2: Generation with TTFT Timing from Transcript

```python
from langfuse import get_client
import datetime

langfuse = get_client()

# Data from transcript
transcript_data = {
    "prompt": "What is Python?",
    "response": "Python is a programming language...",
    "ttft_time": "2025-05-13T14:30:45.123Z",     # Time to first token
    "completion_time": "2025-05-13T14:30:48.456Z", # Full response time
    "output_tokens": 120
}

with langfuse.start_as_current_generation(
    name="llm-call",
    model="gpt-4",
    input={"prompt": transcript_data["prompt"]}
) as generation:

    # Parse ISO 8601 timestamps from transcript
    ttft = datetime.datetime.fromisoformat(
        transcript_data["ttft_time"].replace("Z", "+00:00")
    )

    # Update with transcript timing
    generation.update(
        output=transcript_data["response"],
        completion_start_time=ttft,  # Enables TTFT calculation
        usage_details={"output_tokens": transcript_data["output_tokens"]},
        metadata={
            "source": "transcript",
            "ltm_aware": True
        }
    )
```

**Metrics available:**
- `latency`: Full generation time (ms)
- `timeToFirstToken`: TTFT time (ms) - only when completion_start_time is set

---

### Example 3: Nested Spans with Automatic Context Propagation

```python
from langfuse import get_client

langfuse = get_client()

# Parent span timing is automatic
with langfuse.start_as_current_span(name="full-pipeline") as parent:

    # Child 1 timing is automatic
    with langfuse.start_as_current_span(name="retrieval") as child1:
        results = retrieve_documents()
        child1.update(output={"count": len(results)})

    # Child 2 timing is automatic
    with langfuse.start_as_current_span(name="llm-call") as child2:
        response = call_llm(results)
        child2.update(output=response)

    # Parent automatically captures total time
    parent.update(output=response)
```

**Latencies captured:**
- Parent: Total time for entire pipeline
- Child1: Time for retrieval only
- Child2: Time for LLM call only

---

### Example 4: Using Custom Latency Metrics in Metadata

```python
from langfuse import get_client
import time

langfuse = get_client()

start = time.time()

with langfuse.start_as_current_span(name="operation") as span:
    # Simulate work
    time.sleep(1)
    step1_duration = time.time() - start

    time.sleep(0.5)
    step2_start = time.time()

    time.sleep(1)
    step2_duration = time.time() - step2_start

    # Store custom latency metrics
    span.update(
        metadata={
            "step_1_latency_ms": int(step1_duration * 1000),
            "step_2_latency_ms": int(step2_duration * 1000),
            "total_custom_latency": int((time.time() - start) * 1000),
            "breakdown": {
                "preprocessing": 100,
                "inference": 500,
                "postprocessing": 400
            }
        }
    )
```

**Note:** These custom metrics are stored in metadata and can be:
- Filtered via Metrics API
- Displayed in custom dashboards
- Retrieved programmatically

---

### Example 5: Processing Batch Transcripts with Timing

```python
from langfuse import get_client
import datetime
from typing import List, Dict

langfuse = get_client()

def process_transcript(transcript: Dict) -> None:
    """Process a transcript with proper timing information."""

    with langfuse.start_as_current_span(
        name="process-transcript",
        input={"transcript_id": transcript["id"]}
    ) as trace:

        trace.update_trace(
            user_id=transcript.get("user_id"),
            metadata={"source": "transcript_batch"}
        )

        # Process each message with timing
        for i, message in enumerate(transcript["messages"]):
            if message["role"] == "assistant":
                # Parse timestamps from transcript
                msg_time = datetime.datetime.fromisoformat(
                    message["timestamp"].replace("Z", "+00:00")
                )

                # Create generation for LLM response
                with langfuse.start_as_current_generation(
                    name=f"response_{i}",
                    model=transcript.get("model", "unknown")
                ) as gen:

                    # Timing from transcript data
                    gen.update(
                        input={"prompt": transcript["messages"][i-1]["content"]},
                        output=message["content"],
                        completion_start_time=msg_time,
                        usage_details={
                            "output_tokens": message.get("tokens", 0)
                        },
                        metadata={
                            "sequence_number": i,
                            "has_timing_data": True
                        }
                    )
            else:
                # User message - just log it
                with langfuse.start_as_current_observation(
                    as_type="event",
                    name=f"user_message_{i}",
                    input={"content": message["content"]}
                ):
                    pass

# Process multiple transcripts
transcripts = [
    {
        "id": "transcript_1",
        "user_id": "user_123",
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": "What is AI?",
                "timestamp": "2025-05-13T14:00:00Z"
            },
            {
                "role": "assistant",
                "content": "AI is...",
                "timestamp": "2025-05-13T14:00:03Z",
                "tokens": 100
            }
        ]
    }
]

for transcript in transcripts:
    process_transcript(transcript)

langfuse.flush()
```

---

### Example 6: Querying Latency Data via Metrics API

```python
from langfuse import get_client

langfuse = get_client()

# Query p95 latency by operation name
query = """{
  "view": "observations",
  "metrics": [
    {
      "measure": "latency",
      "aggregation": "p95"
    },
    {
      "measure": "latency",
      "aggregation": "avg"
    }
  ],
  "dimensions": [{"field": "name"}],
  "filters": [
    {
      "column": "type",
      "operator": "equals",
      "value": "generation"
    }
  ],
  "fromTimestamp": "2025-05-01T00:00:00Z",
  "toTimestamp": "2025-05-13T23:59:59Z"
}"""

results = langfuse.api.metrics.metrics(query=query)
print(results)
# Output:
# {
#   "data": [
#     {
#       "name": "llm-call",
#       "latency_p95": 2500,  # 95th percentile in ms
#       "latency_avg": 1200   # Average in ms
#     },
#     ...
#   ]
# }
```

---

### Example 7: TTFT (Time To First Token) Tracking

```python
from langfuse import get_client
import datetime
import time

langfuse = get_client()

# Simulating a streaming LLM response
with langfuse.start_as_current_generation(
    name="streaming-llm",
    model="gpt-4"
) as generation:

    # Record when first token arrives
    time.sleep(2)  # Simulate 2s to first token
    ttft_time = datetime.datetime.now(datetime.timezone.utc)

    # Continue receiving tokens
    full_response = ""
    for token in ["This", " is", " a", " response"]:
        full_response += token
        time.sleep(0.1)  # Simulate token streaming

    # Update with TTFT information
    generation.update(
        output=full_response,
        completion_start_time=ttft_time,  # This enables TTFT calculation
        usage_details={
            "output_tokens": len(full_response.split())
        },
        metadata={
            "streaming": True,
            "ttft_seconds": 2.0  # For reference
        }
    )
```

**Calculated metrics:**
- `latency`: Total time from span start to end (ms)
- `timeToFirstToken`: Time from span start to completion_start_time (ms)

---

### Example 8: Error Tracking with Latency

```python
from langfuse import get_client
import datetime

langfuse = get_client()

try:
    with langfuse.start_as_current_span(name="risky-operation") as span:
        # Simulate work
        result = call_external_api()
        span.update(output=result)
except Exception as e:
    with langfuse.start_as_current_span(name="risky-operation") as span:
        span.update(
            status_message=str(e),
            level="ERROR",
            metadata={
                "error_type": type(e).__name__,
                "failed": True,
                "retry_count": 3
            }
        )
```

**Note:** Latency is still automatically calculated even for failed operations

---

## Timestamp Format Reference

### Python datetime to ISO 8601

```python
import datetime

# Create timestamp
now = datetime.datetime.now(datetime.timezone.utc)
# Output: 2025-05-13 14:30:45.123456+00:00

# Convert to ISO 8601 string (automatic in SDK)
iso_string = now.isoformat()
# Output: 2025-05-13T14:30:45.123456+00:00

# Parse from string
parsed = datetime.datetime.fromisoformat("2025-05-13T14:30:45.123456+00:00")

# From Unix timestamp
from_unix = datetime.datetime.fromtimestamp(1715599845.123456, tz=datetime.timezone.utc)
```

### Valid Formats for Langfuse

```python
# All valid:
datetime.datetime.now(datetime.timezone.utc)
datetime.datetime.fromisoformat("2025-05-13T14:30:45.123456+00:00")
datetime.datetime.fromisoformat("2025-05-13T14:30:45.123456Z".replace("Z", "+00:00"))

# Invalid (will cause errors):
"2025-05-13T14:30:45.123456"  # Missing timezone
1715599845.123456  # Unix timestamp (use datetime.fromtimestamp())
"2025-05-13 14:30:45"  # Space instead of T
```

---

## Parameter Summary Table

| Method | Parameter | Type | Required | Purpose |
|--------|-----------|------|----------|---------|
| `start_as_current_span()` | `name` | str | Yes | Span name |
| | `input` | Any | No | Input data |
| | `output` | Any | No | Output data |
| | `metadata` | Dict | No | Custom metadata |
| | `level` | str | No | DEBUG/DEFAULT/WARNING/ERROR |
| `start_as_current_generation()` | `model` | str | No | Model name |
| | `completion_start_time` | datetime | No | TTFT time |
| | All span params | - | - | Same as span |
| `gen.update()` | `completion_start_time` | datetime | No | TTFT for latency calc |
| | `usage_details` | Dict | No | Token counts |
| | `cost_details` | Dict | No | Cost info |
| | `metadata` | Dict | No | Custom metrics |

---

## Important Notes

1. **No Manual Start/End Parameters**: Unlike some SDKs, Langfuse v3 does NOT have `start_time` or `end_time` parameters. Timing is automatic.

2. **ISO 8601 Format**: Always use Python `datetime.datetime` objects. The SDK handles serialization to ISO 8601.

3. **Context Manager is Preferred**: Always use `with` statements for automatic timing and cleanup.

4. **Latency in Milliseconds**: All latency metrics are in milliseconds when retrieved.

5. **Custom Metrics**: Store custom timing metrics in the `metadata` dict for flexibility.

6. **TTFT Only in Generations**: The `completion_start_time` parameter only applies to generation observations.

7. **Automatic Nesting**: Child spans automatically become children of the currently active span.
