# TAC Agent Composer Redesign

**Date:** 2026-02-23
**Status:** Awaiting Approval
**Scope:** Redesign tac-expert-agent from educational advisor → agentic architecture composer

---

## Problem Statement

The current `tac-expert-agent` teaches theory. Its Report block outputs classification labels.
The user still has to figure out what to actually build.

The new agent outputs a **working blueprint** — a structured, copy-pasteable spec that wires
together real primitives (ADW patterns, hooks, agent files, prompt templates, validation
commands) that a coding agent can execute directly.

---

## Core Redesign: Composer Not Educator

### Stop Doing (current)
- Explains the 8 tactics as a lesson
- Returns classification labels as output
- Has "Self-Improve Scheduled: yes/no" field
- Includes PITER framework prose as deliverable

### Start Doing (new)
- Reads task description
- Selects concrete primitives from internal catalog
- Produces a typed, structured blueprint with exact filenames + commands + wiring
- Blueprint is directly executable by a coding agent

---

## Files to Create / Overwrite

| File | Action |
|------|--------|
| `consulting-co/.claude/agents/tac-expert-agent.md` | CREATE (does not exist) |
| `hyperliquid-python-sdk/.claude/agents/tac-expert-agent.md` | CREATE (does not exist) |
| `afs/sample-multi-tenant-agent-core-app/.claude/agents/tac-expert-agent.md` | OVERWRITE (full redesign) |

**NOT modified:** any `expertise.md`, `_index.md`, `question.md`, `plan.md`, `self-improve.md` files.

---

## New Agent Frontmatter (all three)

```yaml
---
name: tac-expert-agent
description: >
  TAC agentic architecture composer. Given a task, assembles a working blueprint
  of primitives (ADWs, hooks, agents, prompt templates, validation loops).
  Invoke with: "design an agent", "compose architecture", "what primitives do I need",
  "tac blueprint", "adw", "plan build improve", "wire up hooks",
  "agent pattern", "validation loop", "compose workflow", "tac", "tactical agentic".
model: opus
color: purple
tools: Read, Glob, Grep, Write
---
```

---

## Primitive Library (agent's internal catalog)

### ADW Patterns
| ADW | When to Select |
|-----|---------------|
| `plan_build_improve` | New feature, learnings matter |
| `plan_build_review` | Changes needing human approval gate |
| `plan_build_test` | Feature with automated test suite |
| `plan_build_test_review` | Full SDLC, highest quality |
| `maintenance` | Health check, audit, cleanup |
| `question` | Read-only research |
| `self-improve` | Post-implementation expertise update |

### Agent Patterns
| Pattern | Best For |
|---------|----------|
| Calculator | File editing, multi-step tool calls, stateful REPL |
| Router | Task classification, dispatch to specialist agents |
| Pipeline | Sequential SDLC stages with handoff protocol |
| Orchestrator | Fleet management, multi-agent coordination |
| Pong | Single request-response lookups |
| Echo | Event-driven, webhook/cron triggers |

### Hook Selections
| Hook | Event | Wire When |
|------|-------|-----------|
| `stop.py` | Stop | Always — baseline |
| `pre_tool_use.py` | PreToolUse | Dangerous bash operations |
| `post_tool_use.py` | PostToolUse | File edits → lint-on-save |
| `session_start.py` | SessionStart | Projects with env vars / session state |
| `subagent_stop.py` | SubagentStop | Multi-agent orchestration |
| `user_prompt_submit.py` | UserPromptSubmit | Context injection patterns |

### Validation Loops
| Validation | Command |
|------------|---------|
| Python syntax | `python -c "import py_compile; py_compile.compile('{file}', doraise=True)"` |
| Pytest | `pytest {test_file} -v` |
| Ruff lint | `ruff check {file} --fix` |
| Bash syntax | `bash -n {script}.sh` |
| JSON valid | `python -m json.tool {file}` |
| Frontmatter | `grep -n "^---" {file}` |
| TypeScript | `npx tsc --noEmit` |

### Prompt Template Library
| Template | Use For |
|----------|---------|
| Expert Agent | New domain specialist |
| Command: question | Read-only Q&A |
| Command: plan | Planning-only |
| Command: plan_build_improve | Full workflow |
| Command: maintenance | Health check |
| Command: self-improve | Expertise update |
| Expertise file | Domain mental model |

