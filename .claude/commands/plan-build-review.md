---
name: plan-build-review
description: Three-phase ADW workflow - plan, build, then review. Runs entirely via CLI using Max subscription.
argument-hint: <task description>
---

# Plan-Build-Review Workflow

Execute a three-phase development workflow for: $ARGUMENTS

## Phase 1: Plan

Use the Task tool to create a plan:

```
Task(
  subagent_type: "Plan",
  prompt: "Create a detailed implementation plan for: $ARGUMENTS

  Include:
  - Objective and requirements
  - Files to create/modify
  - Technical approach
  - Step-by-step tasks
  - Acceptance criteria

  Explore the codebase first. Save plan to specs/ directory.",
  description: "Planning implementation"
)
```

Report the plan location and key approach to the user.

## Phase 2: Build

Use the Task tool to implement:

```
Task(
  subagent_type: "general-purpose",
  prompt: "Implement the solution based on the plan you just created.

  Original task: $ARGUMENTS

  - Read the plan file
  - Implement each step
  - Follow codebase patterns
  - Write production-quality code
  - Run linters/type checks if available

  Report files created/modified.",
  description: "Building implementation"
)
```

Report the files modified to the user.

## Phase 3: Review

Use the Task tool to validate:

```
Task(
  subagent_type: "Explore",
  prompt: "Review the implementation for: $ARGUMENTS

  - Check git diff for all changes
  - Verify implementation matches plan
  - Look for bugs/issues
  - Check code quality

  Produce risk-tiered report (Blockers/High/Medium/Low).
  Save to specs/ directory.
  Verdict: PASS or FAIL",
  description: "Reviewing implementation"
)
```

## Final Summary

Report to user:
1. Plan location and approach
2. Files created/modified
3. Review verdict and issues by risk tier
4. Recommendations
