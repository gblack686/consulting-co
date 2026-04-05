# Obsidian Folder Tree - Doc-Claude-Workbench

**Vault Location:** `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\`
**Project-Specific Path:** `claude-logs/consulting-co/`

---

## Complete Folder Tree

```
Gbautomation/                              # Your main Obsidian vault
│
├── obsidian-docs/                         # Your existing templates (keep as-is)
│   └── Template-Library-Index.md
│
└── claude-logs/                           # New: All Claude Code workbench logs
    │
    └── consulting-co/                     # Project-specific namespace
        │
        ├── templates/                     # Template definitions
        │   ├── claude-session.md          # Session note template
        │   ├── claude-daily.md            # Daily summary template
        │   ├── bug-entry.md               # Individual bug template
        │   ├── task-entry.md              # Individual task template
        │   └── plan-entry.md              # Individual plan template
        │
        ├── sessions/                      # 🤖 Auto-generated session notes
        │   ├── 2025-12-01/
        │   │   ├── session-abc123.md      # Individual session
        │   │   ├── session-def456.md
        │   │   └── session-ghi789.md
        │   ├── 2025-12-02/
        │   │   └── session-jkl012.md
        │   └── README.md                  # Explains this directory
        │
        ├── daily/                         # 🤖 Auto-generated daily summaries
        │   ├── 2025-12-01.md              # Daily note with all sessions
        │   ├── 2025-12-02.md
        │   ├── 2025-12-03.md
        │   └── README.md                  # Explains this directory
        │
        ├── bugs/                          # 🐛 Bug tracking
        │   ├── bug.md                     # 📌 Master bug list (main file)
        │   ├── active/                    # Active bugs (optional detail)
        │   │   ├── BUG-001-auth-error.md
        │   │   └── BUG-002-api-timeout.md
        │   ├── resolved/                  # Resolved bugs (archive)
        │   │   ├── BUG-000-initial.md
        │   │   └── 2025-12/               # Resolved by month
        │   └── README.md
        │
        ├── tasks/                         # ⚡ Task management
        │   ├── tasks.md                   # 📌 Master task list (main file)
        │   ├── in-progress/               # Active tasks (optional detail)
        │   │   ├── TASK-001-obsidian-templates.md
        │   │   └── TASK-002-neo4j-review.md
        │   ├── completed/                 # Completed tasks (archive)
        │   │   └── 2025-12/               # Completed by month
        │   └── README.md
        │
        ├── plans/                         # 🎯 Planning & roadmaps
        │   ├── plans.md                   # 📌 Master plan list (main file)
        │   ├── active/                    # Current plans
        │   │   ├── PLAN-001-week1-foundation.md
        │   │   └── PLAN-002-admin-agent.md
        │   ├── completed/                 # Completed plans (archive)
        │   │   └── 2025-12/
        │   └── README.md
        │
        ├── decisions/                     # 📋 Architecture Decision Records (ADRs)
        │   ├── ADR-001-drop-langfuse.md
        │   ├── ADR-002-sqlite-events.md
        │   ├── ADR-003-haiku-enrichment.md
        │   ├── index.md                   # ADR index
        │   └── README.md
        │
        ├── learnings/                     # 💡 Knowledge notes & insights
        │   ├── graphiti-integration.md
        │   ├── obsidian-export-patterns.md
        │   ├── neo4j-queries.md
        │   ├── concepts/                  # Concept notes
        │   │   ├── knowledge-graphs.md
        │   │   ├── event-enrichment.md
        │   │   └── bilateral-sync.md
        │   └── README.md
        │
        ├── entities/                      # 🔗 Entity reference notes (from KG)
        │   ├── _index.md                  # Entity index
        │   ├── people/
        │   ├── concepts/
        │   │   ├── Graphiti.md
        │   │   ├── Neo4j.md
        │   │   └── SQLite.md
        │   ├── technologies/
        │   │   ├── Haiku.md
        │   │   ├── Python.md
        │   │   └── Obsidian.md
        │   ├── decisions/                 # Decision entities
        │   └── README.md
        │
        ├── meetings/                      # 👥 Meeting notes (manual)
        │   ├── 2025-12-01-sprint-planning.md
        │   └── README.md
        │
        ├── attachments/                   # 📎 Images, files, etc.
        │   ├── screenshots/
        │   │   ├── neo4j-graph-2025-12-01.png
        │   │   └── dashboard-2025-12-01.png
        │   └── diagrams/
        │       └── architecture-2025-12-01.excalidraw
        │
        └── README.md                      # Main project README
