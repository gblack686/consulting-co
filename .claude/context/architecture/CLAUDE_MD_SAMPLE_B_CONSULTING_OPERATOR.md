# CLAUDE.md - Option B: "The Consulting Operator"
# Operational excellence for a consulting firm powered by TAC methodology

## Project: GBAutomation Consulting Co

AI-native consulting operations. Every workflow is an agentic primitive.
Every deliverable is generated, validated, and shipped by agents.

---

## Ground Rules

1. **You don't write code. You orchestrate agents that write code.** (TAC #1)
2. **Context is king.** Before acting, gather what your agent needs to succeed. (TAC #2)
3. **If you've done it twice, template it.** Problem classes > individual problems. (TAC #3)
4. **Validate everything.** No output ships without a feedback loop. (TAC #5)
5. **One agent, one job.** Don't overload context or conflate responsibilities. (TAC #6)

---

## File Organization

```
consulting-co/
├── CLAUDE.md                    ← You are here (agentic layer config)
├── specs/                       ← Plans, proposals, ADRs
├── proposals/                   ← Client-facing proposals
├── .claude/
│   ├── commands/                ← Reusable prompt templates (TAC #3)
│   │   ├── experts/             ← Self-improving domain experts (ACT-LEARN-REUSE)
│   │   ├── graphiti/            ← Knowledge graph operations
│   │   ├── scoping/             ← Consulting discovery workflows
│   │   ├── ecosystem/           ← Ecosystem management
│   │   ├── bowser/              ← Browser automation
│   │   └── codebase-knowledge-extract/
│   ├── agents/                  ← Specialized agent definitions (TAC #6)
│   ├── skills/                  ← Complex multi-step capabilities
│   ├── adws/                    ← Autonomous development workflows (TAC #4, #7)
│   ├── hooks/                   ← Event-driven automation
│   ├── context/                 ← Generated docs & research
│   │   ├── architecture/        ← Architecture decisions
│   │   ├── implementation/      ← Implementation guides
│   │   ├── research/            ← Research outputs
│   │   ├── planning/            ← Plans and strategies
│   │   └── {group}/             ← Topic-specific context
│   ├── config/                  ← Service configurations
│   └── scripts/                 ← Utility scripts
├── observability/               ← Monitoring & dashboards
├── tac-learning-system/         ← TAC methodology reference
└── tools/                       ← External tool integrations
```

### Rules
- Generated `.md` → `.claude/context/{group}/*.md`
- Obsidian notes → `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation`
- Always use Obsidian templates from `obsidian-docs/Template-Library-Index.md`
- Ports: **3025-3099** (never 3000)

### File Traceability
All generated artifacts are prefixed with a timestamp (`yyyymmdd-hhmmss`) for traceability.
This is non-negotiable — it enables chronological auditing and prevents filename collisions.

| Artifact | Location | Example |
|----------|----------|---------|
| Plans & specs | `specs/` | `20260217-143000-auth-redesign.md` |
| Context docs | `.claude/context/{group}/` | `20260217-143000-api-research.md` |
| ADW outputs | `.claude/adws/` | `20260217-143000-plan-build-result.md` |
| Proposals | `proposals/` | `20260217-143000-acme-sow.md` |
| Expert plans | `.claude/specs/` | `20260217-143000-frontend-darkmode.md` |

---

## Consulting Workflows

### Client Discovery
```
/scoping:consulting-questions     → Master discovery question set
/scoping:analyze-transcripts      → Generate architecture questions from call notes
/scoping:generate-adr             → ADR from meeting notes
/consulting:quick-proposal        → Professional proposal with SOW & timeline
```

### Project Execution
```
/experts:tac:plan "task"          → TAC-informed implementation plan
/plan-build-review                → Three-phase autonomous workflow
/adw "task"                       → Background autonomous execution
/validate                         → Comprehensive validation suite
```

### Knowledge Management
```
/search-knowledge "query"         → Unified search across all knowledge bases
/graphiti:search "concept"        → Knowledge graph entity search
/graphiti:daily                   → Generate daily Obsidian summary
/graphiti:weekly                  → Weekly rollup report
/note-create                      → Create new knowledge note
```

---

## Expert System (ACT-LEARN-REUSE)

Experts are self-improving agents. They accumulate domain knowledge in `expertise.yaml`
files and get smarter with every execution. Never update expertise files manually -
let the self-improve prompt handle it.

| Expert | When to Use | Key Commands |
|--------|-------------|--------------|
| **TAC** | Methodology, planning, ADW design | `/experts:tac:question`, `/experts:tac:plan` |
| **Supabase** | Vault secrets, migrations, queries | `/experts:supabase:question`, `/experts:supabase:plan` |
| **AWS Org** | Sub-accounts, IAM, Lightsail | `/experts:aws-org:question`, `/experts:aws-org:create-account` |
| **OpenClaw** | Agent platform, skill deployment | `/experts:openclaw:status`, `/experts:openclaw:deploy-skill` |

### Expert Lifecycle
```
/experts:{domain}:question   → Query accumulated expertise (REUSE)
/experts:{domain}:plan       → Domain-aware planning (REUSE)
/experts:{domain}:self-improve → Validate & update expertise (LEARN)
/experts:{domain}:plan_build_improve → Full cycle (ACT → LEARN → REUSE)
```

---

## Agent Fleet

### Core Agents (`.claude/agents/`)

| Agent | Responsibility | Data Store |
|-------|---------------|------------|
| **Observability** | Real-time event streaming | SQLite |
| **Langfuse** | Trace logging & cost tracking | Langfuse Cloud |
| **Graphiti** | Knowledge graph (entities, relationships) | Neo4j |
| **Obsidian** | Auto-generated documentation | Markdown vault |
| **Orchestrator** | Multi-agent coordination | N/A |

### Media Agents
| Agent | Purpose |
|-------|---------|
| Video Director | End-to-end video production |
| Cinematographer | Visual composition |
| Nano Prompt Engineer | Optimized prompt generation |
| Video QA Analyst | Quality validation |

### Browser Agents
| Agent | Purpose |
|-------|---------|
| Bowser | Chrome DevTools browser automation |
| Playwright Bowser | Headless parallel browser sessions |
| Bowser QA | UI validation & acceptance testing |

---

## Autonomy Levels (PITER Framework)

| Level | Touchpoints | Example Workflow |
|-------|-------------|------------------|
| **In-Loop** | Many | `/experts:tac:question` (conversational) |
| **Out-Loop** | 2 (prompt + review) | `/plan-build-review` (plan → build → review) |
| **Zero-Touch** | 1 (prompt only) | `/adw` (background autonomous) |

### Graduating to Zero-Touch
1. Start In-Loop for new problem classes
2. Template successful patterns into commands (TAC #3)
3. Add feedback loops with automated validation (TAC #5)
4. Promote to Out-Loop ADW when confidence > 80%
5. Graduate to Zero-Touch when confidence > 90% (TAC #7)

---

## Context Engineering (R&D Framework)

### Reduce
- Keep CLAUDE.md **under 200 lines** in production
- No MCP server bloat - audit `.mcp.json` regularly
- Use context priming (`/commands`) over always-on memory files
- One agent, one prompt, one purpose (TAC #6)

### Delegate
- Use `/search-knowledge` for on-demand context retrieval
- Use `/experts:{domain}:question` for domain-specific lookups
- Use Graphiti for persistent knowledge that spans sessions
- Generated context → `.claude/context/` (not inline in CLAUDE.md)

---

## Validation & Feedback Loops (TAC #5)

### Before Shipping Anything
```bash
# Code changes
/validate                          # Full validation suite

# Agent outputs
/experts:tac:plan_build_improve    # Plan → Build → Self-improve

# Consulting deliverables
/scoping:analyze-transcripts       # Validate against client needs
```

### Agentic Health Metrics
| Metric | Target | Measures |
|--------|--------|----------|
| Attempts | ↓ Decreasing | Fewer retries per task |
| Streak | ↑ Increasing | Consecutive one-shot successes |
| Size | ↑ Increasing | Complexity of autonomous tasks |
| Presence | ↓ Decreasing | Human interventions needed |

---

## Linear Integration

- Project: GBAutomation Marketplace Ecosystem
- Agent Harness: `C:\Users\gblac\OneDrive\Desktop\gbautomation-marketplace-linear`
- Issues: AI-5 through AI-120 (META: AI-120)
- **Critical**: Never set `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` in `.env`

---

## Daily Operations Cheat Sheet

```bash
# Morning standup
/graphiti:daily                    # What happened yesterday
/check-subscriptions               # Credit & usage check
/experts:openclaw:status           # Agent platform health

# During work
/experts:tac:plan "task"           # Plan with TAC methodology
/adw "implementation task"         # Kick off autonomous work
/search-knowledge "topic"          # Find relevant context

# End of day
/graphiti:weekly                   # Weekly progress
/sync-claude-ecosystem             # Sync to Obsidian
```
