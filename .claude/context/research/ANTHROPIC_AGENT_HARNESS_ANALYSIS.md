# Anthropic Agent Harness Analysis

**Repository**: `anthropic-quickstarts`
**Cloned to**: `claude-repos/anthropic-quickstarts`
**Date Analyzed**: 2025-12-04
**Source**: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## Overview

Anthropic published a comprehensive engineering blog post and GitHub repository demonstrating their solution to the **long-running agent problem** - enabling AI agents to work on complex tasks that span hours or days across multiple context windows.

## The Core Problem

**Challenge**: AI agents must work in discrete sessions, and each new session begins with no memory of what came before. Because context windows are limited, complex projects cannot be completed within a single window. Agents need a way to bridge the gap between coding sessions.

**Previous Limitations**:
- Agents would "restart from scratch" each session
- No memory of previous work
- Unable to maintain progress across sessions
- Context window exhaustion on long-running tasks

## Anthropic's Solution

### Two-Agent Pattern

Anthropic developed a **two-fold solution** implemented in the Claude Agent SDK:

1. **Initializer Agent** (Session 1)
   - Sets up the environment on first run
   - Creates comprehensive feature/test list
   - Initializes git repository
   - Establishes project structure

2. **Coding Agent** (Sessions 2+)
   - Makes incremental progress in every session
   - Leaves clear artifacts for next session
   - Persists progress via `feature_list.json` and git commits
   - Auto-resumes from where it left off

### Key Innovation: Context Management

The Claude Agent SDK includes:
- **Context compaction** - prevents context window exhaustion
- **Progress persistence** - via git commits and JSON tracking
- **Session bridging** - clear handoffs between sessions
- **Incremental development** - features completed one by one

## Repository Structure

```
anthropic-quickstarts/
├── autonomous-coding/           # Long-running agent harness
│   ├── agent.py                # Agent session logic (206 lines)
│   ├── autonomous_agent_demo.py # Main entry point (116 lines)
│   ├── client.py               # Claude SDK client (122 lines)
│   ├── security.py             # Bash allowlist security (359 lines)
│   ├── progress.py             # Progress tracking (57 lines)
│   ├── prompts.py              # Prompt utilities (37 lines)
│   └── prompts/
│       ├── app_spec.txt        # App specification
│       ├── initializer_prompt.md # First session prompt
│       └── coding_prompt.md    # Continuation prompt
│
├── agents/                     # Minimal agent implementation
│   ├── agent.py               # Core agent logic (173 lines)
│   ├── tools/                 # Tool implementations
│   │   ├── base.py           # Base tool class
│   │   ├── calculator_mcp.py # MCP calculator
│   │   ├── code_execution.py # Code execution
│   │   ├── file_tools.py     # File operations
│   │   ├── mcp_tool.py       # MCP integration
│   │   ├── think.py          # Thinking tool
│   │   └── web_search.py     # Web search
│   └── utils/
│       ├── connections.py    # MCP connections
│       ├── history_util.py   # Message history
│       └── tool_util.py      # Tool utilities
│
├── computer-use-demo/         # Computer control capabilities
├── customer-support-agent/    # Customer support example
└── financial-data-analyst/    # Financial analysis example
```

## Autonomous Coding Agent Deep Dive

### How It Works

**Session 1 (Initialization):**
1. Reads `app_spec.txt` specification
2. Generates `feature_list.json` with 200 test cases
3. Sets up project structure
4. Initializes git repository
5. Creates first commit

**Sessions 2+ (Coding):**
1. Reads `feature_list.json` to see progress
2. Picks next unimplemented feature
3. Implements feature with tests
4. Marks feature as passing in JSON
5. Commits changes to git
6. Auto-continues to next session

### Security Model (Defense-in-Depth)

The autonomous agent implements **three layers of security**:

1. **OS-level Sandbox**: Bash commands in isolated environment
2. **Filesystem Restrictions**: Operations limited to project directory only
3. **Bash Allowlist**: Only specific commands permitted

