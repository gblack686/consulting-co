# Doc-Claude-Workbench - Updated Architecture Plan
**Version:** 2.0 (No Langfuse)
**Date:** 2025-12-01
**Based On:** quickstart-nexus superseding pattern

---

## Executive Summary

Based on review of `quickstart-nexus/.claude`, the superseding architecture **removes Langfuse** entirely and uses a simpler, more efficient stack:

**The Winning Pattern:**
```
Claude Code Hooks → SQLite (events.db) → Haiku Enrichment → Graphiti/Neo4j → Obsidian
```

**Key Benefits:**
- ✅ **Lightweight** - No 4GB Docker container
- ✅ **Fast** - SQLite is instant, local
- ✅ **Cheap** - Haiku enrichment ~$0.0003/event with 66% cache hit
- ✅ **Simple** - All data in one SQLite file
- ✅ **Real-time Dashboard** - Bun backend + Vue frontend (optional)

---

## Integrations Found in quickstart-nexus

### 1. SQLite Event Storage ✅
**File:** `.claude/observability/backend/events.db`
**Schema:** 51 columns including:
- Basic: event_type, timestamp, session_id
- Enriched: intent, complexity, tool_effectiveness
- Metadata: model, tokens, cost estimates

**Hook Scripts:**
- `send_event.py` - Core event logger
- `send_event_v2.py` - With Haiku enrichment

### 2. Haiku Enrichment ✅
**Location:** `.claude/hooks/batch_enrich.py`
**Features:**
- Real-time enrichment (async, non-blocking)
- Batch processing with Anthropic Batch API (50% cost savings)
- 66% cache hit rate
- Intent detection, complexity estimation, tool effectiveness

**Cost:** ~$0.0003 per event (vs Langfuse overhead)

### 3. Graphiti + Neo4j ✅
**Hook:** `.claude/hooks/log_to_graphiti.py`
**Features:**
- Automatic entity extraction (people, concepts, decisions, tools)
- Relationship mapping
- Temporal indexing
- Knowledge graph growth over time

**Storage:** Neo4j database (local or cloud)

### 4. Obsidian Export ✅
**Script:** `.claude/obsidian/scripts/obsidian_exporter.py`
**Config:** `.claude/obsidian/config/obsidian.yaml`
**Features:**
- Auto-generated session notes
- Daily summaries
- Entity backlinks
- Frontmatter with metadata
- Configurable export frequency

### 5. Multi-Agent Observability Dashboard ✅
**Location:** `.claude/observability/`
**Stack:**
- Backend: Bun + TypeScript + SQLite (port 4000)
- Frontend: Vue 3 + TypeScript (port 5173)
- Real-time: WebSocket for live updates

**Event Types Captured:**
- PreToolUse, PostToolUse
- SubagentStop ⭐ (unique to this system)
- Stop, UserPromptSubmit
- SessionStart, SessionEnd
- Notification, PreCompact

---

## Updated Architecture Layers

### A. Storage & Memory

```
┌─ SQLite (events.db) ────────────────┐
│ - All hook events (51 columns)      │
│ - Enriched with Haiku analysis      │
│ - Fast queries, lightweight         │
│ - Single file, easy backup          │
└──────────────────────────────────────┘

┌─ Neo4j ─────────────────────────────┐
│ - Episodes (session events)          │
│ - Entities (concepts, decisions)     │
│ - Relationships (connections)        │
│ - Temporal index (time queries)      │
└──────────────────────────────────────┘

┌─ Obsidian Vault ────────────────────┐
│ - sessions/ (auto-generated notes)   │
│ - daily/ (daily summaries)           │
│ - bugs/ (bug.md tracking)            │
│ - tasks/ (tasks.md tracking)         │
│ - plans/ (plans.md roadmaps)         │
│ - decisions/ (ADRs)                  │
│ - learnings/ (knowledge notes)       │
│ - entities/ (KG entity references)   │
└──────────────────────────────────────┘
```

### B. Data Flow

