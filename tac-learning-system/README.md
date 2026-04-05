# TAC Learning System v2.0

> Comprehensive knowledge extraction and analysis platform for Tactical Agentic Coding repositories

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run complete analysis
python extract_all_robust.py

# 3. View interactive knowledge graph
# Open: data/graphs/knowledge_graph.html in your browser

# 4. Review metrics
# Read: data/analysis_summary.json
```

## What This Does

Analyzes TAC repositories to extract:
- 📄 **Prompts** - Command files with workflows and delegations
- 🐍 **Code** - Functions, classes, imports, call chains
- ⚙️ **Configs** - MCP servers, env vars, dependencies
- 📊 **Metrics** - Complexity, maintainability, security scores
- 🕸️ **Relationships** - Knowledge graph with 14 relationship types

## Output Files

```
data/
├── tac-2/
│   ├── prompts.json           # All prompt entities
│   ├── code_entities.json     # Functions, classes, modules
│   ├── config_entities.json   # MCP servers, env vars
│   └── static_analysis.json   # Quality and security metrics
│
├── lesson-2/
│   └── concepts.json          # Concepts from transcripts
│
├── graphs/
│   ├── knowledge_graph.json   # Raw graph data
│   └── knowledge_graph.html   # Interactive visualization ⭐
│
└── analysis_summary.json      # Complete pipeline summary
```

## Architecture

The system operates in 5 layers:

1. **Document Parsing** - Extract prompt structure
2. **Code Parsing** - AST analysis of Python files
3. **Config Parsing** - MCP, env, dependencies
4. **Static Analysis** - Radon (complexity) + Bandit (security)
5. **Graph Generation** - Multi-relational knowledge graph

## Individual Tools

Run parsers separately if needed:

```bash
# Parse prompts only
python parser/prompt_parser.py

# Parse code only (AST)
python parser/code_parser.py

# Parse configs only
python parser/config_parser.py

# Run static analysis only
python analysis/static_analyzer.py

# Build graph only
python graph/graph_builder.py
```

## Requirements

```
python-frontmatter==1.0.1
mistune==3.0.2
networkx>=3.0
pyvis>=0.3.2
radon>=6.0.1
bandit>=1.7.5
pyyaml==6.0.1
```

## Results (tac-2)

**Entities Extracted:**
- 5 Prompts
- 12 Modules
- 18 Functions
- 16 Classes
- 5 Concepts
- 2 Environment Variables

**Code Quality:**
- Average Complexity: **21.17** (B grade - well-structured)
- Maintainability Index: **76.24/100** (A grade - very maintainable)
- Security Issues: **118** (0 high severity)

**Knowledge Graph:**
- 56 nodes, 62 edges
- 6 node types, 14 relationship types
- Interactive HTML visualization

## Next Steps

1. **Semantic Matching** - Use embeddings to link prompts to concepts
2. **Graphiti Integration** - Store in Neo4j for semantic search
3. **Obsidian Vault** - Generate linked markdown notes
4. **TAC-Teacher MCP** - Build query tools for learning

## Documentation

See `SYSTEM_UPGRADE_SUMMARY.md` for:
- Complete architecture details
- Before/after comparison
- Technology stack
- Design decisions
- Relationship type definitions

## Configuration

Edit paths in `extract_all_robust.py`:

```python
repo_path = Path(r"C:\path\to\your\tac-repo")
output_base = Path(r"C:\path\to\output")
```

## Troubleshooting

**Bandit is slow:** Timeout is set to 30s per file. For large files, increase in `static_analyzer.py:137`

**Graph won't load:** Check browser console. pyvis requires JavaScript enabled.

**Import errors:** Ensure you're running from the `tac-learning-system` directory.

## License

Built for TAC learning - educational use.

## Credits

Architecture: Multi-layered knowledge extraction platform
Built with: Python AST, networkx, Radon, Bandit, pyvis
