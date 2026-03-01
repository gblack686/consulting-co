# GitHub Issue Agent

*Manages GitHub issues - create, monitor, analyze, and track Claude Code fixes*

---

## Purpose

The GitHub Issue Agent provides comprehensive GitHub issue management capabilities:
- Create, update, and close GitHub issues
- Monitor ADW workflow statuses via issue labels/comments
- Search for duplicate/related issues
- Generate issue analytics (open/closed trends, response times)
- Track fixes automatically created by the GitHub Issue Hook

---

## Capabilities

### 1. Issue Management
- **Create Issues**: Create new issues with title, body, labels, and assignees
- **Update Issues**: Modify title, body, state, labels, or assignees
- **Close Issues**: Close with optional comment and reason
- **Add Comments**: Post comments with bot identifier

### 2. Issue Discovery
- **List Issues**: Filter by state, labels, date range
- **Search Issues**: Full-text search across issues
- **Find Duplicates**: Detect similar issues before creating new ones
- **Get Issue Details**: Retrieve full issue information

### 3. Analytics
- **Open/Closed Trends**: Track issue velocity over time
- **Label Distribution**: Analyze issue categorization
- **Response Times**: Measure time to first response/resolution
- **Fix Tracking**: Monitor Claude Code auto-generated issues

---

## Commands

### List Issues
```bash
# List open issues
gh issue list --repo gblack686/consulting-co --state open

# List Claude Code fix issues
gh issue list --repo gblack686/consulting-co --label claude-code-fix

# List with details
python .claude/skills/github-issue-manager/scripts/list_issues.py --verbose
```

### Create Issue
```bash
# Create via script
python .claude/skills/github-issue-manager/scripts/create_issue.py \
  --title "Fix authentication timeout" \
  --type bug_fix \
  --labels "bug" "high-priority"

# Create via gh CLI
gh issue create --repo gblack686/consulting-co \
  --title "Fix: Database connection pooling" \
  --body "Description here" \
  --label bug
```

### Search Issues
```bash
# Search for related issues
gh search issues "authentication" --repo gblack686/consulting-co

# Search via script
python .claude/skills/github-issue-manager/scripts/list_issues.py --search "timeout"
```

### Close Issue
```bash
# Close with comment
gh issue close 123 --repo gblack686/consulting-co --comment "Fixed in commit abc123"
```

---

## Integration with GitHub Issue Hook

The hook (`github_issue_creator.py`) automatically:
1. Triggers on Stop events
2. Scans conversation for fix indicators
3. Uses Claude Haiku for analysis
4. Creates issues when confidence > threshold

### Hook Configuration

Located at `.claude/skills/github-issue-manager/config/settings.json`:

```json
{
  "enabled": true,
  "default_repo": "gblack686/consulting-co",
  "default_labels": ["claude-code-fix"],
  "min_confidence": 0.7,
  "fix_types_to_track": ["bug_fix", "security_fix"],
  "dry_run": false
}
```

### Hook Logs

Debug logs are written to: `~/.claude/logs/github_issue_debug.log`

---

## ADW Workflow Monitoring

Track ADW (Agentic Development Workflow) status via issues:

### Label Convention
- `adw-active`: ADW currently running
- `adw-complete`: ADW finished successfully
- `adw-blocked`: ADW encountered blocker
- `adw-review`: ADW needs human review

### Example Workflow
```bash
# Create ADW tracking issue
gh issue create --repo gblack686/consulting-co \
  --title "ADW: Implement user authentication" \
  --body "Tracking issue for ADW implementation" \
  --label adw-active

# Update status
gh issue edit 123 --remove-label adw-active --add-label adw-complete

# Add progress comment
gh issue comment 123 --body "[CLAUDE-CODE-FIX] Completed step 3/5"
```

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `github_ops.py` | Core GitHub operations module |
| `test_auth.py` | Verify gh CLI authentication |
| `create_issue.py` | Manual issue creation |
| `list_issues.py` | List/filter/search issues |

---

## Environment

### Required
- `gh` CLI installed and authenticated
- Repository access (read/write)

### Optional
- `ANTHROPIC_API_KEY`: For Haiku analysis in hook

---

## Bot Identifier

All automated comments include the identifier:
```
[CLAUDE-CODE-FIX]
```

This prevents infinite loops and makes automated actions identifiable.

---

## Files

- **Agent Definition**: `.claude/agents/GITHUB_ISSUE_AGENT.md`
- **Hook**: `.claude/hooks/github_issue_creator.py`
- **Skill Directory**: `.claude/skills/github-issue-manager/`
- **Config**: `.claude/skills/github-issue-manager/config/settings.json`
- **Logs**: `~/.claude/logs/github_issue_debug.log`

---

## Status

**Active** - Hook registered in `settings.local.json`

---

**Last Updated**: 2026-01-16
