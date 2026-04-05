# Friday Client Wrap-Up

End-of-week summary of work done, hours logged, and prep for next week. Runs Friday 3pm PT.

## Workflow

1. Scan git log for all commits this week (Monday-Friday) in the consulting-co repo
2. Categorize commits by client (grep for client names in commit messages and file paths)
3. For each client, summarize:
   - What was delivered or progressed
   - Files changed (count and key files)
   - Any open PRs or branches
4. Check `.claude/skills/consulting-intake/client-sessions/` for any new session folders created this week
5. Note any upcoming renewals, follow-ups, or deadlines from session files
6. Save to `.claude/context/clients/weekly-wrap-{YYYY-MM-DD}.md`

## Output

```markdown
# Week Wrap-Up — {date range}

## Work Completed

### Greg Trading
- {bullet list of deliverables/progress}
- Files: {count} changed
- Branch: {branch name if applicable}

### Erica Creations
- {bullet list}

### Fish Group
- {bullet list}

## Internal (GBAutomation)
- {any infrastructure, tooling, or skill work done}

## Next Week
- [ ] {follow-up item 1}
- [ ] {follow-up item 2}
- [ ] {follow-up item 3}

## New Sessions This Week
- {any new client sessions created, or "None"}
```
