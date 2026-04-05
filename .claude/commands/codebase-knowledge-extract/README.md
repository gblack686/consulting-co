# Codebase Knowledge Extraction Commands

Slash commands for TAC Learning System v2.0 - comprehensive knowledge extraction and analysis.

## Quick Reference

| Command | Purpose | Runtime | Output |
|---------|---------|---------|--------|
| `/extract-all` | 🎯 **Run complete pipeline** | ~48s | All files + graph |
| `/parse-prompts` | Extract prompt entities | ~0.5s | `prompts.json` |
| `/parse-code` | AST-based code analysis | ~1.5s | `code_entities.json` |
| `/parse-configs` | Config & dependency parsing | ~0.3s | `config_entities.json` |
| `/analyze-code` | Static analysis (quality + security) | ~45s | `static_analysis.json` |
| `/match-semantics` | Link code to concepts (embeddings) | ~10s | `semantic_matches.json` |
| `/build-graph` | Generate knowledge graph | ~0.8s | `knowledge_graph.html` |
| `/store-graphiti` | 🔥 **Store in Neo4j for semantic search** | ~30s | Neo4j database |

## Recommended Workflow

### For First-Time Analysis
```bash
/extract-all
```
Runs all stages in sequence. Best for comprehensive analysis.

### For Incremental Updates
Run individual commands when specific files change:

```bash
# Code changed? Re-parse and re-analyze
/parse-code
/analyze-code

# Prompts changed? Re-parse and rebuild graph
/parse-prompts
/build-graph

# Configs changed? Re-parse
/parse-configs
```

## Command Details

### `/extract-all` - Master Pipeline
**Use when**: Running full analysis for the first time or want complete refresh

**Stages**:
1. Document parsing (prompts)
2. Code parsing (AST)
3. Config parsing (MCP, env, deps)
4. Static analysis (complexity, security)
5. Graph generation

**Output**: All JSON files + interactive graph + summary report

---

### `/parse-prompts` - Prompt Extraction
**Use when**: Prompt files (.md) have been added/modified

**Extracts**:
- Prompt structure (sections, workflows)
- Delegations (prompt → prompt references)
- Tool mentions
- Success criteria

**Output**: `data/tac-2/prompts.json`

---

### `/parse-code` - Code Analysis
**Use when**: Python files have been added/modified

**Extracts**:
- Functions (signatures, decorators, calls)
- Classes (inheritance, methods)
- Imports (dependencies)
- Type annotations

**Output**: `data/tac-2/code_entities.json`

---

### `/parse-configs` - Configuration Parsing
**Use when**: Config files have been modified (.mcp.json, .env, package.json)

**Extracts**:
- MCP server definitions
- Environment variables (secrets masked)
- Python/Node dependencies
- Build scripts

**Output**: `data/tac-2/config_entities.json`

---

### `/analyze-code` - Static Analysis
**Use when**: Want to check code quality or security

**Analyzes**:
- Cyclomatic complexity (Radon)
- Maintainability index (Radon)
- Security vulnerabilities (Bandit)
- Raw metrics (LOC, comments)

**Output**: `data/tac-2/static_analysis.json`

**Note**: Slowest step (~45s due to Bandit)

---

### `/build-graph` - Knowledge Graph
**Use when**: Want to visualize relationships after extraction

**Prerequisites**: Must have run extraction commands first

**Generates**:
- Multi-relational graph (networkx)
- Interactive HTML visualization (pyvis)
- Graph statistics

**Output**:
- `data/graphs/knowledge_graph.json`
- `data/graphs/knowledge_graph.html` ⭐

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Layer 5: Storage & Query (Graphiti) - Coming Soon      │
├─────────────────────────────────────────────────────────┤
│ Layer 4: Knowledge Graph (/build-graph)                │
├─────────────────────────────────────────────────────────┤
│ Layer 3: Static Analysis (/analyze-code)               │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Entity Extraction                             │
│   - /parse-code (AST)                                   │
│   - /parse-configs (MCP, env, deps)                     │
├─────────────────────────────────────────────────────────┤
│ Layer 1: Document Parsing (/parse-prompts)             │
└─────────────────────────────────────────────────────────┘
```

## Entity Types Extracted

- **Prompt** (5): Command files with workflows
- **Module** (12): Python files
- **Function** (18): Functions with full metadata
- **Class** (16): Classes with inheritance
- **Concept** (5): Learning concepts from transcripts
- **EnvVar** (2): Environment variables

## Relationship Types (14)

### Syntactic
- CALLS, IMPORTS, DEFINES, INHERITS, DECORATES

### Semantic
- DELEGATES_TO, INVOKES, REFERENCES

### Infrastructure
- USES_ENV, DEPENDS_ON, CONFIGURED_BY

### Conceptual
- DEMONSTRATES, IMPLEMENTS, SIMILAR_TO

## Output Structure

```
data/
├── tac-2/
│   ├── prompts.json           # /parse-prompts
│   ├── code_entities.json     # /parse-code
│   ├── config_entities.json   # /parse-configs
│   └── static_analysis.json   # /analyze-code
│
├── lesson-2/
│   └── concepts.json          # Concepts from transcripts
│
├── graphs/
│   ├── knowledge_graph.json   # /build-graph (data)
│   └── knowledge_graph.html   # /build-graph (viz)
│
└── analysis_summary.json      # /extract-all (summary)
```

## Viewing Results

### Interactive Graph
```bash
open data/graphs/knowledge_graph.html
```
Features:
- Hover for entity details
- Drag to rearrange
- Color-coded by type
- Physics simulation

### Summary Report
```bash
cat data/analysis_summary.json | jq
```

### Individual Files
```bash
# Prompts
cat data/tac-2/prompts.json | jq '.[] | {name, prompt_type}'

# Code quality
cat data/tac-2/static_analysis.json | jq '.metadata'

# Dependencies
cat data/tac-2/config_entities.json | jq '.dependencies'
```

## Performance Tips

1. **First run**: Use `/extract-all` for comprehensive analysis
2. **Incremental**: Use individual commands when specific files change
3. **Skip security**: Comment out Bandit in `static_analyzer.py` if speed is critical
4. **Large repos**: Consider parallel execution of independent stages

## Requirements

```bash
pip install python-frontmatter mistune networkx pyvis radon bandit pyyaml
```

## Documentation

- **Architecture**: See `SYSTEM_UPGRADE_SUMMARY.md`
- **Quick Start**: See `README.md`
- **Individual Commands**: See files in this directory

## Next Steps

After extraction, consider:
1. **Semantic Matching**: Link prompts to concepts via embeddings
2. **Graphiti Integration**: Store in Neo4j for semantic search
3. **Obsidian Vault**: Generate linked markdown notes
4. **TAC-Teacher MCP**: Build query tools for learning