```
┌──────────────────────────────────────────────────────┐
│ 1. User Action (prompt, tool use, subagent)         │
└────────────────┬─────────────────────────────────────┘
                 ▼
┌──────────────────────────────────────────────────────┐
│ 2. Claude Code Hook Fires (e.g., Stop)              │
└────────────────┬─────────────────────────────────────┘
                 ▼
┌──────────────────────────────────────────────────────┐
│ 3. Python Hook Script Executes                      │
│    - send_event_v2.py (with enrichment)             │
└────────────────┬─────────────────────────────────────┘
                 ▼
         ┌───────┴───────┐
         ▼               ▼
┌─────────────────┐ ┌─────────────────────┐
│ 4a. SQLite      │ │ 4b. Haiku Enrichment│
│     Insert      │ │     (async)         │
└─────────────────┘ └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ 5. Update SQLite    │
                    │    with enrichment  │
                    └──────────┬──────────┘
                               ▼
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
┌─────────────────────┐                 ┌─────────────────────┐
│ 6a. Graphiti Hook   │                 │ 6b. WebSocket       │
│     (if enabled)    │                 │     Broadcast       │
└──────────┬──────────┘                 └──────────┬──────────┘
           ▼                                       ▼
┌─────────────────────┐                 ┌─────────────────────┐
│ 7a. Neo4j Storage   │                 │ 7b. Live Dashboard  │
│     (entities)      │                 │     Update          │
└──────────┬──────────┘                 └─────────────────────┘
           ▼
┌─────────────────────┐
│ 8. Obsidian Export  │
│    (per-session or  │
│     end-of-day)     │
└─────────────────────┘
```

### C. Agents (To Build)

#### 1. Admin Agent
**Responsibilities:**
- Bilateral sync: Obsidian ↔ Neo4j
- Update bug.md, tasks.md, plans.md
- Generate daily summaries
- Maintain entity reference notes

**Triggers:**
- End of session (Stop hook)
- End of day (cron)
- Manual trigger (slash command)

**Implementation:**
```python
# .claude/agents/admin-agent/admin_agent.py
# Reads from SQLite events.db and Neo4j
# Writes to Obsidian vault
# Uses obsidian_exporter.py as base
```

#### 2. Code-Fix Agent
**Responsibilities:**
- Analyze errors from tool failures
- Suggest code patches
- Log fixes to bug.md
- Update SQLite with fix metadata

**Triggers:**
- PostToolUse with error status
- Manual trigger on demand

**Implementation:**
```python
# .claude/agents/code-fix-agent/code_fix_agent.py
# Uses Haiku for fast analysis
# Logs to events.db + bug.md
```

#### 3. Future Agents (Optional)
- **Refactor Agent** - Optimize codebase for AI
- **Branding Agent** - Visual assets with ComfyUI

---

## Comparison: Old vs New

### Old Plan (Langfuse-based)
| Component | Issue |
|-----------|-------|
| Langfuse | 4GB Docker container, complex setup |
| Storage | Postgres DB for traces |
| Observability | Web UI at port 3000, but heavyweight |
| Cost | More expensive with external service |

### New Plan (quickstart-nexus pattern)
| Component | Benefit |
|-----------|---------|
| SQLite | Single file, lightweight, fast |
| Haiku Enrichment | $0.0003/event, 66% cache hit |
| Dashboard | Optional, Bun + Vue, port 5173 |
| Total Cost | ~$10-20/month (OpenAI for Graphiti only) |

---

## Updated 4-Week Roadmap

### Week 1: Foundation (Copy from quickstart-nexus)
**Days 1-2: Hook System Migration**
- [ ] Copy hook scripts from quickstart-nexus
  - `send_event.py`
  - `send_event_v2.py` (with Haiku)
  - `log_to_graphiti.py`
  - `user_prompt_submit.py`
  - `stop.py`
  - All other hook scripts
- [ ] Copy `utils/` directory (database helpers)
- [ ] Remove all Langfuse references
- [ ] Update settings.local.json

