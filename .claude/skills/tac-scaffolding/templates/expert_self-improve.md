---
type: expert-file
file-type: command
command-name: "self-improve"
domain: "{{DOMAIN}}"
human_reviewed: false
tags: [expert-file, command, self-improve, {{DOMAIN}}]
---

# {{DOMAIN}} Expert - Self-Improve Mode

> Sync expertise with actual {{DOMAIN}} implementation and recent learnings.

## Purpose

Extract patterns and knowledge from recent {{DOMAIN}} work and update expertise.md to stay current.

## Discovery Process

1. **Scan Recent Work**
   - Check git log for recent {{DOMAIN}}-related commits
   - Review changed files in the {{DOMAIN}} domain
   - Look for new patterns or resolved issues

2. **Extract Learnings**
   - New configuration patterns discovered
   - Bugs encountered and their fixes
   - Performance insights
   - Integration points validated

3. **Update Expertise**
   - Add new patterns to expertise.md
   - Update troubleshooting section with recent issues
   - Revise operations section if workflows changed
   - Add new references

4. **Validate Updates**
   - Ensure expertise.md is internally consistent
   - Verify examples still work
   - Cross-reference with actual code

## Output Format

```
## Self-Improvement Report

**Domain**: {{DOMAIN}}
**Date**: {today}
**Sources Scanned**: {count}

### New Learnings
- {Learning 1}
- {Learning 2}

### Updates Made
- {Section}: {Change description}

### Gaps Identified
- {Gap that needs manual review}
```
