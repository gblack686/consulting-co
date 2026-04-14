# Command: Job Monitor

## Purpose
Scan job boards for relevant opportunities matching our criteria.

## Usage
```
/jobs job-monitor [--board {linkedin|wellfound|all}] [--keywords {custom}]
```

## Default Keywords

```yaml
keywords:
  primary:
    - "AI consultant"
    - "AI automation"
    - "Claude consultant"
    - "LLM contract"
    - "AI operations"
  
  secondary:
    - "automation specialist"
    - "AI integration"
    - "process automation"
    - "AI workflow"
    - "no-code automation"
```

## Process

### Step 1: Scan Boards
For each configured board:
1. Search each keyword
2. Filter by criteria (remote, contract)
3. Deduplicate results
4. Sort by posting date

### Step 2: Initial Filter
Exclude opportunities that:
- Require full-time commitment only
- Are onsite only
- Posted >7 days ago
- Have 100+ applicants
- Mention rate < $100/hour

### Step 3: Score Opportunities
```yaml
scoring:
  perfect_match: # Score 90-100
    - Exact keyword match
    - Contract/consulting specified
    - Rate mentioned and good
    - Posted <24 hours ago
    - <20 applicants
  
  good_match: # Score 70-89
    - Related keyword
    - Remote mentioned
    - Posted <3 days ago
    - <50 applicants
  
  maybe: # Score 50-69
    - Tangential keyword
    - Full-time but could pitch consulting
    - Posted <7 days ago
```

### Step 4: Output Report

```markdown
## Job Monitor Report - {date}

**Scan Time**: {timestamp}
**Boards Scanned**: {list}
**Total Found**: {n}
**After Filter**: {n}

### Priority 1 (Score 90+) - Apply Today
| Company | Role | Keywords | Posted | Applicants | Score |
|---------|------|----------|--------|------------|-------|
| {name} | {role} | {keywords} | {when} | {n} | {score} |

### Priority 2 (Score 70-89) - Apply This Week
| Company | Role | Keywords | Posted | Applicants | Score |
|---------|------|----------|--------|------------|-------|
| {name} | {role} | {keywords} | {when} | {n} | {score} |

### Maybe (Score 50-69) - If Time Allows
| Company | Role | Keywords | Posted | Applicants | Score |
|---------|------|----------|--------|------------|-------|
| {name} | {role} | {keywords} | {when} | {n} | {score} |

### Summary
- Immediate action needed: {n} opportunities
- Apply this week: {n} opportunities
- Passed on: {n} opportunities (reasons: {breakdown})
```

## Alert Triggers

Send immediate Slack alert when:
- Perfect match found (score 90+)
- Target company posts relevant role
- High-priority keyword with <10 applicants

## Automation Schedule

```bash
# Morning scan
0 8 * * * /jobs job-monitor --board all

# Afternoon check for new postings
0 15 * * * /jobs job-monitor --board linkedin
```

## Board-Specific Notes

### LinkedIn
- Use Sales Navigator if available
- Filter by "Past 24 hours" 
- Check "Remote" filter
- Note mutual connections

### Wellfound
- Filter by "Remote"
- Filter by "Contract"
- Sort by "Most Recent"
- Check company stage/funding

### Toptal
- Requires profile approval
- Higher quality, lower volume
- Check weekly only

## Output

Save found opportunities to:
`session_output/domains/jobs/opportunities/{date}.yaml`

```yaml
opportunities:
  - id: "{unique_id}"
    source: "{board}"
    company: "{name}"
    role: "{title}"
    url: "{link}"
    posted: "{date}"
    keywords: ["{matched}"]
    score: {n}
    status: "found"
    notes: "{any notes}"
```