**Days 3-4: Obsidian Integration**
- [ ] Create Obsidian folder structure
- [ ] Create 5 templates (session, daily, bug, tasks, plans)
- [ ] Copy `obsidian_exporter.py`
- [ ] Configure `obsidian.yaml`
- [ ] Test manual export

**Days 5-7: Testing & First Content**
- [ ] Run full workflow: prompt → hooks → SQLite → Neo4j → Obsidian
- [ ] Verify all 9 hook types working
- [ ] Take screenshots of Neo4j graph
- [ ] Record Loom: "My Lightweight AI Observability Stack"

### Week 2: Admin Agent
**Days 1-3: Build Admin Agent**
- [ ] Design prompts for bilateral sync
- [ ] Implement Obsidian → Neo4j sync
- [ ] Implement Neo4j → Obsidian sync
- [ ] Auto-update bug.md, tasks.md, plans.md

**Days 4-5: Daily Summaries**
- [ ] Generate end-of-day summaries
- [ ] Create entity reference notes
- [ ] Link related sessions

**Days 6-7: Testing & Content**
- [ ] Test Admin Agent end-to-end
- [ ] Record Loom: "Admin Agent Auto-Syncing Notes"

### Week 3: Code-Fix Agent & Dashboard
**Days 1-3: Code-Fix Agent**
- [ ] Build error analyzer with Haiku
- [ ] Implement patch suggestions
- [ ] Log fixes to bug.md + events.db
- [ ] Test with intentional errors

**Days 4-5: Dashboard (Optional)**
- [ ] Copy observability/ from quickstart-nexus
- [ ] Customize for consulting-co
- [ ] Test real-time event streaming

**Days 6-7: Polish & Content**
- [ ] Document all agents
- [ ] Record Loom: "Code-Fix Agent in Action"

### Week 4: UI for .claude Config
**Days 1-3: Config UI**
- [ ] Simple Streamlit app for editing configs
- [ ] Agent prompt editor
- [ ] Hook enable/disable toggles
- [ ] Settings viewer

**Days 4-5: Branding**
- [ ] Add nano banana visual identity
- [ ] Create agent avatars
- [ ] Apply to dashboard

**Days 6-7: Final Content**
- [ ] Comprehensive README
- [ ] Architecture diagrams
- [ ] Record 2 Looms:
  - "Full Stack Walkthrough"
  - "How to Adapt for Clients"

---

## File Structure (Target State)

```
.claude/
├── agents/
│   ├── admin-agent/
│   │   ├── config.yaml
│   │   ├── prompts/
│   │   └── admin_agent.py
│   └── code-fix-agent/
│       ├── config.yaml
│       ├── prompts/
│       └── code_fix_agent.py
│
├── hooks/
│   ├── utils/
│   │   ├── database.py
│   │   ├── enrichment.py
│   │   └── models.py
│   ├── send_event.py
│   ├── send_event_v2.py
│   ├── log_to_graphiti.py
│   ├── user_prompt_submit.py
│   ├── stop.py
│   ├── session_start.py
│   ├── session_end.py
│   ├── pre_tool_use.py
│   ├── post_tool_use.py
│   └── subagent_stop.py
│
├── observability/
│   ├── backend/
│   │   ├── events.db (SQLite)
│   │   └── src/
│   └── frontend/
│       └── src/
│
├── obsidian/
│   ├── config/
│   │   └── obsidian.yaml
│   └── scripts/
│       └── obsidian_exporter.py
│
├── context/
│   ├── planning/
│   │   ├── TONIGHT-PLAN.md
│   │   └── UPDATED-ARCHITECTURE-PLAN.md
│   └── observability/
│       ├── KNOWLEDGE_GRAPH_STATUS.md
│       ├── ENRICHED_SCHEMA.md
│       └── screenshots/
│
├── scripts/
│   ├── review_neo4j_schema.py
│   └── cleanup_old_events.py
│
├── settings.local.json
└── README.md
```

---

## Technology Stack

### Core Infrastructure
- **Python 3.10+** - Hook scripts, agents
- **SQLite** - Event storage (events.db)
- **Neo4j** - Knowledge graph
- **Obsidian** - Human-readable notes

