# Multi-Agent Deployment Patterns

Maps consulting session complexity to the right OpenClaw agent architecture.

## Pattern Selection (During Session)

| Signal from Client | Pattern | Why |
|---|---|---|
| 1-2 domains, simple workflows, same vibe everywhere | **A: Single Agent** | Overhead of multi-agent not worth it |
| 3+ domains, different vibes per context | **B: Multi-Agent by Domain** | Each domain is a "department" with its own brain |
| Clear personal/work split, different channels | **C: Multi-Agent by Context** | Route by WhatsApp account or channel |
| Complex orchestration, sub-tasks, delegation | **D: Orchestrator + Workers** | Main agent delegates to specialized sub-agents |
| Team/family access, shared device | **E: Multi-Agent by Peer** | Different people talk to different agents |

Most consulting clients will be **Pattern B or C**. Pattern A is for simple setups. Pattern D is for power users.

---

## Pattern A: Single Agent, Many Skills

```
~/.openclaw/
├── openclaw.json
├── agents/main/
└── workspace/
    ├── SOUL.md, USER.md, IDENTITY.md, MEMORY.md
    ├── AGENTS.md, TOOLS.md, HEARTBEAT.md
    └── skills/
        ├── content/write-newsletter/SKILL.md
        ├── content/research-trends/SKILL.md
        ├── business/sync-pipeline/SKILL.md
        └── personal/morning-brief/SKILL.md
```

**openclaw.json**:
```json5
{
  agents: {
    defaults: { workspace: "~/.openclaw/workspace" },
    list: [{ id: "main", default: true }],
  },
}
```

**When to use**: Simple setups, 1-2 domains, same communication style everywhere.

---

## Pattern B: Multi-Agent by Domain

Each domain discovered in the consulting session becomes its own agent. Each agent has its own workspace, personality files, and skills.

```
~/.openclaw/
├── openclaw.json
├── agents/
│   ├── main/           (orchestrator — routes requests, spawns domain agents)
│   ├── content/
│   ├── business/
│   └── personal/
├── workspace-main/
│   ├── SOUL.md         (shared values, orchestrator vibe)
│   ├── USER.md         (full client profile)
│   ├── IDENTITY.md     (main agent identity)
│   ├── MEMORY.md       (global mission, cross-domain context)
│   ├── AGENTS.md       (orchestrator behavior — routes, delegates)
│   └── TOOLS.md        (full tool inventory)
├── workspace-content/
│   ├── SOUL.md         (content-specific vibe: creative, expressive)
│   ├── USER.md         (content-relevant preferences only)
│   ├── IDENTITY.md     (content agent identity)
│   ├── AGENTS.md       (content boundaries: can post, can't send money)
│   ├── TOOLS.md        (YouTube API, ConvertKit, Buffer)
│   ├── HEARTBEAT.md    (check analytics, trending topics)
│   └── skills/
│       ├── write-newsletter/SKILL.md
│       └── research-trends/SKILL.md
├── workspace-business/
│   ├── SOUL.md         (business vibe: professional, precise)
│   ├── USER.md         (business-relevant context)
│   ├── IDENTITY.md     (business agent identity)
│   ├── AGENTS.md       (business boundaries: can read CRM, needs approval for deals)
│   ├── TOOLS.md        (CRM API, invoicing, analytics)
│   ├── HEARTBEAT.md    (check pipeline, follow-ups)
│   └── skills/
│       └── sync-pipeline/SKILL.md
└── workspace-personal/
    ├── SOUL.md         (personal vibe: warm, casual)
    ├── USER.md         (personal preferences)
    ├── IDENTITY.md     (personal agent identity)
    ├── AGENTS.md       (personal boundaries: full autonomy for routine)
    ├── TOOLS.md        (calendar, email, weather)
    ├── HEARTBEAT.md    (morning brief checks)
    └── skills/
        └── morning-brief/SKILL.md
```

**openclaw.json**:
```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4-5" },
      subagents: {
        model: "claude-3-5-haiku",
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
      },
    },
    list: [
      {
        id: "main",
        default: true,
        name: "{agent_name}",
        workspace: "~/.openclaw/workspace-main",
        model: "anthropic/claude-sonnet-4-5",
        subagents: {
          allowAgents: ["content", "business", "personal"],
        },
      },
      {
        id: "content",
        name: "{agent_name} — Content",
        workspace: "~/.openclaw/workspace-content",
        model: "anthropic/claude-sonnet-4-5",
        tools: {
          allow: ["read", "write", "exec", "browser"],
        },
      },
      {
        id: "business",
        name: "{agent_name} — Business",
        workspace: "~/.openclaw/workspace-business",
        model: "anthropic/claude-sonnet-4-5",
        tools: {
          allow: ["read", "write", "exec"],
          deny: ["browser"],
        },
      },
      {
        id: "personal",
        name: "{agent_name} — Personal",
        workspace: "~/.openclaw/workspace-personal",
        model: "anthropic/claude-sonnet-4-5",
        tools: {
          allow: ["read", "write", "exec"],
        },
      },
    ],
  },
  bindings: [
    // Route by keyword or let main orchestrate via sub-agents
  ],
}
```

**When to use**: 3+ domains with different vibes, different tool needs, or different autonomy levels per domain.

---

