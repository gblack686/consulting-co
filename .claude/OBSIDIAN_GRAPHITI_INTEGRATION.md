# Obsidian + Graphiti Integration Plan

**Date:** November 13, 2025
**Integration Type:** Dual-Layer Knowledge System
**Components:** Obsidian Vault + Graphiti Knowledge Graph + Neo4j

---

## Executive Summary

This integration creates a **dual-layer knowledge system** that combines the best of both worlds:

**Obsidian Layer** (File-Based):
- Human-readable markdown notes
- Manual curation and organization
- Rich formatting and templates
- Excellent for deliberate documentation

**Graphiti Layer** (Graph-Based):
- Automatic entity and relationship extraction
- Temporal knowledge graph
- Semantic search and traversal
- Excellent for emergent patterns and connections

**Key Innovation:** Bidirectional sync keeps both systems synchronized, allowing you to work in either layer while maintaining consistency.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Session                      │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
    ┌───────────────────────┐    ┌───────────────────────┐
    │   Obsidian Vault      │◄──►│  Graphiti (Neo4j)     │
    │   (Markdown Files)    │    │  (Knowledge Graph)    │
    └───────────────────────┘    └───────────────────────┘
                │                             │
                │                             │
                ▼                             ▼
    ┌───────────────────────┐    ┌───────────────────────┐
    │   File Operations     │    │   Graph Operations    │
    │   - Daily notes       │    │   - Episodes          │
    │   - ADRs              │    │   - Entities          │
    │   - Learnings         │    │   - Relationships     │
    │   - Search            │    │   - Temporal queries  │
    └───────────────────────┘    └───────────────────────┘
```

### Data Flow

**1. Session Start:**
```
Claude Start → Load Obsidian daily note → Load Graphiti context (last 7 days)
```

**2. During Session:**
```
User asks question → Search Obsidian + Graphiti → Merge results → Answer
```

**3. Session End:**
```
Extract learnings → Save to Obsidian note → Sync to Graphiti episode
```

---

## Integration Patterns

### Pattern 1: Obsidian → Graphiti (Note to Episode)

**When:** User creates/updates important notes (ADRs, decisions, learnings)

**How:**
1. Note is created in Obsidian with frontmatter
2. Hook detects note creation
3. Note content + metadata → Graphiti episode
4. Entities and relationships auto-extracted
5. Graph updated with new knowledge

**Example:**
```markdown
---
date: 2025-11-13
tags: [adr, architecture, decision]
status: accepted
---

# ADR-007: Use Lambda for API Endpoints

## Context
We need cost-effective serverless compute...

## Decision
Use AWS Lambda instead of ECS Fargate...
```

↓ Syncs to Graphiti as:

```python
Episode(
  name="ADR-007-Lambda-API",
  body="Architectural decision to use AWS Lambda...",
  entities=[
    Entity(type="Technology", name="AWS Lambda"),
    Entity(type="Technology", name="ECS Fargate"),
    Entity(type="Decision", name="Serverless Architecture")
  ],
  relationships=[
    Relation(from="ADR-007", to="AWS Lambda", type="IMPLEMENTS"),
    Relation(from="Lambda", to="Cost Optimization", type="ENABLES")
  ]
)
```

### Pattern 2: Graphiti → Obsidian (Episode to Note)

**When:** Graphiti discovers important patterns or entities

**How:**
1. Periodic Graphiti analysis (daily/weekly)
2. Query for frequently connected entities
3. Generate summary note in Obsidian
4. Link to related notes

**Example Queries:**
```cypher
// Find most connected concepts
MATCH (n:Entity)-[r]->()
RETURN n.name, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

↓ Generates Obsidian note:

```markdown
# Knowledge Graph Insights - 2025-11-13

## Most Connected Concepts

1. **AWS Lambda** (45 connections)
   - Used in 12 decisions
   - Related to: API Gateway, Cost Optimization, Serverless
   - [[ADR-007-Lambda-API]]

2. **Authentication** (32 connections)
   - Related to: Security, OAuth, JWT
   - [[ADR-012-Auth0-Integration]]
```

### Pattern 3: Unified Search

**When:** User searches for knowledge

**How:**
1. Query both Obsidian (full-text) and Graphiti (semantic + graph)
2. Merge and rank results
3. Display unified results with source indicators