### AI Services
- **Anthropic Claude Haiku** - Event enrichment ($0.0003/event)
- **OpenAI GPT-4o-mini** - Graphiti entity extraction

### Dashboard (Optional)
- **Bun** - Backend runtime
- **TypeScript** - Backend + frontend
- **Vue 3** - Frontend framework
- **WebSocket** - Real-time updates

### Cost Estimate
- Haiku enrichment: ~$5-10/month (heavy usage)
- Graphiti/OpenAI: ~$5-10/month
- **Total: $10-20/month**

---

## Key Differences from Original Plan

| Aspect | Original Plan | Updated Plan |
|--------|---------------|--------------|
| **Observability** | Langfuse (4GB Docker) | SQLite + Haiku ($0.0003/event) |
| **Storage** | Postgres | SQLite (single file) |
| **Enrichment** | Manual/later | Real-time with Haiku |
| **Dashboard** | None initially | Bun + Vue (optional) |
| **Complexity** | High | Low |
| **Setup Time** | 2+ hours | 30 minutes |
| **Monthly Cost** | $20-50 | $10-20 |
| **Disk Usage** | 4GB+ | <100MB |

---

## Migration Path from Current Setup

### What to Keep
✅ Neo4j + Graphiti integration
✅ Obsidian vault structure (enhance it)
✅ Basic hook concepts
✅ Agent definitions (refactor)

### What to Remove
❌ All Langfuse references
❌ Langfuse Docker container
❌ Langfuse hook scripts
❌ Langfuse documentation

### What to Copy from quickstart-nexus
➕ All hook scripts (send_event*.py, log_to_graphiti.py, etc.)
➕ utils/ directory (database, enrichment helpers)
➕ observability/ dashboard (optional)
➕ obsidian/ export scripts

### Migration Steps
1. **Backup current .claude directory**
   ```bash
   cp -r .claude .claude.backup.$(date +%Y%m%d)
   ```

2. **Copy hook system**
   ```bash
   cp -r ../aws/RevStar/quickstarts/quickstart-nexus/.claude/hooks/* .claude/hooks/
   ```

3. **Copy observability**
   ```bash
   cp -r ../aws/RevStar/quickstarts/quickstart-nexus/.claude/observability .claude/
   ```

4. **Copy obsidian**
   ```bash
   cp -r ../aws/RevStar/quickstarts/quickstart-nexus/.claude/obsidian .claude/
   ```

5. **Update settings.local.json**
   - Remove Langfuse config
   - Add SQLite path
   - Configure Obsidian vault path

6. **Test**
   ```bash
   # Start a Claude session
   # Verify events in SQLite
   sqlite3 .claude/observability/backend/events.db "SELECT * FROM events ORDER BY timestamp DESC LIMIT 5;"
   ```

---

## Success Metrics (Updated)

### Technical
- [ ] SQLite events.db contains all session events
- [ ] Haiku enrichment working with >60% cache hit rate
- [ ] Neo4j graph growing with each session
- [ ] Obsidian notes auto-generated per session
- [ ] Dashboard (if enabled) shows real-time events

### Business
- [ ] Daily use of workbench for projects
- [ ] 4 high-quality Looms recorded
- [ ] 1 client demo-ready environment
- [ ] Clear before/after consulting story

### Personal
- [ ] Obsidian notes actually useful
- [ ] Bug/task tracking actually working
- [ ] Knowledge graph searchable
- [ ] Proud to show clients

---

## Next Steps (Tonight)

See **[TONIGHT-PLAN.md](TONIGHT-PLAN.md)** for detailed 2-hour plan focusing on:
1. Templating Obsidian structure
2. Reviewing Neo4j knowledge graph
3. Taking screenshots for first content

---

**This architecture is proven** - it's working in quickstart-nexus right now. We just need to copy it over and customize for consulting-co.

**Version:** 2.0 (No Langfuse)
**Last Updated:** 2025-12-01
**Next Review:** After Week 1 completion
