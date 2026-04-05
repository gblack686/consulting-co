---
type: expert-file
parent: "[[portfolio-manager/_index]]"
file-type: command
command-name: plan_build_improve
model: sonnet
tags: [expert-file, command, workflow, portfolio-manager]
---

# Portfolio Manager Expert - Plan Build Improve

> Full ACT-LEARN-REUSE workflow for portfolio management changes.

## Purpose

Execute the complete plan-build-improve cycle for a portfolio management change.

## Allowed Tools
`Task, TaskOutput, Read, Write, Edit, Glob, Grep, Bash`

## Critical Constraint

This domain monitors financial positions. All changes must be tested on **paper trading testnet** before applying to mainnet. Never test risk rule changes directly on live positions.

## Workflow

```
ACT → LEARN → REUSE

Step 1: Plan (ACT)  — Create TAC-informed implementation plan
Step 2: Build (ACT) — Execute the implementation
Step 3: Self-Improve (LEARN) — Update expertise with new patterns
```

### Phase 1: PLAN (ACT)

1. Load `expertise.md` for current portfolio manager state
2. Analyze request against existing workflows
3. Assess blast radius: does this affect live position monitoring? live alerts?
4. Classify by TAC pattern
5. If research needed: dispatch browser agent for Hyper Liquid API docs
6. Write plan to `specs/portfolio-manager-{feature}.md`
7. **[CHECKPOINT]**: For any change that affects alert logic — review plan carefully before building

### Phase 2: BUILD (ACT)

1. Create or modify SKILL.md files as planned
   - metadata single-line JSON
   - never hardcode wallet addresses or API keys
   - always include "[APPROVAL GATE]" on any trade-adjacent recommendation
2. Update risk thresholds in SKILL.md if changed
3. Validate cron expressions and timezone settings
4. Test on paper trading testnet:
   - Use `https://api.hyperliquid-testnet.xyz` endpoints
   - Verify alert logic with test positions
5. After testnet validation: apply to mainnet config

### Phase 3: SELF-IMPROVE (LEARN)

After successful build:

1. Read results and outcomes
2. Update `expertise.md` Part 7 with new risk patterns and learnings
3. Update `last_updated` timestamp
4. Document which risk thresholds are most effective

### Quality Gate

Before marking complete:
- [ ] All planned files created/modified
- [ ] No hardcoded API keys or wallet addresses
- [ ] Risk thresholds documented in expertise.md Part 2
- [ ] "[APPROVAL GATE]" present on all recommendation outputs
- [ ] Tested on testnet before mainnet
- [ ] expertise.md still has all 7 parts

## Report Format

```markdown
## Portfolio Manager PBI Complete

### Changes Made
- {file}: {what changed}

### Risk Thresholds Applied
- {threshold_name}: {value}

### Testnet Validation
- Result: {pass|fail}
- Notes: {observations}

### Expertise Updated
- Part {N}: {what was added}

### Score: {score}/100
```
