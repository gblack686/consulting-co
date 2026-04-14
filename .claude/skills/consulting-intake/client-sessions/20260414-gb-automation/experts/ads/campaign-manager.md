# Command: Campaign Manager

## Purpose
Manage, monitor, and optimize advertising campaigns across platforms.

## Usage
```
/ads campaign-manager {action} [--campaign {name}] [--platform {linkedin|meta}]
```

Actions: `status`, `launch`, `pause`, `scale`, `report`

## Status Action

Get current campaign performance.

### Output
```markdown
## Campaign Status - {date}

### LinkedIn Campaigns

| Campaign | Status | Spend | Leads | CPL | CTR |
|----------|--------|-------|-------|-----|-----|
| {name} | {active/paused} | ${X} | {n} | ${Y} | {%} |

**MTD Totals**: Spend ${X}, Leads {n}, Avg CPL ${Y}

### Meta Campaigns

| Campaign | Status | Spend | Leads | CPL | CTR |
|----------|--------|-------|-------|-----|-----|
| {name} | {active/paused} | ${X} | {n} | ${Y} | {%} |

### Budget Status
- Monthly budget: $500
- Spent: ${X} ({%})
- Remaining: ${Y}
- Pace: {on track / over / under}

### Alerts
- {any issues or opportunities}
```

## Launch Action

Launch a new campaign.

### Input
```yaml
campaign:
  name: "{name}"
  platform: "{linkedin|meta}"
  objective: "{lead_gen|traffic|awareness}"
  audience: "{audience_name}"
  daily_budget: ${X}
  creatives: ["{creative_ids}"]
  offer: "{what we're promoting}"
```

### Process
1. Validate all components ready
2. Confirm tracking is set up
3. Create campaign in platform
4. Set targeting parameters
5. Upload creatives
6. Set budget and schedule
7. Launch and verify

### Output
```markdown
## Campaign Launched

**Name**: {name}
**Platform**: {platform}
**Objective**: {objective}
**Daily Budget**: ${X}
**Audience Size**: {estimate}
**Creatives**: {n} variants

**Tracking**: Verified
**Status**: Live

**First check**: {date/time}
```

## Pause Action

Pause underperforming campaign.

### Input
- Campaign name
- Reason for pause

### Process
1. Pause campaign in platform
2. Document reason
3. Note learnings
4. Set review reminder

### Output
```markdown
## Campaign Paused

**Campaign**: {name}
**Paused at**: {datetime}
**Spend before pause**: ${X}
**Leads before pause**: {n}
**CPL**: ${Y}

**Reason**: {reason}

**Learning**: {what we learned}

**Next action**: {what happens next}
```

## Scale Action

Scale a performing campaign.

### Input
- Campaign name
- Scale amount (% or $)

### Pre-Scale Checklist
- [ ] CPL stable for 5+ days
- [ ] Lead quality confirmed
- [ ] Budget available
- [ ] Creative not fatigued

### Process
1. Increase daily budget by {amount}
2. Monitor for CPL changes
3. Set alert for performance drop
4. Document the scale

### Output
```markdown
## Campaign Scaled

**Campaign**: {name}
**Previous budget**: ${X}/day
**New budget**: ${Y}/day
**Increase**: {%}

**Pre-scale CPL**: ${Z}
**Expected leads increase**: +{n}/day

**Review date**: {3 days out}
```

## Report Action

Generate performance report.

### Input
- Date range
- Campaigns to include

### Output
```markdown
## Campaign Report: {date_range}

### Executive Summary
- Total spend: ${X}
- Total leads: {n}
- Avg CPL: ${Y}
- Lead quality: {assessment}
- ROAS: {X}x (estimated)

### Campaign Breakdown

#### {Campaign 1}
- Spend: ${X}
- Leads: {n}
- CPL: ${Y}
- Best creative: {name}
- Best audience: {name}

#### {Campaign 2}
...

### Key Learnings
1. {learning 1}
2. {learning 2}
3. {learning 3}

### Recommendations
1. {action 1}
2. {action 2}
3. {action 3}

### Next Period Plan
- Budget: ${X}
- Focus: {priorities}
- Tests: {what to try}
```

## Daily Monitoring Checklist

```
[ ] All campaigns running
[ ] Spend within expected range
[ ] No CPL spikes
[ ] New leads followed up
[ ] Creative fatigue check
[ ] Budget pace on track
```
