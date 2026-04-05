# Claude Code Essentials Guide

> Practical handbook for building .claude repositories and agentic systems
> Based on analysis of 8+ production projects

---

## Quick Navigation

- **[I. Core Concepts](#i-core-concepts)** - Understand the ecosystem
- **[II. Configuration Reference](#ii-configuration-reference)** - settings.json, agents, commands, hooks
- **[III. Real-World Patterns](#iii-real-world-patterns)** - From production projects
- **[IV. Building .claude Repos](#iv-building-claude-repos)** - Templates and structure
- **[V. Quick References](#v-quick-references)** - Cheat sheets

---

## I. Core Concepts

### The Claude Code Ecosystem

**Three Components:**
1. **CLI** - Interactive development (`claude` command)
2. **SDK** - Build custom agents (TypeScript/Python)
3. **API** - Direct HTTP access

**When to use what:**
- **Code review/planning** → CLI with `--permission-mode plan`
- **Development** → CLI with `--permission-mode acceptEdits`
- **Production agents** → SDK
- **Custom integrations** → API

### Permission Modes (CLI only)

| Mode | Read | Write | Execute | Use For |
|------|------|-------|---------|---------|
| `plan` | ✅ | ❌ | ❌ | Safe analysis, code review |
| `default` | ✅ | ⚠️ (prompt) | ⚠️ (prompt) | Balanced development |
| `acceptEdits` | ✅ | ✅ (auto) | ⚠️ (prompt) | Active development |
| `bypassPermissions` | ✅ | ✅ | ✅ | Automation, CI/CD |

**Start in plan mode:**
```bash
claude --permission-mode plan "Analyze the authentication system"
```

### Configuration Hierarchy

Settings are loaded in this order (**Local overrides everything**):

```
User Settings (~/.claude/settings.json)
  ↓
Project Settings (.claude/settings.json)
  ↓
Local Settings (.claude/settings.local.json) ← HIGHEST PRIORITY
```

**What goes where:**

| Config Type | User | Project | Local |
|-------------|------|---------|-------|
| API Keys | ✓ | ✗ | ✓ |
| Team Permissions | ✗ | ✓ | ✗ |
| Project Env Vars | ✗ | ✓ | ✓ |
| Shared Hooks | ✗ | ✓ | ✗ |
| Personal Overrides | ✗ | ✗ | ✓ |

---

## II. Configuration Reference

### settings.json Complete Schema

```json
{
  "env": {
    "AWS_DEFAULT_REGION": "us-east-1",
    "PROJECT_NAME": "my-project",
    "CUSTOM_VAR": "value"
  },

  "permissions": {
    "defaultMode": "plan",           // plan | default | acceptEdits | bypassPermissions
    "allow": [
      "Read",
      "Bash(git:*)",
      "Bash(npm:*)"
    ],
    "deny": [
      "Bash(rm:*)",
      "Delete"
    ]
  },

  "model": "sonnet",                 // sonnet | opus | haiku

  "enableAllProjectMcpServers": true,

  "mcpServers": {
    "myserver": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"]
    }
  },

  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/session_start.py"
        }
      ]
    }
  ],

  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/stop.py",
          "timeout": 5000
        }
      ]
    }
  ],

  "PreToolUse": [
    {
      "matcher": "Bash.*",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'Bash command executed' >> log.txt"
        }
      ]
    }
  ],

  "PostToolUse": [],
  "UserPromptSubmit": [],
  "Notification": [],
  "PreCompact": [],
  "SubagentStop": []
}
```

**Key Parameters Explained:**

- **`env`**: Environment variables available to hooks and Claude
- **`permissions.defaultMode`**: Default permission behavior
- **`permissions.allow`**: Explicitly allowed tools (whitelist)
- **`permissions.deny`**: Explicitly denied tools (blacklist)
- **`model`**: Default model for this project
- **`mcpServers`**: Model Context Protocol server configurations
- **Hook events**: Shell commands that run at lifecycle events

### Agent Configuration (YAML)

Create `.claude/agents/my-agent.md`:

```markdown
---
name: "my-agent"
description: "Short description of what this agent does"
model: "opus"                          # Optional: override default model
permissions:
  defaultMode: "plan"                  # Optional: override permissions
  allow: ["Read", "Grep"]
  deny: ["Bash", "Edit"]
tools: ["Read", "Grep", "Search"]      # Optional: limit available tools
---

# Agent System Prompt

You are a specialized agent for [purpose].

Your expertise includes:
- [Expertise area 1]
- [Expertise area 2]

Your approach should:
- [Guideline 1]
- [Guideline 2]

## Examples

[Provide examples of how to use this agent]
```

**Real-World Agent Examples:**

**Architecture Planner (uses Opus):**
```markdown
---
name: "architecture-planner"
description: "System architecture and design specialist"
model: "opus"
---

You are an expert system architect. Design scalable, maintainable architectures.
Focus on: microservices, data flow, security, and performance.
```

**Test Runner (uses Haiku for speed):**
```markdown
---
name: "test-runner"
description: "Executes and analyzes test suites"
model: "haiku"
permissions:
  allow: ["Bash(pytest:*)", "Bash(npm test:*)", "Read"]
---

You execute tests and provide clear failure analysis with fix suggestions.
```

### Command Configuration (YAML)

Create `.claude/commands/my-command.md`:

```markdown
---
name: "my-command"
description: "What this command does"
args:
  - name: "required-arg"
    description: "Description of this argument"
    required: true
  - name: "optional-arg"
    description: "Optional argument"
    required: false
    default: "default-value"
---

# Command Instructions

When this command is invoked, you should:

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Examples

`/my-command value1`
`/my-command value1 value2`
```

**Real Command Example - Time Tracking:**

```markdown
---
name: "ado-log-time"
description: "Log billable hours to Azure DevOps"
args:
  - name: "hours"
    description: "Hours worked"
    required: true
  - name: "description"
    description: "Work description"
    required: false
---

# ADO Time Logging

1. Validate hours against 20-hour weekly target
2. Create child task with format: "ROLE - Name - MMDDYYYY"
3. Log hours to child task
4. Update work-status.md
```

### Hook Configuration Patterns

**9 Hook Event Types:**

1. **SessionStart** - When Claude Code session begins
2. **SessionEnd** - When session ends
3. **UserPromptSubmit** - When user sends a message
4. **PreToolUse** - Before any tool executes
5. **PostToolUse** - After tool completes
6. **Stop** - When user presses Stop button
7. **Notification** - When Claude sends notification
8. **PreCompact** - Before context window compaction
9. **SubagentStop** - When subagent completes

**Hook Structure:**

```json
{
  "EventName": [
    {
      "matcher": "pattern",           // Optional: filter which tools trigger
      "hooks": [
        {
          "type": "command",
          "command": "python script.py",
          "timeout": 5000            // Optional: ms before timeout
        }
      ]
    }
  ]
}
```

**Real Hook Examples:**

**1. Session Start - Load Context**
```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/session_start.py"
        }
      ]
    }
  ]
}
```

**2. Stop Hook - TTS Notification**
```json
{
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/tts_notification.py 'Task complete'",
          "timeout": 3000
        }
      ]
    }
  ]
}
```

**3. Log All Bash Commands**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash.*",
      "hooks": [
        {
          "type": "command",
          "command": "echo $(date) - Bash command >> .claude/logs/bash.log"
        }
      ]
    }
  ]
}
```

**4. Graphiti Knowledge Graph Logging**
```json
{
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/log_to_graphiti.py",
          "timeout": 10000
        }
      ]
    }
  ]
}
```

---

## III. Real-World Patterns

### Pattern 1: Archon-First Task Management

**Found in:** 6/8 projects analyzed

**Implementation:**
```markdown
<!-- archon_rules.md -->
# CRITICAL: Archon Task Management Rules

