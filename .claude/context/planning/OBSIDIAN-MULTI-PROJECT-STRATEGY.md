# Obsidian Multi-Project Strategy

**Key Insight:** You're absolutely right! Obsidian should track MULTIPLE project repos, not just one.

---

## 🎯 The Correct Mental Model

### What We Have (Repos)
```
~/OneDrive/Desktop/
├── claude-template/              # Template/workbench (master)
├── consulting-co/                # Active consulting work
├── quickstart-nexus/             # RevStar project
├── client-project-1/             # Future client work
└── client-project-2/             # Another client
```

### What Obsidian Should Track
```
Gbautomation/claude/
├── global/                       # Cross-project patterns
│   ├── agents/                   # Agent PATTERNS (how they work)
│   ├── skills/                   # Skill PATTERNS
│   ├── commands/                 # Command PATTERNS
│   └── resources/                # Docs, guides
│
└── projects/                     # Each repo gets its own namespace
    ├── claude-template/          # Tracks claude-template repo
    │   ├── .claude-mirror/       # What's in claude-template/.claude/
    │   ├── logs/                 # 🔗 LIVE from claude-template/logs/
    │   └── tracking/             # bugs, tasks, plans
    │
    ├── consulting-co/            # Tracks consulting-co repo
    │   ├── .claude-mirror/       # What's in consulting-co/.claude/
    │   ├── logs/                 # 🔗 LIVE from consulting-co/logs/
    │   └── tracking/             # bugs, tasks, plans
    │
    ├── quickstart-nexus/         # Tracks quickstart-nexus repo
    │   ├── .claude-mirror/       # What's in quickstart-nexus/.claude/
    │   ├── logs/                 # 🔗 LIVE from quickstart-nexus/logs/
    │   └── tracking/             # bugs, tasks, plans
    │
    └── client-project-1/         # Future client project
        └── ...
```

---

## 🔗 Bilateral Sync Architecture

### The Problem You Identified
If Obsidian only points to ONE repo, how do we track:
- Multiple projects using the same agents?
- Different projects with different configurations?
- Session logs from different repos?

### The Solution: Multiple Live Connections

Each project in Obsidian should have **symlinks or export configs** that point to its respective repo's `.claude/` directory.

---

## 📁 Correct Directory Structure

### On Disk (Repos)
```
~/OneDrive/Desktop/
├── claude-template/.claude/
│   ├── hooks/
│   ├── agents/admin-agent/
│   ├── agents/code-fix-agent/
│   ├── skills/knowledge-sync/
│   └── observability/backend/events.db
│
├── consulting-co/.claude/         # Could symlink → claude-template/.claude/
│   └── (same structure)           # OR have its own copy
│
└── quickstart-nexus/.claude/
    └── (same structure)
```

### In Obsidian (Views)
```
Gbautomation/claude/projects/
│
├── claude-template/
│   ├── overview.md               # "This is the master template"
│   ├── .claude-mirror/
│   │   ├── agents/
│   │   │   ├── _active.md        # "Admin Agent, Code-Fix Agent"
│   │   │   ├── admin-agent.md    # Links to actual file
│   │   │   └── code-fix-agent.md # Links to actual file
│   │   └── README.md             # Points to C:/...claude-template/.claude/
│   │
│   ├── logs/                     # 🔗 Auto-exported from claude-template
│   │   ├── sessions/
│   │   └── daily/
│   │
│   └── tracking/
│       ├── bugs.md
│       ├── tasks.md
│       └── plans.md
│
├── consulting-co/
│   ├── overview.md               # "Consulting work, uses claude-template"
│   ├── .claude-mirror/
│   │   └── README.md             # "This project uses claude-template/.claude/"
│   │                             # OR lists its own .claude/ if different
│   │
│   ├── logs/                     # 🔗 Auto-exported from consulting-co
│   │   ├── sessions/
│   │   └── daily/
│   │
│   └── tracking/
│       ├── bugs.md               # consulting-co specific bugs
│       ├── tasks.md              # consulting-co specific tasks
│       └── plans.md              # consulting-co specific plans
│
└── quickstart-nexus/
    └── (same pattern)
```

---

## 🔄 How Bilateral Sync Works Across Projects

### Scenario 1: Shared `.claude/` (Symlink Approach)

```bash
# claude-template has the master .claude/
cd ~/OneDrive/Desktop/consulting-co
ln -s ../claude-template/.claude .claude

# Now both repos share the same .claude/ directory
```

**Obsidian Tracking:**
```
projects/claude-template/
  - Master template
  - All agents/skills/commands documented

projects/consulting-co/
  .claude-mirror/README.md:
    "This project uses claude-template/.claude/ via symlink"
    "See: [[../claude-template/.claude-mirror/README]]"
```

