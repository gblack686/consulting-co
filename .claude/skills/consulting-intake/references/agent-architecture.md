# Pipeline Architecture: Transcript to Deployed Workspace

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSULTING SESSION (90 min)                   │
│              Client + Consultant + AI Assistant                  │
│                                                                 │
│  Questions from framework → Client answers → Transcript         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼ transcript.md
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    CLAUDE CODE PIPELINE                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              TAC CODING EXPERT (the meta-brain)            │  │
│  │                                                           │  │
│  │  Has: TAC expertise, expert-building patterns,            │  │
│  │       SKILL.md format, OpenClaw workspace spec            │  │
│  │                                                           │  │
│  │  Knows HOW to build experts. Used throughout.             │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  Step 1: PARSE → Step 2: WORKSPACE → Step 3: DOMAINS → Deploy  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Transcript Parser

Reads transcript → extracts structured data into `session_output/`.

**Inputs**: transcript.md (raw 90-minute session recording)

**Outputs**:
```
session_output/
├── client_profile.json      Name, timezone, pronouns, projects
├── soul_draft.md            Core truths, boundaries, vibe
├── identity.json            Agent name, creature, emoji, vibe
├── mission_statement.md     Mission, 90-day goals, top task
├── tool_inventory.json      Hardware, apps, API keys, budget
├── autonomy.json            Autonomy level, permissions, allowlist
└── domains/
    ├── {domain-1}.json      Domain name, tools, frequency
    │   └── workflows/
    │       ├── {wf-1}.json  Steps, trigger, output, gates, blast
    │       └── {wf-2}.json
    ├── {domain-2}.json
    └── {domain-3}.json
```

**Model**: sonnet (structured extraction from natural language)

---

## Step 2: Workspace Builder

Transforms session_output into OpenClaw workspace files using templates.

**Inputs**: session_output/ directory
**Templates**: `templates/*.tmpl`

**Outputs**:
```
client-workspace/workspace/
├── SOUL.md
├── USER.md
├── IDENTITY.md
├── MEMORY.md
├── AGENTS.md
├── TOOLS.md
└── HEARTBEAT.md
```

Plus `openclaw.json` at the workspace root.

These are direct transforms — no plan-build-improve needed.

**Model**: sonnet (template filling, structured writing)

---

## Step 3: Domain Expert Factory

For EACH domain discovered, run plan-build-improve-validate.

```
┌────────────────────────────────────────────────────────┐
│  Per-Domain Cycle (runs N times, parallelizable)       │
│                                                        │
│  PLAN ──────► BUILD ──────► IMPROVE ──────► VALIDATE   │
│  │            │              │                │         │
│  │ Classify   │ Write 8+    │ Update Part 7  │ Score   │
│  │ by TAC     │ expert      │ with research  │ >= 80%? │
│  │ pattern    │ files       │ findings       │         │
│  │            │              │                │         │
│  │ Dispatch   │ Write       │ Capture API    │ If No:  │
│  │ browser    │ SKILL.md    │ patterns       │ → BUILD │
│  │ + youtube  │ per wf      │                │         │
│  │ agents     │              │                │ If Yes: │
│  │            │ Write cron  │                │ → DONE  │
│  │            │ definitions │                │         │
│  └────────────┴──────────────┴────────────────┘         │
└────────────────────────────────────────────────────────┘
```

### PLAN Phase
1. Load domain spec from session_output
2. Classify each workflow by TAC pattern (see tac-pattern-library.md)
3. Identify API research needs → dispatch `playwright-bowser-agent`
4. Identify tutorial needs → dispatch `youtube-transcript-agent`
5. Determine domain-specific commands needed
6. Output: `specs/{domain}-plan.md`

### BUILD Phase
Generate using `templates/expert/*.tmpl`:
1. `_index.md` — domain overview + command registry
2. `expertise.md` — 7-part mental model
3. `question.md` — 6 question categories
4. `plan.md` — planning workflow
5. `plan_build_improve.md` — full ACT-LEARN-REUSE cycle
6. `self-improve.md` — learning workflow
7. Domain-specific commands (1-3 per domain)
8. OpenClaw `SKILL.md` per workflow (using `templates/skill.md.tmpl`)
9. Cron job definitions for scheduled workflows