**Example:**
```
User: /search authentication

Results (Unified):

📄 Obsidian (3 results)
  1. ADR-012-Auth0-Integration.md
  2. Authentication-Flow-Design.md
  3. Daily-Note-2025-11-10.md

🔗 Graphiti (5 entities, 12 relationships)
  1. Entity: Authentication (32 connections)
     - Related to: OAuth, JWT, Security
     - Last updated: 2025-11-12
  2. Episode: "Implementing JWT refresh tokens"
     - Date: 2025-11-05
     - Files: auth-service.ts

Combined Context:
- Recent discussion about OAuth2 flows
- Decision to use Auth0 (ADR-012)
- Implementation in auth-service.ts
```

---

## Implementation Architecture

### Directory Structure

```
.claude/
├── OBSIDIAN_GRAPHITI_INTEGRATION.md       # This file
├── skills/
│   ├── obsidian-vault/                    # Existing Obsidian skill
│   │   └── ...
│   └── knowledge-sync/                    # NEW: Unified knowledge skill
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── obsidian-to-graphiti.py    # Sync notes → episodes
│       │   ├── graphiti-to-obsidian.py    # Sync episodes → notes
│       │   ├── unified-search.py          # Search both systems
│       │   └── knowledge-curator.py       # Intelligent sync manager
│       └── config/
│           └── sync-settings.json         # Sync configuration
├── hooks/
│   ├── session-start/
│   │   ├── load-obsidian-context.sh       # Load daily note
│   │   └── load-graphiti-context.sh       # Load recent graph context
│   ├── stop/
│   │   ├── log-to-obsidian.sh             # Session → daily note
│   │   └── log-to-graphiti.py             # Session → episode (existing)
│   └── session-end/
│       └── sync-knowledge.py              # Bidirectional sync
└── commands/
    ├── search-knowledge.md                # /search unified search
    ├── sync-to-graph.md                   # /sync-to-graph
    └── graph-insights.md                  # /graph-insights
```

---

## Configuration

### Sync Settings
**File:** `.claude/skills/knowledge-sync/config/sync-settings.json`

```json
{
  "obsidian": {
    "enabled": true,
    "vaultPath": "/path/to/obsidian/vault",
    "syncFolders": ["Decisions", "Learnings"],
    "excludeFolders": ["Private", "Archive"]
  },
  "graphiti": {
    "enabled": true,
    "neo4jUri": "bolt://localhost:7687",
    "neo4jUser": "neo4j",
    "neo4jPassword": "${NEO4J_PASSWORD}",
    "openaiApiKey": "${OPENAI_API_KEY}"
  },
  "sync": {
    "mode": "bidirectional",
    "autoSync": true,
    "syncOnSessionStart": true,
    "syncOnSessionEnd": true,
    "obsidianToGraphiti": {
      "enabled": true,
      "triggers": ["note-create", "note-update"],
      "noteTags": ["adr", "decision", "learning"],
      "minWordCount": 50
    },
    "graphitiToObsidian": {
      "enabled": true,
      "frequency": "weekly",
      "insightTypes": ["connected-concepts", "emerging-patterns"]
    }
  },
  "search": {
    "unifiedSearch": true,
    "weighObsidian": 0.6,
    "weighGraphiti": 0.4,
    "maxResults": 10,
    "mergeStrategy": "interleaved"
  }
}
```

---

## Sync Strategies

### Strategy 1: Selective Sync (Recommended)

**Obsidian → Graphiti:**
- Only sync notes with specific tags: `#adr`, `#decision`, `#learning`
- Only sync notes > 50 words (avoid noise)
- Auto-sync on note creation

**Graphiti → Obsidian:**
- Weekly insights generation
- Only create notes for highly connected concepts (>10 connections)
- Store in `Learnings/Graph Insights/` folder

**Pros:**
- Low overhead
- High signal-to-noise ratio
- Maintains clean vault

**Cons:**
- Not all knowledge in both systems
- Requires manual tagging discipline

### Strategy 2: Full Sync

**Obsidian → Graphiti:**
- Sync all notes in specific folders
- Continuous monitoring with file watchers
- Real-time graph updates

**Graphiti → Obsidian:**
- Daily snapshots of graph state
- Automatic note generation for all entities

**Pros:**
- Complete knowledge coverage
- No manual intervention

**Cons:**
- Higher storage and compute costs
- Potential vault clutter
- More complex to maintain

### Strategy 3: Manual Sync (Fallback)

