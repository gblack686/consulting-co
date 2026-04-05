# Tonight's Plan: Obsidian Templates + Neo4j Review
**Date:** 2025-12-01
**Duration:** 2 hours
**Focus:** Templatize Obsidian + Review Knowledge Graph

---

## What I Found in quickstart-nexus

### ✅ The Good News - You Already Have This Working!

**Superseding Code Location:** `../aws/RevStar/quickstarts/quickstart-nexus/.claude/`

**Key Integrations (NO Langfuse!):**
1. ✅ **SQLite Logging** - `events.db` with 51-column enriched schema
2. ✅ **Haiku Enrichment** - Real-time event analysis with Anthropic Batch API
3. ✅ **Graphiti + Neo4j** - Knowledge graph with entity extraction
4. ✅ **Obsidian Export** - Automated session notes with `obsidian_exporter.py`
5. ✅ **Multi-Agent Observability** - Bun backend + Vue frontend dashboard
6. ✅ **Hook System** - 9 event types captured (including SubagentStop)

### Architecture (Simplified, No Langfuse)

```
Claude Code Hooks → Python Scripts → SQLite events.db
                                   ↓
                         Haiku Enrichment (async)
                                   ↓
                         Graphiti → Neo4j
                                   ↓
                         Obsidian Export (markdown notes)
```

### File Structure Comparison

**Old (consulting-co):**
- ❌ Langfuse (4GB Docker container)
- ✅ Graphiti + Neo4j
- ⚠️ Obsidian (planned but not fully implemented)
- ⚠️ ~20 test files cluttering root

**New (quickstart-nexus):**
- ✅ SQLite only (lightweight, 51-column schema)
- ✅ Haiku enrichment (cost-efficient, 66% cache hit)
- ✅ Graphiti + Neo4j (working)
- ✅ Obsidian export (fully automated)
- ✅ Clean structure (tests in subdirs)

---

## Tonight's Goals (2 Hours)

### Goal 1: Templatize Obsidian Notebook (60 min)

#### 1.1 Review Your Template Library (15 min)
You already have an amazing template collection at:
`C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\obsidian-docs\Template-Library-Index.md`

**Key Templates to Use:**
- **Kepano's Templates** - Daily notes, projects, meetings
- **Templater Plugin** - Dynamic date/time functions
- **Voidashi Structure** - Organized folder hierarchy

#### 1.2 Create Doc-Claude-Workbench Obsidian Structure (30 min)

**Target Vault:** `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\`

**New Folder Structure:**
```
Gbautomation/
├── claude-logs/
│   └── consulting-co/
│       ├── sessions/           # Individual session notes (auto-generated)
│       ├── daily/              # Daily summaries (auto-generated)
│       ├── bugs/               # Bug tracking
│       │   └── bug.md         # Master bug list
│       ├── tasks/              # Task management
│       │   └── tasks.md       # Master task list
│       ├── plans/              # Planning docs
│       │   └── plans.md       # Master plan list
│       ├── decisions/          # Architecture Decision Records (ADRs)
│       ├── learnings/          # Knowledge notes
│       └── entities/           # Entity reference notes (from KG)
```

**Templates to Create:**

1. **`templates/claude-session.md`** - Session note template
```markdown
---
tags: [agent-session]
session_id: {{session_id}}
source_app: consulting-co
model: {{model}}
date: {{date}}
status: {{status}}
---

# Session: {{title}}

## Summary
{{summary}}

## Timeline
{{timeline}}

## Entities Discovered
{{entities}}

## Tools Used
{{tools}}

## Performance
{{performance_metrics}}

## Links
- [[{{previous_session}}|← Previous]]
- [[{{next_session}}|Next →]]
- [[{{daily_note}}|Daily Note]]
```

2. **`templates/claude-daily.md`** - Daily summary template
```markdown
---
tags: [daily-note, agent-activity]
date: {{date}}
---

# {{date}} - Claude Activity

## Summary
{{session_count}} sessions today

