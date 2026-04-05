# Wednesday Lead Follow-Up

Mid-week check for new leads, prospect inquiries, and booking link activity. Runs Wednesday 10am PT.

## Workflow

1. Check git log for any new client session folders created in the past 7 days
2. Read `.claude/skills/consulting-intake/client-sessions/` for sessions without a `workspace/` folder (intake started but not yet built)
3. Check for any files referencing "prospect", "lead", or "inquiry" in `.claude/context/clients/`
4. For any incomplete intakes:
   - Note what stage they're at (transcript only? parsed? workspace built?)
   - Flag as follow-up needed
5. Compile lead pipeline status
6. Save to `.claude/context/clients/lead-pipeline-{YYYY-MM-DD}.md`

## Output

```markdown
# Lead Pipeline — {date}

## Active Prospects
| Name | First Contact | Stage | Next Action | Days Open |
|------|--------------|-------|-------------|-----------|
| {name} | {date} | {stage} | {action} | {days} |

## Recent Bookings
- {any new calendar events with "OpenClaw Setup" or "AI Agent Build" in title}

## Stale Leads (>14 days no activity)
- {name} — last activity {date}, recommend: {action}

## This Week's Follow-Ups
1. [ ] {specific follow-up action}
2. [ ] {specific follow-up action}
```