**Allowed Commands** (from `security.py`):
- **File inspection**: `ls`, `cat`, `head`, `tail`, `wc`, `grep`
- **Node.js**: `npm`, `node`
- **Version control**: `git`
- **Process management**: `ps`, `lsof`, `sleep`, `pkill`

All other commands are **blocked by security hook**.

### Timing Expectations

**⚠️ This is a SLOW process by design:**

- **First session**: Several minutes to generate 200 test cases
- **Each coding iteration**: 5-15 minutes per feature
- **Full application**: Many hours across multiple sessions
- **200 features**: Typical for comprehensive coverage

**Note**: Can be configured for faster demos by reducing feature count in prompts (20-50 features).

### Generated Project Structure

```
my_project/
├── feature_list.json        # Test cases (source of truth)
├── app_spec.txt            # Copied specification
├── init.sh                 # Environment setup
├── claude-progress.txt     # Session notes
├── .claude_settings.json   # Security settings
└── [application files]     # Generated code
```

### Progress Persistence

**Progress tracked via:**
1. **feature_list.json** - Master list with status for each feature
2. **Git commits** - Full version history of all changes
3. **claude-progress.txt** - Human-readable session notes

**Resume capability:**
- Press `Ctrl+C` to pause
- Run same command to resume
- Agent picks up exactly where it left off

## Minimal Agent Implementation

The `agents/` directory contains an **educational reference implementation** showing how to build agents from scratch.

**Key Points:**
- **NOT an SDK** - reference implementation only
- **<300 lines** of core logic
- **Deliberately minimal** - lacks production features
- **Translate to your stack** - patterns over prescription

