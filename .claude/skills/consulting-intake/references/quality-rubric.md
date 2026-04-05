# Quality Rubric: Validation Scoring

Score >= 80% to ship. Below 80% loops back to BUILD with specific fixes.

## Per-Expert Structural Checks (25 points)

| Check | Points | Criteria |
|---|---|---|
| _index.md exists | 3 | Has frontmatter (type, name, domain, specialty, status) |
| expertise.md exists | 5 | Has all 7 parts, 200+ lines, last_updated set |
| question.md exists | 3 | Has 6 question categories with resolution strategies |
| plan.md exists | 3 | Has workflow with TAC classification step |
| plan_build_improve.md exists | 4 | Has ACT-LEARN-REUSE flow with gates |
| self-improve.md exists | 3 | Has outcome analysis and expertise update steps |
| Domain-specific commands | 4 | At least 1 domain command with full workflow |

## Per-Skill Validation (25 points)

| Check | Points | Criteria |
|---|---|---|
| YAML frontmatter parses | 3 | `name` and `description` present |
| metadata is single-line JSON | 5 | **CRITICAL** — OpenClaw parser breaks on multiline |
| Description format | 2 | Follows `"{category}: {Name} - {purpose}"` |
| Steps are actionable | 5 | No placeholders like "do the thing" — actual API calls |
| Trigger defined | 3 | cron expression, heartbeat, webhook, or on-demand |
| Output format specified | 3 | What the result looks like, where it goes |
| Error handling section | 2 | What to do when steps fail |
| Approval gates match AGENTS.md | 2 | High-blast tasks have gates, low-blast are autonomous |

## OpenClaw Config Checks (25 points)

| Check | Points | Criteria |
|---|---|---|
| SOUL.md has 4 sections | 4 | Core Truths, Boundaries, Vibe, Continuity |
| USER.md has required fields | 3 | Name, timezone, at minimum |
| IDENTITY.md has 5 fields | 3 | Name, Creature, Vibe, Emoji, Avatar |
| MEMORY.md has mission | 3 | Mission statement present and coherent |
| AGENTS.md has boundaries | 3 | Safe-autonomously and requires-asking sections |
| TOOLS.md has infrastructure | 2 | At least device type and primary tools listed |
| openclaw.json has model config | 3 | agent.model set to valid provider/model |
| openclaw.json has channel allowFrom | 2 | Not empty (empty = anyone can message) |
| Cron expressions valid | 2 | All cron expressions pass syntax validation |

## Cross-Reference & Security (25 points)

| Check | Points | Criteria |
|---|---|---|
| Timezone consistency | 3 | USER.md timezone matches cron --tz flags |
| Channel consistency | 3 | Delivery channels in skills match openclaw.json config |
| _index.md lists all commands | 3 | Every .md file in expert dir is listed |
| expertise.md covers all workflows | 4 | Each skill has corresponding expertise section |
| No hardcoded API keys | 5 | Skills reference env vars, not literal keys |
| allowFrom populated | 3 | Restricts to client's phone number(s) |
| MEMORY.md not in group context | 2 | AGENTS.md specifies MEMORY.md is private-session only |
| Blast radius matches autonomy | 2 | High-blast skills have approval gates |

## Scoring

```
Total: ___ / 100

>= 90: Excellent — ready to deploy
>= 80: Good — deploy with minor notes
>= 70: Needs work — loop back to BUILD for specific fixes
<  70: Major issues — review plan, may need client clarification
```

## Fix Priority

When looping back to BUILD:
1. **CRITICAL** (blocks deployment): Single-line metadata JSON, missing allowFrom, hardcoded keys
2. **HIGH** (degrades experience): Missing expertise sections, placeholder steps, wrong timezone
3. **MEDIUM** (polish): Missing error handling, incomplete _index listing
4. **LOW** (nice-to-have): Missing avatar, empty Part 7 learnings (expected for new experts)
