# Langfuse Python SDK v3 - Span Latency Research

## Summary of Findings

After researching the Langfuse Python SDK v3 documentation and OpenTelemetry specifications, here are the answers to your questions:

## Question 1: Is there a way to manually set the `latency` field on a span after it's created?

**Answer: NO - Not directly through Langfuse methods.**

The Langfuse SDK does NOT provide a direct `latency` parameter or method to set latency after span creation. However, latency is **automatically calculated** by Langfuse based on span timing.

## Question 2: Can you create a span and then call `.update()` with latency/timing information?

**Answer: NO - `.update()` does NOT have latency parameters.**

The `.update()` method on `LangfuseSpan` and `LangfuseGeneration` has these parameters:

- `input` - Input data
- `output` - Output data
- `metadata` - Additional metadata
- `version` - Version identifier
- `level` - Severity level (DEBUG, DEFAULT, WARNING, ERROR)
- `status_message` - Status message
- `completion_start_time` - **ONLY for generations** (Time to First Token tracking)
- `model` - Model name (generations only)
- `model_parameters` - Model settings (generations only)
- `usage_details` - Token usage (generations only)
- `cost_details` - Cost information (generations only)
- `prompt` - Associated prompt (generations only)

**There is NO `latency`, `start_time`, or `end_time` parameter in `.update()`**

## Question 3: Are there methods like `set_start_time()`, `set_end_time()`, or `set_latency()` on span objects?

**Answer: NO - These methods do NOT exist on LangfuseSpan.**

The Langfuse Span objects do NOT have these methods. Timing is controlled via:
- Span creation timing (automatically recorded)
- The `.end()` method (optionally accepts a timestamp)

## Question 4: What is the exact method signature for creating a span with custom timing?

**Answer: Use `.end(end_time)` parameter - that's the ONLY timing control.**

### Creating a Span:
```python
from langfuse import get_client
from datetime import datetime

langfuse = get_client()

# Create span - timing starts automatically
span = langfuse.start_span(name="my-operation")

# Do work...

# End with optional custom timestamp
span.end(end_time=datetime.now())  # or any datetime
```

### Via Context Manager:
```python
with langfuse.start_as_current_span(name="my-operation") as span:
    # Work happens here
    # Span ends automatically when context exits
    pass
```

## Question 5: Can you pass `latency` directly to span.update()?

**Answer: NO - `latency` is NOT a parameter to `.update()`**

The update() method signature does NOT include latency, start_time, end_time, or duration parameters.

---

## How Latency/Timing Actually Works in Langfuse v3

### Automatic Timing
Langfuse automatically tracks timing by:
1. Recording the start time when `span.start_span()` or `start_as_current_span()` is called
2. Recording the end time when `.end()` is called (or context manager exits)
3. **Calculating latency on the backend** based on these two timestamps

### The Only Timing Control: `.end()` Method

The `.end()` method on both Span and Generation objects accepts an optional `end_time` parameter:

```python
import time
from datetime import datetime
from langfuse import get_client

langfuse = get_client()

span = langfuse.start_span(name="operation")
start = time.time()

# ... do work ...

elapsed = time.time() - start

# Option 1: End with current time (automatic)
span.end()

# Option 2: End with custom timestamp
span.end(end_time=datetime.now())

# Option 3: Calculate and record custom timing
custom_end_time = datetime.fromtimestamp(start + elapsed)
span.end(end_time=custom_end_time)
```

### For Time-to-First-Token (TTFT) on Generations

The ONLY timing-related `.update()` parameter is `completion_start_time` for **generations only**:

```python
import datetime
import time
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_observation(
    as_type="generation",
    name="llm-call"
) as generation:

    # Simulate time to first token
    time.sleep(3)

    # Record when completion started (for TTFT calculation)
    generation.update(
        completion_start_time=datetime.datetime.now(),
        output="LLM response text",
        usage_details={"input_tokens": 5, "output_tokens": 50}
    )

langfuse.flush()
```

---

## Solution: Setting Latency to Reflect Conversation Time Instead of Hook Execution Time

If you need to set latency based on **conversation duration** rather than **function execution time**, here are the solutions:

