# Plan-Build-Review ADW

A three-phase development workflow that replicates the orchestrator's ADW functionality using Claude Code's native Task tool. This runs entirely through the CLI using your Max subscription - no API charges.

## Usage

```
/plan-build-review-adw <task description>
```

## Example

```
/plan-build-review-adw Add a dark mode toggle to the settings page
```

## Workflow Phases

### Phase 1: Plan (Analysis & Design)
- Analyzes the task requirements
- Explores the codebase to understand patterns
- Creates a detailed implementation plan
- Outputs plan to `specs/` directory

### Phase 2: Build (Implementation)
- Implements the solution based on the plan
- Creates/modifies necessary files
- Follows codebase conventions
- Runs verification checks

### Phase 3: Review (Validation)
- Analyzes git diffs
- Validates implementation against plan
- Produces risk-tiered report
- Provides PASS/FAIL verdict

## Instructions

When this skill is invoked with a task description, execute the following three-phase workflow:

### Setup

1. Create a `specs/` directory if it doesn't exist
2. Generate a task keyword from the description (e.g., "dark-mode" from "Add dark mode toggle")
3. Create timestamped filenames for artifacts

### Phase 1: Planning

Use the Task tool with the **Plan** subagent type:

```
Task(
  subagent_type: "Plan",
  prompt: """
  Analyze and create a detailed implementation plan for: {TASK_DESCRIPTION}

  Your plan must include:
  1. **Objective**: Clear statement of what will be built
  2. **Requirements**: List of functional requirements
  3. **Files to Modify/Create**: Specific file paths
  4. **Technical Approach**: Architecture decisions and patterns to use
  5. **Step-by-Step Tasks**: Numbered implementation steps
  6. **Acceptance Criteria**: How to verify success

  Explore the codebase first to understand existing patterns.
  Save your plan to: specs/{task-keyword}-plan.md
  """,
  description: "Planning {task-keyword}"
)
```

**Checkpoint**: Ask user to review the plan before proceeding:
```
AskUserQuestion: "Plan complete. Review specs/{task-keyword}-plan.md. Proceed to build phase?"
```

### Phase 2: Building

Use the Task tool with the **general-purpose** subagent type:

```
Task(
  subagent_type: "general-purpose",
  prompt: """
  Implement the solution based on the plan at: specs/{task-keyword}-plan.md

  Original task: {TASK_DESCRIPTION}

  Instructions:
  1. Read the plan file thoroughly
  2. Implement each step from the plan
  3. Follow existing codebase patterns and conventions
  4. Write production-quality code with proper error handling
  5. Add appropriate comments and documentation
  6. Run any available linters/type checks

  Report what files you created/modified when done.
  """,
  description: "Building {task-keyword}"
)
```

**Checkpoint**: Ask user before review:
```
AskUserQuestion: "Build complete. Files modified: [list]. Proceed to review phase?"
```

### Phase 3: Review

Use the Task tool with the **Explore** subagent type:

```
Task(
  subagent_type: "Explore",
  prompt: """
  Review and validate the implementation for: {TASK_DESCRIPTION}

  Plan location: specs/{task-keyword}-plan.md

  Your review must:
  1. Check git diff to see all changes made
  2. Verify implementation matches the plan
  3. Look for potential bugs or issues
  4. Check for security concerns
  5. Verify code quality and conventions

  Produce a risk-tiered report:
  - **BLOCKERS**: Must fix before merge
  - **HIGH RISK**: Should fix, potential bugs
  - **MEDIUM RISK**: Code quality issues
  - **LOW RISK**: Minor suggestions

  Save report to: specs/{task-keyword}-review.md
  Provide verdict: PASS or FAIL
  """,
  description: "Reviewing {task-keyword}"
)
```

### Final Report

Summarize to the user:
1. **Plan**: Location and key approach
2. **Build**: Files created/modified
3. **Review**: Verdict and issue count by risk tier
4. **Next Steps**: Recommendations based on review

## Output Format

```markdown
## ADW Complete: {task-keyword}

### Phase 1: Plan
- Plan saved to: `specs/{task-keyword}-plan.md`
- Approach: {brief summary}

### Phase 2: Build
- Files modified: {list}
- Key changes: {summary}

### Phase 3: Review
- Verdict: **{PASS/FAIL}**
- Report: `specs/{task-keyword}-review.md`
- Issues: {X blockers, Y high, Z medium, W low}

### Recommendations
{Based on review findings}
```

## Notes

- All three phases run through Claude Code's Task tool
- Uses your Max subscription - no API charges
- Checkpoints allow human-in-the-loop review
- Artifacts saved to `specs/` for inspection
- Can be run from any directory in your codebase
