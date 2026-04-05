---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: command
command-name: self-improve
tags: [expert-file, command, learning, discord-scraping]
---

# Discord & Scraping Expert - Self-Improve

> Update expertise after signal pipeline runs. This is how Sebastian gets smarter at scraping.

## Purpose

After a workflow execution (successful or failed), analyze the outcome and update expertise.md with new patterns and learnings.

## Allowed Tools
`Read, Edit, Glob, Grep, Bash`

## Workflow

### Step 1: Gather Results
1. Read latest run output from `memory/discord-signals/{today}.json`
2. Read `memory/feed-alerts/{today}.json` for alert activity
3. Read `memory/morning-briefs/{today}.md` if morning brief ran
4. Read current `expertise.md` Part 7 for existing patterns

### Step 2: Analyze Outcome

| Check | Question |
|-------|----------|
| **Signal quality** | Were high-quality signals (score ≥ 7) actually high-quality when Greg reviewed them? |
| **False positives** | Did any signals get flagged that were noise? |
| **False negatives** | Did Greg mention any signals that weren't caught? |
| **Alert volume** | Is Greg getting too many / too few Telegram alerts? |
| **Morning brief** | Was the brief complete? Did any data fail to load? |
| **API limits** | Any Discord or YouTube rate limit issues? |
| **Timing** | Did the 15m scrape run on time? Any missed windows? |

### Step 3: Update expertise.md Part 7

Edit `expertise.md` to add new entries:

#### Patterns That Work
```markdown
- {date}: {pattern} — {why it works}
```
Examples: signal keywords that worked well, alert thresholds that were right

#### Patterns To Avoid
```markdown
- {date}: {pattern} — {what went wrong}
```
Examples: Discord message formats that triggered false positives

#### Known Issues
```markdown
- {date}: {issue} — {workaround if known}
```

#### Tips
```markdown
- {date}: {tip}
```

### Step 4: Update Timestamp
Set `last_updated` in expertise.md frontmatter to today's date.

### Step 5: Adjust Signal Thresholds (if needed)
If signal quality feedback suggests threshold tuning:
1. Note the adjustment needed in expertise.md Part 7 Tips
2. Update the scoring logic in `workspace/skills/discord-scraping/scrape-discord/SKILL.md`
3. Document old vs. new threshold

## Report Format

```markdown
## Self-Improve: Discord & Scraping

### Run Analyzed
- Command: {command_name}
- Date: {date}
- Outcome: {success|partial|failed}

### Expertise Updates
- Part 7 Patterns That Work: +{N} entries
- Part 7 Patterns To Avoid: +{N} entries
- Part 7 Known Issues: +{N} entries
- Part 7 Tips: +{N} entries

### Threshold Adjustments
- {parameter}: {old_value} → {new_value} ({reason})

### Cross-Domain Notes
- portfolio-manager: {any signal quality notes that affect trade context}
```
