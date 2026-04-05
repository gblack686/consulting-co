# Pi Extension Selection for Client Workspaces

Maps consulting session data to Pi extension stacks that ship with every client workspace.

## Philosophy

OpenClaw IS Pi under the hood. Pi extensions are the programmable layer — they control what the agent sees, what it can do, how it presents information, and how it orchestrates work. Every client workspace ships with:

1. **Core Stack** — always loaded, non-negotiable
2. **Sample Extensions** — all 16 extensions as reference code the client can activate

The Vue consulting dashboard connects to the proxy (port 3050) which translates Pi runtime events (lifecycle, thinking, tool_use, assistant, text) into the frontend's event types. Extensions enhance what Pi does; the dashboard shows what Pi is doing.

---

## Core Extension Stack (Always Shipped)

These 4 extensions form the default `pi` experience for every client:

| Extension | Why Core | What It Does |
|-----------|----------|-------------|
| `minimal.ts` | Every session needs context visibility | Single-line footer: model + 10-block context meter |
| `theme-cycler.ts` | Branding + visual polish | Ctrl+X/Q cycle themes, `/theme` picker, 51 color tokens |
| `cross-agent.ts` | Claude Code interop | Loads commands from `.claude/`, `.gemini/`, `.codex/` directories |
| `pi-pi.ts` | Self-building agent | Meta-agent that builds new Pi agents with parallel expert research |

**Default launch command** (in justfile):
```bash
pi -e extensions/minimal.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts -e extensions/pi-pi.ts
```

---

## Extension Selection Matrix

During **Step 2b** of the pipeline, analyze `session_output/` to select additional extensions:

### From autonomy.json

| Signal | Extension | Justification |
|--------|-----------|---------------|
| `level: "ask-everything"` | `purpose-gate.ts` | Forces intent declaration — agent won't work until purpose is set |
| `level: "guided"` | `tilldone.ts` | Task-driven discipline — must define tasks before using tools |
| `restricted_paths` or `restricted_commands` present | `damage-control.ts` | Safety auditing — blocks patterns matching YAML rules |
| `level: "autonomous"` or `"just-get-it-done"` | None extra | Core stack is sufficient |

### From tool_inventory.json

| Signal | Extension | Justification |
|--------|-----------|---------------|
| `budget: "tight"` or monthly < $50 | `tool-counter.ts` | Cost visibility — shows tokens, cost, model in rich footer |
| `budget: "moderate"` or has cost tracking interest | `tool-counter-widget.ts` | Persistent cost badge widget |

### From domains/ (count + complexity)

| Signal | Extension | Justification |
|--------|-----------|---------------|
| 3+ domains, Pattern B/D selected | `agent-team.ts` | Dispatcher orchestrator with team grid dashboard |
| Sequential workflows (plan→build→review) | `agent-chain.ts` | Pipeline orchestrator with $ORIGINAL/$INPUT passing |
| Domains need background research tasks | `subagent-widget.ts` | `/sub` spawns background agents with live streaming |
| Single agent but multiple personas | `system-select.ts` | `/system` swaps agent persona + restricts tools per persona |

### From client_profile.json

| Signal | Extension | Justification |
|--------|-----------|---------------|
| Developer / power user | `session-replay.ts` | Scrollable timeline overlay for debugging |
| Minimalist / focus-oriented | `pure-focus.ts` | Strips footer + status entirely — zen mode |

---

## Recommended Stacks

### Stack 1: Lean Client (1-2 domains, budget-conscious)
```bash
pi -e extensions/minimal.ts \
   -e extensions/theme-cycler.ts \
   -e extensions/cross-agent.ts \
   -e extensions/pi-pi.ts \
   -e extensions/tool-counter.ts
```

### Stack 2: Safety-First Client (restricted autonomy, compliance needs)
```bash
pi -e extensions/minimal.ts \
   -e extensions/theme-cycler.ts \
   -e extensions/cross-agent.ts \
   -e extensions/pi-pi.ts \
   -e extensions/damage-control.ts \
   -e extensions/purpose-gate.ts
```

