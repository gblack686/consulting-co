---
type: expert-file
parent: "[[pi/_index]]"
file-type: expertise
human_reviewed: false
source: pi-vs-claude-code repo + npm packages + official docs
last_validated: 2026-03-02
local_clone_root: C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code
tags: [expert-file, mental-model, pi-agent, extensions]
---

# Pi Agent Expertise (Complete Mental Model)

> **Sources**: pi-vs-claude-code repo (16 extensions), COMPARISON.md, PI_VS_OPEN_CODE.md, TOOLS.md, THEME.md, RESERVED_KEYS.md
> **Package**: `@mariozechner/pi-coding-agent@0.55.0` (globally installed)
> **Docs**: https://docs.openclaw.ai (Pi section)

---

## Part 1: What Pi Is

Pi is a **programmable coding agent platform** — a minimal harness with 4 tools, ~200-token system prompt, and 25+ in-process TypeScript extension events. Created by Mario Zechner (libGDX, 24.8K stars). MIT licensed.

**Philosophy**: "If I don't need it, it won't be built. Build what you need."

**Pi is NOT**: A batteries-included product. No built-in plan mode, no MCP, no permissions, no web search, no sub-agents, no teams. All of these can be built with extensions.

**Pi IS**: A race car chassis. You design the body, aero, and electronics.

### Architecture
```
pi-ai           → LLM calls, streaming, OAuth, 324 models, 20+ providers
pi-agent-core   → Agent types, tool definitions, session management
pi-coding-agent → 4 tools, SKILL.md loading, ExtensionAPI, jiti runtime
pi-tui          → Terminal UI, 51 color tokens, Box/Text/Container/Spacer
```

### The 4 Built-in Tools
```typescript
read(path, limit?, offset?): string     // Read files + images
write(path, content): void              // Create/overwrite files
edit(path, oldText, newText): void      // Surgical find-and-replace
bash(command, timeout?): string         // Shell execution with streaming
```

Optional tools via `--tools` flag: `grep`, `find`, `ls`

---

## Part 2: Extension System

### How Extensions Work
- **In-process TypeScript** — runs in the same Bun/Node.js runtime as the agent loop
- **Zero build step** — `.ts` files executed via jiti at runtime
- **Composable** — stack with `-e` flags: `pi -e ext1.ts -e ext2.ts`
- **Ephemeral testing** — `pi -e npm:@foo/bar` try without installing

### Extension Skeleton
```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    // ctx.ui — UI APIs
    // ctx.model — current model info
    // ctx.cwd — working directory
    // ctx.sessionManager — session state
    // ctx.getContextUsage() — context window usage
  });

  pi.on("tool_call", async (event, ctx) => {
    // event.toolName, event.args
    // return { action: "block", reason: "..." }  // block tool
    // return { args: modifiedArgs }               // modify args
  });

  pi.registerTool({
    name: "my_tool",
    description: "Does something",
    parameters: Type.Object({ input: Type.String() }),
    execute: async (args) => ({ result: "done" })
  });

  pi.registerCommand("mycmd", async (args, ctx) => {
    // /mycmd handler
  });

  pi.registerShortcut("ctrl+x", async (ctx) => {
    // keyboard shortcut handler
  });
}
```

### All 25+ Extension Events

**Session Events:**
| Event | When | Can Block? | Key Use |
|-------|------|-----------|---------|
| `session_start` | Session begins | No | Initialize UI, load state |
| `session_shutdown` | Session ends | No | Cleanup, save state |
| `session_before_compact` | Before compaction | No | Replace compaction logic entirely |
| `session_compact` | After compaction | No | React to compaction |
| `session_before_fork` | Before branch fork | No | Pi-only session tree |
| `session_fork` | After branch fork | No | |
| `session_before_switch` | Before branch switch | No | |
| `session_switch` | After branch switch | No | |
| `session_before_tree` | Before tree view | No | |
| `session_tree` | After tree view | No | |

