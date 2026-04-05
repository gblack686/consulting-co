---
name: build-skill
description: "Infrastructure: Build Skill - Create a new OpenClaw SKILL.md from a workflow description"
---

# Build Skill

## Purpose

Create a validated OpenClaw SKILL.md file from a workflow description. One skill, one purpose — never combine multiple workflows into a single skill.

## Variables

- `workflow_description`: What the user wants automated
- `domain`: Which domain this skill belongs to
- `agent_id`: Target agent to install the skill for

## Instructions

- IMPORTANT: `metadata` field MUST be single-line JSON. The parser breaks on multiline. This is the #1 deployment-breaking issue.
- IMPORTANT: One skill, one purpose. If the request combines multiple workflows (e.g., "research AND write newsletter"), split into separate skills.
- Description format MUST follow: `"{Category}: {Name} - {purpose}"`
- Never hardcode API keys in the skill body. Use `metadata.openclaw.requires.env` for gating.
- Approval gates (`**[APPROVAL GATE]**`) are required for any action that sends external messages, deletes data, or modifies config.
- If a similar skill already exists, confirm before overwriting.

## Relevant Files

- `TOOLS.md` — SKILL.md format spec and frontmatter rules
- `memory/patterns.md` — Previously successful skill patterns

## Workflow

1. Classify the workflow type:
   - Scheduled output → template with cron trigger
   - Research/discovery → browser + search tools
   - Sync/integration → API calls + data transform
   - Content production → multi-phase with approval gate
   - Analytics/reporting → data gather + format + deliver
2. Determine required tools, env vars, and config keys
3. Check for existing similar skill: `openclaw skills list`
4. Generate YAML frontmatter:
   - `name`: kebab-case (e.g., `write-newsletter`)
   - `description`: `"{Category}: {Name} - {purpose}"`
   - `metadata`: single-line JSON only
5. Write skill body using TAC structure:
   - `## Purpose` — one sentence
   - `## Variables` — if the skill takes inputs
   - `## Instructions` — guardrails and IMPORTANT rules
   - `## Workflow` — numbered steps in phases
   - `## Report` — output format
6. Save to: `~/.openclaw/workspace-{agent_id}/skills/{skill-name}/SKILL.md`
7. Validate against per-skill rubric (25 points):
   - YAML parses (3), metadata single-line (5), description format (2)
   - Actionable steps (5), trigger defined (3), output format (3)
   - Error handling (2), approval gates for high-blast (2)
8. If score >= 20/25: install the skill
9. If score < 20: fix issues and re-validate (max 2 loops)
10. Verify with `openclaw skills list` that the skill loaded

## Report

```
## Build Complete: {skill-name}

- **Score**: {score}/25
- **Location**: {path}
- **Category**: {category}
- **Tools**: {tool_list}
- **Requirements**: {env_vars, bins, config}
- **Issues**: {none | list of issues}
```
