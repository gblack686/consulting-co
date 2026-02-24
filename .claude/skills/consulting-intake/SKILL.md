---
name: consulting-intake
description: "OpenClaw installation consulting pipeline. Processes a 90-minute consulting session transcript into a complete OpenClaw workspace with per-domain expert systems. Parses client goals, domains, workflows, and preferences into SOUL.md, USER.md, IDENTITY.md, MEMORY.md, AGENTS.md, TOOLS.md, HEARTBEAT.md, OpenClaw SKILL.md files, cron jobs, and full Claude Code expert directories (8+ files each) using TAC plan-build-improve-validate cycles. Use when processing a consulting transcript, building domain experts, or assembling a client workspace package."
---

# OpenClaw Consulting Intake Pipeline

## Overview

Transform a 90-minute consulting session transcript into a fully configured OpenClaw workspace with self-improving domain expert systems. This skill is the TAC Coding Expert — the meta-brain that knows how to build other experts.

## When to Use This Skill

- Processing a consulting session transcript into deliverables
- Building a domain expert system from a client spec
- Assembling OpenClaw workspace files from session data
- Validating a client workspace package before deployment
- User mentions "consulting intake", "process transcript", "build domain expert"

## Session Naming Convention

Every client session lives in a `YYYYMMDD-{project}/` directory under `client-sessions/`:

```
client-sessions/
├── 20260221-greg-trading/
├── 20260301-jane-content/
└── 20260315-acme-support/
```

**Format**: `YYYYMMDD` (intake date) + `-` + `{client-project}` (kebab-case, descriptive).

This feeds directly into the GitHub branch name: `client/YYYYMMDD-{project}`.

## Pipeline Commands

### `/consulting-intake parse-transcript <path>`
Parse a consulting transcript into structured session output.
Output dir: `client-sessions/YYYYMMDD-{project}/`

### `/consulting-intake build-workspace <session_output_dir>`
Generate OpenClaw workspace files (SOUL, USER, IDENTITY, etc.) from parsed session data.

### `/consulting-intake build-domain <domain_spec.json>`
Build a complete expert system for one domain using plan-build-improve-validate.

### `/consulting-intake validate <package_dir>`
Quality-check the complete client package (experts + workspace + config).

### `/consulting-intake repo-setup <session_dir>`
Initialize or update the OpenClaw clients GitHub repo and create a client branch.

### `/consulting-intake deploy <package_dir> --host <ip> --key <path>`
Deploy the assembled package to a client's OpenClaw instance via SSH (or local copy for Windows).

## Architecture

```
Transcript → Parse → Build Workspace → Build Domain Experts → Validate → Repo Setup → Deploy
                          │                    │                              │
                   YYYYMMDD-{project}/  ┌──────┼──────┐              branch: client/
                   session_output/      ▼      ▼      ▼              YYYYMMDD-{project}
                   workspace/         PLAN  BUILD  IMPROVE
                   experts/         (research)(write)(validate)
                                       │      │      │
                              Browser ─┘  Templates  Loop if <80%
                              YouTube
```

## Core Knowledge

This skill's intelligence comes from these reference files:

| Reference | Purpose |
|-----------|---------|
| `references/session-framework.md` | 30 discovery questions mapped to OpenClaw files |
| `references/openclaw-workspace-spec.md` | Format spec for all 7 workspace files |
| `references/skill-format-spec.md` | OpenClaw SKILL.md format with frontmatter rules |
| `references/expert-system-pattern.md` | The 8-file expert pattern (from eval expert) |
| `references/agent-architecture.md` | Full pipeline architecture with flow diagrams |
| `references/multi-agent-patterns.md` | 5 deployment patterns: single, domain, context, orchestrator, peer |
| `references/model-tiers.md` | 3 cost tiers (cheap/mid/pro) with OpenRouter model IDs and intelligent routing patterns |
| `references/tac-pattern-library.md` | Which TAC pattern applies to which workflow type |
| `references/quality-rubric.md` | Scoring criteria for validation (>= 80% to ship) |
| `references/github-repo-strategy.md` | Branch model, repo init, `.gitignore`, PR workflow |
| `client-facing/` | Welcome email, prep guide, agenda, glossary, service agreement |
| `templates/` | Shared workspace templates (SOUL, USER, IDENTITY, etc.) |
| `templates/agent-workspace/` | Per-domain agent workspace templates (Pattern B) |
| `templates/expert/` | Claude Code expert system templates (8-file pattern) |

### External Reference
| Document | Location |
|----------|----------|
| OpenClaw Multi-Agent Architecture | `.claude/context/architecture/OPENCLAW_MULTI_AGENT_ARCHITECTURE.md` |

