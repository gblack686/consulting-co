---
type: expert-file
parent: "[[pi/_index]]"
file-type: command
command-name: "create-extension"
human_reviewed: false
tags: [expert-file, command, scaffolding]
---

# Pi Agent Expert - Create Extension

> Scaffold a new Pi extension with the correct structure, events, and UI APIs.

## Purpose
Generate a complete, working Pi extension TypeScript file based on the user's requirements. Uses the extension skeleton, event system, and TUI APIs from expertise.md.

## Usage
```
/experts:pi:create-extension [description]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Write`, `Edit`

---

## Resolution Strategy

1. **Read `expertise.md`** Parts 2-3 for extension skeleton, events, and TUI APIs
2. **Read reference extensions** matching the requested category
3. **Scaffold the extension** with correct imports, events, and structure
4. **Write to** `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions/{name}.ts`

---

## Extension Categories & Reference Files

| Category | Reference Extension | Key APIs |
|----------|-------------------|----------|
| UI / Footer | `minimal.ts`, `tool-counter.ts` | `setFooter`, `setStatus`, theme tokens |
| UI / Widget | `tool-counter-widget.ts` | `setWidget`, `invalidate()` |
| UI / Header | `pure-focus.ts` | `setHeader` |
| UI / Theme | `theme-cycler.ts` | `registerShortcut`, `registerCommand` |
| Safety | `damage-control.ts` | `tool_call` blocking, YAML config |
| Discipline | `purpose-gate.ts`, `tilldone.ts` | `input` blocking, `before_agent_start` injection |
| Multi-Agent | `agent-team.ts`, `agent-chain.ts` | `registerTool`, `registerCommand`, `setWidget` |
| Observability | `session-replay.ts` | Overlays, event accumulation |
| Cross-tool | `cross-agent.ts` | File scanning, `registerCommand` |

---

## Scaffold Template

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // === State ===
  // Define mutable state here

  // === Session Lifecycle ===
  pi.on("session_start", async (_event, ctx) => {
    // Initialize UI, load persisted state
    // ctx.ui — UI APIs
    // ctx.cwd — working directory
    // ctx.model — current model info
  });

  pi.on("session_shutdown", async (_event, ctx) => {
    // Cleanup, save state
  });

  // === Input Processing ===
  // pi.on("input", async (event, ctx) => {
  //   // event.text — user's input
  //   // return { action: "block", reason: "..." }  // block input
  //   // return { text: "modified text" }            // modify input
  // });

  // pi.on("before_agent_start", async (event, ctx) => {
  //   // event.systemPrompt — current system prompt
  //   // return { systemPrompt: event.systemPrompt + "\n\nExtra instructions" }
  // });

  // === Tool Events ===
  // pi.on("tool_call", async (event, ctx) => {
  //   // event.toolName, event.args
  //   // return { action: "block", reason: "..." }  // block tool
  //   // return { args: modifiedArgs }               // modify args
  // });

  // pi.on("tool_result", async (event, ctx) => {
  //   // event.toolName, event.result
  //   // return { result: modifiedResult }           // modify result
  // });

  // === Agent Lifecycle ===
  // pi.on("agent_start", async (_event, ctx) => {});
  // pi.on("agent_end", async (_event, ctx) => {});
  // pi.on("turn_start", async (_event, ctx) => {});
  // pi.on("turn_end", async (_event, ctx) => {});

  // === Message Events ===
  // pi.on("message_start", async (_event, ctx) => {});
  // pi.on("message_end", async (event, ctx) => {
  //   // event.usage — token counts
  // });

  // === Custom Tools ===
  // pi.registerTool({
  //   name: "my_tool",
  //   description: "Does something",
  //   parameters: Type.Object({ input: Type.String() }),
  //   execute: async (args) => ({ result: "done" })
  // });

  // === Commands ===
  // pi.registerCommand("mycmd", async (args, ctx) => {
  //   // /mycmd handler
  // });

  // === Shortcuts ===
  // pi.registerShortcut("ctrl+x", async (ctx) => {
  //   // Safe keys: ctrl+x, ctrl+q, ctrl+h, f1-f12
  // });
}
```

---

## Scaffolding Workflow

### Step 1: Classify the Request

Determine which category the extension falls into (UI, Safety, Discipline, Multi-Agent, Observability, Cross-tool).

### Step 2: Select Reference Extension

Read the closest reference extension from the table above to understand the pattern.

### Step 3: Select Events

Map requirements to events:
- Need to gate input? → `input` (blocking)
- Need to inject context? → `before_agent_start`
- Need to audit tools? → `tool_call` (blocking)
- Need live progress? → `tool_execution_start/update/end`
- Need cost tracking? → `turn_end`, `message_end`
- Need UI? → `session_start` for setup

### Step 4: Select UI Surfaces

- Persistent info → `setFooter` or `setWidget`
- Compact status → `setStatus`
- User interaction → `input()`, `select()`, `confirm()`
- Full-screen → Overlay

### Step 5: Apply Theme Tokens

Use `theme.fg(token, text)`:
- `success` — primary values (counts, active states)
- `accent` — secondary values (percentages, tool names)
- `warning` — punctuation, cost values
- `dim` — labels, separators
- `muted` — subdued text
- `error` — error states

### Step 6: Write the Extension

Write to `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions/{name}.ts`

### Step 7: Create Justfile Recipe

Add to `justfile`:
```just
ext-{name}:
    pi -e extensions/{name}.ts -e extensions/theme-cycler.ts
```

### Step 8: Test

```bash
just ext-{name}
# Or directly:
pi -e extensions/{name}.ts
```

---

## Output Format

```markdown
## Extension Created

**File**: `extensions/{name}.ts`
**Category**: {category}
**Events Used**: {list}
**UI Surfaces**: {list}
**Keybindings**: {list or "none"}

## How to Run

```bash
just ext-{name}
# Or:
pi -e extensions/{name}.ts -e extensions/theme-cycler.ts
```

## What It Does

{1-2 sentence description}

## Key Implementation Details

- {detail 1}
- {detail 2}
```

---

## Important Constraints

1. **Import only from** `@mariozechner/pi-coding-agent` and `@mariozechner/pi-tui`
2. **No build step** — file runs directly via jiti
3. **Avoid reserved keybindings** — check Part 3 of expertise.md
4. **Only `input` and `tool_call` can block** — other events are observe-only
5. **Theme tokens are strings** — apply with `theme.fg()`, not CSS
6. **`render(width)` returns `string[]`** — one string per line, handle width truncation
7. **Use `invalidate()`** — call after state changes to trigger re-render
8. **TypeBox for tool schemas** — `import { Type } from "@sinclair/typebox"`
