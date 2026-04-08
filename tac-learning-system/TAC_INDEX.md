---
name: TAC Learning System Index
description: Curriculum index for elite context engineering, agent composition, and multi-agent orchestration patterns
version: 1.0
updated: 2026-04-08
---

# TAC Learning System — Pattern Discovery Guide

## Directory Structure

```
tac-learning-system/
├── elite-context-engineering/    # How to load and manage context for agents
├── building-specialized-agents/  # Agent architecture patterns
├── multi-agent-orchestration/    # Multi-agent coordination
├── software-delivery-adw/        # Delivery workflows (ADW pattern)
├── tac-1/                        # TAC Level 1 curriculum
├── tac-2/                        # TAC Level 2 curriculum
├── extractor/                    # Knowledge extraction patterns
├── index/                        # Cross-references and indices
├── data/                         # Sample data and configs
└── diagrams/                     # Architecture diagrams
```

## Prompting Patterns by Category

### Context Engineering
- **Context windowing**: How to manage large codebases in limited context
- **Progressive loading**: Load only what's needed, expand on demand
- **Cross-referencing**: Link related files and decisions

### Agent Composition
- **Single responsibility**: One agent, one job
- **Tool selection**: Right tools for the right agent
- **Domain rules**: Restrict what agents can read/write/delete
- **Expertise yaml**: Accumulated knowledge per agent

### Multi-Agent Orchestration
- **Orchestrator pattern**: Central coordinator delegates to teams
- **Depth-2 delegation**: Orchestrator → Lead → Member (max depth)
- **Sequential vs parallel**: When to serialize vs parallelize
- **TillDone pattern**: Track tasks through completion with state machine

### Software Delivery (ADW)
- **ADW = Agentic Delivery Workflow**: Plan → Build → Validate → Deploy
- **Index tracking**: ADW_INDEX.md tracks all deliveries
- **Answer keys**: ANSWER_KEY.md for validation criteria

## Quick Search

```bash
# Find patterns for a specific topic
find ~/repos/consulting-co/tac-learning-system/ -name "*.md" | xargs grep -l "keyword"

# Browse by category
ls ~/repos/consulting-co/tac-learning-system/<category>/

# Read the master index
cat ~/repos/consulting-co/tac-learning-system/README.md
```
