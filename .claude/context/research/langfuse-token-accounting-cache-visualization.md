# Langfuse Token Accounting and Cache Visualization Research Summary

## Overview
Langfuse has made significant improvements to token accounting and cost visualization, particularly around supporting modern LLM pricing models that include cache tokens, audio tokens, and reasoning tokens. This research documents the latest features related to token tracking and visualization.

---

## 1. Token Usage Display in Trace Details

### Flexible Token Type Support
Langfuse now supports **arbitrary usage types** beyond simple input/output tokens. The system intelligently categorizes tokens:

- **Input tokens**: Any usage type with "input" in the key name
- **Output tokens**: Any usage type with "output" in the key name
- **Other custom types**: Audio tokens, reasoning tokens, cache-related tokens, etc.

### Usage Details Structure
When ingesting token data, you can provide multiple usage types with their own costs:

```python
usage_details={
    "input": 10,
    "output": 5,
    "cache_read_input_tokens": 2,
    "some_other_token_count": 10,
    "total": 17,  # optional, automatically calculated if omitted
}
```

### Automatic Calculation
If the `total` is not provided, Langfuse automatically derives it from all ingested usage types.

---

## 2. Cache Token Handling and Visualization

### Separate Cache Token Tracking
Cache tokens are displayed as **distinct usage types** separate from standard input tokens:

- **`cache_read_input_tokens`**: Tracks tokens read from cache
- Displayed independently in trace details UI
- Different pricing tier than regular input tokens (typically lower cost)

### Cache Token in Cost Calculation
Cache tokens are priced separately in cost definitions:

```python
cost_details={
    "input": 1.0,          # Regular input token cost
    "cache_read_input_tokens": 0.5,  # Cache read tokens cost 50% of regular
    "output": 1.0,         # Output token cost
    "total": 2.5,          # optional, auto-calculated
}
```

### OpenAI-Style Cache Token Support
Langfuse supports OpenAI's native cache token schema with automatic mapping:

```python
usage_details={
    "prompt_tokens": 10,
    "completion_tokens": 25,
    "total_tokens": 35,
    "prompt_tokens_details": {
        "cached_tokens": 5,      # Cache tokens mapped to cache_read_input_tokens
        "audio_tokens": 2,       # Audio tokens tracked separately
    },
    "completion_tokens_details": {
        "reasoning_tokens": 15,  # Reasoning tokens tracked separately
    },
}
```

These are automatically flattened with prefixes:
- `prompt_tokens_details.cached_tokens` → `input_cached_tokens`
- `completion_tokens_details.reasoning_tokens` → `output_reasoning_tokens`

---

## 3. Cost Calculation and Visualization

### Two-Tier Cost Tracking Method

#### Method 1: Ingested Cost (Most Accurate)
- **Source**: Directly from LLM provider responses when available
- **Accuracy**: Most accurate as it reflects actual billing
- **When used**: Preferred when LLM API provides cost information

#### Method 2: Inferred Cost (Automatic)
- **Source**: Calculated by Langfuse using model definitions and tokenizers
- **Triggers**: When (1) usage is ingested or inferred AND (2) matching model definition exists
- **Process**: Matches model name via regex pattern, applies configured prices per usage type

### Cost Display in UI

The Langfuse UI displays:
1. **Cost breakdown by usage type**: Each token type shows its individual cost contribution
2. **Total cost per generation**: Sum of all usage type costs
3. **Cost per usage type**: USD calculations for each category (input, output, cache_read_input_tokens, etc.)

### Model Definition Configuration

Custom model definitions allow flexible cost configuration:

```json
{
  "match_pattern": "(?i)^(claude-3-opus)$",  // Regex matching
  "prices": {
    "input": 0.015,
    "output": 0.075,
    "cache_read_input_tokens": 0.00375,  // 25% of input price
    "cache_creation_input_tokens": 0.02,  // 133% of input price
  }
}
```

---

## 4. Model Name Handling

### Model Matching via Regex Patterns
- **Pattern matching**: User-defined and Langfuse-maintained models use regex matching
- **Case insensitive support**: Example: `(?i)^(gpt-4-0125-preview)$`
- **Priority**: User-defined models take priority over Langfuse-maintained models

### Predefined Model Tokenizers
Langfuse includes predefined models with built-in tokenizers:

| Model | Tokenizer | Package | Notes |
|-------|-----------|---------|-------|
| `gpt-4o` | `o200k_base` | `tiktoken` | Latest OpenAI model |
| `gpt*` | `cl100k_base` | `tiktoken` | Previous GPT models |
| `claude*` | `claude` | `@anthropic-ai/tokenizer` | Anthropic models (note: not 100% accurate for Claude 3) |