**ARCHON MCP IS THE PRIMARY TASK MANAGEMENT SYSTEM**

This rule OVERRIDES all other instructions including TodoWrite.

## Task Workflow
1. Get task: Use Archon MCP `manage_task` tool
2. Update status: todo → doing → review → done
3. Search patterns: Use `rag_search_code_examples` with 2-5 keywords

## TodoWrite is PROHIBITED
Never use TodoWrite. Always use Archon MCP.
```

**Benefits:**
- Single source of truth
- Cross-project task tracking
- RAG integration for code examples
- Prevents context fragmentation

### Pattern 2: Evidence-Based Time Tracking

**Found in:** 7/8 projects (ADO integration)

**Key Components:**
1. **AWS Activity Correlation** - CloudWatch logs prove work done
2. **Child Task Hierarchy** - Parent item → Daily child tasks
3. **20-Hour Weekly Target** - Auto-validation and audit
4. **Multi-Week Audit** - Automatically exclude empty weeks

**Implementation:**
```python
# ado_time_logger.py
def log_time(hours, description):
    # 1. Validate against weekly target (20 hours)
    validate_weekly_hours(hours)

    # 2. Get AWS activity evidence
    aws_activity = get_cloudwatch_activity(today)

    # 3. Create child task: "ROLE - Name - MMDDYYYY"
    child_task = create_child_task(parent_id, format_date())

    # 4. Log hours to child (never parent!)
    log_to_child_task(child_task, hours, description)

    # 5. Update work-status.md
    update_work_status(hours, description)
