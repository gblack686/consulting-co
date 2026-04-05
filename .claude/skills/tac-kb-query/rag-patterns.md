# RAG Query Patterns (pgvector)

Reference for querying the TAC vector index via `kb_search.py`.

## Overview

The pgvector index stores 149 KB components with OpenAI embeddings for semantic search:

| Folder | Records | Content |
|--------|---------|---------|
| commands | 106 | CLI commands and prompt templates |
| skills | 22 | Reusable skill modules |
| agents | 11 | Subagent configurations |
| output-styles | 11 | Output formatting templates |

## Script Location

```
.claude/scripts/kb_search.py
```

## Basic Usage

```bash
# Run from project root
python .claude/scripts/kb_search.py "your query here"
```

## Query Modes

### Default: Combined Search

Searches both vector index AND Graphiti knowledge graph:

```bash
python .claude/scripts/kb_search.py "plan_build_review workflow"
```

### Vector-Only Search

Fast, focused on specific components:

```bash
python .claude/scripts/kb_search.py --vector-only "git commit command"
```

### Graphiti-Only Search

Concepts and relationships (requires running Graphiti server):

```bash
python .claude/scripts/kb_search.py --graphiti-only "TAC methodology"
```

---

## Filtering Options

### By Folder

```bash
# Commands only
python .claude/scripts/kb_search.py --folder commands "git"

# Skills only
python .claude/scripts/kb_search.py --folder skills "diagram"

# Agents only
python .claude/scripts/kb_search.py --folder agents "build"

# Output styles only
python .claude/scripts/kb_search.py --folder output-styles "report"
```

### By Type

```bash
# Command type
python .claude/scripts/kb_search.py --type command "review"

# Skill type
python .claude/scripts/kb_search.py --type skill "planning"

# Agent type
python .claude/scripts/kb_search.py --type agent "implementation"
```

### Combined Filters

```bash
# Commands that are skills
python .claude/scripts/kb_search.py --folder commands --type skill "build"
```

---

## Result Control

### Adjust Result Count

```bash
# More results
python .claude/scripts/kb_search.py --top-k 20 "query"

# Fewer results
python .claude/scripts/kb_search.py --top-k 5 "query"
```

### Adjust Similarity Threshold

```bash
# Lower threshold (more results, possibly less relevant)
python .claude/scripts/kb_search.py --threshold 0.3 "query"

# Higher threshold (fewer, more relevant results)
python .claude/scripts/kb_search.py --threshold 0.7 "query"
```

### Verbose Output

Shows file paths and IDs:

```bash
python .claude/scripts/kb_search.py --verbose "query"
```

### JSON Output

For programmatic use:

```bash
python .claude/scripts/kb_search.py --json "query"
```

---

## Query Patterns by Use Case

### Pattern 1: Find Commands for a Task

```bash
# What commands help with planning?
python .claude/scripts/kb_search.py --folder commands "implementation planning"

# What commands help with code review?
python .claude/scripts/kb_search.py --folder commands "code review feedback"

# What commands help with git?
python .claude/scripts/kb_search.py --folder commands "git commit push"
```

### Pattern 2: Find Skills for a Capability

```bash
# Diagram creation skills
python .claude/scripts/kb_search.py --folder skills "diagram visualization"

# Memory and knowledge skills
python .claude/scripts/kb_search.py --folder skills "memory knowledge graph"

# Environment setup skills
python .claude/scripts/kb_search.py --folder skills "environment setup check"
```

### Pattern 3: Find Agents for Delegation

```bash
# Build/implementation agents
python .claude/scripts/kb_search.py --folder agents "build implementation code"

# Analysis/exploration agents
python .claude/scripts/kb_search.py --folder agents "explore analyze scout"

# Planning agents
python .claude/scripts/kb_search.py --folder agents "plan design architect"
```

### Pattern 4: Find Related Components

When you find one component, search for related ones:

```bash
# Found "plan" command, find related
python .claude/scripts/kb_search.py "plan_build_review workflow steps"

# Found "excalidraw" skill, find related
python .claude/scripts/kb_search.py "diagram visualization flowchart"
```

### Pattern 5: Broad Discovery

When exploring what's available:

```bash
# All available planning tools
python .claude/scripts/kb_search.py --verbose "planning implementation"

# All testing/validation tools
python .claude/scripts/kb_search.py --verbose "test validate review"

# All deployment tools
python .claude/scripts/kb_search.py --verbose "deploy infrastructure CDK"
```

---

## Result Interpretation

### Understanding Similarity Scores

| Score | Interpretation |
|-------|----------------|
| 0.8+ | Highly relevant |
| 0.6-0.8 | Relevant |
| 0.5-0.6 | Marginally relevant |
| <0.5 | Weak match (filtered by default) |

### Result Structure

Text output:
```
1. [VEC] [command] plan (0.82)
   Creates a concise engineering implementation plan...

2. [VEC] [skill] excalidraw (0.71)
   Create and edit Excalidraw diagrams programmatically...
```

JSON output:
```json
{
  "source": "vector",
  "id": "abc123",
  "name": "plan",
  "type": "command",
  "summary": "Creates a concise engineering...",
  "file_path": "commands/plan.md",
  "similarity": 0.82
}
```

---

## Programmatic Usage

Import in Python scripts:

```python
from kb_search import search_kb, SearchResult

# Basic search
results: list[SearchResult] = search_kb("git commit")

# With filters
results = search_kb(
    query="implementation planning",
    top_k=5,
    vector_only=True,
    folder_filter="commands",
    threshold=0.6
)

# Process results
for r in results:
    print(f"{r.name} ({r.type}): {r.similarity:.2f}")
    print(f"  Path: {r.file_path}")
    print(f"  Summary: {r.summary[:100]}...")
```

---

## Embedding Details

| Property | Value |
|----------|-------|
| Model | `text-embedding-3-small` |
| Dimensions | 1536 |
| Distance | Cosine |
| Index Type | IVFFlat (lists=100) |

### How Similarity is Calculated

```sql
1 - (embedding <=> query_embedding) AS similarity
```

The `<=>` operator computes cosine distance. Subtracting from 1 gives similarity.

---

## Troubleshooting

### "Missing dependency" Error

Install requirements:
```bash
pip install openai supabase boto3 httpx
```

### No Results Returned

1. **Lower threshold**:
   ```bash
   python .claude/scripts/kb_search.py --threshold 0.3 "query"
   ```

2. **Try different terms**: The index uses semantic search, so try synonyms

3. **Check the index has data**:
   ```bash
   python .claude/scripts/kb_search.py --json "" | wc -l
   ```

### Authentication Errors

The script gets credentials from AWS Secrets Manager. Ensure:
- AWS credentials are configured (`aws configure`)
- Secret `gbautomation/infrastructure/supabase` exists
- Secret contains `access_token` or `service_key`

### Slow Queries

- The first query initializes the OpenAI client (slight delay)
- Use `--vector-only` to skip Graphiti (faster)
- Reduce `--top-k` for fewer results

---

## Database Schema

The vector index table structure:

```sql
CREATE TABLE kb_index (
  id TEXT PRIMARY KEY,
  file_path TEXT NOT NULL,
  folder TEXT NOT NULL,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  summary TEXT NOT NULL,
  tags TEXT[],
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat index for fast cosine similarity
CREATE INDEX ON kb_index
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## Related Tools

| Tool | Purpose |
|------|---------|
| `kb_search.py` | Search both tiers |
| `create_vector_index.py` | Rebuild vector index |
| `execute_via_mcp.py` | Execute SQL via Management API |
| Graphiti MCP | Search knowledge graph |