### Stack 3: Multi-Domain Client (3+ domains, Pattern B)
```bash
pi -e extensions/minimal.ts \
   -e extensions/theme-cycler.ts \
   -e extensions/cross-agent.ts \
   -e extensions/pi-pi.ts \
   -e extensions/agent-team.ts
```

### Stack 4: Pipeline Client (sequential ADW workflows)
```bash
pi -e extensions/minimal.ts \
   -e extensions/theme-cycler.ts \
   -e extensions/cross-agent.ts \
   -e extensions/pi-pi.ts \
   -e extensions/agent-chain.ts
```

### Stack 5: Power User (developer, full observability)
```bash
pi -e extensions/minimal.ts \
   -e extensions/theme-cycler.ts \
   -e extensions/cross-agent.ts \
   -e extensions/pi-pi.ts \
   -e extensions/tool-counter.ts \
   -e extensions/agent-team.ts \
   -e extensions/session-replay.ts
```

---

## Client Workspace Extension Layout

```
openclaw-{client}/
├── workspace/                    # OpenClaw workspace files
├── extensions/                   # Pi extensions (shipped with workspace)
│   ├── minimal.ts               # Core: compact footer
│   ├── theme-cycler.ts          # Core: theme cycling
│   ├── cross-agent.ts           # Core: .claude/ command loading
│   ├── pi-pi.ts                 # Core: meta-agent builder
│   ├── themeMap.ts              # Shared: theme defaults (dependency)
│   ├── pure-focus.ts            # Sample: zen mode
│   ├── tool-counter.ts          # Sample: cost tracking footer
│   ├── tool-counter-widget.ts   # Sample: cost widget
│   ├── purpose-gate.ts          # Sample: intent declaration
│   ├── tilldone.ts              # Sample: task discipline
│   ├── damage-control.ts        # Sample: safety auditing
│   ├── agent-team.ts            # Sample: dispatcher + grid
│   ├── agent-chain.ts           # Sample: sequential pipelines
│   ├── system-select.ts         # Sample: persona swapping
│   ├── subagent-widget.ts       # Sample: background agents
│   └── session-replay.ts        # Sample: timeline overlay
├── .pi/agents/                   # Pi agent definitions
│   ├── scout.md
│   ├── planner.md
│   ├── builder.md
│   ├── reviewer.md
│   └── teams.yaml
├── dashboard/                    # Vue consulting dashboard (built)
├── experts/                      # Claude Code expert systems
├── openclaw.json                 # Gateway config
└── justfile                      # All launch commands
```

---

## Justfile Recipes (generated per client)

```just
# ─── Pi Extension Sessions ───────────────────────────────────────────────────

# Launch Pi with core extensions (default interactive session)
pi-core:
    pi -e extensions/minimal.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts -e extensions/pi-pi.ts

# Launch Pi with cost tracking
pi-costs:
    pi -e extensions/minimal.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts -e extensions/tool-counter.ts

# Launch Pi with safety auditing
pi-safe:
    pi -e extensions/minimal.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts -e extensions/damage-control.ts

# Launch Pi with agent orchestration (multi-domain dispatcher)
pi-orchestrate:
    pi -e extensions/agent-team.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts

# Launch Pi with sequential pipeline (plan-build-review)
pi-pipeline:
    pi -e extensions/agent-chain.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts

# Launch Pi with full observability
pi-debug:
    pi -e extensions/minimal.ts -e extensions/theme-cycler.ts -e extensions/session-replay.ts -e extensions/tool-counter.ts

# Launch Pi zen mode (no distractions)
pi-focus:
    pi -e extensions/pure-focus.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts

# Launch Pi with task discipline
pi-tasks:
    pi -e extensions/tilldone.ts -e extensions/theme-cycler.ts -e extensions/cross-agent.ts
```

---

## Pi Agent Definitions (shipped with workspace)

Every client workspace gets `.pi/agents/` with agent definitions matching their domains:

### Standard Agents (always included)

```markdown
# .pi/agents/scout.md
---
name: scout
description: Fast recon and codebase exploration
tools: read,grep,find,ls
---
You are a scout agent. Investigate quickly and report findings concisely.
Do NOT modify any files. Focus on structure, patterns, and key entry points.
```