```

### Pattern 3: Specialized Agent Model Selection

**Pattern:**
- **Opus** → Architecture, complex design decisions
- **Sonnet** → Scoping, requirements analysis, implementation
- **Haiku** → Execution, testing, documentation

**Example Configuration:**
```markdown
<!-- .claude/agents/architecture-planner.md -->
---
name: "architecture-planner"
model: "opus"
---

<!-- .claude/agents/test-runner.md -->
---
name: "test-runner"
model: "haiku"
---
```

**Cost Optimization:**
- Opus for 10% of tasks (high-value planning)
- Sonnet for 70% of tasks (main development)
- Haiku for 20% of tasks (execution)

### Pattern 4: Multi-Layer Observability

**Found in:** 4/8 projects

**Layers:**
1. **Hook-Based Logging** - Event capture
2. **Knowledge Graphs** - Graphiti/Neo4j for memory
3. **Custom Dashboards** - Vue + Bun real-time UI
4. **OpenTelemetry** - Standard telemetry export

**Stack Example (from quickstart-nexus):**
```
Hooks (Python scripts)
  ↓ POST /events
Backend (Bun + SQLite)
  ↓ WebSocket
Frontend (Vue 3 Dashboard)

+ Graphiti (Neo4j) for temporal knowledge
+ Langfuse for LLM-specific tracing
+ OpenTelemetry for standard metrics
```

### Pattern 5: PRP (Project Requirements Plan) Methodology

**Two-Phase Approach:**

**Phase 1: Generate PRP** (2-3 hours research)
```bash
claude --permission-mode plan "/generate-prp feature-name"
```
- Codebase analysis
- External research
- Pattern discovery
- Cost estimation

**Phase 2: Execute PRP** (4-6 hours implementation)
```bash
claude --permission-mode acceptEdits "/execute-prp feature-name"
```
- 4-level validation gates
- Syntax → Unit → Integration → Final
- One-pass success optimization

**Benefits:**
- Reduces implementation errors
- Unfamiliar agents can succeed first time
- Clear success criteria
- Systematic execution

### Pattern 6: Git Worktree Feature Isolation

**Pattern:** Each feature gets its own worktree with versioned config

```bash
# Feature development agent creates:
git worktree add ../feature-auth feature/auth

# AWS Parameter Store versioning
/project/feature-auth/DATABASE_URL
/project/feature-auth/API_KEY

