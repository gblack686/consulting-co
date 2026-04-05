# Obsidian Folder Tree V2 - Complete Claude Workbench

**Vault Location:** `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\`
**New Structure:** `claude/` with `logs/`, `core/`, and `resources/`

---

## Complete Folder Tree

```
Gbautomation/                              # Your main Obsidian vault
│
├── obsidian-docs/                         # Your existing templates (keep as-is)
│   └── Template-Library-Index.md
│
└── claude/                                # 🎯 Main Claude workbench directory
    │
    ├── logs/                              # 📊 Session logs & daily notes
    │   └── consulting-co/                 # Project-specific namespace
    │       │
    │       ├── templates/                 # Template definitions
    │       │   ├── claude-session.md      # Session note template
    │       │   ├── claude-daily.md        # Daily summary template
    │       │   ├── bug-entry.md           # Individual bug template
    │       │   ├── task-entry.md          # Individual task template
    │       │   └── plan-entry.md          # Individual plan template
    │       │
    │       ├── sessions/                  # 🤖 Auto-generated session notes
    │       │   ├── 2025-12-01/
    │       │   │   ├── session-abc123.md
    │       │   │   ├── session-def456.md
    │       │   │   └── session-ghi789.md
    │       │   ├── 2025-12-02/
    │       │   └── README.md
    │       │
    │       ├── daily/                     # 🤖 Auto-generated daily summaries
    │       │   ├── 2025-12-01.md
    │       │   ├── 2025-12-02.md
    │       │   └── README.md
    │       │
    │       ├── bugs/                      # 🐛 Bug tracking
    │       │   ├── bug.md                 # 📌 Master bug list
    │       │   ├── active/
    │       │   │   ├── BUG-001-auth-error.md
    │       │   │   └── BUG-002-api-timeout.md
    │       │   ├── resolved/
    │       │   │   └── 2025-12/
    │       │   └── README.md
    │       │
    │       ├── tasks/                     # ⚡ Task management
    │       │   ├── tasks.md               # 📌 Master task list
    │       │   ├── in-progress/
    │       │   │   ├── TASK-001-obsidian-templates.md
    │       │   │   └── TASK-002-neo4j-review.md
    │       │   ├── completed/
    │       │   │   └── 2025-12/
    │       │   └── README.md
    │       │
    │       ├── plans/                     # 🎯 Planning & roadmaps
    │       │   ├── plans.md               # 📌 Master plan list
    │       │   ├── active/
    │       │   │   ├── PLAN-001-week1-foundation.md
    │       │   │   └── PLAN-002-admin-agent.md
    │       │   ├── completed/
    │       │   │   └── 2025-12/
    │       │   └── README.md
    │       │
    │       ├── decisions/                 # 📋 Architecture Decision Records
    │       │   ├── ADR-001-drop-langfuse.md
    │       │   ├── ADR-002-sqlite-events.md
    │       │   ├── index.md
    │       │   └── README.md
    │       │
    │       ├── learnings/                 # 💡 Knowledge notes
    │       │   ├── concepts/
    │       │   │   ├── knowledge-graphs.md
    │       │   │   ├── event-enrichment.md
    │       │   │   └── bilateral-sync.md
    │       │   ├── graphiti-integration.md
    │       │   ├── obsidian-export-patterns.md
    │       │   └── README.md
    │       │
    │       ├── entities/                  # 🔗 Entity reference notes (from KG)
    │       │   ├── _index.md
    │       │   ├── concepts/
    │       │   │   ├── Graphiti.md
    │       │   │   ├── Neo4j.md
    │       │   │   └── SQLite.md
    │       │   ├── technologies/
    │       │   │   ├── Haiku.md
    │       │   │   ├── Python.md
    │       │   │   └── Obsidian.md
    │       │   └── README.md
    │       │
    │       ├── meetings/                  # 👥 Meeting notes
    │       │   └── README.md
    │       │
    │       ├── attachments/               # 📎 Images, files, etc.
    │       │   ├── screenshots/
    │       │   │   ├── neo4j-graph-2025-12-01.png
    │       │   │   └── dashboard-2025-12-01.png
    │       │   └── diagrams/
    │       │       └── architecture-2025-12-01.excalidraw
    │       │
    │       └── README.md                  # Main project README
    │
    ├── core/                              # 🔧 Claude Code configuration files
    │   │
    │   ├── CLAUDE.md                      # 📌 Main project instructions
    │   │
    │   ├── prompts/                       # 💬 Prompt library
    │   │   ├── index.md                   # Prompt catalog
    │   │   ├── agents/
    │   │   │   ├── admin-agent-sync.md
    │   │   │   ├── code-fix-analysis.md
    │   │   │   └── entity-extraction.md
    │   │   ├── commands/
    │   │   │   ├── obsidian-daily-summary.md
    │   │   │   ├── neo4j-query-builder.md
    │   │   │   └── bug-report-generator.md
    │   │   ├── skills/
    │   │   │   ├── knowledge-sync-workflow.md
    │   │   │   └── enrichment-analyzer.md
    │   │   └── README.md
    │   │
    │   ├── hooks/                         # 🪝 Hook documentation
    │   │   ├── index.md                   # Hook catalog
    │   │   ├── lifecycle-overview.md
    │   │   ├── send-event.md              # How send_event.py works
    │   │   ├── haiku-enrichment.md        # How enrichment works
    │   │   ├── graphiti-logging.md        # How log_to_graphiti works
    │   │   ├── session-lifecycle.md
    │   │   └── README.md
    │   │
    │   ├── agents/                        # 🤖 Agent documentation
    │   │   ├── index.md                   # Agent catalog
    │   │   ├── admin-agent.md
    │   │   │   ├── Overview
    │   │   │   ├── Capabilities
    │   │   │   ├── Configuration
    │   │   │   ├── Prompts used
    │   │   │   └── Examples
    │   │   ├── code-fix-agent.md
    │   │   ├── observability-agent.md
    │   │   ├── graphiti-agent.md
    │   │   └── README.md
    │   │
    │   ├── skills/                        # 🎯 Skills documentation
    │   │   ├── index.md                   # Skills catalog
    │   │   ├── knowledge-sync.md
    │   │   ├── obsidian-vault.md
    │   │   ├── neo4j-queries.md
    │   │   └── README.md
    │   │
    │   ├── commands/                      # ⌨️ Slash commands documentation
    │   │   ├── index.md                   # Commands catalog
    │   │   ├── obsidian-commands.md
    │   │   │   ├── /obsidian:daily
    │   │   │   ├── /obsidian:summary
    │   │   │   └── /obsidian:export
    │   │   ├── scoping-commands.md
    │   │   │   ├── /scoping:analyze-transcripts
    │   │   │   └── /scoping:generate-adr
    │   │   ├── consulting-commands.md
    │   │   └── README.md
    │   │
    │   ├── workflows/                     # 🔄 ADWS (Agentic Dev Workflows)
    │   │   ├── index.md                   # Workflow catalog
    │   │   ├── daily-standup.md
    │   │   │   ├── Trigger
    │   │   │   ├── Steps
    │   │   │   ├── Agents involved
    │   │   │   └── Output
    │   │   ├── bug-fix-workflow.md
    │   │   ├── feature-development.md
    │   │   ├── knowledge-sync-workflow.md
    │   │   ├── weekly-review.md
    │   │   └── README.md
    │   │
    │   ├── schemas/                       # 📐 Data schemas
    │   │   ├── sqlite-events-schema.md
    │   │   ├── neo4j-schema.md
    │   │   ├── obsidian-frontmatter.md
    │   │   └── README.md
    │   │
    │   └── README.md                      # Core directory overview
    │
    └── resources/                         # 📚 Documentation & references
        │
        ├── table-of-contents.md           # 📌 Master TOC with descriptions
        │
        ├── quickstart/                    # 🚀 Getting started guides
        │   ├── index.md
        │   ├── 00-overview.md
        │   ├── 01-setup-obsidian.md
        │   ├── 02-setup-neo4j.md
        │   ├── 03-setup-hooks.md
        │   ├── 04-first-session.md
        │   └── README.md
        │
        ├── guides/                        # 📖 How-to guides
        │   ├── index.md                   # Guide catalog with descriptions
        │   ├── bilateral-sync-guide.md
        │   ├── entity-extraction-guide.md
        │   ├── custom-agent-guide.md
        │   ├── custom-hook-guide.md
        │   ├── obsidian-export-guide.md
        │   ├── neo4j-query-guide.md
        │   └── README.md
        │
        ├── architecture/                  # 🏗️ Architecture docs
        │   ├── index.md
        │   ├── system-overview.md
        │   ├── data-flow.md
        │   ├── storage-layers.md
        │   ├── agent-architecture.md
        │   ├── hook-lifecycle.md
        │   └── README.md
        │
        ├── api-reference/                 # 📘 API documentation
        │   ├── index.md
        │   ├── hooks-api.md
        │   ├── agents-api.md
        │   ├── obsidian-exporter-api.md
        │   ├── sqlite-api.md
        │   ├── neo4j-api.md
        │   └── README.md
        │
        ├── integrations/                  # 🔌 Integration docs
        │   ├── index.md                   # Integration catalog
        │   ├── graphiti-integration.md
        │   ├── neo4j-integration.md
        │   ├── obsidian-integration.md
        │   ├── haiku-enrichment.md
        │   ├── sqlite-integration.md
        │   └── README.md
        │
        ├── troubleshooting/               # 🔧 Troubleshooting
        │   ├── index.md
        │   ├── common-issues.md
        │   ├── neo4j-issues.md
        │   ├── obsidian-issues.md
        │   ├── hook-issues.md
        │   └── README.md
        │
        ├── examples/                      # 💡 Examples & templates
        │   ├── index.md
        │   ├── agent-examples/
        │   │   ├── custom-admin-agent.md
        │   │   └── custom-analyzer-agent.md
        │   ├── hook-examples/
        │   │   ├── custom-enrichment-hook.md
        │   │   └── custom-notification-hook.md
        │   ├── workflow-examples/
        │   │   ├── code-review-workflow.md
        │   │   └── research-workflow.md
        │   └── README.md
        │
        ├── external-links/                # 🔗 External documentation
        │   ├── index.md                   # Categorized external links
        │   ├── claude-code.md             # Claude Code official docs
        │   ├── graphiti.md                # Graphiti docs & repos
        │   ├── neo4j.md                   # Neo4j docs & resources
        │   ├── obsidian.md                # Obsidian docs & plugins
        │   ├── anthropic.md               # Anthropic API docs
        │   └── README.md
        │
        ├── best-practices/                # ✨ Best practices
        │   ├── index.md
        │   ├── prompt-engineering.md
        │   ├── agent-design.md
        │   ├── knowledge-graph-design.md
        │   ├── obsidian-organization.md
        │   └── README.md
        │
        ├── changelog/                     # 📝 Version history
        │   ├── index.md
        │   ├── v2.0-no-langfuse.md
        │   ├── v1.0-initial.md
        │   └── README.md
        │
        └── README.md                      # Resources directory overview
