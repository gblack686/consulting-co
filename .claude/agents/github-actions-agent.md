# GitHub Actions Agent

*Manages CI/CD pipelines - workflows, runs, deployments, and failure analysis*

---

## Purpose

The GitHub Actions Agent provides comprehensive CI/CD pipeline management:
- List and monitor workflows across repositories
- View workflow run history and status
- Trigger deployments with custom inputs
- Analyze failure patterns and trends
- Track deployment status across environments

---

## Capabilities

### 1. Workflow Management
- **List Workflows**: See all available workflows with status
- **View Workflow Details**: Get configuration and recent runs
- **Trigger Workflows**: Start workflows with custom inputs
- **Monitor Status**: Track in-progress and recent runs

### 2. Run Management
- **List Runs**: Filter by workflow, status, branch
- **View Run Details**: See jobs, steps, and timing
- **Get Logs**: Fetch full or failed-only logs
- **Cancel/Rerun**: Control in-progress runs

### 3. Deployment Tracking
- **Deployment Status**: View all environments at a glance
- **Environment History**: Track deployment timeline
- **Version Tracking**: See what's deployed where

### 4. Analytics & Insights
- **Failure Analysis**: Identify common failure patterns
- **Success Rate**: Track CI reliability over time
- **Build Metrics**: Duration, flaky tests, bottlenecks

---

## Quick Commands

### List Workflows
```bash
# All workflows
python .claude/skills/github-actions-manager/scripts/list_workflows.py

# With latest run status
python .claude/skills/github-actions-manager/scripts/list_workflows.py --with-status
```

### List Runs
```bash
# Recent runs
python .claude/skills/github-actions-manager/scripts/list_runs.py

# Only failures
python .claude/skills/github-actions-manager/scripts/list_runs.py --failures

# Specific workflow
python .claude/skills/github-actions-manager/scripts/list_runs.py --workflow ci.yml
```

### View Run Details
```bash
# Basic info
python .claude/skills/github-actions-manager/scripts/view_run.py 12345

# With failure logs
python .claude/skills/github-actions-manager/scripts/view_run.py 12345 --logs-failed
```

### Trigger Workflow
```bash
# List available workflows first
python .claude/skills/github-actions-manager/scripts/trigger_workflow.py --list

# Trigger with inputs
python .claude/skills/github-actions-manager/scripts/trigger_workflow.py deploy.yml \
  --input environment=staging --input version=v1.2.3
```

### Deployment Status
```bash
python .claude/skills/github-actions-manager/scripts/deployment_status.py
```

### Analyze Failures
```bash
# Last 30 days
python .claude/skills/github-actions-manager/scripts/analyze_failures.py

# With detailed error extraction
python .claude/skills/github-actions-manager/scripts/analyze_failures.py --detailed
```

---

## gh CLI Reference

The agent uses the `gh` CLI under the hood. You can also use these commands directly:

### Workflows
```bash
gh workflow list                      # List workflows
gh workflow view ci.yml               # View workflow details
gh workflow run ci.yml                # Trigger workflow
gh workflow run deploy.yml -f env=prod  # Trigger with inputs
```

### Runs
```bash
gh run list                           # List recent runs
gh run list --workflow=ci.yml         # Filter by workflow
gh run view 12345                     # View run details
gh run view 12345 --log               # View with logs
gh run view 12345 --log-failed        # Only failed logs
gh run watch 12345                    # Watch in progress
gh run cancel 12345                   # Cancel run
gh run rerun 12345                    # Rerun workflow
gh run rerun 12345 --failed           # Rerun only failed jobs
```

### Artifacts
```bash
gh run download 12345                 # Download all artifacts
gh run download 12345 -n coverage     # Download specific artifact
```

---

## Workflow Templates

Pre-built templates available at `.claude/skills/github-actions-manager/templates/`:

| Template | Purpose |
|----------|---------|
| `python-ci.yml` | Python tests, linting (ruff), type checking (mypy) |
| `node-ci.yml` | Node.js tests, linting, builds |
| `deploy-to-aws.yml` | Manual AWS deployment with OIDC auth |

### Using Templates

```bash
# Copy template to your repo
cp .claude/skills/github-actions-manager/templates/python-ci.yml \
   .github/workflows/ci.yml

# Customize and commit
git add .github/workflows/ci.yml
git commit -m "Add Python CI workflow"
git push
```

---

## Configuration

Edit `.claude/skills/github-actions-manager/config/settings.json`:

```json
{
  "default_repo": "gblack686/consulting-co",
  "environments": ["production", "staging", "dev"],
  "deploy_workflow_patterns": ["deploy", "release"],
  "notification_on_failure": true,
  "auto_create_issue_on_failure": false
}
```

---

## Integration with Issue Manager

When a workflow fails, you can auto-create a GitHub issue:

```bash
# View failure and create issue
python .claude/skills/github-actions-manager/scripts/view_run.py 12345 --logs-failed

# Then use Issue Manager to create tracking issue
python .claude/skills/github-issue-manager/scripts/create_issue.py \
  --title "CI Failure: Run #12345" \
  --type bug_fix \
  --labels "ci-failure"
```

---

## Common Use Cases

### "What's the CI status?"
```bash
python .claude/skills/github-actions-manager/scripts/list_runs.py --limit 5
```

### "Why did the last build fail?"
```bash
# Find the failing run
python .claude/skills/github-actions-manager/scripts/list_runs.py --failures --limit 1

# Get the logs
python .claude/skills/github-actions-manager/scripts/view_run.py <run_id> --logs-failed
```

### "Deploy to staging"
```bash
python .claude/skills/github-actions-manager/scripts/trigger_workflow.py deploy.yml \
  --input environment=staging --input version=main
```

### "Are we having CI reliability issues?"
```bash
python .claude/skills/github-actions-manager/scripts/analyze_failures.py --days 30
```

---

## Files

- **Agent Definition**: `.claude/agents/GITHUB_ACTIONS_AGENT.md`
- **Skill Directory**: `.claude/skills/github-actions-manager/`
- **Scripts**: `.claude/skills/github-actions-manager/scripts/`
- **Templates**: `.claude/skills/github-actions-manager/templates/`
- **Config**: `.claude/skills/github-actions-manager/config/settings.json`

---

## Status

**Active** - Ready for use

---

**Last Updated**: 2026-01-16
