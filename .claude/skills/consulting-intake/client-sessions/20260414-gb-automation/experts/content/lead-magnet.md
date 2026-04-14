# Command: Lead Magnet

## Purpose
Create downloadable resources that capture leads and demonstrate expertise.

## Usage
```
/content lead-magnet {topic} [--type {checklist|template|guide|calculator}]
```

## Input
- Topic/pain point
- Type preference
- Target audience
- Desired outcome after using

## Lead Magnet Types

| Type | Best For | Time to Consume | Complexity |
|------|----------|-----------------|------------|
| Checklist | Process verification | 2-5 min | Low |
| Template | Repeatable tasks | 5-10 min | Medium |
| Guide | Education/how-to | 10-20 min | Medium |
| Calculator | ROI/decisions | 2-5 min | High |

## Process

### Step 1: Define the Magnet

```yaml
lead_magnet:
  title: "{compelling title}"
  subtitle: "{specific promise}"
  type: "{checklist|template|guide|calculator}"
  target_audience: "{who this is for}"
  pain_point: "{what problem it solves}"
  promise: "{specific outcome}"
  time_to_value: "{X minutes}"
```

### Step 2: Outline Content

**Checklist Outline**:
```markdown
# {Title}

## Before You Start
- {Prerequisite 1}
- {Prerequisite 2}

## The Checklist
### Phase 1: {Name}
- [ ] {Step 1}
- [ ] {Step 2}

### Phase 2: {Name}
- [ ] {Step 3}
- [ ] {Step 4}

## Common Mistakes to Avoid
- {Mistake 1}
- {Mistake 2}

## Next Steps
{CTA to service}
```

**Template Outline**:
```markdown
# {Title} Template

## How to Use This Template
{Quick instructions}

## The Template

### Section 1: {Name}
{Template fields with placeholders}

### Section 2: {Name}
{Template fields with placeholders}

## Example (Filled In)
{Completed example}

## Need Help?
{CTA to service}
```

**Guide Outline**:
```markdown
# {Title}

## Why This Matters
{Problem context}

## What You'll Learn
- {Outcome 1}
- {Outcome 2}
- {Outcome 3}

## Chapter 1: {Topic}
{Content}

## Chapter 2: {Topic}
{Content}

## Chapter 3: {Topic}
{Content}

## Quick Start Checklist
{Action items}

## Get Expert Help
{CTA to service}
```

### Step 3: Create Landing Page Copy

```markdown
## Headline
{Benefit-focused headline}

## Subheadline
{Specific promise + timeframe}

## What You'll Get
- {Benefit 1}
- {Benefit 2}
- {Benefit 3}

## Who This Is For
{ICP description}

## Form
- Email (required)
- First name (optional)

## Button
{Action-oriented CTA}
```

### Step 4: Create Follow-Up Sequence

**Email 1 (Immediate)**:
```
Subject: Your {Lead Magnet Name} is here

{Download link}

Quick tip: Start with {first action} to get the fastest result.

More soon,
Greg
```

**Email 2 (Day 2)**:
```
Subject: Did you try {specific tip}?

Most people who download {Lead Magnet} get stuck at {common blocker}.

Here's how to get past it: {tip}

{CTA to next resource or call}
```

**Email 3 (Day 5)**:
```
Subject: The next level

If you've gone through {Lead Magnet}, you're ahead of most.

But here's what separates good from great: {insight}

Want help implementing? {CTA to call}
```

## Output

```markdown
## Lead Magnet: {Title}

**Type**: {type}
**Target**: {audience}
**Promise**: {outcome}

### Assets Created
- [ ] Lead magnet content (PDF/doc)
- [ ] Landing page copy
- [ ] Thank you page copy
- [ ] 3-email follow-up sequence
- [ ] LinkedIn promo post

### Distribution
- Landing page URL: {url}
- Promo post scheduled: {date}
- Email sequence active: {yes/no}
```

## Quality Criteria

Strong lead magnet:
- [ ] Solves ONE specific problem
- [ ] Delivers value in <10 minutes
- [ ] Demonstrates expertise without giving away everything
- [ ] Natural bridge to paid service
- [ ] Easy to consume and implement
- [ ] Shareable (people want to forward it)

## Lead Magnet Ideas for GB Automation

| Title | Type | Pain Point |
|-------|------|------------|
| "AI Automation Audit Checklist" | Checklist | Don't know where to start |
| "Weekly Operations Template" | Template | Disorganized workflows |
| "ROI Calculator: AI Assistant" | Calculator | Uncertain about investment |
| "5-Step AI Setup Guide" | Guide | Technical overwhelm |
