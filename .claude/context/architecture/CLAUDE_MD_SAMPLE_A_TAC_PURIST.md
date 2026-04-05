# CLAUDE.md - Option A: "The TAC Purist"
# Built on all 8 TAC Tactics as first-class directives

## Identity

This is `consulting-co` - a Claude Code-native consulting operations repo.
Every file, command, and agent follows TAC (Tactical Agentic Coding) principles.

---

## TAC Directives (Non-Negotiable)

### Tactic #1: Stop Coding
- NEVER type application code directly. Use agents, commands, and ADWs.
- Your job is to **plan, review, and orchestrate** - not write code.
- If you catch yourself writing more than 5 lines of code, STOP. Create a command or ADW instead.

### Tactic #2: Adopt the Agent's Perspective
- Before every task, ask: "What context does my agent need to succeed?"
- Always provide: relevant file paths, types, architecture docs, and constraints.
- Reference `.claude/agents/README.md` for the 5-agent architecture.

### Tactic #3: Template Your Engineering
- Solve **problem classes**, not individual problems.
- Before creating a one-off solution, check if a template exists in `.claude/commands/`.
- If you solve a problem twice, create a command. If three times, create an ADW.
- All plans go to `specs/` with validation commands.

### Tactic #4: Stay Out The Loop (PITER)
- **P**rompt: GitHub Issues or slash commands as input
- **I**nput: Well-defined, structured data
- **T**rigger: Hooks, GitHub webhooks, or cron
- **E**nvironment: Isolated execution (git worktrees for parallel work)
- **R**eview: Pull requests with automated validation

### Tactic #5: Always Add Feedback Loops
- Every generated file MUST have a validation path.
- Code changes require: lint + type-check + test.
- Use `/validate` or `/experts:tac:plan_build_improve` for closed-loop execution.
- Never ship without a feedback loop.

### Tactic #6: One Agent, One Prompt, One Purpose
- Each agent in `.claude/agents/` has a single responsibility.
- Don't overload context. Use the R&D framework: **Reduce** bloat, **Delegate** retrieval.
- Keep CLAUDE.md under 200 lines. Use context priming (slash commands) over always-on memory.

### Tactic #7: Target Zero-Touch Engineering
- Progress: In-Loop → Out-Loop → Zero-Touch
- When confidence hits 90%, remove the human review step.
- Use `/adw` for background autonomous workflows.
- Use git worktrees for parallel agent execution.

### Tactic #8: Prioritize Agentics
- Spend 50%+ of engineering time on the **agentic layer** (commands, hooks, agents, ADWs).
- The agentic layer IS the product. Application code is a side effect.
- Every new capability should be a reusable primitive first, application feature second.

---

## Codebase Organization

### File Traceability (Core Principle)
Every generated artifact is timestamped and routed to its canonical location.
Prefix format: `yyyymmdd-hhmmss` (e.g., `20260217-143000-auth-refactor.md`).

| Artifact Type | Destination | Naming Convention |
|---------------|-------------|-------------------|
| Implementation plans | `.claude/specs/` | `yyyymmdd-hhmmss-{slug}.md` |
| Generated context docs | `.claude/context/{group}/` | `yyyymmdd-hhmmss-{topic}.md` |
| ADW outputs | `.claude/adws/` | `yyyymmdd-hhmmss-{workflow}.md` |
| Obsidian notes | Obsidian vault | Use vault templates |
| Proposals & SOWs | `specs/` or `proposals/` | `yyyymmdd-hhmmss-{client}-{type}.md` |

This ensures every artifact is traceable to when it was created, enables chronological
auditing, and prevents filename collisions when the same task is re-planned.

### Port Policy
- Never use port 3000. Use random ports in range **3025-3099**.

### Context Engineering (R&D)
| Strategy | Action |
|----------|--------|
| **Reduce** | No MCP server bloat. Delete unused .mcp.json entries. Keep CLAUDE.md < 200 lines. |
| **Delegate** | Use `/search-knowledge` for dynamic context. Use `/experts:tac:question` for TAC lookups. |

---

## Agentic Primitives Catalog

