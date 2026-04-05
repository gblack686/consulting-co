---
type: expert-file
parent: "[[pi/_index]]"
file-type: command
command-name: "question"
human_reviewed: false
tags: [expert-file, command, read-only]
---

# Pi Agent Expert - Question Mode

> Read-only command to query Pi Agent knowledge without making any changes.

## Purpose
Answer questions about Pi coding agent — extensions, events, UI APIs, agent definitions, multi-model workflows, and comparisons with Claude Code/OpenCode — **without making any code changes**.

## Usage
```
/experts:pi:question [question]
```

## Allowed Tools
`Read`, `Glob`, `Grep` (read-only only)

---

## Resolution Strategy

1. **Read `expertise.md`** for the complete Pi mental model
2. **Read source files** in `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/` for implementation details
3. **Read comparison docs** (COMPARISON.md, PI_VS_OPEN_CODE.md) for cross-tool questions

## Question Categories

### Category 1: Extension Questions
Questions about Pi's extension system, events, APIs.

**Examples**: "What events can block?", "How do I register a tool?", "What's the extension skeleton?"

**Resolution**: Read `expertise.md` Part 2 (Extension System)

### Category 2: UI/TUI Questions
Questions about setHeader, setFooter, setWidget, themes, overlays.

**Examples**: "How do I add a widget?", "What theme tokens are available?", "How do I create an overlay?"

**Resolution**: Read `expertise.md` Part 3 (TUI APIs) + source extensions for examples

### Category 3: Agent Orchestration Questions
Questions about agent teams, chains, subagents, dispatcher pattern.

**Examples**: "How do agent chains work?", "What's the dispatcher pattern?", "How do I define a team?"

**Resolution**: Read `expertise.md` Part 4-5 + `.pi/agents/` files

### Category 4: Comparison Questions
Questions comparing Pi to Claude Code, OpenCode, or other tools.

**Examples**: "What can Pi do that Claude Code can't?", "Is Pi better for X?", "How do hooks compare?"

**Resolution**: Read `COMPARISON.md` and `PI_VS_OPEN_CODE.md` in the pi-vs-claude-code repo

### Category 5: Practical Questions
Questions about running Pi, installing extensions, configuring models.

**Examples**: "How do I start Pi with extensions?", "What models does Pi support?", "How do I use RPC mode?"

**Resolution**: Read `expertise.md` Part 7-8

---

## Source Locations

```
C:\Users\gblac\OneDrive\Desktop\tac\pi-vs-claude-code\
├── extensions/          # 16 extension source files
├── .pi/agents/          # Agent definitions + teams + chains
├── COMPARISON.md        # Claude Code vs Pi comparison
├── PI_VS_OPEN_CODE.md   # Pi vs OpenCode comparison
├── TOOLS.md             # 4 built-in tool signatures
├── THEME.md             # Theme color conventions
└── RESERVED_KEYS.md     # Keybinding reference
```

## Report Format

```markdown
## Answer

{Direct answer}

## Key Points

- {Point 1}
- {Point 2}

## Source Reference

- Primary: `{path/to/source}`

## Code Example (if applicable)

```typescript
// relevant code snippet
```
```
