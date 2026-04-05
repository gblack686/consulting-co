---
type: expert
name: "pi"
domain: [pi-agent, extensions, tui, coding-agent, multi-model]
specialty: "Pi Coding Agent — Programmable Terminal Agent Platform"
status: active
created: 2026-03-02
updated: 2026-03-02
tags: [expert, domain-expertise, pi-agent, extensions, tui]
---

# Pi Agent Expert

## Domain Overview
Pi is a minimal, MIT-licensed, model-agnostic terminal coding agent by Mario Zechner (libGDX creator). Unlike batteries-included tools, Pi ships 4 tools and a ~200-token system prompt — everything else is opt-in via in-process TypeScript extensions. Pi is the runtime that powers OpenClaw (145K stars).

## Expert Type
**Platform Expert** — Deep expertise in Pi's extension system, TUI APIs, agent orchestration, multi-model workflows, and the distinction between Pi (programmable platform) and product-style agents (Claude Code, OpenCode).

## Core Insight
> **Key Insight**: Pi is a platform, not a product. The extension system runs in-process (same runtime as the agent loop) with 25+ typed events, full UI control, and zero build step. The ceiling is whatever you can build in TypeScript.

## Key Capabilities
- **25+ Extension Events**: 7 categories — session, input, agent lifecycle, tool calls, tool execution, messages, context
- **Full TUI Control**: setHeader, setFooter, setStatus, setWidget, overlays, dialogs, custom editors
- **4 Core Tools**: read, write, edit, bash (+3 optional: grep, find, ls)
- **324 Models**: 20+ native providers, model switching mid-session, different models per sub-agent
- **Agent Orchestration**: Agent teams, agent chains, subagent widgets, dispatcher pattern
- **Session Architecture**: JSONL tree with branching/forking/labels (not linear)

## Frameworks

### Pi Architecture Stack
| Layer | Package | Role |
|-------|---------|------|
| **pi-ai** | `@mariozechner/pi-ai` | LLM calls, streaming, OAuth, 324 models |
| **pi-agent-core** | `@mariozechner/pi-agent-core` | Agent types, tool definitions, session management |
| **pi-coding-agent** | `@mariozechner/pi-coding-agent` | 4 tools, SKILL.md loading, extension API |
| **pi-tui** | `@mariozechner/pi-tui` | Terminal UI, 51 color tokens, rendering |

### Extension Event Categories
| Category | Events | Key Capability |
|----------|--------|---------------|
| Session | session_start, session_shutdown, session_before_compact | Lifecycle + custom compaction |
| Input | input, before_agent_start | Block/transform prompts, inject system prompts per-turn |
| Agent | agent_start, agent_end, turn_start, turn_end | Granular lifecycle tracking |
| Tool Calls | tool_call, tool_result | Block/modify tool args, transform results |
| Tool Execution | tool_execution_start, _update, _end | Real-time streaming of tool progress |
| Messages | message_start, message_update, message_end | Token-by-token access |
| Context | context, model_select | Direct context manipulation, model switch events |

### UI Surface APIs
| API | What It Controls |
|-----|-----------------|
| `ctx.ui.setHeader()` | Replace logo/keybinding hints |
| `ctx.ui.setFooter()` | Custom footer (model, tokens, cost, git branch) |
| `ctx.ui.setStatus()` | Status line with themed colors |
| `ctx.ui.setWidget(key, renderFn)` | Persistent panels above/below editor |
| `ctx.ui.select()` | Selection dialog |
| `ctx.ui.confirm()` | Confirmation dialog |
| `ctx.ui.input()` | Text input dialog |
| `ctx.ui.notify()` | Notification |
| Overlays | Full-screen apps (session replay, games, QA tools) |

## Expert Files
| File | Purpose |
|------|---------|
| [[pi/expertise\|expertise]] | Complete Pi mental model (extensions, events, UI, tools) |
| [[pi/question\|question]] | Query Pi knowledge without making changes |
| [[pi/plan\|plan]] | Plan Pi extensions or configurations |
| [[pi/self-improve\|self-improve]] | Update expertise from pi-vs-claude-code repo |
| [[pi/create-extension\|create-extension]] | Scaffold a new Pi extension |

## Source Locations

### SOURCE 1: pi-vs-claude-code (Extensions Playground)
```
C:\Users\gblac\OneDrive\Desktop\tac\pi-vs-claude-code
├── extensions/          16 extension .ts files
├── .pi/agents/          Agent definitions + teams.yaml + agent-chain.yaml
├── CLAUDE.md            Project conventions
├── COMPARISON.md        Claude Code vs Pi feature comparison
├── PI_VS_OPEN_CODE.md   Pi vs OpenCode deep comparison
├── TOOLS.md             Pi's 4 built-in tool signatures
├── THEME.md             Theme color conventions
└── RESERVED_KEYS.md     Keybinding reference
```

### SOURCE 2: Pi npm packages
```
@mariozechner/pi-coding-agent@0.55.0 (globally installed)
@mariozechner/pi-ai, pi-agent-core, pi-tui (dependencies)
```

## Related
- [[tac/_index|TAC Expert]] — Methodology that Pi implements
- [[hooks/_index|Hooks Expert]] — Claude Code hooks (Pi's equivalent: extension events)
- [[openclaw/_index|OpenClaw Expert]] — Gateway platform built on Pi runtime