**Export Config:**
```yaml
# claude-template/.claude/obsidian/config/obsidian.yaml
vault:
  path: "~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects/claude-template"

# consulting-co/.claude/obsidian/config/obsidian.yaml (if it exists)
vault:
  path: "~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects/consulting-co"
```

### Scenario 2: Independent `.claude/` Directories

```bash
# Each repo has its own .claude/
claude-template/.claude/
consulting-co/.claude/
quickstart-nexus/.claude/
```

**Obsidian Tracking:**
Each project independently documents what it has:

```
projects/claude-template/.claude-mirror/agents/_active.md:
  - Admin Agent (configured)
  - Code-Fix Agent (configured)

projects/consulting-co/.claude-mirror/agents/_active.md:
  - Admin Agent (configured) - copied from claude-template
  - Project-specific-agent (custom)

projects/quickstart-nexus/.claude-mirror/agents/_active.md:
  - YouTube Analysis Agent (unique to this project)
```

---

## 🎯 Recommended Approach: Hybrid

### Master Template (claude-template)
- Has the canonical `.claude/` directory
- All standard agents, skills, commands
- This is what you clone for new projects

### Active Projects
**Option A: Symlink for simple projects**
```bash
cd consulting-co
ln -s ../claude-template/.claude .claude
# Uses master template as-is
```

**Option B: Copy & customize for complex projects**
```bash
cd client-project-1
cp -r ../claude-template/.claude .claude
# Then customize for client
```

### Obsidian Auto-Export Configuration

**Each repo's `.claude/` needs its own export config:**

```yaml
# claude-template/.claude/obsidian/config/obsidian.yaml
vault:
  path: "~/obsidian/Gbautomation/claude/projects/claude-template"
  project_name: "claude-template"

# consulting-co/.claude/obsidian/config/obsidian.yaml
vault:
  path: "~/obsidian/Gbautomation/claude/projects/consulting-co"
  project_name: "consulting-co"

# quickstart-nexus/.claude/obsidian/config/obsidian.yaml
vault:
  path: "~/obsidian/Gbautomation/claude/projects/quickstart-nexus"
  project_name: "quickstart-nexus"
```

**Then the export script detects which project:**
```python
# .claude/obsidian/scripts/obsidian_exporter.py

import os
from pathlib import Path

def get_project_config():
    """Auto-detect which project we're in."""
    cwd = Path.cwd()
    config_file = cwd / ".claude/obsidian/config/obsidian.yaml"

    if config_file.exists():
        # Load config, get vault path
        return load_config(config_file)
    else:
        # Fallback: derive from current directory name
        project_name = cwd.name
        return {
            "vault_path": f"~/obsidian/Gbautomation/claude/projects/{project_name}",
            "project_name": project_name
        }
```

---

## 🔗 Live Connections for Bilateral Sync

### Admin Agent Needs to Know About All Projects

```python
# .claude/agents/admin-agent/admin_agent.py

import os
from pathlib import Path

# Define all projects the Admin Agent should track
PROJECTS = [
    {
        "name": "claude-template",
        "repo_path": Path("~/OneDrive/Desktop/claude-template"),
        "obsidian_path": Path("~/obsidian/Gbautomation/claude/projects/claude-template"),
        "neo4j_namespace": "claude-template"
    },
    {
        "name": "consulting-co",
        "repo_path": Path("~/OneDrive/Desktop/consulting-co"),
        "obsidian_path": Path("~/obsidian/Gbautomation/claude/projects/consulting-co"),
        "neo4j_namespace": "consulting-co"
    },
    {
        "name": "quickstart-nexus",
        "repo_path": Path("~/OneDrive/Desktop/quickstart-nexus"),
        "obsidian_path": Path("~/obsidian/Gbautomation/claude/projects/quickstart-nexus"),
        "neo4j_namespace": "quickstart-nexus"
    },
]

def sync_project(project):
    """Sync one project: Obsidian ↔ Neo4j"""
    # Read from Obsidian
    obsidian_notes = read_obsidian_notes(project["obsidian_path"])

    # Sync to Neo4j (with project namespace)
    sync_to_neo4j(obsidian_notes, namespace=project["neo4j_namespace"])

    # Read from Neo4j
    neo4j_entities = read_neo4j_entities(namespace=project["neo4j_namespace"])

    # Generate Obsidian entity notes
    generate_entity_notes(neo4j_entities, project["obsidian_path"] / "entities")

def sync_all_projects():
    """Run bilateral sync for all tracked projects"""
    for project in PROJECTS:
        if project["repo_path"].exists():
            sync_project(project)
```

---

## 📊 Example: Multi-Project View in Obsidian