## Pattern C: Multi-Agent by Context

Split by life context rather than workflow domain. Fewer agents, broader scope each.

```
~/.openclaw/
├── workspace-home/     (personal + content + hobbies)
├── workspace-work/     (business + clients + finance)
```

**openclaw.json**:
```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

**When to use**: Clear personal/work split, different WhatsApp accounts or channels per context.

---

## Pattern D: Orchestrator + Workers

Main agent dispatches specialized sub-agents for complex tasks.

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
        subagents: {
          model: "anthropic/claude-sonnet-4-5",
          allowAgents: ["researcher", "writer", "analyst"],
          maxSpawnDepth: 2,
          maxChildrenPerAgent: 5,
        },
      },
      {
        id: "researcher",
        workspace: "~/.openclaw/workspace-researcher",
        tools: { allow: ["read", "exec", "browser"] },
      },
      {
        id: "writer",
        workspace: "~/.openclaw/workspace-writer",
        tools: { allow: ["read", "write", "edit", "exec"] },
      },
      {
        id: "analyst",
        workspace: "~/.openclaw/workspace-analyst",
        tools: { allow: ["read", "exec"] },
      },
    ],
  },
}
```

Sub-agent behavior:
- Run in isolated sessions (non-blocking)
- Only get AGENTS.md + TOOLS.md (no SOUL/IDENTITY)
- Report results back to parent on completion
- Support nesting up to depth 5 (depth 2 recommended)

**When to use**: Power users, complex multi-step workflows, cost optimization (haiku workers, opus orchestrator).

---

## Pattern E: Multi-Agent by Peer

Different people talk to different agents on the same device.

```json5
{
  bindings: [
    { agentId: "alex", match: { peer: { kind: "direct", id: "+15551230001" } } },
    { agentId: "family", match: { peer: { kind: "group", id: "120363...@g.us" } } },
  ],
}
```

**When to use**: Family/team access, WhatsApp group bots, shared infrastructure.

---

## Mapping Domains to Agents

### What the Pipeline Should Produce

For each domain discovered in the consulting session, decide:

| Decision | Separate Agent | Skill in Main Agent |
|----------|---------------|-------------------|
| Domain needs different vibe | Agent | — |
| Domain needs different tools | Agent | — |
| Domain needs different autonomy level | Agent | — |
| Domain is simple (1-2 workflows) | — | Skill |
| Domain shares tools with others | — | Skill |
| Client wants unified personality | — | Skill |

### Hybrid Approach (Most Common)

Most clients will get:
- **Main agent** — personal assistant, morning brief, general queries
- **1-2 domain agents** — for their most complex domains (content, business)
- **Skills in main** — for simple workflows that don't warrant a full agent

### Per-Domain Agent Workspace

Each domain agent workspace contains:
1. **SOUL.md** — domain-adapted vibe (creative for content, precise for business)
2. **USER.md** — domain-relevant client context only
3. **IDENTITY.md** — domain agent identity (optional: same name, different emoji)
4. **AGENTS.md** — domain-specific boundaries and autonomy
5. **TOOLS.md** — only the tools this domain needs
6. **HEARTBEAT.md** — domain-specific periodic checks
7. **skills/** — domain workflow skills

### What Stays Shared

- `MEMORY.md` in main agent workspace — global mission, cross-domain context
- openclaw.json — single gateway config with all agents
- Claude Code experts — in `.claude/commands/experts/` for ongoing development

---

## Deploy Script Changes

### Multi-Agent Deployment

```bash
# Deploy main workspace
scp -r -i {key} workspace-main/* ubuntu@{host}:~/.openclaw/workspace-main/

# Deploy per-domain workspaces
for domain in content business personal; do
  scp -r -i {key} workspace-${domain}/* ubuntu@{host}:~/.openclaw/workspace-${domain}/
done

# Deploy config (includes agents list + bindings)
scp -i {key} openclaw.json ubuntu@{host}:~/.openclaw/openclaw.json

# Create agent directories
ssh -i {key} ubuntu@{host} "
  for agent in main content business personal; do
    mkdir -p ~/.openclaw/agents/\${agent}/agent
    mkdir -p ~/.openclaw/agents/\${agent}/sessions
  done
"

# Restart gateway (hot-reloads agents)
ssh -i {key} ubuntu@{host} "systemctl --user restart openclaw-gateway"

# Verify all agents loaded
ssh -i {key} ubuntu@{host} "openclaw agents list --bindings"

# Health check
ssh -i {key} ubuntu@{host} "openclaw doctor"
```

---

## Sub-Agent vs. Full Agent Decision

| Factor | Sub-Agent | Full Agent |
|--------|-----------|------------|
| Own personality (SOUL, IDENTITY) | No (gets AGENTS+TOOLS only) | Yes |
| Own memory | No (shares parent session) | Yes (own workspace) |
| Directly reachable by user | No (spawned by parent) | Yes (via bindings) |
| Persistent across sessions | No (ephemeral) | Yes |
| Own cron jobs | No | Yes |
| Own heartbeat | No | Yes |
| Cost when idle | Zero | Zero (only costs when active) |

**Rule of thumb**: If the domain needs its own personality, memory, or scheduled tasks, make it a full agent. If it's just a background worker for research or processing, make it a sub-agent.
