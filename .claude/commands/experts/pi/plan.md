---
type: expert-file
parent: "[[pi/_index]]"
file-type: command
command-name: "plan"
human_reviewed: false
tags: [expert-file, command, planning]
---

# Pi Agent Expert - Plan Mode

> Plan Pi extensions, agent configurations, or TUI customizations with full knowledge of Pi's architecture.

## Purpose
Create Pi-informed implementation plans for extensions, agent teams, chains, UI customizations, and tool registrations. Ensures plans leverage Pi's extension system correctly and avoid reserved keybindings, blocked events, and anti-patterns.

## Usage
```
/experts:pi:plan [user_request]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Bash`, `Edit`, `Write`, `TodoWrite`

---

## CRITICAL: Pi Knowledge Retrieval

Before planning, load the Pi mental model:
1. Read `expertise.md` for architecture, events, APIs
2. Read source extensions in `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions/` for implementation patterns
3. Read `.pi/agents/` for agent definition format

---

## Pi-Informed Planning Framework

### Step 1: Task Classification

| Task Type | Approach |
|-----------|----------|
| UI tweak | Single extension, TUI APIs only |
| Safety/discipline | Extension with `tool_call` blocking |
| Agent orchestration | Agent definitions + team/chain + dispatcher extension |
| Tool integration | `pi.registerTool()` in extension |
| Full platform | Multiple stacked extensions |

### Step 2: Extension Event Selection

Map requirements to the correct events:

| Need | Event(s) | Can Block? |
|------|----------|-----------|
| Gate user input | `input` | Yes |
| Inject system prompt | `before_agent_start` | No (modify) |
| Block dangerous tools | `tool_call` | Yes |
| Transform tool output | `tool_result` | No (modify) |
| Track costs/tokens | `turn_end`, `message_end` | No |
| Custom UI | `session_start` (setup), `agent_end` (update) | No |
| React to model change | `model_select` | No |
| Real-time tool progress | `tool_execution_start/update/end` | No |

### Step 3: UI Surface Selection

| Need | API |
|------|-----|
| Replace logo/hints | `ctx.ui.setHeader()` |
| Model/cost/branch info | `ctx.ui.setFooter()` |
| Compact status | `ctx.ui.setStatus()` |
| Persistent panel | `ctx.ui.setWidget()` |
| User input | `ctx.ui.input()`, `ctx.ui.select()`, `ctx.ui.confirm()` |
| Alert | `ctx.ui.notify()` |

### Step 4: Keybinding Check

**Reserved (cannot use):** escape, ctrl+c, ctrl+d, ctrl+z, shift+tab, ctrl+p, ctrl+shift+p, ctrl+l, ctrl+o, ctrl+t, ctrl+g, alt+enter, enter, ctrl+k

**Safe:** ctrl+x, ctrl+q, ctrl+h (with caution), f1-f12

### Step 5: Agent Architecture (if multi-agent)

| Complexity | Pattern |
|------------|---------|
| Single expert swap | `system-select` extension + `.pi/agents/*.md` |
| Background workers | `subagent-widget` extension |
| Dispatcher + grid | `agent-team` extension |
| Sequential pipeline | `agent-chain` extension |
| Parallel research | Custom extension with `pi.registerTool()` |

### Step 6: Extension Stacking

Plan which extensions compose together:
```bash
# UI base (pick one)
pi -e extensions/minimal.ts       # Compact footer
pi -e extensions/tool-counter.ts  # Rich footer with costs

# Always add
pi -e extensions/theme-cycler.ts  # Theme support

# Safety (optional)
pi -e extensions/damage-control.ts

# Orchestration (pick one if needed)
pi -e extensions/agent-team.ts    # Dispatcher
pi -e extensions/agent-chain.ts   # Pipeline
```

---

## Plan Output Format

```markdown
# Pi Extension Plan: {Title}

## Classification
- **Type**: {UI tweak | safety | orchestration | tool | platform}
- **Events Required**: {list of events}
- **UI Surfaces**: {header | footer | status | widget | overlay | none}
- **Keybindings**: {list or "none"}

## Extension Architecture
- **New Extensions**: {count}
- **Stacked With**: {existing extensions to compose with}
- **Agent Definitions**: {new .pi/agents/*.md files needed}

## Implementation Steps

### Step 1: {title}
{description}

### Step 2: {title}
{description}

## Files to Create/Modify
| File | Action |
|------|--------|
| `extensions/{name}.ts` | Create |
| `.pi/agents/{name}.md` | Create |

## Validation
- [ ] Extension loads without errors: `pi -e extensions/{name}.ts`
- [ ] Events fire correctly
- [ ] UI renders at various terminal widths
- [ ] No keybinding conflicts
- [ ] Composes with theme-cycler

## Reference Extensions
- {Similar existing extension for pattern reference}
```

---

## Examples

### Example 1: Cost Dashboard Widget
```
/experts:pi:plan "Add a persistent widget showing per-model cost breakdown"
```

**Classification**: UI tweak
**Events**: `turn_end` (accumulate costs), `model_select` (track model)
**UI**: `ctx.ui.setWidget()` with themed colors
**Reference**: `tool-counter-widget.ts`

### Example 2: Agent Pipeline for Code Review
```
/experts:pi:plan "Create a plan-code-review agent chain"
```

**Classification**: Orchestration
**New files**: `.pi/agents/coder.md`, `.pi/agents/code-reviewer.md`, update `agent-chain.yaml`
**Extension**: Use existing `agent-chain.ts`
**Reference**: `agent-chain.yaml` plan-build-review pattern

### Example 3: File Write Approval Gate
```
/experts:pi:plan "Block all file writes to production/ directory"
```

**Classification**: Safety
**Events**: `tool_call` (block write/edit to production/)
**Reference**: `damage-control.ts` path blocking pattern
