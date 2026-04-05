---
type: expert-file
file-type: command
command-name: "plan"
domain: "{{DOMAIN}}"
human_reviewed: false
tags: [expert-file, command, planning, {{DOMAIN}}]
---

# {{DOMAIN}} Expert - Plan Mode

> Create implementation plans for {{DOMAIN}} work.

## Purpose

Generate detailed, actionable plans for {{DOMAIN}} tasks before implementation.

## Planning Framework

### Step 1: Requirements Analysis
- What is the goal?
- What constraints exist?
- What dependencies are involved?

### Step 2: Architecture Decision
- What approach fits best?
- What are the trade-offs?
- What's the simplest path?

### Step 3: Implementation Breakdown
- What files need to change?
- What's the order of operations?
- What are the validation steps?

## Plan Output Format

```markdown
# {{DOMAIN}} Implementation Plan

## Goal
{One-sentence objective}

## Approach
{Selected approach and rationale}

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| path | create/edit | why |

## Steps

1. {Step with acceptance criteria}
2. {Step with acceptance criteria}
3. {Step with acceptance criteria}

## Validation
- [ ] Check 1
- [ ] Check 2

## Risks
- {Risk and mitigation}
```

## Examples

### Example: Simple Task
User: "Add a new endpoint to {{DOMAIN}}"
Plan: Single-file change, 3 steps, 2 validation checks.

### Example: Complex Task
User: "Refactor {{DOMAIN}} architecture"
Plan: Multi-file change, phased approach, rollback strategy.
