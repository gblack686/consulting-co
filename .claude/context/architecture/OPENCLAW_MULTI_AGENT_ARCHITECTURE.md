# OpenClaw Multi-Agent Architecture Reference

> Extracted from docs.openclaw.ai on 2026-02-19. Comprehensive reference for designing
> multi-agent OpenClaw deployments as a consulting product.

---

## Table of Contents

1. [Agent Creation Methods](#1-agent-creation-methods)
2. [Agent Directory Structure](#2-agent-directory-structure)
3. [Workspace Files & Templates](#3-workspace-files--templates)
4. [Agent Configuration in openclaw.json](#4-agent-configuration-in-openclawjson)
5. [Multi-Agent Routing & Bindings](#5-multi-agent-routing--bindings)
6. [Sub-Agent Spawning & Orchestration](#6-sub-agent-spawning--orchestration)
7. [Skills System](#7-skills-system)
8. [Sandbox & Tool Policies Per Agent](#8-sandbox--tool-policies-per-agent)
9. [Session Management](#9-session-management)
10. [Agent Loop & Runtime](#10-agent-loop--runtime)
11. [Lobster Workflow Runtime](#11-lobster-workflow-runtime)
12. [Channel Integration & Multi-Account](#12-channel-integration--multi-account)
13. [Agent-to-Agent Communication](#13-agent-to-agent-communication)
14. [Bootstrapping & First-Run Ritual](#14-bootstrapping--first-run-ritual)
15. [Configuration Management & Hot Reload](#15-configuration-management--hot-reload)
16. [Complete Multi-Agent Examples](#16-complete-multi-agent-examples)
17. [CLI Command Reference](#17-cli-command-reference)

---

## 1. Agent Creation Methods

### A. Onboarding Wizard (Recommended First-Time Setup)

```bash
openclaw onboard --install-daemon
```

Nine-step interactive flow:
1. **Existing Config Detection** - Keep / Modify / Reset existing `openclaw.json`
2. **Model/Auth** - Select provider (Anthropic, OpenAI, xAI, Gemini, Moonshot, etc.) and default model
3. **Workspace** - Set agent workspace path (default: `~/.openclaw/workspace`)
4. **Gateway** - Configure port, bind address, auth mode, Tailscale
5. **Channels** - WhatsApp, Telegram, Discord, Google Chat, Mattermost, Signal, etc.
6. **Daemon** - LaunchAgent (macOS) or systemd (Linux/WSL2)
7. **Health Check** - Starts gateway, runs `openclaw health`
8. **Skills** - Install recommended skills and dependencies
9. **Finish** - Summary and next steps

QuickStart mode provides automatic defaults:
- Local gateway on loopback, port 18789
- Token-based auth (auto-generated)
- Tailscale disabled

### B. CLI Agent Addition

```bash
openclaw agents add coding
openclaw agents add social
openclaw agents add work
```

Creates separate agents with distinct workspaces and auth profiles. Verify with:
```bash
openclaw agents list --bindings
```

### C. Non-Interactive / Scripted Setup

```bash
openclaw onboard --non-interactive \
  --mode local --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --install-daemon \
  --skip-skills
```

### D. Manual Configuration

Edit `~/.openclaw/openclaw.json` directly (JSON5 format with comments and trailing commas).

### E. RPC API (Programmatic)

Gateway exposes `wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status` for remote clients (e.g., macOS app driving setup on a remote server).

### F. Configuration Commands

| Command | Purpose |
|---------|---------|
| `openclaw onboard` | Interactive full setup |
| `openclaw configure` | Reconfiguration wizard |
| `openclaw config get <key>` | Retrieve setting |
| `openclaw config set <key> <value>` | Update setting |
| `openclaw config unset <key>` | Remove setting |
| `openclaw doctor` | Validate and diagnose |
| `openclaw doctor --fix` | Auto-repair issues |

---

## 2. Agent Directory Structure

### Complete File Tree

```
~/.openclaw/
├── openclaw.json                          # Main config (JSON5)
├── .env                                    # Global env fallback
├── agents/
│   ├── main/
│   │   ├── agent/
│   │   │   └── auth-profiles.json         # Per-agent auth credentials
│   │   └── sessions/                      # Session transcripts & metadata
│   ├── coding/
│   │   ├── agent/
│   │   │   └── auth-profiles.json
│   │   └── sessions/
│   └── work/
│       ├── agent/
│       │   └── auth-profiles.json
│       └── sessions/
├── workspace/                             # Default agent workspace (or workspace-<agentId>)
│   ├── AGENTS.md                          # Operating instructions, memory rules
│   ├── SOUL.md                            # Persona, tone, boundaries
│   ├── USER.md                            # User identity & preferences
│   ├── IDENTITY.md                        # Agent name, vibe, emoji
│   ├── TOOLS.md                           # Local tool notes
│   ├── HEARTBEAT.md                       # Periodic check-in checklist
│   ├── BOOT.md                            # Gateway restart checklist
│   ├── BOOTSTRAP.md                       # One-time first-run ritual (deleted after)
│   ├── MEMORY.md                          # Curated long-term memory
│   ├── memory/
│   │   └── YYYY-MM-DD.md                  # Daily memory logs
│   ├── skills/                            # Per-agent skills
│   └── canvas/                            # Optional Canvas UI files
├── workspace-coding/                      # Separate workspace per agent
├── workspace-work/
├── skills/                                # Shared skills (all agents)
├── credentials/
│   └── whatsapp/
│       ├── personal/                      # Per-account auth dirs
│       └── biz/
└── logs/
    └── gateway.log
```

### Critical Rules

- **NEVER reuse `agentDir` across agents** - causes auth/session collisions
- Each agent gets its own `~/.openclaw/agents/<agentId>/` directory
- Each agent gets its own workspace (e.g., `workspace-home`, `workspace-work`)
- Credentials stored outside workspace - never version-control them
- Sessions stored at `~/.openclaw/agents/<agentId>/sessions/`

---

## 3. Workspace Files & Templates

### AGENTS.md (Operating Instructions)

Loaded at every session start. Defines:
- Three foundational reads: SOUL.md, USER.md, daily memory
- Memory architecture (daily logs + curated long-term)
- Behavioral boundaries (safe autonomy vs. requires permission)
- Group chat protocol (when to respond, when to stay silent)
- Heartbeat system configuration
- Rule: "if you want to remember something, WRITE IT TO A FILE"

### SOUL.md (Persona & Boundaries)

Loaded every session. Establishes:
- "Not a chatbot - becoming someone"
- "Be genuinely helpful, not performatively helpful"
- Develop actual opinions and preferences
- Privacy is non-negotiable
- Conversational tone: "concise when needed, thorough when it matters"

### USER.md (User Context)

User identity, preferences, communication style. Loaded every session.

### IDENTITY.md (Agent Identity)

Agent name, vibe, emoji. Auto-created during bootstrap.

### BOOTSTRAP.md (First-Run Ritual)

One-time interactive Q&A that:
- Collects identity details
- Persists results to IDENTITY.md, USER.md, SOUL.md
- Self-deletes after completion
- Always runs on the gateway host

### Bootstrap Limits

- `agents.defaults.bootstrapMaxChars`: 20000 (per file)
- `agents.defaults.bootstrapTotalMaxChars`: 150000 (all files combined)

---

## 4. Agent Configuration in openclaw.json

### Full Agent Definition Schema

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["openai/gpt-5.2"],
      },
      models: {
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "openai/gpt-5.2": { alias: "GPT" },
      },
      imageMaxDimensionPx: 1200,
      sandbox: {
        mode: "off",        // off | non-main | all
        scope: "session",   // session | agent | shared
      },
      heartbeat: {
        every: "0m",        // 30m, 2h, 0m to disable
        target: "none",     // last | whatsapp | telegram | discord | none
      },
      subagents: {
        model: "claude-3-5-haiku",
        archiveAfterMinutes: 60,
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
      },
      bootstrapMaxChars: 20000,
      bootstrapTotalMaxChars: 150000,
    },

    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace-main",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Bot Name" },
        groupChat: {
          mentionPatterns: ["@bot", "@mention"],
        },
        sandbox: {
          mode: "off",
          scope: "agent",
        },
        tools: {
          allow: ["exec", "read"],
          deny: ["write"],
        },
        subagents: {
          model: "claude-3-5-sonnet",
          thinking: "enabled",
          allowAgents: ["worker-1", "worker-2"],
        },
      },
      {
        id: "coding",
        workspace: "~/.openclaw/workspace-coding",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
}
```

### Key Agent Fields

| Field | Purpose |
|-------|---------|
| `id` | Unique agent identifier |
| `default` | Mark as primary agent (true/false) |
| `name` | Human-readable display name |
| `workspace` | Directory path for agent data |
| `agentDir` | State directory for auth, models, config |
| `model` | Override model (or use `model.primary` + `model.fallbacks`) |
| `identity.name` | Agent's display name |
| `groupChat.mentionPatterns` | Regex patterns for group mentions |
| `sandbox` | Per-agent sandbox config |
| `tools` | Per-agent tool allow/deny lists |
| `subagents` | Sub-agent configuration overrides |

### Config File Organization

Supports `$include` for splitting across files:

```json5
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/a.json5", "./clients/b.json5"],
  },
}
```

- Nesting up to 10 levels
- Array of files: deep-merged in order (later wins)
- Relative paths resolve from including file location

---

## 5. Multi-Agent Routing & Bindings

### Binding Rule Structure

```json5
{
  bindings: [
    {
      agentId: "target-agent-id",
      match: {
        channel: "whatsapp",        // Channel name
        accountId: "biz",           // Account identifier
        peer: {
          kind: "direct",           // direct | group
          id: "+15551234567",       // Phone number, group ID, etc.
        },
        teamId: "T123",            // Slack-specific
        guildId: "123...",          // Discord-specific
        roles: ["admin"],           // Discord role-based
      },
    },
  ],
}
```

### Routing Priority (Most-Specific Wins)

Bindings are **deterministic** with this evaluation order:

1. **Peer match** - exact DM/group/channel ID
2. **Parent peer match** - thread inheritance
3. **Guild ID + roles** - Discord
4. **Guild ID** - Discord
5. **Team ID** - Slack
6. **Account ID match** - per-account routing
7. **Channel-level match** - broad channel routing
8. **Fallback to default agent** - agent with `default: true`

When a binding includes multiple match fields, **ALL fields must match**.

### Session Key Format

- Direct messages: `agent:<agentId>:<mainKey>` (collapses per agent)
- Groups: `agent:<agentId>:<channel>:group:<id>`
- Threads: `agent:<agentId>:<channel>:group:<id>:thread:<threadId>`
- Telegram forums: `agent:<agentId>:telegram:group:<id>:topic:<topicId>`

### Broadcast Groups (Multi-Agent Processing)

Multiple agents process the same peer concurrently:

```json5
{
  broadcast: {
    strategy: "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"],
    "+15555550123": ["support", "logger"],
  },
}
```

---

## 6. Sub-Agent Spawning & Orchestration

### Spawning Methods

**Slash command:**
```
/subagents spawn <agentId> <task> [--model <model>] [--thinking <level>]
```

**Programmatic (sessions_spawn tool):**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `task` | string | Yes | The work to delegate |
| `label` | string | No | Human-readable identifier |
| `agentId` | string | No | Target agent (default: caller) |
| `model` | string | No | Override model |
| `thinking` | string | No | Override reasoning depth |
| `runTimeoutSeconds` | number | No | Abort timer (default: 0 = no timeout) |
| `cleanup` | string | No | `delete` or `keep` (default: keep) |

### Sub-Agent Management Commands

| Command | Purpose |
|---------|---------|
| `/subagents list` | View all active sub-agents |
| `/subagents kill <id\|#\|all>` | Terminate runs |
| `/subagents log <id\|#> [limit] [tools]` | Inspect execution logs |
| `/subagents info <id\|#>` | View metadata, session ID, transcript |
| `/subagents send <id\|#> <message>` | Communicate with running sub-agent |
| `/subagents steer <id\|#> <message>` | Redirect execution |

### Session Isolation

Sub-agents run in isolated sessions: `agent:<agentId>:subagent:<uuid>`

### Lifecycle

- **Non-blocking spawn** - returns `{ status: "accepted", runId, childSessionKey }` immediately
- **Completion announcement** - sends final update to requester chat when finished
- **Auto-archival** - sessions archive after `archiveAfterMinutes` (default: 60)
- **Completion messages** include: result, status (`completed`/`failed`/`timed out`), runtime, token stats

### Nested Sub-Agents (Orchestrator Pattern)

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
      },
    },
  },
}
```

| Depth | Session Format | Role | Can Spawn? |
|-------|----------------|------|------------|
| 0 | `agent:<id>:main` | Primary agent | Always |
| 1 | `agent:<id>:subagent:<uuid>` | Orchestrator | If `maxSpawnDepth >= 2` |
| 2 | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | Worker | Never |

**Announcement chain:** depth-2 worker -> depth-1 orchestrator -> main -> user

### Tool Policy by Depth

- **Depth 1 (orchestrator):** Gets `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history`
- **Depth 1 (leaf):** No session tools
- **Depth 2 (worker):** No session tools; `sessions_spawn` always denied

### Sub-Agent Configuration

```json5
{
  agents: {
    list: [{
      id: "orchestrator",
      subagents: {
        model: "claude-3-5-sonnet",
        thinking: "enabled",
        allowAgents: ["worker-1", "worker-2"],
      },
    }],
    defaults: {
      subagents: {
        model: "claude-3-5-haiku",
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

### Sub-Agent Tool Override

```json5
{
  tools: {
    subagents: {
      tools: {
        deny: ["gateway", "cron"],
        allow: ["read", "exec", "process"],
      },
    },
  },
}
```

### Constraints

- Max nesting depth: 5 (depth 2 recommended)
- Max children per agent: configurable (default 5, max 20)
- Max concurrent: configurable (default 8)
- `/stop` cascades: aborts orchestrator and all children recursively
- Sub-agent context injects only AGENTS.md + TOOLS.md (no SOUL/IDENTITY)
- Gateway restarts lose pending announcements

---

## 7. Skills System

### Skill Format

Skills are directories containing a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name
description: What this skill does
metadata: {"openclaw":{"requires":{"bins":["uv"],"env":["API_KEY"]},"primaryEnv":"API_KEY"}}
---

## Instructions for the agent

Use `{baseDir}` to reference the skill folder path.
```

### Storage Locations (Precedence Order)

1. **Workspace skills** - `<workspace>/skills/` (highest - per-agent)
2. **Managed/local skills** - `~/.openclaw/skills/` (shared across agents)
3. **Bundled skills** - shipped with installation (lowest)
4. **Extra dirs** - `skills.load.extraDirs` (lowest precedence)

Naming conflicts: workspace > managed > bundled.

### Skill Frontmatter Options

| Key | Values | Purpose |
|-----|--------|---------|
| `name` | string | Skill identifier |
| `description` | string | What the skill does |
| `homepage` | URL | Display in macOS UI |
| `user-invocable` | true/false | Expose as slash command (default: true) |
| `disable-model-invocation` | true/false | Exclude from model prompt (default: false) |
| `command-dispatch` | "tool" | Dispatch slash command to tool |
| `command-tool` | tool name | Specific tool to invoke |

### Metadata Gating (Load-Time Filtering)

```json
{"openclaw":{
  "always": true,
  "emoji": "icon",
  "os": ["darwin", "linux", "win32"],
  "requires": {
    "bins": ["uv"],
    "anyBins": ["npm", "pnpm"],
    "env": ["API_KEY"],
    "config": ["feature.enabled"]
  },
  "primaryEnv": "API_KEY",
  "skillKey": "custom-key"
}}
```

### Skills Configuration in openclaw.json

```json5
{
  skills: {
    allowBundled: ["skill-a", "skill-b"],   // restrict bundled skills
    entries: {
      "skill-name": {
        enabled: true,
        apiKey: "SECRET_VALUE",             // maps to primaryEnv
        env: {
          API_KEY: "SECRET_VALUE",
        },
        config: {
          customField: "value",
        },
      },
    },
    load: {
      watch: true,
      watchDebounceMs: 250,
      extraDirs: ["/path/to/extra/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm",                   // npm | pnpm | yarn | bun
    },
  },
}
```

### Skill Installation (ClawHub)

```bash
clawhub install <skill-slug>
clawhub update --all
clawhub sync --all
```

### Token Impact

Per-skill overhead: ~97 chars + name + description + location = ~24 tokens per skill in system prompt.

---

## 8. Sandbox & Tool Policies Per Agent

### Sandbox Modes

| Mode | Behavior |
|------|----------|
| `off` | No sandboxing |
| `non-main` | Sandbox non-main sessions only |
| `all` | Always sandbox |

### Sandbox Scopes

| Scope | Behavior |
|-------|----------|
| `session` | New container per session |
| `agent` | Shared container per agent |
| `shared` | Pooled across agents |

### Tool Policy Precedence (Restrictive Cascade)

Each level can further restrict but **cannot grant back denied tools**:

1. Tool profile (global or agent-specific)
2. Provider-specific tool profile
3. Global allow/deny lists
4. Provider allow/deny lists
5. Agent-specific allow/deny lists
6. Agent provider allow/deny lists
7. Sandbox tool policy
8. Subagent tool policy

### Tool Groups (Shorthands)

| Group | Tools |
|-------|-------|
| `group:runtime` | exec, bash, process |
| `group:fs` | read, write, edit, apply_patch |
| `group:sessions` | sessions_list, sessions_history, sessions_send, sessions_spawn, session_status |
| `group:memory` | memory_search, memory_get |
| `group:ui` | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging` | message |
| `group:nodes` | nodes |
| `group:openclaw` | all built-in OpenClaw tools |

### Example: Read-Only Agent

```json5
{
  tools: {
    allow: ["read"],
    deny: ["exec", "write", "edit", "apply_patch", "process"],
  },
}
```

### Example: Messaging-Only Agent

```json5
{
  tools: {
    allow: ["sessions_list", "sessions_send", "sessions_history", "session_status"],
    deny: ["exec", "write", "edit", "apply_patch", "read", "browser"],
  },
}
```

---

## 9. Session Management

### Session Configuration

```json5
{
  session: {
    dmScope: "per-channel-peer",   // main | per-peer | per-channel-peer | per-account-channel-peer
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
  },
}
```

### Scope Options

| Scope | Isolation Level |
|-------|----------------|
| `main` | Shared across all conversations |
| `per-peer` | Isolated per user |
| `per-channel-peer` | Isolated per user per channel (recommended) |
| `per-account-channel-peer` | Full isolation by account + channel + peer |

### Reset Modes

- `daily` - Reset at specified hour
- `idleMinutes` - Reset after inactivity period

---

## 10. Agent Loop & Runtime

### Execution Flow (5 Phases)

1. **Entry & Validation** - RPC validates params, resolves session, returns `{ runId, acceptedAt }`
2. **Model Resolution** - Resolves model, thinking/verbose defaults, loads skills snapshot
3. **Serialized Execution** - Per-session + global queue serialization, model + auth resolution, timeout enforcement
4. **Event Stream Bridging** - Tool events -> `stream: "tool"`, assistant deltas -> `stream: "assistant"`, lifecycle -> `stream: "lifecycle"`
5. **Reply Assembly** - Combines text, reasoning blocks, tool summaries, filters NO_REPLY tokens

### Context Assembly (Before Streaming)

- Workspace resolution (sandbox redirect if needed)
- Skills injection (cached snapshots)
- Bootstrap context injection into system prompt
- Write lock acquisition on session

### Hook Points

**Internal hooks:**
- `agent:bootstrap` - modify bootstrap files before prompt
- Command hooks - `/new`, `/reset`, `/stop`

**Plugin hooks:**
- `before_model_resolve` - override provider/model
- `before_prompt_build` - inject context
- `agent_end` - inspect final messages
- `before/after_compaction` - observe compaction
- `before/after_tool_call` - intercept tool execution
- `message_received/sending/sent` - message lifecycle
- `session_start/end` - session boundaries

### Timeouts

- `agent.wait` default: 30 seconds
- Agent runtime default: 600 seconds

---

## 11. Lobster Workflow Runtime

### Purpose

Deterministic multi-step tool pipelines with approval gates. Eliminates token-expensive LLM orchestration for repeatable workflows.

### Pipeline Structure

```yaml
name: inbox-triage
args:
  tag:
    default: "family"
steps:
  - id: collect
    command: inbox list --json
  - id: categorize
    command: inbox categorize --json
    stdin: $collect.stdout
  - id: approve
    command: inbox apply --approve
    stdin: $categorize.stdout
    approval: required
  - id: execute
    command: inbox apply --execute
    stdin: $categorize.stdout
    condition: $approve.approved
```

### Key Features

- Steps reference prior outputs via `$step.stdout` or `$step.json`
- Approval gates pause execution until human confirms
- Resume tokens allow continuation without re-execution
- LLM steps available via `llm-task` plugin for structured classification
- Local subprocess only (no outbound network calls)
- Sandbox-aware

### Multi-Agent Integration

"Use `/prose` to orchestrate multi-agent prep, then run a Lobster pipeline for deterministic approvals."

Sub-agents access Lobster via `tools.subagents.tools` allowlisting.

---

## 12. Channel Integration & Multi-Account

### Supported Channels (30+)

WhatsApp, Telegram, Discord, Slack, Signal, iMessage, LINE, Matrix, IRC, Mattermost, Microsoft Teams, Google Chat, Feishu, Zalo, grammY, Broadcast Groups, and more.

### Multi-Account WhatsApp Example

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
  channels: {
    whatsapp: {
      accounts: {
        personal: { authDir: "~/.openclaw/credentials/whatsapp/personal" },
        biz: { authDir: "~/.openclaw/credentials/whatsapp/biz" },
      },
      dmPolicy: "allowlist",
      allowFrom: ["+15551230001"],
    },
  },
}
```

Login sequence:
```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

### Multi-Bot Discord Example

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "coding", workspace: "~/.openclaw/workspace-coding" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "discord", accountId: "default" } },
    { agentId: "coding", match: { channel: "discord", accountId: "coding" } },
  ],
  channels: {
    discord: {
      accounts: {
        default: {
          token: "DISCORD_BOT_TOKEN_MAIN",
          guilds: {
            "123456789012345678": {
              channels: { "222222222222222222": { allow: true } },
            },
          },
        },
        coding: {
          token: "DISCORD_BOT_TOKEN_CODING",
          guilds: {
            "123456789012345678": {
              channels: { "333333333333333333": { allow: true } },
            },
          },
        },
      },
    },
  },
}
```

### DM Policies

| Policy | Behavior |
|--------|----------|
| `pairing` | Unknown senders get one-time pairing code (default) |
| `allowlist` | Only `allowFrom` entries or paired senders |
| `open` | Allow all (requires `allowFrom: ["*"]`) |
| `disabled` | Ignore all DMs |

---

## 13. Agent-to-Agent Communication

### Configuration

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,       // Off by default
      allow: ["home", "work"],
    },
  },
}
```

Must be explicitly enabled AND allowlisted.

---

## 14. Bootstrapping & First-Run Ritual

### Process

1. Agent launches for first time
2. System seeds: AGENTS.md, BOOTSTRAP.md, IDENTITY.md, USER.md
3. Interactive Q&A sequence (one question at a time)
4. Results persisted to: IDENTITY.md, USER.md, SOUL.md
5. BOOTSTRAP.md deleted (runs only once)

### Key Constraints

- Always runs on the **gateway host**
- Users must edit workspace files directly on gateway host for remote setups
- `skipBootstrap: true` in config disables bootstrap file creation
- Regenerate defaults via `openclaw setup`

---

## 15. Configuration Management & Hot Reload

### Hot Reload Modes

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

| Mode | Behavior |
|------|----------|
| `hybrid` | Hot-applies safe changes, auto-restarts critical ones (default) |
| `hot` | Hot-applies safe; warns about restart-needed changes |
| `restart` | Full restart on any change |
| `off` | No file watching |

**Hot-apply fields:** Channels, agents, models, automation, sessions, tools, UI

**Restart-required:** Gateway server (`gateway.*`), infrastructure (`discovery`, `plugins`)

### Environment Variables

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

Substitution syntax: `${VAR_NAME}` in strings. Escape with `$${VAR}`.

### RPC Config Updates

Rate limit: 3 requests per 60 seconds per `deviceId+clientIp`.

**Full replace:**
```bash
openclaw gateway call config.apply --params '{
  "raw": "{ agents: { defaults: { workspace: \"~/.openclaw/workspace\" } } }",
  "baseHash": "<hash>",
  "sessionKey": "agent:main:whatsapp:dm:+15555550123"
}'
```

**Partial update (merge patch):**
```bash
openclaw gateway call config.patch --params '{
  "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
  "baseHash": "<hash>"
}'
```

---

## 16. Complete Multi-Agent Examples

### Example A: Personal + Work Split by WhatsApp Account

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
  channels: {
    whatsapp: {
      accounts: {
        personal: { authDir: "~/.openclaw/credentials/whatsapp/personal" },
        biz: { authDir: "~/.openclaw/credentials/whatsapp/biz" },
      },
    },
  },
}
```

### Example B: Fast Chat vs Deep Work by Channel

```json5
{
  agents: {
    list: [
      { id: "chat", workspace: "~/.openclaw/workspace-chat", model: "anthropic/claude-sonnet-4-5" },
      { id: "opus", workspace: "~/.openclaw/workspace-opus", model: "anthropic/claude-opus-4-6" },
    ],
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "opus", match: { channel: "telegram" } },
  ],
}
```

### Example C: Peer-Based Routing (Different People -> Different Agents)

```json5
{
  agents: {
    list: [
      { id: "alex", workspace: "~/.openclaw/workspace-alex" },
      { id: "mia", workspace: "~/.openclaw/workspace-mia" },
    ],
  },
  bindings: [
    { agentId: "alex", match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230001" } } },
    { agentId: "mia", match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230002" } } },
  ],
}
```

### Example D: Family Bot in WhatsApp Group (Sandboxed)

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        identity: { name: "Family Bot" },
        groupChat: { mentionPatterns: ["@family", "@familybot"] },
        sandbox: { mode: "all", scope: "agent" },
        tools: {
          allow: ["exec", "read", "sessions_list", "sessions_history"],
          deny: ["write", "edit", "browser"],
        },
      },
    ],
  },
  bindings: [
    {
      agentId: "family",
      match: { channel: "whatsapp", peer: { kind: "group", id: "120363999999999999@g.us" } },
    },
  ],
}
```

### Example E: Orchestrator with Sub-Agents

```json5
{
  agents: {
    list: [
      {
        id: "orchestrator",
        workspace: "~/.openclaw/workspace-orchestrator",
        model: "anthropic/claude-opus-4-6",
        subagents: {
          model: "anthropic/claude-sonnet-4-5",
          thinking: "enabled",
          allowAgents: ["researcher", "coder", "reviewer"],
          maxSpawnDepth: 2,
          maxChildrenPerAgent: 5,
        },
      },
      {
        id: "researcher",
        workspace: "~/.openclaw/workspace-researcher",
        tools: { allow: ["read", "exec", "browser"] },
      },
      {
        id: "coder",
        workspace: "~/.openclaw/workspace-coder",
        tools: { allow: ["read", "write", "edit", "exec"] },
      },
      {
        id: "reviewer",
        workspace: "~/.openclaw/workspace-reviewer",
        tools: { allow: ["read"] },
      },
    ],
  },
}
```

### Example F: Personal Assistant + Restricted Agents

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Personal Assistant",
        workspace: "~/.openclaw/workspace",
        sandbox: { mode: "off" },
      },
      {
        id: "family",
        name: "Family Bot",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent" },
        tools: {
          allow: ["read"],
          deny: ["exec", "write", "edit", "apply_patch", "process", "browser"],
        },
      },
    ],
  },
  bindings: [
    {
      agentId: "family",
      match: {
        provider: "whatsapp",
        accountId: "*",
        peer: { kind: "group", id: "120363424282127706@g.us" },
      },
    },
  ],
}
```

---

## 17. CLI Command Reference

### Agent Management

```bash
openclaw agents add <name>          # Create new agent
openclaw agents list --bindings     # List agents with routing
openclaw agents list                # List all agents
```

### Channel Management

```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
openclaw channels status --probe
```

### Gateway Management

```bash
openclaw gateway restart
openclaw gateway start
openclaw gateway stop
```

### Diagnostics

```bash
openclaw doctor                     # Validate config
openclaw doctor --fix               # Auto-repair
openclaw health                     # Health check
openclaw status                     # System status
```

### Session Management

```bash
openclaw sessions list
openclaw sessions history <sessionKey>
```

### Skills

```bash
openclaw skills list
openclaw skills install <name>
clawhub install <skill-slug>
clawhub update --all
```

### Sub-Agents

```bash
/subagents spawn <agentId> <task>
/subagents list
/subagents kill <id|#|all>
/subagents log <id|#>
/subagents info <id|#>
/subagents send <id|#> <message>
/subagents steer <id|#> <message>
```

---

## Key Architectural Takeaway

> "This lets **multiple people** share one Gateway server while keeping their AI 'brains' and data isolated."

Each agent is a fully isolated persona with:
- Dedicated workspace (files, memory, personality)
- Per-agent state directory (auth, sessions)
- Independent session store
- Configurable sandbox and tool restrictions
- Individual model selection
- Routing rules that deterministically direct messages

The gateway is the single entry point that routes messages to the correct agent based on binding rules, with sub-agents providing hierarchical delegation for complex tasks.
