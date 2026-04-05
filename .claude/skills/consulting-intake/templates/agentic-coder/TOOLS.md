# Agentic Coder — Tools Reference

This file contains the specifications you need to build correctly. Skills define HOW to do things. This file defines the FORMATS and RULES.

## Device

- **Type**: {device_type}
- **OS**: {device_os}
- **OpenClaw Version**: {openclaw_version}
- **Gateway Port**: 18789

---

## OpenClaw CLI Reference

### Agent Management
```bash
openclaw agents add <name>           # Create new agent
openclaw agents list --bindings      # List agents with routing rules
openclaw agents list                 # List all agents
```

### Skill Management
```bash
openclaw skills list                 # List loaded skills
openclaw skills install <name>       # Install from ClawHub
clawhub install <skill-slug>         # Install from registry
```

### Cron Management
```bash
# One-shot (runs once)
openclaw cron add --name "Task name" \
  --at "2026-03-01T09:00:00" --tz "{client_timezone}" \
  --skill "skill-name" --mode main --delivery announce

# Interval (repeating)
openclaw cron add --name "Task name" \
  --every "30m" \
  --skill "skill-name" --mode isolated --delivery none

# Cron expression
openclaw cron add --name "Task name" \
  --cron "0 7 * * *" --tz "{client_timezone}" \
  --skill "skill-name" --mode main --delivery announce

openclaw cron list                   # List all cron jobs
openclaw cron remove --name "name"   # Remove a cron job
```

### Schedule Types
| Type | Flag | Example |
|------|------|---------|
| One-shot | `--at` | `"2026-03-01T09:00:00"` |
| Interval | `--every` | `"30m"`, `"2h"`, `"1d"` |
| Cron | `--cron` | `"0 7 * * *"` (7am daily) |

### Execution Modes
| Mode | Behavior |
|------|----------|
| `main` | Runs in user's main session (has memory context) |
| `isolated` | Fresh session (no memory bleed) |

### Delivery Modes
| Mode | Behavior |
|------|----------|
| `announce` | Sends result to configured channel |
| `webhook` | POSTs result to a URL |
| `none` | Silent (logs only) |

### Diagnostics
```bash
openclaw doctor                      # Validate config
openclaw doctor --fix                # Auto-repair
openclaw health                      # Health check
openclaw gateway restart             # Restart gateway
```

---

## SKILL.md Format Spec

### Required Structure
```markdown
---
name: skill-name
description: "{Category}: {Skill Name} - {one-line purpose}"
---

# Skill Title

Instructions for the agent.
```

### Frontmatter Fields
| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | Yes | string | Kebab-case (e.g., `write-newsletter`) |
| `description` | Yes | string | Format: `"{Category}: {Name} - {purpose}"` |
| `user-invocable` | No | boolean | Expose as `/skill-name` command |
| `disable-model-invocation` | No | boolean | Prevent auto-invocation |
| `metadata` | No | JSON | **MUST BE SINGLE-LINE** |

### CRITICAL: metadata Format
```yaml
# CORRECT — single line
metadata: {"openclaw": {"requires": {"env": ["API_KEY"]}}}

# WRONG — breaks the parser
metadata:
  openclaw:
    requires:
      env:
        - API_KEY
```

### metadata.openclaw.requires (Gating)
| Key | Purpose | Example |
|-----|---------|---------|
| `bins` | Required CLI tools | `["ffmpeg", "yt-dlp"]` |
| `env` | Required env vars | `["CONVERTKIT_API_KEY"]` |
| `config` | Required config keys | `["channels.telegram"]` |
| `os` | Required OS | `["linux", "darwin"]` |

### Skill Body Best Practices
1. Start with purpose (one sentence)
2. List allowed tools
3. Phased workflow (numbered steps in phases)
4. Mark approval gates with `**[APPROVAL GATE]**`
5. Specify output format
6. Include error handling section
7. Specify delivery (where output goes)

### Token Impact
~24 tokens per loaded skill. Keep skill count reasonable.

### Skill Locations (Precedence)
1. `<workspace>/skills/` — per-agent (highest)
2. `~/.openclaw/skills/` — shared across agents
3. Bundled skills — shipped with OpenClaw (lowest)

---

## Workspace File Formats

### SOUL.md (4 sections required)
1. **Core Truths** — foundational principles (3-5 items)
2. **Boundaries** — limits on behavior (3-5 items)
3. **Vibe** — communication style, tone, personality
4. **Continuity** — reminder to review/update these files

### USER.md
- Name, nickname, pronouns, timezone
- Context section: projects, interests, preferences

### IDENTITY.md
- Name, Creature, Vibe, Emoji, Avatar