### Global Agent Documentation
```markdown
# Admin Agent (Global Pattern)
Location: `claude/global/agents/admin-agent.md`

## Overview
Bilateral sync between Obsidian and Neo4j.

## Projects Using This Agent
- [[../projects/claude-template/overview|claude-template]] ✅
- [[../projects/consulting-co/overview|consulting-co]] ✅
- [[../projects/quickstart-nexus/overview|quickstart-nexus]] ✅

## Configuration Examples
See each project's `.claude-mirror/agents/admin-agent.md` for project-specific config.
```

### Project-Specific Configuration
```markdown
# Admin Agent - consulting-co Config
Location: `claude/projects/consulting-co/.claude-mirror/agents/admin-agent.md`

## Source
This project uses the Admin Agent from:
[[../../claude-template/.claude-mirror/agents/admin-agent|claude-template]]

## Configuration
File: `~/Desktop/consulting-co/.claude/agents/admin-agent/config.yaml`

```yaml
triggers:
  - stop_hook
  - daily_cron

files:
  bug_tracker: ~/obsidian/Gbautomation/claude/projects/consulting-co/tracking/bugs.md
  task_tracker: ~/obsidian/Gbautomation/claude/projects/consulting-co/tracking/tasks.md
```

## Customizations for This Project
- We run daily sync at 11pm
- We filter out test sessions
- We export to consulting-co namespace in Neo4j
```

---

## ✅ Correct Migration Plan

### Step 1: Set Up claude-template as Master
```bash
cd ~/OneDrive/Desktop/claude-template

# Copy planning docs
cp ../consulting-co/.claude/context/planning/*.md context/planning/

# Set up Obsidian export config
mkdir -p .claude/obsidian/config
cat > .claude/obsidian/config/obsidian.yaml <<EOF
vault:
  path: "~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects/claude-template"
  project_name: "claude-template"
EOF

# Commit
git add .
git commit -m "Set up as master template with planning docs"
git push
```

### Step 2: Set Up Obsidian for Multi-Project
```bash
cd ~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects

# Keep both project directories
# - claude-template/ (tracks claude-template repo)
# - consulting-co/ (tracks consulting-co repo)

# Update each overview.md to point to correct repo
```

### Step 3: Set Up consulting-co
```bash
cd ~/OneDrive/Desktop/consulting-co

# Option A: Symlink to claude-template (if you want shared .claude/)
ln -s ../claude-template/.claude .claude

# Option B: Copy and customize (if you want independent .claude/)
cp -r ../claude-template/.claude .claude
# Then set up separate obsidian export config
cat > .claude/obsidian/config/obsidian.yaml <<EOF
vault:
  path: "~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects/consulting-co"
  project_name: "consulting-co"
EOF
```

### Step 4: Update Admin Agent for Multi-Project
```python
# claude-template/.claude/agents/admin-agent/config.yaml

projects:
  - name: claude-template
    repo_path: ~/OneDrive/Desktop/claude-template
    obsidian_path: ~/obsidian/Gbautomation/claude/projects/claude-template
    neo4j_namespace: claude-template

  - name: consulting-co
    repo_path: ~/OneDrive/Desktop/consulting-co
    obsidian_path: ~/obsidian/Gbautomation/claude/projects/consulting-co
    neo4j_namespace: consulting-co
```

---

## 🎯 Final Answer to Your Question

**You're absolutely right!** Obsidian needs:

1. **Live connections to EACH project's repo**
   - claude-template → `projects/claude-template/`
   - consulting-co → `projects/consulting-co/`
   - quickstart-nexus → `projects/quickstart-nexus/`

2. **Each project's export config points to its own Obsidian namespace**
   - claude-template exports to `projects/claude-template/logs/`
   - consulting-co exports to `projects/consulting-co/logs/`

3. **Admin Agent tracks ALL projects**
   - Configured with list of projects
   - Syncs each independently
   - Each gets its own Neo4j namespace

4. **Global docs show which projects use what**
   - `global/agents/admin-agent.md` lists all projects using it
   - Each `projects/{name}/.claude-mirror/` shows that project's specific config

---

## 🚀 Updated Migration: Keep Both Projects

### In Obsidian
```
claude/
├── global/                       # Shared patterns
└── projects/
    ├── claude-template/          # Master template
    │   ├── overview.md           # "This is the template"
    │   ├── logs/                 # From claude-template repo
    │   └── tracking/
    │
    └── consulting-co/            # Active work
        ├── overview.md           # "Uses claude-template"
        ├── logs/                 # From consulting-co repo
        └── tracking/
```

### On Disk
```
~/OneDrive/Desktop/
├── claude-template/              # Master template
│   └── .claude/                  # The canonical pattern
│
└── consulting-co/                # Your work
    └── .claude/ → symlink        # Points to claude-template/.claude/
                                  # OR its own copy if customized
```

**Does this make sense now?** Multi-project tracking with bilateral sync for each! 🎯
