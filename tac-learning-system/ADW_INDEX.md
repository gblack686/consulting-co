---
title: "TAC ADW Index - AI Developer Workflows"
type: index
---

# ADW Index - AI Developer Workflows

> Complete catalog of AI Developer Workflows and Agentic Primitives across TAC lessons.

## Overview

| Lesson | ADWs | Focus | Key Primitives |
|--------|------|-------|----------------|
| TAC-4 | 1 | Foundation SDLC | adw_plan_build |
| TAC-5 | 6 | Planning & Building | Composable phases |
| TAC-6 | 18 | Complete SDLC Pipeline | 5 phases + triggers |
| TAC-7 | 16 | Isolated SDLC | Worktree isolation |
| TAC-8 | 40+ | Multi-Agent Apps | Task boards, Notion |
| TAC-9 | 0 | Context Engineering | Scripts, TS wrappers |
| TAC-10 | 0 | Prompt Engineering | Meta-prompts, commands |
| TAC-11 | 0 | Custom Agents | 8 agent patterns |
| TAC-12 | 0 | Orchestration | Full orchestrator apps |
| **Total** | **80+** | **Full Agentic Layer** | **Multiple paradigms** |

> **Note:** Lessons 9-12 shift from ADWs to other agentic primitives (agents, orchestrators, prompts)

---