```

---

## Directory Breakdown

### 📊 `claude/logs/` - Session Logs & Activity

**Purpose:** All auto-generated and manual tracking for sessions, bugs, tasks, plans
- Auto-generated session notes
- Daily summaries
- Bug tracking (bug.md master file)
- Task management (tasks.md master file)
- Planning (plans.md master file)
- ADRs
- Learnings
- Entity references from Neo4j

**Key Files:**
- `bugs/bug.md` - Master bug tracker
- `tasks/tasks.md` - Master task list
- `plans/plans.md` - Master plan list

---

### 🔧 `claude/core/` - Configuration & Code References

**Purpose:** Documentation of your Claude Code setup (prompts, hooks, agents, skills, workflows)

#### `core/CLAUDE.md`
The main project instructions file that lives in your actual `.claude/CLAUDE.md`
- Documented here as reference
- Links to actual file in project
- Explains project-specific rules and patterns

#### `core/prompts/`
**Purpose:** Library of all prompts used across the system

**Structure:**
```
prompts/
├── index.md                    # Searchable prompt catalog
├── agents/                     # Agent-specific prompts
│   ├── admin-agent-sync.md    # Bilateral sync prompt
│   ├── code-fix-analysis.md   # Error analysis prompt
│   └── entity-extraction.md   # Haiku extraction prompt
├── commands/                   # Slash command prompts
├── skills/                     # Skill-specific prompts
└── README.md
```

**Each prompt document includes:**
- Prompt text
- Variables/placeholders
- Expected output format
- Usage examples
- Version history

#### `core/hooks/`
**Purpose:** Documentation of all hook scripts

**Example: `hooks/send-event.md`**
```markdown
# send_event.py Hook

