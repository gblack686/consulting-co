# Obsidian Folder Tree V3 - Clarified Purpose

**Vault Location:** `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\`

---

## 🎯 Purpose Clarification

### What Goes in Obsidian vs. What Stays in `.claude/`

**Obsidian is for:**
- ✅ **Reading & reviewing** - Human-readable docs you want to search/link/review
- ✅ **Cross-project knowledge** - Shared agents, resources, learnings
- ✅ **Runtime logs** - Session notes, daily summaries (auto-generated)
- ✅ **Project snapshots** - What agents/commands/skills THIS project uses
- ✅ **Tracking** - Bugs, tasks, plans (master files)

**`.claude/` directory is for:**
- 🔧 **Execution** - Actual Python scripts, configs, hooks (runtime files)
- 🔧 **Source of truth** - Live code that Claude Code executes
- 🔧 **Version controlled** - Git commits, branches, deployments

**The Relationship:**
```
.claude/                          →  Obsidian claude/
├── hooks/send_event.py          →  core/hooks/send-event.md (docs)
├── agents/admin-agent/          →  core/agents/admin-agent.md (docs)
├── prompts/sync.md              →  core/prompts/admin-sync.md (reference copy)
└── settings.local.json          →  (not in Obsidian - too technical)
```

---

## Reorganized Structure

```
Gbautomation/                              # Your main Obsidian vault
│
└── claude/                                # Claude workbench documentation
    │
    ├── global/                            # 🌍 Cross-project resources
    │   │
    │   ├── agents/                        # Reusable agent library
    │   │   ├── _index.md                  # All available agents
    │   │   ├── admin-agent.md             # Documented agent pattern
    │   │   ├── code-fix-agent.md
    │   │   ├── observability-agent.md
    │   │   ├── graphiti-agent.md
    │   │   └── README.md
    │   │
    │   ├── skills/                        # Reusable skill library
    │   │   ├── _index.md
    │   │   ├── knowledge-sync.md
    │   │   ├── obsidian-vault.md
    │   │   └── README.md
    │   │
    │   ├── commands/                      # Reusable command library
    │   │   ├── _index.md
    │   │   ├── obsidian-commands.md
    │   │   ├── scoping-commands.md
    │   │   └── README.md
    │   │
    │   ├── prompts/                       # Reusable prompt library
    │   │   ├── _index.md
    │   │   ├── agent-prompts/
    │   │   │   ├── admin-agent-sync.md
    │   │   │   └── code-fix-analysis.md
    │   │   ├── command-prompts/
    │   │   └── skill-prompts/
    │   │
    │   ├── workflows/                     # Reusable ADWS patterns
    │   │   ├── _index.md
    │   │   ├── bug-fix-workflow.md
    │   │   ├── feature-development.md
    │   │   └── weekly-review.md
    │   │
    │   └── resources/                     # Documentation library
    │       ├── table-of-contents.md       # Master index
    │       ├── quickstart/
    │       ├── guides/
    │       ├── architecture/
    │       ├── integrations/
    │       ├── troubleshooting/
    │       ├── examples/
    │       ├── external-links/
    │       └── best-practices/
    │
    └── projects/                          # 📁 Per-project namespaces
        │
        ├── consulting-co/                 # This project
        │   │
        │   ├── overview.md                # 📌 Project snapshot
        │   │   # What this project is
        │   │   # Tech stack
        │   │   # Goals
        │   │   # Status
        │   │
        │   ├── .claude-mirror/            # Mirror of .claude/ structure
        │   │   ├── agents/                # Which agents THIS project uses
        │   │   │   ├── _active.md         # List of active agents
        │   │   │   ├── admin-agent.md     # Project-specific config notes
        │   │   │   └── code-fix-agent.md
        │   │   ├── skills/                # Which skills THIS project uses
        │   │   │   ├── _active.md
        │   │   │   └── knowledge-sync.md
        │   │   ├── commands/              # Which commands THIS project has
        │   │   │   ├── _active.md
        │   │   │   └── obsidian.md
        │   │   └── README.md
        │   │
        │   ├── logs/                      # 🤖 Runtime logs (auto-generated)
        │   │   ├── sessions/
        │   │   │   ├── 2025-12-01/
        │   │   │   │   ├── session-abc123.md
        │   │   │   │   └── session-def456.md
        │   │   │   └── README.md
        │   │   ├── daily/
        │   │   │   ├── 2025-12-01.md
        │   │   │   └── README.md
        │   │   └── README.md
        │   │
        │   ├── tracking/                  # 📋 Manual tracking
        │   │   ├── bugs.md                # 📌 Master bug tracker
        │   │   ├── tasks.md               # 📌 Master task list
        │   │   ├── plans.md               # 📌 Master roadmap
        │   │   ├── bugs/                  # Bug details (optional)
        │   │   │   ├── active/
        │   │   │   └── resolved/
        │   │   ├── tasks/                 # Task details (optional)
        │   │   │   ├── in-progress/
        │   │   │   └── completed/
        │   │   └── plans/                 # Plan details (optional)
        │   │       ├── active/
        │   │       └── completed/
        │   │
        │   ├── decisions/                 # 📋 ADRs
        │   │   ├── _index.md
        │   │   ├── ADR-001-drop-langfuse.md
        │   │   ├── ADR-002-sqlite-events.md
        │   │   └── README.md
        │   │
        │   ├── learnings/                 # 💡 Project-specific knowledge
        │   │   ├── graphiti-integration.md
        │   │   ├── obsidian-patterns.md
        │   │   └── README.md
        │   │
        │   ├── entities/                  # 🔗 From Neo4j KG (auto-generated)
        │   │   ├── _index.md
        │   │   ├── concepts/
        │   │   │   ├── Graphiti.md
        │   │   │   └── Neo4j.md
        │   │   ├── technologies/
        │   │   └── README.md
        │   │
        │   ├── docs/                      # 📄 Project-specific docs
        │   │   ├── setup-guide.md
        │   │   ├── deployment.md
        │   │   └── README.md
        │   │
        │   ├── attachments/               # 📎 Screenshots, diagrams
        │   │   ├── screenshots/
        │   │   └── diagrams/
        │   │
        │   └── templates/                 # Note templates
        │       ├── session.md
        │       ├── daily.md
        │       ├── bug.md
        │       └── task.md
        │
        ├── quickstart-nexus/              # Another project (example)
        │   ├── overview.md
        │   ├── .claude-mirror/
        │   ├── logs/
        │   ├── tracking/
        │   └── ...
        │
        └── _index.md                      # List of all projects
