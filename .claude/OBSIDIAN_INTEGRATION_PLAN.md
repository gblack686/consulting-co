# Obsidian AI Agent Integration Plan

**Date:** November 13, 2025
**Repository:** consulting-co
**Framework:** VIBE Planning Framework
**Integration Target:** [Obsidian AI Agent](https://github.com/m-rgba/obsidian-ai-agent)

---

## Executive Summary

This plan outlines the integration of Obsidian knowledge base capabilities into the Claude Code workflow through a bidirectional sync system. The integration enables Claude Code to read, write, search, and organize notes in an Obsidian vault while maintaining the vault as a persistent knowledge graph for project context, decisions, and learnings.

**Key Benefits:**
- Persistent project knowledge across sessions
- Seamless note-taking during development
- Automatic documentation of architectural decisions
- Search and retrieve context from past work
- Bidirectional sync between Claude Code and Obsidian

**Integration Approach:** Skill-based with hook automation + optional MCP server

---

## Integration Architecture

### Option 1: Skill-Based Integration (Recommended for MVP)

**Location:** `.claude/skills/obsidian-vault/`

**Components:**
1. **SKILL.md** - Main skill definition for Obsidian operations
2. **scripts/vault-sync.js** - Node.js script for vault operations
3. **config/vault-settings.json** - Vault configuration
4. **templates/** - Note templates for different contexts

**Pros:**
- Simpler to implement
- No external dependencies
- Works entirely within Claude Code
- Easy to version control

**Cons:**
- One-way communication (Claude → Obsidian)
- No real-time sync from Obsidian → Claude
- Requires Obsidian vault to be accessible filesystem

### Option 2: MCP Server Integration (Future Enhancement)

**Location:** `.claude/mcp-servers/obsidian-mcp/`

**Components:**
1. MCP server using FastMCP or TypeScript SDK
2. Bidirectional communication protocol
3. Real-time vault change detection
4. Note graph traversal and semantic search

**Pros:**
- True bidirectional sync
- Real-time updates
- Advanced features (graph queries, backlinks)
- Integrates with Obsidian plugin ecosystem

**Cons:**
- More complex setup
- Requires MCP server process running
- Additional maintenance overhead

**Recommendation:** Start with Option 1 (Skill-based), migrate to Option 2 after validating workflow.

---

## Primitive Design

### Commands (6 total)

#### 1. Note Creation
- **`/note-create [title]`** - Create a new note in the vault
  - Prompts for: Category (daily, architecture, decisions, learnings, tasks)
  - Auto-generates frontmatter with tags, date, project
  - Opens note for editing

#### 2. Note Search
- **`/note-search [query]`** - Search vault for notes
  - Full-text search across all markdown files
  - Returns ranked results with snippets
  - Offers to load context into conversation

#### 3. Decision Log
- **`/decision-log [title]`** - Log architectural decision
  - Uses ADR (Architecture Decision Record) template
  - Auto-links to related project files
  - Tags with date and decision category

#### 4. Daily Note
- **`/daily-note`** - Create or open today's daily note
  - Auto-generates daily note structure
  - Includes: Tasks, Learnings, Time log, Context
  - Links to active work items

#### 5. Vault Sync
- **`/vault-sync`** - Manual sync to Obsidian vault
  - Commits current session context to vault
  - Updates project index
  - Creates backlinks to relevant notes

#### 6. Context Load
- **`/context-load [note-name]`** - Load note into conversation context
  - Reads specified note
  - Includes linked notes (1 level deep)
  - Primes conversation with note content

---

### Agents (2 total)

#### 1. **@obsidian-organizer** (Sonnet)
- **Purpose:** Organize and structure vault notes
- **Triggers:** When vault becomes cluttered or on command
- **Actions:**
  - Analyzes note structure
  - Suggests tagging improvements
  - Reorganizes folder hierarchy
  - Identifies orphaned notes
  - Creates MOCs (Maps of Content)

#### 2. **@knowledge-curator** (Sonnet)
- **Purpose:** Extract learnings from sessions and curate knowledge
- **Triggers:** End of coding session or on command
- **Actions:**
  - Reviews session transcript
  - Extracts key decisions and learnings
  - Creates/updates relevant notes
  - Links new knowledge to existing notes
  - Maintains knowledge graph coherence

---

### Hooks (4 events)

#### SessionStart Hook
**File:** `.claude/hooks/session-start/obsidian-context-load.sh`

```bash
# Load recent notes and today's daily note
# Prime context with current project state
# Check for pending tasks in vault
```

**Actions:**
1. Open today's daily note (create if doesn't exist)
2. Load recent project-related notes (last 3 days)
3. Check for flagged tasks or TODOs
4. Display vault summary (note count, recent changes)

#### Stop Hook
**File:** `.claude/hooks/stop/obsidian-session-log.sh`

```bash
# Log current session to vault
# Update daily note with progress
# Sync work status to vault
```

**Actions:**
1. Append session summary to daily note
2. Update work-status.md in vault
3. Tag notes created/modified during session
4. Commit changes to vault git repo (if applicable)

#### SessionEnd Hook
**File:** `.claude/hooks/session-end/obsidian-knowledge-sync.sh`

```bash
# Extract learnings and sync to vault
# Trigger @knowledge-curator agent
# Create session retrospective note
```

**Actions:**
1. Run @knowledge-curator to extract learnings
2. Create session retrospective (if significant work done)
3. Update project index with new references
4. Backup vault (if configured)

#### PreToolUse Hook (Optional)
**File:** `.claude/hooks/pre-tool-use/obsidian-decision-capture.sh`

```bash
# Capture architectural decisions before major changes
# Auto-log to decision journal
```

**Actions:**
1. Detect major architectural changes (file structure, dependencies)
2. Prompt for decision rationale
3. Auto-create decision record
4. Link to affected files

---

### Skills (1 core skill)

#### **obsidian-vault**
**File:** `.claude/skills/obsidian-vault/SKILL.md`

**Description:** Comprehensive Obsidian vault management for persistent project knowledge

**Capabilities:**
- Create, read, update notes
- Search vault with filters (tags, dates, folders)
- Generate note templates
- Maintain vault structure
- Export/import knowledge
- Graph visualization (text-based)
- Backlink management

**Triggers:**
- User requests note operations
- Automatic during hooks
- Invoked by other agents for knowledge retrieval

**Model:** Sonnet (balanced performance and cost)

---

## Directory Structure

```
.claude/
├── skills/
│   └── obsidian-vault/
│       ├── SKILL.md                      # Main skill definition
│       ├── scripts/
│       │   ├── vault-operations.js       # Core vault operations
│       │   ├── note-templates.js         # Template generators
│       │   ├── search-engine.js          # Vault search logic
│       │   └── graph-builder.js          # Knowledge graph utils
│       ├── templates/
│       │   ├── daily-note.md             # Daily note template
│       │   ├── adr.md                    # Architecture Decision Record
│       │   ├── learning.md               # Learning note template
│       │   ├── task.md                   # Task note template
│       │   └── project-index.md          # Project index template
│       ├── config/
│       │   ├── vault-settings.json       # Vault configuration
│       │   └── note-categories.yaml      # Note taxonomy
│       └── README.md                     # Setup guide
├── commands/
│   ├── note-create.md                    # /note-create command
│   ├── note-search.md                    # /note-search command
│   ├── decision-log.md                   # /decision-log command
│   ├── daily-note.md                     # /daily-note command
│   ├── vault-sync.md                     # /vault-sync command
│   └── context-load.md                   # /context-load command
├── hooks/
│   ├── session-start/
│   │   └── obsidian-context-load.sh
│   ├── stop/
│   │   └── obsidian-session-log.sh
│   ├── session-end/
│   │   └── obsidian-knowledge-sync.sh
│   └── pre-tool-use/
│       └── obsidian-decision-capture.sh  # Optional
├── agents/
│   ├── obsidian-organizer.md             # @obsidian-organizer agent
│   └── knowledge-curator.md              # @knowledge-curator agent
└── docs/
    └── obsidian-integration-guide.md     # User documentation
```

---

## Configuration

### Vault Settings
**File:** `.claude/skills/obsidian-vault/config/vault-settings.json`

```json
{
  "vaultPath": "/path/to/obsidian/vault",
  "projectFolder": "Projects/consulting-co",
  "dailyNotesFolder": "Daily Notes",
  "decisionsFolder": "Decisions",
  "learningsFolder": "Learnings",
  "templatesFolder": "Templates",
  "autoSync": true,
  "syncOnSessionStart": true,
  "syncOnSessionEnd": true,
  "createDailyNote": true,
  "knowledgeGraphEnabled": true,
  "backlinksEnabled": true,
  "tagPrefix": "cc",
  "defaultTemplate": "daily-note",
  "searchDepth": 2
}
```

### Note Categories
**File:** `.claude/skills/obsidian-vault/config/note-categories.yaml`

```yaml
categories:
  daily:
    folder: "Daily Notes"
    template: "daily-note.md"
    tags: ["daily", "journal"]

  architecture:
    folder: "Decisions/Architecture"
    template: "adr.md"
    tags: ["architecture", "decision"]

  learnings:
    folder: "Learnings"
    template: "learning.md"
    tags: ["learning", "knowledge"]

  tasks:
    folder: "Tasks"
    template: "task.md"
    tags: ["task", "todo"]

  meetings:
    folder: "Meetings"
    template: "meeting.md"
    tags: ["meeting", "notes"]
```

---

## Note Templates

### Daily Note Template
**File:** `.claude/skills/obsidian-vault/templates/daily-note.md`

```markdown
---
date: {{date}}
project: {{project}}
tags: [daily, {{project-tag}}]
---

# {{date-formatted}}

## Context
<!-- What am I working on today? -->

## Tasks
- [ ]

## Decisions Made
<!-- Link to decision records -->

## Learnings
<!-- What did I learn today? -->

## Time Log
| Start | End | Activity | Hours |
|-------|-----|----------|-------|
|       |     |          |       |

## Notes
<!-- Additional context, thoughts, observations -->

## Links
<!-- Related notes, files, PRs -->

---

**Created by:** Claude Code
**Session:** {{session-id}}
```

### Architecture Decision Record Template
**File:** `.claude/skills/obsidian-vault/templates/adr.md`

```markdown
---
date: {{date}}
status: proposed|accepted|deprecated|superseded
tags: [adr, architecture, decision]
project: {{project}}
---

# ADR-{{number}}: {{title}}

## Status
{{status}} - {{date}}

## Context
<!-- What is the issue we're addressing? -->

## Decision
<!-- What is the change we're proposing? -->

## Consequences
### Positive
-

### Negative
-

### Neutral
-

## Alternatives Considered
1.

## Implementation Notes
<!-- How will this be implemented? -->

## Related Decisions
<!-- Links to related ADRs -->

---

**Created by:** Claude Code
**Author:** {{author}}
```

---

## Integration Workflows

### Workflow 1: Session Start
1. User runs `claude` in project directory
2. **SessionStart hook** triggers
3. Obsidian context load script runs:
   - Creates/opens today's daily note
   - Loads recent project notes (last 3 days)
   - Checks for pending tasks in vault
4. Claude displays vault summary
5. User begins work with full context

### Workflow 2: Making an Architectural Decision
1. User discusses architecture change with Claude
2. Claude detects significant decision
3. **PreToolUse hook** (optional) prompts for decision rationale
4. User runs `/decision-log "Use Lambda instead of ECS"`
5. Claude creates ADR using template
6. ADR is linked to affected files
7. Decision logged in daily note

### Workflow 3: Session End Knowledge Capture
1. User completes work, types "stop" or ends session
2. **SessionEnd hook** triggers
3. **@knowledge-curator** agent activates:
   - Reviews session transcript
   - Extracts key learnings
   - Creates/updates learning notes
   - Links to related concepts
4. Session retrospective created
5. Project index updated
6. Vault synced (git commit if enabled)

### Workflow 4: Searching Past Knowledge
1. User asks: "How did we solve the authentication issue last month?"
2. User runs `/note-search authentication`
3. Claude searches vault:
   - Finds 5 relevant notes
   - Displays snippets
4. User runs `/context-load "Auth Architecture Decision"`
5. Claude loads note + linked notes
6. Conversation continues with full context

---

## Technical Implementation

### Core Dependencies

**Node.js Libraries:**
```json
{
  "dependencies": {
    "glob": "^10.3.10",
    "gray-matter": "^4.0.3",
    "marked": "^11.1.0",
    "fuse.js": "^7.0.0",
    "date-fns": "^3.0.0",
    "yaml": "^2.3.4"
  }
}
```

### Vault Operations Script (Simplified)
**File:** `.claude/skills/obsidian-vault/scripts/vault-operations.js`

```javascript
const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const glob = require('glob');
const Fuse = require('fuse.js');

class ObsidianVault {
  constructor(vaultPath) {
    this.vaultPath = vaultPath;
    this.config = this.loadConfig();
  }

  // Create note from template
  createNote(title, category = 'daily') {
    const template = this.loadTemplate(category);
    const frontmatter = this.generateFrontmatter(title, category);
    const content = this.renderTemplate(template, frontmatter);
    const filePath = this.getNotePath(title, category);

    fs.writeFileSync(filePath, content);
    return filePath;
  }

  // Search vault
  searchNotes(query, options = {}) {
    const notes = this.getAllNotes();
    const fuse = new Fuse(notes, {
      keys: ['title', 'content', 'tags'],
      threshold: 0.3,
      includeScore: true
    });

    return fuse.search(query);
  }

  // Get all notes
  getAllNotes() {
    const pattern = path.join(this.vaultPath, '**/*.md');
    const files = glob.sync(pattern);

    return files.map(file => {
      const content = fs.readFileSync(file, 'utf8');
      const parsed = matter(content);
      return {
        path: file,
        title: path.basename(file, '.md'),
        frontmatter: parsed.data,
        content: parsed.content,
        tags: parsed.data.tags || []
      };
    });
  }

  // Load note with backlinks
  loadNoteWithLinks(notePath, depth = 1) {
    const note = this.loadNote(notePath);
    if (depth === 0) return note;

    const links = this.extractLinks(note.content);
    const linkedNotes = links.map(link =>
      this.loadNoteWithLinks(link, depth - 1)
    );

    return { ...note, linkedNotes };
  }

  // Additional methods...
}

