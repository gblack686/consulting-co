---
description: Generate a session report summarizing all LinkedIn activity today
argument-hint: [date]
---

# LinkedIn Session Report

Aggregate all LinkedIn activity logs for a given date into a single session report.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| OUTPUT_DIR | `.claude/context/linkedin` | Where logs are stored |
| DATE | today | Override with {PROMPT} if specified |

## Workflow

1. Determine the date — use {PROMPT} if provided, otherwise today's date
2. Read all log files for that date:
   - `{OUTPUT_DIR}/{date}_prospect_research.json`
   - `{OUTPUT_DIR}/{date}_profile_views.json`
   - `{OUTPUT_DIR}/{date}_engagement_log.json`
   - `{OUTPUT_DIR}/{date}_outreach_log.json`
   - `{OUTPUT_DIR}/{date}_inmail_log.json`
3. If `prospect_master.json` exists, read it for pipeline totals
4. Aggregate the data into a session report
5. Save report to `{OUTPUT_DIR}/{date}_session_report.md`
6. Display the report

## Report Format

```markdown
# LinkedIn Session Report — {date}

## Credits Used Today
| Type | Used | Remaining (est.) | Monthly Total |
|------|------|-------------------|---------------|
| Profile views | {n} | unlimited | unlimited |
| Connection requests | {n} | ~{n} | ~100/week |
| InMails | {n} | {n} | {15 or 50} |
| Engagements (free) | {n} | unlimited | unlimited |

## Activity Summary
| Action | Count |
|--------|-------|
| Profiles researched | {n} |
| Profile view viewers harvested | {n} |
| Posts liked | {n} |
| Comments left | {n} |
| Connection requests sent | {n} |
| InMails sent | {n} |
| **Total actions** | **{n}** |

## Blocklist Enforced
| Blocked | Count | Rule |
|---------|-------|------|
| Accenture Federal | {n} | accenture-federal |

## Prospect Pipeline (Cumulative)
| Status | Count |
|--------|-------|
| Researched | {n} |
| Engaged | {n} |
| Connection sent | {n} |
| Connected | {n} |
| InMail sent | {n} |
| Replied | {n} |
| Meeting booked | {n} |
| Converted | {n} |
| **Total prospects** | **{n}** |

## Top Prospects Actioned Today
| Name | Company | Title | Action | Fit Score |
|------|---------|-------|--------|-----------|
| {name} | {company} | {title} | {action} | {score} |

## Issues
- {any CAPTCHAs, throttling, errors, or anomalies}

## Recommendations
- {next steps based on credits remaining and pipeline status}
```

## Notes

- This skill does NOT open a browser — it reads local log files only
- Run at end of day to summarize activity
- Use before planning tomorrow's campaign