**Input Events:**
| Event | When | Can Block? | Key Use |
|-------|------|-----------|---------|
| `input` | User submits prompt | **Yes** | Gate input, transform text, inject context |
| `before_agent_start` | Before agent processes | No (modify) | Inject system prompt per-turn, modify prompt |

**Agent Lifecycle:**
| Event | When | Can Block? | Key Use |
|-------|------|-----------|---------|
| `agent_start` | Agent begins | No | Start timers |
| `agent_end` | Agent finishes | No | Stop timers, summarize |
| `turn_start` | Turn begins | No | Turn counting |
| `turn_end` | Turn ends | No | Cost accumulation |

**Tool Events:**
| Event | When | Can Block? | Key Use |
|-------|------|-----------|---------|
| `tool_call` | Before tool executes | **Yes** | Block, modify args, audit |
| `tool_result` | After tool completes | No (modify) | Transform results, log |
| `tool_execution_start` | Tool begins running | No | Live progress UI |
| `tool_execution_update` | Tool output streaming | No | Real-time output display |
| `tool_execution_end` | Tool finishes | No | Tool counters, stats |

**Message Events:**
| Event | When | Can Block? | Key Use |
|-------|------|-----------|---------|
| `message_start` | Response begins | No | Typing indicators |
| `message_update` | Token streamed | No | Token-by-token access |
| `message_end` | Response complete | No | Accumulate costs |

**Other Events:**
| Event | When | Can Block? | Key Use |
|-------|------|-----------|---------|
| `model_select` | Model changed | No | React to model switches |
| `context` | Context window access | No | Direct message manipulation |
| `user_bash` | User types !! command | No | Track user shell commands |
| `BashSpawnHook` | Before bash spawns | No (modify) | Modify command/cwd/env |

### Typed Tool Call Narrowing
```typescript
import { isToolCallEventType } from "@mariozechner/pi-coding-agent";

pi.on("tool_call", async (event, ctx) => {
  if (isToolCallEventType(event, "bash")) {
    // event.args.command is typed as string
    if (event.args.command.includes("rm -rf")) {
      return { action: "block", reason: "Dangerous command" };
    }
  }
  if (isToolCallEventType(event, "write")) {
    // event.args.path, event.args.content typed
  }
});
```

---

## Part 3: TUI APIs

### UI Surfaces
```typescript
// Header — replace logo and keybinding hints
ctx.ui.setHeader((tui, theme) => ({
  render(width): string[] { return ["custom header"]; },
  invalidate() {},
}));

// Footer — model, tokens, cost, branch, tool counts
ctx.ui.setFooter((tui, theme, footerData) => ({
  dispose: () => {},
  invalidate() {},
  render(width): string[] { return [line1, line2]; },
}));

// Status line — compact info
ctx.ui.setStatus("key", "value");

// Widgets — persistent panels
ctx.ui.setWidget("key", (tui, theme) => ({
  render(width): string[] { return ["widget content"]; },
  invalidate() {},
}));

// Dialogs
const answer = await ctx.ui.input("Question?", "placeholder");
const choice = await ctx.ui.select("Pick one", items);
const ok = await ctx.ui.confirm("Are you sure?");

// Notifications
ctx.ui.notify("Message", "warning");
```

### Theme System
51 color tokens. Apply with `theme.fg(token, text)`:

| Token | Role | Used For |
|-------|------|----------|
| `success` | Primary value | Token counts, hash fills, branch name |
| `accent` | Secondary value | Percentages, tool names |
| `warning` | Punctuation/frame | Brackets, parens, cost |
| `dim` | Filler/spacing | Dashes, labels, separators |
| `muted` | Subdued text | CWD name, fallback states |
| `error` | Error state | Error messages |
| `borderMuted` | Borders | Separator lines |