```

---

## Core Files Breakdown

### 📌 Master Files (These are your main dashboards)

**1. `bugs/bug.md`** - Master Bug Tracker
- Lists all bugs (active + resolved)
- Auto-updated by Code-Fix Agent
- Manually editable
- Links to detailed bug notes

**2. `tasks/tasks.md`** - Master Task Tracker
- Lists all tasks (pending, in-progress, completed)
- Auto-updated by Admin Agent
- Manually editable
- Links to detailed task notes

**3. `plans/plans.md`** - Master Plan List
- Current sprint/roadmap
- Next sprint planning
- Backlog items
- Auto-updated by Admin Agent
- Links to detailed plan notes

### 🤖 Auto-Generated Directories

**1. `sessions/`**
- One markdown file per Claude Code session
- Generated by `obsidian_exporter.py`
- Frontmatter with session metadata
- Timeline of tools used
- Entities discovered
- Performance metrics

**2. `daily/`**
- One markdown file per day
- Aggregates all sessions from that day
- Summary statistics
- Top entities
- Links to all session notes

### ✍️ Manual Directories

**3. `decisions/`**
- Architecture Decision Records (ADRs)
- Format: ADR-XXX-title.md
- Manually created (or prompted by agents)
- Follows standard ADR template

**4. `learnings/`**
- Knowledge notes about concepts
- How-to guides
- Patterns discovered
- Manually created

**5. `meetings/`**
- Meeting notes
- Manually created
- Use meeting template from your template library

---

## File Naming Conventions

### Sessions
```
Format: session-{session_id}.md
Example: session-abc123def456.md
Location: sessions/YYYY-MM-DD/
```

### Daily Notes
```
Format: YYYY-MM-DD.md
Example: 2025-12-01.md
Location: daily/
```

### Bugs
```
Master: bugs/bug.md
Detail: bugs/active/BUG-{number}-{slug}.md
Example: bugs/active/BUG-001-auth-timeout.md
Archive: bugs/resolved/YYYY-MM/BUG-{number}-{slug}.md
```

### Tasks
```
Master: tasks/tasks.md
Detail: tasks/in-progress/TASK-{number}-{slug}.md
Example: tasks/in-progress/TASK-001-obsidian-templates.md
Archive: tasks/completed/YYYY-MM/TASK-{number}-{slug}.md
```

### Plans
```
Master: plans/plans.md
Detail: plans/active/PLAN-{number}-{slug}.md
Example: plans/active/PLAN-001-week1-foundation.md
Archive: plans/completed/YYYY-MM/PLAN-{number}-{slug}.md
```

### Decisions (ADRs)
```
Format: ADR-{number}-{slug}.md
Example: ADR-001-drop-langfuse.md
Location: decisions/
```

### Learnings
```
Format: {slug}.md
Example: graphiti-integration.md
Location: learnings/ or learnings/concepts/
```

### Entities
```
Format: {Entity-Name}.md
Example: Graphiti.md, Neo4j.md
Location: entities/{type}/
```

---

## Frontmatter Standards

### Session Notes
```yaml
---
tags: [agent-session, consulting-co]
session_id: abc123def456
source_app: consulting-co
model: claude-sonnet-4-5
date: 2025-12-01
time: 14:30:00
status: completed
duration_seconds: 245
tools_used: 8
entities_discovered: 5
performance: fast
---
```

### Daily Notes
```yaml
---
tags: [daily-note, agent-activity, consulting-co]
date: 2025-12-01
sessions: 5
total_tools: 42
total_entities: 23
total_duration_seconds: 1250
avg_performance: fast
---
```

### Bugs
```yaml
---
tags: [bug, tracking]
bug_id: BUG-001
title: Authentication timeout on startup
status: active
priority: high
date_created: 2025-12-01
date_resolved: null
file: .claude/hooks/session_start.py
logged_by: Code-Fix Agent
---
```

### Tasks
```yaml
---
tags: [task, tracking]
task_id: TASK-001
title: Create Obsidian templates
status: in-progress
priority: high
date_created: 2025-12-01
date_completed: null
assigned_to: Greg
logged_by: Admin Agent
---
```

### Plans
```yaml
---
tags: [plan, roadmap]
plan_id: PLAN-001
title: Week 1 - Foundation
status: active
timeframe: 2025-12-01 to 2025-12-07
date_created: 2025-12-01
logged_by: Admin Agent
---
```

### Decisions (ADRs)
```yaml
---
tags: [decision, architecture, adr]
adr_id: ADR-001
title: Drop Langfuse for SQLite + Haiku
status: accepted
date: 2025-12-01
deciders: [Greg]
---
```

### Learnings
```yaml
---
tags: [learning, knowledge]
topic: Graphiti Integration
date: 2025-12-01
related: [Neo4j, Knowledge Graphs]
---
```

### Entities
```yaml
---
tags: [entity, concept]
entity_type: Technology
connections: 15
first_mentioned: 2025-11-15
last_updated: 2025-12-01
source: Neo4j Knowledge Graph
---
```

---

## Linking Strategy

### Backlinks
All notes should link bidirectionally:
- Sessions link to daily notes
- Sessions link to entities discovered
- Bugs link to sessions where found
- Tasks link to related sessions
- Plans link to related tasks

### Example Session Note Links
```markdown
## Links
- [[2025-12-01|Today's Daily Note]]
- [[Graphiti]] - Entity discovered
- [[Neo4j]] - Entity discovered
- [[BUG-001-auth-timeout]] - Bug found
- [[session-def456|← Previous Session]]
- [[session-ghi789|Next Session →]]
```

### Example Entity Note Links
```markdown
## Mentioned In
- [[session-abc123]] (2025-12-01)
- [[session-def456]] (2025-12-01)
- [[ADR-002-sqlite-events]] (Decision)

## Related Entities
- [[SQLite]]
- [[Haiku]]
- [[Obsidian]]
```

---

## Tags Strategy

### Core Tags
```
#agent-session      - All session notes
#daily-note        - Daily summaries
#bug               - All bugs
#task              - All tasks
#plan              - All plans
#decision / #adr   - Architecture decisions
#learning          - Knowledge notes
#entity            - Entity reference notes
```

### Status Tags
```
#status/active
#status/completed
#status/in-progress
#status/resolved
#status/archived
```

### Priority Tags
```
#priority/high
#priority/medium
#priority/low
```

### Source Tags
```
#source/agent        - Generated by agent
#source/manual       - Created manually
#source/neo4j        - From knowledge graph
```

### Project Tags
```
#consulting-co       - All notes for this project
```

---

## README Files Content

### `claude-logs/consulting-co/README.md`
```markdown
# Claude Code Workbench - consulting-co

Automated observability and knowledge management for the consulting-co project.

## Structure
- `sessions/` - Auto-generated session notes
- `daily/` - Daily summaries
- `bugs/` - Bug tracking (see bug.md)
- `tasks/` - Task management (see tasks.md)
- `plans/` - Planning & roadmaps (see plans.md)
- `decisions/` - Architecture Decision Records
- `learnings/` - Knowledge notes
- `entities/` - Entity references from knowledge graph

## Key Files
- **[bug.md](bugs/bug.md)** - Master bug tracker
- **[tasks.md](tasks/tasks.md)** - Master task list
- **[plans.md](plans/plans.md)** - Master plan list

## Auto-Generation
Session notes are automatically generated by:
- Hook: `.claude/hooks/stop.py`
- Script: `.claude/obsidian/scripts/obsidian_exporter.py`
- Config: `.claude/obsidian/config/obsidian.yaml`
```

### Per-Directory READMEs
Each directory has a README.md explaining:
- Purpose of the directory
- File naming conventions
- Auto-generated vs manual
- How to use the files

---

## Dataview Queries (Optional)

If you install the Dataview plugin, add these to your daily note template:

### Active Bugs
```dataview
TABLE status, priority, file, date_created
FROM "claude-logs/consulting-co/bugs"
WHERE contains(tags, "bug") AND status = "active"
SORT priority DESC, date_created DESC
```

### In-Progress Tasks
```dataview
TABLE status, priority, date_created
FROM "claude-logs/consulting-co/tasks"
WHERE contains(tags, "task") AND status = "in-progress"
SORT priority DESC, date_created DESC
```

### Recent Sessions
```dataview
TABLE model, tools_used, entities_discovered, performance
FROM "claude-logs/consulting-co/sessions"
WHERE contains(tags, "agent-session")
SORT date DESC
LIMIT 10
```

---

## Graph View

Your Obsidian graph will show:
- **Center nodes:** Master files (bug.md, tasks.md, plans.md)
- **Session clusters:** Daily notes linking to multiple sessions
- **Entity clusters:** Entities linking to sessions where mentioned
- **Decision trails:** ADRs linking to related sessions and entities

---

## Storage Estimates

**Per Session Note:** ~5-10 KB
**Per Daily Note:** ~15-30 KB
**Per Bug/Task/Plan:** ~2-5 KB

**Monthly Estimate (50 sessions):**
- Sessions: ~500 KB
- Daily notes: ~600 KB
- Bugs/Tasks/Plans: ~100 KB
- **Total:** ~1.5 MB/month

**Yearly Estimate:** ~18 MB

---

## Next Steps

### Tonight (TONIGHT-PLAN.md)
1. Create this folder structure in Gbautomation vault
2. Create 5 core templates
3. Create master files (bug.md, tasks.md, plans.md)
4. Configure obsidian.yaml to point to this structure

### Week 1
5. Test auto-generation with dummy session
6. Verify backlinks work correctly
7. Add README.md files to each directory

### Week 2
8. Implement Admin Agent for auto-updates
9. Set up bilateral sync (Obsidian ↔ Neo4j)
10. Create entity reference notes from KG

---

**This structure supports:**
- ✅ Auto-generation (sessions, daily)
- ✅ Manual curation (bugs, tasks, plans, decisions, learnings)
- ✅ Bilateral sync (Obsidian ↔ Neo4j)
- ✅ Knowledge graph integration (entities)
- ✅ Backlinks and relationships
- ✅ Tag-based organization
- ✅ Future Dataview queries
- ✅ Clean separation of concerns

**Ready to create this structure?** Start with TONIGHT-PLAN.md!
