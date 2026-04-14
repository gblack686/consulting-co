---
name: TAC Repository Index
description: Master index for Tactical Agentic Coding patterns, agents, commands, and skills
version: 2.0
organization: gblack686-openclaw
maintained_by: forge+sebastian
updated: 2026-04-08
---

# TAC Repository — Consulting-Co

## Structure

| Directory | Count | Purpose |
|-----------|-------|---------|
| `.claude/agents/` | 33+ | Single-responsibility agent definitions |
| `.claude/commands/` | 100+ | Command templates (PRP pattern) |
| `.claude/skills/` | 15+ | Skill definitions with SKILL.md |
| `specs/core-guides/` | 10+ | TAC methodology documentation |
| `tac-learning-system/` | 50+ files | Elite context engineering curriculum |

## Agent Format (Frontmatter)

```yaml
---
name: agent-name
model: provider/model-id
expertise:
  - path: relative/path/to/yaml
    use-when: "description of when to activate"
    updatable: true
    max-lines: 10000
skills:
  - path: skills/skill-name.md
    use-when: "when to use"
tools:
  - read
  - write
  - edit
  - bash
domain:
  - path: some/path
    read: true
    upsert: true
    delete: false
---
```

## Command Format (PRP)

Every command domain has three files:
- `question.md` — Gather requirements, clarify scope
- `plan.md` — Architecture and implementation plan
- `self-improve.md` — Post-completion review and improvements

## Prompting Patterns

### Pattern: Context Loading
```markdown
## Context
<relevant files, decisions, constraints>

## Task
<specific deliverable>

## Constraints
- Follow existing patterns in <reference files>
- Use <specific library/framework>
```

### Pattern: Agent Composer
```markdown
You are <agent-name>. Your job: <single responsibility>.

## Variables
- $PROJECT_ROOT: <path>
- $OUTPUT_DIR: <path>

## Rules
1. Read before writing
2. Validate before committing
3. Follow TAC patterns
```

### Pattern: Expert Command
```markdown
## Question Phase
What are we building? → question.md

## Plan Phase
How will we build it? → plan.md

## Validation Phase
Did we build it right? → self-improve.md
```

## Key Agents by Domain

### Infrastructure
- `aws-org-expert-agent.md` — AWS organization management
- `github-actions-agent.md` — CI/CD pipelines
- `build-agent.md` — Build and deploy

### Research & Analysis
- `graphiti-agent.md` — Knowledge graph
- `ai-codebase-optimizer.md` — Code analysis

### Client Work
- `browser-agent.md` / `bowser-agent.md` — Browser automation
- `github-issue-agent.md` — Issue management
- `google-workspace-agent.md` — Gmail/Calendar/Drive

## Quick Search

```bash
# Find agents for a domain
grep -rl "keyword" .claude/agents/

# Find commands for a task
grep -rl "keyword" .claude/commands/

# Find skills
grep -rl "keyword" .claude/skills/

# Search TAC curriculum
grep -rl "keyword" tac-learning-system/
```
