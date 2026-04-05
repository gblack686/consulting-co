# /search Command (Unified)

Search across both Obsidian vault and Graphiti knowledge graph simultaneously.

## Usage

```bash
/search [query]
```

## Parameters

- `query` (required): Search query - can include keywords, concepts, or topics

## Examples

```bash
# Simple search
/search authentication

# Multi-word search
/search "aws lambda architecture"

# Concept search
/search event-driven patterns

# Technology search
/search react hooks
```

## Behavior

When you run this command, Claude will:

1. **Search Obsidian** (parallel):
   - Full-text search in note content
   - Tag matching
   - Title matching
   - Fuzzy search for typos

2. **Search Graphiti** (parallel):
   - Semantic search (embeddings)
   - Entity name matching
   - Episode content search
   - Relationship traversal

3. **Merge Results**:
   - Rank by relevance (weighted: 60% Obsidian, 40% Graphiti)
   - Remove duplicates
   - Interleave sources
   - Display top 10 results

4. **Display**:
   - Source indicators (📄 Obsidian, 🔗 Graphiti)
   - Relevance scores
   - Context snippets
   - Quick actions

## Output Example

```
Found 8 results for "authentication":

📄 OBSIDIAN (Relevance: 0.95)
  1. ADR-012-Auth0-Integration.md (Nov 10, 2025)
     Tags: #adr #architecture #authentication
     "...decided to use Auth0 for authentication instead of building
     custom solution. Factors: Time to market, security best practices..."

  2. Authentication-Flow-Design.md (Nov 5, 2025)
     Tags: #learning #security
     "...JWT tokens stored in httpOnly cookies for maximum security.
     Refresh token rotation implemented to prevent token theft..."

🔗 GRAPHITI (Relevance: 0.88)
  3. Entity: JWT Authentication (18 connections)
     Type: Technology
     Last Updated: Nov 12, 2025
     Connected to: OAuth2, Refresh Tokens, Security, httpOnly Cookies

  4. Episode: "Implementing JWT refresh tokens" (Nov 8, 2025)
     Source: Claude Session session-abc123
     Tools Used: Edit auth-middleware.ts
     "Implemented automatic token refresh with rotation to prevent
     token theft attacks..."

  5. Relationship: JWT → httpOnly Cookies [SECURITY_PATTERN]
     Strength: High (mentioned in 5 episodes)
     First: Nov 5, 2025
     Last: Nov 12, 2025

📄 OBSIDIAN (Relevance: 0.82)
  6. Daily Note - 2025-11-10.md
     "Troubleshooting: Auth0 integration required adding custom claims
     to JWT tokens for role-based access control..."

🔗 GRAPHITI (Relevance: 0.79)
  7. Entity: Auth0 (12 connections)
     Type: Service
     Related: OAuth2, JWT, RBAC, Identity Provider

  8. Episode: "Auth0 custom claims configuration" (Nov 10, 2025)
     "Added custom claims to JWT token for user roles..."

Actions:
  /load-context 1,2,3      - Load selected results into conversation
  /load-context 1-4        - Load range into conversation
  /graph-map authentication - Visualize knowledge graph
  /note-create from-search - Create new note from search insights
```

## Search Filters

### By Source
```bash
/search authentication --obsidian-only
/search authentication --graphiti-only
```

### By Date
```bash
/search authentication --after 2025-11-01
/search authentication --before 2025-11-13
/search authentication --last-7-days
```

### By Type
```bash
/search authentication --type adr
/search authentication --type learning
/search authentication --entities-only
```

### Combined Filters
```bash
/search authentication --type adr --after 2025-11-01 --obsidian-only
```

## Advanced Features

### Context Loading
After search, quickly load results:
```bash
/load-context 1,3,5        # Load specific items
/load-context 1-4          # Load range
/load-context all-obsidian # Load all Obsidian results
```

### Related Searches
System suggests related searches based on graph connections:
```
Related searches:
  - oauth2 implementation
  - jwt token security
  - refresh token rotation
```

### Search History
View recent searches:
```bash
/search --history
```

Repeat previous search:
```bash
/search --repeat 2
```

## Performance

**Expected Latency:**
- Small vault + light graph: 1-2 seconds
- Medium vault + active graph: 2-3 seconds
- Large vault + heavy graph: 3-5 seconds

**Optimization:**
- Results cached for 1 hour
- Parallel search execution
- Indexed Obsidian vault
- Optimized Neo4j queries

## Configuration

Search behavior configured in:
`.claude/skills/knowledge-sync/config/sync-settings.json`

```json
{
  "search": {
    "weighObsidian": 0.6,
    "weighGraphiti": 0.4,
    "maxResults": 10,
    "enableSemanticSearch": true
  }
}
```

## Comparison: /search vs /note-search

| Feature | /search (Unified) | /note-search (Obsidian) |
|---------|------------------|------------------------|
| Sources | Obsidian + Graphiti | Obsidian only |
| Search Type | Semantic + Full-text + Graph | Full-text + Fuzzy |
| Relationships | Yes (from graph) | No |
| Entities | Yes (from graph) | No |
| Speed | 2-3s | < 1s |
| Best For | Comprehensive research | Quick note lookup |

## Related Commands

- `/note-search` - Obsidian-only search (faster)
- `/graph-insights` - Generate insights from graph patterns
- `/knowledge-map` - Visualize knowledge connections
- `/context-load` - Load search results into context

## Troubleshooting

### No results from Graphiti
**Check:**
1. Neo4j running: `neo4j status`
2. Graphiti MCP server running
3. Episodes exist: Check Neo4j browser

### Slow search
**Optimize:**
1. Reduce `maxResults` in config
2. Use filters to narrow search
3. Clear cache: `/search --clear-cache`

### Irrelevant results
**Tune:**
1. Adjust weights in `sync-settings.json`
2. Use more specific queries
3. Add filters (`--type`, `--after`)

## Tips

**Best Practices:**
- Use specific terms over general ones
- Combine keywords for precision
- Use filters to narrow results
- Load context before asking followup questions

**Examples of Good Queries:**
- `aws lambda cold start optimization`
- `react hooks useState performance`
- `authentication jwt refresh token rotation`

**Examples of Poor Queries:**
- `help` (too vague)
- `a` (too short)
- `the thing I did yesterday` (use dates instead)
