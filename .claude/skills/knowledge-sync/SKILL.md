# Knowledge Sync Skill

> Unified knowledge management across Obsidian and Graphiti

## Purpose

This skill provides bidirectional synchronization between:
- **Obsidian Vault** (file-based markdown notes)
- **Graphiti Knowledge Graph** (Neo4j temporal graph)

Creating a dual-layer knowledge system that combines human-curated documentation with automatically extracted relationships and patterns.

## When to Use This Skill

Activate when:
- Syncing important notes to the knowledge graph
- Searching across both file and graph layers
- Generating insights from graph patterns
- Loading historical context spanning both systems

## Capabilities

### Bidirectional Sync
- **Obsidian → Graphiti**: Sync tagged notes as episodes with entity extraction
- **Graphiti → Obsidian**: Generate insight notes from graph patterns
- **Conflict Resolution**: Timestamp-based with user prompts
- **Selective Sync**: Only sync notes with specific tags

### Unified Search
- **Multi-source**: Search both Obsidian (full-text) and Graphiti (semantic + graph)
- **Merged Results**: Intelligent ranking and deduplication
- **Context Loading**: Load results from either source into conversation
- **Relationship Discovery**: Find connections across both systems

### Knowledge Insights
- **Pattern Detection**: Identify frequently connected concepts
- **Temporal Analysis**: Track how knowledge evolves over time
- **Gap Identification**: Find missing connections or documentation
- **Auto-generation**: Create summary notes from graph insights

## Configuration

**Location:** `.claude/skills/knowledge-sync/config/sync-settings.json`

### Required Environment Variables

```bash
# Neo4j Configuration (for Graphiti)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"

# OpenAI (for Graphiti entity extraction)
export OPENAI_API_KEY="sk-..."

# Obsidian Vault Path (in sync-settings.json)
```

### Sync Configuration

```json
{
  "sync": {
    "mode": "selective",
    "triggers": ["note-create", "note-update"],
    "noteTags": ["adr", "decision", "learning"],
    "minWordCount": 50
  }
}
```

## Available Commands

- `/search [query]` - Unified search across both systems
- `/sync-to-graph [note]` - Sync specific note to Graphiti
- `/graph-insights` - Generate Obsidian notes from graph patterns
- `/knowledge-map [topic]` - Visualize knowledge connections

## Integration with Hooks

### SessionStart
- Loads recent Graphiti context (last 7 days)
- Opens Obsidian daily note
- Displays unified knowledge dashboard

### SessionEnd
- Syncs session learnings to both systems
- Updates daily note with summary
- Creates Graphiti episode with extracted entities

## Workflow Example

```
User: /search authentication

System:
  📄 Obsidian (3 results)
    1. ADR-012-Auth0-Integration.md
    2. Authentication-Flow-Design.md

  🔗 Graphiti (5 entities, 8 relationships)
    1. Entity: JWT Authentication (18 connections)
       Related: OAuth2, Security, Tokens
    2. Episode: "Implementing refresh tokens" (Nov 8)

User: /load-context 1,2,3

System: [Loads all sources into conversation context]

User: We should use Auth0

System: [Creates ADR, syncs to both Obsidian and Graphiti]
  ✓ Created: Decisions/ADR-013-Auth0.md
  ✓ Synced to Graphiti: Episode ep-auth0-decision
  ✓ Entities extracted: Auth0, OAuth2, JWT
```

## Dependencies

```bash
cd .claude/skills/knowledge-sync
pip install -r requirements.txt
```

**Python Requirements:**
- graphiti-core
- neo4j
- python-dotenv
- openai
- asyncio

**Uses existing skills:**
- obsidian-vault (file operations)
- Graphiti integration from other projects

## Model Recommendation

**Default:** Sonnet
- Balanced for search and extraction
- Good at entity recognition

**For extraction:** Haiku
- Cost-effective for entity extraction
- Sufficient for most sync operations

## Security

- Neo4j credentials via environment variables
- OpenAI key never logged
- Obsidian vault respects `.claudeignore`
- Selective folder permissions
- All sync operations audited

## Performance

**Unified Search:** ~2-3 seconds
**Sync Operation:** ~3-5 seconds per note
**Graph Insights:** ~10-15 seconds (weekly generation)

**Optimization:**
- Parallel search execution
- Cached entity embeddings
- Batch sync operations
- Lazy relationship loading

## Troubleshooting

### "Cannot connect to Neo4j"
Check:
1. Neo4j is running: `neo4j status`
2. Credentials in `.env` correct
3. Port 7687 accessible

### "OpenAI API error"
Check:
1. API key in environment: `echo $OPENAI_API_KEY`
2. API quota not exceeded
3. Model availability

### "Sync conflicts"
- System will prompt for resolution
- Default: Keep most recent version
- Manual override with `--force-obsidian` or `--force-graphiti`

## Version

**Version:** 1.0
**Requires:**
- Neo4j 5.x+
- Graphiti MCP server
- Obsidian vault skill
- OpenAI API access
