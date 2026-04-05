# Doc-Claude-Workbench Evolution Plan
**Project:** Flagship Agentic Development Workbench
**Version:** 1.0
**Date:** 2025-12-01
**Status:** Planning Phase

---

## Executive Summary

Transform the current consulting-co `.claude` directory into **"doc-claude-workbench"** - a flagship, living portfolio project that:
- Showcases your agentic / Claude / Knowledge Graph expertise
- Doubles as your own production dev workspace
- Serves as your primary consulting demo and pitch material
- Is interesting enough to create content around (Looms, posts, proposals)

This is the **one killer consulting story**: *"I dogfood an internal agentic workbench that keeps my notes, bugs, and code history in sync across Obsidian + Neo4j + SQL. That's the same pattern I'll use to wire up your org."*

---

## Current State Analysis

### What You Have (Already Impressive!)

#### Repositories Found
1. **claude-code-hooks-mastery** (Last updated: 2025-08-21)
2. **claude-code-hooks-multi-agent-observability** (Last updated: 2025-11-16)
   - Real-time monitoring for Claude Code agents
3. **claude-template** (Last updated: 2025-11-29) ⭐ Most recent
   - This is your baseline template

#### Current .claude Directory Structure
```
.claude/
├── agents/                     # 7 agent definitions
│   ├── AI_CODEBASE_OPTIMIZER.md
│   ├── GRAPHITI_AGENT.md
│   ├── INTEGRATION_ORCHESTRATOR.md
│   ├── LANGFUSE_AGENT.md
│   ├── OBSERVABILITY_AGENT.md
│   ├── OBSIDIAN_AGENT.md
│   └── YOUTUBE_ANALYSIS_AGENT.md
│
├── commands/                   # Custom slash commands
│   ├── codebase-knowledge-extract/
│   ├── consulting/
│   ├── obsidian/
│   ├── scoping/
│   └── youtube-detailed-analysis.md
│
├── hooks/                      # 15+ lifecycle hooks
│   ├── log_to_graphiti.py
│   ├── log_to_langfuse.py
│   ├── observe_to_graphiti.py
│   ├── post_tool_use.py
│   ├── pre_tool_use.py
│   ├── session_start.py
│   ├── session_end.py
│   ├── stop.py
│   ├── subagent_stop.py
│   └── user_prompt_submit.py
│
├── skills/                     # 5 custom skills
│   ├── knowledge-sync/
│   ├── obsidian-schema-generator/
│   ├── obsidian-vault/
│   ├── revstar-quickstart-workflow/
│   └── youtube-video-archiver/
│
├── orchestrator/              # Multi-agent orchestration
│   ├── orchestrator_3_stream/
│   ├── orchestrator_db/
│   └── docker-compose.yml
│
└── docs/                      # 30+ documentation files
    ├── ARCHITECTURE.md
    ├── NEXT_LEVEL_VISION.md
    ├── COMPLETE_STACK_QUICK_START.md
    └── ... (observability, integration, setup guides)
```

#### Active Integrations
✅ **Graphiti + Neo4j** - Knowledge graph with entity extraction
✅ **Langfuse** - Full observability with distributed tracing
✅ **Claude Code Hooks** - Auto-logging every conversation
✅ **Obsidian Integration** - Comprehensive blueprint (partially implemented)
✅ **Multi-Agent Orchestration** - Docker-based orchestrator with DB

#### The Challenge
- **Too many test files** (~20+ test_*.py files in root .claude)
- **Unclear service boundaries** - Which agent does what?
- **No central UI** - All configuration via file editing
- **Scattered documentation** - Hard to know where to start
- **No "optimize for AI" tooling** - Manual config tweaking

---

## Phase 1: Housekeeping & Cleanup (Tonight - 2 hours)

### Goal
Clean up the current directory structure and establish clear boundaries.

### Tasks