## Overview
Posts events to SQLite backend for storage and enrichment.

## Trigger
All lifecycle events (UserPromptSubmit, Stop, PreToolUse, etc.)

## Configuration
Location: `.claude/hooks/send_event.py`
Backend: http://localhost:4000/events

## Data Flow
1. Hook receives stdin (event data)
2. Formats as JSON
3. POST to backend
4. Backend stores in SQLite

## Schema
See: [[sqlite-events-schema]]

## Related
- [[haiku-enrichment]]
- [[observability-backend]]
```

#### `core/agents/`
**Purpose:** Documentation of each agent

**Example: `agents/admin-agent.md`**
```markdown
# Admin Agent

## Overview
Bilateral sync between Obsidian and Neo4j. Auto-updates bug.md, tasks.md, plans.md.

## Capabilities
- Sync Obsidian → Neo4j (new notes → graph)
- Sync Neo4j → Obsidian (entities → reference notes)
- Update master files (bug.md, tasks.md, plans.md)
- Generate daily summaries
- Create entity reference notes

## Configuration
File: `.claude/agents/admin-agent/config.yaml`

## Prompts Used
- [[admin-agent-sync]] - Main sync prompt
- [[entity-extraction]] - Entity detection

## Triggers
- End of session (Stop hook)
- End of day (cron)
- Manual: `/admin:sync`

