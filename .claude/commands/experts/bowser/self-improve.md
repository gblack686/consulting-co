---
type: expert-file
parent: "[[bowser/_index]]"
file-type: command
command-name: "self-improve"
human_reviewed: false
tags: [expert-file, command, self-improve, bowser]
---

# Bowser Expert - Self-Improve Mode

> Validate and update bowser expertise by scanning actual browser automation implementations in this codebase.

## Purpose
Scan the current project's browser automation commands, skills, and justfile recipes, compare against the expertise mental model, and update the expertise file with any new patterns, configurations, or lessons learned.

## Usage
```
/experts:bowser:self-improve
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Edit`

---

## Workflow

### Step 1: Scan Current Browser Automation Assets

```
Glob: .claude/commands/bowser/*.md
Glob: .claude/skills/browser-automation/**/*
Glob: .claude/skills/youtube-transcript*.md
Glob: .claude/skills/youtube-video-archiver/**/*
Glob: ai_review/user_stories/*.yaml
Glob: .claude/context/tac-scan/*_metadata.json
```

### Step 2: Catalog Findings

For each asset found:
- Which backend does it use? (claude-bowser, playwright-bowser, Apify, API)
- Which command invokes it?
- Any new workflows not in expertise.md?
- Any new quirks or workarounds discovered?

### Step 3: Check Extracted Videos

Scan `.claude/context/tac-scan/` for metadata files:
- How many videos have been extracted?
- Which extraction method was used (browser vs Apify)?
- Any missing transcripts or descriptions?
- Any resource links that weren't followed?

### Step 4: Compare Against Expertise

| Check | Action |
|-------|--------|
| New bowser command found | Add to Part 2 |
| New browser quirk discovered | Add to Part 4 |
| New extraction pattern | Add to Part 3 |
| New agent type used | Add to Part 9 |
| Updated justfile recipe | Update Part 5 |
| New QA story format | Update Part 6 |
| Best practice violation | Flag for review |

### Step 5: Update Expertise

Edit `expertise.md` with:
- New commands or workflows discovered
- Updated backend capabilities
- Corrected quirk workarounds
- New extracted video entries in Part 8
- Updated best practices from real usage

### Step 6: Report

```markdown
## Self-Improve Report

### Assets Scanned
- {N} bowser commands found
- {N} skills found
- {N} justfile recipes found
- {N} user story YAML files found
- {N} extracted videos in tac-scan

### Expertise Updates
- Added: {new commands, quirks, or patterns}
- Updated: {corrected information}
- Flagged: {issues needing human review}

### Coverage
| Component | In Codebase | In Expertise |
|-----------|------------|--------------|
| youtube-transcript | Yes/No | Yes/No |
| ui-review | Yes/No | Yes/No |
| hop-automate | Yes/No | Yes/No |
| amazon-add-to-cart | Yes/No | Yes/No |
| blog-summarizer | Yes/No | Yes/No |
| Apify skill | Yes/No | Yes/No |
| Justfile recipes | Yes/No | Yes/No |

### Extracted Videos
| Video ID | Transcript | Description | Metadata | Resource Links |
|----------|-----------|-------------|----------|----------------|
| {id} | Yes/No | Yes/No | Yes/No | {count} |
```