#### 1.1 Archive Test Files
```bash
mkdir -p .claude/archive/tests-pre-refactor
mv .claude/check_*.py .claude/archive/tests-pre-refactor/
mv .claude/test_*.py .claude/archive/tests-pre-refactor/
mv .claude/fetch_*.py .claude/archive/tests-pre-refactor/
mv .claude/extract_*.py .claude/archive/tests-pre-refactor/
mv .claude/verify_*.py .claude/archive/tests-pre-refactor/
```

#### 1.2 Consolidate Documentation
```bash
mkdir -p .claude/docs/archive
# Keep only these in root:
# - README.md
# - ARCHITECTURE.md
# - NEXT_LEVEL_VISION.md
# Move the rest to docs/
mv .claude/*_COMPLETE.md .claude/docs/archive/
mv .claude/*_SETUP*.md .claude/docs/setup/
mv .claude/*_GUIDE*.md .claude/docs/guides/
```

#### 1.3 Organize Scripts by Purpose
```bash
mkdir -p .claude/scripts/{graphiti,langfuse,obsidian,testing}
# Move operational scripts to appropriate folders
```

#### 1.4 Create Service Inventory
Document what each service actually does:

**File to create:** `.claude/SERVICE_INVENTORY.md`

---

## Phase 2: Service Renaming & Clarity (Week 1)

### Goal
Make service names crystal clear and eliminate confusion.

### Current Services → Renamed Services

#### Agents (Keep These Names)
1. ✅ **OBSERVABILITY_AGENT** - Good name
2. ✅ **GRAPHITI_AGENT** - Good name
3. ✅ **LANGFUSE_AGENT** - Good name
4. ✅ **OBSIDIAN_AGENT** - Good name
5. ✅ **INTEGRATION_ORCHESTRATOR** - Good name
6. 🔄 **AI_CODEBASE_OPTIMIZER** → Rename to **CODEBASE_OPTIMIZER_AGENT**
7. 🔄 **YOUTUBE_ANALYSIS_AGENT** → Move to separate project/archive

#### Skills (Reorganize)
1. ✅ **obsidian-vault** - Core skill, keep
2. ✅ **knowledge-sync** - Core skill, keep
3. 🔄 **obsidian-schema-generator** → Merge into obsidian-vault
4. 🔄 **revstar-quickstart-workflow** → Move to separate projects/
5. 🔄 **youtube-video-archiver** → Move to separate projects/

#### Hooks (Standardize Naming)
Current naming is inconsistent:
- `log_to_graphiti.py` ✅
- `log_to_langfuse.py` ✅
- `observe_to_graphiti.py` 🔄 → Rename to `log_to_graphiti_observe.py`
- etc.

**New Naming Convention:**
```
<lifecycle>_<action>_<target>.py

Examples:
- session_start_logger.py
- session_end_sync.py
- tool_use_pre_validator.py
- tool_use_post_logger.py
```

---

## Phase 3: Doc-Claude-Workbench Architecture (Weeks 2-4)

### Core Concept

**One flagship, living portfolio project** with:
1. **Knowledge graph backbone** (Neo4j episodes + SQL hooks)
2. **Admin agent** that keeps notes, backlinks, and bug history in sync
3. **Code-fix agent** that patches code + logs every change
4. **Dashboard UI** with graph viz, prompt editor, workflows, memories
5. **Obsidian integration** as the "human brain" layer

### Architecture Layers

#### A. Storage & Memory
```
┌─ Neo4j ─────────────────────────┐
│ - Episodes (session events)      │
│ - Entities (concepts, decisions) │
│ - Relationships (connections)    │
│ - Temporal index (time queries)  │
└──────────────────────────────────┘

┌─ SQL (Postgres/SQLite) ─────────┐
│ - Runs, agents, code patches     │
│ - Prompts, configs               │
│ - Structured events              │
└──────────────────────────────────┘

┌─ Files / Obsidian ──────────────┐
│ - bug.md, tasks.md, plans.md     │
│ - Agent configs (YAML/JSON)      │
│ - Daily notes & backlinks        │
└──────────────────────────────────┘
```

#### B. Agents

