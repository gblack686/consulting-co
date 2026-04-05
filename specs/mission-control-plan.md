# Mission Control — Implementation Plan
**Source:** Alex Finn — "OpenClaw is 100x better with this tool (Mission Control)" (RhLpV6QDBFE)
**Date:** 2026-03-18
**Existing foundation:** `gb-automation-landing` (Vite/React, port 5173) + `customer-gateway-proxy` (port 3050 → OpenClaw :18789)

---

## What It Is

Mission Control is a **custom Next.js web dashboard** that the OpenClaw agent builds and maintains for itself. Every tool on it is vibe-coded by the agent on request — no hardcoded tools. It connects to OpenClaw's workspace files (MEMORY.md, cron jobs, AGENTS.md, skills) via the gateway proxy WebSocket.

Alex Finn's prompt to start: *"I want my own mission control where we can build custom tools. Please build it in Next.js and host it on the local host. Make it a clean interface that looks like Linear."*

---

## The 6 Core Pages (from transcript)

### 1. Task Board (0:35)
**Kanban board for tracking all agent tasks**

- Columns: Backlog → In Progress → In Review → Done
- Each task shows: assignee (G = Greg/user, H = Henry/agent), description, timestamps
- **Live Activity Feed** on left sidebar: real-time stream of everything the agent is doing
- "In Review" column: tasks needing human approval before proceeding
- **Key integration:** Agent checks task board every heartbeat; picks up any tasks assigned to it in Backlog and executes autonomously
- Add new tasks via UI → agent auto-discovers and works them

**Prompt to build:** *"Build me a kanban task board where I can see tasks assigned to you and me. Include a live activity feed on the left showing everything you're doing in real time. In every heartbeat, check the task board for any tasks in the backlog assigned to you and complete them."*

---

### 2. Calendar (3:57)
**Cron job and scheduled task viewer**

- Shows all scheduled cron jobs as calendar events
- Lets user verify the agent actually scheduled tasks it promised to do
- Critical for: "I'll do that every morning" — confirm it's actually in cron
- After scheduling a task via chat: come here to verify it appears

**Prompt to build:** *"Build a calendar screen for our mission control that shows all my cron jobs and scheduled tasks. I want to verify you're actually being proactive."*

---

### 3. Projects (5:10)
**High-level project tracker**

- One entry per major project
- Shows: project name, progress %, last worked on, linked tasks/memories/docs
- Prevents context-switching trap — keeps focus on what actually matters
- **Reverse prompt integration:** "What's one task we can do right now to progress one of our major projects?"
- Cross-links to Task Board, Memory, and Docs pages

**Prompt to build:** *"Build a projects screen in our mission control. Add a project for every major project we're working on. Show progress and link tasks, memories, and docs to each project."*

---

### 4. Memory (7:03)
**MEMORY.md browser and journal**

- Displays all agent memories organized by day (like a journal)
- Separate section for long-term memories vs daily memories
- Searchable — find old conversations and decisions fast
- Source: reads from `~/.openclaw/workspace/MEMORY.md` and daily memory files

**Prompt to build:** *"I want a memory screen in our mission control that allows me to view every memory you have organized by day. Build that out and also have a long-term memory section that shows all long-term memories."*

---

### 5. Docs (8:29)
**All agent-generated documents in one place**

- Every doc the agent creates (PRDs, reports, newsletters, plans, architecture docs) appears here
- Auto-categorized by type (plan, report, draft, research, etc.)
- Format tag shown per doc (markdown, HTML, JSON, etc.)
- **Searchable** — find docs by keyword instantly
- Eliminates having to scroll back through Telegram/Discord chat history
- Source: watches a `docs/` folder the agent writes to

**Prompt to build:** *"I want a docs tool where I can go back and view all the previous documents you created for me in a nicely formatted view. Make it searchable and categorize the documents."*

---

### 6. Team (10:29)
**Agent org chart + mission statement**

- Shows all active agents and sub-agents: name, role, model, device
- Mission statement prominently displayed at top
- Used by agents as "source of truth" for who to delegate work to
- Helps agents remember: "I should give dev work to the coder agent, research to the scout"
- **Reverse prompt:** "What task can we do right now that brings us closer to our mission statement?"

**Prompt to build:** *"Build a team screen that shows me all the agents and sub-agents we have running, their roles, what models they use, and what devices they're on. Put our mission statement at the top."*

---

### 7. Office (12:44) — Optional / Fun
**2D pixel art live agent activity view**

- Animated pixel art office with desks for each agent
- When an agent is working, it sits at its desk; when idle, it wanders
- Agents can "meet at the water cooler" when communicating with each other
- Shows what each agent is currently working on
- Makes the system feel alive and engaging — increases usage

**Prompt to build:** *"I want a screen that visualizes all the work you're doing. I want a 2D pixel art office that shows you and all sub agents. I want them to have desks and when they are doing work, they go to their desk and actually do the work."*

---

## Tech Stack Decision

