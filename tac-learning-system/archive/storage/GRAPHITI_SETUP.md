# Graphiti Storage Setup Guide

> Store TAC knowledge graph in Neo4j for semantic search and temporal queries

## Prerequisites

### 1. Neo4j Database

**Option A: Docker (Recommended)**
```bash
# Pull Neo4j image
docker pull neo4j:latest

# Run Neo4j container
docker run \
    --name neo4j-tac \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:latest

# Access Neo4j Browser: http://localhost:7474
# Username: neo4j
# Password: password
```

**Option B: Neo4j Desktop**
1. Download from https://neo4j.com/download/
2. Install and create new database
3. Set password: `password` (or customize)
4. Start database

**Option C: Neo4j Aura (Cloud)**
1. Sign up at https://neo4j.com/cloud/aura/
2. Create free tier database
3. Note connection URI and credentials

### 2. Environment Variables

Set required environment variables:

```bash
# Required: OpenAI API key (Graphiti uses OpenAI for embeddings)
export OPENAI_API_KEY="sk-..."

# Optional: Neo4j connection (defaults shown)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="password"
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-...
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=password
```

### 3. Python Dependencies

Graphiti should already be installed. Verify:

```bash
pip show graphiti-core
```

If not installed:
```bash
pip install graphiti-core
```

## Quick Start

### 1. Start Neo4j

```bash
# If using Docker
docker start neo4j-tac

# Verify it's running
docker ps | grep neo4j
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-key"
export NEO4J_PASSWORD="your-neo4j-password"
```

### 3. Run Ingestion

```bash
cd tac-learning-system
python storage/graphiti_storage.py
```

**Expected output:**
```
============================================================
GRAPHITI INGESTION PIPELINE
============================================================
Connecting to Neo4j at bolt://localhost:7687...
✅ Connected to Graphiti/Neo4j

📄 Ingesting 5 prompts...
  ✅ Ingested prompt: Prime
  ✅ Ingested prompt: Install
  ...

🐍 Ingesting 12 modules...
  ✅ Ingested module: server
  ✅ Ingested module: data_models
  ...

💡 Ingesting 5 concepts...
  ✅ Ingested concept: Core Four
  ✅ Ingested concept: SDLC
  ...

🔗 Ingesting 2 semantic matches...
  ✅ Ingested match: List Built-in Tools → Core Four
  ...

✅ Graphiti ingestion complete!

============================================================
EXAMPLE SEARCHES
============================================================

🔍 Searching: 'What is the Core Four?'
✅ Found 3 results
Query: What is the Core Four?
Results: 3
  1. Core Four
  2. List Built-in Tools
  3. Context
```

## What Gets Stored

### Episodes Created

Graphiti organizes knowledge into episodes:

1. **tac2_prompts** - Prompt entities
   - Prompt structure, delegations, tools
   - Example: "Prime command reads git ls-files and README.md"

2. **tac2_code** - Code entities
   - Functions, classes, imports
   - Example: "upload_file function accepts UploadFile, calls convert_csv_to_sqlite"

3. **lesson2_concepts** - Learning concepts
   - Concept definitions, categories
   - Example: "Core Four: Context, Model, Prompt, Tools"

4. **tac2_semantic_links** - Semantic matches
   - Code-to-concept relationships
   - Example: "List Built-in Tools demonstrates Core Four (0.319 similarity)"

### Knowledge Graph Structure

Graphiti automatically:
- Creates entity nodes (prompts, functions, concepts)
- Extracts relationships from text
- Generates embeddings for semantic search
- Enables temporal queries

## Querying the Knowledge Graph

### Using Python API

```python
import asyncio
from storage.graphiti_storage import GraphitiStorage

async def search_example():
    storage = GraphitiStorage(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )

    # Semantic search
    results = await storage.search("Show me all prompts", num_results=5)

    for result in results:
        print(result)

    await storage.close()

asyncio.run(search_example())
```

### Using Neo4j Browser