### IMPROVE Phase
1. Incorporate browser research → expertise.md Part 4 (tool config)
2. Incorporate YouTube findings → expertise.md Part 7 (patterns)
3. Review built files vs. plan for gaps

### VALIDATE Phase
Score using quality-rubric.md:
- Per-Expert Structural: 25 pts
- Per-Skill Validation: 25 pts
- OpenClaw Config: 25 pts
- Cross-Reference & Security: 25 pts
- **If < 80% → loop back to BUILD with specific fixes**
- **If >= 80% → domain COMPLETE**

---

## Step 4: Assembly & Deployment

```
client-workspace/
├── workspace/              OpenClaw workspace files
│   ├── SOUL.md
│   ├── USER.md
│   ├── IDENTITY.md
│   ├── MEMORY.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   └── skills/
│       ├── {domain-1}/
│       │   ├── {workflow-1}/SKILL.md
│       │   └── {workflow-2}/SKILL.md
│       └── {domain-2}/
│           └── {workflow}/SKILL.md
│
├── experts/                Claude Code expert systems
│   ├── {domain-1}/
│   │   ├── _index.md
│   │   ├── expertise.md
│   │   ├── question.md
│   │   ├── plan.md
│   │   ├── plan_build_improve.md
│   │   ├── self-improve.md
│   │   └── {domain-command}.md
│   └── {domain-2}/
│       └── ...
│
├── openclaw.json           Gateway config
├── cron-setup.sh           Cron job install commands
└── quality_report.md       Validation scores
```

### Deploy Commands
```bash
# Package
tar -czf client-workspace.tar.gz client-workspace/

# Deploy workspace files
scp -i {key} client-workspace/workspace/* ubuntu@{host}:~/.openclaw/workspace/

# Deploy skills
scp -r -i {key} client-workspace/workspace/skills/* ubuntu@{host}:~/.openclaw/workspace/skills/

# Deploy config
scp -i {key} client-workspace/openclaw.json ubuntu@{host}:~/.openclaw/openclaw.json

# Restart gateway
ssh -i {key} ubuntu@{host} "systemctl --user restart openclaw-gateway"

# Install cron jobs
ssh -i {key} ubuntu@{host} "bash -s" < client-workspace/cron-setup.sh

# Verify
ssh -i {key} ubuntu@{host} "openclaw doctor --non-interactive"
```

---

## Standard Components (Pre-Built)

### TAC Coding Expert
The meta-brain with TAC methodology baked in. Used throughout every step.

```
.claude/commands/experts/tac-coding/
├── _index.md              TAC-informed expert construction
├── expertise.md           7-part: expert arch, workspace spec, SKILL format,
│                          TAC patterns, cron spec, parsing, quality scoring
├── question.md            6 categories of TAC/expert questions
├── plan.md                Domain analysis + TAC classification
├── plan_build_improve.md  Full ACT-LEARN-REUSE per domain
├── self-improve.md        Update after each domain build
├── parse-transcript.md    Domain command: transcript → session_output
├── build-workspace.md     Domain command: session_output → workspace files
├── build-domain-expert.md Domain command: domain spec → expert directory
└── validate-package.md    Domain command: package → quality_report
```

### Research Utilities (dispatched during PLAN)

**Browser Research**:
```
Task(subagent_type: "playwright-bowser-agent")
Model: sonnet | Max turns: 15
Purpose: API docs, auth methods, MCP servers, ClawHub plugins
Output: Structured JSON → expertise.md Part 4
```

**YouTube Research**:
```
Task(subagent_type: "youtube-transcript-agent")
Model: haiku | Max turns: 20
Purpose: OpenClaw integration tutorials, working prompts, pitfalls
Output: Transcript files → expertise.md Part 7
```

---

## Model Selection Per Pipeline Step

| Step | Model | Reasoning |
|------|-------|-----------|
| Transcript parsing | sonnet | Structured extraction from natural language |
| Workspace file generation | sonnet | Template transforms, structured writing |
| Domain planning | sonnet | TAC classification, research dispatch |
| Expert file generation | sonnet | Structured writing, pattern application |
| Browser research | sonnet | Web navigation + structured extraction |
| YouTube research | haiku | Transcript extraction is mechanical |
| Quality validation | opus | Deep reasoning, judgment for scoring |