### Commands (`/command-name`)
| Command | Purpose | TAC Tactic |
|---------|---------|------------|
| `/adw` | Background autonomous workflow | #4, #7 |
| `/plan-build-review` | Three-phase ADW | #3, #5 |
| `/validate` | Comprehensive validation suite | #5 |
| `/check-subscriptions` | Usage across all services | #2 |
| `/sync-claude-ecosystem` | Sync .claude to Obsidian | #3 |
| `/search-knowledge` | Unified knowledge search | #6 |
| `/test-agent` | Test agent prompts | #5 |

### Expert Agents (`/experts:domain:action`)
| Expert | Domain | Key Actions |
|--------|--------|-------------|
| `/experts:tac:*` | TAC methodology | `question`, `plan`, `plan_build_improve`, `self-improve` |
| `/experts:supabase:*` | Vault secrets | `question`, `plan`, `maintenance` |
| `/experts:aws-org:*` | AWS Organization | `question`, `create-account`, `grant-policy` |
| `/experts:openclaw:*` | OpenClaw agent platform | `status`, `run-task`, `deploy-skill` |

**Expert Pattern** (ACT-LEARN-REUSE):
```
ACT    → Expert executes domain task
LEARN  → Expert updates expertise.yaml with new knowledge
REUSE  → Next execution benefits from accumulated expertise
```

### Specialized Agents (`.claude/agents/`)
| Agent | Purpose | Pattern |
|-------|---------|---------|
| Observability | Real-time event capture | Echo |
| Langfuse | Trace logging & analysis | Calculator |
| Graphiti | Knowledge graph builder | Calculator |
| Obsidian | Auto-documentation | Pong |
| Orchestrator | Multi-agent coordination | Orchestrator |

### Skills (`.claude/skills/`)
| Skill | Purpose |
|-------|---------|
| `youtube-video-archiver` | Scrape, transcribe, archive videos |
| `aws-config-manager` | AWS credentials & secrets |
| `github-actions-manager` | CI/CD pipeline management |
| `plan-build-review-adw` | Autonomous development workflow |
| `anthropic-memory` | Session tracking & entity extraction |
| `obsidian-agent-archiver` | Document agents into Obsidian KB |

### Command Groups
| Group | Commands | Purpose |
|-------|----------|---------|
| `graphiti:*` | `search`, `stats`, `daily`, `weekly`, `export` | Knowledge graph operations |
| `scoping:*` | `consulting-questions`, `analyze-transcripts`, `generate-adr` | Client consulting |
| `ecosystem:*` | `scan-claude-folder`, `copy-to-obsidian`, `assign-mtg-cards` | Ecosystem management |
| `bowser:*` | `hop-automate`, `blog-summarizer`, `youtube-transcript` | Browser automation |
| `codebase-knowledge-extract:*` | `parse-code`, `build-graph`, `store-graphiti` | Codebase analysis |

---

## ADW Patterns

| Pattern | Workflow | Autonomy Level |
|---------|----------|----------------|
| `plan_build` | Plan → Build | Out-Loop |
| `plan_build_review` | Plan → Build → Review | Out-Loop |
| `plan_build_review_fix` | Plan → Build → Review → Fix | Zero-Touch |
| `sdlc` | Full lifecycle | Zero-Touch |
| `*_iso` | Isolated in git worktree | Zero-Touch |

---

## Validation Strategy (Tactic #5)

```yaml
validation:
  linting: [ruff, eslint]
  type_check: [pyright, tsc]
  unit_tests: [pytest, vitest]
  integration: [test_integration.py]
  build: [npm run build]
  custom_evals: [/validate, /ultimate_validate_command]
```

---

## Agentic KPIs

Track these metrics to measure agentic maturity:
- **Attempts ↓** - Fewer tries per task
- **Streak ↑** - Consecutive one-shot successes
- **Size ↑** - Larger tasks handled autonomously
- **Presence ↓** - Less human intervention required

---

## Quick Reference

```
# Plan with TAC expertise
/experts:tac:plan "your task description"

# Execute autonomous workflow
/adw "your task description"

# Validate everything
/validate

# Search accumulated knowledge
/search-knowledge "query"

# Check system health
/experts:openclaw:status
```