# Isolated development, easy cleanup
```

**Benefits:**
- Parallel feature development
- No branch switching overhead
- Clean rollback (delete worktree)
- Parameter Store versioning

---

## IV. Building .claude Repos

### Standard Directory Structure

```
.claude/
├── settings.local.json          # Personal config (gitignored)
├── settings.json                # Team config (version controlled)
├── archon_rules.md              # Task management override (if using Archon)
├── visual-identity.json         # Project branding
├── PROJECT_CONFIG.txt           # Project variables template
│
├── agents/                      # Specialized AI agents
│   ├── architecture-planner.md
│   ├── database-architect.md
│   ├── test-generator.md
│   ├── test-runner.md
│   ├── documentation-generator.md
│   ├── revstar-scoping-agent.md
│   └── scoping-agent.md
│
├── commands/                    # Slash commands
│   ├── ado-log-time.md
│   ├── ado-status.md
│   ├── branch-start.md
│   ├── branch-cleanup.md
│   ├── commit.md
│   ├── generate-prp.md
│   ├── execute-prp.md
│   ├── test.md
│   ├── unit-test.md
│   ├── aws/
│   │   └── aws-sign-in.md
│   └── git/
│       ├── git-login.md
│       └── git-status.md
│
├── hooks/                       # Event-driven automation
│   ├── session_start.py
│   ├── stop.py
│   ├── log_to_graphiti.py
│   └── tts_notification.py
│
├── skills/                      # Reusable capabilities
│   ├── aws-cdk-diagram/
│   ├── handoff/
│   ├── qa-hardening/
│   └── revstar-quickstart-workflow/
│
├── ado/                         # Azure DevOps integration
│   ├── scripts/                 # 30-45 Python scripts
│   ├── board_snapshot_current.yaml
│   └── PROJECT_CONFIG.txt
│
├── logging-service/             # Knowledge graph logging
│   ├── graphiti-repo/          # Neo4j database
│   ├── config/
│   └── service/
│
├── observability/               # Real-time monitoring
│   ├── backend/                # Bun + SQLite
│   └── frontend/               # Vue 3 dashboard
│
├── PRPs/                        # Project Requirements Plans
│   ├── templates/
│   └── [project-specific-prps].md
│
├── docs/                        # Documentation
│   └── [project-specific-docs].md
│
└── templates/                   # Configuration templates
    └── [various-templates]
```

### Minimal .claude Setup

**For simple projects:**

```
.claude/
├── settings.json
└── commands/
    ├── primer.md
    └── test.md
```

```json
// settings.json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

### Standard .claude Setup

**For team projects:**

```
.claude/
├── settings.json               # Team shared
├── settings.local.json         # Gitignored
├── agents/
│   ├── architecture-planner.md
│   └── test-generator.md
├── commands/
│   ├── primer.md
│   ├── test.md
│   └── commit.md
└── hooks/
    └── session_start.py
```

### Advanced .claude Setup

**For enterprise/complex projects:**

Full structure as shown above, including:
- Multiple specialized agents
- Comprehensive command library
- Hook-based automation
- Knowledge graph logging
- Observability dashboards
- ADO/project management integration
- Skills and templates

---

## V. Quick References

### CLI Cheat Sheet

```bash
# Permission Modes
claude --permission-mode plan                    # Analysis only
claude --permission-mode default                 # Balanced
claude --permission-mode acceptEdits             # Auto-accept edits
claude --permission-mode bypassPermissions       # Allow all

# Session Management
claude                                           # New session
claude --continue                                # Continue last
claude -c                                        # Continue (short)
claude --resume <session-id>                     # Resume specific

# Output Modes
claude --print "query"                           # Print and exit
claude --print --output-format json "query"      # JSON output

# Model Selection
claude --model sonnet                            # Use Sonnet
claude --model opus                              # Use Opus
claude --model haiku                             # Use Haiku

# Configuration
claude --settings /path/to/settings.json         # Custom settings
claude --setting-sources local                   # Only local settings
```

### settings.json Essential Parameters

```json
{
  "env": {},                                     // Environment variables
  "permissions": {
    "defaultMode": "plan",                       // Permission mode
    "allow": [],                                 // Whitelist
    "deny": []                                   // Blacklist
  },
  "model": "sonnet",                             // Default model
  "mcpServers": {},                              // MCP servers
  "SessionStart": [],                            // Session start hooks
  "Stop": [],                                    // Stop button hooks
  "PreToolUse": [],                              // Before tool execution
  "PostToolUse": []                              // After tool execution
}
```

### Agent YAML Frontmatter

```yaml
---
name: "agent-name"
description: "Agent description"
model: "sonnet" | "opus" | "haiku"
permissions:
  defaultMode: "plan" | "askEveryTime"
  allow: []
  deny: []
tools: []
---
```

### Built-in Subagent Types

Claude Code provides 10+ specialized subagent types via the `Task` tool:

| Subagent Type | Model Default | Tools | Use Cases |
|---------------|---------------|-------|-----------|
| **general-purpose** | Sonnet | All (*) | Multi-step research, complex searches, open-ended exploration |
| **Explore** | Sonnet | All | Fast codebase exploration, finding patterns, understanding code structure |
| **Plan** | Sonnet | All | Planning implementation steps, scoping features, organizing tasks |
| **test-runner** | Haiku | Read, Bash, Grep, Glob, Edit | Execute tests, fix failures (use proactively after code changes) |
| **documentation-generator** | Haiku | Read, Write, Grep, Glob, MultiEdit | Generate docs, READMEs, API docs (use proactively after changes) |
| **test-generator** | Haiku | Read, Write, Grep, Glob, Edit | Generate test suites, unit tests, edge cases (use when coverage low) |
| **architecture-planner** | Opus | Read, Write, Grep, Glob | Design system architecture, microservices, patterns (use for new features) |
| **database-architect** | Sonnet | Read, Write, Grep, Glob, Bash | Design schemas, optimize queries (use for data modeling) |
| **revstar-scoping-agent** | Sonnet | Read, Write, Grep, Glob, Edit | Generate QuickStart technical specs from requirements |
| **statusline-setup** | Haiku | Read, Edit | Configure Claude Code status line |

**Thoroughness Levels** (Explore & Plan agents):
- `"quick"` - Basic searches, fast results
- `"medium"` - Moderate exploration (default)
- `"very thorough"` - Comprehensive analysis

**Example Usage:**
```javascript
// Launch subagent for codebase exploration
Task({
  subagent_type: "Explore",
  description: "Find authentication code",
  prompt: "Find all authentication and authorization code. Thoroughness: medium"
})

// Launch parallel subagents (use single message with multiple Task calls)
Task({ subagent_type: "test-runner", ... })
Task({ subagent_type: "documentation-generator", ... })
```

### All Available Tools

Tools available to Claude Code and subagents:

**File Operations:**
- `Read` - Read files from filesystem
- `Write` - Create or overwrite files
- `Edit` - Make exact string replacements
- `MultiEdit` - Edit multiple files simultaneously
- `NotebookEdit` - Edit Jupyter notebook cells

**Search & Discovery:**
- `Glob` - Find files by glob pattern
- `Grep` - Search file contents with regex

**Execution:**
- `Bash` - Execute shell commands
- `BashOutput` - Retrieve background shell output
- `KillShell` - Terminate background shells

**Web & External:**
- `WebFetch` - Fetch and analyze web content
- `WebSearch` - Search the web
- MCP Tools (Ref, AWS Documentation, CloudWatch, Chrome DevTools, IDE)

**Task Management:**
- `Task` - Launch specialized subagents
- `TodoWrite` - Manage task lists
- `AskUserQuestion` - Ask clarifying questions
- `ExitPlanMode` - Exit plan mode to start coding

**Skills & Commands:**
- `Skill` - Execute plugin skills
- `SlashCommand` - Execute custom user commands

### Command YAML Frontmatter

```yaml
---
name: "command-name"
description: "Command description"
args:
  - name: "arg-name"
    description: "Argument description"
    required: true | false
    default: "value"
---
```

### Hook Events Quick Reference

```
SessionStart      → Session begins
SessionEnd        → Session ends
UserPromptSubmit  → User sends message
PreToolUse        → Before tool executes
PostToolUse       → After tool completes
Stop              → Stop button pressed
Notification      → Claude notification
PreCompact        → Before context compaction
SubagentStop      → Subagent completes
```

---

## Consulting Workflow Summary

### Discovery Phase
1. Voice conversation to understand:
   - Project requirements
   - Team size and skills
   - Infrastructure (AWS, Azure, GCP)
   - Async vs sync needs
   - Dependencies
   - Budget constraints

### Design Phase
2. Design .claude repository:
   - Select primitives needed (commands, agents, hooks)
   - Choose observability level
   - Plan integrations (ADO, Archon, Graphiti)
   - Create boilerplate structure

### Implementation Phase
3. Build and deploy:
   - Create .claude directory structure
   - Configure settings.json
   - Write custom commands and agents
   - Set up hooks for automation
   - Add logging and observability
   - Document everything

### Handoff Phase
4. Client delivery:
   - VIBE_PLAN.md documentation
   - CLAUDE.md quick reference
   - Training session
   - Support documentation

---

**This handbook is based on analysis of 8 production .claude repositories and official Anthropic documentation.**

**Version:** 1.0
**Last Updated:** November 2025
**Maintained by:** Greg Black / GB Automation
