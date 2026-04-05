# Anthropic Memory Tool Skill

A simple, file-based memory management system using Anthropic's native Memory Tool, extracting high-level patterns from CORE Memory/Graphiti without the infrastructure complexity.

## 🎯 Purpose

Provide session-based memory, entity tracking, and knowledge organization using markdown files instead of graph databases. Perfect for teams who want the benefits of memory systems without running Neo4j.

## ✨ Features

- **Session Tracking** - Auto-generate summaries for each Claude session
- **Entity Extraction** - Identify files, technologies, concepts, and decisions
- **Pattern Recognition** - Detect recurring themes across sessions
- **Obsidian Integration** - Export to Obsidian vault for human curation
- **Unified Search** - Semantic search across all memories
- **Zero Infrastructure** - Just markdown files, no databases

## 📁 Structure

```
.claude/skills/anthropic-memory/
├── skill.md              # Main skill definition
├── config/
│   └── memory-config.yaml    # Configuration
├── scripts/
│   ├── memory_executor.py    # Core memory operations
│   ├── entity_extractor.py   # Entity extraction via Claude
│   ├── obsidian_exporter.py  # Export to Obsidian
│   └── unified_search.py     # Search functionality
└── README.md             # This file

.claude/memories/
├── sessions/             # Per-session summaries
├── patterns/             # Recurring patterns
├── entities/             # Entity registry
└── index.md             # Master index
```

## 🚀 Quick Start

### 1. Installation

No installation needed - the skill uses built-in Claude capabilities.

### 2. Configuration

Edit `.claude/skills/anthropic-memory/config/memory-config.yaml`:

```yaml
memory_base_path: .claude/memories
obsidian_vault_path: ~/Desktop/obsidian/Gbautomation
enable_entity_extraction: true
enable_obsidian_export: true
```

### 3. Enable Stop Hook

Add to `.claude/settings.local.json`:

```json
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

### 4. Use Commands

**Search memories:**
```
/memory-search authentication patterns
```

**View specific memory:**
```
/memory-view sessions/2026-01-11_session1.md
```

**List entities:**
```
/memory-entities
```

**View patterns:**
```
/memory-patterns
```

## 📖 Usage Examples

### Automatic Session Memory

Every Claude session automatically creates a memory:

```markdown
---
date: 2026-01-11
session_id: abc123
tags: [api-design, rest]
entities: [FastAPI, Pydantic, routes.py]
---

# Session Summary

## Context
User designed a new REST API for product management.

## Entities Discovered
- **File**: app/products/routes.py
- **Technology**: FastAPI, Pydantic
- **Concept**: RESTful design, CRUD operations

## Tools Used
- Write (5 times) - Created new files
- Read (3 times) - Reviewed existing code
- Bash (2 times) - Ran tests

## Key Learnings
- Used Pydantic for request validation
- Implemented async endpoints for better performance
- Added comprehensive error handling

## Related Sessions
- [[2026-01-10-session5]] - Initial API planning
```

### Search Memories

```python
# Search for authentication-related memories
/memory-search authentication security JWT

# Returns:
# 1. sessions/2026-01-11_session1.md - Auth implementation (95% match)
# 2. patterns/authentication.md - Auth patterns (87% match)
# 3. sessions/2026-01-08_session3.md - JWT setup (76% match)
```

### Entity Tracking

View all tracked entities:

```
/memory-entities

# Returns:
# Files (23):
#   - app/auth/middleware.ts
#   - app/users/service.py
#   - ...
#
# Technologies (15):
#   - FastAPI, JWT, OAuth2, PostgreSQL, ...
#
# Concepts (12):
#   - Token refresh rotation, RBAC, API versioning, ...
```

### Pattern Detection

```
/memory-patterns

# Returns:
# Detected Patterns:
#
# 1. Authentication (5 occurrences)
#    - JWT token-based auth
#    - Refresh token rotation
#    - httpOnly cookies
#
# 2. Error Handling (4 occurrences)
#    - Custom exception classes
#    - Centralized error handlers
#    - Structured error responses
```

## 🔧 Configuration Options

### Memory Paths

```yaml
memory_base_path: .claude/memories
obsidian_vault_path: ~/Desktop/obsidian/Gbautomation
```

### Entity Extraction

```yaml
enable_entity_extraction: true
entity_extraction_model: claude-haiku-4
entity_types:
  - files
  - technologies
  - concepts
  - decisions
```

### Pattern Detection

```yaml
enable_pattern_detection: true
pattern_similarity_threshold: 0.75
min_occurrences_for_pattern: 3
```

### Obsidian Export

```yaml
enable_obsidian_export: true
export_on_session_end: true
create_backlinks: true
```

### Search Settings

```yaml
search_result_limit: 10
semantic_search_enabled: true
search_snippet_length: 200
```

## 🧠 How It Works

### On Session End (Stop Hook):

```
1. Read conversation transcript from .claude/transcripts/
2. Extract entities using Claude subagent:
   - Files mentioned
   - Technologies used
   - Concepts discussed
   - Decisions made