## Sessions
{{session_list}}

## Top Entities
{{top_entities}}

## Performance
{{aggregate_metrics}}

## Tomorrow's Focus
- [ ]
```

3. **`templates/bug.md`** - Bug tracking template
```markdown
---
tags: [bugs, tracking]
---

# Bug Tracker

## Active Bugs
{{active_bugs}}

## Resolved Bugs
{{resolved_bugs}}

## Bug Template
\`\`\`markdown
### 🐛 [BUG-{{number}}] {{title}}
**Date:** {{date}}
**Status:** {{status}}
**File:** {{file}}
**Description:**
{{description}}

**Fix Applied:**
{{fix}}

**Logged By:** Code-Fix Agent
\`\`\`
```

4. **`templates/tasks.md`** - Task tracking template
```markdown
---
tags: [tasks, tracking]
---

# Task Tracker

## In Progress
{{in_progress_tasks}}

## Pending
{{pending_tasks}}

## Completed
{{completed_tasks}}

## Task Template
\`\`\`markdown
### ⚡ [TASK-{{number}}] {{title}}
**Date:** {{date}}
**Status:** {{status}}
**Priority:** {{priority}}
**Description:**
{{description}}

**Progress:**
{{progress}}

**Logged By:** Admin Agent
\`\`\`
```

5. **`templates/plans.md`** - Planning template
```markdown
---
tags: [planning, tracking]
---

# Plans & Roadmaps

## Current Sprint
{{current_sprint}}

## Next Sprint
{{next_sprint}}

## Backlog
{{backlog}}

## Plan Template
\`\`\`markdown
### 🎯 [PLAN-{{number}}] {{title}}
**Date:** {{date}}
**Status:** {{status}}
**Timeframe:** {{timeframe}}
**Description:**
{{description}}

**Steps:**
{{steps}}

**Logged By:** Admin Agent
\`\`\`
```

#### 1.3 Configure Obsidian Export for consulting-co (15 min)

**Create:** `.claude/obsidian/config/obsidian.yaml`

```yaml
# Obsidian Vault Export Configuration for consulting-co

vault:
  # Path to Obsidian vault - using dynamic {pwd} variable
  path: "C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/claude-logs/consulting-co"

  daily_notes_format: "YYYY-MM-DD"

  directories:
    sessions: "sessions"
    daily: "daily"
    bugs: "bugs"
    tasks: "tasks"
    plans: "plans"
    decisions: "decisions"
    learnings: "learnings"
    entities: "entities"

export:
  frequency: "per-session"

  include:
    metrics: true
    entities: true
    timeline: true
    relationships: true
    tool_details: false

  limits:
    max_tools_in_timeline: 100
    max_entities_per_type: 15
    max_tool_output_chars: 500

  frontmatter:
    default_tags:
      - agent-session
    properties:
      - session_id
      - source_app
      - model
      - date
      - status
      - performance
      - entities

daily_summary:
  enabled: true
  include_stats: true
  group_by_source_app: true
  sort_by: "timestamp"

backlinks:
  create_entity_notes: false
  link_related_sessions: true
  tag_entity_types: true

formatting:
  flavor: "obsidian"
  code_block_language: "json"
  timestamp_format: "HH:MM:SS"
  use_emoji: true
  emoji_map:
    fast: "⚡"
    medium: "🔄"
    slow: "🐌"
    completed: "✅"
    active: "🔵"
    error: "❌"
```

**Copy Script:** Copy `quickstart-nexus/.claude/obsidian/scripts/obsidian_exporter.py` to `.claude/obsidian/scripts/`

---

### Goal 2: Review Neo4j Knowledge Graph (60 min)

#### 2.1 Connect to Neo4j (5 min)

**Check if Neo4j is running:**
```bash
docker ps | grep neo4j
# OR
neo4j status
```

**If not running:**
```bash
docker start neo4j-claude
# OR
neo4j start
```

**Connection Details:**
- URL: http://localhost:7474
- Username: neo4j
- Password: (from .env NEO4J_PASSWORD)

