# Model Tiers Reference

Three tiers for OpenClaw deployments. Use Q15 in the session framework to select.
All models accessed via OpenRouter (`OPENROUTER_API_KEY`).

---

## Tier: Cheap

**When to use**: Hobbyists, experimenters, tight budgets. Good-enough quality for most personal automation.

**Est. cost**: ~$2–15/mo typical usage

| Role | Model | OpenRouter ID | Price (per M tokens) |
|------|-------|--------------|----------------------|
| Brain | DeepSeek V3 | `openrouter/deepseek/deepseek-chat-v3` | $0.27 in / $1.10 out |
| Muscle / Coder | GLM-4-32B | `openrouter/thudm/glm-4-32b` | ~$0.07 in / $0.14 out |
| Subagent default | GLM-4-32B | `openrouter/thudm/glm-4-32b` | same |
| Fallback | Gemini Flash | `openrouter/google/gemini-2.0-flash-001` | $0.10 in / $0.40 out |

> Note: Verify `openrouter/thudm/glm-4-32b` slug at openrouter.ai/models — Zhipu AI model IDs may vary.

### openclaw.json snippet
```json5
model: {
  primary: "openrouter/deepseek/deepseek-chat-v3",
  fallbacks: ["openrouter/thudm/glm-4-32b"],
},
subagents: {
  model: "openrouter/thudm/glm-4-32b",
},
```

---

## Tier: Mid

**When to use**: Small teams, active daily use, clients who want reliable quality without breaking the bank.

**Est. cost**: ~$20–60/mo typical usage

| Role | Model | OpenRouter ID | Price (per M tokens) |
|------|-------|--------------|----------------------|
| Brain | Gemini 2.0 Flash | `openrouter/google/gemini-2.0-flash-001` | $0.10 in / $0.40 out |
| Muscle / Coder | DeepSeek V3 | `openrouter/deepseek/deepseek-chat-v3` | $0.27 in / $1.10 out |
| Subagent default | DeepSeek V3 | `openrouter/deepseek/deepseek-chat-v3` | same |
| Fallback | GLM-4-32B | `openrouter/thudm/glm-4-32b` | ~$0.07 in / $0.14 out |

**Why Gemini Flash as brain**: Fastest inference, handles long context well (1M window), great for orchestration. DeepSeek V3 as coder is best-in-class for coding tasks at this price.

### openclaw.json snippet
```json5
model: {
  primary: "openrouter/google/gemini-2.0-flash-001",
  fallbacks: ["openrouter/deepseek/deepseek-chat-v3"],
},
subagents: {
  model: "openrouter/deepseek/deepseek-chat-v3",
},
```

---

## Tier: Pro (Intelligent Routing — No Claude Tax)

**When to use**: Power users, business-critical workflows, clients who need near-Claude quality without $15/M output costs.

**Est. cost**: ~$50–200/mo depending on usage volume

**Strategy**: No single model. Route by task type. Gemini 2.5 Pro orchestrates, DeepSeek R1 handles reasoning, DeepSeek V3 handles coding/execution.

| Role | Model | OpenRouter ID | Price (per M tokens) |
|------|-------|--------------|----------------------|
| Orchestrator / Brain | Gemini 2.5 Pro | `openrouter/google/gemini-2.5-pro-preview` | ~$1.25 in / $5.00 out |
| Reasoning / Analysis | DeepSeek R1 | `openrouter/deepseek/deepseek-r1` | $0.55 in / $2.19 out |
| Coding / Execution | DeepSeek V3 | `openrouter/deepseek/deepseek-chat-v3` | $0.27 in / $1.10 out |
| Fallback | Gemini Flash | `openrouter/google/gemini-2.0-flash-001` | $0.10 in / $0.40 out |

> Why not Claude: Claude Sonnet 4.5 costs ~$3/M in, $15/M out. Gemini 2.5 Pro achieves similar results at ~1/3 the output cost. DeepSeek R1 matches Claude for reasoning tasks at ~1/7 the cost.

### Routing Pattern

Route each domain agent to the model that fits its job:

```json5
// Main agent (orchestrator) — Gemini 2.5 Pro
{
  id: "main",
  model: "openrouter/google/gemini-2.5-pro-preview",
}

// Code-heavy domain — DeepSeek V3
{
  id: "dev-agent",
  model: "openrouter/deepseek/deepseek-chat-v3",
}

// Analysis/research domain — DeepSeek R1
{
  id: "research-agent",
  model: "openrouter/deepseek/deepseek-r1",
}
```

### openclaw.json defaults snippet
```json5
model: {
  primary: "openrouter/google/gemini-2.5-pro-preview",
  fallbacks: [
    "openrouter/deepseek/deepseek-r1",
    "openrouter/google/gemini-2.0-flash-001",
  ],
},
subagents: {
  model: "openrouter/deepseek/deepseek-chat-v3",  // coding/muscle tasks
},
```

---

## Quick Selection Guide

Ask Q15 from session-framework.md, then use this decision tree:

```
"Monthly AI budget?"
  < $20    → Cheap tier
  $20–$100 → Mid tier
  > $100   → Pro tier (intelligent routing)
  Unlimited → Pro tier with usage caps

"Priority: cost vs quality?"
  Cost     → Cheap
  Balance  → Mid
  Quality  → Pro

"Use case complexity?"
  Personal tasks / scheduling  → Cheap or Mid
  Business workflows / coding  → Mid or Pro
  Financial decisions / complex reasoning → Pro
```

---

## Model ID Quick Reference

| Provider | Model | OpenRouter ID |
|----------|-------|--------------|
| DeepSeek | Chat V3 (coder/general) | `openrouter/deepseek/deepseek-chat-v3` |
| DeepSeek | R1 (reasoning) | `openrouter/deepseek/deepseek-r1` |
| Google | Gemini 2.0 Flash (fast/cheap) | `openrouter/google/gemini-2.0-flash-001` |
| Google | Gemini 2.5 Pro (quality) | `openrouter/google/gemini-2.5-pro-preview` |
| Zhipu AI | GLM-4-32B (cheap coder) | `openrouter/thudm/glm-4-32b` |
| Qwen | Qwen 2.5 72B (alt mid) | `openrouter/qwen/qwen-2.5-72b-instruct` |
| Anthropic | Claude Sonnet 4.5 (premium) | `openrouter/anthropic/claude-sonnet-4-5` |

Browse current pricing: https://openrouter.ai/models
