# TAC ADW Index

130+ Agentic Development Workflows (ADWs) across TAC repositories.

## What is an ADW?

An ADW (Agentic Development Workflow) is a Python script that orchestrates Claude Code to execute multi-step development tasks. ADWs live in `adws/` folders.

## ADW Evolution Across TAC

| TAC | ADW Count | Key Patterns |
|-----|-----------|--------------|
| tac-2, 3, 4 | Minimal | Basic structure |
| tac-5 | 8 | Plan → Build → Test |
| tac-6 | 14 | + Document, Review |
| tac-7 | 22 | + Isolated worktrees |
| tac-8 | 26+ per app | + Notion, Triggers |
| software-delivery-adw | 18 | Enterprise patterns |
| adw-designer | Templates | Blueprint system |

## ADW Categories

### Basic Workflows
| ADW | Purpose |
|-----|---------|
| `adw_build.py` | Execute build step |
| `adw_plan.py` | Create implementation plan |
| `adw_test.py` | Run test suite |

### Composite Workflows
| ADW | Steps |
|-----|-------|
| `adw_plan_build.py` | Plan → Build |
| `adw_plan_build_test.py` | Plan → Build → Test |
| `adw_plan_build_review.py` | Plan → Build → Review |
| `adw_plan_build_test_review.py` | Full SDLC |

### Advanced Workflows (tac-7+)
| ADW | Purpose |
|-----|---------|
| `adw_*_iso.py` | Isolated worktree execution |
| `adw_sdlc_iso.py` | Full SDLC in isolation |
| `adw_sdlc_zte_iso.py` | Zero-to-end delivery |
| `adw_ship_iso.py` | Ship to production |

### Integration Workflows (tac-8)
| ADW | Integration |
|-----|-------------|
| `adw_build_update_task.py` | Update task tracker |
| `adw_plan_implement_update_task.py` | Full task lifecycle |
| `adw_build_update_notion_task.py` | Notion integration |
| `adw_trigger_cron_todone.py` | Cron-triggered |
| `adw_trigger_cron_notion_tasks.py` | Notion polling |

## By Repository

### tac-5/adws (8 workflows)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-5\adws\`

```
adws/
├── adw_build.py
├── adw_plan.py
├── adw_plan_build.py
├── adw_plan_build_test.py
├── adw_test.py
├── adw_modules/        # 9 helper modules
├── adw_tests/          # Test suite
└── adw_triggers/       # Trigger implementations
```

### tac-6/adws (14 workflows)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-6\adws\`

New in tac-6:
- adw_document.py
- adw_patch.py
- adw_plan_build_document.py
- adw_plan_build_review.py
- adw_plan_build_test_review.py
- adw_review.py
- adw_sdlc.py

### tac-7/adws (22 workflows)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-7\adws\`

All tac-6 workflows plus `_iso` variants for worktree isolation:
- adw_build_iso.py
- adw_document_iso.py
- adw_patch_iso.py
- adw_plan_build_document_iso.py
- adw_plan_build_iso.py
- adw_plan_build_review_iso.py
- adw_plan_build_test_iso.py
- adw_plan_build_test_review_iso.py
- adw_plan_iso.py
- adw_review_iso.py
- adw_sdlc_iso.py
- adw_sdlc_zte_iso.py
- adw_ship_iso.py
- adw_test_iso.py

### tac-8/tac8_app5__nlq_to_sql_aea/adws (26 workflows)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-8\tac8_app5__nlq_to_sql_aea\adws\`

Most comprehensive - includes AEA (Agentic Engineering Architecture) patterns:
- All tac-7 iso workflows
- adw_aea_patch.py (AEA-specific)
- Enhanced data types in adw_modules/

### software-delivery-adw/adws (18 workflows)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\software-delivery-adw\adws\`

Enterprise-focused:
- adw_config.py
- adw_deploy.py
- adw_develop.py
- adw_discovery.py
- adw_planning.py
- adw_review.py
- adw_scoping.py
- adw_scoping_modular.py
- adw_scoping_templates.py
- adw_test.py
- adw_test_infra.py
- adw_ui_review.py
- scoping_instructions.yaml

### adw-designer/blueprints/adws (Templates)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\adw-designer\blueprints\adws\`

Blueprint templates for creating new ADWs:
- adw_build_update_task.py
- adw_chore_implement.py
- adw_plan_implement_update_task.py
- adw_prompt.py
- adw_slash_command.py
- adw_modules/ (agent.py, data_models.py, utils.py)
- adw_triggers/adw_trigger_cron_todone.py

## ADW Module System

All ADWs share common modules in `adw_modules/`:

| Module | Purpose |
|--------|---------|
| `agent.py` | Claude Code agent wrapper |
| `agent_sdk.py` | Agent SDK integration |
| `data_models.py` | Shared data types |
| `data_types.py` | Type definitions |
| `git_ops.py` | Git operations |
| `utils.py` | Utility functions |
| `workflow_ops.py` | Workflow operations |
| `worktree_ops.py` | Worktree management |

## ADW Trigger System

Triggers in `adw_triggers/` enable automated workflow execution:

| Trigger | Purpose |
|---------|---------|
| `adw_trigger_cron_todone.py` | Poll task boards |
| `adw_trigger_cron_notion_tasks.py` | Poll Notion |
| Webhook triggers | Respond to events |

## Creating New ADWs

See: [ADW Designer Skill](file:///C:/Users/gblac/OneDrive/Desktop/tac/adw-designer/SKILL.md)