---

## What Ships to the Client

| Layer | Contents | Destination |
|-------|----------|-------------|
| OpenClaw Workspace | SOUL, USER, IDENTITY, MEMORY, AGENTS, TOOLS, HEARTBEAT | `~/.openclaw/workspace/` |
| OpenClaw Skills | SKILL.md per workflow (triggers, delivery) | `~/.openclaw/workspace/skills/` |
| OpenClaw Config | Model routing, channels, allowlists, sessions, extensions | `~/.openclaw/openclaw.json` |
| Pi Extensions | 16 TypeScript extensions (4 core + 12 samples) | `extensions/` in client repo |
| Pi Agent Definitions | .pi/agents/*.md + teams.yaml + agent-chain.yaml | `.pi/agents/` in client repo |
| Vue Dashboard | Consulting chat UI (built static files) | `dashboard/` served from proxy |
| Cron Jobs | Scheduled tasks (briefs, syncs, reports) | Via `openclaw cron add` |
| Claude Code Experts | Full expert system per domain (self-improving) | `.claude/commands/experts/` |

The experts are the consulting engagement made permanent. They encode domain knowledge into a self-improving system the client continues to use.

---

## Pi Extension Layer

Pi extensions run in-process in the Pi runtime (which powers OpenClaw). They control safety, UI, orchestration, and observability.

### Core Stack (always loaded)

| Extension | Purpose |
|-----------|---------|
| `minimal.ts` | Compact footer with model + context meter |
| `theme-cycler.ts` | Theme support (Ctrl+X/Q cycle, /theme picker) |
| `cross-agent.ts` | Loads commands from .claude/, .gemini/, .codex/ |
| `pi-pi.ts` | Meta-agent that builds new Pi agents |

### Sample Extensions (shipped as reference code)

| Extension | Category | Activates When |
|-----------|----------|---------------|
| `damage-control.ts` | Safety | Restricted autonomy, compliance needs |
| `purpose-gate.ts` | Discipline | "Ask-everything" autonomy level |
| `tilldone.ts` | Discipline | Task-heavy workflows |
| `tool-counter.ts` | Observability | Budget-conscious clients |
| `agent-team.ts` | Orchestration | 3+ domains, Pattern B/D |
| `agent-chain.ts` | Orchestration | Sequential workflows (plan-build-review) |
| `subagent-widget.ts` | Orchestration | Background research tasks |
| `system-select.ts` | Orchestration | Single agent, multiple personas |
| `session-replay.ts` | Observability | Developer / power user clients |
| `pure-focus.ts` | UI | Minimalist / focus-oriented clients |
| `tool-counter-widget.ts` | Observability | Extended cost tracking |

See `references/pi-extension-selection.md` for the full selection matrix.

---

## Vue Dashboard Layer

The consulting dashboard provides a web chat interface powered by Pi/OpenClaw under the hood:

```
Browser → http://<EIP>:3050/              Vue dashboard (static files)
Browser → ws://<EIP>:3050?token=xxx       WebSocket (real-time events)
                    ↕
Customer Gateway Proxy (Express, port 3050)
    ├── express.static('dashboard/')       serves Vue build
    ├── WebSocket ↔ Pi protocol translation
    └── REST: /health, /admin/tokens
                    ↕
Pi Runtime (OpenClaw Gateway, port 18789)
    ├── Extensions (core stack + selected extras)
    ├── Agent definitions (.pi/agents/)
    ├── Skills + Workspace files
    └── Sub-agent spawning (max 8 concurrent)
```

Pi runtime events are translated by the proxy into dashboard-compatible types:

| Pi Event | Dashboard Event | Vue Component |
|----------|----------------|---------------|
| lifecycle (start/end) | agent_created/updated | AgentList (pulse) |
| thinking | thinking_block | ThinkingBlockRow |
| tool_use | tool_use_block | ToolUseBlockRow |
| assistant (delta) | chat_stream | OrchestratorChat |
| text (final) | orchestrator_chat | OrchestratorChatRow |