### ANSI Helpers
```typescript
import { truncateToWidth, visibleWidth, wrapTextWithAnsi } from "@mariozechner/pi-tui";
import { DynamicBorder } from "@mariozechner/pi-coding-agent";
import { Container, Text, Box, Spacer } from "@mariozechner/pi-tui";
```

### Keybindings
**Reserved (cannot override):** escape, ctrl+c, ctrl+d, ctrl+z, shift+tab, ctrl+p, ctrl+shift+p, ctrl+l, ctrl+o, ctrl+t, ctrl+g, alt+enter, enter, ctrl+k

**Safe for extensions:** ctrl+x, ctrl+q, ctrl+h (with caution), f1-f12

---

## Part 4: Agent Definitions

### Format (.pi/agents/*.md)
```markdown
---
name: scout
description: Fast recon and codebase exploration
tools: read,grep,find,ls
---
You are a scout agent. Investigate the codebase quickly and report findings concisely.
Do NOT modify any files. Focus on structure, patterns, and key entry points.
```

Fields:
- `name` — agent identifier (kebab-case)
- `description` — shown in team grid, select dialogs
- `tools` — comma-separated tool restrictions
- Body — system prompt injected into agent

### Teams (.pi/agents/teams.yaml)
```yaml
full:
  - scout
  - planner
  - builder
  - reviewer
  - documenter
  - red-team

plan-build:
  - planner
  - builder
  - reviewer

frontend:
  - planner
  - builder
  - bowser
```

### Agent Chains (.pi/agents/agent-chain.yaml)
```yaml
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

Variables: `$ORIGINAL` = user's original prompt, `$INPUT` = previous step's output

---

## Part 5: The 16 Extensions (pi-vs-claude-code)

### UI Customization
| # | Extension | What It Does |
|---|-----------|-------------|
| 1 | `pure-focus` | Strips footer + status line. Zen mode. |
| 2 | `minimal` | Single-line footer: model + 10-block context meter |
| 3 | `theme-cycler` | Ctrl+X/Q cycle themes, /theme picker, 51 color tokens |
| 4 | `tool-counter` | Rich 2-line footer: model, context, tokens, cost, branch, tool tally |
| 5 | `tool-counter-widget` | Persistent widget with per-tool colored badges |

### Discipline & Safety
| # | Extension | What It Does |
|---|-----------|-------------|
| 6 | `purpose-gate` | Forces intent declaration. Blocks all prompts until purpose set. Injects into system prompt per-turn. |
| 7 | `tilldone` | Task-driven work. Must define tasks before using tools. Three-state lifecycle (idle/inprogress/done). |
| 8 | `damage-control` | Safety auditing via YAML rules. Intercepts tool calls, blocks dangerous patterns, zero-access paths. |

### Multi-Agent
| # | Extension | What It Does |
|---|-----------|-------------|
| 9 | `cross-agent` | Loads commands from .claude/, .gemini/, .codex/ directories. Cross-tool compatibility. |
| 10 | `system-select` | `/system` swaps system prompt from agent .md files. Restricts tools per agent. |
| 11 | `subagent-widget` | `/sub` spawns background agents. `/subcont` continues. Live streaming widgets. |
| 12 | `agent-team` | Dispatcher-only orchestrator. Grid dashboard. Delegates via `dispatch_agent` tool. |
| 13 | `agent-chain` | Sequential pipeline. plan-build-review, scout-flow, plan-review-plan chains. |

### Meta & Observability
| # | Extension | What It Does |
|---|-----------|-------------|
| 14 | `pi-pi` | Meta-agent that builds Pi agents. Parallel expert research. Firecrawl docs. |
| 15 | `session-replay` | Scrollable timeline overlay of session history. |
| 16 | N/A | `themeMap.ts` — shared theme defaults across all extensions |

---

## Part 6: Key Differences from Claude Code

| Dimension | Claude Code | Pi |
|-----------|------------|-----|
| Runtime | Proprietary CLI | MIT, open source |
| System prompt | ~10K tokens | ~200 tokens |
| Extensions | Shell hooks (external) | TypeScript (in-process) |
| Events | 14 hook events | 25+ extension events |
| UI customization | Status line only | Full TUI (header, footer, status, widgets, overlays, dialogs) |
| Models | Claude-only (gateway workaround) | 324 models, 20+ providers native |
| Sub-agents | Native Task tool, 7 parallel | Build via extensions |
| MCP | Native first-class | Not built-in (by design) |
| Permissions | 5 modes, deny-first | YOLO default (build with extensions) |
| Session format | Linear | JSONL tree (branching/forking) |
| State persistence | No built-in | `pi.appendEntry()` survives restarts |

### 8 Hook Points Pi Has That Claude Code Doesn't
1. `input` — block/transform user prompts before agent sees them
2. `before_agent_start` — inject system prompt per-turn dynamically
3. `agent_start`/`agent_end`/`turn_start`/`turn_end` — granular lifecycle
4. `tool_execution_start`/`_update`/`_end` — real-time tool streaming
5. `context` — direct context window manipulation
6. `model_select` — react to model switches
7. `session_before_fork`/`session_fork` — session branching
8. `BashSpawnHook` — intercept at process spawn level

---

## Part 7: Programmatic & SDK

### CLI Modes
```bash
pi                           # Interactive TUI
pi -p "prompt"               # Print mode (non-interactive)
pi --mode json               # JSONL event streaming
pi --mode rpc                # RPC mode (26+ commands, any language)
pi -e extensions/foo.ts      # Load extension
pi -e npm:@foo/bar           # Ephemeral npm extension
pi --tools grep,find,ls      # Enable optional tools
```

### Node.js SDK
```typescript
import { createAgentSession } from "@mariozechner/pi-coding-agent";

