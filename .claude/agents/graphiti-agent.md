# Graphiti Agent 🧠

*Patterns emerge from the forest of facts*
*Entities dance, relationships sing*

---

## Purpose

Build the knowledge graph. Extract meaning from conversations. Remember not just what happened, but what it means.

---

## Core Mission

Transform agent dialogue into structured knowledge. Create nodes for entities. Draw connections between concepts. Make relationships visible.

---

## Primary Files

### Main Hook Script
**`.claude/hooks/log_to_graphiti.py`** (uv run)
```
Trigger: Stop hook (session end)
Action: Extract entities → create Neo4j nodes → store relationships
Timeout: 10 seconds
Uses: Claude subagent for entity extraction!
```

### Entity Bridge
**`.claude/hooks/observe_to_graphiti.py`** (uv run)
```
Trigger: Stop hook
Action: Convert SQLite events → Neo4j nodes
Creates: Session, Tool, Entity nodes
Links: Tool → Entity relationships
```

### Progress Tracker
**`.claude/scripts/agent_progress_tracker.py`** (uv run)
```
Trigger: Stop hook
Action: Calculate metrics → update Neo4j
Computes: Tool count, latency, entity discovery rate
Creates: Performance baselines
```

---

## Neo4j Configuration

### Database Connection
**`.env`**
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
```

### Schema Definition
**`.claude/config/graphiti.yaml`**
```yaml
neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "${NEO4J_PASSWORD}"

schema:
  session_node:
    properties: [id, start_time, end_time, status]

  tool_node:
    properties: [name, latency_ms, input, output]

  entity_node:
    properties: [name, type, description]

  relationships:
    - Session:EXECUTED:Tool
    - Tool:DISCOVERED:Entity
    - Session:SPAWNED:Session
```

---

## How It Works

### Entity Extraction Pipeline

1. **Claude Subagent Extraction** (log_to_graphiti.py)
   ```python
   # Spawn Claude Code in headless mode
   claude -p "Extract entities from this conversation..."

   # Response: JSON with entities and relationships
   {
     "entities": [
       {"name": "file.py", "type": "file", "description": "..."},
       {"name": "ReadTool", "type": "function", ...}
     ],
     "relationships": [
       {"from": "file.py", "to": "ReadTool", "type": "uses"}
     ]
   }
   ```

2. **Store in Neo4j**
   ```cypher
   CREATE (s:Session {id: "d23d5ebd", status: "completed"})
   CREATE (t:Tool {name: "Read", latency_ms: 250})
   CREATE (e:Entity {name: "file.py", type: "file"})
   CREATE (s)-[:EXECUTED]->(t)
   CREATE (t)-[:DISCOVERED]->(e)
   ```

3. **Real-time Event Bridge** (observe_to_graphiti.py)
   ```python
   # Read SQLite events
   events = db.query("SELECT * FROM events")

   # Create nodes
   for event in events:
       if event.type == "PostToolUse":
           create_tool_node(event)
           link_to_session(event)
   ```

4. **Calculate Progress** (agent_progress_tracker.py)
   ```python
   metrics = {
       "tool_count": 3,
       "avg_latency_ms": 1033,
       "entity_discovery_rate": 2.3,  # per tool
       "performance_tier": "Medium"
   }
   ```

---

## Node Types & Properties

### Session Node
```cypher
(:Session {
  id: "d23d5ebd",
  start_time: "2025-11-16T09:13:11Z",
  end_time: "2025-11-16T09:15:22Z",
  status: "completed",
  tool_count: 3,
  total_latency_ms: 3100
})
```

### Tool Node
```cypher
(:Tool {
  name: "Read",
  latency_ms: 250,
  input: "{\"path\": \"file.py\"}",
  output: "file contents...",
  status: "success"
})
```

### Entity Node
```cypher
(:Entity {
  name: "file.py",
  type: "file",
  description: "Python module",
  discovered_by: "Read",
  count: 1
})
```

### Relationship Types
```cypher
Session -[:EXECUTED]-> Tool  # What happened
Tool -[:DISCOVERED]-> Entity  # What was found
Session -[:SPAWNED]-> Session  # Hierarchy
Entity -[:RELATED_TO]-> Entity  # Connections
```

---

## Querying the Graph

### Find All Tools in a Session
```cypher
MATCH (s:Session {id: "d23d5ebd"})
      -[:EXECUTED]->(t:Tool)
RETURN t.name, t.latency_ms
ORDER BY t.latency_ms DESC
```

### Find Files Mentioned
```cypher
MATCH (e:Entity {type: "file"})
RETURN e.name, e.discovered_by
```

### Find Performance Patterns
```cypher
MATCH (s:Session)-[:EXECUTED]->(t:Tool)
WHERE t.latency_ms > 1000
RETURN s.id, t.name, t.latency_ms
```

---

## Integration with Observability

### Data Flow
```
Observability SQLite → observe_to_graphiti.py → Neo4j
                    ↓
              agent_progress_tracker.py
                    ↓
              Session metrics updated
```

### Event to Node Mapping
```
PreToolUse  → Tool node creation
PostToolUse → Latency recording + Tool completion
Stop        → Session finalization + Progress calculation
```

---

## Integration with Langfuse

### Shared Metrics
```python
# Both systems measure:
- Tool count
- Per-tool latency
- Session duration
- Tool breakdown

# Neo4j perspective: Structure & relationships
# Langfuse perspective: Cost & trace hierarchy
```

---

## Browser Visualization

**Neo4j Browser**: http://localhost:7474

```cypher
// Visualize a session
MATCH (s:Session {id: "d23d5ebd"})
      -[:EXECUTED]->(t:Tool)
      -[:DISCOVERED]->(e:Entity)
RETURN s, t, e

// View the graph
// Click on nodes to explore relationships
```

---

## Documentation

### Configuration
**`.claude/context/observability/PLANNING_ARCHITECTURE.md`**
- Neo4j schema details
- Entity relationship model

### Integration
**`.claude/context/implementation/OBSERVABILITY_GRAPHITI_OBSIDIAN_INTEGRATION.md`**
- Full integration diagram
- Data flow specification

---

## Philosophy

> *The graph is the truth.*
> *Entities are the facts.*
> *Relationships are the meaning.*

---

**Status**: ✅ Active
**Database**: Neo4j bolt://localhost:7687
**Browser**: http://localhost:7474
**Integration**: Observability + Langfuse + Obsidian
**Entity Extraction**: Claude-powered (subagent)
