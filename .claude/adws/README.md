# ADWs (Agentic Development Workflows)

Placeholder folder for ADW files discovered in TAC repositories.

## What is an ADW?

An ADW (Agentic Development Workflow) is a Python script that orchestrates Claude Code to execute multi-step development tasks autonomously.

## ADW Sources

See the TAC Learning System for comprehensive ADW indexes:
- [TAC ADW Index](../../tac-learning-system/index/adws/README.md)

## Key TAC ADW Locations

| TAC | Path | Count |
|-----|------|-------|
| tac-5 | `desktop/tac/tac-5/adws/` | 8 |
| tac-6 | `desktop/tac/tac-6/adws/` | 14 |
| tac-7 | `desktop/tac/tac-7/adws/` | 22 |
| tac-8 (app5) | `desktop/tac/tac-8/tac8_app5__nlq_to_sql_aea/adws/` | 26 |
| software-delivery-adw | `desktop/tac/software-delivery-adw/adws/` | 18 |
| adw-designer | `desktop/tac/adw-designer/blueprints/adws/` | Templates |

## ADW Patterns

### Basic
- `adw_build.py` - Execute build step
- `adw_plan.py` - Create implementation plan
- `adw_test.py` - Run test suite

### Composite
- `adw_plan_build.py` - Plan → Build
- `adw_plan_build_test.py` - Plan → Build → Test
- `adw_sdlc.py` - Full software development lifecycle

### Isolated (tac-7+)
- `adw_*_iso.py` - Runs in isolated git worktree

### Triggered
- `adw_trigger_cron_*.py` - Cron-scheduled workflows
