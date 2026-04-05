---
name: add-agent
description: "Infrastructure: Add Agent - Create a new domain agent with workspace and bindings"
---

# Add Agent

## Purpose

Create a new domain agent in the OpenClaw fleet with its own workspace, state directory, and session store. One agent, one domain — never overload a single agent with unrelated responsibilities.

## Variables

- `domain`: The domain this agent covers (e.g., content, business, personal, health)
- `agent_id`: Unique kebab-case identifier (e.g., `content-agent`)
- `display_name`: Human-readable name (e.g., `Content Agent`)
- `model`: Model tier — `anthropic/claude-sonnet-4-5` (default) or `anthropic/claude-3-5-haiku` (high-volume)
- `sandbox_mode`: `off` | `non-main` | `all`. Default: `non-main`

## Instructions

- IMPORTANT: Never reuse `agentDir` across agents. This causes auth/session collisions that are extremely hard to debug.
- IMPORTANT: Each agent gets its own workspace directory. No sharing.
- This skill has TWO approval gates — one before creating directories, one before registering in openclaw.json. Both are mandatory.
- Binding priority order: peer > parent peer > guild+roles > guild > team > account > channel > default. Check for conflicts before adding.
- Sub-agents only receive AGENTS.md + TOOLS.md (no SOUL, no IDENTITY). Keep AGENTS.md self-contained.
- Run `openclaw doctor` after registration to catch config issues early.

## Relevant Files

- `TOOLS.md` — Agent configuration schema, binding rules, tool groups
- `openclaw.json` — Current agent fleet configuration
- `SOUL.md` — Main agent's principles (adapt for domain)

## Workflow

1. Identify domain, required tools (allow/deny), and channel/peer bindings
2. Determine model tier and sandbox policy
3. **[APPROVAL GATE]** Announce the agent plan — domain, tools, model, bindings — and wait for confirmation
4. Create directory structure:
   ```bash
   mkdir -p ~/.openclaw/agents/{agent-id}/agent
   mkdir -p ~/.openclaw/agents/{agent-id}/sessions
   mkdir -p ~/.openclaw/workspace-{agent-id}/skills
   mkdir -p ~/.openclaw/workspace-{agent-id}/memory
   ```
5. Generate workspace files in `~/.openclaw/workspace-{agent-id}/`:
   - SOUL.md — domain-adapted principles (Core Truths, Boundaries, Vibe, Continuity)
   - USER.md — domain-relevant client context only
   - IDENTITY.md — domain persona (Name, Creature, Vibe, Emoji, Domain)
   - AGENTS.md — domain-scoped operating instructions with out-of-scope redirect
   - TOOLS.md — only domain-relevant tools and APIs
   - HEARTBEAT.md — domain periodic checks (or empty to skip)
6. **[APPROVAL GATE]** Show the openclaw.json agent entry before registering
7. Add agent to `openclaw.json` agents.list with id, workspace, agentDir, model, tools, sandbox
8. Add binding rules if channel/peer routing is needed
9. Run `openclaw doctor` to validate config
10. Run validate-workspace skill against the new workspace (must score >= 80%)
11. If validation fails, fix issues and re-validate (max 2 loops)

## Report

```
## Agent Added: {display_name}

- **ID**: {agent-id}
- **Domain**: {domain}
- **Model**: {model}
- **Workspace**: ~/.openclaw/workspace-{agent-id}
- **Sandbox**: {mode}
- **Tools**: allow=[{list}], deny=[{list}]
- **Bindings**: {channel/peer rules or "none"}
- **Validation Score**: {score}/100
- **Next Steps**: {install domain skills, add cron jobs, etc.}
```
