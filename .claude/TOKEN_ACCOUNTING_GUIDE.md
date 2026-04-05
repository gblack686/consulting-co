# Claude Code Token Accounting Guide

## Understanding Token Types in Langfuse Traces

When you see traces in Langfuse, the token counts include multiple types of tokens from Claude's API response.

## Token Types Explained

### 1. **input_tokens** (Fresh Input)
- Direct input tokens that are NOT cached
- **Billing:** Full price ($3.00 per MTok for Sonnet 4.5)
- **Typical size:** Small (10-50 tokens)
- **Example:** Your latest user message

### 2. **output_tokens** (Response Tokens)
- Tokens in Claude's response
- **Billing:** Full price ($15.00 per MTok for Sonnet 4.5)
- **Typical size:** Varies (100s to 1000s)
- **Example:** Claude's answer and tool calls

### 3. **cache_read_input_tokens** (Cached Input)
- Tokens read from Anthropic's prompt cache
- **Billing:** 90% discount ($0.30 per MTok for Sonnet 4.5)
- **Typical size:** Very large (40,000-150,000+ tokens)
- **Example:** System prompt, conversation history, file contents

### 4. **cache_creation_input_tokens** (Cache Write)
- Tokens written to cache (one-time cost)
- **Billing:** Full price ($3.00 per MTok for Sonnet 4.5)
- **Typical size:** Can be very large (10,000-100,000+ tokens)
- **Example:** First time system prompt is cached

### 5. **thinking_tokens** (Extended Thinking - Optional)
- Tokens used for extended thinking (if enabled)
- **Billing:** Different pricing tier
- **Typical size:** Varies based on thinking depth
- **Example:** Internal reasoning before response

## Understanding the "Total" in Langfuse

When you see a total like **147,496 tokens**, this typically represents:

```
Total = input_tokens + cache_read_input_tokens + output_tokens
```

**Example from actual trace:**
- input_tokens: 14
- cache_read_input_tokens: 140,866
- output_tokens: 7,062
- **Total: 147,942**

**Note:** `cache_creation_input_tokens` is tracked separately as it's a one-time write cost, not part of every request.

## Cost Calculation

Langfuse auto-calculates costs based on:
1. Model name (must be exact: `claude-sonnet-4-5-20250929`)
2. Token types and their respective pricing tiers
3. Cache pricing discounts

**Example cost breakdown:**
```
Input:  14 tokens × $3.00/MTok       = $0.000042
Cache:  140,866 × $0.30/MTok (90% off) = $0.042260
Output: 7,062 × $15.00/MTok          = $0.105930
                                Total = $0.148232
```

## Subagent Token Accounting

When Claude Code spawns subagents (via Task tool), their token usage is **automatically included** in the parent conversation's usage object. You don't need to track them separately.

**Example:**
- User asks Claude to spawn an Explore agent
- Explore agent reads 50 files, uses 100K tokens
- These 100K tokens appear in the main conversation's `cache_read_input_tokens`

## Cache Behavior

### 5-Minute Ephemeral Cache
- Prompt caching uses 5-minute windows
- Reuses cached content if same within 5 minutes
- Huge cost savings on repeated context (system prompt, files, history)

### Cache Breakdown
The `cache_creation` object shows:
```json
{
  "ephemeral_5m_input_tokens": 11629,
  "ephemeral_1h_input_tokens": 0
}
```

Currently only 5-minute caching is used in Claude Code.

## What We Log to Langfuse

Our hook (`log_to_langfuse.py`) extracts and logs:

✅ **All token types** from Claude's usage object
✅ **Actual model name** from transcript
✅ **Cache token types** with proper field names
✅ **Thinking tokens** (if present in future)
✅ **Tool calls** as separate spans

**Usage details structure sent to Langfuse:**
```python
{
  "input": 14,
  "output": 7062,
  "cache_read_input_tokens": 140866,
  "cache_creation_input_tokens": 11629,
  "thinking_tokens": 0  # If extended thinking used
}
```

## Verifying Traces

Use `.claude/check_trace_details.py` to inspect:
- Token counts by type
- Cost calculation
- Model name
- Input/output presence

**Example output:**
```
Model: claude-sonnet-4-5-20250929
Tokens: 14 input + 7062 output = 147942 total
Cost: $0.148232
```

## FAQ

**Q: Why is my total so high (150K+) when I only sent 100 tokens?**
A: The total includes cached tokens (context, system prompt, files). You're only paying full price for ~100 fresh tokens + discounted cache reads.

**Q: Does this include thinking tokens?**
A: Yes, if extended thinking is enabled. They appear as `thinking_tokens` in the usage object. Not present in regular conversations.

**Q: Are subagent tokens tracked separately?**
A: No, they're automatically included in the parent conversation's usage. The main conversation usage object reflects all work done.

**Q: How accurate is the cost calculation?**
A: Very accurate. Langfuse uses the exact model name to look up current Anthropic pricing and applies cache discounts automatically.

---

**Last Updated:** 2025-11-14
**Hook Version:** log_to_langfuse.py with full token type support