**Obsidian → Graphiti:**
- User runs `/sync-to-graph` command
- User selects specific notes to sync
- Batch processing

**Graphiti → Obsidian:**
- User runs `/graph-insights` command
- Generate insights on demand

**Pros:**
- Full user control
- No automatic overhead

**Cons:**
- Requires user discipline
- May miss connections

**Recommendation:** Start with **Strategy 1 (Selective Sync)**, upgrade to Strategy 2 if needed.

---

## Commands

### 1. `/search [query]`
**Description:** Unified search across Obsidian and Graphiti

**Behavior:**
```bash
/search authentication jwt

# Searches:
# - Obsidian: Full-text + tag search
# - Graphiti: Semantic search + entity lookup + relationship traversal

# Returns merged results with source indicators
```

**Output:**
```
Found 8 results for "authentication jwt":

📄 OBSIDIAN
  1. ADR-012-Auth0-Integration.md (Nov 10)
     "...JWT tokens stored in httpOnly cookies..."

  2. Authentication-Flow-Design.md (Nov 5)
     "...Refresh token rotation implemented..."

🔗 GRAPHITI
  3. Entity: JWT Authentication (18 connections)
     Connected to: OAuth2, Refresh Tokens, Security

  4. Episode: "Implementing JWT middleware" (Nov 8)
     Tools used: Edit auth-middleware.ts

  5. Relationship: JWT → httpOnly Cookies [SECURITY_PATTERN]

Load context: /load-context [number]
```

### 2. `/sync-to-graph [note-name?]`
**Description:** Sync Obsidian note(s) to Graphiti

**Behavior:**
```bash
# Sync specific note
/sync-to-graph "ADR-007-Lambda-API"

# Sync all notes with tag
/sync-to-graph --tag adr

# Sync all in folder
/sync-to-graph --folder Decisions
```

### 3. `/graph-insights`
**Description:** Generate Obsidian notes from Graphiti patterns

**Behavior:**
```bash
/graph-insights

# Queries Graphiti for:
# - Most connected entities
# - Emerging relationship patterns
# - Temporal trends
# - Orphaned concepts

# Generates insight notes in Obsidian
```

### 4. `/knowledge-map`
**Description:** Visualize knowledge graph as text diagram

**Behavior:**
```bash
/knowledge-map authentication

# Generates ASCII graph visualization
# Shows entities, relationships, temporal flow
```

---

## Hook Scripts

### SessionStart Hook: Load Unified Context

**File:** `.claude/hooks/session-start/load-unified-context.py`

```python
#!/usr/bin/env python3
"""
Load context from both Obsidian and Graphiti on session start.
"""

import asyncio
from obsidian_vault import ObsidianVault
from graphiti_core import Graphiti

async def main():
    # 1. Load Obsidian daily note
    vault = ObsidianVault("/path/to/vault")
    daily_note = vault.get_or_create_daily_note()
    print(f"📄 Loaded daily note: {daily_note.path}")

    # 2. Load recent Graphiti context (last 7 days)
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )

    recent_episodes = await graphiti.search_episodes(
        days_back=7,
        limit=5
    )

    print(f"🔗 Loaded {len(recent_episodes)} recent episodes from Graphiti")

    # 3. Display unified context
    print("\n" + "="*60)
    print("📚 Knowledge Context Loaded")
    print("="*60)
    print(f"Daily Note: {daily_note.title}")
    print(f"Pending Tasks: {len(daily_note.tasks)}")
    print(f"Recent Graph Activity: {len(recent_episodes)} episodes")
    print("="*60 + "\n")

    await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### SessionEnd Hook: Bidirectional Sync

**File:** `.claude/hooks/session-end/sync-knowledge.py`

```python
#!/usr/bin/env python3
"""
Bidirectional sync between Obsidian and Graphiti on session end.
"""

import asyncio
import json
import sys
from pathlib import Path

