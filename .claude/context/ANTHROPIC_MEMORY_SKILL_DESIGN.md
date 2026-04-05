# Anthropic Memory Tool Skill - Design Document

**Created**: 2026-01-11
**Based On**: Existing Graphiti/CORE agents (simplified)
**Purpose**: Replace complex Neo4j/CORE setup with simple Anthropic Memory Tool

---

## 📋 Executive Summary

We're simplifying from a complex 5-system integration (Observability, Langfuse, Graphiti, Obsidian, Hooks) to a **single Anthropic Memory Tool skill** that captures the best patterns without the infrastructure overhead.

## 🎯 What We're Keeping from CORE

### High-Level Patterns (Preserve)

1. **Entity Extraction** → Store entities in memory files
2. **Session Tracking** → Session-based memory organization
3. **Relationship Awareness** → Document connections in markdown
4. **Obsidian Integration** → Export memory to Obsidian vault
5. **Search Capability** → Unified search across memory files
6. **Hook Integration** → Automatic memory storage on session end

### Infrastructure to Abandon

- ❌ Neo4j database
- ❌ Graphiti MCP server
- ❌ CORE Memory backend
- ❌ Complex multi-system orchestration
- ❌ Real-time observability dashboard

## 🏗️ New Architecture

```
┌─────────────────────────────────────────────┐
│     Anthropic Memory Tool Skill             │
├─────────────────────────────────────────────┤
│                                             │
│  Components:                                │
│  1. Memory Storage (file-based)             │
│     └─ /memories directory                  │
│                                             │
│  2. Entity Extraction (Claude-powered)      │
│     └─ Extract entities from conversations  │
│                                             │
│  3. Session Management                      │
│     └─ Track session context               │
│                                             │
│  4. Obsidian Export                         │
│     └─ Generate markdown summaries         │
│                                             │
│  5. Unified Search                          │
│     └─ Search across memory + Obsidian     │
│                                             │
└─────────────────────────────────────────────┘
```

## 📁 File Structure

```
.claude/
├── skills/
│   └── anthropic-memory/
│       ├── skill.md                    # Main skill definition
│       ├── config/
│       │   └── memory-config.yaml      # Configuration
│       ├── scripts/
│       │   ├── memory_executor.py      # Execute memory operations
│       │   ├── entity_extractor.py     # Extract entities
│       │   ├── obsidian_exporter.py    # Export to Obsidian
│       │   └── unified_search.py       # Search functionality
│       └── README.md                   # Documentation
│
├── hooks/
│   └── memory_ingest_hook.py          # Stop hook integration
│
└── memories/
    ├── sessions/                       # Session-specific memories
    │   ├── 2026-01-11_session1.md
    │   └── 2026-01-11_session2.md
    ├── patterns/                       # Code patterns (like code-review)
    │   ├── concurrency.md
    │   └── architecture.md
    ├── entities/                       # Extracted entities
    │   ├── technologies.md
    │   ├── files.md
    │   └── concepts.md
    └── index.md                        # Master index
```

## 🎨 Key Features

### 1. Session-Based Memory

**Pattern from**: GRAPHITI_AGENT.md

Each session gets a memory file:

```markdown
# Session 2026-01-11-session1

## Summary
User worked on authentication implementation

## Entities Discovered
- **File**: auth-middleware.ts
- **Technology**: JWT, OAuth2
- **Concept**: Token refresh rotation

## Tools Used
- Read (3 times)
- Edit (2 times)
- Bash (1 time)

## Key Learnings
- Implemented httpOnly cookie pattern for security
- Used refresh token rotation to prevent theft

## Related Sessions
- [[2026-01-10-session3]] - Initial auth design
```

### 2. Entity Extraction

**Pattern from**: GRAPHITI_AGENT.md (simplified)

Use Claude to extract entities:

```python
# entity_extractor.py
def extract_entities(conversation_transcript: str) -> dict:
    """Use Claude to extract entities from conversation"""

    prompt = """
    Extract entities from this conversation:
    - Files (code files mentioned)
    - Technologies (frameworks, libraries)
    - Concepts (patterns, techniques)
    - Decisions (architectural choices)

    Return JSON format.
    """

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content)
```

### 3. Unified Search

**Pattern from**: search-knowledge.md