## Examples
[Usage examples with screenshots]

## Related
- [[bilateral-sync-guide]]
- [[obsidian-integration]]
```

#### `core/skills/`
**Purpose:** Documentation of installed skills

**Example: `skills/knowledge-sync.md`**
```markdown
# Knowledge Sync Skill

## Overview
Unified search and sync across Obsidian + Graphiti.

## Commands
- `/search [query]` - Search both layers
- `/sync-to-graph [note]` - Sync note to Neo4j
- `/graph-insights` - Generate insights

## Configuration
File: `.claude/skills/knowledge-sync/config.json`

## How It Works
[Detailed explanation with diagrams]

## Examples
[Usage examples]
```

#### `core/commands/`
**Purpose:** Documentation of all slash commands

**Example: `commands/obsidian-commands.md`**
```markdown
# Obsidian Commands

## /obsidian:daily
Generate today's Obsidian daily summary.

**Location:** `.claude/commands/obsidian/daily.md`
**Trigger:** Manual or cron
**Output:** `claude/logs/consulting-co/daily/YYYY-MM-DD.md`

## /obsidian:summary
Generate summary for specific date.

**Usage:** `/obsidian:summary 2025-12-01`

## /obsidian:export
Export current session to Obsidian.

**Usage:** `/obsidian:export`
```

#### `core/workflows/` (ADWS)
**Purpose:** Agentic Development Workflow Specifications

**Example: `workflows/bug-fix-workflow.md`**
```markdown
# Bug Fix Workflow (ADWS)

## Trigger
PostToolUse event with error status

