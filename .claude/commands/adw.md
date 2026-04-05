---
name: adw
description: Background ADW - kicks off autonomous Plan→Build→Review workflow. Check status with /adw-status.
argument-hint: <task description>
---

# Background ADW Workflow

Launch a background autonomous development workflow for: $ARGUMENTS

## Execution

Use the Task tool with `run_in_background: true` to launch the complete ADW:

```
Task(
  subagent_type: "general-purpose",
  run_in_background: true,
  prompt: """
  Execute a complete Plan→Build→Review ADW for: $ARGUMENTS

  You are an autonomous development workflow agent. Complete ALL THREE phases without stopping:

  ## Phase 1: Plan
  1. Explore the codebase to understand patterns
  2. Create a detailed implementation plan with:
     - Objective and requirements
     - Files to create/modify
     - Technical approach
     - Step-by-step tasks
     - Acceptance criteria
  3. Save plan to specs/{task-keyword}-plan.md

  ## Phase 2: Build
  1. Read your plan file
  2. Implement each step
  3. Follow codebase patterns
  4. Write production-quality code
  5. Run linters/type checks if available

  ## Phase 3: Review
  1. Check git diff for all changes
  2. Verify implementation matches plan
  3. Look for bugs/issues
  4. Check code quality
  5. Save review to specs/{task-keyword}-review.md with:
     - BLOCKERS / HIGH / MEDIUM / LOW risk tiers
     - Verdict: PASS or FAIL

  ## Final Output
  End with a summary:
  - Plan location
  - Files modified
  - Review verdict
  - Any blockers or recommendations
  """,
  description: "ADW: {brief task keyword}"
)
```

## Response to User

After launching, immediately respond:

```
ADW launched in background.

Task: $ARGUMENTS
Output file: [path from Task result]

Commands:
- Check status: Read the output file path above
- View specs: ls specs/

The workflow will complete autonomously through Plan→Build→Review phases.
```

Do NOT wait for the task to complete. Return immediately after launching.
