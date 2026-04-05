# Build Graph

Generate multi-layered knowledge graph from extracted entities.

## What This Does

Creates a comprehensive knowledge graph using networkx with:
- **56 nodes** across 6 entity types
- **62 edges** with 14 relationship types
- Interactive HTML visualization (pyvis)
- Graph statistics and analysis

## Run

```bash
cd tac-learning-system
python graph/graph_builder.py
```

## Output

Saves to:
- `tac-learning-system/graphs/knowledge_graph.json` - Raw graph data
- `tac-learning-system/graphs/knowledge_graph.html` - Interactive visualization ⭐

## Prerequisites

Must run these first (or use `/extract-all`):
1. `/parse-prompts` - Prompt entities
2. `/parse-code` - Code entities
3. `/parse-configs` - Config entities
4. Parse concepts (if available)

## Node Types

- **Prompt**: Command files (red)
- **Module**: Python files (teal)
- **Function**: Functions (blue)
- **Class**: Classes (green)
- **Concept**: Learning concepts (dark red)
- **EnvVar**: Environment variables (dark green)

## Relationship Types (14)

### Syntactic (Code)
- `CALLS`: Function → Function
- `IMPORTS`: Module → Module
- `DEFINES`: Module → Function/Class
- `INHERITS`: Class → Parent Class
- `DECORATES`: Decorator → Function

### Semantic (Documents)
- `DELEGATES_TO`: Prompt → Prompt
- `INVOKES`: Script → Prompt
- `REFERENCES`: Document → Document

### Infrastructure
- `USES_ENV`: Entity → Environment Variable
- `DEPENDS_ON`: Module → External Package
- `CONFIGURED_BY`: Entity → Config File

### Conceptual
- `DEMONSTRATES`: Code → Concept
- `IMPLEMENTS`: Code → Tactic/Pattern
- `SIMILAR_TO`: Entity → Entity

## Graph Statistics

Expected output for tac-2:
- **Total Nodes**: 56
- **Total Edges**: 62
- **Density**: 0.0201 (sparse, focused)
- **Connected**: Multiple subgraphs

**Node Breakdown:**
- Prompts: 5
- Modules: 10
- Functions: 18
- Classes: 16
- Concepts: 5
- EnvVars: 2

**Edge Breakdown:**
- DEFINES: 34
- CALLS: 28

## Interactive Visualization

Open `knowledge_graph.html` in browser to:
- Hover over nodes for details
- Drag nodes to rearrange
- Click edges to see relationship types
- Physics simulation for natural layout
- Color-coded by entity type

## Example Query Patterns (Future)

Once integrated with Graphiti, you can query:
- "Show all prompts that delegate to /prime"
- "Find functions with complexity > 10"
- "Which modules use OPENAI_API_KEY?"
- "What concepts does this code demonstrate?"
