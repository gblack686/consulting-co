# HEARTBEAT.md - GB Automation

## Scheduled Operations

### Daily Heartbeats

| Time (ET) | Operation | Domain | Description |
|-----------|-----------|--------|-------------|
| 6:00 AM | `morning-briefing` | All | Compile overnight activity, plan day |
| 8:00 AM | `outreach-batch` | Outreach | Send queued connection requests |
| 9:00 AM | `content-publish` | Content | Post scheduled LinkedIn content |
| 12:00 PM | `pipeline-check` | Sales | Review active conversations, suggest follow-ups |
| 3:00 PM | `job-scan` | Jobs | Check job boards for matches |
| 6:00 PM | `daily-metrics` | All | Compile daily metrics report |
| 9:00 PM | `self-improve-cycle` | All | Run self-improvement on all domains |

### Weekly Heartbeats

| Day | Time | Operation | Domain | Description |
|-----|------|-----------|--------|-------------|
| Monday | 7:00 AM | `weekly-planning` | All | Set weekly targets, review pipeline |
| Wednesday | 2:00 PM | `content-calendar` | Content | Plan next week's content |
| Friday | 5:00 PM | `weekly-review` | All | Metrics review, learnings log update |
| Sunday | 8:00 PM | `week-prep` | All | Prep outreach batches for Monday |

### Trigger-Based Operations

| Trigger | Operation | Domain | Response Time |
|---------|-----------|--------|---------------|
| New LinkedIn message | `dm-response` | Outreach | <1 hour |
| Discovery call booked | `call-prep` | Sales | Immediate |
| Proposal requested | `proposal-draft` | Sales | <4 hours |
| New job match | `job-alert` | Jobs | Immediate |
| Ad budget 80% spent | `budget-alert` | Ads | Immediate |

## Cron Definitions

```bash
# Morning briefing
0 6 * * * openclaw run morning-briefing

# Outreach batch
0 8 * * * openclaw run outreach-batch

# Content publish
0 9 * * * openclaw run content-publish

# Pipeline check
0 12 * * * openclaw run pipeline-check

# Job scan
0 15 * * * openclaw run job-scan

# Daily metrics
0 18 * * * openclaw run daily-metrics

# Self-improve cycle
0 21 * * * openclaw run self-improve-all

# Weekly planning (Monday)
0 7 * * 1 openclaw run weekly-planning

# Content calendar (Wednesday)
0 14 * * 3 openclaw run content-calendar

# Weekly review (Friday)
0 17 * * 5 openclaw run weekly-review

# Week prep (Sunday)
0 20 * * 0 openclaw run week-prep
```

## Health Checks

| Check | Frequency | Threshold | Action |
|-------|-----------|-----------|--------|
| API connectivity | Every 5 min | 3 failures | Alert + retry |
| Outreach quota | Hourly | <10 remaining | Pause batch |
| Response rate | Daily | <10% | Flag for review |
| Error rate | Hourly | >5% | Alert + investigate |
| Budget burn | Daily | >25%/week | Alert |

## Self-Improvement Schedule

Each domain runs self-improvement:

| Domain | Frequency | Focus |
|--------|-----------|-------|
| Outreach | Daily 9 PM | Message effectiveness, response rates |
| Content | Daily 9 PM | Engagement metrics, topic performance |
| Sales | Daily 9 PM | Conversion rates, objection handling |
| Jobs | Daily 9 PM | Match quality, application success |
| Ads | Daily 9 PM | ROAS, targeting efficiency |

All domains also run a **weekly deep improvement** on Friday at 6 PM, analyzing the full week's data and updating expertise files.
