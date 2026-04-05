# CLAUDE.md - Option C: "The Composable Architecture"
# Minimal core config + composable primitives. TAC principles drive structure.

## Core Identity

Consulting-co. Agentic-first. Every capability is a composable primitive.

---

## Constraints

- Generated files → `.claude/context/{group}/*.md`
- Obsidian → `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation` (use templates)
- Ports → 3025-3099
- OAuth → Never set `ANTHROPIC_API_KEY` in .env (CLI handles auth)

## File Traceability

Every generated artifact gets a timestamp prefix: `yyyymmdd-hhmmss-{slug}.md`.
No exceptions. This is how we audit, deduplicate, and trace decisions back to their origin.

```
.claude/specs/20260217-143000-auth-redesign.md        ← Plan
.claude/context/research/20260217-150000-oauth-options.md  ← Research
.claude/adws/20260217-160000-plan-build-auth.md       ← ADW output
proposals/20260217-170000-acme-chatbot-sow.md         ← Client deliverable
```

When an expert runs `/experts:{domain}:plan`, the output goes to `.claude/specs/` with this prefix.
When a plan is re-run, the new timestamp creates a new file — old plans are never overwritten.

---

## Architecture: The Agentic Layer

> "Prioritize your agentic layer. 50%+ of engineering time goes here." — TAC #8

```
┌─────────────────────────────────────────────────────────┐
│  CLAUDE.md (this file)                                  │
│  Minimal config. Context priming only. < 200 lines.     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Commands    │  │   Experts    │  │    Skills     │  │
│  │  (Templates) │  │  (Learning)  │  │  (Complex)    │  │
│  │  TAC #3      │  │  ACT-LEARN   │  │  Multi-step   │  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬────────┘  │
│         │                │                  │           │
│  ┌──────┴────────────────┴──────────────────┴────────┐  │
│  │              Agents (TAC #6)                       │  │
│  │  One agent, one prompt, one purpose                │  │
│  │  Patterns: Pong | Echo | Calculator                │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────┴────────────────────────────┐  │
│  │              ADWs (TAC #4, #7)                     │  │
│  │  Autonomous workflows: plan → build → review       │  │
│  │  Autonomy: In-Loop → Out-Loop → Zero-Touch         │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────┴────────────────────────────┐  │
│  │              Hooks (Event-Driven)                  │  │
│  │  SessionStart | PreToolUse | PostToolUse | Stop    │  │
│  │  Feeds: Observability, Langfuse, Graphiti, Obsidian│  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Validation Layer (TAC #5)                              │
│  Every output has a feedback loop. No exceptions.       │
│  /validate | /ultimate_validate_command | pytest | tsc  │
└─────────────────────────────────────────────────────────┘
```

---

## Primitive Composition Guide

### When to Use What

| Signal | Primitive | Create In | Example |
|--------|-----------|-----------|---------|
| One-off task | Direct prompt | N/A | "Fix this typo" |
| Done it twice | **Command** | `.claude/commands/` | `/consulting:quick-proposal` |
| Domain expertise accumulates | **Expert** | `.claude/commands/experts/{domain}/` | `/experts:aws-org:question` |
| Multi-step with references | **Skill** | `.claude/skills/{name}/` | YouTube archiver |
| Autonomous multi-phase | **ADW** | `.claude/adws/` | Plan → Build → Review |
| Event-driven side effect | **Hook** | `.claude/hooks/` | Log to Langfuse on Stop |
| Dedicated single purpose | **Agent** | `.claude/agents/` | Obsidian KB Expert |

### Composition Patterns

```
# Simple: Command alone
/consulting:quick-proposal "AI chatbot for law firm"

# Composed: Expert + Command
/experts:tac:plan "Add real-time notifications"
# → then execute the plan with:
/plan-build-review

# Orchestrated: ADW with validation
/adw "Implement user authentication"
# → ADW internally runs: plan → build → test → review

# Full stack: Expert + ADW + Hooks + Agents
/experts:tac:plan_build_improve "New microservice"
# → Expert plans with accumulated knowledge (REUSE)
# → ADW executes autonomously (ACT)
# → Hooks log to Langfuse/Graphiti/Obsidian
# → Expert self-improves from results (LEARN)
```

---

## Command Catalog

### Consulting & Scoping
| Command | Input | Output |
|---------|-------|--------|
| `/consulting:quick-proposal` | Client description | Proposal + SOW + timeline |
| `/scoping:consulting-questions` | None | Discovery question set |
| `/scoping:analyze-transcripts` | Call transcript | Architecture questions |
| `/scoping:generate-adr` | Meeting notes | ADR document |