##### 1. Admin Agent
**Responsibilities:**
- Watches for new events (bugs, decisions, notes)
- Writes/updates Neo4j nodes/edges
- Writes/updates Obsidian markdown (bug.md, tasks.md, plans.md)
- Maintains change log for agents
- **Bilateral sync:** Obsidian ↔ KG

**Implementation:**
```python
# .claude/agents/admin-agent/
├── config.yaml
├── prompts/
│   ├── sync_obsidian_to_kg.md
│   ├── sync_kg_to_obsidian.md
│   └── generate_changelog.md
└── admin_agent.py
```

##### 2. Code-Fix Agent
**Responsibilities:**
- Takes: snippet + error / intention
- Returns: patched code + one-line summary
- Logs each change to SQL (time, file, diff summary)
- Updates Obsidian (bug.md / changes.md)

**Implementation:**
```python
# .claude/agents/code-fix-agent/
├── config.yaml
├── prompts/
│   ├── analyze_error.md
│   ├── generate_fix.md
│   └── log_change.md
└── code_fix_agent.py
```

##### 3. Future Agents (Optional)
- **Branding/Visual Agent** - nano banana + ComfyUI prompts
- **Refactor Agent** - "optimize codebase for AI"

#### C. UI / Dashboard

**Tech Stack Options:**
1. **Streamlit** - Fastest to prototype
2. **Flask + HTML/Tailwind** - More control
3. **Next.js + shadcn/ui** - Production-grade

**Dashboard Tabs:**

##### Tab 1 - Dashboard
- Today's focus
- Recent bugs, changes, tasks
- Hot graph (top 10 nodes/relationships)

##### Tab 2 - Agent Prompts / Config
- Edit prompts for all agents
- Editable via UI, stored in repo
- Live reload on save

##### Tab 3 - Workflows
- Dev workflow checklists:
  - "Start new feature"
  - "Debug issue"
  - "Refactor module"
- Each triggers one or more agents

##### Tab 4 - Memories
- Surfaces bug.md, tasks.md, plans.md
- Button: "Summarize last 7 days" (calls Admin agent)

##### Tab 5 - 3D Graph Viz (Future)
- V1: Neo4j Browser / Bloom
- V2: Three.js fancy 3D graph

---

## Phase 4: "Optimize for AI" Feature (Week 3)

### Goal
Create tools to automatically improve .claude configuration for AI consumption.

### Features

#### 1. Config Analyzer
Analyzes your .claude directory and suggests improvements:
- File organization issues
- Naming inconsistencies
- Missing documentation
- Circular dependencies
- Unused files

#### 2. Prompt Optimizer
- Scans all agent prompts
- Suggests improvements for clarity
- Checks token efficiency
- Validates variables and placeholders

#### 3. Schema Validator
- Validates all YAML/JSON configs
- Checks for required fields
- Suggests schema improvements

#### 4. Documentation Generator
- Auto-generates README files
- Creates API docs from code
- Builds dependency graphs

**Implementation:**
```python
# .claude/tools/optimize-for-ai/
├── analyzer.py
├── prompt_optimizer.py
├── schema_validator.py
└── doc_generator.py
```

---

## Phase 5: UI for .claude Configuration (Week 4)

### Goal
Create a web UI to quickly modify .claude configurations without editing files.

### Features

#### 1. Agent Manager
- List all agents
- Enable/disable agents
- Edit prompts inline
- View agent logs

#### 2. Hook Manager
- Visual hook lifecycle diagram
- Enable/disable specific hooks
- Edit hook scripts with syntax highlighting
- Test hooks with sample data

#### 3. Skill Manager
- Browse installed skills
- Configure skill settings
- View skill documentation
- Install new skills from templates

#### 4. Command Builder
- Create new slash commands via form
- Template selection
- Live preview
- Deploy instantly

#### 5. Settings Editor
- Global .claude settings
- Environment variables (encrypted)
- API key management
- Backup/restore configs

