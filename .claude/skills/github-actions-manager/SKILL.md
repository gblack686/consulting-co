---
name: github-actions-manager
description: Manage GitHub Actions workflows, monitor CI/CD pipelines, trigger deployments, and analyze failures. Use when checking build status, deploying, or investigating CI issues.
---

# GitHub Actions Manager

## Overview

Complete GitHub Actions CI/CD management for Claude Code:
- **Workflow Management** - List, trigger, and monitor workflows
- **Run Tracking** - View status, logs, and history
- **Deployment Dashboard** - Track environments at a glance
- **Failure Analysis** - Identify patterns and improve reliability

## When to Use This Skill

Activate this skill when:
- Checking CI/CD build status
- Triggering deployments
- Investigating workflow failures
- Analyzing build reliability trends
- Setting up new CI/CD workflows

## Quick Start

### Check CI Status
```bash
# Recent workflow runs
python .claude/skills/github-actions-manager/scripts/list_runs.py

# Deployment status across environments
python .claude/skills/github-actions-manager/scripts/deployment_status.py
```

### Investigate Failure
```bash
# Find recent failures
python .claude/skills/github-actions-manager/scripts/list_runs.py --failures

# View failure details
python .claude/skills/github-actions-manager/scripts/view_run.py <run_id> --logs-failed
```

### Trigger Deployment
```bash
# List available workflows
python .claude/skills/github-actions-manager/scripts/trigger_workflow.py --list

# Deploy to staging
python .claude/skills/github-actions-manager/scripts/trigger_workflow.py deploy.yml \
  --input environment=staging --input version=v1.2.3
```

### Analyze Reliability
```bash
# Last 30 days of failure analysis
python .claude/skills/github-actions-manager/scripts/analyze_failures.py --days 30
```

## Architecture

```
.claude/skills/github-actions-manager/
├── SKILL.md                    # This file
├── config/
│   └── settings.json           # Configuration
├── scripts/
│   ├── gh_actions_ops.py       # Core operations module
│   ├── list_workflows.py       # List available workflows
│   ├── list_runs.py            # List workflow runs
│   ├── view_run.py             # View run details and logs
│   ├── trigger_workflow.py     # Trigger workflow runs
│   ├── deployment_status.py    # Deployment dashboard
│   └── analyze_failures.py     # Failure analysis
└── templates/
    ├── python-ci.yml           # Python CI template
    ├── node-ci.yml             # Node.js CI template
    └── deploy-to-aws.yml       # AWS deployment template
```

## Scripts Reference

### list_workflows.py

List all workflows in a repository.

```bash
python scripts/list_workflows.py [options]

Options:
  --repo, -r         Repository (owner/repo)
  --with-status, -s  Include latest run status
  --json             Output as JSON
```

### list_runs.py

List workflow run history with filters.

```bash
python scripts/list_runs.py [options]

Options:
  --repo, -r       Repository (owner/repo)
  --workflow, -w   Filter by workflow filename
  --status, -s     Filter: queued, in_progress, completed
  --branch, -b     Filter by branch
  --limit, -n      Max runs (default: 20)
  --failures, -f   Show only failures
  --verbose, -v    Detailed output
  --json           Output as JSON
```

### view_run.py

View details of a specific run.

```bash
python scripts/view_run.py <run_id> [options]

Options:
  --repo, -r        Repository (owner/repo)
  --logs, -l        Show full logs
  --logs-failed, -f Show only failed step logs
  --json            Output as JSON
```

### trigger_workflow.py

Trigger a workflow run.

```bash
python scripts/trigger_workflow.py [workflow] [options]

Options:
  --repo, -r    Repository (owner/repo)
  --ref         Branch/tag to run on (default: main)
  --input, -i   Workflow input (key=value, can repeat)
  --list, -l    List available workflows
  --dry-run     Show without triggering
```

### deployment_status.py

Show deployment status across environments.

