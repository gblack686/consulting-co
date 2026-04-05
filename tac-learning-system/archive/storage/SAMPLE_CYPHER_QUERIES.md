# Sample Cypher Queries for TAC Knowledge Graph

> **Note:** Neo4j is not currently running. These are example queries to run after ingesting data.

## Setup First

### 1. Start Neo4j
```bash
# Start Docker Desktop first, then:
docker run \
    --name neo4j-tac \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

### 2. Ingest Data
```bash
cd tac-learning-system
export OPENAI_API_KEY="sk-..."
python storage/graphiti_storage.py
```

### 3. Run Sample Queries
```bash
# Using Python
python storage/query_neo4j.py

# Or open Neo4j Browser
# http://localhost:7474
```

---

## Sample Cypher Queries

### 1. Database Statistics

**Count all nodes:**
```cypher
MATCH (n)
RETURN count(n) as total_nodes
```

**Count nodes by label:**
```cypher
MATCH (n)
RETURN labels(n) as label, count(n) as count
ORDER BY count DESC
```

**Count all relationships:**
```cypher
MATCH ()-[r]->()
RETURN count(r) as total_relationships
```

**Count relationships by type:**
```cypher
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
```

---

### 2. Find Core Concepts

**Find all episodes about concepts:**
```cypher
MATCH (e:Episode)
WHERE e.name CONTAINS 'concept'
RETURN e.name, e.content
LIMIT 10
```

**Search for "Core Four":**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'Core Four'
RETURN e.name as episode,
       substring(e.content, 0, 300) as preview
```

**Find concept definitions:**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'Definition:'
RETURN e.name,
       substring(e.content, 0, 200) as definition
LIMIT 10
```

---

### 3. Find TAC Prompts

**All prompt episodes:**
```cypher
MATCH (e:Episode)
WHERE e.name CONTAINS 'prompt'
RETURN e.name, e.created_at
ORDER BY e.created_at DESC
```

**Prompts with delegations:**
```cypher
MATCH (e:Episode)
WHERE e.name CONTAINS 'prompt'
  AND e.content CONTAINS 'Delegations:'
RETURN e.name,
       substring(e.content, 0, 300) as content
```

**Find specific prompt:**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'Prompt: Prime'
RETURN e.name, e.content
```

---

### 4. Find Code Entities

**All code modules:**
```cypher
MATCH (e:Episode)
WHERE e.name CONTAINS 'code'
  AND e.content CONTAINS 'Python Module:'
RETURN e.name,
       substring(e.content, 0, 200) as preview
LIMIT 10
```

**Functions with decorators:**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'Decorators:'
RETURN e.name,
       substring(e.content, 0, 300) as content
LIMIT 10
```

**High complexity functions:**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'Complexity:'
  AND e.content =~ '.*Complexity: [1-9][0-9]+.*'
RETURN e.name,
       substring(e.content, 0, 200) as content
```

---

### 5. Find Semantic Matches

**All semantic matches:**
```cypher
MATCH (e:Episode)
WHERE e.name CONTAINS 'semantic'
RETURN e.name, e.content
```

**Code-to-concept links:**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'demonstrates concept'
RETURN substring(e.content, 0, 300) as match_description
```

**High similarity matches:**
```cypher
MATCH (e:Episode)
WHERE e.content CONTAINS 'Similarity Score:'
  AND e.content =~ '.*Similarity Score: 0\\.[4-9].*'
RETURN e.name,
       substring(e.content, 0, 250) as high_similarity_match
```

---

### 6. Find Entities (Extracted by Graphiti)

**All entities:**
```cypher
MATCH (n:Entity)
RETURN n.name, n.summary
LIMIT 20
```

**Entities by type:**
```cypher
MATCH (n:Entity)
WHERE n.entity_type IS NOT NULL
RETURN n.entity_type as type, count(n) as count
ORDER BY count DESC
```

**Find specific entity:**
```cypher
MATCH (n:Entity)
WHERE n.name CONTAINS 'Core Four'
RETURN n.name, n.summary, n.created_at
```

---

### 7. Graph Relationships

**Show sample graph:**
```cypher
MATCH (a)-[r]->(b)
RETURN a.name as from,
       type(r) as relationship,
       b.name as to
LIMIT 25
```

**Find all relationships for an entity:**
```cypher
MATCH (n:Entity {name: 'Core Four'})-[r]-(connected)
RETURN n.name, type(r), connected.name
```

**Path between two entities:**
```cypher
MATCH path = shortestPath(
  (a:Entity {name: 'Prime'})-[*]-(b:Entity {name: 'Core Four'})
)
RETURN path
```

---

### 8. Temporal Queries

**Recent episodes (last 7 days):**
```cypher
MATCH (e:Episode)
WHERE e.created_at > datetime() - duration('P7D')
RETURN e.name, e.created_at
ORDER BY e.created_at DESC
```

**Episodes by date:**
```cypher
MATCH (e:Episode)
RETURN date(e.created_at) as date,
       count(e) as episodes_created
