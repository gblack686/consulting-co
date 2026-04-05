# OpenClaw Workspace File Specification

Source: https://docs.openclaw.ai

## Directory Structure

```
~/.openclaw/workspace/
├── SOUL.md           Core values and decision-making principles
├── USER.md           Person you're assisting
├── IDENTITY.md       Agent identity (name, creature, vibe, emoji)
├── MEMORY.md         Curated long-term facts (private sessions only)
├── AGENTS.md         Session behavior, memory protocol, boundaries
├── TOOLS.md          Environment-specific infrastructure details
├── HEARTBEAT.md      Periodic check tasks (empty = skip heartbeats)
├── memory/
│   └── YYYY-MM-DD.md Daily logs (append-only, auto-created)
└── skills/
    └── {domain}/
        └── {workflow}/
            └── SKILL.md
```

---

## SOUL.md

**Purpose**: Constitution for agent behavior. Loaded every session.

**Sections**:
1. **Core Truths** — 4 foundational principles:
   - Prioritize genuine assistance over performative language
   - Develop and express authentic opinions
   - Exhaust available resources before requesting help
   - Build credibility through competence
2. **Boundaries** — 3 limits:
   - Privacy is absolute
   - Request approval for external actions
   - Exercise caution in shared contexts
3. **Vibe** — Communication style (practical, personality-driven, no corporate tone)
4. **Continuity** — These files are persistent memory; review and update regularly

**Notes**: "Yours to evolve" — designed to be edited by both user and agent over time.

---

## USER.md

**Purpose**: Build understanding of the person you're assisting.

**Fields**:
- Name
- What to call them
- Pronouns (optional)
- Timezone
- Notes

**Context section**: Interests, current projects, preferences, personality traits.

**Principle**: Gather practical knowledge "to help you better serve them" while respecting privacy.

---

## IDENTITY.md

**Purpose**: Agent self-definition. "This isn't just metadata — it's the start of figuring out who you are."

**Fields**:
- `Name:` — pick something you like
- `Creature:` — AI? robot? familiar? ghost in the machine?
- `Vibe:` — sharp? warm? chaotic? calm?
- `Emoji:` — signature emoji
- `Avatar:` — workspace-relative path, URL, or data URI

---

## MEMORY.md

**Purpose**: Curated durable facts. Loaded ONLY in private/direct sessions (never in group chats).

**Content**: Mission statement, long-term goals, key decisions, preferences that should persist forever.

**Auto-flush**: When sessions approach context compaction, OpenClaw triggers a silent turn to persist durable memories before compression.

**Memory search**: Vector-based semantic search over all memory files. Hybrid BM25 + vector with temporal decay (30-day half-life). MEMORY.md is marked evergreen (no decay).

---

## AGENTS.md

**Purpose**: Session behavior constitution. Loaded every session.

**Sections**:
1. **Identity & Context Loading** — on session start:
   - Read SOUL.md ("this is who you are")
   - Read USER.md ("this is who you're helping")
   - Read recent memory files for continuity
   - Read MEMORY.md only in direct sessions
2. **Memory Architecture** — three-tier:
   - Daily notes (`memory/YYYY-MM-DD.md`): raw session logs
   - Long-term (`MEMORY.md`): curated, main sessions only
   - Operational (`TOOLS.md`): local skill references
3. **Behavioral Boundaries**:
   - Safe autonomously: file ops, web search, workspace tasks
   - Requires asking: external comms, destructive ops, uncertain actions
4. **Group Chat Protocol**: respond when asked, use reactions, don't dominate
5. **Heartbeat System**: batch routine tasks, when to stay quiet (HEARTBEAT_OK)

---

## TOOLS.md

**Purpose**: Environment-specific settings. "Skills define *how* tools work. This file is for *your* specifics."

**Content categories**: Camera devices, SSH hosts, TTS voices, API endpoints, local paths.

**Key rule**: "Skills are shared. Your setup is yours." Separates reusable skill logic from personal infrastructure.

---

## HEARTBEAT.md

**Purpose**: Task list for periodic agent check-ins (default every 30 minutes).

**Format**: Keep empty (or comments only) to skip heartbeat API calls. Add tasks when you want periodic checks.

**Examples**:
```markdown
- Check inbox for new emails from {important contacts}
- Review calendar for upcoming meetings
- Check {analytics tool} for anomalies
- If it's after 11pm, respond HEARTBEAT_OK (quiet hours)
```

**Cost note**: Each heartbeat runs a full agent turn, consuming tokens. Disable with `agents.defaults.heartbeat.every: "0m"` until confident.

---

## openclaw.json

**Purpose**: Gateway and agent configuration.

**Key sections**:
```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6",
    "workspace": "~/.openclaw/workspace",
    "thinkingDefault": "high",
    "timeoutSeconds": 1800,
    "heartbeat": { "every": "30m" }
  },
  "channels": {
    "whatsapp": {
      "allowFrom": ["+15555550123"]
    }
  },
  "session": {
    "scope": "per-sender",
    "resetTriggers": ["/new", "/reset"],
    "reset": { "mode": "daily", "atHour": 4, "idleMinutes": 10080 }
  },
  "skills": {
    "entries": {
      "skill-name": {
        "enabled": true,
        "env": { "API_KEY": "value" }
      }
    }
  },
  "cron": {
    "enabled": true
  }
}
```