### Solution 1: Manual End Time Calculation
```python
from datetime import datetime, timedelta
from langfuse import get_client

langfuse = get_client()

# Assume conversation_duration is in seconds
conversation_duration = 120  # 2 minutes

span = langfuse.start_span(name="conversation")

# Start time is captured automatically
# Calculate end time based on conversation duration
conversation_end_time = span.start_time + timedelta(seconds=conversation_duration)

span.end(end_time=conversation_end_time)
```

### Solution 2: Store Timing in Metadata
Since there's no direct latency field, store timing info in metadata for later analysis:
```python
from datetime import datetime, timedelta
from langfuse import get_client

langfuse = get_client()

span = langfuse.start_span(
    name="conversation",
    metadata={
        "conversation_duration_seconds": 120,
        "recorded_at": datetime.now().isoformat()
    }
)

# ... work ...

span.update(
    metadata={
        "actual_hook_execution_time_ms": 50,
        "conversation_wall_clock_time_seconds": 120
    }
)

span.end()
```

### Solution 3: Create Custom Span with Set End Time
```python
from datetime import datetime, timedelta
from langfuse import get_client

langfuse = get_client()

# Get conversation start and end times from your system
conversation_start = datetime(2025, 11, 14, 10, 0, 0)
conversation_end = datetime(2025, 11, 14, 10, 2, 0)  # 2 minutes later

span = langfuse.start_span(name="conversation")

# Simulate the conversation duration by setting custom end time
span.end(end_time=conversation_end)

# Langfuse will calculate latency as: conversation_end - span.start_time
```

---

## OpenTelemetry Property Mapping

From Langfuse's OpenTelemetry integration, the relevant property mapping is:

- `langfuse.observation.completion_start_time` → ISO 8601 date string (generations only)

**Note:** There is NO property for setting span duration or latency directly. Timing is always derived from the span's start and end times.

---

## Key Insights

1. **Latency is NOT explicitly set** - it's calculated from start and end timestamps
2. **The ONLY timing control is `span.end(end_time=...)`**
3. **No `.update()` support for timing** - timing must be set at span creation and/or end
4. **For generations, `completion_start_time` enables TTFT tracking** - this is the only exception
5. **Use metadata for additional timing context** if you need to track both hook execution time and wall-clock conversation time

---

## Code Examples Summary

### Example 1: Basic Span with Custom End Time
```python
from datetime import datetime
from langfuse import get_client

langfuse = get_client()

span = langfuse.start_span(name="api-call")
# ... do work ...
span.end(end_time=datetime.now())
```

### Example 2: Conversation Duration Tracking
```python
from datetime import datetime, timedelta
from langfuse import get_client

langfuse = get_client()

# Record conversation that happened offline
conversation_start = datetime(2025, 11, 14, 10, 0, 0)
conversation_end = datetime(2025, 11, 14, 10, 5, 0)  # 5 minutes

with langfuse.start_as_current_span(
    name="user-conversation",
    metadata={
        "conversation_duration_seconds": (conversation_end - conversation_start).total_seconds()
    }
) as span:
    # Span ends with custom time
    pass

span.end(end_time=conversation_end)
```

### Example 3: Generation with TTFT
```python
from datetime import datetime
import time
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_observation(
    as_type="generation",
    name="llm-inference"
) as gen:

    # Wait for first token
    time.sleep(2)
    ttft_time = datetime.now()

    # Wait for rest of output
    time.sleep(1)

    gen.update(
        completion_start_time=ttft_time,  # ONLY timing field in update()
        output="Full response text",
        usage_details={"input_tokens": 10, "output_tokens": 50}
    )

langfuse.flush()
```

---

## References

- **Langfuse Docs**: https://langfuse.com/docs/observability/sdk/python/instrumentation#updating-observations
- **Advanced Usage**: https://langfuse.com/docs/observability/sdk/python/advanced-usage#passing-completion_start_time-for-ttft-tracking
- **OpenTelemetry Property Mapping**: https://langfuse.com/integrations/native/opentelemetry#property-mapping
- **OpenTelemetry Span API**: https://opentelemetry.io/docs/specs/otel/trace/api/#end

