# TAC Process Directory

Process a TAC repository directory for knowledge base ingestion (both Graphiti and pgvector).

## Usage

```
/tac-process-directory [directory_name]
/tac-process-directory --all
/tac-process-directory --list
```

## TAC Directory Inventory (22 directories)

### Core Tactics (8)
| Directory | Lesson | Topic |
|-----------|--------|-------|
| `tac-1` | Lesson 1 | Stop Coding |
| `tac-2` | Lesson 2 | Adopt Your Agent's Perspective |
| `tac-3` | Lesson 3 | Template Your Engineering |
| `tac-4` | Lesson 4 | Stay Out The Loop (PITER) |
| `tac-5` | Lesson 5 | Always Add Feedback Loops |
| `tac-6` | Lesson 6 | One Agent, One Prompt, One Purpose |
| `tac-7` | Lesson 7 | Target Zero-Touch Engineering |
| `tac-8` | Lesson 8 | Prioritize Agentics |

### Advanced Lessons (12)
| Directory | Lesson | Topic |
|-----------|--------|-------|
| `rd-framework-context-window-mastery` | 9 | Elite Context Engineering |
| `seven-levels-agentic-prompt-formats` | 10 | Agentic Prompt Engineering |
| `building-domain-specific-agents` | 11 | Building Specialized Agents |
| `multi-agent-orchestration-the-o-agent` | 12 | Multi-Agent Orchestration |
| `agent-experts` | 13 | Agent-Experts (ACT-LEARN-REUSE) |
| `orchestrator-agent-with-adws` | 14 | Orchestrator Agent with ADWs |
| `agentic-finance-review` | 15 | Software Delivery ADW |
| `claude-code-hooks-mastery` | - | Lifecycle Hooks Deep Dive |
| `claude-code-damage-control` | - | Defense-in-Depth Safety |
| `agent-sandboxes` | - | Environment Isolation |
| `agent-sandbox-skill` | - | Sandbox Skill Template |
| `fork-repository-skill` | - | Fork Repository Skill |

### TAC Root Path
```
C:\Users\gblac\OneDrive\Desktop\tac\
```

---

## Processing Workflow

When invoked, perform these steps:

### Step 1: Validate Directory

```bash
# Check directory exists
ls -la "C:/Users/gblac/OneDrive/Desktop/tac/${DIRECTORY}/"
```

### Step 2: Extract Key Content

For each TAC directory, extract and summarize:

| File/Folder | Priority | Content Type |
|-------------|----------|--------------|
| `README.md` | Required | Main concepts, overview |
| `CLAUDE.md` | High | Claude Code instructions |
| `.claude/commands/` | High | Command definitions |
| `.claude/skills/` | High | Skill modules |
| `.claude/agents/` | High | Agent configurations |
| `adws/` | High | ADW definitions |
| `ai_docs/` | Medium | Reference documentation |
| `specs/` | Medium | Implementation specs |
| `scripts/` | Low | Utility scripts |

### Step 3: Generate Summaries

For each directory, create a structured summary:

```yaml
name: {directory_name}
type: tac_repository
lesson: {lesson_number or null}
topic: {main topic}
path: C:/Users/gblac/OneDrive/Desktop/tac/{directory_name}
summary: |
  {2-3 sentence overview from README.md}
key_concepts:
  - {concept 1}
  - {concept 2}
  - {concept 3}
frameworks:
  - {framework if applicable}
patterns:
  - {pattern if applicable}
components:
  commands: [{list of commands}]
  skills: [{list of skills}]
  agents: [{list of agents}]
  adws: [{list of ADWs}]
```

### Step 4: Ingest to Knowledge Bases

#### Tier 1: Graphiti (Knowledge Graph)

```python
mcp__graphiti__add_memory(
    name=f"TAC Repository: {directory_name}",
    episode_body=summary_yaml,
    source="json",
    source_description="TAC repository documentation",
    group_id="ai-agent-kb"
)
```

#### Tier 2: pgvector (Vector Index)

For each component (command, skill, agent, ADW), add to vector index:

```python
# Run the indexer script
python .claude/scripts/create_vector_index.py --source tac --directory {directory_name}
```

---

## Output Format

After processing, output:

```
## TAC Directory Processed: {directory_name}

### Summary
{2-3 sentence overview}

### Key Concepts
- {concept 1}
- {concept 2}

### Components Found
| Type | Count | Names |
|------|-------|-------|
| Commands | {n} | {list} |
| Skills | {n} | {list} |
| Agents | {n} | {list} |
| ADWs | {n} | {list} |

### Ingestion Status
- [ ] Graphiti: {status}
- [ ] pgvector: {status}
```

---

## Examples

### Process Single Directory

```
/tac-process-directory tac-3
```

Output:
```
## TAC Directory Processed: tac-3

### Summary
Lesson 3: Template Your Engineering - Identify repeating problem classes
and create reusable templates to solve them systematically.

### Key Concepts
- Problem class identification
- Template creation
- Pattern extraction

### Components Found
| Type | Count | Names |
|------|-------|-------|
| Commands | 2 | plan, build |
| Skills | 0 | - |
| Agents | 0 | - |
| ADWs | 1 | plan_build |

### Ingestion Status
- [x] Graphiti: Added episode "TAC Repository: tac-3"
- [x] pgvector: Indexed 3 components
```

### List All Directories

```
/tac-process-directory --list
```

### Process All Directories

```
/tac-process-directory --all
```

---

## Processing Script

The command delegates to:

```
.claude/scripts/tac_process_directory.py
```

### Script Arguments

| Argument | Description |
|----------|-------------|
| `directory` | Single directory name to process |
| `--all` | Process all 22 directories |
| `--list` | List all directories with status |
| `--dry-run` | Show what would be processed without ingesting |
| `--graphiti-only` | Only ingest to knowledge graph |
| `--vector-only` | Only ingest to vector index |
| `--force` | Re-process even if already ingested |

---

## Status Tracking

Track which directories have been processed:

```
.claude/data/tac-processing-status.json
```

```json
{
  "last_updated": "2026-01-29T...",
  "directories": {
    "tac-1": {
      "processed": true,
      "graphiti_episode_id": "...",
      "vector_records": 3,
      "last_processed": "2026-01-29T..."
    },
    "tac-2": {
      "processed": false
    }
  }
}
```