## TAC-4: Foundation SDLC

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\tac-4\adws\`

| File | Description |
|------|-------------|
| `adw_plan_build.py` | Complete Plan & Build workflow - fetches issue, creates branch, plans, builds, creates PR |

---

## TAC-5: Advanced Planning & Building

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\tac-5\adws\`

| File | Description |
|------|-------------|
| `adw_plan.py` | Planning phase - classify issue, create branch, generate plan |
| `adw_build.py` | Building phase - implement solution based on plan |
| `adw_test.py` | Testing phase - run tests, validate implementation |
| `adw_plan_build.py` | Orchestrator - chains plan + build |
| `adw_plan_build_test.py` | Extended - plan + build + test |

---

## TAC-6: Complete SDLC Pipeline

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\tac-6\adws\`

### Core Phases
| File | Description |
|------|-------------|
| `adw_plan.py` | Planning phase |
| `adw_build.py` | Building phase |
| `adw_test.py` | Testing phase (MAX_RETRY: 4) |
| `adw_review.py` | Code review phase |
| `adw_document.py` | Documentation phase |
| `adw_patch.py` | Quick fix workflow |

### Composed Workflows
| File | Phases Included |
|------|-----------------|
| `adw_plan_build.py` | Plan → Build |
| `adw_plan_build_test.py` | Plan → Build → Test |
| `adw_plan_build_review.py` | Plan → Build → Review |
| `adw_plan_build_document.py` | Plan → Build → Document |
| `adw_plan_build_test_review.py` | Plan → Build → Test → Review |
| `adw_plan_build_test_review_document.py` | All 5 phases |
| `adw_sdlc.py` | Full SDLC orchestrator |

### Triggers
| File | Type |
|------|------|
| `adw_triggers/trigger_cron.py` | Scheduled execution |
| `adw_triggers/trigger_webhook.py` | Event-driven execution |

---

## TAC-7: Isolated SDLC (Worktrees)

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\tac-7\adws\`

All workflows have `_iso` suffix for worktree isolation:

| File | Description |
|------|-------------|
| `adw_plan_iso.py` | Isolated planning |
| `adw_build_iso.py` | Isolated building |
| `adw_test_iso.py` | Isolated testing |
| `adw_review_iso.py` | Isolated code review |
| `adw_document_iso.py` | Isolated documentation |
| `adw_patch_iso.py` | Isolated patching |
| `adw_ship_iso.py` | Shipping/deployment |
| `adw_sdlc_iso.py` | Full SDLC with isolation |
| `adw_sdlc_zte_iso.py` | Zero-Touch Engineering |

**Key Feature:** Git worktrees enable concurrent execution with separate branches and ports (3025-3099).

---

## TAC-8: Multi-Agent Applications

### App 1: Agent Layer Primitives
| File | Description |
|------|-------------|
| `adw_prompt.py` | Ad-hoc Claude Code prompt execution |
| `adw_sdk_prompt.py` | SDK-focused prompts |
| `adw_slash_command.py` | Custom slash commands |
| `adw_chore_implement.py` | Chore workflow |

### App 2: Multi-Agent ToDone
| File | Description |
|------|-------------|
| `adw_build_update_task.py` | Build + update task |
| `adw_plan_implement_update_task.py` | Full task workflow |
| `adw_trigger_cron_todone.py` | Task distribution scheduler |

### App 3: Out-Loop Multi-Agent Task Board
Same structure as App 2 with task board integration.

### App 4: Agentic Prototyping
| File | Description |
|------|-------------|
| `adw_build_update_notion_task.py` | Notion API integration |
| `adw_plan_implement_update_notion_task.py` | Full Notion workflow |
| `adw_trigger_cron_notion_tasks.py` | Notion task scheduler |

### App 5: NLQ to SQL AEA
Full ISO SDLC set with AEA (Agent Engineering Architecture) support.

---

## Support Modules (Common)

**Location:** `adws/adw_modules/`

| Module | Purpose |
|--------|---------|
| `workflow_ops.py` | Core operations (classify, plan, implement) |
| `agent.py` | Agent execution and templating |
| `github.py` | GitHub API (issues, PRs, comments) |
| `git_ops.py` | Git operations (branch, commit, push) |
| `state.py` | ADWState for persistence |
| `data_types.py` | Pydantic models |
| `utils.py` | Utilities (logger, ADW IDs) |

---

## Key Patterns

1. **State Persistence** - ADWState tracks workflow execution
2. **Composable Phases** - Mix and match SDLC steps
3. **Isolation Modes** - Regular, Worktree, ZTE
4. **Trigger Systems** - Cron and webhook automation
5. **Multi-Agent** - Coordinate agents on shared tasks

---

## TAC-9: Elite Context Engineering (No ADWs)

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\elite-context-engineering\`

**Focus:** Context window management, not workflow automation.

| Component | Description |
|-----------|-------------|
| `apps/cc_ts_wrapper/` | TypeScript Claude Code wrapper |
| `apps/hello_cc_1.ts` | Hello world CC example |
| `apps/hello_cc_2.ts` | Extended CC example |
| `scripts/` | Context measurement scripts |
| `.claude/commands/` | Context priming commands |

---

## TAC-10: Agentic Prompt Engineering (No ADWs)

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\agentic-prompt-engineering\`

**Focus:** Prompt levels and meta-prompts.

| Component | Description |
|-----------|-------------|
| `apps/prompt_tier_list/` | Prompt tier classification app |
| `.claude/commands/t_metaprompt_workflow.md` | Meta-prompt for creating prompts |

---

## TAC-11: Building Specialized Agents (No ADWs)

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\building-specialized-agents\apps\`

**Focus:** Custom agent patterns using Claude SDK.

| Agent | Description |
|-------|-------------|
| `custom_1_pong_agent/` | Simplest custom agent - system prompt override |
| `custom_2_echo_agent/` | Custom tools with @tool decorator |
| `custom_3_calc_agent/` | Calculator with focused functionality |
| `custom_4_social_hype_agent/` | Social media agent with TTS |
| `custom_5_qa_agent/` | QA testing agent |
| `custom_6_tri_copy_writer/` | Copywriting agent with backend |
| `custom_7_micro_sdlc_agent/` | Micro SDLC orchestrator |
| `custom_8_ultra_stream_agent/` | Streaming agent |

---

## TAC-12: Multi-Agent Orchestration (No ADWs)

**Location:** `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\apps\`

**Focus:** Orchestrator infrastructure (not ADW scripts).

| Component | Description |
|-----------|-------------|
| `orchestrator_3_stream/` | Full orchestrator with streaming |
| `orchestrator_3_stream/backend/` | FastAPI backend with WebSocket |
| `orchestrator_3_stream/backend/modules/agent_manager.py` | Agent CRUD operations |
| `orchestrator_3_stream/backend/modules/orchestrator_service.py` | Core orchestration logic |
| `orchestrator_db/` | Database models and migrations |

---

## Paradigm Shift: Lessons 9-12

Lessons 9-12 represent a shift from **ADW scripts** to **higher-level primitives**:

```
TAC 4-8: ADW Scripts (adw_*.py)
    ↓
TAC 9: Context Engineering (measurement, priming)
    ↓
TAC 10: Prompt Engineering (7 levels, meta-prompts)
    ↓
TAC 11: Custom Agents (SDK patterns)
    ↓
TAC 12: Orchestration (full infrastructure)
```

---

## Diagram

See [[diagrams/adw-architecture.excalidraw]] for visual architecture.

---

## Related

- [[loot.md]] files for each lesson
- [[quiz.md]] files for testing knowledge
- [[transcript.txt]] files for full video content