Search across memory files + Obsidian:

```python
# unified_search.py
def unified_search(query: str):
    """Search both memory files and Obsidian vault"""

    # 1. Search memory files (Anthropic Memory Tool)
    memory_results = search_memory_files(query)

    # 2. Search Obsidian vault
    obsidian_results = search_obsidian(query)

    # 3. Merge and rank
    return merge_results(memory_results, obsidian_results)
```

### 4. Obsidian Integration

**Pattern from**: OBSIDIAN_AGENT.md

Auto-generate daily summaries:

```python
# obsidian_exporter.py
def export_to_obsidian(session_id: str):
    """Export session memory to Obsidian vault"""

    # Read session memory
    session = read_memory(f"/memories/sessions/{session_id}.md")

    # Generate daily summary
    daily_note = generate_daily_summary(session)

    # Write to Obsidian
    write_obsidian_note(daily_note)
```

### 5. Hook Integration

**Pattern from**: INTEGRATION_ORCHESTRATOR.md

Auto-trigger on session end:

```json
// .claude/settings.local.json
{
  "hooks": {
    "Stop": [
      {
        "command": "uv run .claude/hooks/memory_ingest_hook.py",
        "timeout": 10
      }
    ]
  }
}
```

## 💻 Skill Definition

```markdown
---
name: anthropic-memory
description: Intelligent memory system using Anthropic's native memory tool
tools: []
model: sonnet
---

You are a memory management specialist using Anthropic's native Memory Tool.

## Core Capabilities

1. **Store Session Memories**: Save conversation summaries with entity extraction
2. **Search Knowledge**: Find relevant memories across sessions
3. **Entity Tracking**: Maintain entity index (files, technologies, concepts)
4. **Pattern Recognition**: Identify and store recurring patterns
5. **Obsidian Integration**: Export to Obsidian vault for human curation

## Memory Organization

### Directories
- `/memories/sessions/` - Individual session summaries
- `/memories/patterns/` - Recurring patterns and learnings
- `/memories/entities/` - Entity registry
- `/memories/index.md` - Master index

### File Format
All files use markdown with YAML frontmatter:
```markdown
---
date: 2026-01-11
session_id: abc123
tags: [authentication, security]
entities: [JWT, OAuth2, auth-middleware.ts]
---

# Summary

...
```

## Automatic Behaviors

### On Session Start
- Check memory for related context
- Load relevant patterns
- Search for mentioned entities

### On Session End
- Extract entities from conversation
- Store session summary
- Update entity index
- Export to Obsidian

## Commands

- `/memory-search [query]` - Search across all memories
- `/memory-view [path]` - View specific memory file
- `/memory-entities` - List all tracked entities
- `/memory-patterns` - View learned patterns

## Integration Points

1. **Anthropic Memory Tool** - Native file-based storage
2. **Obsidian** - Markdown export for human curation
3. **Stop Hook** - Automatic ingestion
4. **Context Management** - Automatic optimization
```

## 🛠️ Implementation Steps

### Phase 1: Core Memory Executor (Week 1)

```python
# memory_executor.py
from anthropic import Anthropic
from pathlib import Path
import json

class MemoryExecutor:
    def __init__(self, memory_dir: Path = Path("./memories")):
        self.memory_dir = memory_dir
        self.client = Anthropic()

    def create_memory(self, path: str, content: str):
        """Create or update memory file using Anthropic API"""
        # Implementation

    def view_memory(self, path: str) -> str:
        """View memory file"""
        # Implementation

    def search_memories(self, query: str) -> list:
        """Search across memory files"""
        # Implementation
```

### Phase 2: Entity Extraction (Week 1)

```python
# entity_extractor.py
def extract_from_transcript(transcript: str) -> dict:
    """Extract entities using Claude"""

    extraction_prompt = """
    Extract these entity types:
    1. Files (with paths)
    2. Technologies (frameworks, libraries, tools)
    3. Concepts (patterns, techniques, approaches)
    4. Decisions (choices made, rationale)

    Return as JSON.
    """

    # Use Claude to extract
    # Store in /memories/entities/
```

### Phase 3: Hook Integration (Week 2)