**Tech Stack:**
```
Frontend: React + Tailwind + shadcn/ui
Backend: FastAPI
Database: SQLite (for UI state)
File Watcher: watchdog (auto-reload on file changes)
```

**File Structure:**
```
.claude/ui/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json
├── backend/
│   ├── api/
│   ├── services/
│   └── main.py
└── docker-compose.yml
```

---

## Implementation Roadmap

### Tonight (2 hours) - Housekeeping ✅
- [x] Clean up test files → archive/
- [x] Organize documentation
- [x] Create service inventory
- [ ] Review Neo4j schema (2-3 Cypher queries)
- [ ] Export 1-2 screenshots for first Loom

### Week 1 (Dec 2-8) - Clarity & Foundation
**Days 1-2:** Service Renaming
- [ ] Rename agents following convention
- [ ] Standardize hook naming
- [ ] Reorganize skills

**Days 3-4:** Admin Agent
- [ ] Implement basic admin agent
- [ ] Set up bilateral sync (Obsidian ↔ Neo4j)
- [ ] Test with bug.md, tasks.md, plans.md

**Days 5-7:** Testing & Documentation
- [ ] Test admin agent end-to-end
- [ ] Create updated SERVICE_INVENTORY.md
- [ ] Record Loom: "How my Admin agent syncs notes to KG"

### Week 2 (Dec 9-15) - Code-Fix Agent & Change Log
**Days 1-3:** Code-Fix Agent
- [ ] Implement code-fix agent
- [ ] Add SQL logging for changes
- [ ] Integrate with bug.md

**Days 4-5:** Dashboard UI (Basic)
- [ ] Set up Streamlit or Flask+Tailwind
- [ ] Create Tab 1: Dashboard (read-only)
- [ ] Create Tab 4: Memories (render markdown)

**Days 6-7:** Testing & Content
- [ ] Test code-fix agent workflow
- [ ] Record Loom: "Code-fix agent auto-logs its work"

### Week 3 (Dec 16-22) - Dashboard & Prompt Editor
**Days 1-3:** Dashboard Completion
- [ ] Tab 2: Prompt editor (editable)
- [ ] Tab 3: Workflows (buttons)
- [ ] Live reload on config changes

**Days 4-5:** "Optimize for AI" Tools
- [ ] Config analyzer
- [ ] Prompt optimizer
- [ ] Run on current .claude directory

**Days 6-7:** Polish & Content
- [ ] Fix issues found by optimizer
- [ ] Record Loom: "Walkthrough of dashboard + prompt editing"

### Week 4 (Dec 23-29) - Polish & Branding
**Days 1-2:** Nano Banana Branding
- [ ] Add logo, color palette
- [ ] Create agent avatar (ComfyUI)
- [ ] Apply branding to UI

**Days 3-4:** 3D Graph Experiment
- [ ] Set up Neo4j Browser view
- [ ] Optional: Experiment with Three.js

**Days 5-7:** Documentation & Content
- [ ] Write comprehensive README.md
- [ ] Frame as "Agentic dev workbench / portfolio piece"
- [ ] Record 2 Looms:
  - "Architecture overview"
  - "How this pattern maps to client environments"

---

## Content Strategy (No Pressure)

### Loom Schedule
**Week 1:** Admin agent syncing notes to KG (3-7 min)
**Week 2:** Code-fix agent auto-logging (3-7 min)
**Week 3:** Dashboard walkthrough (5-7 min)
**Week 4:** Architecture overview + client mapping (7-10 min)

### Optional: Social Media
- Post Loom links to LinkedIn
- Short Twitter threads with screenshots
- Hashnode article: "Building My AI Second Brain"

**Rule:** Only create content when you're already excited. No forcing it.

---

## Success Metrics

### Technical Metrics
- [ ] All agents working with <3s response time
- [ ] 95%+ uptime for Neo4j, Langfuse, Obsidian sync
- [ ] <100ms UI response time
- [ ] Zero data loss in bilateral sync

### Business Metrics
- [ ] 4 high-quality Looms completed
- [ ] 1 comprehensive README for pitch
- [ ] 1 working demo environment (can show clients)
- [ ] Clear "before/after" story for consulting