async def main():
    hook_data = json.load(sys.stdin)
    transcript_path = hook_data.get("transcript_path")

    # 1. Extract learnings from session (existing Graphiti logic)
    from service.extractors import HaikuExtractor
    extractor = HaikuExtractor()
    extraction = await extractor.extract_from_transcript(transcript_path)

    # 2. Sync to Graphiti (existing)
    from graphiti_core import Graphiti
    graphiti = Graphiti(...)
    await graphiti.add_episode(
        name=f"session-{hook_data['session_id']}",
        episode_body=format_episode(extraction),
        reference_time=datetime.now()
    )

    # 3. Sync to Obsidian (NEW)
    from obsidian_vault import ObsidianVault
    vault = ObsidianVault("/path/to/vault")

    # Create learning notes for significant concepts
    if extraction.related_concepts:
        for concept in extraction.related_concepts[:3]:
            vault.create_or_update_note(
                title=f"Learning: {concept}",
                category="learning",
                content=extraction.solution.approach,
                tags=["auto-generated", "graphiti-sync"]
            )

    # Update daily note with session summary
    daily_note = vault.get_daily_note()
    vault.append_to_note(
        daily_note,
        f"\n## Session Summary\n"
        f"- Intent: {extraction.intent}\n"
        f"- Complexity: {extraction.complexity}\n"
        f"- Concepts: {', '.join(extraction.related_concepts)}\n"
    )

    print("✓ Synced to both Obsidian and Graphiti")
    await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Unified Search Implementation

### Search Flow

```python
#!/usr/bin/env python3
"""
Unified search across Obsidian and Graphiti.
"""

import asyncio
from typing import List, Dict

class UnifiedSearch:
    def __init__(self, vault: ObsidianVault, graphiti: Graphiti):
        self.vault = vault
        self.graphiti = graphiti

    async def search(self, query: str, max_results: int = 10) -> List[Dict]:
        # Search both systems in parallel
        obsidian_results, graphiti_results = await asyncio.gather(
            self.search_obsidian(query),
            self.search_graphiti(query)
        )

        # Merge and rank results
        merged = self.merge_results(
            obsidian_results,
            graphiti_results,
            query
        )

        return merged[:max_results]

    async def search_obsidian(self, query: str) -> List[Dict]:
        """Search Obsidian with fuzzy matching."""
        results = self.vault.search_notes(query)
        return [
            {
                "source": "obsidian",
                "type": "note",
                "title": r.title,
                "snippet": r.snippet,
                "score": r.score,
                "path": r.path,
                "tags": r.tags
            }
            for r in results
        ]

    async def search_graphiti(self, query: str) -> List[Dict]:
        """Search Graphiti with semantic + graph search."""
        # Entity search
        entities = await self.graphiti.search_nodes(
            query=query,
            limit=5
        )

        # Episode search
        episodes = await self.graphiti.search_episodes(
            query=query,
            limit=5
        )

        # Relationship search
        facts = await self.graphiti.search_facts(
            query=query,
            limit=5
        )

        results = []

        # Convert to unified format
        for entity in entities:
            results.append({
                "source": "graphiti",
                "type": "entity",
                "title": entity.name,
                "entity_type": entity.type,
                "connections": entity.degree,
                "score": entity.similarity_score
            })

        for episode in episodes:
            results.append({
                "source": "graphiti",
                "type": "episode",
                "title": episode.name,
                "snippet": episode.body[:200],
                "date": episode.created_at,
                "score": episode.similarity_score
            })

        return results

    def merge_results(
        self,
        obsidian: List[Dict],
        graphiti: List[Dict],
        query: str
    ) -> List[Dict]:
        """Merge and rank results from both sources."""
        # Weight configuration
        OBSIDIAN_WEIGHT = 0.6
        GRAPHITI_WEIGHT = 0.4

        # Apply weights
        for r in obsidian:
            r["final_score"] = r["score"] * OBSIDIAN_WEIGHT

        for r in graphiti:
            r["final_score"] = r["score"] * GRAPHITI_WEIGHT

        # Merge and sort
        all_results = obsidian + graphiti
        all_results.sort(key=lambda x: x["final_score"], reverse=True)

        return all_results
```

---

## Use Cases

### Use Case 1: Architectural Decision Making

**Scenario:** You need to decide between two architectural approaches.

**Workflow:**
```bash
1. /search "microservices vs monolith"
   → Returns past ADRs + graph patterns

2. Claude analyzes both Obsidian notes and Graphiti relationships

3. /decision-log "Modular Monolith with Domain Boundaries"
   → Creates ADR in Obsidian
   → Syncs to Graphiti as episode
   → Entities extracted: "Modular Monolith", "Domain Boundaries"

4. Future searches automatically link to this decision
```

### Use Case 2: Learning Synthesis

**Scenario:** Weekly knowledge review and synthesis.