ORDER BY date DESC
```

---

### 9. Full-Text Search

**Search all content:**
```cypher
MATCH (e:Episode)
WHERE toLower(e.content) CONTAINS toLower('upload file')
RETURN e.name, substring(e.content, 0, 200) as preview
LIMIT 10
```

**Multi-keyword search:**
```cypher
MATCH (e:Episode)
WHERE (e.content CONTAINS 'Core Four' OR e.content CONTAINS 'SDLC')
RETURN e.name, substring(e.content, 0, 200) as preview
```

---

### 10. Complex Queries

**Find prompts demonstrating concepts:**
```cypher
MATCH (prompt:Episode), (concept:Episode)
WHERE prompt.name CONTAINS 'prompt'
  AND concept.name CONTAINS 'concept'
  AND EXISTS {
    MATCH (semantic:Episode)
    WHERE semantic.name CONTAINS 'semantic'
      AND semantic.content CONTAINS prompt.name
      AND semantic.content CONTAINS concept.name
  }
RETURN prompt.name as prompt_name,
       concept.name as concept_name
```

**Aggregate statistics:**
```cypher
MATCH (e:Episode)
RETURN e.name as episode_type,
       count(e) as count,
       min(e.created_at) as first_created,
       max(e.created_at) as last_created
ORDER BY count DESC
```

---

## Expected Results (After Ingestion)

### Episode Breakdown
- **tac2_prompts**: 5 episodes (one per prompt)
- **tac2_code**: 12 episodes (one per module)
- **lesson2_concepts**: 5 episodes (one per concept)
- **tac2_semantic_links**: 2 episodes (semantic matches)

### Entity Extraction
After Graphiti processes episodes, you should see:
- **Entity nodes**: Extracted entities (prompts, functions, concepts)
- **Relationship edges**: Connections between entities
- **Embeddings**: Similarity scores for semantic search

---

## Running Queries

### Option 1: Neo4j Browser (Visual)
1. Open http://localhost:7474
2. Login: neo4j / password
3. Paste queries above
4. Click "Play" button
5. View results as table or graph

### Option 2: Python Script
```bash
cd tac-learning-system
python storage/query_neo4j.py
```

### Option 3: Programmatic
```python
from storage.query_neo4j import Neo4jQueryRunner

runner = Neo4jQueryRunner()

# Custom query
result = runner.run_query("""
    MATCH (e:Episode)
    WHERE e.content CONTAINS 'Core Four'
    RETURN e.name, e.content
""")

for record in result:
    print(record['e.name'])
    print(record['e.content'])

runner.close()
```

---

## Troubleshooting

### No results found?

**Check data ingestion:**
```cypher
// Should return >0
MATCH (e:Episode)
RETURN count(e) as episode_count
```

If 0, run ingestion:
```bash
python storage/graphiti_storage.py
```

### Neo4j connection error?

**Verify Neo4j is running:**
```bash
docker ps | grep neo4j
```

**Check connection:**
```bash
# Should see "Connected to Neo4j"
python storage/query_neo4j.py
```

### Entities not extracted?

Graphiti processes episodes asynchronously. Wait a few minutes, then check:
```cypher
MATCH (n:Entity)
RETURN count(n)
```

---

## Advanced Queries

### Find Related Entities
```cypher
MATCH (e:Entity {name: 'upload_file'})-[r]-(related)
RETURN e.name, type(r), related.name, related.summary
```

### Semantic Similarity
```cypher
// Find entities similar to "Core Four"
MATCH (target:Entity {name: 'Core Four'})
MATCH (other:Entity)
WHERE other <> target
  AND other.embedding IS NOT NULL
  AND target.embedding IS NOT NULL
RETURN other.name,
       gds.similarity.cosine(target.embedding, other.embedding) as similarity
ORDER BY similarity DESC
LIMIT 10
```

### Community Detection
```cypher
// Find clusters of related entities
CALL gds.louvain.stream('myGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name as entity,
       communityId
ORDER BY communityId
```

---

## Next Steps

1. **Start Neo4j**: `docker run ... neo4j`
2. **Ingest data**: `python storage/graphiti_storage.py`
3. **Run queries**: `python storage/query_neo4j.py`
4. **Explore visually**: Open http://localhost:7474
5. **Build on**: Create custom queries for your use case

---

## References

- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/
- Graphiti Documentation: https://help.getzep.com/graphiti
- Neo4j Browser Guide: http://localhost:7474/browser/

---

**To run sample queries right now:**

```bash
# 1. Start Neo4j (if Docker Desktop is running)
docker run --name neo4j-tac -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

# 2. Set API key
export OPENAI_API_KEY="sk-..."

# 3. Ingest data
python storage/graphiti_storage.py

# 4. Run queries
python storage/query_neo4j.py

# 5. Or open browser
# http://localhost:7474
```