```bash
python scripts/deployment_status.py [options]

Options:
  --repo, -r  Repository (owner/repo)
  --json      Output as JSON
```

Output:
```
Environment     Status          Branch          Last Deploy  Run ID
-------------------------------------------------------------------
production      ✅ success      main            2h ago       12345
staging         ✅ success      develop         30m ago      12346
dev             🔄 running      feature/x       in progress  12347
```

### analyze_failures.py

Analyze failure patterns over time.

```bash
python scripts/analyze_failures.py [options]

Options:
  --repo, -r      Repository (owner/repo)
  --days, -d      Days to analyze (default: 30)
  --workflow, -w  Filter by workflow
  --detailed      Fetch logs for error patterns
  --json          Output as JSON
```

Output:
```
============================================================
FAILURE ANALYSIS - Last 30 Days
============================================================

📊 Overview:
   Total Runs:   150
   Successes:    138 ✅
   Failures:     12 ❌
   Success Rate: 92.0%

📋 Failures by Workflow:
   CI: 8 (67%)
   Deploy: 4 (33%)

💡 Recommendations:
   🔧 Focus on 'CI' workflow (8 failures)
```

## Workflow Templates

### Python CI (`templates/python-ci.yml`)

Complete Python CI with:
- Matrix testing (Python 3.11, 3.12)
- Linting with ruff
- Type checking with mypy
- Tests with pytest and coverage
- Codecov integration

### Node.js CI (`templates/node-ci.yml`)

Complete Node.js CI with:
- Matrix testing (Node 18.x, 20.x)
- ESLint integration
- TypeScript type checking
- Jest tests with coverage
- Build artifact upload

### Deploy to AWS (`templates/deploy-to-aws.yml`)

Manual deployment workflow with:
- Environment selection (dev/staging/production)
- Version input
- OIDC authentication (no long-lived secrets)
- Dry run option
- Success/failure notifications

## Configuration

### settings.json

```json
{
  "default_repo": "gblack686/consulting-co",
  "environments": ["production", "staging", "dev"],
  "deploy_workflow_patterns": ["deploy", "release", "publish"],
  "notification_on_failure": true,
  "auto_create_issue_on_failure": false,
  "watched_workflows": [],
  "default_branch": "main"
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `default_repo` | `gblack686/consulting-co` | Default repository |
| `environments` | `[prod, staging, dev]` | Environment names to track |
| `deploy_workflow_patterns` | `[deploy, release]` | Patterns to identify deploy workflows |
| `notification_on_failure` | `true` | Enable failure notifications |
| `auto_create_issue_on_failure` | `false` | Auto-create issues for failures |

## gh CLI Quick Reference

```bash
# Workflows
gh workflow list                      # List workflows
gh workflow run ci.yml                # Trigger workflow
gh workflow run deploy.yml -f env=prod  # Trigger with inputs

# Runs
gh run list                           # Recent runs
gh run list --workflow=ci.yml         # Filter by workflow
gh run view 12345                     # View run
gh run view 12345 --log-failed        # Failed logs only
gh run watch 12345                    # Watch live
gh run cancel 12345                   # Cancel
gh run rerun 12345 --failed           # Rerun failed jobs

# Artifacts
gh run download 12345 -n coverage     # Download artifact
```

## Integration with Issue Manager

Create tracking issues for CI failures:

```bash
# 1. Identify failure
python scripts/list_runs.py --failures --limit 1

# 2. Get details
python scripts/view_run.py 12345 --logs-failed

# 3. Create issue
python .claude/skills/github-issue-manager/scripts/create_issue.py \
  --title "CI Failure: Tests timeout in integration suite" \
  --type bug_fix \
  --labels "ci-failure" "tests"
```

## Dependencies

- Python 3.11+
- `gh` CLI (https://cli.github.com/)
- GitHub repo access

## Version

**Version:** 1.0.0
**Created:** 2026-01-16
