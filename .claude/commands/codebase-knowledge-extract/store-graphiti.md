# Store in Graphiti

Store extracted knowledge graph in Neo4j via Graphiti for semantic search and temporal queries.

## What This Does

Ingests all extracted TAC data into Graphiti/Neo4j:
- **Prompts** → Episode-based storage with structure and relationships
- **Code entities** → Functions, classes, imports with metadata
- **Concepts** → Learning concepts with definitions
- **Semantic matches** → Code-to-concept links

Enables natural language queries like:
- "What is the Core Four?"
- "Show me prompts that handle file uploads"
- "Which functions demonstrate the SDLC?"

## Prerequisites

### 1. Neo4j Running

**Docker (Recommended):**
```bash
docker run \
    --name neo4j-tac \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

**Or:** Neo4j Desktop / Aura Cloud

### 2. Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional (defaults shown)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

### 3. Extracted Data

Must have run these first:
- `/extract-all` OR
- `/parse-prompts` + `/parse-code` + `/match-semantics`

## Run

```bash
cd tac-learning-system
python storage/graphiti_storage.py
```

## Output

```
============================================================
GRAPHITI INGESTION PIPELINE
============================================================
Connecting to Neo4j at bolt://localhost:7687...
✅ Connected to Graphiti/Neo4j

📄 Ingesting 5 prompts...
  ✅ Ingested prompt: Prime
  ✅ Ingested prompt: Install
  ✅ Ingested prompt: List Built-in Tools
  ✅ Ingested prompt: Natural Language SQL Interface
  ✅ Ingested prompt: Delete Table

🐍 Ingesting 12 modules...
  ✅ Ingested module: server
  ✅ Ingested module: data_models
  ... (10 more)

💡 Ingesting 5 concepts...
  ✅ Ingested concept: Core Four
  ✅ Ingested concept: Software Development Lifecycle
  ✅ Ingested concept: Agentic Coding
  ✅ Ingested concept: Leverage Points
  ✅ Ingested concept: Agent Perspective

🔗 Ingesting 2 semantic matches...
  ✅ Ingested match: List Built-in Tools → Core Four
  ✅ Ingested match: Natural Language SQL Interface → Core Four

✅ Graphiti ingestion complete!
```

## What Gets Stored

### Episodes (4 types)

1. **tac2_prompts** - Prompt entities
   - Structure, delegations, tool mentions
   - Example: "Prime command: Run git ls-files, Read README.md"

2. **tac2_code** - Code entities
   - Functions, classes, imports, complexity
   - Example: "upload_file accepts UploadFile, returns FileUploadResponse"

3. **lesson2_concepts** - Learning concepts
   - Definitions, categories, keywords
   - Example: "Core Four: Context, Model, Prompt, Tools"

4. **tac2_semantic_links** - Semantic matches
   - Code-to-concept relationships
   - Example: "List Built-in Tools demonstrates Core Four (0.319 similarity)"

### Graphiti Processing

Automatically:
- Extracts entities from episode text
- Generates OpenAI embeddings
- Creates relationships
- Enables semantic search

## Example Queries

### Python API

```python
from storage.graphiti_storage import GraphitiStorage
import asyncio

async def search():
    storage = GraphitiStorage()

    # Find prompts
    results = await storage.search("list all TAC prompts")

    # Find code implementing concepts
    results = await storage.search("which functions use the Core Four?")

    # Find relationships
    results = await storage.search("what prompts delegate to prime?")

    await storage.close()

asyncio.run(search())
```

### Neo4j Browser

Open http://localhost:7474 and run Cypher:

```cypher
// Show all entities
MATCH (n) RETURN n LIMIT 25

// Find episodes
MATCH (n:Episode)
WHERE n.name = 'tac2_prompts'
RETURN n

// Find relationships
MATCH (a)-[r]->(b)
RETURN a, r, b LIMIT 50
```

## Performance

### Ingestion Time (tac-2)
- Prompts: ~5s (5 entities)
- Code: ~15s (12 modules)
- Concepts: ~5s (5 concepts)
- Semantic: ~2s (2 matches)
- **Total: ~30 seconds**

*First run may take longer to download OpenAI model*

### Storage
- Neo4j database: ~50-100 MB
- Embeddings: ~5-10 MB
- Relationships: ~1-5 MB

## Verification

### Check Neo4j Browser

1. Open http://localhost:7474
2. Login: neo4j / password
3. Run: `MATCH (n) RETURN count(n)`
4. Should see 20+ nodes

### Test Search

```python
results = await storage.search("Core Four")
# Should return concept definition
```

### View Episodes

```cypher
MATCH (e:Episode)
RETURN e.name, e.created_at
ORDER BY e.created_at DESC
```

## Integration with TAC Learning System

After Graphiti storage:

```
Extracted Data (JSON)
  ↓
Graphiti/Neo4j
  ↓
Semantic Search
  ↓
TAC-Teacher MCP Server (future)
  ↓
Interactive Learning Tools
```

## Configuration

### Custom Neo4j Server

Edit `graphiti_storage.py`:

```python
storage = GraphitiStorage(
    neo4j_uri="bolt://your-server:7687",
    neo4j_user="custom_user",
    neo4j_password="secure_password"
)
```

### Environment Variables

Set in shell or `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...

# Neo4j (optional, these are defaults)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Troubleshooting

### Connection Failed

```
❌ Failed to connect to Neo4j: ...
```

**Solutions:**
1. Start Neo4j: `docker start neo4j-tac`
2. Check port: `docker ps | grep 7687`
3. Verify credentials

### OPENAI_API_KEY Not Set

```
❌ Error: OPENAI_API_KEY environment variable required
```

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-key"
```

### Empty Search Results

**Causes:**
1. Data not ingested - run ingestion script
2. Query too specific - try broader terms
3. Embeddings not generated - check logs

### Slow Ingestion

**Normal:**
- OpenAI API has rate limits
- Embedding generation takes time
- First run downloads models

**Speed up:**
- Use batch processing
- Cache embeddings
- Add delays between calls

## Advanced Usage

### Re-ingest Data

Safe to run multiple times - Graphiti handles duplicates:

```bash
python storage/graphiti_storage.py
```

### Query by Episode

```cypher
// Find all prompt episodes
MATCH (e:Episode)
WHERE e.name STARTS WITH 'tac2_prompts'
RETURN e
```

### Temporal Queries

```cypher
// Find recent episodes
MATCH (e:Episode)
WHERE e.created_at > datetime() - duration('P7D')
RETURN e.name, e.created_at
```

### Custom Episodes

Add your own:

```python
await client.add_episode(
    name="custom_analysis",
    episode_body="My custom facts about the codebase",
    source=EpisodeType.text,
    reference_time=datetime.now()
)
```

## Next Steps

1. **Query the graph**: Use semantic search
2. **Visualize**: Explore in Neo4j Browser
3. **Build MCP tools**: Create TAC-Teacher server
4. **Temporal analysis**: Track changes over time

## Documentation

- Setup Guide: `storage/GRAPHITI_SETUP.md`
- Graphiti Docs: https://help.getzep.com/graphiti
- Neo4j Browser: http://localhost:7474

## Example Searches (After Ingestion)

```python
# What is the Core Four?
→ Returns concept definition + related prompts

# Show me file upload functions
→ Returns upload_file, convert_csv_to_sqlite

# Which prompts delegate to prime?
→ Returns /install (delegates to /prime)

# What are complex functions?
→ Returns functions with complexity > 10
```