## Pipeline Detail

### Step 1: Parse Transcript

Read `references/session-framework.md` for the question-to-file mapping. Extract:

1. **Client Profile** → `session_output/client_profile.json`
   - Name, timezone, pronouns, working hours
   - Current projects, interests
   - Communication preferences

2. **Soul & Vibe** → `session_output/soul_draft.md`
   - Core truths (quality bar, AI experience)
   - Boundaries (what agent must never do without asking)
   - Vibe (communication style, emoji usage, tone)

3. **Identity** → `session_output/identity.json`
   - Agent name, creature type, vibe, emoji

4. **Mission** → `session_output/mission_statement.md`
   - Mission statement
   - 90-day goals
   - Top autonomous task candidate

5. **Tool Inventory** → `session_output/tool_inventory.json`
   - Hardware (device type, specs)
   - Apps & tools (with API status)
   - API keys & subscriptions — always capture `openrouter_api_key` (recommended default LLM provider)
   - Channel preference (Telegram/Discord/WhatsApp)
   - Budget for AI costs
   - Models: capture `brain_model` and `muscle_model` in OpenRouter format (e.g. `openrouter/anthropic/claude-sonnet-4-5`)

6. **Domains** → `session_output/domains/{name}.json` (one per domain)
   - Domain name and description
   - Tools used in this domain
   - Frequency (daily/weekly/ad-hoc)

7. **Workflows** → `session_output/domains/{domain}/workflows/{name}.json`
   - Step-by-step procedure (from "train a new hire" question)
   - Trigger type (cron/webhook/heartbeat/on-demand)
   - Output format and delivery channel
   - Decision points (human approval gates)
   - Blast radius (what happens if it goes wrong)

8. **Autonomy Config** → `session_output/autonomy.json`
   - Autonomy level (ask-everything to just-get-it-done)
   - External communication permissions
   - Allowlist (who can talk to agent)
   - Session reset preferences

### Step 2: Build Workspace

Transform session_output into OpenClaw workspace files using templates in `templates/`.

Read `references/openclaw-workspace-spec.md` for exact format requirements.

| Session Data | OpenClaw File | Template |
|---|---|---|
| client_profile + identity | USER.md, IDENTITY.md | `templates/USER.md.tmpl`, `templates/IDENTITY.md.tmpl` |
| soul_draft | SOUL.md | `templates/SOUL.md.tmpl` |
| mission_statement | MEMORY.md | `templates/MEMORY.md.tmpl` |
| autonomy + session prefs | AGENTS.md | `templates/AGENTS.md.tmpl` |
| tool_inventory | TOOLS.md | `templates/TOOLS.md.tmpl` |
| periodic workflows | HEARTBEAT.md | `templates/HEARTBEAT.md.tmpl` |
| model + channels + session | openclaw.json | `templates/openclaw.json.tmpl` |
| all of the above | justfile | `templates/justfile.tmpl` |

Fill `{CLIENT_NAME}`, `{AGENT_NAME}`, `{INTAKE_DATE}`, `{DOMAIN_LIST}` in the justfile template.
The justfile lives at the **repo root** (not inside `workspace/`) so clients can run `just setup` immediately after cloning.

### Step 3: Build Domain Experts

For EACH domain in `session_output/domains/`, run the plan-build-improve-validate cycle.

Read `references/expert-system-pattern.md` for the 8-file structure.
Read `references/tac-pattern-library.md` for TAC pattern selection.

#### PLAN Phase
1. Load domain spec (name, tools, workflows)
2. Classify each workflow by TAC pattern:
   - Scheduled output → TAC-3 (Template Engineering)
   - Research/discovery → TAC-6 (One Agent One Purpose)
   - Sync/integration → TAC-5 (Feedback Loops)
   - Content production → TAC-3 + TAC-9 (Context Engineering)
3. Identify API research needs → dispatch browser agent:
   ```
   Task(subagent_type: "playwright-bowser-agent", prompt: "Research {tool} API...")
   ```
4. Identify tutorial research needs → dispatch youtube agent:
   ```
   Task(subagent_type: "youtube-transcript-agent", prompt: "Search OpenClaw {tool}...")
   ```
5. Determine domain-specific commands needed (see Command Selection Logic below)
6. Output: `specs/{domain}-plan.md`

#### BUILD Phase
Generate all files using templates in `templates/expert/`:

1. `_index.md` — from `templates/expert/_index.md.tmpl`
2. `expertise.md` — from `templates/expert/expertise.md.tmpl` (7 parts)
3. `question.md` — from `templates/expert/question.md.tmpl` (6 categories)
4. `plan.md` — from `templates/expert/plan.md.tmpl`
5. `plan_build_improve.md` — from `templates/expert/plan_build_improve.md.tmpl`
6. `self-improve.md` — from `templates/expert/self-improve.md.tmpl`
7. Domain-specific commands — generated based on workflow types
8. OpenClaw SKILL.md files — from `templates/skill.md.tmpl` per workflow
9. Cron job definitions — CLI commands for `openclaw cron add`

#### IMPROVE Phase
1. Review built files against plan
2. Incorporate API research findings into expertise.md Part 6
3. Incorporate YouTube tutorial patterns into expertise.md Part 7
4. Update Part 7 (Patterns & Learnings) with build experience

#### VALIDATE Phase
Read `references/quality-rubric.md` for full scoring criteria.

Score each domain expert. If < 80%, loop back to BUILD with specific fixes.

### Step 4: Validate Package

Run `references/quality-rubric.md` against the complete assembled package.

### Step 5a: GitHub Repo Setup

Read `references/github-repo-strategy.md` for the full strategy.

**Each client gets their own private repo**:
```
github.com/gblack686/openclaw-{client-project}
  main              ← delivered workspace (the client's files)
  update/YYYYMMDD   ← future iterations
```

**Procedure**:
1. Create private repo `gblack686/openclaw-{client-project}`
   - Example: `gblack686/openclaw-greg-trading`
2. Clone it locally to `~/openclaw-{client-project}`
3. Copy deliverables to the clone:
   - `workspace/` — all OpenClaw config files
   - `experts/` — domain expert systems
   - `PACKAGE_SUMMARY.md`, `VALIDATION_REPORT.md`
   - **Exclude**: `session_output/` (contains raw transcript data — internal only)
4. Commit: `"intake: {YYYYMMDD} {client} — {N} domains, score {score}/100"`
5. Push `main` to GitHub
6. Optionally invite client as read-only collaborator:
   ```bash
   gh api repos/gblack686/openclaw-{client-project}/collaborators/{github-user} \
     --method PUT --field permission=pull
   ```

**For future iterations** (new features, updates):
```bash
git checkout -b "update/YYYYMMDD"
# make changes
git push -u origin "update/YYYYMMDD"
gh pr create --base main --head "update/YYYYMMDD" --title "[{client}] Update"
```

### Step 5b: Deploy

For **local Windows** (Greg's setup):
```bash
# Copy workspace files to OpenClaw directory
cp -r workspace/* ~/.openclaw/workspace/
cp -r workspace/skills/* ~/.openclaw/workspace/skills/

# Restart gateway
openclaw restart

# Install cron jobs
bash workspace/cron-setup.sh

# Verify
openclaw doctor
```

For **remote server** (SSH deploy):
```bash
tar -czf client-workspace.tar.gz workspace/ experts/
scp -i {key} workspace/* ubuntu@{host}:~/.openclaw/workspace/
scp -r -i {key} workspace/skills/* ubuntu@{host}:~/.openclaw/workspace/skills/
ssh -i {key} ubuntu@{host} "systemctl --user restart openclaw-gateway"
ssh -i {key} ubuntu@{host} "bash ~/cron-setup.sh"
ssh -i {key} ubuntu@{host} "openclaw doctor --non-interactive"
```

## Command Selection Logic

For each domain, analyze workflows and generate domain-specific commands:

| Workflow Type | Generated Command | Example |
|---|---|---|
| Scheduled outputs | `schedule-{type}.md` | schedule-newsletter, schedule-report |
| Research/discovery | `research-{topic}.md` | research-trends, research-competitors |
| Sync/integration | `sync-{tool}.md` | sync-pipeline, sync-analytics |
| Content production | `draft-{type}.md` | draft-script, draft-post |
| Analytics/reporting | `report-{metric}.md` | report-kpis, report-engagement |
| Maintenance/cleanup | `maintenance.md` | maintenance (standard) |

Every domain always gets the standard 6: `_index, expertise, question, plan, plan_build_improve, self-improve`.

## Research Agent Configs

### Browser Research (dispatched during PLAN)
```
Task(subagent_type: "playwright-bowser-agent")

Prompt: Research the {tool_name} API for OpenClaw integration.
Find: API docs URL, auth method, base URL, key endpoints,
      MCP server availability, ClawHub plugin availability.
Return: Structured JSON.
```

### YouTube Research (dispatched during PLAN)
```
Task(subagent_type: "youtube-transcript-agent")

Prompt: Search for "OpenClaw {tool_name} integration" tutorials.
Extract: Config steps, credentials needed, working prompts,
         skill examples, common pitfalls.
Save to: .claude/context/tac-scan/
```