### Tokenization Configuration
For custom models using OpenAI-style tokenizers:

```json
{
  "tokenizerModel": "gpt-3.5-turbo",  // tiktoken model name
  "tokensPerName": -1,                 // Chatmessage tokenization config
  "tokensPerMessage": 4                // Chatmessage tokenization config
}
```

### Model Definition Management
- **UI method**: Project Settings > Models, add via "+" button
- **API method**: RESTful API endpoints for CRUD operations
  - `GET /api/public/models`
  - `POST /api/public/models`
  - `GET /api/public/models/{id}`
  - `DELETE /api/public/models/{id}`

---

## 5. Recent Trace Visualization Improvements

### Redesigned Trace View (March 2025)
Langfuse introduced significant UI/UX improvements:

**Visual Enhancements:**
- Clearer visual flow of trace and observation hierarchy
- Detailed view of each trace and observation with input/output
- Refined, sophisticated interface design

**Navigation Features:**
1. **Tree/Timeline Toggle**: Switch between chronological and hierarchical views
   - Both views offer equivalent metrics and scores
   - Preserves all information in both modes
2. **Customizable View Settings**: Show/hide controls for:
   - Scores
   - Comments
   - Metrics
   - Color coding support
3. **Powerful Search**: Locate observations by:
   - Type (span, generation, event)
   - ID
   - Name
   - Combined search criteria

### Token and Cost Information Display
The improved trace view displays:
- Tokens per usage type with clear breakdown
- Cost calculations per usage type
- Visual comparison between different token categories
- Cache token differentiation from regular tokens

---

## 6. Key Features for Advanced LLM Pricing Models

### Support for Modern Token Types
Langfuse now handles:
- **Cache tokens**: `cache_read_input_tokens`, `cache_creation_input_tokens`
- **Audio tokens**: `audio_tokens`, `input_audio_tokens`, `output_audio_tokens`
- **Reasoning tokens**: `reasoning_tokens`, `output_reasoning_tokens`
- **Custom tokens**: Any arbitrary token type with custom pricing

### Reasoning Model Considerations
- **Cost inference limitation**: o1-style reasoning models cannot have cost inferred from tokenization
- **Reason**: Reasoning tokens only appear in actual API responses, not in input
- **Solution**: Must manually provide token usage from LLM API response
- **Supported integrations**: OpenAI wrapper, Langchain, LlamaIndex, LiteLLM provide automatic token collection

### December 2024 Cost Tracking Update
Major improvements added support for:
- Arbitrary usage types (not just input/output)
- All modern LLM pricing categories
- Custom pricing per usage type
- More accurate cost calculations for complex pricing models

---

## 7. SDK Integration Examples

### Python SDK - Using Decorator
```python
from langfuse import observe, get_client

langfuse = get_client()

@observe(as_type="generation")
def anthropic_completion(**kwargs):
    response = anthropic_client.messages.create(**kwargs)

    langfuse.update_current_generation(
        usage_details={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
            "cache_read_input_tokens": response.usage.cache_read_input_tokens
        },
        cost_details={
            "input": 1.0,
            "cache_read_input_tokens": 0.5,
            "output": 1.0,
        }
    )
    return response.content[0].text
```

### JavaScript/TypeScript SDK
```typescript
const generation = startObservation(
    "llm-call",
    {
        model: "gpt-4",
        input: [{ role: "user", content: "..." }],
    },
    { asType: "generation" }
);

generation.update({
    usageDetails: {
        input: 10,
        output: 5,
        cache_read_input_tokens: 2,
        total: 17,
    },
    costDetails: {
        input: 1,
        output: 1,
        cache_read_input_tokens: 0.5,
        total: 2.5,
    },
    output: { content: "..." },
});
```

---

## Key Takeaways

1. **Flexible Token Accounting**: Langfuse intelligently handles any token type with automatic categorization and cost calculation
2. **Cache Token Separation**: Cache tokens are displayed distinctly with separate pricing support
3. **Dual Cost Methods**: Supports both ingested (accurate) and inferred (automatic) cost calculations
4. **Modern LLM Support**: Handles complex pricing including audio, reasoning, and cache tokens
5. **Improved Visualization**: Recent trace view redesign provides better hierarchy, search, and customization
6. **Model Definitions**: Regex-based model matching with priority to user-defined models
7. **API-First Design**: Full programmatic access to model definitions and token tracking via REST APIs