Alex Finn specifies **Next.js** hosted locally. Our existing stack:
- `gb-automation-landing` = Vite + React (already built, `/dashboard` route exists)
- `customer-gateway-proxy` = Node.js WebSocket bridge (port 3050)

**Decision options:**

| Option | Pros | Cons |
|--------|------|------|
| **A: Extend gb-automation-landing** | Already exists, same stack, `/dashboard` becomes Mission Control | Vite not Next.js; mixing concerns |
| **B: New Next.js app** | Matches Alex Finn's exact spec; cleaner separation | New app to manage, separate port |
| **C: Hybrid** | Add `/mission-control` routes to existing app | Works but messy |

**Recommendation: Option A** — extend the existing dashboard. The `/dashboard` route already has the 3-panel layout (Sessions \| EventStream \| Chat). Expand it with the 7 Mission Control pages as sidebar nav items. No need for Next.js specifically — that's just Alex Finn's preference.

---

## Data Sources (what powers each page)

| Page | Data Source | How to Access |
|------|------------|---------------|
| Task Board | `~/.openclaw/workspace/tasks.md` or new `tasks.json` | Agent writes tasks to file; MC reads via gateway API |
| Calendar | `openclaw cron list` output | Gateway exposes cron endpoint |
| Projects | `~/.openclaw/workspace/projects.md` | Agent writes; MC reads |
| Memory | `~/.openclaw/workspace/MEMORY.md` + daily memory files | Gateway file read endpoint |
| Docs | `~/.openclaw/workspace/docs/` folder | Watch folder, render markdown |
| Team | `~/.openclaw/workspace/AGENTS.md` | Parse AGENTS.md |
| Office | Agent heartbeat WebSocket | Real-time via existing WS connection |

---

## Integration with OpenClaw Gateway

The gateway proxy at port 3050 already bridges WebSocket from the frontend. Needed additions:

```
GET  /api/tasks          → reads tasks.json from workspace
GET  /api/cron           → runs `openclaw cron list` via SSH/shell
GET  /api/projects       → reads projects.md
GET  /api/memories       → reads MEMORY.md + daily files
GET  /api/docs           → lists docs/ folder with metadata
GET  /api/agents         → reads AGENTS.md
WS   /ws                 → existing (heartbeat + live activity feed)
POST /api/tasks          → creates new task, agent picks up via heartbeat
```

---

## Build Order (phased)

### Phase 1 — Foundation (Linear Issue LIN-MC-1)
- Scaffold Mission Control sidebar nav in `gb-automation-landing` `/dashboard`
- Add gateway API endpoints for tasks, memory, agents, cron
- **Page 1: Task Board** — highest value, solves #1 user complaint ("what is my agent doing?")
- **Page 2: Calendar** — cron verification, critical for trust

### Phase 2 — Content (LIN-MC-2)
- **Page 3: Docs** — document library (high daily use)
- **Page 4: Memory** — memory browser (great for orientation)

### Phase 3 — Organization (LIN-MC-3)
- **Page 5: Projects** — cross-links tasks + memories + docs
- **Page 6: Team** — agent org chart + mission statement display

### Phase 4 — Delight (LIN-MC-4)
- **Page 7: Office** — 2D pixel art (fun, optional)
- Personalization: reverse-prompt tool to discover client-specific tools
- Per-client customization hooks

---

## Linear Issues to Create

| Issue | Title | Effort |
|-------|-------|--------|
| LIN-MC-1 | Mission Control: scaffold nav + gateway API + Task Board + Calendar | L |
| LIN-MC-2 | Mission Control: Docs page + Memory browser | M |
| LIN-MC-3 | Mission Control: Projects + Team pages | M |
| LIN-MC-4 | Mission Control: Office (2D pixel art) + reverse-prompt tool discovery | L |
| LIN-MC-5 | Mission Control: per-client deploy (add to consulting-intake pipeline) | M |

---

## Key Prompts from Alex Finn (for agents to use)

**Bootstrap:**
> "I want my own mission control where we can build custom tools. Please build it in Next.js and host it on the local host. Make it a clean interface that looks like Linear."

**Task board + heartbeat integration:**
> "In every heartbeat, check the task board for any tasks in the backlog assigned to you and complete them autonomously."

**Discover custom tools:**
> "Based on what you know about me, what we've done, our workflows, our mission statement, our goals — what custom tools should we build out in our mission control?"

**Find mission statement:**
> "Based on everything you know about me, what should our mission statement be?"

**Use this video:**
> "Check this out: https://youtu.be/RhLpV6QDBFE — is there anything in this video we haven't done yet? Build it out."

---

## Connection to Consulting Intake (META-5)

Every client workspace built via `consulting-intake` should eventually include:
1. A mission control deploy step in Step 5b
2. A `mission-control-setup` skill in the workspace skills list
3. The Task Board pre-populated with the client's top Phase 1 workflows from their workflow catalog
4. The Team page pre-populated from their `AGENTS.md`
5. The Mission Statement pulled from their `session_output/mission_statement.md`