module.exports = ObsidianVault;
```

---

## Security & Permissions

### Vault Access Control
- Vault path must be explicitly configured in `vault-settings.json`
- No automatic vault discovery (prevent accidental access)
- Read-only mode available via config flag
- Sensitive notes can be excluded via `.claudeignore` pattern

### Data Privacy
- All vault operations logged to `.claude/logs/obsidian-operations.log`
- No external API calls (fully local)
- Vault contents never sent to external services
- Optional encryption for sensitive notes (future enhancement)

### Permission Model
```json
{
  "obsidianVault": {
    "read": true,
    "write": true,
    "delete": false,
    "allowedFolders": [
      "Projects/consulting-co",
      "Daily Notes",
      "Decisions",
      "Learnings"
    ],
    "deniedFolders": [
      "Private",
      "Archive"
    ]
  }
}
```

---

## Timeline & Deliverables

### Phase 1: Foundation (Week 1)
**Deliverables:**
- [ ] Directory structure created
- [ ] Core skill definition (SKILL.md)
- [ ] Basic vault operations script
- [ ] Note templates (daily, ADR, learning)
- [ ] Configuration files
- [ ] `/note-create` command
- [ ] `/note-search` command

**Estimated Effort:** 8-12 hours

### Phase 2: Automation (Week 2)
**Deliverables:**
- [ ] SessionStart hook (context loading)
- [ ] Stop hook (session logging)
- [ ] SessionEnd hook (knowledge sync)
- [ ] @knowledge-curator agent
- [ ] `/decision-log` command
- [ ] `/daily-note` command
- [ ] `/vault-sync` command
- [ ] `/context-load` command

**Estimated Effort:** 12-16 hours

### Phase 3: Enhancement (Week 3)
**Deliverables:**
- [ ] @obsidian-organizer agent
- [ ] PreToolUse hook (decision capture)
- [ ] Advanced search (tags, dates, folders)
- [ ] Backlink management
- [ ] Graph visualization (text-based)
- [ ] Documentation
- [ ] Testing & validation

**Estimated Effort:** 8-12 hours

### Phase 4: MCP Migration (Future)
**Deliverables:**
- [ ] MCP server implementation
- [ ] Bidirectional sync
- [ ] Real-time vault monitoring
- [ ] Advanced graph queries
- [ ] Plugin ecosystem integration

**Estimated Effort:** 24-32 hours

---

## Success Metrics

### Adoption Metrics
- [ ] Daily note created automatically every session
- [ ] At least 3 decision records created per week
- [ ] 80%+ of sessions include vault interaction
- [ ] Knowledge search used 5+ times per week

### Quality Metrics
- [ ] Vault remains organized (< 5% orphaned notes)
- [ ] Notes are properly tagged (95%+ compliance)
- [ ] Backlinks maintained (automatic validation)
- [ ] Knowledge graph coherent (validated by @obsidian-organizer)

### Efficiency Metrics
- [ ] 50% reduction in "how did we solve X?" questions
- [ ] Context loaded in < 2 seconds
- [ ] Search results returned in < 1 second
- [ ] Session start < 5 seconds (with context loading)

---

## Risks & Mitigations

### Risk 1: Vault Corruption
**Mitigation:**
- Automatic git-based versioning
- Pre-write validation
- Backup before destructive operations
- Read-only mode for testing

### Risk 2: Performance Degradation (Large Vaults)
**Mitigation:**
- Implement search indexing
- Lazy loading of linked notes
- Configurable search depth
- Folder-based scope limiting

### Risk 3: Sync Conflicts
**Mitigation:**
- Use append-only operations when possible
- Timestamp-based conflict resolution
- Manual merge prompts for conflicts
- Git integration for version control

### Risk 4: User Adoption
**Mitigation:**
- Start with minimal friction (auto-daily notes)
- Show immediate value (context loading)
- Progressive enhancement (add features as needed)
- Documentation and examples

---

## Integration with Existing .claude Setup

### Compatibility with Current Skills
- **revstar-quickstart-workflow**: Can log project scope to vault
- **aws-cdk-diagram**: Can save diagrams as notes with explanations
- **git-wizard**: Can log recovery actions to decision records

### Hook Orchestration
Current hooks + Obsidian hooks = combined workflow

**Example SessionStart Hook Sequence:**
1. Git status check (existing)
2. Obsidian context load (new)
3. Load recent PRs (existing)
4. Display combined dashboard

### Command Namespacing
All Obsidian commands prefixed with `/note-*` or `/vault-*` to avoid conflicts

---

## Configuration Quick Start

### Step 1: Create Vault
```bash
# Create or link Obsidian vault
mkdir -p ~/obsidian-vaults/consulting-co
```

### Step 2: Configure Settings
```bash
# Edit vault settings
code .claude/skills/obsidian-vault/config/vault-settings.json
# Set vaultPath to your Obsidian vault
```

### Step 3: Initialize Vault Structure
```bash
# Run initialization command
/vault-init
# Creates folder structure and templates
```

### Step 4: Test Integration
```bash
# Create first daily note
/daily-note
# Verify note created in vault
# Open in Obsidian to confirm
```

---

## Future Enhancements

### Planned Features (Post-MVP)
1. **MCP Server** - Bidirectional sync with Obsidian plugin
2. **Graph Queries** - Advanced graph traversal and pattern matching
3. **Semantic Search** - Embeddings-based similarity search
4. **Voice Notes** - TTS integration for verbal notes
5. **Calendar Integration** - Sync with Google Calendar, Outlook
6. **Task Management** - Obsidian tasks plugin integration
7. **Dataview Queries** - Execute Dataview queries from Claude
8. **Canvas Support** - Interact with Obsidian canvas boards
9. **Mobile Sync** - Mobile vault synchronization
10. **AI Summarization** - Auto-summarize long notes

### Research Areas
- Integration with Obsidian community plugins
- Real-time collaborative editing
- Multi-vault support
- Cloud vault synchronization (Obsidian Sync compatible)

---

## Approval & Next Steps

### Implementation Checklist
- [ ] Review and approve this integration plan
- [ ] Confirm vault path and structure
- [ ] Decide on Phase 1 vs. Full implementation
- [ ] Schedule implementation timeline
- [ ] Assign owner for vault management
- [ ] Test Obsidian vault access

### Questions for Stakeholder
1. Do you already have an Obsidian vault for this project?
2. What is the expected vault size (number of notes)?
3. Are there existing note templates or conventions?
4. Should this integrate with Obsidian git plugin?
5. Is MCP server integration desired for Phase 1?
6. What is the priority order for commands/hooks?

---

**Approved and ready for implementation!**

---

**Version:** 1.0
**Author:** Claude Code Integration Team
**Based on:** VIBE Planning Framework
**Last Updated:** November 13, 2025
