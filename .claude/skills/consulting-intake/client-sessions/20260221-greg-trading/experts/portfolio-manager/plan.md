---
type: expert-file
parent: "[[portfolio-manager/_index]]"
file-type: command
command-name: plan
tags: [expert-file, command, planning]
---

# Portfolio Manager Expert - Plan Mode

> Create TAC-informed implementation plans for portfolio management changes.

## Purpose

Analyze a requested change or addition to portfolio monitoring workflows and produce an implementation plan.

## Allowed Tools
`Read, Write, Glob, Grep, Bash`

## Workflow

### Step 1: Load Context
1. Read `expertise.md` for current portfolio manager state
2. Read `_index.md` for available commands and tools
3. Read relevant `MEMORY.md` entries for past risk configuration decisions

### Step 2: Analyze Request
1. What is being asked? (new alert? new risk rule? new journal metric?)
2. Which existing workflows are affected?
3. Does this touch live trading? (highest blast radius — be careful)
4. Are there dependencies on other domains?

### Step 3: Classify by TAC Pattern

| If the request involves... | Use TAC Pattern |
|---------------------------|-----------------|
| A new recurring risk check | TAC-6: One Agent One Purpose |
| Risk data sync to another tool | TAC-5: Feedback Loops |
| Weekly performance report format | TAC-3: Template Engineering |
| Approval-gated risk action | TAC-5 + TAC-12: Orchestration |
| Learning from trade outcomes | TAC-10: Self-Improving Prompts |

### Step 4: Research (if needed)
- **Hyper Liquid API research**:
  ```
  Task(subagent_type: "playwright-bowser-agent",
       prompt: "Research Hyper Liquid API for {specific endpoint}. Find: request format, response schema, auth requirements.")
  ```

### Step 5: Output Plan
Write to `specs/portfolio-manager-{feature}.md`:

```markdown
# Plan: {feature_name}

## TAC Pattern: {pattern_name}
## Affected Files: {file_list}
## New Files Needed: {new_file_list}

## Implementation Steps
1. {step}
2. {step}

## Validation Criteria
- Alert fires correctly on test position
- No false positives on healthy positions
- No trade execution side effects

## Blast Radius: {low|medium|high}
## Estimated Complexity: {low|medium|high}
```

**Note**: Always assess blast radius for portfolio manager changes — this domain touches financial data.
