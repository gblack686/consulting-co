# Extract All

Run complete knowledge extraction pipeline - all 5 stages in sequence.

## What This Does

Executes the comprehensive analysis pipeline:

1. **Document Parsing** - Extract prompt entities
2. **Code Parsing** - AST-based Python analysis
3. **Config Parsing** - MCP servers, env vars, dependencies
4. **Static Analysis** - Complexity, maintainability, security
5. **Graph Generation** - Multi-relational knowledge graph

## Run

```bash
cd tac-learning-system
python extract_all_robust.py
```

## Total Runtime

~48 seconds for tac-2 repository (12 Python files)

Breakdown:
- Document parsing: ~0.5s
- Code parsing: ~1.5s
- Config parsing: ~0.3s
- Static analysis: ~45s (Bandit is slow)
- Graph generation: ~0.8s

## Output Files

All saved to `tac-learning-system/data/`:

```
data/
├── tac-2/
│   ├── prompts.json           # Prompt entities
│   ├── code_entities.json     # Code entities (functions, classes)
│   ├── config_entities.json   # Config entities (MCP, env)
│   └── static_analysis.json   # Quality & security metrics
│
├── lesson-2/
│   └── concepts.json          # Concept entities
│
├── graphs/
│   ├── knowledge_graph.json   # Raw graph data
│   └── knowledge_graph.html   # Interactive visualization ⭐
│
└── analysis_summary.json      # Complete pipeline summary
```

## Expected Results (tac-2)

### Entities Extracted
- Prompts: 5
- Modules: 12
- Functions: 18
- Classes: 16
- Concepts: 5
- Environment Variables: 2

### Code Quality
- Average Complexity: 21.17 (B grade)
- Maintainability: 76.24/100 (A grade)
- Security Issues: 118 (0 high severity)
- Complex Functions: 2

### Knowledge Graph
- Total Nodes: 56
- Total Edges: 62
- Node Types: 6
- Relationship Types: 14

## Viewing Results

1. **Interactive Graph**:
   ```bash
   open data/graphs/knowledge_graph.html
   ```
   (Or drag into browser)

2. **Summary Report**:
   ```bash
   cat data/analysis_summary.json
   ```

3. **Individual Files**:
   - Prompts: `data/tac-2/prompts.json`
   - Code: `data/tac-2/code_entities.json`
   - Configs: `data/tac-2/config_entities.json`
   - Analysis: `data/tac-2/static_analysis.json`

## Console Output

The script prints progress for each stage:

```
============================================================
TAC REPOSITORY COMPREHENSIVE ANALYSIS
============================================================

🔍 Stage 1: Document Parsing (Prompts)
------------------------------------------------------------
✅ Extracted 5 prompts

🐍 Stage 2: Code Parsing (AST)
------------------------------------------------------------
✅ Extracted 18 functions
✅ Extracted 16 classes
✅ Extracted 53 imports

⚙️  Stage 3: Config Parsing (MCP, Env, Dependencies)
------------------------------------------------------------
✅ Extracted 0 MCP servers
✅ Extracted 2 environment variables

📊 Stage 4: Static Analysis (Complexity, Security)
------------------------------------------------------------
✅ Average complexity: 21.17
✅ Average maintainability: 76.24/100
✅ Security issues: 118 (0 high severity)

🕸️  Stage 5: Graph Generation (Relationships)
------------------------------------------------------------
✅ Total nodes: 56
✅ Total edges: 62

============================================================
COMPREHENSIVE ANALYSIS SUMMARY
============================================================

✅ All stages complete!
📁 Output directory: tac-learning-system/data
🌐 Interactive graph: tac-learning-system/data/graphs/knowledge_graph.html

============================================================
🎉 ANALYSIS COMPLETE!
============================================================
```

## Configuration

Edit paths in `extract_all_robust.py`:

```python
repo_path = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")
output_base = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data")
```

## Individual Commands

To run stages separately:
- `/parse-prompts` - Stage 1 only
- `/parse-code` - Stage 2 only
- `/parse-configs` - Stage 3 only
- `/analyze-code` - Stage 4 only
- `/build-graph` - Stage 5 only

## Troubleshooting

**Bandit timeout**: Increase timeout in `static_analyzer.py:137`
**Import errors**: Run from `tac-learning-system` directory
**Graph won't load**: Enable JavaScript in browser
