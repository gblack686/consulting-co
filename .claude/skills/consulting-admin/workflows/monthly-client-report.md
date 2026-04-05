# Monthly Client Report

Generate per-client monthly summary reports. Runs 1st of each month at 10am PT.

## Workflow

1. For each client in `.claude/skills/consulting-intake/client-sessions/`:
   - Read client_profile.json for name, business, contact info
   - Scan git log for all commits in the past month touching this client
   - Read weekly digests from `.claude/context/clients/weekly-digest-*.md` (last 4)
   - Read health scores from `.claude/context/clients/health-scores.md` (last 4 entries)
   - Read VALIDATION_REPORT.md for deployment quality score
2. Compile per-client monthly report
3. Save to `.claude/context/clients/monthly-{client-slug}-{YYYY-MM}.md`
4. Save summary of all clients to `.claude/context/clients/monthly-summary-{YYYY-MM}.md`

## Per-Client Report Format

```markdown
# Monthly Report — {Client Name}
## {Month Year}

### Summary
- **Domains Active**: {count} ({list})
- **Agent**: {agent name} on {platform}
- **Health Score Trend**: {avg of 4 weekly scores} ({trend: up/down/flat})

### Deliverables This Month
- {bullet list from git commits + weekly wraps}

### Key Metrics
- Commits: {count}
- Files changed: {count}
- Validation score: {score}/100
- Sessions held: {count}

### Issues & Resolutions
- {any blockers encountered and how they were resolved}

### Recommendations
- {1-3 actionable recommendations for next month}

### Next Steps
- [ ] {planned work for next month}
```

## All-Clients Summary Format

```markdown
# GBAutomation Monthly Summary — {Month Year}

| Client | Domains | Health | Deliverables | Revenue | Status |
|--------|---------|--------|-------------|---------|--------|
| Greg Trading | 5 | 8.0 | 12 commits | ${amount} | Active |
| Erica Creations | 4 | 6.5 | 8 commits | ${amount} | Active |
| Fish Group | 5 | 7.2 | 15 commits | ${amount} | Active |

**Total Revenue**: ${total}
**Active Clients**: {count}
**New This Month**: {count or None}
```