### Personal Metrics
- [ ] Daily use of workbench for own projects
- [ ] Obsidian notes actually staying in sync
- [ ] Bug tracking actually working
- [ ] Feeling proud to show this off

---

## Migration Plan from Current Setup

### What to Keep
✅ All hooks (rename/reorganize)
✅ Graphiti, Langfuse, Obsidian integrations
✅ Core agents (Observability, Graphiti, Langfuse, Obsidian)
✅ ARCHITECTURE.md, NEXT_LEVEL_VISION.md

### What to Archive
📦 Test files (move to archive/)
📦 Old documentation (move to docs/archive/)
📦 YouTube analysis (separate project)
📦 RevStar workflow (separate project)

### What to Refactor
🔄 Agent naming conventions
🔄 Hook naming conventions
🔄 Skills organization
🔄 Documentation structure

---

## Risk Mitigation

### Technical Risks
**Risk:** Bilateral sync creates data conflicts
**Mitigation:** Implement conflict resolution strategy, use timestamps

**Risk:** UI adds complexity, slows down workflow
**Mitigation:** Keep file-based config as primary, UI as optional overlay

**Risk:** Too many agents, system becomes slow
**Mitigation:** Profile performance, implement lazy loading

### Scope Risks
**Risk:** Feature creep, never ship
**Mitigation:** Stick to 4-week roadmap, cut features aggressively

**Risk:** Trying to make it perfect
**Mitigation:** Ship MVP each week, iterate based on dogfooding

---

## Open Questions & Decisions Needed

### Architecture Decisions
1. **SQL Database:** SQLite vs Postgres?
   - Recommendation: **SQLite** for simplicity

2. **UI Framework:** Streamlit vs Flask vs Next.js?
   - Recommendation: **Streamlit** for speed, migrate to Next.js later if needed

3. **Admin Agent Trigger:** Hook-based vs cron-based?
   - Recommendation: **Hook-based** for real-time, optional cron for cleanup

### Configuration Decisions
4. **Where should bugs.md, tasks.md, plans.md live?**
   - Option A: `.claude/memories/`
   - Option B: Obsidian vault with sync
   - Recommendation: **Both** - bilateral sync

5. **How to handle conflicts in bilateral sync?**
   - Recommendation: Obsidian is source of truth for manual edits, KG is source of truth for automated extractions

### User Experience Decisions
6. **Should UI be always-on or on-demand?**
   - Recommendation: **On-demand** - launch with `claude-ui` command

7. **Should we use the existing orchestrator/ or build new?**
   - Recommendation: **Refactor existing** - it's already Docker-based

---

## Next Steps (Choose Your Path)

### Path A: Quick Win Tonight (2 hours)
1. Run housekeeping tasks
2. Review Neo4j with 2-3 Cypher queries
3. Export screenshots for first content piece
4. **Outcome:** Clean foundation, ready to build

### Path B: Full Week 1 Push (This Week)
1. Complete housekeeping
2. Service renaming
3. Implement Admin Agent
4. **Outcome:** Working bilateral sync, first Loom ready

### Path C: All-In 4-Week Sprint
1. Follow full roadmap
2. Ship MVP each week
3. Create content along the way
4. **Outcome:** Production-ready workbench, portfolio piece, consulting demo

---

## Conclusion

You already have 80% of the pieces. This plan is about:
1. **Organizing** what you have
2. **Clarifying** service boundaries
3. **Adding** the missing 20% (Admin Agent, Code-Fix Agent, UI)
4. **Dogfooding** it daily
5. **Showcasing** it for consulting

**The killer pitch:** *"I built and use this workbench daily. It's the same pattern I'll adapt for your org."*

---

**Ready to start?** Let's begin with Phase 1 housekeeping tonight.

**Questions? Feedback?** Let's discuss and adjust the plan.

---

**Version:** 1.0
**Last Updated:** 2025-12-01
**Next Review:** After Week 1 completion