### Context Engineering Blocks
| Block | What to Load |
|-------|-------------|
| Foundation | CLAUDE.md + settings.json |
| Expert | expertise.md for relevant domain |
| Spec | specs/{task}.md |
| Hook | .claude/hooks/*.py + settings.json hooks |
| Agent roster | .claude/agents/*.md |

---

## Composition Logic (Decision Tree)

```
STEP 1 — TASK TYPE
  Produces files/code? → BUILD → continue
  Research only?       → RESEARCH → question ADW + Pong pattern

STEP 2 — RISK
  High-risk (prod/auth/billing)?    → plan_build_review + write_guard hook
  Has automated tests?              → plan_build_test or plan_build_test_review
  Default                           → plan_build_improve

STEP 3 — AGENT PATTERN
  Multi-step file operations? → Calculator
  Routing to specialists?     → Router or Orchestrator
  Single-step?                → Pong
  Event-triggered?            → Echo

STEP 4 — HOOKS
  Always: stop.py
  Has file writes? → post_tool_use.py (lint)
  Has dangerous bash? → pre_tool_use.py (blocking)
  Multi-agent? → subagent_stop.py

STEP 5 — VALIDATION LOOP
  Python touched? → py_compile + pytest
  Shell scripts?  → bash -n check
  settings.json?  → json.tool
  Agent files?    → frontmatter grep
  UI code?        → playwright E2E

STEP 6 — CONTEXT ENGINEERING
  Load only relevant expertise.md files
  Never load all experts at once
```

---

## Blueprint Output Format (replaces Report block)

```markdown
## TAC BLUEPRINT: {task summary}

### Task Classification
- Type: {BUILD | RESEARCH | MAINTENANCE}
- Risk: {HIGH | MEDIUM | LOW}
- Autonomy: {In-Loop | Out-Loop | Zero-Touch}

### Primitives Selected

#### ADW Pattern
- Selected: `{adw_name}`
- Steps: {step 1} → {step 2} → {step 3}

#### Agent Pattern
- Selected: {Calculator | Router | Pipeline | Orchestrator | Pong | Echo}
- Agent file: `.claude/agents/{name}.md`
- Model: {haiku | sonnet | opus}
- Tools: {comma-separated list}

#### Hooks to Wire
| Hook | Event | Handler | Purpose |
|------|-------|---------|---------|
| stop.py | Stop | baseline | TTS + session log |
| post_tool_use.py | PostToolUse | ruff_linter | lint-on-save |

#### Validation Loop
```bash
{validation command 1}
{validation command 2}
```

### Files to Create
| File | Action | Template |
|------|--------|----------|
| `.claude/agents/{name}.md` | CREATE | Expert Agent |
| `specs/{task}-spec.md` | CREATE | Implementation plan |

### Context Engineering
- Load: {file} — reason
- Exclude: {file} — noise

### Execution Command
```bash
{exact command to run the ADW or agent}
```

### Self-Improve Target
After execution, update: `.claude/commands/experts/{domain}/expertise.md`
```

---

## Project-Specific Adaptations

### consulting-co
- Reads: `.claude/commands/experts/tac/expertise.md`
- General purpose — works for any project type

### afs/sample-multi-tenant-agent-core-app (EAGLE)
- Reads: `.claude/commands/experts/tac/expertise.md` (already exists)
- Context blocks: backend, eval, deployment expertise.md
- Validation: adds pytest for EAGLE eval suite + CDK synth for deploy tasks

### hyperliquid-python-sdk
- No tac expert commands exist — includes compressed **inline primitive catalog** as fallback
- Context blocks: quant, discord, kiyotaka expertise.md
- Validation preference: plan_build_test (backtests validate quant correctness)

---

## Anti-Patterns Removed

- No PITER framework explanation as deliverable
- No "Autonomy: In-Loop" classification label as final output
- No "Self-Improve Scheduled: yes/no" field
- No "Key Insight:" prose paragraphs
- No reference to TAC lesson numbers (tac-1 through tac-8)

---

## Validation of Output Files

```bash
grep -n "^---" {agent_file}          # frontmatter present
grep "^name:" {agent_file}           # name: tac-expert-agent
grep "^model:" {agent_file}          # model: opus
grep "^color:" {agent_file}          # color: purple
grep "TAC BLUEPRINT" {agent_file}    # blueprint format present
grep "^## " {agent_file}             # only: Purpose, Instructions, Workflow, Report
```