3. Generate session summary with metadata
4. Update entity index
5. Detect patterns (if ≥3 occurrences)
6. Export to Obsidian vault
```

### On Memory Search:

```
1. User queries: /memory-search authentication
2. Search session files in .claude/memories/sessions/
3. Search pattern files in .claude/memories/patterns/
4. Search entity index in .claude/memories/entities/
5. Rank results by semantic similarity
6. Return top N matches with context
```

## 📊 Comparison: CORE vs Anthropic Memory

| Feature | CORE Memory | Anthropic Memory |
|---------|-------------|------------------|
| **Storage** | Neo4j database | Markdown files |
| **Setup** | Docker, services | Just files |
| **Search** | Cypher queries | Claude semantic search |
| **Entities** | Graph nodes | Markdown lists |
| **Relationships** | Graph edges | Wiki links |
| **Cost** | $100-300/mo | $0 infrastructure |
| **Maintenance** | High | Low |
| **Scalability** | High | Medium |
| **Portability** | Low | High |

## 🔐 Security

### Path Validation
All paths validated to prevent traversal attacks:
```python
def validate_memory_path(path: str):
    # Ensures path stays within .claude/memories/
```

### Memory Poisoning Prevention
- Never execute code from memories
- Sanitize all user input
- Validate file formats
- Limit file sizes (10MB max)

### Data Privacy
- All data stored locally
- No cloud storage required
- User controls all exports
- No external transmission (except Obsidian)

## 🎨 Integration with Other Agents

### With OBSIDIAN_AGENT
- Export session summaries to Obsidian vault
- Create daily notes with session links
- Use wiki-style backlinks

### With Meta-Agent
- Use meta-agent to generate new memory extraction patterns
- Create specialized entity extractors

### With AI_CODEBASE_OPTIMIZER
- Store codebase optimization decisions
- Track refactoring patterns
- Document architectural choices

## 📈 Success Metrics

Track these metrics to measure effectiveness:

```yaml
Metrics:
  memory_coverage: 100%        # Sessions with summaries
  entity_accuracy: 90%+        # Correctly extracted entities
  search_relevance: 85%+       # Useful search results
  pattern_detection: TBD       # Patterns identified
  export_success: 100%         # Successful Obsidian exports
```

## 🐛 Troubleshooting

### Memory Not Created

Check Stop hook fired:
```bash
cat .claude/logs/memory.log
```

### Entity Extraction Failed

Check Claude API key:
```bash
echo $ANTHROPIC_API_KEY
```

### Obsidian Export Failed

Verify vault path:
```bash
ls ~/Desktop/obsidian/Gbautomation
```

### Search Returns No Results

Rebuild index:
```bash
uv run .claude/skills/anthropic-memory/scripts/rebuild_index.py
```

## 📚 Related Documentation

### From consulting-co
- `.claude/agents/GRAPHITI_AGENT.md` - Entity extraction patterns
- `.claude/agents/OBSIDIAN_AGENT.md` - Markdown export patterns
- `.claude/commands/search-knowledge.md` - Unified search patterns

### From Obsidian Vault
- `desktop/obsidian/Gbautomation/memory/Memory-System-Index.md`
- `desktop/obsidian/Gbautomation/memory/Anthropic-Memory-Tool-Guide.md`

### Design Documents
- `.claude/context/ANTHROPIC_MEMORY_SKILL_DESIGN.md` - Original design

## 🚦 Status

- ✅ Skill structure created
- ✅ Configuration file created
- ✅ Documentation complete
- ⏳ Core scripts (memory_executor.py)
- ⏳ Entity extraction (entity_extractor.py)
- ⏳ Stop hook integration
- ⏳ Obsidian export
- ⏳ Unified search

## 🤝 Contributing

This skill is part of the consulting-co internal toolkit. To extend:

1. Add new entity types in `config/memory-config.yaml`
2. Create custom extraction prompts in `scripts/entity_extractor.py`
3. Add new search algorithms in `scripts/unified_search.py`
4. Extend Obsidian templates in `scripts/obsidian_exporter.py`

## 📝 Philosophy

> **Simplicity over complexity.**
> **Files over databases.**
> **Human-readable over optimized.**
> **Context over completeness.**

This skill prioritizes ease of use and maintainability over maximum performance. It's designed for teams who want memory capabilities without running infrastructure.

---

**Last Updated**: 2026-01-11
**Status**: 🚧 In Development
**Maintainer**: GB Automation Consulting
