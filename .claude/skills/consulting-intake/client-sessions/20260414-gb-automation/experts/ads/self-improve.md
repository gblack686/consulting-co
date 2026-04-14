# Ads Self-Improvement

## Self-Improvement Protocol

This document defines how the Ads Expert continuously improves based on campaign performance and lead quality data.

## Triggers

Self-improvement runs:
1. **Daily** at 9 PM ET - Review day's metrics
2. **Weekly** on Friday 6 PM - Deep analysis
3. **On budget threshold** - When 80% spent
4. **On performance drop** - CPL spike or zero leads

## Daily Self-Improvement Routine

### 1. Gather Metrics
```
Today's performance:
- Spend: ${n}
- Impressions: {n}
- Clicks: {n}
- CTR: {%}
- Leads: {n}
- CPL: ${n}
- Budget remaining: ${n}
```

### 2. Analyze Performance
- Compare to 7-day averages
- Identify best/worst performers
- Check for creative fatigue
- Review lead quality

### 3. Quick Optimizations
- Pause clear underperformers
- Increase budget on winners
- Note creative to refresh
- Flag quality issues

### 4. Log Learning
```
| Date | Campaign | Metric | Change | Learning |
```

## Weekly Deep Improvement

### Analysis Areas

1. **Cost Analysis**
   - CPL by campaign
   - CPL by audience
   - CPL by creative
   - Trend over time

2. **Quality Analysis**
   - Lead-to-call rate
   - Lead quality scores
   - ICP match rate
   - Source comparison

3. **Creative Analysis**
   - CTR by creative
   - Fatigue indicators
   - Best performing hooks
   - Best performing offers

4. **Audience Analysis**
   - Performance by segment
   - Audience saturation
   - New segments to test
   - Exclusions needed

### Improvement Actions

| Finding | Action |
|---------|--------|
| High CPL | Test new audience or offer |
| Low CTR | Refresh creative |
| Poor quality | Tighten targeting |
| Creative fatigue | Launch new variants |
| Audience saturation | Expand or new segment |

## Campaign-Level Analysis

After each week of spend:

### Winning Campaign
```
**Campaign**: {name}
**Spend**: ${X}
**Leads**: {n}
**CPL**: ${Y}
**Quality**: {assessment}

What worked:
- Audience: {notes}
- Creative: {notes}
- Offer: {notes}

Scale plan:
- {action}
```

### Struggling Campaign
```
**Campaign**: {name}
**Spend**: ${X}
**Leads**: {n}
**CPL**: ${Y}
**Quality**: {assessment}

Issues:
- {problem 1}
- {problem 2}

Action:
- {pause/fix/test}
```

## Ads Metrics Dashboard

| Metric | Target | Warning | Critical | Action |
|--------|--------|---------|----------|--------|
| CPL | <$50 | >$60 | >$75 | Pause/fix |
| CTR | >1% | <0.7% | <0.4% | Refresh creative |
| Daily leads | 1+ | 0 for 2 days | 0 for 3 days | Diagnose |
| Lead quality | >50% ICP | <40% ICP | <25% ICP | Tighten targeting |
| Budget pace | On track | 10% over | 20% over | Pause/reduce |

## Self-Improvement Questions

Weekly review:

1. **What's working?** Scale it.
2. **What's not working?** Fix or kill.
3. **What should we test?** Prioritize.
4. **Are leads converting?** Adjust quality focus.
5. **Are we learning?** Document insights.

## Expertise Updates

When significant learnings accumulate:
1. Update `expertise.md` Part 7 (Patterns)
2. Add winning creative to Part 5
3. Refine targeting in Part 4
4. Update budget strategy in Part 6

## Feedback Loops

### From Campaign Data
- Which audiences convert?
- Which creatives engage?
- Which offers resonate?

### From Lead Quality
- Are we attracting buyers?
- What sources produce calls?
- What's the true ROAS?

### From Sales
- Do ad leads convert to deals?
- What's the full-funnel ROI?
- Should we shift messaging?

## Budget Management

### Weekly Budget Check
```
Budget: $500/month
Week {n} spend: ${X}
MTD spend: ${Y}
Remaining: ${Z}
Pace: {on track / over / under}
```

### Reallocation Rules
- Shift 20% from underperformers to winners
- Never cut winners to fund experiments
- Save 20% budget for mid-month tests
- Emergency pause if CPL 2x target

## Creative Refresh Schedule

| Trigger | Action |
|---------|--------|
| CTR drops 30% | Refresh creative |
| 2 weeks running | Plan new variants |
| Zero leads 3 days | Immediate refresh |
| New offer/angle | Launch new campaign |