#### 2.2 Review Current Schema (20 min)

**Create:** `.claude/scripts/review_neo4j_schema.py`

```python
#!/usr/bin/env python3
"""Review Neo4j schema and data."""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

def run_query(query, description):
    print(f"\n{'='*60}")
    print(f"📊 {description}")
    print(f"{'='*60}\n")

    with driver.session() as session:
        result = session.run(query)
        for record in result:
            print(record)
    print()

# 1. Node Labels
run_query(
    "CALL db.labels()",
    "All Node Labels in Database"
)

# 2. Relationship Types
run_query(
    "CALL db.relationshipTypes()",
    "All Relationship Types"
)

# 3. Count Episodes
run_query(
    "MATCH (e:Episode) RETURN count(e) as episode_count",
    "Total Episodes Stored"
)

# 4. Count Entities
run_query(
    "MATCH (e:Entity) RETURN count(e) as entity_count",
    "Total Entities Extracted"
)

# 5. Recent Episodes
run_query(
    """
    MATCH (e:Episode)
    RETURN e.name, e.created_at, e.source
    ORDER BY e.created_at DESC
    LIMIT 10
    """,
    "Last 10 Episodes (Most Recent)"
)

# 6. Top Entities by Connections
run_query(
    """
    MATCH (e:Entity)-[r]-()
    WITH e, count(r) as connections
    RETURN e.name, e.type, connections
    ORDER BY connections DESC
    LIMIT 20
    """,
    "Top 20 Most Connected Entities"
)

# 7. Entity Types Breakdown
run_query(
    """
    MATCH (e:Entity)
    RETURN e.type as entity_type, count(e) as count
    ORDER BY count DESC
    """,
    "Entity Types Breakdown"
)

# 8. Sample Relationships
run_query(
    """
    MATCH (a:Entity)-[r]->(b:Entity)
    RETURN type(r) as relationship, a.name as from, b.name as to
    LIMIT 15
    """,
    "Sample Entity Relationships"
)

# 9. Episodes by Source
run_query(
    """
    MATCH (e:Episode)
    RETURN e.source, count(e) as count
    ORDER BY count DESC
    """,
    "Episodes Grouped by Source"
)

# 10. Graph Stats
run_query(
    """
    MATCH (n)
    RETURN
      count(DISTINCT labels(n)) as label_count,
      count(n) as total_nodes
    """,
    "Overall Graph Statistics"
)

driver.close()
```

**Run it:**
```bash
cd .claude/scripts
python review_neo4j_schema.py > neo4j_review_output.txt
```

#### 2.3 Take Screenshots (10 min)

**Open Neo4j Browser:** http://localhost:7474

**Run These Cypher Queries & Screenshot:**

1. **Graph Visualization - Top Entities:**
```cypher
MATCH (e:Entity)-[r]-()
WITH e, count(r) as connections
ORDER BY connections DESC
LIMIT 10
MATCH path = (e)-[r]-(connected)
RETURN path
LIMIT 50
```

2. **Timeline View - Recent Activity:**
```cypher
MATCH (e:Episode)
WHERE e.created_at IS NOT NULL
RETURN e.name, e.created_at, e.source
ORDER BY e.created_at DESC
LIMIT 20
```

3. **Entity Clustering:**
```cypher
MATCH (e1:Entity)-[r1]-(shared:Entity)-[r2]-(e2:Entity)
WHERE e1 <> e2
RETURN e1, r1, shared, r2, e2
LIMIT 50
```

**Save Screenshots:**
```
.claude/context/observability/screenshots/
├── graph-top-entities.png
├── timeline-recent.png
└── entity-clusters.png
```

#### 2.4 Document Current KG Status (25 min)

**Create:** `.claude/context/observability/KNOWLEDGE_GRAPH_STATUS.md`