## Steps
1. **Detect** - Hook catches tool error
2. **Analyze** - Code-Fix Agent analyzes error
3. **Suggest** - Generate patch suggestion
4. **Log** - Update bug.md with BUG-XXX entry
5. **Store** - Save to SQLite events.db
6. **Notify** - User sees suggestion

## Agents Involved
- Code-Fix Agent (primary)
- Admin Agent (logging)

## Prompts Used
- [[code-fix-analysis]]

## Output
- bug.md updated
- bugs/active/BUG-XXX-{slug}.md created
- Event in SQLite with fix suggestion

## Example
[Full example with screenshots]
```

#### `core/schemas/`
**Purpose:** Data structure documentation

**Example: `schemas/sqlite-events-schema.md`**
```markdown
# SQLite Events Schema

## Table: events

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_type | TEXT | UserPromptSubmit, Stop, etc. |
| timestamp | TEXT | ISO 8601 |
| session_id | TEXT | Unique session ID |
| ... | ... | ... |
| intent | TEXT | Haiku enrichment |
| complexity | TEXT | Haiku enrichment |
| tool_effectiveness | TEXT | Haiku enrichment |

[Full 51-column schema]

## Indexes
- idx_session_id
- idx_timestamp
- idx_event_type

## Queries
See: [[neo4j-query-guide]]
```

---

### 📚 `claude/resources/` - Documentation Library

**Purpose:** Comprehensive documentation, guides, references

#### `resources/table-of-contents.md` 📌
**The master index with descriptions**

```markdown
# Claude Workbench - Documentation TOC

## 🚀 Getting Started
- [[00-overview]] - What is doc-claude-workbench
- [[01-setup-obsidian]] - Set up Obsidian vault
- [[02-setup-neo4j]] - Set up Neo4j knowledge graph
- [[03-setup-hooks]] - Configure hooks
- [[04-first-session]] - Run your first session

## 📖 How-To Guides
- [[bilateral-sync-guide]] - Sync Obsidian ↔ Neo4j
- [[entity-extraction-guide]] - Extract entities from sessions
- [[custom-agent-guide]] - Build custom agents
- [[custom-hook-guide]] - Build custom hooks
- [[obsidian-export-guide]] - Configure exports
- [[neo4j-query-guide]] - Query the knowledge graph

## 🏗️ Architecture
- [[system-overview]] - High-level architecture
- [[data-flow]] - How data flows through the system
- [[storage-layers]] - SQLite, Neo4j, Obsidian
- [[agent-architecture]] - How agents work
- [[hook-lifecycle]] - Hook execution flow

## 📘 API Reference
- [[hooks-api]] - Hook script API
- [[agents-api]] - Agent API
- [[obsidian-exporter-api]] - Export script API
- [[sqlite-api]] - Database schema & queries
- [[neo4j-api]] - Cypher queries & patterns

## 🔌 Integrations
- [[graphiti-integration]] - Graphiti + Neo4j setup
- [[neo4j-integration]] - Neo4j configuration
- [[obsidian-integration]] - Obsidian vault setup
- [[haiku-enrichment]] - Haiku enrichment pipeline
- [[sqlite-integration]] - SQLite backend setup

## 🔧 Troubleshooting
- [[common-issues]] - FAQ & solutions
- [[neo4j-issues]] - Neo4j troubleshooting
- [[obsidian-issues]] - Obsidian troubleshooting
- [[hook-issues]] - Hook debugging

## 💡 Examples
- [[agent-examples]] - Custom agent examples
- [[hook-examples]] - Custom hook examples
- [[workflow-examples]] - ADWS examples

## 🔗 External Links
- [[claude-code]] - Official Claude Code docs
- [[graphiti]] - Graphiti documentation
- [[neo4j]] - Neo4j documentation
- [[obsidian]] - Obsidian documentation
- [[anthropic]] - Anthropic API docs

## ✨ Best Practices
- [[prompt-engineering]] - Writing effective prompts
- [[agent-design]] - Designing agents
- [[knowledge-graph-design]] - KG best practices
- [[obsidian-organization]] - Organizing notes