### Knowledge Operations
| Command | Input | Output |
|---------|-------|--------|
| `/search-knowledge` | Query string | Unified search results |
| `/note-create` | Topic | New knowledge note |
| `/note-search` | Query | Matching notes |
| `/graphiti:search` | Concept | Graph entities |
| `/graphiti:daily` | None | Today's Obsidian summary |
| `/graphiti:weekly` | None | Weekly rollup |
| `/graphiti:stats` | None | Graph statistics |

### Automation & DevOps
| Command | Input | Output |
|---------|-------|--------|
| `/adw` | Task description | Background autonomous workflow |
| `/plan-build-review` | Task description | Three-phase execution |
| `/validate` | None | Full validation report |
| `/check-subscriptions` | None | Usage across all services |
| `/sync-claude-ecosystem` | None | Obsidian sync report |
| `/github-scrape` | None | Daily activity report |

### Browser Automation
| Command | Input | Output |
|---------|-------|--------|
| `/bowser:hop-automate` | Workflow name | Automated browser session |
| `/bowser:blog-summarizer` | Blog URL | Summary saved |
| `/bowser:youtube-transcript` | Video URL | Transcript extracted |
| `/bowser:ui-review` | App URL | UI validation report |

---

## Expert Domains

Each expert follows the **ACT-LEARN-REUSE** lifecycle:

```
.claude/commands/experts/{domain}/
├── expertise.yaml          # Accumulated mental model (REUSE source)
├── question.md             # Query the expert
├── plan.md                 # Domain-aware planning
├── self-improve.md         # Validate & update knowledge (LEARN)
└── plan_build_improve.md   # Full cycle: ACT → LEARN → REUSE
```

| Domain | Expertise | Maturity |
|--------|-----------|----------|
| `tac` | TAC methodology, ADW design, agent patterns | Advanced |
| `supabase` | Vault secrets, RLS, migrations | Intermediate |
| `aws-org` | Organization, sub-accounts, IAM, Lightsail | Advanced |
| `openclaw` | Agent platform, skill deployment, SSH | Intermediate |

**Golden Rule**: Never edit `expertise.yaml` manually. Run `/experts:{domain}:self-improve`.

---

## Context Engineering

### The R&D Framework

**Reduce** — Kill context bloat before it kills your agent:
- This CLAUDE.md stays under 200 lines (production)
- Audit `.mcp.json` monthly — delete unused servers
- No inline documentation walls — link to `.claude/context/` instead
- Use context priming (slash commands) over always-on includes

**Delegate** — Let agents fetch what they need:
- `/search-knowledge` for cross-source retrieval
- `/experts:{domain}:question` for domain lookups
- `/graphiti:search` for entity relationships
- `.claude/context/{group}/` for deep reference material

### Context Budget Rule
```
CLAUDE.md        → 200 lines max (always loaded)
Commands         → Loaded on invocation only
Experts          → expertise.yaml loaded on invocation only
Skills           → SKILL.md loaded on invocation only
.claude/context/ → Never auto-loaded, retrieved on demand
```

---

## Validation (TAC #5: Always Add Feedback Loops)

Every primitive type has a validation path:

| Primitive | Validation Method |
|-----------|-------------------|
| Code changes | `/validate` (lint + type + test + build) |
| Plans | `/experts:tac:plan` (TAC-informed review) |
| Expert knowledge | `/experts:{domain}:self-improve` (codebase validation) |
| Consulting deliverables | `/scoping:analyze-transcripts` (requirement alignment) |
| Agent outputs | `/bowser:ui-review` (visual verification) |
| Full workflows | `/plan-build-review` (autonomous three-phase) |

---

## Maturity Progression

```
Level 1: In-Loop           → You prompt, review every step
Level 2: Out-Loop (PITER)  → You prompt once, review the PR
Level 3: Zero-Touch (ZTE)  → You prompt once, agent ships it

Current target: Out-Loop for most workflows, Zero-Touch for proven patterns.
```

### Graduating a Workflow
1. Run In-Loop 3+ times successfully
2. Template the pattern as a command (TAC #3)
3. Add automated validation (TAC #5)
4. Wrap in ADW for Out-Loop execution (TAC #4)
5. When streak > 5, promote to Zero-Touch (TAC #7)
