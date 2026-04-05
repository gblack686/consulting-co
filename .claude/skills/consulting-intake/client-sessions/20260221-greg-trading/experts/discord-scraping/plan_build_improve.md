---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: command
command-name: plan_build_improve
model: sonnet
tags: [expert-file, command, workflow, discord-scraping]
---

# Discord & Scraping Expert - Plan Build Improve

> Full ACT-LEARN-REUSE workflow for Discord scraping and signal pipeline changes.

## Purpose

Execute the complete plan-build-improve cycle for a Discord scraping change or addition.

## Allowed Tools
`Task, TaskOutput, Read, Write, Edit, Glob, Grep, Bash`

## Workflow

```
ACT → LEARN → REUSE

Step 1: Plan (ACT)  — Create TAC-informed implementation plan
Step 2: Build (ACT) — Execute the implementation
Step 3: Self-Improve (LEARN) — Update expertise with new patterns
```

## Flow Control

```
Receive Request
    │
    ▼
  PLAN ──────► Plan Approved?
    ▲               │
    │ No             │ Yes
    └────────────────┘
                     │
                     ▼
                   BUILD ──────► Successful?
                     ▲               │
                     │ No → Fix      │ Yes
                     └───────────────┘
                                     │
                                     ▼
                              Human-in-the-Loop?
                                     │
                              Yes    │    No
                              ▼      │    │
                           Review    │    │
                              │      │    │
                        Approved?    │    │
                              │      │    │
                         Yes  ▼      ▼    ▼
                        Self-Improve
                              │
                              ▼
                            Done
```

### Phase 1: PLAN (ACT)

1. Load `expertise.md` for current Discord scraping state
2. Analyze request against existing workflows (scrape-discord, monitor-feeds, morning-brief)
3. Classify by TAC pattern (see plan.md Step 3)
4. If research needed:
   - Dispatch browser agent for Discord/YouTube API docs
   - Dispatch YouTube agent for integration tutorials
5. Write implementation plan to `specs/discord-scraping-{feature}.md`
6. **[CHECKPOINT]**: Review plan before proceeding — especially for new channels or data sources

### Phase 2: BUILD (ACT)

Execute the plan:

1. Create or modify SKILL.md files as specified
   - metadata must be single-line JSON
   - description format: `"Trading: {Name} - {purpose}"`
   - verify `DISCORD_BOT_TOKEN` env var referenced correctly
2. Update `memory/feed-rules.json` if new alert rules are added
3. For new cron jobs: validate cron syntax, confirm America/Los_Angeles timezone
4. For morning brief changes: preserve all 7 sections, only edit affected parts
5. Test where possible:
   - Validate frontmatter YAML parses
   - Test signal parser with sample Discord message text
   - Verify Telegram delivery in test environment

### Phase 3: SELF-IMPROVE (LEARN)

After successful build:

1. Read results of what was built
2. Compare actual vs. planned implementation
3. Update `expertise.md` Part 7 with new patterns and findings
4. Update `last_updated` timestamp on expertise.md
5. If API research was done: update Part 4 with real endpoint findings

### Quality Gate

Before marking complete:
- [ ] All planned files created/modified
- [ ] SKILL.md frontmatter valid (metadata single-line JSON)
- [ ] expertise.md still has all 7 parts
- [ ] _index.md updated with new commands/skills
- [ ] No hardcoded API keys (use env vars: DISCORD_BOT_TOKEN, TELEGRAM_BOT_TOKEN)
- [ ] Signal scoring thresholds documented in expertise.md

## Report Format

```markdown
## Discord & Scraping PBI Complete

### Changes Made
- {file}: {what changed}

### New Files
- {file}: {purpose}

### Expertise Updated
- Part {N}: {what was added}

### Patterns Learned
- {pattern}

### Score: {score}/100
```
