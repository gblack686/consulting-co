---
type: expert-file
parent: "[[overstory/_index]]"
file-type: command
command-name: "plan"
human_reviewed: false
tags: [expert-file, command, planning]
---

# Overstory Expert - Plan Mode

> Create implementation plans informed by Overstory's architecture, patterns, and conventions.

## Purpose
Create plans for changes to the Overstory codebase or for using Overstory to orchestrate multi-agent work on other projects.

## Usage
```
/experts:overstory:plan [user_request]
```

## Allowed Tools
`Read`, `Grep`, `Glob`, `Agent` (Explore, Plan)

---

## Planning Framework

### Step 1: Classify the Request

| Type | Description | Approach |
|------|-------------|----------|
| **Use Overstory** | User wants to orchestrate agents on their project | Guide `ov init`, config, sling |
| **Extend Overstory** | User wants to add a feature to Overstory | Follow Overstory's conventions |
| **Debug Overstory** | Something isn't working | Use `ov doctor`, inspect logs |
| **New Agent Role** | Define a new agent type | Create base definition + update manifest |
| **New Runtime** | Add support for another coding agent | Implement AgentRuntime interface |
| **New Command** | Add a CLI command | Add to `src/commands/`, register in `src/index.ts` |

---

### Step 2: Understand Overstory Conventions

Before planning, ensure alignment with these patterns:

**TypeScript**:
- Strict mode (`noExplicitAny`, `noUncheckedIndexedAccess`)
- All shared types in `src/types.ts` (single source of truth)
- Bun-native APIs (`bun:sqlite`, `Bun.spawn`, `Bun.file`)
- Biome formatting (tabs, 100 char width)

**Architecture**:
- One file per CLI command in `src/commands/`
- Each subsystem has its own directory (`mail/`, `merge/`, `sessions/`, etc.)
- Custom error types extending `OverstoryError`
- Tests colocated with source (`.test.ts` alongside `.ts`)

**Testing**:
- Never mock what you can use for real
- Real filesystems (`mkdtemp()`), real SQLite (`:memory:`), real git
- Only mock tmux and external APIs

**Config**:
- Project config: `.overstory/config.yaml` (committed)
- Local overrides: `.overstory/config.local.yaml` (gitignored)

---

### Step 3: Context Gathering

Read these files before planning changes to Overstory:

| File | When to Read |
|------|-------------|
| `CLAUDE.md` | Always — primary technical reference |
| `src/types.ts` | Any code change — understand domain types |
| `src/config.ts` | Config-related changes |
| `src/commands/{related}.ts` | Command changes |
| `src/runtimes/types.ts` | Runtime-related changes |
| `CHANGELOG.md` | Understand recent changes |
| `CONTRIBUTING.md` | Contribution guidelines |

---

### Step 4: Plan Output

```markdown
# Overstory Plan: {Title}

## Classification
- **Type**: {use | extend | debug | new-role | new-runtime | new-command}
- **Subsystem**: {commands | agents | mail | merge | runtimes | watchdog | etc.}
- **Risk Level**: {low | medium | high}

## Files to Modify
| File | Change Type | Description |
|------|------------|-------------|
| `src/...` | modify/create | ... |

## Implementation Steps
1. {Step 1}
2. {Step 2}

## Quality Gates
- [ ] `bun test` passes
- [ ] `bun run lint` passes
- [ ] `bun run typecheck` passes

## Considerations
- {Any risks, edge cases, or dependencies}
```

---

## Using Overstory on a Project

When the user wants to USE Overstory (not modify it):

### Quick Start Plan
```bash
cd <project>
ov init --yes                              # Bootstrap .overstory/
ov hooks install                           # Deploy guards
ov coordinator start                       # Start coordinator
ov sling <task> --capability builder       # Spawn worker
ov status                                  # Check fleet
ov merge --all                             # Merge results
ov clean                                   # Teardown
```

### Multi-Agent Plan
1. **Decompose** the task into independent units of work
2. **Assign capabilities**: scout (research), builder (implement), reviewer (validate)
3. **Configure** max concurrent agents, quality gates
4. **Spawn** agents with `ov sling`
5. **Monitor** with `ov dashboard` or `ov status`
6. **Merge** completed branches with `ov merge`
7. **Review** with `ov costs` for token analysis

---

## Source Reference
- Repo: `C:/Users/gblac/OneDrive/Desktop/overstory`
- README: `C:/Users/gblac/OneDrive/Desktop/overstory/README.md`
- CLAUDE.md: `C:/Users/gblac/OneDrive/Desktop/overstory/CLAUDE.md`
- CONTRIBUTING.md: `C:/Users/gblac/OneDrive/Desktop/overstory/CONTRIBUTING.md`
