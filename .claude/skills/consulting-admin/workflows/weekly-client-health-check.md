# Weekly Client Health Check

Score each client's engagement and deployment health. Runs Monday 9am PT.

## Health Dimensions (per client)

| Dimension | Weight | How to Score |
|-----------|--------|-------------|
| Deployment Health | 30% | Check if agent config exists, last deploy date, smoke test results |
| Engagement Recency | 25% | Days since last email/session/commit activity |
| Open Items | 20% | Count of unresolved blockers or pending deliverables |
| Billing Status | 15% | Paid/unpaid, approaching renewal |
| Satisfaction Signal | 10% | Positive/negative tone in recent emails or session notes |

## Workflow

1. For each client in `.claude/skills/consulting-intake/client-sessions/`:
   - Read `session_output/client_profile.json` for client name and metadata
   - Read `workspace/` folder for deployment artifacts (existence = deployed)
   - Check `VALIDATION_REPORT.md` for last validation score
   - Check git log for commits in last 7 days touching this client
   - Check for any files with "blocker", "issue", or "TODO" references
2. Score each dimension 0-10, compute weighted total
3. Flag any client scoring below 6/10 as NEEDS_ATTENTION
4. Append results to `.claude/context/clients/health-scores.md` (running log)

## Output

```markdown
# Client Health — {date}

| Client | Deploy | Engage | Items | Billing | Signal | Total | Flag |
|--------|--------|--------|-------|---------|--------|-------|------|
| Greg Trading | 8 | 7 | 9 | 8 | 8 | 8.0 | OK |
| Erica Creations | 6 | 5 | 7 | 7 | 7 | 6.2 | OK |
| Fish Group | 7 | 8 | 6 | 7 | 8 | 7.1 | OK |

## Action Items
- {any client below 6.0 gets a recommended action}
```
