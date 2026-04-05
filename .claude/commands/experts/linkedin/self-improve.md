---
type: expert-file
parent: "[[linkedin/_index]]"
file-type: command
command-name: "self-improve"
human_reviewed: false
tags: [expert-file, command, self-improve, linkedin]
---

# LinkedIn Expert - Self-Improve Mode

> Validate and update LinkedIn expertise by scanning actual outreach data, prospect files, and campaign results in this codebase.

## Purpose
Scan the current project's LinkedIn automation outputs, prospect data, outreach logs, and browser automation patterns, compare against the expertise mental model, and update the expertise file with any new patterns, results, or lessons learned.

## Usage
```
/experts:linkedin:self-improve
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Edit`

---

## Workflow

### Step 1: Scan Current LinkedIn Assets

```
Glob: .claude/context/linkedin/**/*.json
Glob: .claude/context/linkedin/**/*.md
Glob: .claude/commands/experts/linkedin/*.md
Glob: .claude/skills/**/linkedin*
Glob: .claude/skills/**/inmail*
Glob: .claude/skills/**/prospect*
Glob: .claude/context/**/linkedin*.md
```

### Step 2: Catalog Findings

For each asset found:
- What type of LinkedIn data is it? (prospects, outreach log, session report)
- How many prospects are tracked?
- What outreach channels were used? (InMail, connection, engagement)
- What reply rates are observed?
- Any new workflows or patterns not in expertise.md?

### Step 3: Analyze Campaign Performance

Scan outreach logs for:
- InMail reply rates (target: > 25% for credit refund optimization)
- Connection acceptance rates (target: > 30%)
- Which subject line patterns performed best?
- Which ICP segments had highest engagement?
- Time-of-day / day-of-week performance patterns

### Step 4: Check Browser Automation Patterns

Scan for:
- Any new MCP Chrome DevTools patterns used with LinkedIn
- Updated CSS selectors (LinkedIn changes DOM frequently)
- New detection avoidance techniques discovered
- Pacing adjustments that proved necessary

### Step 5: Compare Against Expertise

| Check | Action |
|-------|--------|
| New workflow discovered | Add to Part 3 |
| Updated pacing rules | Update Part 2 |
| New InMail template that works | Add to Part 5 |
| Updated LinkedIn DOM selectors | Update Part 4 |
| New safety finding | Update Part 7 |
| Campaign performance data | Update Part 9 |
| New ICP insights | Update Part 8 |
| New credit recovery pattern | Update Part 1 |

### Step 6: Update Expertise

Edit `expertise.md` with:
- New workflows or workflow refinements
- Updated pacing rules based on real usage
- New/corrected DOM selectors for LinkedIn pages
- Performance data from actual campaigns
- New InMail templates with measured reply rates
- Updated safety rules from real detection events
- New ICP filters based on conversion data

### Step 7: Report

```markdown
## Self-Improve Report

### Assets Scanned
- {N} prospect files found
- {N} outreach logs found
- {N} session reports found
- {N} engagement logs found
- Total prospects tracked: {N}

### Campaign Performance
| Metric | Value | Target |
|--------|-------|--------|
| InMail reply rate | {X}% | > 25% |
| Connection acceptance rate | {X}% | > 30% |
| Profile view → connection rate | {X}% | > 15% |
| Meeting booking rate | {X}% | > 5% |

### Expertise Updates
- Added: {new workflows, templates, or patterns}
- Updated: {corrected pacing, selectors, or limits}
- Flagged: {issues needing human review}

### Coverage
| Component | In Codebase | In Expertise |
|-----------|------------|--------------|
| Profile research workflow | Yes/No | Yes/No |
| Connection campaign | Yes/No | Yes/No |
| InMail campaign | Yes/No | Yes/No |
| Engagement farming | Yes/No | Yes/No |
| Profile view harvesting | Yes/No | Yes/No |
| Prospect master DB | Yes/No | Yes/No |
| Outreach templates | Yes/No | Yes/No |
| Session reports | Yes/No | Yes/No |

### Top Performing Templates
| Template | Reply Rate | Sample Size |
|----------|-----------|-------------|
| {subject line} | {X}% | {N} |

### Safety Incidents
| Date | Issue | Resolution |
|------|-------|------------|
| {date} | {what happened} | {how it was resolved} |
```
