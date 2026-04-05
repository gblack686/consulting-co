---
type: expert-file
file-type: command
command-name: "plan_build_improve"
domain: "{{DOMAIN}}"
human_reviewed: false
tags: [expert-file, command, workflow, {{DOMAIN}}]
---

# {{DOMAIN}} Expert - Plan, Build, Improve

> Full end-to-end workflow: plan the work, build it, then capture learnings.

## Purpose

Execute a complete {{DOMAIN}} task from planning through implementation to knowledge capture.

## Workflow

### Phase 1: Plan
Run `/experts:{{DOMAIN}}:plan` to generate an implementation plan.

- Analyze requirements
- Select approach
- Break down into steps
- Get user approval before proceeding

### Phase 2: Build
Implement the approved plan.

- Follow the step order from the plan
- Validate each step before moving to the next
- If blocked, adjust the plan and re-confirm with user

### Phase 3: Improve
Run `/experts:{{DOMAIN}}:self-improve` to capture learnings.

- Extract patterns from what was built
- Update expertise.md with new knowledge
- Document any issues encountered

## Success Criteria

- [ ] Plan approved by user
- [ ] All plan steps completed
- [ ] Validation checks pass
- [ ] Expertise updated with learnings