```

---

## Key Concepts

### 1. **`global/`** - Cross-Project Library

**Purpose:** Reusable patterns that apply to ALL projects

**What goes here:**
- Agent documentation (how to use admin-agent in any project)
- Skill documentation (knowledge-sync pattern)
- Command documentation (obsidian commands)
- Prompt library (reusable prompts)
- Workflow patterns (ADWS templates)
- Resources (guides, tutorials, external links)

**Example: `global/agents/admin-agent.md`**
```markdown
# Admin Agent (Global Pattern)

## Overview
Reusable agent for bilateral Obsidian ↔ Neo4j sync.

## Capabilities
[Generic capabilities across all projects]

## Configuration Template
[How to configure for any project]

## Projects Using This
- [[projects/consulting-co/overview#agents|consulting-co]]
- [[projects/quickstart-nexus/overview#agents|quickstart-nexus]]

## Examples
[Generic examples]
```

---

### 2. **`projects/{project-name}/`** - Per-Project Namespace

**Purpose:** Project-specific implementation, logs, and tracking

#### **`overview.md`** - Project Snapshot
```markdown
---
tags: [project, consulting-co]
status: active
tech_stack: [Python, Neo4j, SQLite, Haiku, Obsidian]
---

# consulting-co Project

## Overview
Doc-claude-workbench - Flagship agentic development platform.

## Tech Stack
- Python 3.10+
- SQLite (events.db)
- Neo4j + Graphiti
- Haiku enrichment
- Obsidian export

## Active Agents
- [[.claude-mirror/agents/admin-agent|Admin Agent]] - Bilateral sync
- [[.claude-mirror/agents/code-fix-agent|Code-Fix Agent]] - Error analysis

## Active Skills
- [[.claude-mirror/skills/knowledge-sync|Knowledge Sync]]
- [[.claude-mirror/skills/obsidian-vault|Obsidian Vault]]

## Active Commands
- `/obsidian:daily` - Generate daily summary
- `/obsidian:export` - Export session
- `/scoping:analyze-transcripts` - Analyze call notes

## Project Structure
See: [[.claude-mirror/README|.claude Mirror]]

## Key Files
- [[tracking/bugs|bugs.md]] - Master bug tracker
- [[tracking/tasks|tasks.md]] - Master task list
- [[tracking/plans|plans.md]] - Master roadmap

## Status
🟢 Active development
- Week 1: Foundation ✅
- Week 2: Admin Agent (in progress)

## Links
- Repo: `C:/Users/gblac/OneDrive/Desktop/consulting-co/`
- Obsidian: This vault
- Neo4j: `bolt://localhost:7687`
```

---

#### **`.claude-mirror/`** - Snapshot of `.claude/` Structure

**Purpose:** Show what THIS project's `.claude/` directory contains

**NOT a copy of the code** - Just documentation/reference

**Structure:**
```
.claude-mirror/
├── agents/
│   ├── _active.md              # "This project uses: admin-agent, code-fix-agent"
│   ├── admin-agent.md          # Project-specific notes about this agent
│   └── code-fix-agent.md
│
├── skills/
│   ├── _active.md              # "This project uses: knowledge-sync"
│   └── knowledge-sync.md       # How we use it in THIS project
│
├── commands/
│   ├── _active.md              # "This project has: /obsidian:*, /scoping:*"
│   ├── obsidian.md
│   └── scoping.md
│
└── README.md                   # Overview of .claude/ structure
```

**Example: `.claude-mirror/agents/_active.md`**
```markdown
# Active Agents - consulting-co

## Installed Agents
- ✅ [[admin-agent]] - Bilateral sync (configured)
- ✅ [[code-fix-agent]] - Error analysis (configured)
- ⚪ [[observability-agent]] - Available but not active

## Configuration
Location: `C:/Users/gblac/.../consulting-co/.claude/agents/`

## See Also
- [[../overview#agents|Project Overview]]
- [[../../global/agents/_index|All Available Agents]]
```

**Example: `.claude-mirror/agents/admin-agent.md`**
```markdown
# Admin Agent - consulting-co Config

## How We Use It
This project uses admin-agent for:
- Daily summary generation
- Auto-update bugs.md, tasks.md, plans.md
- Sync entities from Neo4j → Obsidian

## Configuration
File: `.claude/agents/admin-agent/config.yaml`

```yaml
triggers:
  - stop_hook
  - daily_cron

sync:
  obsidian_to_neo4j: true
  neo4j_to_obsidian: true

files:
  bug_tracker: tracking/bugs.md
  task_tracker: tracking/tasks.md
  plan_tracker: tracking/plans.md
```

## Customizations
- We disabled entity notes (too noisy)
- We run daily sync at 11pm
- We filter out test sessions

## Prompts Used
- [[../../global/prompts/agent-prompts/admin-agent-sync|Standard sync prompt]]
- Custom: See `.claude/agents/admin-agent/prompts/`

## See Also
- [[../../global/agents/admin-agent|Global Admin Agent Docs]]
- [[../overview#agents|Project Agents]]
```

---

#### **`logs/`** - Auto-Generated Runtime Logs

**Purpose:** Session notes and daily summaries (auto-generated by hooks)

**What goes here:**
- `sessions/` - One .md file per Claude session
- `daily/` - One .md file per day (aggregated)

**Note:** This is ONLY for logs. No manual editing needed.

---

#### **`tracking/`** - Manual Tracking

**Purpose:** Master files for bugs, tasks, plans

**Structure:**
```
tracking/
├── bugs.md                    # 📌 Master bug tracker (primary file)
├── tasks.md                   # 📌 Master task list (primary file)
├── plans.md                   # 📌 Master roadmap (primary file)
├── bugs/                      # Optional detail notes
│   ├── active/
│   └── resolved/
├── tasks/                     # Optional detail notes
│   ├── in-progress/
│   └── completed/
└── plans/                     # Optional detail notes
    ├── active/
    └── completed/
```

**Key Insight:** Most people only need the 3 master files. The subdirectories are optional for complex projects.

---

#### **`decisions/`** - ADRs

**Purpose:** Architecture Decision Records for THIS project

---

#### **`learnings/`** - Project Knowledge

**Purpose:** Project-specific learnings (not reusable across projects)

Example: `graphiti-integration.md` specific to how consulting-co uses Graphiti

---

#### **`entities/`** - Auto-Generated Entity Notes

**Purpose:** Entity reference notes from Neo4j (auto-generated)

Only if you enable entity note generation (can be noisy).

---

#### **`docs/`** - Project Documentation

**Purpose:** Project-specific setup guides, deployment docs, etc.

Different from `global/resources/` which is cross-project.

---

#### **`attachments/`** - Media Files

Screenshots, diagrams, etc.

---

#### **`templates/`** - Note Templates

Templates specific to THIS project (if different from global templates).

---

## Information Architecture

### Global vs. Project

| Content | Global | Project |
|---------|--------|---------|
| Agent documentation | ✅ Pattern/usage | Project-specific config |
| Skill documentation | ✅ How it works | How we use it here |
| Command documentation | ✅ Command reference | Commands we have |
| Prompts | ✅ Reusable library | Custom prompts (if any) |
| Workflows | ✅ ADWS templates | Custom workflows |
| Resources/Guides | ✅ All docs here | N/A |
| Session logs | ❌ | ✅ Auto-generated |
| Bug/Task tracking | ❌ | ✅ bugs.md, tasks.md |
| ADRs | ❌ | ✅ Per-project decisions |
| Learnings | ❌ | ✅ Per-project knowledge |

---

## Example: Finding Information

### "How do I use the Admin Agent?"

**Path 1: Learn the pattern (global)**
```
global/agents/admin-agent.md
  → Capabilities, configuration, examples
  → Links to guide: global/resources/guides/bilateral-sync-guide.md
```

**Path 2: See how consulting-co uses it (project)**
```
projects/consulting-co/.claude-mirror/agents/admin-agent.md
  → How we configured it
  → What we customized
  → Links back to global docs
```

---

### "What agents does consulting-co use?"

**Path 1: Project overview**
```
projects/consulting-co/overview.md
  → Active Agents section
  → Links to .claude-mirror/agents/
```

**Path 2: .claude-mirror**
```
projects/consulting-co/.claude-mirror/agents/_active.md
  → List of installed agents
  → Links to each agent's config notes
```

---

### "Show me all available agents across all projects"

**Path: Global index**
```
global/agents/_index.md
  → All documented agents
  → Which projects use them
  → Links to each agent's docs
```

---

## File Naming Conventions

### Global Files
```
global/agents/admin-agent.md           # Pattern name (kebab-case)
global/prompts/agent-prompts/sync.md   # Descriptive name
global/resources/guides/setup-neo4j.md # Action-oriented name
```

### Project Files
```
projects/consulting-co/overview.md              # overview.md always
projects/consulting-co/logs/sessions/session-abc123.md
projects/consulting-co/tracking/bugs.md         # Master file
projects/consulting-co/decisions/ADR-001-title.md
```

### Index Files
```
_index.md    # Catalog/directory of items
_active.md   # What's currently active/installed
README.md    # Directory explanation
```

---

## Frontmatter Standards

### Global Documentation
```yaml
---
tags: [global, agent, admin]
type: pattern
reusable: true
difficulty: intermediate
---
```

### Project Overview
```yaml
---
tags: [project, consulting-co]
status: active
tech_stack: [Python, Neo4j, SQLite]
created: 2025-12-01
---
```

### Project .claude-mirror Notes
```yaml
---
tags: [config, agent, consulting-co]
component: admin-agent
location: .claude/agents/admin-agent/
last_updated: 2025-12-01
---
```

### Session Logs
```yaml
---
tags: [session, auto-generated]
session_id: abc123
project: consulting-co
date: 2025-12-01
---
```

---

## Linking Strategy

### From Project to Global
```markdown
# Admin Agent - consulting-co

See: [[../../global/agents/admin-agent|Global Admin Agent Docs]]
```

### From Global to Projects
```markdown
# Admin Agent (Global)

## Projects Using This
- [[../projects/consulting-co/overview#agents|consulting-co]]
- [[../projects/quickstart-nexus/overview#agents|quickstart-nexus]]
```

### Cross-Project Links
```markdown
# consulting-co Overview

Similar project: [[../quickstart-nexus/overview|quickstart-nexus]]
```

---

## What About Actual Code?

**The `.claude/` directory in your project contains:**
- Actual Python scripts (hooks, agents)
- Actual YAML configs
- Actual prompt markdown files
- Actual settings

**The Obsidian `claude/` vault contains:**
- Documentation ABOUT those files
- References to where those files are
- How to use them
- Project-specific customizations
- Runtime logs (auto-generated)

**Example:**

**Actual Code:**
```
C:/Users/gblac/.../consulting-co/.claude/hooks/send_event.py
```

**Obsidian Documentation:**
```
Gbautomation/claude/global/resources/guides/hooks-guide.md
  → Explains what hooks are
  → Links to examples

Gbautomation/claude/projects/consulting-co/.claude-mirror/README.md
  → Lists which hooks THIS project has
  → Links to actual file location
```

---

## Storage Estimates

### Global (one-time)
- agents/: ~500 KB (10-20 agents)
- skills/: ~300 KB (5-10 skills)
- commands/: ~200 KB (10-20 commands)
- prompts/: ~400 KB (50+ prompts)
- workflows/: ~200 KB (10+ workflows)
- resources/: ~5 MB (comprehensive guides)
**Total:** ~6.5 MB (one-time setup)

### Per Project
- overview.md + .claude-mirror/: ~100 KB
- logs/: ~1.5 MB/month
- tracking/: ~50 KB
- decisions/: ~100 KB
- learnings/: ~200 KB
**Total:** ~2 MB + 1.5 MB/month

### Multiple Projects (3 projects)
- Global: 6.5 MB (shared)
- 3 Projects: 6 MB + 4.5 MB/month
**Total:** 12.5 MB + 4.5 MB/month

**Yearly:** ~67 MB for 3 active projects

---

## Migration Steps

### Step 1: Create Global Structure
```bash
cd ~/OneDrive/Desktop/obsidian/Gbautomation
mkdir -p claude/global/{agents,skills,commands,prompts,workflows,resources}
```

### Step 2: Create Project Structure
```bash
mkdir -p claude/projects/consulting-co/{.claude-mirror,logs,tracking,decisions,learnings,docs,attachments,templates}
```

### Step 3: Create Index Files
```bash
touch claude/global/agents/_index.md
touch claude/global/resources/table-of-contents.md
touch claude/projects/consulting-co/overview.md
```

### Step 4: Document Global Patterns
Start with agents you already have:
- Admin Agent
- Code-Fix Agent
- Observability Agent

### Step 5: Document Project-Specific Usage
In `.claude-mirror/`, document how consulting-co uses each agent.

### Step 6: Set Up Auto-Export
Configure `obsidian_exporter.py` to write to:
```
claude/projects/consulting-co/logs/
```

---

## Next Steps (Tonight)

From TONIGHT-PLAN.md:

**Create Structure (45 min):**
1. Create `claude/global/` structure
2. Create `claude/projects/consulting-co/` structure
3. Create `overview.md` for consulting-co
4. Create `_active.md` for agents/skills/commands
5. Create 5 templates in `templates/`
6. Create `tracking/bugs.md`, `tracking/tasks.md`, `tracking/plans.md`

**Document Current State (45 min):**
7. Document 3-5 agents in `global/agents/`
8. Document what consulting-co uses in `.claude-mirror/`
9. Start `global/resources/table-of-contents.md`

**Then:**
10. Review Neo4j (remaining time from 2-hour plan)

---

## Summary

### ✅ What This Structure Gives You

1. **Separation of Concerns**
   - Global: Reusable patterns
   - Project: Specific implementation

2. **Discoverability**
   - Start at project overview
   - Follow links to global docs
   - Or start at global and see all projects

3. **No Duplication**
   - Agent pattern documented once (global)
   - Project-specific config separate (.claude-mirror)

4. **Clean Logs**
   - Auto-generated in `logs/`
   - Tracking in `tracking/`
   - Documentation in `.claude-mirror/` and `global/`

5. **Scalability**
   - Add new projects easily
   - Reuse global docs
   - Each project self-contained

6. **Obsidian-Friendly**
   - Only files you want to read/search
   - Not cluttered with runtime code
   - Perfect for knowledge management

---

**Does this structure make sense?** It separates:
- ✅ Global reusable patterns
- ✅ Project-specific usage
- ✅ Runtime logs (auto-generated)
- ✅ Manual tracking (bugs/tasks/plans)
- ✅ Documentation vs. actual code

Ready to build this tonight? 🚀