**Core Components:**
1. **agent.py** - Claude API interactions + tool execution loop
2. **tools/** - Both native tools and MCP tool integration
3. **utils/** - Message history and MCP server connections

**Design Philosophy:**
> "Sophisticated AI behaviors emerge from a simple foundation: LLMs using tools in a loop"

### Supported Tools

**Native Tools:**
- `ThinkTool` - Internal reasoning
- `CodeExecutionTool` - Run code safely
- `FileTools` - File operations
- `WebSearchTool` - Search the web

**MCP Integration:**
- `MCPTool` - Connect to any MCP server
- `CalculatorMCP` - Example MCP calculator

## Key Insights from Anthropic's Blog Post

### 1. Long-Running Problem Statement
Most complex projects cannot be completed within a single context window. Agents need:
- Memory across sessions
- Progress tracking
- Incremental development
- Clear handoffs between sessions

### 2. Solution Components
- **Initializer pattern** - One-time setup with comprehensive planning
- **Coding pattern** - Incremental progress with artifact creation
- **Git persistence** - Version control as memory
- **Feature lists** - Explicit progress tracking

### 3. Context Management
- **Compaction** - Summarize old context to fit in window
- **Selective context** - Only load relevant history
- **Artifact-based** - Use files/commits instead of full context

### 4. Production Considerations
- Security is critical (allowlist, sandboxing, filesystem restrictions)
- Progress must be explicitly persisted
- Sessions should be resumable
- Clear success/failure criteria per feature

## Comparison to Claude Code SDK

| Feature | Claude Agent SDK | This Harness |
|---------|-----------------|--------------|
| **Context Management** | Built-in compaction | Manual via git/JSON |
| **Multi-session** | Automatic | Explicit tracking |
| **Security** | Configurable | Allowlist-based |
| **Code Length** | Production-ready | ~1400 lines total |
| **Purpose** | General-purpose SDK | Educational reference |
| **Tool Support** | Extensive | Minimal set |
| **MCP Integration** | Full support | Reference implementation |

## Usage Examples

### Running Autonomous Coding Agent

```bash
# Set API key
export ANTHROPIC_API_KEY='your-key'

# Run with default settings (200 features, many hours)
python autonomous_agent_demo.py --project-dir ./my_project

# Quick demo (3 iterations only)
python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3

# Custom model
python autonomous_agent_demo.py --project-dir ./my_project --model claude-sonnet-4-5-20250929
```

### Using Minimal Agent

```python
from agents.agent import Agent
from agents.tools.think import ThinkTool
from agents.tools.web_search import WebSearchTool

# Create agent with tools
agent = Agent(
    name="ResearchAgent",
    system="You are a research assistant.",
    tools=[ThinkTool(), WebSearchTool()],
)

# Run the agent
response = agent.run("What are the latest developments in quantum computing?")
print(response)
```

### Adding MCP Servers

```python
agent = Agent(
    name="MCPAgent",
    tools=[ThinkTool()],
    mcp_servers=[
        {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "mcp_server_name"],
        },
    ]
)
```

## Security Best Practices

From `security.py` analysis:

1. **Allowlist approach** - Only permit known-safe commands
2. **Filesystem isolation** - Restrict to project directory
3. **OS sandboxing** - Run in isolated environment
4. **No network access** - Unless explicitly needed
5. **Process limits** - Can only kill dev server processes
6. **Input validation** - All bash commands validated before execution

**Example Security Hook:**
```python
def validate_bash_command(command: str) -> bool:
    """Validate command against allowlist"""
    base_command = command.split()[0]
    return base_command in ALLOWED_COMMANDS
```

## Key Takeaways

### 1. Long-Running Agents Are Now Practical
The two-agent pattern (initializer + coder) solves the multi-session problem.

### 2. Progress Must Be Explicit
Don't rely on context alone - use:
- Git commits
- JSON tracking files
- Clear feature/test lists

### 3. Security Is Non-Negotiable
Autonomous agents need:
- Command allowlists
- Filesystem restrictions
- Sandboxed execution

### 4. Simplicity Works
The core implementation is <300 lines, proving sophisticated behavior emerges from simple foundations.

### 5. Educational Value
This repository teaches fundamentals, not prescriptive patterns. Adapt to your stack.

## Related Resources

**Anthropic Official:**
- [Blog Post: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [Claude Agent SDK Docs](https://docs.claude.com/en/docs/agents-and-tools/claude-code/overview)
- [GitHub: anthropic-quickstarts](https://github.com/anthropics/anthropic-quickstarts)

**Other Repos:**
- [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- [claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)
- [claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos)

## Implementation Ideas for consulting-co

### 1. Adapt for QuickStart Projects
Use the two-agent pattern for QuickStart POC development:
- Initializer: Generate feature list from client requirements
- Coder: Implement features incrementally across sessions

### 2. Security Model Integration
Adopt the three-layer security approach:
- Apply to all autonomous Claude Code agents
- Use allowlist pattern for bash commands
- Restrict filesystem access to project directories

### 3. Progress Tracking Pattern
Implement explicit progress tracking:
- Feature lists in JSON format
- Git commits as memory
- Session notes for human review

### 4. MCP Tool Integration
Study the MCP integration patterns:
- Connect to custom MCP servers
- Build domain-specific tools
- Integrate with existing infrastructure

### 5. Educational Material
Use as training material for team:
- Study minimal agent implementation
- Understand tool execution loops
- Learn context management strategies

## Next Steps

1. **Explore the code**: Study `autonomous-coding/agent.py` and `agents/agent.py`
2. **Run demos**: Test autonomous coding agent with sample projects
3. **Adapt security**: Apply security patterns to existing QuickStart agents
4. **Build tools**: Create domain-specific tools following these patterns
5. **Document learnings**: Share insights with team

## Statistics

- **Total Code**: ~1,400 lines across all components
- **Core Agent Logic**: <300 lines (educational version)
- **Security Implementation**: 359 lines
- **Test Coverage**: 290 lines of security tests
- **Projects Included**: 5 (autonomous coding, agents, computer-use, support, financial)

---

**Conclusion**: This repository demonstrates that long-running autonomous agents are now practical with proper architecture (two-agent pattern), persistence (git + JSON), and security (allowlist + sandboxing). The educational implementation shows sophisticated behavior emerges from simple foundations.