## 📝 Changelog
- [[v2.0-no-langfuse]] - Current version
- [[v1.0-initial]] - Initial release
```

#### `resources/quickstart/`
Step-by-step setup guides for new users

#### `resources/guides/`
Detailed how-to guides with examples and screenshots

#### `resources/architecture/`
System architecture documentation with diagrams

#### `resources/api-reference/`
API documentation for all components

#### `resources/integrations/`
Integration guides for each external service

#### `resources/troubleshooting/`
Common issues and solutions

#### `resources/examples/`
Real-world examples and templates

#### `resources/external-links/`
Categorized links to external documentation

**Example: `external-links/graphiti.md`**
```markdown
# Graphiti Resources

## Official Documentation
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Graphiti Core Docs](https://github.com/getzep/graphiti/tree/main/graphiti_core)
- [MCP Server](https://github.com/getzep/graphiti/tree/main/mcp_server)

## Tutorials
- Quickstart with Neo4j
- Entity extraction patterns
- Temporal queries

## Community
- GitHub Issues
- Discord

## Related
- [[neo4j]]
- [[knowledge-graph-design]]
```

---

## Key Features of This Structure

### ✅ Separation of Concerns
- **logs/** - Runtime data (sessions, bugs, tasks)
- **core/** - Code & configuration documentation
- **resources/** - Educational content & references

### ✅ Discoverable
- `table-of-contents.md` is your entry point
- Every directory has `index.md` and `README.md`
- Cross-linked everywhere with `[[wikilinks]]`

### ✅ Searchable
- Obsidian search finds everything
- Tags on all documents
- Dataview queries possible

### ✅ Maintainable
- Clear naming conventions
- One document per topic
- Version history in changelog/

### ✅ Scalable
- Add new projects under `logs/`
- Add new docs under `resources/`
- Add new configs under `core/`

---

## Example: Complete Documentation for One Hook

**File:** `claude/core/hooks/send-event.md`
```markdown
---
tags: [hook, documentation, core]
hook_name: send_event
file_location: .claude/hooks/send_event.py
version: 2.0
---

# send_event.py Hook

## Overview
Core hook that posts all lifecycle events to SQLite backend.

## Trigger Events
- UserPromptSubmit
- Stop
- PreToolUse
- PostToolUse
- SessionStart
- SessionEnd
- SubagentStop
- Notification
- PreCompact

## Configuration
**File:** `.claude/hooks/send_event.py`
**Backend:** http://localhost:4000/events
**Timeout:** 5 seconds

## Data Flow
1. Claude Code fires hook
2. Hook receives JSON via stdin
3. Extracts: event_type, session_id, timestamp, payload
4. POST to backend endpoint
5. Backend stores in SQLite events.db
6. Returns success/failure

## Schema
See: [[sqlite-events-schema]]

## Code Reference
\`\`\`python
# Actual location
C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/hooks/send_event.py
\`\`\`

## Related Hooks
- [[send-event-v2]] - With Haiku enrichment
- [[log-to-graphiti]] - Neo4j logging

## Related Agents
- None (this is infrastructure)

## Troubleshooting
See: [[hook-issues#send-event]]

## Examples
See: [[hook-examples#send-event]]

## Changelog
- v2.0 - Added enrichment support
- v1.0 - Initial release
```

---

## Example: Complete Table of Contents Entry

**File:** `claude/resources/table-of-contents.md` (excerpt)

```markdown
## 📖 How-To Guides

### [[bilateral-sync-guide|Bilateral Sync Guide]]
**Description:** Learn how to set up bidirectional sync between Obsidian notes and Neo4j knowledge graph. Covers sync triggers, conflict resolution, and entity mapping.
**Difficulty:** Intermediate
**Time:** 20 minutes
**Prerequisites:** [[01-setup-obsidian]], [[02-setup-neo4j]]

### [[entity-extraction-guide|Entity Extraction Guide]]
**Description:** Configure Haiku-powered entity extraction from Claude sessions. Includes prompt engineering, entity types, and relationship mapping.
**Difficulty:** Advanced
**Time:** 30 minutes
**Prerequisites:** [[haiku-enrichment]], [[graphiti-integration]]

### [[custom-agent-guide|Custom Agent Guide]]
**Description:** Step-by-step guide to building your own custom agent. Covers agent structure, prompt design, tool access, and deployment.
**Difficulty:** Advanced
**Time:** 45 minutes
**Prerequisites:** [[agent-architecture]], [[prompt-engineering]]
```

---

## Frontmatter Standards

### Core Documentation
```yaml
---
tags: [core, documentation, hooks]
component: send_event
type: hook
file_location: .claude/hooks/send_event.py
version: 2.0
last_updated: 2025-12-01
---
```

### Resource Documentation
```yaml
---
tags: [guide, how-to, bilateral-sync]
difficulty: intermediate
time_required: 20 minutes
prerequisites: [obsidian-setup, neo4j-setup]
last_updated: 2025-12-01
---
```

### External Links
```yaml
---
tags: [external, reference]
category: graphiti
link_type: official documentation
last_verified: 2025-12-01
---
```

---

## Navigation Examples

### From a Session Note
```markdown
# Session: Fix Authentication Bug

[Session content...]

## Related
- [[bug.md#BUG-001]] - This bug
- [[admin-agent]] - Agent that logged this
- [[send-event]] - Hook that captured this
- [[troubleshooting/common-issues]] - If you hit issues
```

### From a Core Doc
```markdown
# Admin Agent

[Agent documentation...]

## See Also
- **Guide:** [[bilateral-sync-guide]]
- **Example:** [[agent-examples/custom-admin-agent]]
- **Troubleshooting:** [[troubleshooting/common-issues#admin-agent]]
- **External:** [[obsidian/plugins]]
```

---

## Quick Reference Cards

Add these to `resources/` for quick lookup:

### `resources/quick-reference-hooks.md`
One-page reference of all hooks

### `resources/quick-reference-agents.md`
One-page reference of all agents

### `resources/quick-reference-commands.md`
One-page reference of all slash commands

---

## Storage Estimates

**Per Project:**
- logs/: ~1.5 MB/month (session data)
- core/: ~500 KB (documentation)
- resources/: ~2 MB (guides + examples)

**Total:** ~4 MB/month per project

**Yearly:** ~48 MB

---

## Migration from Current Structure

### Step 1: Create Directory Structure
```bash
cd ~/OneDrive/Desktop/obsidian/Gbautomation
mkdir -p claude/{logs,core,resources}
mkdir -p claude/logs/consulting-co
# ... (full structure from tree above)
```

### Step 2: Copy Existing Logs (if any)
```bash
# Move any existing logs
mv claude-logs/* claude/logs/
```

### Step 3: Create Core Documentation
Start documenting:
- CLAUDE.md reference
- Hook documentation
- Agent documentation
- Schemas

### Step 4: Create Resources
Start with:
- table-of-contents.md
- quickstart/ guides
- Basic troubleshooting

### Step 5: Link Everything
Add wikilinks between all documents

---

## Next Steps (Tonight)

### From TONIGHT-PLAN.md

**Create This Structure (30 min):**
1. Create main directories: `claude/{logs,core,resources}`
2. Create logs/consulting-co structure
3. Create 5 templates in logs/consulting-co/templates/
4. Create table-of-contents.md skeleton
5. Create core/ index files

**Then:**
6. Review Neo4j (remaining time)
7. Take screenshots
8. Document findings

---

**This gives you:**
- ✅ Complete separation: logs, core, resources
- ✅ Discoverable via table-of-contents.md
- ✅ Searchable via Obsidian
- ✅ Scalable to multiple projects
- ✅ Professional documentation structure
- ✅ Easy onboarding for others (or yourself in 6 months!)

**Ready to create this structure?** Start with TONIGHT-PLAN.md and build incrementally!