const session = await createAgentSession({
  model: "anthropic:claude-sonnet-4-6",
  cwd: "/path/to/project",
  extensions: ["./my-ext.ts"],
});

// Full internal API access
session.steer("new direction");      // interrupt and redirect
session.followUp("continue with");   // queue after completion
const stats = session.getSessionStats(); // tokens, cost, tool calls
await session.exportToHtml("output.html");
```

### Registration APIs
```typescript
pi.registerTool({ name, description, parameters, execute })
pi.registerCommand("name", handler)
pi.registerShortcut("ctrl+x", handler)
pi.registerFlag("--my-flag", handler)
pi.registerProvider(providerConfig)
pi.appendEntry(data)  // persist to session JSONL
pi.events  // shared event bus between extensions
```

---

## Part 8: Running Pi

### Justfile Recipes (pi-vs-claude-code)
```bash
just pi                    # Vanilla
just ext-minimal           # Compact footer + themes
just ext-purpose-gate      # Declare intent first
just ext-tool-counter      # Rich footer with costs
just ext-subagent-widget   # Background agents
just ext-agent-team        # Dispatcher + grid
just ext-agent-chain       # Sequential pipelines
just ext-pi-pi             # Meta-agent builder
just ext-damage-control    # Safety auditing
just ext-session-replay    # Timeline overlay
```

### Extension Stacking Patterns
```bash
# Compact + themes (default combo)
pi -e extensions/minimal.ts -e extensions/theme-cycler.ts

# Safety + observability
pi -e extensions/damage-control.ts -e extensions/tool-counter.ts -e extensions/theme-cycler.ts

# Full orchestration
pi -e extensions/agent-team.ts -e extensions/theme-cycler.ts

# Multi-agent pipeline
pi -e extensions/agent-chain.ts -e extensions/theme-cycler.ts
```

### Windows Notes
- `pi` installed at `C:/Users/gblac/AppData/Roaming/npm/pi`
- Needs `fd` and `rg` in PATH (installed at `~/bin/`)
- `just open` recipe uses macOS `osascript` — use `just ext-*` directly on Windows
- Package manager: `bun` (not npm/yarn)
