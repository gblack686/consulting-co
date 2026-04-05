---
name: tac-kb-query
description: Query TAC knowledge bases using Graphiti (knowledge graph) and pgvector (RAG) to learn about TAC methodology, discover patterns, and build new ADWs.
---

# TAC KB Query Skill

Query the AI-Agent-KB using two complementary approaches:
1. **Graphiti** - Knowledge graph for conceptual queries, relationships, mental models
2. **pgvector** - Vector index for finding specific components (commands, skills, agents)

## Quick Reference

| Query Type | Tool/Method | Best For |
|------------|-------------|----------|
| Concept relationships | `search_memory_facts` | "How does Tactic #3 relate to ADWs?" |
| Entity discovery | `search_nodes` | "What experts exist in the KB?" |
| Component lookup | `kb_search.py --vector-only` | "Find all commit-related commands" |
| Combined search | `kb_search.py` | "Everything about plan_build_review" |

## TAC Content Overview

The TAC knowledge base contains:

### 11 TAC Repositories
| Repository | Focus |
|------------|-------|
| agent-experts | ACT-LEARN-REUSE pattern for domain expertise |
| agentic-finance-review | Self-validating agents with feedback loops |
| agent-sandboxes | Environment isolation and sandboxing |
| building-domain-specific-agents | Specialized domain agent techniques |
| claude-code-damage-control | Defense-in-depth safety patterns |
| claude-code-hooks-mastery | Lifecycle hooks deep dive |
| multi-agent-orchestration-the-o-agent | Fleet management patterns |
| orchestrator-agent-with-adws | ADWs with orchestrator pattern |
| rd-framework-context-window-mastery | Context optimization |
| seven-levels-agentic-prompt-formats | Progressive prompt complexity |
| building-specialized-agents | Agent design patterns (Pong, Echo, Calculator) |

### 15 TAC Lessons
| Lesson | Topic |
|--------|-------|
| 1-8 | Core Tactics (Stop Coding → Prioritize Agentics) |
| 9 | Elite Context Engineering |
| 10 | Agentic Prompt Engineering |
| 11 | Building Specialized Agents |
| 12 | Multi-Agent Orchestration |
| 13 | Agent-Experts |
| 14 | Orchestrator Agent with ADWs |
| 15 | Software Delivery ADW |

### Key Frameworks
- **Core Four**: Context, Model, Prompt, Tools
- **PITER**: Prompt, Input, Trigger, Environment, Review
- **R&D**: Reduce & Delegate (context management)
- **ACT-LEARN-REUSE**: Agent learning cycle
- **12 Leverage Points**: Advanced agentic system optimization
- **7 Prompt Levels**: HOP (Higher Order Prompt) hierarchy

---

## Graphiti Queries (Knowledge Graph)

Use MCP tools to query the knowledge graph for TAC concepts and relationships.

### Available MCP Tools

| Tool | Use For |
|------|---------|
| `mcp__graphiti__search_nodes` | Find entities (experts, concepts, patterns) |
| `mcp__graphiti__search_memory_facts` | Find relationships between entities |
| `mcp__graphiti__get_episodes` | Retrieve source episodes (ingested content) |

### Example: Find TAC Concepts

```
mcp__graphiti__search_nodes(
  query="TAC tactics methodology",
  max_nodes=10,
  group_ids=["ai-agent-kb"]
)
```

### Example: Find Relationships

```
mcp__graphiti__search_memory_facts(
  query="plan_build_review workflow steps",
  max_facts=10,
  group_ids=["ai-agent-kb"]
)
```

### Example: Get Episodes

```
mcp__graphiti__get_episodes(
  group_ids=["ai-agent-kb"],
  max_episodes=20
)
```

## Vector Index Queries (pgvector/RAG)

Use `kb_search.py` to find specific KB components via semantic search.

### Script Location

```
.claude/scripts/kb_search.py
```

### Basic Usage

```bash
# Search all sources
python .claude/scripts/kb_search.py "how to create a git commit"

# Vector index only (fast, specific components)
python .claude/scripts/kb_search.py --vector-only "commit command"

# Filter by folder
python .claude/scripts/kb_search.py --folder commands "git"

# Filter by type
python .claude/scripts/kb_search.py --type skill "diagram"

# JSON output for programmatic use
python .claude/scripts/kb_search.py --json "ADW workflow"
```

### Command-Line Options

| Flag | Description |
|------|-------------|
| `--vector-only` | Only search pgvector index (skip Graphiti) |
| `--graphiti-only` | Only search knowledge graph (skip vectors) |
| `--folder <name>` | Filter by folder: commands, agents, skills, hooks |
| `--type <name>` | Filter by type: command, agent, skill, hook, expert |
| `--top-k <n>` | Max results per source (default: 10) |
| `--threshold <f>` | Min similarity threshold (default: 0.5) |
| `--verbose` | Show detailed output with file paths |
| `--json` | Output results as JSON |

### Indexed Content