### AGENTS.md (required sections)
1. **Identity & Context Loading** — what to read on session start
2. **Memory Architecture** — daily logs + MEMORY.md rules
3. **Behavioral Boundaries** — safe-autonomously vs requires-asking
4. **Group Chat Protocol** (if applicable)
5. **Heartbeat System** (if applicable)

### TOOLS.md
- Device info, API credentials (env var references only), MCP servers, local paths
- "Skills define HOW. This file defines YOUR specifics."

### HEARTBEAT.md
- Empty = skip heartbeats (no API cost)
- Each line = one periodic check task
- During quiet hours: respond HEARTBEAT_OK

### MEMORY.md
- Curated durable facts. Loaded in private sessions only.
- Evergreen: no temporal decay in vector search.
- Mission statement, long-term goals, key decisions.

---

## Agent Configuration Schema

### Adding an Agent to openclaw.json
```json5
{
  agents: {
    list: [
      {
        id: "agent-id",            // Unique identifier
        name: "Display Name",      // Human-readable
        workspace: "~/.openclaw/workspace-{id}",
        agentDir: "~/.openclaw/agents/{id}/agent",
        model: "anthropic/claude-sonnet-4-5",
        tools: {
          allow: ["read", "write", "exec"],
          deny: ["browser"],
        },
        sandbox: {
          mode: "off",             // off | non-main | all
          scope: "agent",          // session | agent | shared
        },
      },
    ],
  },
}
```

### Critical Rules
- **Never reuse agentDir** across agents (causes auth/session collisions)
- Each agent gets own workspace directory
- Each agent gets own `~/.openclaw/agents/<id>/` state directory
- Create directories before adding agent:
  ```bash
  mkdir -p ~/.openclaw/agents/{id}/agent
  mkdir -p ~/.openclaw/agents/{id}/sessions
  mkdir -p ~/.openclaw/workspace-{id}/skills
  mkdir -p ~/.openclaw/workspace-{id}/memory
  ```

### Binding Rules (Multi-Agent Routing)
```json5
{
  bindings: [
    {
      agentId: "target-agent",
      match: {
        channel: "whatsapp",           // Channel name
        peer: { kind: "direct", id: "+15551234567" },  // Specific person
      },
    },
  ],
}
```

Priority: peer > parent peer > guild+roles > guild > team > account > channel > default.
All match fields must match simultaneously.

### Sub-Agent Configuration
```json5
{
  subagents: {
    model: "claude-3-5-haiku",        // Cheaper model for workers
    maxSpawnDepth: 2,                  // Recommended max
    maxChildrenPerAgent: 5,
    maxConcurrent: 8,
    archiveAfterMinutes: 60,
  },
}
```

Sub-agents only get AGENTS.md + TOOLS.md (no SOUL, no IDENTITY).

---

## Tool Groups (for allow/deny lists)

| Group | Tools |
|-------|-------|
| `group:runtime` | exec, bash, process |
| `group:fs` | read, write, edit, apply_patch |
| `group:sessions` | sessions_list, sessions_history, sessions_send, sessions_spawn |
| `group:memory` | memory_search, memory_get |
| `group:ui` | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging` | message |

---

## Validation Scoring Rubric

### Per-Skill (25 points)
| Check | Points |
|-------|--------|
| YAML frontmatter parses | 3 |
| metadata single-line JSON | 5 |
| Description format correct | 2 |
| Steps are actionable | 5 |
| Trigger defined | 3 |
| Output format specified | 3 |
| Error handling present | 2 |
| Approval gates for high-blast | 2 |

### Per-Workspace (25 points)
| Check | Points |
|-------|--------|
| SOUL.md has 4 sections | 4 |
| USER.md has name + timezone | 3 |
| IDENTITY.md has 5 fields | 3 |
| AGENTS.md has boundaries | 3 |
| TOOLS.md has infrastructure | 2 |
| No hardcoded API keys | 5 |
| allowFrom populated | 3 |
| Cron expressions valid | 2 |

### Cross-Reference (25 points)
| Check | Points |
|-------|--------|
| Timezone consistency | 3 |
| Channel consistency | 3 |
| Skills referenced exist | 4 |
| Tool policies match needs | 5 |
| Bindings point to valid agents | 5 |
| MEMORY.md private-session only | 2 |
| Blast radius matches autonomy | 3 |

### Score Thresholds
| Score | Action |
|-------|--------|
| >= 90 | Excellent — deploy |
| >= 80 | Good — deploy with notes |
| 70-79 | Needs work — fix specific issues, re-validate |
| < 70 | Major issues — announce problems, request guidance |