**Workflow:**
```bash
1. /graph-insights
   → Queries Graphiti for week's most connected concepts

2. Generates Obsidian note:
   "Weekly Synthesis - 2025-W46.md"
   - Top 5 concepts
   - Emerging patterns
   - Links to related notes and episodes

3. User reviews, edits, and expands

4. Updated note syncs back to Graphiti with richer context
```

### Use Case 3: Context Recovery

**Scenario:** You worked on a feature 3 months ago and need to remember the approach.

**Workflow:**
```bash
1. /search "user authentication implementation"

2. Results from both systems:
   📄 Obsidian: ADR-012, auth-flow-design.md
   🔗 Graphiti: 5 episodes, 12 entities, 8 relationships

3. /load-context 1,2,3
   → Loads Obsidian notes + Graphiti episodes into conversation

4. Claude has full historical context to answer questions
```

---

## Data Schema Mapping

### Obsidian Note → Graphiti Episode

```yaml
Obsidian Note:
  title: "ADR-007-Lambda-API"
  frontmatter:
    date: "2025-11-13"
    tags: ["adr", "architecture"]
    status: "accepted"
  content: "Markdown content..."

↓ Maps to ↓

Graphiti Episode:
  name: "ADR-007-Lambda-API"
  episode_body: "Full markdown content"
  reference_time: 2025-11-13
  source_description: "Obsidian ADR"
  metadata:
    obsidian_path: "Decisions/ADR-007.md"
    tags: ["adr", "architecture"]
    status: "accepted"

Extracted Entities:
  - Entity(type="Technology", name="AWS Lambda")
  - Entity(type="Decision", name="Serverless Architecture")

Extracted Relationships:
  - Relation(from="ADR-007", to="AWS Lambda", type="IMPLEMENTS")
```

### Graphiti Entity → Obsidian Note

```yaml
Graphiti Entity:
  type: "Concept"
  name: "Event-Driven Architecture"
  connections: 25
  last_updated: "2025-11-13"
  related_episodes: [...]

↓ Generates ↓

Obsidian Note:
  path: "Learnings/Graph Insights/Event-Driven-Architecture.md"
  frontmatter:
    generated: true
    source: "graphiti"
    connections: 25
    last_synced: "2025-11-13"
  content:
    # Event-Driven Architecture

    **Graph Connections:** 25
    **Last Updated:** Nov 13, 2025

    ## Related Concepts
    - [[Message Queues]]
    - [[Asynchronous Processing]]
    - [[Event Sourcing]]

    ## Episodes Mentioning This
    - [[Session-2025-11-10]] - Implementing event bus
    - [[ADR-015-Event-Bus]] - Decision to use EventBridge

    ## Relationships
    - ENABLES → [[Scalability]]
    - REQUIRES → [[Message Queues]]
    - ALTERNATIVE_TO → [[Request-Response Pattern]]
```

---

## Performance Considerations

### Latency

**Obsidian Search:**
- Small vault (< 1000 notes): ~50-100ms
- Medium vault (1000-5000): ~200-500ms
- Large vault (> 5000): ~1-2s

**Graphiti Search:**
- Semantic search: ~500ms-1s (depends on OpenAI)
- Graph traversal: ~100-300ms (Neo4j query)
- Combined: ~1-2s

**Unified Search Total:** ~2-3s (acceptable for interactive use)

### Optimization Strategies

1. **Caching:**
   - Cache frequent searches (Redis/in-memory)
   - Cache entity embeddings
   - Cache Obsidian index

2. **Parallel Execution:**
   - Search both systems concurrently
   - Async I/O for all operations

3. **Selective Sync:**
   - Only sync tagged notes
   - Rate limit Graphiti API calls
   - Batch updates

4. **Lazy Loading:**
   - Load relationships on demand
   - Stream search results
   - Paginate graph queries

---

## Security & Privacy

### Data Isolation

- Obsidian vault can exclude private folders (`.claudeignore`)
- Graphiti can use separate Neo4j databases per project
- Environment variables for all credentials

### Access Control

```json
{
  "obsidian": {
    "allowedFolders": ["Decisions", "Learnings"],
    "deniedFolders": ["Private", "Archive"]
  },
  "graphiti": {
    "databases": ["claude-code-project-1"],
    "excludeDatabases": ["personal-vault"]
  }
}
```

### Audit Logging

