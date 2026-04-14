# Command: Targeting Optimizer

## Purpose
Optimize ad targeting based on performance data and lead quality feedback.

## Usage
```
/ads targeting-optimizer {action} [--campaign {name}]
```

Actions: `analyze`, `recommend`, `test`, `expand`, `narrow`

## Analyze Action

Analyze current targeting performance.

### Input
- Campaign performance data
- Lead quality feedback
- Audience segments

### Output
```markdown
## Targeting Analysis: {campaign}

### Audience Performance

| Segment | Spend | Leads | CPL | Quality | Score |
|---------|-------|-------|-----|---------|-------|
| {seg1} | ${X} | {n} | ${Y} | {%} | {n}/10 |
| {seg2} | ${X} | {n} | ${Y} | {%} | {n}/10 |

### Top Performers
1. {segment} - CPL ${X}, Quality {%}
2. {segment} - CPL ${X}, Quality {%}

### Underperformers
1. {segment} - CPL ${X}, Quality {%}
2. {segment} - CPL ${X}, Quality {%}

### Insights
- {insight 1}
- {insight 2}
- {insight 3}

### Recommendations
1. {recommendation}
2. {recommendation}
```

## Recommend Action

Generate targeting recommendations.

### Based on Data
```yaml
recommendations:
  scale:
    - audience: "{name}"
      reason: "Lowest CPL, high quality"
      action: "Increase budget 30%"
      
  test:
    - audience: "{name}"
      reason: "Similar to top performer"
      hypothesis: "Should perform similarly"
      
  pause:
    - audience: "{name}"
      reason: "High CPL, low quality"
      action: "Pause immediately"
      
  refine:
    - audience: "{name}"
      change: "{specific refinement}"
      reason: "To improve quality"
```

### Output
```markdown
## Targeting Recommendations

### Immediate Actions
1. **Scale**: {audience} - {reason}
2. **Pause**: {audience} - {reason}

### Tests to Run
1. {audience test description}
2. {audience test description}

### Refinements
1. {audience}: {specific change}
2. {audience}: {specific change}

### Priority Order
1. {action 1}
2. {action 2}
3. {action 3}
```

## Test Action

Set up an audience test.

### Input
```yaml
test:
  name: "{test name}"
  control: "{current audience}"
  variant: "{new audience}"
  budget_split: "50/50"
  duration: "7 days"
  success_metric: "CPL"
```

### Output
```markdown
## Audience Test Setup

**Test**: {name}
**Duration**: {days}

### Control
- Audience: {definition}
- Budget: ${X}/day

### Variant
- Audience: {definition}
- Budget: ${X}/day

### Success Criteria
- Primary: {metric} improvement of {%}
- Secondary: {metric}

### Checkpoints
- Day 3: First look (no changes)
- Day 5: Early read
- Day 7: Decision

### Decision Rules
- If variant CPL <90% of control → Scale variant
- If variant CPL >110% of control → Keep control
- If within 10% → Continue test
```

## Expand Action

Expand successful targeting.

### Process
1. Identify winning attributes
2. Find similar segments
3. Create expanded audiences
4. Maintain quality signals

### Expansion Options

**LinkedIn**:
- Add similar job titles
- Expand to related industries
- Add lookalike companies
- Broaden seniority (carefully)

**Meta**:
- Lookalike audiences (1%, 2%, 3%)
- Interest expansion
- Behavioral expansion

### Output
```markdown
## Targeting Expansion Plan

### Current Winner
- Audience: {definition}
- CPL: ${X}
- Quality: {%}

### Expansion Options

#### Option A: Job Title Expansion
- Add: {titles}
- Est. size increase: {%}
- Risk: {low/medium/high}

#### Option B: Industry Expansion  
- Add: {industries}
- Est. size increase: {%}
- Risk: {low/medium/high}

#### Option C: Lookalike
- Source: {audience}
- Size: {%}
- Est. quality: {assessment}

### Recommended Sequence
1. {first expansion} - lowest risk
2. {second expansion} - if first works
3. {third expansion} - if scaling needed
```

## Narrow Action

Tighten targeting to improve quality.

### Narrowing Options

**Exclusions**:
- Job functions that don't convert
- Company sizes that don't buy
- Geographic regions
- Competitors

**Refinements**:
- Add required skills/interests
- Increase seniority requirement
- Narrow industry focus
- Add intent signals

### Output
```markdown
## Targeting Refinement Plan

### Current State
- Audience: {definition}
- CPL: ${X}
- Quality: {%}

### Issue
{why quality is low}

### Refinements

#### Exclusions to Add
- Exclude: {criteria}
- Reason: {why}

#### Criteria to Tighten
- Change: {from} → {to}
- Reason: {why}

### Expected Impact
- Audience size: {before} → {after}
- Est. CPL change: {impact}
- Est. quality change: {impact}

### Implementation
1. {step 1}
2. {step 2}
3. {step 3}
```

## Audience Building Templates

### LinkedIn Starter Audiences

```yaml
audience_1_founders:
  name: "Founders - Small Agencies"
  targeting:
    job_function: ["Marketing", "Operations"]
    seniority: ["Owner", "CXO"]
    company_size: "1-10"
    industry: ["Marketing & Advertising", "Professional Services"]
  estimated_size: "5,000-15,000"
  
audience_2_ops_leaders:
  name: "Ops Leaders - SMB"
  targeting:
    job_function: ["Operations", "Business Development"]
    seniority: ["Director", "VP"]
    company_size: "11-50"
    industry: ["Technology", "Professional Services"]
  estimated_size: "15,000-30,000"
```

### Meta Starter Audiences

```yaml
retargeting_visitors:
  name: "Website Visitors 30d"
  source: "Pixel"
  window: "30 days"
  exclusions: ["Converted"]
  
lookalike_customers:
  name: "Lookalike - Past Clients"
  source: "Customer List"
  size: "1%"
  country: "US"
```
