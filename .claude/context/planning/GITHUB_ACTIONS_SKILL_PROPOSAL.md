# GitHub Actions CI/CD Skill Proposal

## Overview

A skill for managing GitHub Actions workflows, monitoring CI/CD pipelines, and deployment testing.

## Components

### 1. Skill: `github-actions-manager`

**Purpose**: Manage workflows, view run status, trigger deployments

**Scripts**:
```
.claude/skills/github-actions-manager/
├── SKILL.md
├── config/
│   └── workflows.json          # Tracked workflows and repos
└── scripts/
    ├── list_workflows.py       # List available workflows
    ├── list_runs.py            # View workflow run history
    ├── trigger_workflow.py     # Manually trigger workflow
    ├── view_run.py             # Get run details and logs
    ├── cancel_run.py           # Cancel in-progress run
    └── workflow_templates/     # Common workflow templates
        ├── python-ci.yml
        ├── node-ci.yml
        └── deploy-to-aws.yml
```

### 2. Agent: `GITHUB_ACTIONS_AGENT.md`

**Capabilities**:
- List and describe available workflows
- Show recent run status (pass/fail/pending)
- Trigger workflow runs with inputs
- View run logs and failure details
- Cancel stuck or unwanted runs
- Create/modify workflow files
- Analyze failure patterns

### 3. Hook (Optional): `deployment_notifier.py`

**Trigger**: After successful deploy workflows
**Purpose**: Notify via TTS or log when deployments complete

---

## Key Commands

### List Workflows
```bash
# Via gh CLI
gh workflow list --repo gblack686/consulting-co

# Via script (with status)
python scripts/list_workflows.py --with-status
```

### View Run History
```bash
# Recent runs for a workflow
gh run list --workflow=ci.yml --limit 10

# Via script with analysis
python scripts/list_runs.py --workflow ci.yml --analyze
```

### Trigger Workflow
```bash
# Trigger with inputs
gh workflow run deploy.yml -f environment=staging -f version=1.2.3

# Via script
python scripts/trigger_workflow.py deploy.yml --env staging --version 1.2.3
```

### View Run Details
```bash
# Get run status and logs
gh run view 12345 --log

# Via script (formatted)
python scripts/view_run.py 12345
```

### Check Deployment Status
```bash
# Current deployment status across environments
python scripts/deployment_status.py

# Output:
# ┌─────────────┬─────────┬──────────────┬─────────────────┐
# │ Environment │ Status  │ Version      │ Last Deploy     │
# ├─────────────┼─────────┼──────────────┼─────────────────┤
# │ production  │ ✅ live │ v1.2.3       │ 2h ago          │
# │ staging     │ ✅ live │ v1.2.4-beta  │ 30m ago         │
# │ dev         │ 🔄 deploying │ v1.2.5  │ in progress     │
# └─────────────┴─────────┴──────────────┴─────────────────┘
```

---

## Workflow Templates

### Python CI (`python-ci.yml`)
```yaml
name: Python CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src tests/
      - run: ruff check src/
```

### Deploy to AWS (`deploy-to-aws.yml`)
```yaml
name: Deploy to AWS

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, staging, production]
      version:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1
      - run: ./scripts/deploy.sh ${{ inputs.environment }} ${{ inputs.version }}
```

---

## Integration with Issue Manager

When a workflow fails, the agent can:
1. Analyze the failure logs
2. Create a GitHub issue with the error details
3. Suggest fixes based on the error pattern

```bash
# Example: Auto-create issue for CI failure
python scripts/view_run.py 12345 --on-failure create-issue
```

---

## Analytics Features

### Failure Analysis
```bash
python scripts/analyze_failures.py --days 30

# Output:
# Top Failure Reasons (Last 30 Days):
# 1. Test timeout (12 occurrences) - tests/integration/test_api.py
# 2. Linting errors (8 occurrences) - src/utils/
# 3. Dependency conflict (3 occurrences) - requirements.txt
```

### Build Performance
```bash
python scripts/build_metrics.py

# Output:
# Average Build Time: 4m 32s
# Success Rate: 94%
# Slowest Step: pytest (2m 15s)
# Recommendation: Consider parallel test execution
```

---

## Implementation Order

### Phase 1: Core Scripts
1. `list_workflows.py` - List available workflows
2. `list_runs.py` - View run history
3. `view_run.py` - Get run details and logs
4. `trigger_workflow.py` - Trigger workflows

### Phase 2: Agent
5. Create `GITHUB_ACTIONS_AGENT.md`
6. Document common commands and use cases

### Phase 3: Templates & Analytics
7. Add workflow templates
8. Add `analyze_failures.py`
9. Add `deployment_status.py`

### Phase 4: Integration
10. Hook for deployment notifications
11. Integration with Issue Manager for failures

---

## gh CLI Commands Reference

```bash
# Workflows
gh workflow list                    # List all workflows
gh workflow view ci.yml             # View workflow details
gh workflow run ci.yml              # Trigger workflow
gh workflow disable ci.yml          # Disable workflow

# Runs
gh run list                         # List recent runs
gh run list --workflow=ci.yml       # Filter by workflow
gh run view 12345                   # View run details
gh run view 12345 --log             # View with logs
gh run view 12345 --log-failed      # Only failed step logs
gh run watch 12345                  # Watch run in progress
gh run cancel 12345                 # Cancel run
gh run rerun 12345                  # Rerun failed run
gh run rerun 12345 --failed         # Rerun only failed jobs

# Artifacts
gh run download 12345               # Download artifacts
gh run download 12345 -n coverage   # Download specific artifact
```

---

## Questions for Implementation

1. Which repos should be tracked by default?
2. Should failures auto-create issues?
3. Notification preferences (TTS, desktop, email)?
4. Should we include deployment approval workflows?

---

**Created**: 2026-01-16
