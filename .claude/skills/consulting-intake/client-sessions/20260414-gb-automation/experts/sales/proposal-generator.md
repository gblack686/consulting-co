# Command: Proposal Generator

## Purpose
Create tailored proposals based on discovery call insights.

## Usage
```
/sales proposal-generator {prospect} [--tier {standard|professional|custom}]
```

## Input
- Discovery call notes/debrief
- Prospect company and pain points
- Tier preference (if specified)

## Process

### Step 1: Load Discovery Data
Pull from discovery debrief:
- Company name and context
- Primary and secondary pain points
- Quantified impact
- Key quotes
- Qualification scores

### Step 2: Select Tier
```yaml
tier_selection:
  standard:
    price: "$3,500/month"
    commitment: "3 months"
    domains: 2
    fit: "Single founder, small team, focused needs"
    
  professional:
    price: "$5,000/month"
    commitment: "3 months"
    domains: 5
    fit: "Growing team, complex workflows, multiple areas"
    
  enterprise:
    price: "Custom"
    commitment: "6 months"
    domains: "Unlimited"
    fit: "Established company, many stakeholders, complex requirements"
```

### Step 3: Calculate ROI
```yaml
roi_calculation:
  hours_saved_weekly: {X}
  hourly_value: ${Y}
  monthly_value: ${X * Y * 4.3}
  investment: ${tier_price}
  monthly_roi: ${monthly_value - investment}
  roi_percentage: {%}
  payback_period: "{weeks}"
```

### Step 4: Select Case Study
Choose based on:
- Industry match
- Pain point match
- Company size match
- Result relevance

### Step 5: Generate Proposal

## Proposal Template

```markdown
# Proposal for {Company Name}

Prepared for: {Prospect Name}
Prepared by: Greg Black, GB Automation
Date: {Date}

---

## Executive Summary

Based on our conversation on {date}, I understand that {Company} is facing challenges with {primary_pain}, which is costing approximately {quantified_impact} per {time_period}.

I'm recommending our {Tier} package, which will {primary_benefit} within {timeline}.

---

## Understanding Your Situation

You shared that:
- {Pain point 1 with their words}
- {Pain point 2 with their words}
- {Pain point 3 with their words}

> "{Key quote from discovery}"

This is costing you {hours/money} and preventing you from {what they want to do instead}.

---

## Proposed Solution

### What We'll Build

**Domain 1: {Name}**
- {Workflow 1}
- {Workflow 2}
- {Workflow 3}

**Domain 2: {Name}**
- {Workflow 1}
- {Workflow 2}
- {Workflow 3}

{Add more domains if Professional tier}

### How It Works

**Week 1: Discovery & Setup**
- 90-minute intake session
- AI assistant configured
- First workflows live

**Week 2-4: Expansion**
- Additional workflows added
- Refinement based on feedback
- Self-improvement active

**Ongoing**
- Continuous improvement
- Weekly check-ins
- Priority support

---

## Expected Outcomes

Based on similar clients, you can expect:

| Metric | Current | After 90 Days |
|--------|---------|---------------|
| Hours spent on {task} | {X}/week | {Y}/week |
| {Other metric} | {before} | {after} |
| {Other metric} | {before} | {after} |

### ROI Projection

| Item | Value |
|------|-------|
| Estimated time saved | {X} hours/week |
| Value of your time | ${Y}/hour |
| Monthly value created | ${Z} |
| Monthly investment | ${tier_price} |
| **Net monthly ROI** | **${Z - tier_price}** |
| **ROI percentage** | **{%}** |

---

## Social Proof

### Similar Client: {Company Type}

**Challenge**: {What they faced}

**Solution**: {What we did}

**Results**: 
- {Result 1}
- {Result 2}
- {Result 3}

> "{Client quote}"

---

## Investment

### {Tier Name} Package

**${tier_price}/month** (3-month commitment)

Includes:
- {Inclusion 1}
- {Inclusion 2}
- {Inclusion 3}
- {Inclusion 4}

Total investment: **${tier_price * 3}** for 3 months

---

## Next Steps

1. **Review this proposal** and let me know any questions
2. **Schedule kick-off** - I have availability {dates}
3. **Sign & pay** - Contract and payment link below
4. **90-minute intake** - We get started immediately

Ready to proceed?

[Schedule Kick-off Call] | [Sign Contract]

---

## Questions?

Reply to this email or book a quick call: {calendar_link}

Looking forward to helping {Company} {achieve_outcome}.

Greg Black
GB Automation
```

## Output

```markdown
## Proposal Generated: {Company}

**Tier**: {tier}
**Price**: ${price}/month
**Domains**: {n}

### Files Created
- proposal_{company}_{date}.md
- proposal_{company}_{date}.pdf (if PDF enabled)

### Key Customizations
- Pain points: {list}
- Case study: {which}
- ROI: {percentage}

### Next Steps
- [ ] Review proposal
- [ ] Send to prospect
- [ ] Set follow-up for {date}
```

## Quality Checklist

Before sending:
- [ ] Company name spelled correctly
- [ ] Pain points reflect their words
- [ ] ROI calculation is realistic
- [ ] Case study is relevant
- [ ] Pricing is correct for tier
- [ ] No placeholder text remaining
- [ ] Next steps are clear
- [ ] Links work