```markdown
# .pi/agents/planner.md
---
name: planner
description: Analyze requirements and create implementation plans
tools: read,grep,find,ls
---
You are a planning agent. Analyze the task, identify risks, and produce a clear plan.
```

```markdown
# .pi/agents/builder.md
---
name: builder
description: Implement code changes following plans
tools: read,write,edit,bash,grep,find,ls
---
You are a builder agent. Follow the plan precisely. Write clean, tested code.
```

### Per-Domain Agents (generated from session_output/domains/)

For each domain, generate a `.pi/agents/{domain}.md`:
```markdown
---
name: {domain_name}
description: {domain_description}
tools: {domain_tools}
---
{domain_system_prompt from SOUL.md vibe + domain expertise}
```

### Teams (generated from domain count)

```yaml
# .pi/agents/teams.yaml
full:
  - scout
  - planner
  - builder
  - reviewer

plan-build:
  - planner
  - builder

{domain_name}:
  - planner
  - builder
  - {domain_name}
```

### Chains (generated from workflow types)

```yaml
# .pi/agents/agent-chain.yaml
plan-build-review:
  description: "Full development cycle"
  steps:
    - agent: planner
      prompt: "Analyze and plan: $ORIGINAL"
    - agent: builder
      prompt: |
        ORIGINAL TASK: $ORIGINAL
        PLAN FROM PREVIOUS STEP: $INPUT
        Implement the plan.
    - agent: reviewer
      prompt: |
        ORIGINAL TASK: $ORIGINAL
        IMPLEMENTATION: $INPUT
        Review the implementation.
```

---

## Vue Dashboard Integration

The consulting dashboard (Vue frontend) connects to Pi via the customer gateway proxy:

```
Browser → http://<EIP>:3050/              (Vue dashboard)
Browser → ws://<EIP>:3050?token=xxx       (WebSocket)
                    ↕
Customer Gateway Proxy (Express, port 3050)
    ├── express.static('dashboard/')       ← serves Vue build
    ├── WebSocket ↔ Pi protocol translation
    └── REST: /health, /admin/tokens
                    ↕
Pi Runtime (OpenClaw Gateway, port 18789)
    ├── Extensions loaded (core stack + selected extras)
    ├── Agent definitions (.pi/agents/)
    ├── Skills (SKILL.md files)
    └── Workspace files (SOUL, USER, etc.)
```

### Pi Event → Dashboard Mapping

| Pi Runtime Event | Proxy Translation | Vue Component |
|-----------------|-------------------|---------------|
| stream: "lifecycle" | agent_created/updated | AgentList.vue (pulse) |
| stream: "thinking" | thinking_block | ThinkingBlockRow.vue |
| stream: "tool_use" | tool_use_block | ToolUseBlockRow.vue |
| stream: "assistant" | chat_stream | OrchestratorChat.vue |
| stream: "text" | orchestrator_chat | OrchestratorChatRow.vue |

Extensions enhance what happens INSIDE Pi — the dashboard shows what Pi is doing. The tool-counter extension tracks costs internally; the dashboard could show them in the UI. The agent-team extension dispatches agents; the dashboard shows agent cards pulsing.

---

## Pipeline Integration Point

This extension selection happens in **Step 2b** of the consulting-intake pipeline:

```
Step 1: Parse Transcript → session_output/
Step 2a: Build Workspace → SOUL, USER, IDENTITY, etc.
Step 2b: Select Pi Extensions ← THIS REFERENCE
  - Read autonomy.json → safety extensions
  - Read tool_inventory.json → cost extensions
  - Count domains/ → orchestration extensions
  - Read client_profile.json → UX extensions
  - Copy selected extensions to workspace
  - Generate .pi/agents/ from domains
  - Generate justfile Pi recipes
  - Configure openclaw.json extensions field
Step 3: Build Domain Experts
Step 4: Validate
Step 5: Deploy (includes dashboard build)
```

---

## Source Location

All extension source files live in:
```
C:\Users\gblac\OneDrive\Desktop\tac\pi-vs-claude-code\extensions\
```

During the BUILD phase, copy all 16 .ts files + themeMap.ts to the client workspace's `extensions/` directory.
