---
name: domain-discovery
description: "Meta-skill: Scan GitHub repos, discover domain areas, catalog them in Obsidian, and generate reverse prompts for each domain. The agent self-organizes its own knowledge architecture."
---

# Domain Discovery

## Purpose

You are going to explore a set of GitHub repositories that belong to your operator. Based on file structure, recency, README content, and code patterns, you will:

1. **Discover** what domains exist across the repos
2. **Catalog** each domain with goals, status, and key files
3. **Archive** findings into Obsidian as a structured second brain
4. **Generate reverse prompts** — meta-questions that will help you build deeper skills for each domain

This is a self-organizing skill. You decide the domain boundaries. You decide the hierarchy. You ask the operator clarifying questions when you're unsure.

## Trigger

Run when first setting up a new OpenClaw workspace, or periodically to discover new work areas. Invoke with:

```
Hey, I'd like you to scan my GitHub repos and figure out what I'm working on. Come up with a domain map — what are my active projects, what's stale, what connects to what? Then help me set up workflows for each domain.
```

## Process

### Phase 1: Repo Scan

For each GitHub repo the operator gives you access to:

1. **Clone or fetch** the repo (read-only scan — never push)
2. **Analyze structure**:
   - What language/framework? (package.json, Cargo.toml, pyproject.toml, etc.)
   - What's the README say? What problem does it solve?
   - What are the top-level directories? (src/, skills/, agents/, workspace/, etc.)
   - Any OpenClaw workspace files? (SOUL.md, AGENTS.md, openclaw.json)
   - Any Claude Code files? (CLAUDE.md, .claude/)
3. **Check recency**:
   - When was the last commit? Last week = active. Last month = warm. Older = cold.
   - Which files changed most recently? These reveal current focus.
   - Any branches besides main? Active branches = work in progress.
4. **Extract intent**:
   - What is this repo trying to accomplish?
   - Who is the user? (personal project, client work, learning, tool)
   - What APIs/services does it integrate with?

### Phase 2: Domain Classification

Group repos into domains. A domain is a coherent area of work — not just a repo, but a *purpose*.

**Rules for domain boundaries:**
- Multiple repos can belong to one domain (e.g., `hyperliquid-python-sdk` + `openclaw-greg-trading` → "Trading" domain)
- One repo can span multiple domains (e.g., `consulting-co` touches "Consulting", "Infrastructure", "Client Delivery")
- Domains should feel natural — the operator should read them and say "yeah, that's right"
- Aim for 4-8 domains. Fewer = too vague. More = too fragmented.

**For each domain, determine:**

| Field | Description |
|-------|-------------|
| **Name** | Short, clear domain name (e.g., "Trading", "Client Delivery", "Infrastructure") |
| **Description** | One paragraph — what this domain is about, why it matters |
| **Repos** | Which GitHub repos belong here |
| **Key Files** | The 3-5 most important files across all repos in this domain |
| **Status** | Active / Warm / Cold — based on commit recency |
| **APIs & Services** | What external systems are involved |
| **Current Focus** | What's being worked on right now (from recent commits) |
| **Goal** | What is the operator trying to achieve in this domain? (infer from code + context) |
| **Gaps** | What's missing? What would make this domain more complete? |
| **Connections** | How does this domain relate to other domains? |

### Phase 3: Reverse Prompt Generation

For each domain, generate 3-5 **reverse prompts** — meta-questions the operator can ask you to build out deeper capabilities. These follow Alex Finn's pattern:

> "Hey, I'd like to set up an advanced [DOMAIN] workflow based on what we do together. What is a system we can come up with where you are [DOING DOMAIN-SPECIFIC WORK] and then [TRIGGERING FOLLOW-UP ACTIONS]?"

**Examples by domain type:**

**Trading:**
- "Hey, I'd like to set up an advanced trading signal workflow. What system can we build where you monitor Discord channels for alpha, score each signal, and leave briefs in a trading-signals channel — then trigger position analysis in a separate risk channel?"
- "Help me design a daily trading review. Every evening, summarize my positions, P&L, and any signals I missed. What questions should I answer to make this review actually useful?"

**Client Delivery:**
- "I'd like to set up a client onboarding workflow where you scan a new client's APIs, generate a domain map of their business, and propose the first 5 skills to build. What information do you need from me to make this work?"
- "Help me build a session prep system. Before each client call, pull their latest data, open items, and any messages. What's the ideal prep brief look like?"

**Infrastructure:**
- "I'd like you to help me set up a monitoring workflow for my Lightsail instances. What should you check, how often, and what should trigger an alert vs. a daily summary?"

**The key insight from Alex:** Don't just install skills. Have OpenClaw build its own. These reverse prompts are how the operator kicks off that process — they're conversation starters that lead to skill creation.

### Phase 4: Obsidian Archive

Write findings to the Obsidian vault as structured notes.

**Directory structure:**
```
{obsidian_vault}/AI-Agent-KB/domains/
├── _domain-index.md          ← Master index with all domains
├── trading/
│   ├── _overview.md           ← Domain overview (from Phase 2 fields)
│   ├── repos.md               ← Repo inventory with links
│   ├── reverse-prompts.md     ← Generated meta-prompts
│   └── goals.md               ← Current goals + gaps
├── client-delivery/
│   ├── _overview.md
│   ├── repos.md
│   ├── reverse-prompts.md
│   └── goals.md
├── infrastructure/
│   └── ...
└── ...
```

**Frontmatter for _overview.md:**
```yaml
---
domain: Trading
status: active
repos: [hyperliquid-python-sdk, openclaw-greg-trading]
apis: [Hyperliquid, Discord, YouTube]
last_scan: 2026-03-17
tags: [domain, ai-agent-kb, auto-generated]
---
```

**Frontmatter for _domain-index.md:**
```yaml
---
title: Domain Index
type: index
generated_by: domain-discovery
last_scan: 2026-03-17
tags: [domain, index, auto-generated]
---
```

### Phase 5: Self-Improvement Prompts

After cataloging everything, generate a list of "next steps" — things the operator should tell you to do. These are actionable, specific, and ordered by impact:

```markdown
## Recommended Next Steps

### Quick Wins (do today)
1. "Hey, build a skill that [specific action from gap analysis]"
2. "Set up a cron job that [specific recurring task]"

### This Week
3. "Help me connect [Domain A] to [Domain B] by [specific integration]"
4. "Build a daily digest that covers [domains with daily activity]"

### Strategic
5. "Design a multi-agent setup where [agent per domain] and [orchestration pattern]"
```

## Output

Two deliverables:

1. **Console report** — Summary of domains found, status, and top reverse prompts
2. **Obsidian archive** — Full structured notes in the vault

## Notes

- Always ask before writing to Obsidian — confirm the vault path first
- Never expose API keys or secrets found in repos — redact them
- If a repo has an openclaw.json, extract the agent identity and model config
- If a repo has a CLAUDE.md, extract the project conventions
- Re-run periodically — domains shift as work evolves
- This skill should evolve itself: if the operator says "you missed X" or "that's wrong", update the domain map and save the correction as a memory
