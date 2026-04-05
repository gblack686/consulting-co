# META-2: GitHub SDLC Skill — Build Plan
**Date:** 2026-03-18
**Build location:** `.claude/skills/consulting-intake/templates/skills/github-sdlc/`

---

## What to Build

Standardized software delivery conventions + a GitHub Actions CI pipeline for every client workspace. Ships via consulting-intake pipeline at Step 5a (GitHub repo setup).

---

## Files to Create

```
templates/skills/github-sdlc/
└── SKILL.md
references/sdlc-conventions.md
templates/github/
├── workflows/validate-intake.yml
└── pull_request_template.md
```

---

## SKILL.md Spec

**What this skill does when invoked:**
1. Creates `.github/workflows/validate-intake.yml` in the client repo
2. Creates `.github/pull_request_template.md`
3. Creates `CONTRIBUTING.md` with commit + branch conventions
4. Optionally creates initial Linear issue linking config

**Commit conventions (Conventional Commits):**
```
type(scope): description

Types: feat, fix, refactor, docs, test, chore, skill, agent
Scope: domain name (e.g. feat(discord-scraping): add signal quality scorer)
```

**Branch conventions:**
- `main` — stable, deployed
- `update/YYYYMMDD-{description}` — client updates
- `skill/{skill-name}` — new skill development
- `fix/{issue-slug}` — bug fixes

**PR format:**
```
Title: [{client}] {type}: {description}
Body: Summary | Test Plan | Checklist
Labels: skill | client-workspace | meta | bug | enhancement
```

---

## validate-intake.yml Spec

Trigger: `on: [pull_request]`

Jobs:
1. **validate-skill-frontmatter** — check all `SKILL.md` files have required frontmatter fields
2. **check-template-placeholders** — grep for `{placeholder}` patterns not filled in workspace files
3. **lint-openclaw-json** — validate `openclaw.json` is valid JSON with required keys
4. **check-no-secrets** — fail if any file contains potential secret patterns (API keys, tokens)

---

## pull_request_template.md Spec

```markdown
## Summary
-

## Type
- [ ] New skill
- [ ] Client workspace update
- [ ] Bug fix
- [ ] Meta skill

## Test Plan
- [ ] Tested against greg-trading or michael-fisch session
- [ ] No template placeholders remaining
- [ ] openclaw.json valid JSON

## Linear Issue
Refs AI-
```

---

## references/sdlc-conventions.md Spec

Document:
- Full commit convention guide with examples
- Branch naming guide with examples
- PR review process (Greg auto-assigned)
- Release tagging: `v{YYYYMMDD}` on merge to main
- How workflow catalog items map to Linear issues
- How to run `validate-intake.yml` locally

---

## Acceptance Criteria

- [ ] SKILL.md passes `skill-format-spec.md` validation
- [ ] `validate-intake.yml` passes GitHub Actions syntax check
- [ ] Frontmatter validator catches missing fields
- [ ] Placeholder checker catches unfilled `{variables}`
- [ ] `references/sdlc-conventions.md` has full examples
- [ ] Referenced in `SKILL.md` pipeline table (Step 5a)

---

## Prompt for OpenClaw

> "Build the GitHub SDLC skill from the spec at `specs/meta2-github-sdlc-plan.md`. Create `templates/skills/github-sdlc/SKILL.md`, `references/sdlc-conventions.md`, `templates/github/workflows/validate-intake.yml`, and `templates/github/pull_request_template.md`. The GitHub Actions workflow should validate SKILL.md frontmatter, check for unfilled template placeholders, and validate openclaw.json structure."
