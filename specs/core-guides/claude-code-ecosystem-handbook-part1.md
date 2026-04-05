# Claude Code Ecosystem Handbook

> The Complete Guide to Building Agentic AI Systems with Claude Code
> For Consultants, Developers, and AI Engineers
> Version 1.0 | November 2025

---

## Table of Contents

### Part I: Understanding the Ecosystem
- [Chapter 1: The Three Components](#chapter-1-the-three-components)
- [Chapter 2: Permission Modes](#chapter-2-permission-modes)
- [Chapter 3: Configuration System](#chapter-3-configuration-system)

### Part II: The Primitives System
- [Chapter 4: Commands (Slash Commands)](#chapter-4-commands-slash-commands)
- [Chapter 5: Agents (Subagents)](#chapter-5-agents-subagents)
- [Chapter 6: Hooks (Event-Driven Automation)](#chapter-6-hooks-event-driven-automation)
- [Chapter 7: Skills (Reusable Capabilities)](#chapter-7-skills-reusable-capabilities)
- [Chapter 8: Tools & MCP](#chapter-8-tools--mcp)

### Part III: Configuration Reference
- [Chapter 9: settings.json Complete Reference](#chapter-9-settingsjson-complete-reference)
- [Chapter 10: Agent Configuration Reference](#chapter-10-agent-configuration-reference)
- [Chapter 11: Command Configuration Reference](#chapter-11-command-configuration-reference)
- [Chapter 12: Hook Configuration Patterns](#chapter-12-hook-configuration-patterns)

### Part IV: Patterns & Best Practices
- [Chapter 13: Real-World Patterns](#chapter-13-real-world-patterns)
- [Chapter 14: Security & Permissions](#chapter-14-security--permissions)
- [Chapter 15: Observability & Logging](#chapter-15-observability--logging)

### Part V: Building .claude Repositories
- [Chapter 16: Repository Structure](#chapter-16-repository-structure)
- [Chapter 17: Boilerplate Templates](#chapter-17-boilerplate-templates)
- [Chapter 18: Team Workflows](#chapter-18-team-workflows)

### Appendices
- [Appendix A: CLI Quick Reference](#appendix-a-cli-quick-reference)
- [Appendix B: settings.json Full Schema](#appendix-b-settingsjson-full-schema)
- [Appendix C: Common Patterns Library](#appendix-c-common-patterns-library)
- [Appendix D: Troubleshooting Guide](#appendix-d-troubleshooting-guide)

---

# Part I: Understanding the Ecosystem

## Chapter 1: The Three Components

Claude Code provides three ways to interact with Claude AI:

### 1.1 CLI (Command Line Interface)

**What it is:** The `claude` command-line tool for interactive development.

**Best for:**
- Interactive development sessions
- Code review and planning
- Rapid prototyping
- Local development workflows

**How to start:**
```bash
claude                           # Interactive session
claude --permission-mode plan    # Analysis only
claude --continue                # Continue last conversation
```

**Key features:**
- Interactive sessions with conversation history
- Four permission modes (plan, default, acceptEdits, bypassPermissions)
- Session management (continue, resume, fork)
- Custom commands and subagents
- Hook system for automation

### 1.2 SDK (Agent Software Development Kit)

**What it is:** Framework for building custom AI agents in TypeScript or Python.

**Best for:**
- Production AI systems
- Custom agent workflows
- Enterprise integrations
- Programmatic control

**How to start:**
```typescript
// TypeScript
import { Agent } from '@anthropic-ai/agent-sdk';

const agent = new Agent({
  apiKey: process.env.ANTHROPIC_API_KEY,
  model: 'claude-sonnet-4-5-20250929',
});
```

```python
# Python
from anthropic_sdk import Agent

agent = Agent(
    api_key=os.environ['ANTHROPIC_API_KEY'],
    model='claude-sonnet-4-5-20250929'
)
```

**Key features:**
- Full programmatic control
- Custom tool integration
- Context management
- Production-ready error handling

### 1.3 API (Anthropic API)

**What it is:** Direct HTTP API access to Claude models.

**Best for:**
- Maximum control and customization
- Non-standard workflows
- Integration with existing systems
- Custom UI/UX

**How to start:**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, Claude"}]
  }'
```

**Key features:**
- Complete flexibility
- Lowest-level access
- Custom implementations
- No framework overhead

### 1.4 Decision Matrix

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Code review | **CLI** (plan mode) | Safe analysis without modifications |
| Feature development | **CLI** (acceptEdits) | Interactive with conversation history |
| Production agent | **SDK** | Production-ready framework |
| Custom UI integration | **API** | Maximum control |
| CI/CD automation | **CLI** (bypassPermissions) or **SDK** | Depends on complexity |
| Learning/exploration | **CLI** (plan mode) | Safe environment |

---

## Chapter 2: Permission Modes

Permission modes control how Claude interacts with your codebase and tools. This is **exclusive to the CLI**.

### 2.1 The Four Modes

#### Plan Mode (`--permission-mode plan`)

**Capabilities:**
- ✅ Read files
- ✅ Search codebase
- ✅ Analyze architecture
- ✅ Answer questions
- ✅ Create plans
- ❌ **Cannot modify files**
- ❌ **Cannot execute commands**

**Use cases:**
- Code reviews
- Architecture analysis
- Planning sessions
- Learning unfamiliar codebases
- Production environment exploration

**Example:**
```bash
claude --permission-mode plan "Analyze the authentication system for security issues"
```

#### Default Mode (`--permission-mode default`)

**Capabilities:**
- ✅ Everything plan mode can do
- ✅ Modify files (prompts for permission first time)
- ✅ Execute commands (prompts for permission first time)
- 🔐 Prompts once per tool type

**Use cases:**
- General development
- Balanced security and convenience
- Shared development environments

**Example:**
```bash
claude --permission-mode default "Fix the authentication bug"
```

#### Accept Edits Mode (`--permission-mode acceptEdits`)

**Capabilities:**
- ✅ Everything default mode can do
- ✅ **Auto-accepts file edit permissions**
- ⚠️ Still prompts for dangerous commands

**Use cases:**
- Active development sessions
- Refactoring
- Rapid prototyping
- Trusted environments

**Example:**
```bash
claude --permission-mode acceptEdits "Refactor the user module"
```

#### Bypass Permissions Mode (`--permission-mode bypassPermissions`)

**Capabilities:**
- ✅ Everything with **NO prompts**
- ⚠️ Maximum risk

**Use cases:**
- CI/CD automation
- Sandboxed environments
- Scripts and pipelines

**Example:**
```bash
claude --permission-mode bypassPermissions "Run full test suite and fix all failures"
```

### 2.2 Permission Mode Comparison

| Feature | plan | default | acceptEdits | bypassPermissions |
|---------|------|---------|-------------|-------------------|
| Read files | ✅ | ✅ (prompt 1st) | ✅ | ✅ |
| Search code | ✅ | ✅ (prompt 1st) | ✅ | ✅ |
| Edit files | ❌ | ✅ (prompt each) | ✅ (auto) | ✅ |
| Run commands | ❌ | ✅ (prompt each) | ✅ (prompt) | ✅ |
| Delete files | ❌ | ✅ (prompt each) | ✅ (prompt) | ✅ |
| Safety level | 🔒 Highest | 🔐 High | ⚠️ Medium | ⚠️ Low |
| Prompts | None | First use | Edits auto | None |

### 2.3 Two-Phase Workflow Pattern

**Recommended approach for complex tasks:**

```bash
# Phase 1: Plan (safe analysis)
claude --permission-mode plan "Design solution for user authentication"
# [Review plan, discuss, validate approach]

# Phase 2: Implement (execute plan)
claude --permission-mode acceptEdits --continue "Implement the authentication plan"
```

**Benefits:**
- Safe exploration before making changes
- Clear separation of planning and execution
- Conversation history preserved
- Reduced risk of mistakes

