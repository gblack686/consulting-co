# Claude Code Auto-Compact: Comprehensive Analysis

**Date**: 2025-12-04
**Sources**:
- [What is Claude Code Auto-Compact](https://claudelog.com/faqs/what-is-claude-code-auto-compact/)
- [Agent SDK Overview](https://platform.claude.com/docs/en/api/agent-sdk/overview)
- [Building agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- Anthropic Quickstarts Repository Analysis

## Overview

**Auto-compact** is Claude Code's automatic context window management system that intelligently summarizes conversations when approaching memory limits, enabling long-running agent sessions without manual intervention.

## The Problem It Solves

**Context Window Exhaustion**: Claude's context window is finite (~200k tokens). Long conversations, especially with:
- Multiple code files
- Extensive tool use
- MCP server integrations
- Multi-session work

...quickly fill the context window, causing:
- Performance degradation
- Loss of working memory
- Session interruptions
- Inability to continue tasks

## How Auto-Compact Works

### Automatic Process

1. **Monitors Context Usage**: Tracks token count approaching limit
2. **Analyzes Conversation**: Identifies key information worth preserving
3. **Creates Summary**: Condenses previous interactions, decisions, and code changes
4. **Replaces Old Messages**: Swaps detailed history with concise summary
5. **Continues Seamlessly**: Agent proceeds with preserved context

### What Gets Preserved vs. Summarized

#### ✅ Preserved (Critical Context)
- **Recent code changes** and file modifications
- **Project structure** and architectural decisions
- **Ongoing task context** and current objectives
- **Key patterns** and naming conventions
- **Active debugging** sessions
- **Unresolved issues** and decisions

#### 📝 Summarized (Historical Context)
- Detailed explanations no longer relevant
- Resolved debugging sessions
- Exploratory discussions without code changes
- Historical context that's been superseded
- Redundant information already captured in code

## Three Context Management Options

### 1. Auto-Compact (Default) ⭐
**When**: Automatic when approaching limits
**Best For**: Hands-off management, most users
**Pros**:
- No manual intervention needed
- Seamless continuation
- Intelligent preservation of key context
**Cons**:
- Less control over what's preserved
- Timing not user-controlled
- Some users find it "opaque" or "error-prone"

**Enable in Claude Agent SDK**:
```python
from claude_code_sdk import Agent

agent = Agent(
    model="claude-sonnet-4-20250514",
    auto_compact=True,  # Enable automatic compaction
    tools=[...]
)
```

### 2. Manual Compact (`/compact`) 🎯
**When**: User decides when to compact
**Best For**: Precise control, logical breakpoints
**Pros**:
- Full control over timing
- Can specify preservation instructions
- Strategic compaction at natural boundaries

**Usage Examples**:
```bash
# Basic manual compact
/compact

# Compact with specific preservation instructions
/compact only keep the names of the websites we reviewed

# Preserve coding patterns
/compact preserve the coding patterns we established

# Keep architectural decisions
/compact keep the architectural decisions and API designs
```

**Strategic Timing**:
- After completing a feature
- Before starting a new major task
- After resolving a complex bug
- At the end of a logical work session

### 3. Clear (`/clear`) 🔄
**When**: Need completely fresh start
**Best For**: New unrelated tasks
**Behavior**: Wipes all context, starts from scratch
**Warning**: Loses ALL conversation history

## Configuration and Settings

### Check Current Configuration

```bash
/config
```

Shows:
- Whether auto-compact is enabled
- Current context usage
- Token count
- Available space

### Managing Context Before Compaction

**Disable Unused MCP Servers** (v2.0.10+):
```bash
/context    # View context usage
/mcp        # List MCP servers

# Disable specific server
/mcp disable <server-name>
```

**Why**: Each MCP server consumes context tokens. Disabling unused servers frees space before compaction is needed.

## Implementation in Anthropic Quickstarts

### Minimal Agent Implementation

From `agents/utils/history_util.py`:

```python
class MessageHistory:
    """Manages chat history with token tracking and context management."""

    def __init__(
        self,
        model: str,
        system: str,
        context_window_tokens: int,
        client: Any,
        enable_caching: bool = True,
    ):
        self.context_window_tokens = context_window_tokens
        self.messages: list[dict[str, Any]] = []
        self.total_tokens = 0
        # ... initialization

    def truncate(self) -> None:
        """Remove oldest messages when context window limit is exceeded."""
        if self.total_tokens <= self.context_window_tokens:
            return

        TRUNCATION_NOTICE = "[Earlier history has been truncated.]"

        # Remove oldest message pairs (user + assistant)
        while (
            self.message_tokens
            and len(self.messages) >= 2
            and self.total_tokens > self.context_window_tokens
        ):
            # Remove oldest pair
            self.messages.pop(0)  # User message
            self.messages.pop(0)  # Assistant message

            # Update token count
            input_tokens, output_tokens = self.message_tokens.pop(0)
            self.total_tokens -= input_tokens + output_tokens

            # Add truncation notice
            if self.messages:
                self.messages[0] = {
                    "role": "user",
                    "content": [{"type": "text", "text": TRUNCATION_NOTICE}]
                }
```

### Key Implementation Details

**Truncation Strategy**:
- Removes oldest **message pairs** (user + assistant together)
- Maintains conversation flow integrity
- Adds truncation notice as first message
- Tracks tokens precisely for accurate management

**Token Tracking**:
```python
async def add_message(self, role: str, content: str, usage: Any | None = None):
    """Track token usage per message"""
    if role == "assistant" and usage:
        total_input = (
            usage.input_tokens
            + usage.cache_read_input_tokens
            + usage.cache_creation_input_tokens
        )
        output_tokens = usage.output_tokens
        self.message_tokens.append((current_turn_input, output_tokens))
        self.total_tokens += current_turn_input + output_tokens
```

**Automatic Invocation**:
```python
async def _agent_loop(self, user_input: str):
    """Agent execution loop with automatic truncation"""
    while True:
        self.history.truncate()  # Called before every API request
        params = self._prepare_message_params()
        response = self.client.messages.create(**params)
        # ... process response
```

## Custom Compaction Strategies

### Strategy 1: Artifact-Based Persistence (Autonomous Coding)

Instead of relying solely on context, persist critical information to files:

```python
# Progress tracking via JSON
{
    "features": [
        {"id": 1, "name": "User login", "status": "passing"},
        {"id": 2, "name": "Dashboard", "status": "in_progress"},
        {"id": 3, "name": "Settings", "status": "not_started"}
    ]
}

# Session notes via text file
"""
Session 3 Progress:
- Implemented user authentication
- Created dashboard layout
- Next: Settings page
"""

# Git commits as memory
git log --oneline
# a1b2c3d Implement user authentication
# d4e5f6g Add dashboard component
```

**Benefits**:
- Context-independent memory
- Survives session restarts
- Human-readable progress tracking
- Version control integration

### Strategy 2: Selective Context Preservation

Only load relevant context for current task:

```python
def get_relevant_context(task: str, history: MessageHistory):
    """Load only context relevant to current task"""
    # Search git history
    relevant_commits = search_commits_for(task)

    # Search feature list
    relevant_features = search_features_for(task)

    # Build focused context
    focused_prompt = f"""
    Task: {task}

    Relevant previous work:
    {relevant_commits}

    Related features:
    {relevant_features}
    """

    return focused_prompt
```

### Strategy 3: Hierarchical Summarization

Summarize at multiple levels:

```python
# Detailed (recent) - Last 5 messages, full detail
# Medium (recent past) - Last 20 messages, key points only
# High-level (distant past) - Everything else, one-line summaries

def hierarchical_compact(messages: list):
    recent = messages[-5:]        # Keep full detail
    medium = messages[-20:-5]     # Summarize to key points
    distant = messages[:-20]      # High-level summary only

    return {
        "recent": recent,
        "medium_summary": summarize_key_points(medium),
        "distant_summary": one_line_summary(distant)
    }
```

### Strategy 4: Domain-Specific Compaction

Custom compaction logic for specific domains:

```python
class CodingCompactor:
    """Preserve code-specific context"""

    def compact(self, messages):
        preserved = {
            "code_changes": extract_code_blocks(messages),
            "file_modifications": extract_file_edits(messages),
            "architectural_decisions": extract_decisions(messages),
            "bugs_fixed": extract_bug_fixes(messages),
            "tests_written": extract_tests(messages)
        }

        # Summarize everything else
        other = summarize_non_code_context(messages)

        return {**preserved, "other_context": other}
```

## Performance Considerations

### Context Window Sizes (as of Dec 2024)

| Model | Context Window | Notes |
|-------|---------------|-------|
| Claude Sonnet 4.5 | 200k tokens | Default for most work |
| Claude Opus 4.5 | 200k tokens | Higher quality reasoning |
| Claude Haiku 4.5 | 200k tokens | Faster, cheaper |

**Token Estimation**:
- 1 token ≈ 4 characters
- Average code file: 500-2000 tokens
- Typical conversation turn: 100-500 tokens

### When Performance Degrades

⚠️ **Warning**: "Claude's performance degrades significantly when working memory is constrained"

**Signs of Context Pressure**:
- Slower responses
- Forgetting recent context
- Repeating questions
- Less coherent outputs
- Tool execution errors

**Proactive Management**:
1. Monitor token usage via `/config`
2. Disable unused MCP servers
3. Manual compact at logical breakpoints
4. Use artifact-based persistence
5. Clear context between unrelated tasks

## Best Practices

### 1. Proactive Compaction
Don't wait for automatic compaction. Compact at logical boundaries:
- ✅ After feature completion
- ✅ Before starting new major work
- ✅ After long debugging sessions
- ✅ Between client projects

### 2. Preserve Critical Context
Use manual compact with specific instructions:
```bash
/compact preserve: API designs, database schema, architectural decisions
```

### 3. Leverage Artifacts
Don't rely solely on conversation context:
- Git commits for code history
- JSON files for structured data
- Text files for session notes
- README for project overview

### 4. MCP Server Hygiene
Regularly audit and disable unused servers:
```bash
/mcp list           # See all servers
/mcp disable <name> # Disable unused ones
```

### 5. Monitor Token Usage
Check context regularly:
```bash
/config  # View current usage
```

### 6. Strategic Clear
For completely unrelated work:
```bash
/clear  # Fresh start, no context baggage
```

## Limitations and Considerations

### Auto-Compact Limitations

**Not Perfect**:
- May lose subtle context
- Timing not always optimal
- Summary quality varies
- Some users report it as "error-prone"

**Opaque Process**:
- Can't see what will be preserved
- No control over summarization quality
- Difficult to debug context loss

**Alternative Approach**:
Some users prefer **manual compaction only** with auto-compact disabled for full control.

### When Not to Rely on Compaction

❌ **Don't use compaction for**:
- Security credentials
- API keys (use environment variables)
- Complex multi-step algorithms (document externally)
- Critical business logic (persist to code)

✅ **Do rely on compaction for**:
- Conversational context
- Recent debugging history
- Exploratory discussions
- Intermediate reasoning

## Comparison: Auto-Compact vs. Manual vs. Artifacts

| Aspect | Auto-Compact | Manual Compact | Artifact-Based |
|--------|--------------|----------------|----------------|
| **Control** | Low | High | Highest |
| **Convenience** | High | Medium | Low |
| **Reliability** | Medium | High | Highest |
| **Transparency** | Low | Medium | High |
| **Survives Restart** | No | No | Yes |
| **Context Pressure** | Handles | Handles | Prevents |
| **Best For** | Quick tasks | Precise control | Long-running |

## Future Enhancements (Speculation)

Potential future features:
- **Customizable compaction rules** - User-defined preservation logic
- **Domain-specific compactors** - Specialized for coding, writing, analysis
- **Compaction previews** - See what will be preserved before compacting
- **Incremental compaction** - Gradual summarization vs. sudden truncation
- **Context snapshots** - Save/restore context states
- **Smart MCP management** - Automatically enable/disable based on usage

## Key Takeaways

1. **Auto-compact is default** - Works automatically for most users
2. **Manual compact gives control** - Better for complex long-running work
3. **Artifacts beat context** - Persistent files > conversation memory
4. **Monitor proactively** - Don't wait for performance degradation
5. **MCP servers matter** - Disable unused servers to free tokens
6. **Compact strategically** - At logical boundaries, not mid-task
7. **Preserve explicitly** - Specify what to keep in manual compacts

## Resources

- [Claude Code Auto-Compact FAQ](https://claudelog.com/faqs/what-is-claude-code-auto-compact/)
- [Agent SDK Overview](https://platform.claude.com/docs/en/api/agent-sdk/overview)
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Long-Running Agent Harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Repository: `claude-repos/anthropic-quickstarts/agents/utils/history_util.py`

## Conclusion

Auto-compact is a powerful feature that enables long-running agent sessions, but it's **not a silver bullet**. The most robust approach combines:

1. **Auto-compact** for basic context management
2. **Manual compaction** at strategic points
3. **Artifact-based persistence** for critical information
4. **Proactive monitoring** of context usage

The Anthropic quickstarts demonstrate that the most sophisticated long-running agents use **explicit persistence** (git + JSON) rather than relying solely on context compaction.