```markdown
# Knowledge Graph Status Report
**Date:** {{today}}
**Neo4j Version:** {{version}}

## Summary
- **Episodes:** {{episode_count}}
- **Entities:** {{entity_count}}
- **Relationships:** {{relationship_count}}

## Top Entities (by connections)
{{top_20_entities}}

## Entity Types
{{entity_type_breakdown}}

## Recent Activity
{{last_10_episodes}}

## Sample Queries for Exploration

### Find all decisions related to authentication
\`\`\`cypher
MATCH (e:Entity {type: "Decision"})-[r]-(related)
WHERE toLower(e.name) CONTAINS "auth"
RETURN e, r, related
\`\`\`

### Show evolution of a concept over time
\`\`\`cypher
MATCH (e:Episode)-[:MENTIONS]->(entity:Entity {name: "Langfuse"})
RETURN e.name, e.created_at
ORDER BY e.created_at ASC
\`\`\`

### Find all tools used in sessions
\`\`\`cypher
MATCH (e:Episode)-[:USED_TOOL]->(tool:Entity {type: "Tool"})
RETURN tool.name, count(e) as usage_count
ORDER BY usage_count DESC
\`\`\`

## Screenshots
![Top Entities](screenshots/graph-top-entities.png)
![Timeline](screenshots/timeline-recent.png)
![Clusters](screenshots/entity-clusters.png)

## Next Steps
- [ ] Create unified search across Obsidian + Neo4j
- [ ] Implement Admin Agent for bilateral sync
- [ ] Add entity reference notes in Obsidian
- [ ] Set up weekly insights generation
```

---

## Checklist for Tonight

### Obsidian Setup
- [ ] Create folder structure in Gbautomation vault
- [ ] Create 5 markdown templates (session, daily, bug, tasks, plans)
- [ ] Copy `obsidian_exporter.py` from quickstart-nexus
- [ ] Create `obsidian.yaml` config
- [ ] Test export with a dummy session

### Neo4j Review
- [ ] Start Neo4j (if not running)
- [ ] Run `review_neo4j_schema.py` script
- [ ] Take 3 screenshots of Neo4j Browser visualizations
- [ ] Document findings in `KNOWLEDGE_GRAPH_STATUS.md`
- [ ] Identify top 10 most connected entities
- [ ] Note any gaps or cleanup needed

### Documentation
- [ ] Create folder: `.claude/context/observability/screenshots/`
- [ ] Save Neo4j review output
- [ ] Save screenshots
- [ ] Update main README with new Obsidian structure

---

## Output Deliverables

By end of tonight, you should have:

1. ✅ **Obsidian templates** - 5 markdown templates ready to use
2. ✅ **Vault structure** - Clean folder hierarchy in Gbautomation
3. ✅ **Neo4j review** - Documented current KG state
4. ✅ **Screenshots** - 3 visualizations for first Loom/content
5. ✅ **Config files** - `obsidian.yaml` ready for export

---

## Tomorrow's Preview (Week 1)

Once tonight's foundation is set:

**Day 1-2:** Copy hook system from quickstart-nexus
- Remove all Langfuse references
- Keep SQLite + Haiku enrichment
- Add Obsidian export trigger

**Day 3-4:** Implement Admin Agent
- Bilateral sync (Obsidian ↔ Neo4j)
- Auto-update bug.md, tasks.md, plans.md
- Generate daily summaries

**Day 5-7:** Testing & First Loom
- Test full workflow end-to-end
- Record Loom: "My AI Second Brain - Obsidian + Neo4j Sync"

---

## Key Insight from quickstart-nexus

**The winning pattern is simple:**
```
Hooks → SQLite (lightweight) → Haiku Enrichment (cheap) → Graphiti/Neo4j (smart) → Obsidian (human-readable)
```

**NOT:**
```
Hooks → Langfuse (4GB Docker) → Complex tracing → ???
```

You already nailed this in quickstart-nexus. Just need to:
1. Template the Obsidian part
2. Copy the pattern to consulting-co
3. Use it daily
4. Show it off

---

**Ready to start?** Let's begin with the Obsidian templates!