| Folder | Count | Content |
|--------|-------|---------|
| commands | 106 | CLI commands, prompts |
| skills | 22 | Reusable skill modules |
| agents | 11 | Subagent configurations |
| output-styles | 11 | Output formatting templates |

## Combined Query Workflows

### Workflow 1: Learning About a TAC Concept

1. **Start with Graphiti** - Get conceptual understanding
   ```
   mcp__graphiti__search_memory_facts(
     query="Tactic #3 Template Your Engineering",
     max_facts=5
   )
   ```

2. **Find related components** - Get actionable items
   ```bash
   python .claude/scripts/kb_search.py --vector-only "template engineering"
   ```

3. **Read source files** - Deep dive into specific components

### Workflow 2: Building a New ADW

1. **Search for similar ADWs** - Learn from existing patterns
   ```
   mcp__graphiti__search_nodes(
     query="ADW workflow patterns",
     entity_types=["ADW", "Workflow"]
   )
   ```

2. **Find component building blocks**
   ```bash
   python .claude/scripts/kb_search.py --folder skills "planning"
   python .claude/scripts/kb_search.py --folder commands "build"
   ```

3. **Check for relevant agents**
   ```bash
   python .claude/scripts/kb_search.py --type agent "implementation"
   ```

### Workflow 3: Discovering Expertise

1. **Search for expert mental models**
   ```
   mcp__graphiti__search_nodes(
     query="expertise mental model patterns",
     max_nodes=10
   )
   ```

2. **Find related skills**
   ```bash
   python .claude/scripts/kb_search.py --type skill "expert"
   ```

## Query Patterns by Use Case

### "How do I...?" Questions

Use vector search for actionable answers:
```bash
python .claude/scripts/kb_search.py "how to create implementation plan"
```

### "What is...?" Questions

Use Graphiti for conceptual understanding:
```
mcp__graphiti__search_memory_facts(query="what is PITER framework")
```

### "Show me examples of..." Requests

Use vector search with type filters:
```bash
python .claude/scripts/kb_search.py --type command --verbose "example"
```

### "What relates to...?" Questions

Use Graphiti for relationship discovery:
```
mcp__graphiti__search_memory_facts(query="relates to plan_build_review")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Query Interface                          │
│  ┌─────────────────────┐  ┌─────────────────────────────┐  │
│  │  kb_search.py       │  │  MCP Tools                  │  │
│  │  (unified search)   │  │  (search_nodes, etc.)       │  │
│  └─────────┬───────────┘  └─────────────┬───────────────┘  │
└────────────┼────────────────────────────┼───────────────────┘
             │                            │
     ┌───────▼───────┐           ┌────────▼────────┐
     │  Supabase     │           │  Graphiti MCP   │
     │  pgvector     │           │  Server         │
     │  (149 records)│           │  (:8000)        │
     └───────────────┘           └────────┬────────┘
                                          │
                                 ┌────────▼────────┐
                                 │  FalkorDB       │
                                 │  Knowledge Graph│
                                 │  (:6379)        │
                                 └─────────────────┘
```

## Tier Strategy

| Tier | Source | Content | Query Method |
|------|--------|---------|--------------|
| **Tier 1** | Graphiti | Experts, ADWs, mental models | MCP tools |
| **Tier 2** | pgvector | Commands, skills, agents | kb_search.py |

### Why Two Tiers?

- **Graphiti** excels at relationship extraction and concept mapping
- **pgvector** provides fast semantic search for component lookup
- Combined approach gives comprehensive TAC understanding

## Prerequisites

### For pgvector queries:
- AWS credentials (for Secrets Manager)
- Python 3.11+ with: `openai`, `supabase`, `boto3`, `httpx`

### For Graphiti queries:
- Graphiti MCP server running (`/graphiti start`)
- FalkorDB accessible on port 6379

## Troubleshooting

### Vector search returns no results

1. Check similarity threshold (default 0.5 may be too high):
   ```bash
   python .claude/scripts/kb_search.py --threshold 0.3 "query"
   ```

2. Verify index has records:
   ```bash
   python .claude/scripts/kb_search.py --json "" | head
   ```

### Graphiti queries fail

1. Check MCP server status:
   ```bash
   curl http://localhost:8000/health
   ```

2. Start Graphiti if needed:
   ```bash
   /graphiti start
   ```

### Missing components in vector index

The index covers AI-Agent-KB folders:
- `commands/`, `agents/`, `skills/`, `output-styles/`

Expert files are in Graphiti (Tier 1), not vector index (Tier 2).

## Source Files

```
.claude/skills/tac-kb-query/
├── SKILL.md                      # This file
├── cypher-patterns.md            # Graphiti/Cypher query reference
├── rag-patterns.md               # pgvector RAG query patterns
└── combined-query-examples.md    # Full workflow examples
```

## Related Resources

- `/graphiti` - Graphiti MCP management
- `/experts:tac:question` - TAC methodology questions
- `/experts:memory:question` - Memory system questions
