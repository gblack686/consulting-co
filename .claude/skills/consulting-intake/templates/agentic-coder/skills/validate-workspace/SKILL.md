---
name: validate-workspace
description: "Infrastructure: Validate Workspace - Quality-check workspace files, skills, and cross-references"
---

# Validate Workspace

## Purpose

Run the full validation rubric against a workspace. Score every file, every skill, and every cross-reference. Fix what can be fixed automatically, flag what needs human input.

## Variables

- `workspace_path`: Path to the workspace to validate (defaults to current agent's workspace)
- `fix_mode`: `auto` (fix and re-validate) or `report` (report only). Default: `auto`

## Instructions

- IMPORTANT: Never skip the cross-reference checks. A skill that parses correctly but references a missing agent is still broken.
- IMPORTANT: When scanning for hardcoded keys, check patterns: `sk-`, `key_`, `token=`, `Bearer `, `password=`, base64-encoded strings longer than 40 chars.
- Auto-fix is limited to structural issues (missing sections, multiline metadata). Never auto-fix content decisions.
- If a fix makes the score worse, revert it immediately.
- Score normalization: per-skill scores are averaged, then combined with workspace (25) + cross-reference (25) for a /75 base, normalized to /100.

## Relevant Files

- `TOOLS.md` — Full validation rubric with point values
- `memory/patterns.md` — Known common failures and fixes

## Workflow

1. Inventory all workspace files: SOUL.md, USER.md, IDENTITY.md, MEMORY.md, AGENTS.md, TOOLS.md, HEARTBEAT.md
2. List all skills: `openclaw skills list`
3. List all cron jobs: `openclaw cron list`
4. List all agents: `openclaw agents list --bindings`
5. Run **Per-Skill Validation** (25 points each):
   - YAML frontmatter parses (3)
   - metadata single-line JSON (5)
   - Description format correct (2)
   - Steps are actionable (5)
   - Trigger defined (3)
   - Output format specified (3)
   - Error handling present (2)
   - Approval gates for high-blast (2)
6. Run **Per-Workspace Validation** (25 points):
   - SOUL.md has 4 sections (4)
   - USER.md has name + timezone (3)
   - IDENTITY.md has 5 fields (3)
   - AGENTS.md has boundaries (3)
   - TOOLS.md has infrastructure (2)
   - No hardcoded API keys (5)
   - allowFrom populated (3)
   - Cron expressions valid (2)
7. Run **Cross-Reference Validation** (25 points):
   - Timezone consistency (3)
   - Channel consistency (3)
   - Skills referenced exist (4)
   - Tool policies match needs (5)
   - Bindings point to valid agents (5)
   - MEMORY.md private-session only (2)
   - Blast radius matches autonomy (3)
8. Calculate and normalize score to /100
9. If `fix_mode=auto` and score is 70-89: attempt auto-fixes, re-validate
10. Determine action: >= 90 deploy, >= 80 deploy with notes, 70-79 fix and loop, < 70 announce problems

## Report

```
## Workspace Validation Report

**Overall Score**: {score}/100
**Action**: {Excellent|Good|Needs Work|Major Issues}

### Per-Skill Scores
| Skill | Score | Issues |
|-------|-------|--------|
| {name} | {n}/25 | {issues or "None"} |

### Workspace Score: {n}/25
- [x] SOUL.md: 4 sections
- [ ] USER.md: missing timezone
...

### Cross-Reference Score: {n}/25
- [x] Timezone consistent
- [ ] Skill "morning-brief" in cron but not installed
...

### Fixes Applied
{list of auto-fixes, or "None needed"}

### Remaining Issues
{list of issues requiring human input, or "None"}
```
