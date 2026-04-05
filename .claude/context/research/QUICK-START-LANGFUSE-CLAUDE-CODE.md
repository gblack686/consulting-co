# Quick Start: Langfuse + Claude Code Integration

**Last Updated**: 2025-11-14
**Estimated Setup Time**: 10 minutes

## The Problem You're Solving

Your Claude Code traces show only 7 seconds, but actual execution includes:
- Multiple tool calls (Bash, Read, Write)
- File operations
- Subprocess executions
- Multiple LLM generations

**Root Cause**: Claude Code emits LOGS (not TRACES), and you're not capturing individual tool executions as timed spans.

## The Solution (3 Steps)

### Step 1: Install claude_telemetry (2 min)

```bash
pip install claude_telemetry
```

### Step 2: Configure Environment (3 min)

Create `.env` file or export these:

```bash
# Your existing keys
export ANTHROPIC_API_KEY="sk-ant-..."
export LANGFUSE_PUBLIC_KEY="lf_pk_..."
export LANGFUSE_SECRET_KEY="lf_sk_..."
export LANGFUSE_HOST="https://cloud.langfuse.com"

# New OTLP configuration for Claude Code tracing
export OTEL_EXPORTER_OTLP_ENDPOINT="https://cloud.langfuse.com/api/public/otel"
export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer ${LANGFUSE_PUBLIC_KEY}"
export OTEL_SERVICE_NAME="claude-agent-system"
export OTEL_LOGS_EXPORTER="none"  # Important: Claude Code logs aren't compatible
export CLAUDE_CODE_ENABLE_TELEMETRY=1
```

### Step 3: Update Your Code (5 min)

**Before** (Missing tool timing):
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4000,
    messages=[{"role": "user", "content": "Analyze the codebase"}]
)
# ❌ Only captures LLM call (7s)
# ❌ Misses Bash commands, file reads, etc.
```

**After** (Captures everything):
```python
import asyncio
from claude_telemetry import run_agent_with_telemetry

async def main():
    result = await run_agent_with_telemetry(
        prompt="Analyze the codebase",
        extra_args={
            "model": "sonnet",
            "max-tokens": "4000"
        }
    )
    return result

asyncio.run(main())
# ✅ Captures LLM calls + tool executions
# ✅ Shows proper breakdown: Bash (2s), Read (1s), LLM (7s), etc.
```

## What You'll See in Langfuse

### Before (Broken)
```
Trace (7s total)
 └─ LLM Generation (7s)
```

### After (Fixed)
```
Trace (14.1s total)
 ├─ user.prompt (event)
 ├─ tool.bash (2.0s) - npm install
 ├─ tool.bash (0.5s) - git status
 ├─ tool.read (0.3s) - package.json
 ├─ tool.read (0.2s) - README.md
 ├─ llm.generation (7.0s) - Analysis
 ├─ tool.write (0.4s) - report.md
 └─ llm.generation (3.7s) - Summary
```

## Verify It Works

1. Run your updated code
2. Go to Langfuse dashboard: https://cloud.langfuse.com
3. Check latest trace
4. Verify you see:
   - ✅ Multiple child spans (not just one)
   - ✅ Each tool call shows duration
   - ✅ Total duration matches wall-clock time

## Common Issues

### Issue: Traces still not showing tool calls

**Cause**: Using direct Anthropic client instead of claude_telemetry

**Fix**: Make sure you're using `run_agent_with_telemetry`, not `client.messages.create`

### Issue: Total duration still wrong

**Cause**: Not using `async`/`await` properly

**Fix**: Ensure your function is `async` and you use `await`:
```python
async def my_function():
    result = await run_agent_with_telemetry(...)  # Must use await
```

### Issue: Flat trace (no nesting)

**Cause**: Threading breaks context propagation

**Fix**: Use `asyncio`, not `ThreadPoolExecutor`

## CLI Usage (Alternative)

Don't want to change code? Use the CLI wrapper:

```bash
# Replace 'claude code' with 'claudia'
claudia "Analyze the project and create a report"

# Pass any flags through
claudia --model opus --max-tokens 8000 "Refactor authentication"
```

## Advanced: Multi-Agent Workflows

```python
from langfuse import observe
from claude_telemetry import run_agent_with_telemetry

@observe(as_type="span")  # Outer span for entire workflow
async def content_pipeline(topic: str):

    # Research agent - creates nested trace
    @observe(as_type="generation")
    async def research():
        return await run_agent_with_telemetry(
            prompt=f"Research {topic}"
        )

    # Writing agent - creates nested trace
    @observe(as_type="generation")
    async def write(research):
        return await run_agent_with_telemetry(
            prompt=f"Write article based on: {research}"
        )

    # Execute pipeline
    research_result = await research()
    final_article = await write(research_result)

    return final_article

# Run it
result = await content_pipeline("AI observability")
```

**Langfuse shows**:
```
content_pipeline (120s)
 ├─ research (60s)
 │   └─ claude.agent.run (59.5s)
 │       ├─ tool.bash (5s) - web search
 │       └─ llm.generation (54.5s)
 └─ write (60s)
     └─ claude.agent.run (59.5s)
         ├─ tool.read (0.5s)
         └─ llm.generation (59s)
```

## Resources

**Full Analysis**: See `LANGFUSE-CLAUDE-CODE-INTEGRATION-ANALYSIS.md` in this directory

**Key Repositories**:
- claude_telemetry: https://github.com/TechNickAI/claude_telemetry
- dev-agent-lens: https://github.com/Teraflop-Inc/dev-agent-lens

**Official Docs**:
- Langfuse OTEL: https://langfuse.com/integrations/native/opentelemetry
- Claude Code Monitoring: https://code.claude.com/docs/en/monitoring-usage

## Need Help?

Check the full analysis document for:
- Detailed architecture diagrams
- Troubleshooting guide
- Performance optimization tips
- Alternative proxy-based approach
- Custom tool instrumentation examples