All sync operations logged:
```
2025-11-13 10:30:15 | SYNC | Obsidian → Graphiti | ADR-007.md → Episode
2025-11-13 10:30:16 | EXTRACT | Entities: 3, Relations: 5
2025-11-13 10:30:17 | SUCCESS | Episode ID: ep-123abc
```

---

## Migration Path

### Phase 1: Setup (Week 1)
- [ ] Install Neo4j locally
- [ ] Configure Graphiti MCP server
- [ ] Test Graphiti with sample episodes
- [ ] Verify existing Obsidian integration

### Phase 2: Unidirectional Sync (Week 2)
- [ ] Implement Obsidian → Graphiti sync
- [ ] Create sync hook scripts
- [ ] Test with selective folders
- [ ] Validate entity extraction

### Phase 3: Bidirectional Sync (Week 3)
- [ ] Implement Graphiti → Obsidian insights
- [ ] Create weekly insight generation
- [ ] Test round-trip sync
- [ ] Resolve conflicts

### Phase 4: Unified Search (Week 4)
- [ ] Implement unified search command
- [ ] Merge and rank results
- [ ] Optimize performance
- [ ] User testing

### Phase 5: Production (Week 5+)
- [ ] Monitor sync performance
- [ ] Optimize queries
- [ ] Add advanced features
- [ ] Documentation

---

## Cost Estimate

### Infrastructure Costs

**Neo4j:**
- Local: Free
- Neo4j Aura (cloud): ~$50-150/month

**OpenAI API (for Graphiti extraction):**
- Light usage (~100 episodes/week): ~$10-20/month
- Medium usage (~500 episodes/week): ~$50-100/month
- Heavy usage (1000+ episodes/week): ~$150-300/month

**Total Monthly:** $60-400 depending on usage

### Development Costs

**Phase 1-2 (Unidirectional):** 20-30 hours
**Phase 3-4 (Bidirectional + Search):** 30-40 hours
**Phase 5 (Production Polish):** 10-15 hours

**Total Implementation:** 60-85 hours

---

## Success Metrics

### Adoption
- [ ] 90%+ of ADRs synced to Graphiti
- [ ] Weekly insights generated and reviewed
- [ ] Unified search used 10+ times/week

### Quality
- [ ] Entity extraction accuracy > 85%
- [ ] Relationship detection accuracy > 80%
- [ ] Search relevance score > 4/5

### Performance
- [ ] Unified search < 3 seconds
- [ ] Sync latency < 5 seconds
- [ ] No data loss in bidirectional sync

### Value
- [ ] 50% reduction in "how did we solve X?" time
- [ ] 30% increase in cross-project pattern recognition
- [ ] Emerging patterns identified proactively

---

## Future Enhancements

### Advanced Graph Queries
- Temporal pattern detection
- Causal chain analysis
- Concept drift tracking
- Anomaly detection

### AI-Powered Insights
- Automatic ADR generation from patterns
- Predictive decision support
- Knowledge gap identification
- Trend forecasting

### Multi-Vault Support
- Cross-project knowledge graph
- Team knowledge sharing
- Privacy-preserving sync
- Federated search

### Visualization
- Interactive graph UI
- Temporal flow diagrams
- Concept maps
- Relationship explorer

---

## Troubleshooting

### Issue: Sync conflicts
**Solution:** Implement conflict resolution with timestamps + user prompts

### Issue: High OpenAI costs
**Solution:** Use cheaper models for extraction (GPT-4o-mini), batch requests

### Issue: Neo4j performance degradation
**Solution:** Implement graph pruning, archive old episodes, optimize indices

### Issue: Duplicate entities
**Solution:** Improve entity resolution, fuzzy matching, canonical names

---

## Next Steps

### Decision Points

1. **Sync Strategy:** Selective (recommended) vs. Full vs. Manual?
2. **Frequency:** Real-time vs. Batch (hourly/daily)?
3. **Direction:** Unidirectional (Obs→Graphiti) vs. Bidirectional?
4. **Insights:** Weekly auto-generation vs. On-demand?

### Implementation Order

1. Set up Neo4j and Graphiti MCP server
2. Test existing Graphiti hook with Obsidian
3. Implement selective Obsidian → Graphiti sync
4. Build unified search
5. Add Graphiti → Obsidian insights
6. Optimize and productionize

---

**Ready to implement? Start with Phase 1 setup!**

**Version:** 1.0
**Author:** Claude Code Integration Team
**Last Updated:** November 13, 2025
