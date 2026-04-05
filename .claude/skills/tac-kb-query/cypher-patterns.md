# Cypher/Graphiti Query Patterns

Reference for querying the TAC knowledge graph via Graphiti MCP tools.

## MCP Tool Reference

### search_nodes

Find entities in the knowledge graph.

```python
mcp__graphiti__search_nodes(
    query: str,              # Natural language search query
    group_ids: list[str],    # Filter by group (e.g., ["ai-agent-kb"])
    max_nodes: int = 10,     # Max results
    entity_types: list[str]  # Filter by entity type
)
```

**Entity Types in TAC KB:**
- `Expert` - TAC experts with mental models
- `ADW` - AI Developer Workflows
- `Tactic` - TAC tactics (#1-#8)
- `Framework` - PITER, R&D, Core Four, etc.
- `Pattern` - Design patterns (Pong, Echo, Calculator)
- `Concept` - General TAC concepts

### search_memory_facts

Find relationships between entities.

```python
mcp__graphiti__search_memory_facts(
    query: str,              # Natural language search query
    group_ids: list[str],    # Filter by group
    max_facts: int = 10,     # Max results
    center_node_uuid: str    # Center search around specific node
)
```

**Fact Types:**
- `CONTAINS` - Entity contains sub-entity
- `RELATES_TO` - General relationship
- `PRECEDES` - Sequential ordering
- `REQUIRES` - Dependency relationship
- `IMPLEMENTS` - Implementation relationship

### get_episodes

Retrieve source content that was ingested.

```python
mcp__graphiti__get_episodes(
    group_ids: list[str],    # Filter by group
    max_episodes: int = 10   # Max results
)
```

---

## Common Query Patterns

### Pattern 1: Concept Exploration

Find a concept and its relationships:

```python
# Step 1: Find the concept node
result = mcp__graphiti__search_nodes(
    query="Tactic #3 Template Your Engineering",
    group_ids=["ai-agent-kb"],
    max_nodes=5
)

# Step 2: Get relationships centered on that node
facts = mcp__graphiti__search_memory_facts(
    query="Template Your Engineering",
    center_node_uuid=result.nodes[0].uuid,
    max_facts=10
)
```

### Pattern 2: ADW Discovery

Find ADW workflows and their components:

```python
# Find ADW entities
adws = mcp__graphiti__search_nodes(
    query="plan_build_review workflow",
    group_ids=["ai-agent-kb"],
    entity_types=["ADW", "Workflow"]
)

# Get steps and dependencies
steps = mcp__graphiti__search_memory_facts(
    query="workflow steps sequence",
    group_ids=["ai-agent-kb"]
)
```

### Pattern 3: Expert Mental Model

Extract an expert's mental model:

```python
# Find the expert
expert = mcp__graphiti__search_nodes(
    query="TAC Expert methodology",
    entity_types=["Expert"]
)

# Get their knowledge areas
knowledge = mcp__graphiti__search_memory_facts(
    query="TAC expertise areas tactics",
    max_facts=20
)
```

### Pattern 4: Pattern Relationships

Discover how patterns relate:

```python
# Find pattern nodes
patterns = mcp__graphiti__search_nodes(
    query="Pong Echo Calculator agent patterns",
    entity_types=["Pattern"]
)

# See how they connect
relationships = mcp__graphiti__search_memory_facts(
    query="agent pattern relationships usage",
    max_facts=15
)
```

### Pattern 5: Framework Components

Understand framework structure:

```python
# Find framework
framework = mcp__graphiti__search_nodes(
    query="PITER framework",
    entity_types=["Framework"]
)

# Get components
components = mcp__graphiti__search_memory_facts(
    query="PITER Prompt Input Trigger Environment Review",
    max_facts=10
)
```

---

## Query Optimization Tips

### 1. Use Specific Entity Types

```python
# Slow - searches all entities
search_nodes(query="planning")

# Fast - filters to specific type
search_nodes(query="planning", entity_types=["ADW"])
```

### 2. Center Queries on Known Nodes

When you have a node UUID, use `center_node_uuid` to find directly related facts:

```python
# Get facts radiating from a specific node
search_memory_facts(
    query="",  # Can be empty when centered
    center_node_uuid="abc-123-def"
)
```

### 3. Use Group IDs

Always filter by group to avoid cross-contamination:

```python
# TAC knowledge base
group_ids=["ai-agent-kb"]

# Claude Code session history
group_ids=["claude-code-nci-oa-agent"]
```

### 4. Combine with Vector Search

For comprehensive results, query both systems:

```python
# Graphiti for concepts
concepts = search_memory_facts(query="plan_build_review")

# Vector for components
# python kb_search.py --vector-only "plan_build_review"
```

---

## Example Queries for TAC Learning

### Core Tactics (Lessons 1-8)

```python
# "What are the 8 TAC Tactics?"
mcp__graphiti__search_memory_facts(
    query="8 TAC tactics list Stop Coding Prioritize Agentics",
    group_ids=["ai-agent-kb"],
    max_facts=15
)

# "What is Tactic #4 Stay Out The Loop?"
mcp__graphiti__search_memory_facts(
    query="Tactic 4 Stay Out The Loop PITER framework",
    group_ids=["ai-agent-kb"]
)
```

### Advanced Lessons (9-15)

```python
# "What is Elite Context Engineering?" (Lesson 9)
mcp__graphiti__search_memory_facts(
    query="Elite Context Engineering R&D framework reduce delegate",
    group_ids=["ai-agent-kb"]
)

# "What are the 7 Prompt Levels?" (Lesson 10)
mcp__graphiti__search_memory_facts(
    query="7 prompt levels HOP Higher Order Prompt hierarchy",
    group_ids=["ai-agent-kb"]
)

# "How do I build specialized agents?" (Lesson 11)
mcp__graphiti__search_memory_facts(
    query="building specialized agents Pong Echo Calculator patterns",
    group_ids=["ai-agent-kb"]
)

# "What is multi-agent orchestration?" (Lesson 12)
mcp__graphiti__search_memory_facts(
    query="multi-agent orchestration O-Agent fleet management",
    group_ids=["ai-agent-kb"]
)

# "How does ACT-LEARN-REUSE work?" (Lesson 13)
mcp__graphiti__search_memory_facts(
    query="ACT LEARN REUSE agent-experts cycle expertise",
    group_ids=["ai-agent-kb"]
)

# "What is Orchestrator with ADWs?" (Lesson 14)
mcp__graphiti__search_memory_facts(
    query="orchestrator ADW AI Developer Workflow structured",
    group_ids=["ai-agent-kb"]
)

# "What is Software Delivery ADW?" (Lesson 15)
mcp__graphiti__search_memory_facts(
    query="software delivery ADW end-to-end workflow",
    group_ids=["ai-agent-kb"]
)
```

### TAC Repositories

```python
# "What does agent-sandboxes cover?"
mcp__graphiti__search_memory_facts(
    query="agent-sandboxes environment isolation Docker permission",
    group_ids=["ai-agent-kb"]
)

# "What is claude-code-damage-control?"
mcp__graphiti__search_memory_facts(
    query="damage control defense-in-depth safety validation rollback",
    group_ids=["ai-agent-kb"]
)

# "What does hooks-mastery teach?"
mcp__graphiti__search_memory_facts(
    query="hooks-mastery PreToolUse PostToolUse Notification Stop lifecycle",
    group_ids=["ai-agent-kb"]
)

# "What is rd-framework about?"
mcp__graphiti__search_memory_facts(
    query="R&D framework context window optimization reduce delegate",
    group_ids=["ai-agent-kb"]
)
```

### Key Frameworks

```python
# "What is the Core Four?"
mcp__graphiti__search_memory_facts(
    query="Core Four Context Model Prompt Tools fundamentals",
    group_ids=["ai-agent-kb"]
)

# "What is PITER framework?"
mcp__graphiti__search_memory_facts(
    query="PITER Prompt Input Trigger Environment Review automation",
    group_ids=["ai-agent-kb"]
)

# "What are the 12 Leverage Points?"
mcp__graphiti__search_memory_facts(
    query="12 leverage points agentic systems optimization",
    group_ids=["ai-agent-kb"]
)

# "What are Agentic KPIs?"
mcp__graphiti__search_memory_facts(
    query="Agentic KPIs key performance indicators metrics",
    group_ids=["ai-agent-kb"]
)
```

### Agent Patterns

```python
# "How do I choose between agent patterns?"
mcp__graphiti__search_memory_facts(
    query="when to use Pong vs Echo vs Calculator pattern",
    group_ids=["ai-agent-kb"]
)

# "What is the Meta-Agent pattern?"
mcp__graphiti__search_memory_facts(
    query="Meta-Agent pattern creates modifies agents factory",
    group_ids=["ai-agent-kb"]
)
```

### ADWs and Workflows

```python
# "What ADWs exist for code review?"
mcp__graphiti__search_nodes(
    query="code review workflow ADW",
    group_ids=["ai-agent-kb"],
    entity_types=["ADW"]
)

# "What primitives does TAC recommend?"
mcp__graphiti__search_memory_facts(
    query="TAC primitives command hook agent ADW skill",
    group_ids=["ai-agent-kb"]
)

# "What is plan_build_review workflow?"
mcp__graphiti__search_memory_facts(
    query="plan_build_review three-phase workflow validation",
    group_ids=["ai-agent-kb"]
)
```

---

## Interpreting Results

### Node Results

```json
{
  "uuid": "abc-123",
  "name": "Tactic #3 Template Your Engineering",
  "labels": ["Tactic", "Concept"],
  "summary": "Identify repeating problem classes and create reusable templates..."
}
```

### Fact Results

```json
{
  "uuid": "def-456",
  "fact": "Template Your Engineering enables ADW creation for problem classes",
  "source_node": {"name": "Tactic #3", "type": "Tactic"},
  "target_node": {"name": "ADW", "type": "Concept"},
  "relationship": "ENABLES",
  "valid_at": "2026-01-28T...",
  "invalid_at": null  // null means still valid
}
```

### Episode Results

```json
{
  "uuid": "ghi-789",
  "name": "TAC Expert Expertise",
  "source": "text",
  "content": "The TAC methodology consists of 8 tactics...",
  "created_at": "2026-01-28T..."
}
```

---

## Troubleshooting

### No results returned

1. Check group_id is correct (`"ai-agent-kb"`)
2. Verify Graphiti server is running
3. Try broader query terms
4. Check if Tier 1 ingestion has run

### Too many irrelevant results

1. Add entity_types filter
2. Use center_node_uuid for focused queries
3. Reduce max_nodes/max_facts

### Stale data

Facts have temporal metadata. Check `invalid_at`:
- `null` = still valid
- timestamp = superseded by newer information