```python
# memory_ingest_hook.py
def ingest_session(session_dir: Path):
    """Called by Stop hook to ingest session"""

    # 1. Read chat transcript
    transcript = read_transcript(session_dir)

    # 2. Extract entities
    entities = extract_entities(transcript)

    # 3. Store session memory
    store_memory(transcript, entities)

    # 4. Update indices
    update_entity_index(entities)

    # 5. Export to Obsidian
    export_to_obsidian(session_dir)
```

### Phase 4: Search & Retrieval (Week 2)

```python
# unified_search.py
def search(query: str, sources=["memory", "obsidian"]):
    """Unified search across sources"""

    results = []

    if "memory" in sources:
        memory_results = search_memory_files(query)
        results.extend(memory_results)

    if "obsidian" in sources:
        obsidian_results = search_obsidian_vault(query)
        results.extend(obsidian_results)

    return rank_and_merge(results)
```

### Phase 5: Obsidian Integration (Week 3)

```python
# obsidian_exporter.py
def export_session(session_id: str, obsidian_path: Path):
    """Export session to Obsidian vault"""

    # Read session memory
    session = load_session(session_id)

    # Format for Obsidian
    note = format_obsidian_note(session)

    # Write to vault
    (obsidian_path / f"sessions/{session_id}.md").write_text(note)

    # Update daily note
    update_daily_note(session, obsidian_path)
```

## 📊 Comparison: Old vs New

| Feature | Old (CORE/Graphiti) | New (Anthropic Memory) |
|---------|---------------------|------------------------|
| **Storage** | Neo4j database | File-based markdown |
| **Setup** | Complex (Docker, services) | Simple (just files) |
| **Search** | Cypher queries | Claude-powered semantic |
| **Entities** | Graph nodes | Markdown lists |
| **Relationships** | Graph edges | Document links |
| **Cost** | $100-300/mo infrastructure | $0 infrastructure |
| **Maintenance** | High | Low |
| **Scalability** | High (database) | Medium (filesystem) |
| **Portability** | Low (requires Neo4j) | High (just files) |

## 🎯 Integration Services to Preserve

### 1. Obsidian Export ✅
- Keep the markdown generation
- Simplify format (no graph data)
- Direct file writes

### 2. Entity Tracking ✅
- Keep entity extraction
- Store in simple markdown lists
- No graph relationships

### 3. Session Tracking ✅
- Keep session summaries
- File-based instead of graph nodes
- Simple parent/child references

### 4. Search ✅
- Keep unified search
- Use Claude for semantic matching
- Simple grep for file search

### 5. Hook Integration ✅
- Keep Stop hook pattern
- Simplify to single script
- No parallel processing needed

## 🚫 What We're Removing

- ❌ Neo4j database and browser
- ❌ Graphiti MCP server
- ❌ Real-time observability dashboard
- ❌ Langfuse integration
- ❌ Complex multi-system orchestration
- ❌ Graph relationship tracking
- ❌ Temporal queries
- ❌ Performance tier classification

## 📝 Next Steps

1. ✅ Review this design
2. ⏳ Create skill structure in `.claude/skills/anthropic-memory/`
3. ⏳ Implement memory_executor.py
4. ⏳ Implement entity_extractor.py
5. ⏳ Create Stop hook integration
6. ⏳ Test with sample session
7. ⏳ Add Obsidian export
8. ⏳ Implement unified search
9. ⏳ Document and deploy

## 🔗 Reference Documents

### From consulting-co
- `.claude/agents/GRAPHITI_AGENT.md` - Entity extraction pattern
- `.claude/agents/INTEGRATION_ORCHESTRATOR.md` - Hook cascade pattern
- `.claude/agents/OBSIDIAN_AGENT.md` - Markdown export pattern
- `.claude/commands/search-knowledge.md` - Unified search pattern
- `.claude/skills/knowledge-sync/SKILL.md` - Sync architecture

### From Obsidian docs
- `desktop/obsidian/Gbautomation/memory/Memory-System-Index.md`
- `desktop/obsidian/Gbautomation/memory/Anthropic-Memory-Tool-Guide.md`
- `desktop/obsidian/Gbautomation/memory/Code-Bug-Agent-Example.md`
- `desktop/obsidian/Gbautomation/memory/Memory-Best-Practices.md`

---

**Status**: 📋 Design Phase
**Next**: Implementation
**Timeline**: 3 weeks to production
