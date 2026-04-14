# Command: Discovery Call

## Purpose
Conduct effective discovery calls that qualify prospects and set up successful proposals.

## Usage
```
/sales discovery-call {prospect} [--prep|--conduct|--debrief]
```

## Modes

### Prep Mode
Prepare for an upcoming discovery call.

### Conduct Mode
Real-time support during the call.

### Debrief Mode
Post-call analysis and next steps.

## Prep Mode Process

### Step 1: Research Prospect
```yaml
research:
  company: "{name}"
  website: "{url}"
  industry: "{industry}"
  size: "{employees/revenue}"
  recent_news: "{relevant updates}"
  
  prospect:
    name: "{name}"
    role: "{title}"
    linkedin: "{url}"
    background: "{relevant history}"
    content_engaged: "{posts, likes, etc.}"
```

### Step 2: Identify Likely Pain Points
Based on research, hypothesize:
1. Primary pain: {hypothesis}
2. Secondary pain: {hypothesis}
3. Potential blocker: {hypothesis}

### Step 3: Prepare Personalized Questions
```
Opening hook: "{specific observation}"

Questions:
1. "{personalized question based on research}"
2. "{question about their specific situation}"
3. "{question about a recent post/update}"
```

### Step 4: Select Case Study
Choose most relevant case study based on:
- Same industry?
- Same company size?
- Same pain point?
- Similar results needed?

### Step 5: Generate Call Brief
```markdown
## Discovery Call Brief: {Prospect Name}

**Scheduled**: {datetime}
**Duration**: {30/45 min}

### Quick Facts
- Company: {name} - {what they do}
- Role: {title}
- Size: {employees}
- Likely pains: {hypotheses}

### Personalized Opening
"{opening hook}"

### Key Questions
1. {question}
2. {question}
3. {question}

### Case Study Ready
{Title} - {one-line summary}

### Watch For
- {buying signal 1}
- {warning sign 1}

### Goal
{specific goal for this call}
```

## Conduct Mode Support

### Call Flow Tracker
```
[  ] Opening & rapport (2 min)
[  ] Set agenda (1 min)
[  ] Situation questions (5 min)
[  ] Problem questions (10 min)
[  ] Implication questions (5 min)
[  ] Qualification (5 min)
[  ] Solution fit (5 min)
[  ] Next steps (5 min)
```

### Real-Time Prompts

If stuck on opening:
- "Thanks for taking the time. Before we dive in, I noticed {observation} - tell me more about that."

If stuck on pain:
- "What keeps you up at night about {topic}?"
- "If you had to pick one thing to fix, what would it be?"

If need to quantify:
- "How many hours does that cost you each week?"
- "What's the dollar impact of that?"

If need to qualify:
- "What's your timeline for solving this?"
- "Is there a budget for this?"
- "Who else needs to weigh in?"

### Note-Taking Template
```
Situation:
- Current tools: 
- Team size:
- Key processes:

Pain Points:
- Primary:
- Secondary:
- Impact:

Qualification:
- Budget: Y/N
- Authority: Y/N
- Need: Y/N
- Timeline:

Solution Fit:
- Good fit: Y/N
- Domains needed:
- Complexity:

Next Steps:
- Action:
- By when:
```

## Debrief Mode Process

### Step 1: Capture Notes
Immediately after call, document:
- Key pain points identified
- Specific quotes from prospect
- Qualification status
- Red flags or concerns
- Buying signals observed

### Step 2: Score Opportunity
```yaml
qualification:
  budget: {1-5}
  authority: {1-5}
  need: {1-5}
  timeline: {1-5}
  total: {out of 20}
  
fit_assessment: "{good fit / maybe / poor fit}"
recommended_action: "{proposal / nurture / disqualify}"
```

### Step 3: Plan Next Steps
If proceeding to proposal:
- Deadline: {when}
- Key points to address: {list}
- Case study to include: {which}
- ROI to calculate: {based on what}

### Step 4: Update Pipeline
- Move to appropriate stage
- Set follow-up task
- Log call summary

## Output

```markdown
## Discovery Call Debrief: {Prospect}

**Date**: {date}
**Duration**: {actual}
**Attendees**: {who}

### Summary
{2-3 sentence summary}

### Pain Points
1. {pain 1} - Impact: {quantified}
2. {pain 2} - Impact: {quantified}

### Key Quotes
> "{memorable quote}"
> "{memorable quote}"

### Qualification Score
Budget: {score}/5
Authority: {score}/5
Need: {score}/5
Timeline: {score}/5
**Total: {score}/20**

### Fit Assessment
{assessment with reasoning}

### Next Steps
- [ ] {action} by {date}
- [ ] {action} by {date}

### Notes for Proposal
{specific points to address}
```
