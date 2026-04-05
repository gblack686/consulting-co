---
name: review-memory
description: "Infrastructure: Review Memory - Extract patterns from recent memory entries and update persistent knowledge"
---

# Review Memory

## Purpose

Periodically review memory entries, extract recurring patterns, identify failure modes, and update persistent knowledge. This is how the agent fleet gets smarter over time — every build teaches something, and this skill makes sure those lessons stick.

## Variables

- `lookback_days`: Number of days to review. Default: `7`
- `memory_dir`: Path to memory directory. Default: `memory/`

## Instructions

- IMPORTANT: Never delete or modify original memory entries. This skill only reads entries and writes to `patterns.md`.
- If no new entries exist since last review, report "No new entries" and stop. Do not create empty pattern updates.
- Conflicting patterns (e.g., "always use X" vs "never use X") should be flagged, not resolved — keep both with notes and ask for resolution.
- Patterns seen 3+ times are "High Confidence". First occurrence is "Emerging". Not seen in 30+ days is "Deprecated".
- Back up `patterns.md` to `patterns.md.bak` before any write.

## Relevant Files

- `memory/*.md` — Daily build logs (format: `YYYY-MM-DD.md`)
- `memory/patterns.md` — Persistent pattern knowledge (created/updated by this skill)

## Workflow

1. Read all files in `{memory_dir}`
2. Identify entries from the last `{lookback_days}` days
3. If no new entries since last review, report and stop
4. Analyze entries for recurring themes:
   - **Build patterns** — skill structures that scored well, frontmatter that passes first try
   - **Failure patterns** — common validation failures, recurring cross-reference issues
   - **Tool patterns** — most requested integrations, frequently needed env vars
   - **Workflow patterns** — most common types, average phases per skill, approval gate frequency
5. Read existing `memory/patterns.md` (create if missing)
6. Back up current patterns to `memory/patterns.md.bak`
7. Merge new patterns with existing:
   - Reinforce patterns seen multiple times (increase confidence)
   - Add new patterns with "first seen: {date}" marker
   - Move patterns not seen in 30+ days to Deprecated
8. Write updated `memory/patterns.md`
9. Generate recommendations:
   - Workflow type built 3+ times → suggest reusable template
   - Recurring failure → pre-generate fix snippet
   - New domain cluster → suggest adding a domain agent

## Report

```
## Memory Review: {date}

**Entries analyzed**: {n} (last {lookback_days} days)
**Builds**: {n} | **Validations**: {n} | **Issues**: {n}

### Top Patterns
- {pattern_1}: seen {n} times (High Confidence)
- {pattern_2}: seen {n} times (High Confidence)
- {pattern_3}: first seen {date} (Emerging)

### Recurring Issues
- {issue}: {frequency}, suggested fix: {fix}

### Recommendations
- {recommendation_1}
- {recommendation_2}

### Knowledge Base
- patterns.md: {added} new, {reinforced} reinforced, {deprecated} deprecated
```
