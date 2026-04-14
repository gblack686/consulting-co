# Command: Prospect Research

## Purpose
Research and qualify prospects for outreach, gathering personalization data for effective messaging.

## Usage
```
/outreach prospect-research {target_criteria}
```

## Input
- Target criteria (industry, role, company size, signals)
- Number of prospects to research
- Priority level (P1-P4)

## Process

### Step 1: Identify Prospects
1. Search LinkedIn Sales Navigator (or standard search)
2. Apply filters:
   - Role: Founder, CEO, COO, Head of Ops
   - Industry: {target_industry}
   - Company size: 1-50 employees
   - Location: US, UK, Canada (English-speaking)
   - Activity: Posted in last 30 days

### Step 2: Initial Screen
For each prospect:
- [ ] Fits ICP role criteria
- [ ] Company size matches
- [ ] Active on LinkedIn (posts/comments recently)
- [ ] No existing connection/conversation
- [ ] Not a competitor

### Step 3: Deep Research
For qualified prospects, gather:

**Professional Context**
- Current role and company
- Previous experience
- Key accomplishments
- Content they've posted

**Company Context**
- What the company does
- Recent news/funding
- Tech stack (if visible)
- Team size and growth

**Personalization Hooks**
- Recent posts or comments
- Mutual connections
- Shared interests or background
- Pain points mentioned

**Engagement Score**
Calculate based on:
- Posts in last 30 days (1 point each)
- Comments given (0.5 points each)
- Followers count (bonus if >1000)

### Step 4: Output

Generate prospect card:
```yaml
name: {full_name}
title: {role}
company: {company_name}
linkedin: {url}
priority: {P1-P4}
engagement_score: {n}

personalization_hooks:
  - {hook_1}
  - {hook_2}
  - {hook_3}

recent_activity:
  - type: {post/comment}
    topic: {topic}
    date: {date}

pain_signals:
  - {signal_1}
  - {signal_2}

suggested_template: {A/B/C}
custom_first_line: "{personalized opening}"
```

## Output Location
Save to: `session_output/domains/outreach/prospects/{company_name}.yaml`

## Batch Processing
When researching multiple prospects:
1. Process in parallel where possible
2. Deduplicate against existing prospects
3. Sort output by priority
4. Generate summary stats

## Quality Criteria
Each prospect card must have:
- [ ] At least 2 personalization hooks
- [ ] Custom first line drafted
- [ ] Priority assigned
- [ ] Engagement score calculated