1. Open http://localhost:7474
2. Login with neo4j/password
3. Run Cypher queries:

```cypher
// Show all entities
MATCH (n) RETURN n LIMIT 25

// Find prompts
MATCH (n:Entity)
WHERE n.name CONTAINS 'Prompt'
RETURN n

// Find relationships
MATCH (a)-[r]->(b)
RETURN a, r, b LIMIT 50

// Search by episode
MATCH (n:Episode)
WHERE n.name = 'tac2_prompts'
RETURN n
```

## Example Queries

### 1. Find All Prompts
```python
results = await storage.search("list all TAC prompts")
```

### 2. Find Code Related to Concept
```python
results = await storage.search("which functions implement the Core Four?")
```

### 3. Find Delegations
```python
results = await storage.search("what prompts delegate to the prime command?")
```

### 4. Find Complex Functions
```python
results = await storage.search("show me functions with high complexity")
```

## Architecture

### Data Flow

```
Extracted Data (JSON)
  ↓
Graphiti Storage Module
  ↓
Episode Creation (text format)
  ↓
Graphiti Processing
  - Extract entities
  - Generate embeddings
  - Create relationships
  ↓
Neo4j Storage
  - Nodes: Entities
  - Edges: Relationships
  - Embeddings: Vector search
```

### Episode Types

- **Text Episodes**: Natural language descriptions
- **Temporal**: Timestamped for historical queries
- **Source**: Tagged by extraction stage

## Performance

### Ingestion Time (tac-2)

| Stage | Count | Time |
|-------|-------|------|
| Prompts | 5 | ~5s |
| Code | 12 modules | ~15s |
| Concepts | 5 | ~5s |
| Semantic | 2 matches | ~2s |
| **Total** | | **~30s** |

*Note: First run downloads OpenAI embeddings model*

### Storage Size

- Neo4j database: ~50-100 MB for tac-2
- Embeddings: ~5-10 MB
- Relationships: ~1-5 MB

## Troubleshooting

### Connection Refused

**Error**: `Failed to connect to Neo4j`

**Solutions:**
1. Verify Neo4j is running: `docker ps | grep neo4j`
2. Check connection URI: `bolt://localhost:7687`
3. Verify credentials: neo4j/password
4. Check firewall settings

### OPENAI_API_KEY Not Set

**Error**: `OPENAI_API_KEY environment variable required`

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Slow Ingestion

**Cause**: OpenAI API rate limits or embedding generation

**Solutions:**
1. Reduce batch size in code
2. Use caching for embeddings
3. Wait between API calls

### Empty Search Results

**Possible causes:**
1. No data ingested yet - run ingestion first
2. Query too specific - try broader terms
3. Embeddings not generated - check Graphiti logs

## Advanced Configuration

### Custom Neo4j Settings

Edit `graphiti_storage.py`:

```python
storage = GraphitiStorage(
    neo4j_uri="bolt://your-server:7687",
    neo4j_user="custom_user",
    neo4j_password="custom_password"
)
```

### Batch Ingestion

For large repositories, process in batches:

```python
# Process 10 entities at a time
for i in range(0, len(prompts), 10):
    batch = prompts[i:i+10]
    await storage.ingest_prompts(batch)
    await asyncio.sleep(1)  # Rate limiting
```

### Custom Episodes

Create episodes for specific analysis:

```python
await client.add_episode(
    name="security_analysis",
    episode_body="Found SQL injection in line 42",
    source=EpisodeType.text,
    reference_time=datetime.now()
)
```

## Next Steps

After ingestion:

1. **Query the graph**: Use semantic search to find relationships
2. **Visualize**: Use Neo4j Browser to explore
3. **Build MCP tools**: Create TAC-Teacher MCP server
4. **Temporal queries**: Track changes over time

## References

- Graphiti Documentation: https://help.getzep.com/graphiti
- Neo4j Cypher: https://neo4j.com/docs/cypher-manual/
- Neo4j Browser: http://localhost:7474
