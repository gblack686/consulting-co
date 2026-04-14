# Command: Case Study

## Purpose
Create compelling case studies that demonstrate results and build credibility.

## Usage
```
/content case-study {client_name_or_type} [--format {full|snippet|linkedin}]
```

## Input
- Client name or anonymized type
- Permission level (name, company, anonymous)
- Key metrics/results
- Format needed

## Process

### Step 1: Gather Information

**Required Data**:
```yaml
client:
  name: "{name or type}"
  industry: "{industry}"
  size: "{company size}"
  permission: "{full|company_only|anonymous}"

before_state:
  situation: "{what they were dealing with}"
  pain_points:
    - "{pain 1}"
    - "{pain 2}"
    - "{pain 3}"
  attempted_solutions: "{what they tried}"
  cost_of_problem: "{time/money impact}"

solution:
  approach: "{what we did}"
  timeline: "{how long}"
  key_changes:
    - "{change 1}"
    - "{change 2}"
    - "{change 3}"

after_state:
  results:
    - metric: "{metric 1}"
      before: "{before value}"
      after: "{after value}"
    - metric: "{metric 2}"
      before: "{before value}"
      after: "{after value}"
  qualitative:
    - "{benefit 1}"
    - "{benefit 2}"
  quote: "{client quote}"
```

### Step 2: Select Format

| Format | Length | Use Case |
|--------|--------|----------|
| Full | 500-1000 words | Website, proposals |
| Snippet | 150-250 words | LinkedIn, emails |
| LinkedIn | 200-300 words | Social post |

### Step 3: Write Case Study

**Full Format Structure**:
```markdown
# {Headline: Result + Client Type}

## The Challenge
{2-3 paragraphs describing the before state}

## The Solution
{2-3 paragraphs describing what we did}

## The Results
{Metrics with before/after comparison}

## Key Takeaways
{3 bullet points of learnings}

## Client Quote
> "{Quote}"
> — {Name}, {Title} at {Company}
```

**Snippet Format**:
```markdown
**Challenge**: {Client type} was struggling with {pain}. {Impact}.

**Solution**: We implemented {approach} over {timeline}.

**Results**: 
- {Metric 1}: {before} → {after}
- {Metric 2}: {before} → {after}

**Quote**: "{short quote}"
```

**LinkedIn Format**:
```markdown
{Client type} transformation:

BEFORE:
- {Pain 1}
- {Pain 2}
- {Pain 3}

AFTER ({timeline}):
- {Result 1}
- {Result 2}
- {Result 3}

The shift? {One key insight}

{CTA}
```

### Step 4: Add Visuals

Recommended visuals:
- Before/after comparison chart
- Timeline graphic
- Key metric callouts
- Client logo (if permitted)

### Step 5: Create Derivatives

From each full case study, create:
- 1 LinkedIn post
- 3 snippet quotes
- 1 email proof point
- Proposal insert

## Output

```markdown
## Case Study: {Client/Type}

**Permission Level**: {full|company|anonymous}
**Format**: {full|snippet|linkedin}

---

{Case study content}

---

**Derivatives Created**:
- [ ] LinkedIn post
- [ ] Email snippets
- [ ] Proposal insert

**Tags**: {industry}, {pain_point}, {result_type}
```

## Case Study Bank

Maintain library of case studies indexed by:
- Industry
- Pain point addressed
- Result type (time saved, revenue, efficiency)
- Anonymization level

## Quality Criteria

Strong case study has:
- [ ] Specific, quantified results
- [ ] Clear before/after contrast
- [ ] Relatable pain points
- [ ] Credible timeline
- [ ] Authentic voice
- [ ] Clear takeaway
- [ ] Permission obtained
