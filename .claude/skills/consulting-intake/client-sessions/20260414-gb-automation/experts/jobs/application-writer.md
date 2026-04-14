# Command: Application Writer

## Purpose
Write personalized, consultant-positioned applications for job opportunities.

## Usage
```
/jobs application-writer {opportunity_id_or_url}
```

## Input
- Job opportunity details
- Company research
- Relevant case studies

## Process

### Step 1: Load Opportunity
Pull opportunity data:
- Company name
- Role title
- Job description
- Requirements
- Keywords matched

### Step 2: Research Company
Quick research (2-3 min):
```yaml
company_research:
  name: "{name}"
  what_they_do: "{description}"
  size: "{employees}"
  funding: "{stage/amount}"
  recent_news: "{anything notable}"
  linkedin_presence: "{observations}"
  mutual_connections: ["{names}"]
  specific_need: "{why they're hiring}"
```

### Step 3: Identify Hook
Find the most compelling personalization:

| Hook Type | Example |
|-----------|---------|
| Recent news | "Saw you just raised Series A..." |
| Specific problem | "Your post mentioned struggling with..." |
| Mutual connection | "{Name} and I were just discussing..." |
| Their content | "Your recent article on {topic}..." |
| Company achievement | "Congrats on {milestone}..." |

### Step 4: Select Proof Point
Choose most relevant case study:
- Same industry?
- Same problem?
- Similar company size?
- Comparable results?

### Step 5: Draft Application

```markdown
{Personalized hook referencing their specific situation}

I help {their type of company} {achieve outcome}. Recently, I worked with {similar company} to {specific result with numbers}.

What caught my attention about this role: {specific observation showing you read the posting}.

I'd love to explore how I could help {company} {achieve their goal}. Would a 15-minute call this week work?

Greg Black
GB Automation
{portfolio_or_case_study_link}
```

### Step 6: Quality Check

Checklist:
- [ ] First line is personalized (not generic)
- [ ] Includes quantified result
- [ ] Under 150 words
- [ ] Consultant positioning (not employee)
- [ ] Clear CTA
- [ ] Proofread
- [ ] Link included

### Step 7: Output

```markdown
## Application Ready: {Company} - {Role}

**Opportunity ID**: {id}
**Score**: {score}
**Applied within**: {hours since posted}

---

{Full application text}

---

**Hook Type**: {type used}
**Proof Point**: {case study referenced}
**Word Count**: {n}

**Ready to send**: Yes / Needs review

**Next Step**: Send via {platform}
```

## Application Templates

### Template A: Recent Achievement Hook
```
Congrats on {recent achievement} - that's no small feat.

I've been helping {similar companies} {achieve outcome} through AI automation. Most recently, {example} saw {result}.

I noticed you're looking for help with {their need}. Happy to share how we approached similar challenges.

Quick call this week?

Greg Black | GB Automation
{link}
```

### Template B: Problem Hook
```
{Pain point observation from their posting}

I get it - I've helped {n} companies solve exactly this. {Example} went from {before} to {after} in {timeframe}.

Would love to explore if our approach fits what you're building.

15 minutes this week?

Greg Black | GB Automation
{link}
```

### Template C: Mutual Connection Hook
```
{Mutual connection} mentioned you might need help with {topic}.

I've been working on exactly this - helped {example} {achieve result}.

Happy to share what we've learned. Quick call?

Greg Black | GB Automation
{link}
```

## Do's and Don'ts

### Do
- Reference something specific about them
- Lead with a result
- Keep it short (<150 words)
- Make responding easy
- Position as consultant

### Don't
- Start with "I'm interested in..."
- Write more than 3 paragraphs
- Attach resume upfront
- Use corporate speak
- Sound desperate
