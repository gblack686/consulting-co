# Observability to Graphiti Knowledge Graph Integration Architecture

## Executive Summary

This document specifies the technical architecture for integrating the Claude Code Observability system with Graphiti (Neo4j knowledge graph) and Obsidian vault. The integration enables real-time transformation of agent execution traces into a queryable knowledge graph and exportable markdown notes.

**Key Innovation**: Leverage existing Graphiti entity extraction while adding structured agent telemetry (sessions, tools, latency, subagent hierarchies) to create a comprehensive AI development knowledge base.

---

## 1. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE AGENT SESSION                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY HOOKS LAYER                     │
│  PreToolUse → PostToolUse → SubagentStop → Stop                 │
│  (send_event.py to SQLite events.db)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY SQLite DATABASE                  │
│  source_app | session_id | hook_event_type | payload | ts       │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
    ┌───────────────────────┐  ┌──────────────────────┐
    │ REAL-TIME PROCESSING  │  │  BATCH PROCESSING    │
    │ (observe_to_graphiti) │  │  (log_to_graphiti)   │
    └───────────────────────┘  └──────────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              GRAPHITI EVENT TRANSFORMATION LAYER                 │
│  • Session lifecycle tracking                                    │
│  • Tool invocation mapping                                       │
│  • Subagent hierarchy resolution                                 │
│  • Entity extraction orchestration                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       NEO4J KNOWLEDGE GRAPH                      │
│  ┌──────────────┐  ┌────────────┐  ┌─────────────┐            │
│  │   Session    │  │    Tool    │  │   Subagent  │            │
│  │    Nodes     │  │   Nodes    │  │    Nodes    │            │
│  └──────────────┘  └────────────┘  └─────────────┘            │
│  ┌──────────────┐  ┌────────────┐                              │
│  │   Entity     │  │  Episode   │                              │
│  │   Nodes      │  │   Nodes    │  (Graphiti native)          │
│  └──────────────┘  └────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROGRESS METRICS CALCULATOR                    │
│  • Session timeline & duration                                   │
│  • Tool usage statistics                                         │
│  • Subagent hierarchy analysis                                   │
│  • Entity discovery rate                                         │
│  • Performance benchmarks                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OBSIDIAN MARKDOWN EXPORTER                      │
│  Daily Summaries │ Session Reports │ Entity Maps                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OBSIDIAN VAULT                            │
│  ~/obsidian/consulting-co/                                       │
│  ├── daily/2025-11-15.md                                         │
│  ├── sessions/consulting-co_abc12345.md                         │
│  └── entities/file_handler_py.md                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Neo4j Schema Design

### 2.1 Node Types

#### **AgentSession** Node
Represents a complete agent execution session.

```cypher
CREATE (s:AgentSession {
  session_id: String,              // Unique session identifier (first 8 chars used in display)
  source_app: String,              // Application name (e.g., "consulting-co")
  agent_id: String,                // Display format: "source_app:session_id_short"
  start_time: DateTime,            // Session start timestamp
  end_time: DateTime,              // Session end timestamp (null if in progress)
  status: String,                  // "in_progress" | "completed" | "failed" | "subagent"
  model_name: String,              // LLM model used (e.g., "claude-sonnet-4-5-20250929")
  total_tools: Integer,            // Count of tool invocations
  avg_tool_latency_ms: Float,      // Average tool execution time
  total_entities: Integer,         // Count of discovered entities
  hierarchy_depth: Integer,        // Max subagent nesting level (0 = root)
  parent_session_id: String,       // Reference to parent if subagent
  created_at: DateTime,            // Node creation timestamp
  updated_at: DateTime             // Last update timestamp
})
```

**Indexes**:
```cypher
CREATE INDEX session_id_idx FOR (s:AgentSession) ON (s.session_id);
CREATE INDEX source_app_idx FOR (s:AgentSession) ON (s.source_app);
CREATE INDEX agent_id_idx FOR (s:AgentSession) ON (s.agent_id);
```

#### **ToolInvocation** Node
Represents a single tool call during an agent session.

```cypher
CREATE (t:ToolInvocation {
  tool_call_id: String,            // Unique identifier for this tool call
  session_id: String,              // Reference to parent session
  tool_name: String,               // Name of tool (Read, Edit, Bash, etc.)
  start_time: DateTime,            // PreToolUse timestamp
  end_time: DateTime,              // PostToolUse timestamp
  latency_ms: Float,               // Execution duration (end_time - start_time)
  status: String,                  // "success" | "error" | "blocked"
  input_summary: String,           // Truncated JSON of tool input (max 500 chars)
  output_summary: String,          // Truncated tool output (max 500 chars)
  error_message: String,           // Error details if status=error
  sequence_number: Integer,        // Tool order within session (1-based)
  created_at: DateTime
})
```

**Indexes**:
```cypher
CREATE INDEX tool_session_idx FOR (t:ToolInvocation) ON (t.session_id);
CREATE INDEX tool_name_idx FOR (t:ToolInvocation) ON (t.tool_name);
```

#### **SubagentExecution** Node
Tracks subagent spawn events and their lifecycle.

```cypher
CREATE (sa:SubagentExecution {
  subagent_session_id: String,     // Session ID of the subagent
  parent_session_id: String,       // Session ID of parent agent
  start_time: DateTime,            // When subagent was spawned
  end_time: DateTime,              // When subagent completed
  purpose: String,                 // Extracted intent/purpose
  outcome: String,                 // What the subagent accomplished
  depth_level: Integer,            // Nesting depth (1 = direct child)
  created_at: DateTime
})
```

**Indexes**:
```cypher
CREATE INDEX subagent_parent_idx FOR (sa:SubagentExecution) ON (sa.parent_session_id);
```

#### **Entity** Node (Graphiti Native)
Graphiti automatically creates Entity nodes from episode text. We'll add custom properties.

```cypher
// Graphiti creates these, we add custom properties via MERGE
MERGE (e:Entity {name: String})
ON CREATE SET
  e.entity_type = String,          // file|function|concept|technology|pattern
  e.first_seen = DateTime,
  e.mention_count = 1,
  e.sessions = [session_id]
ON MATCH SET
  e.mention_count = e.mention_count + 1,
  e.sessions = e.sessions + session_id
```

#### **Episode** Node (Graphiti Native)
Graphiti's native episode node stores conversation turns.

```cypher
// Graphiti creates these automatically
(ep:Episode {
  name: String,                    // e.g., "consulting-co-abc12345-20251115-143022"
  source_description: String,
  content: String,                 // Full episode text
  created_at: DateTime,
  reference_time: DateTime
})
```

### 2.2 Relationship Types

```cypher
// Session hierarchy
(parent:AgentSession)-[:SPAWNED_SUBAGENT]->(child:AgentSession)

// Tool invocations
(s:AgentSession)-[:INVOKED_TOOL]->(t:ToolInvocation)

// Subagent tracking
(parent:AgentSession)-[:HAS_SUBAGENT]->(sa:SubagentExecution)
(sa:SubagentExecution)-[:EXECUTED_AS]->(child:AgentSession)

// Entity discovery
(s:AgentSession)-[:DISCOVERED_ENTITY]->(e:Entity)
(t:ToolInvocation)-[:REFERENCED_ENTITY]->(e:Entity)

// Episode linkage
(s:AgentSession)-[:GENERATED_EPISODE]->(ep:Episode)
(ep:Episode)-[:MENTIONS_ENTITY]->(e:Entity)  // Graphiti creates this

// Sequential tool order
(t1:ToolInvocation)-[:NEXT_TOOL]->(t2:ToolInvocation)
```

### 2.3 Constraints

```cypher
CREATE CONSTRAINT unique_session_id FOR (s:AgentSession) REQUIRE s.session_id IS UNIQUE;
CREATE CONSTRAINT unique_tool_call_id FOR (t:ToolInvocation) REQUIRE t.tool_call_id IS UNIQUE;
CREATE CONSTRAINT unique_subagent_session FOR (sa:SubagentExecution) REQUIRE sa.subagent_session_id IS UNIQUE;
```

---

## 3. Event Processing Pipeline

### 3.1 SQLite Event Schema

The observability backend stores events in SQLite with this structure:

```sql
-- Inferred from send_event.py
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_app TEXT NOT NULL,
  session_id TEXT NOT NULL,
  hook_event_type TEXT NOT NULL,  -- PreToolUse, PostToolUse, SubagentStop, Stop
  timestamp INTEGER NOT NULL,     -- Unix timestamp in milliseconds
  model_name TEXT,
  payload TEXT NOT NULL,          -- JSON string
  chat TEXT,                      -- Optional full transcript (JSON array)
  summary TEXT                    -- Optional AI-generated summary
);

CREATE INDEX idx_session ON events(session_id);
CREATE INDEX idx_source_app ON events(source_app);
CREATE INDEX idx_event_type ON events(hook_event_type);
CREATE INDEX idx_timestamp ON events(timestamp);
```

### 3.2 Event Query Strategy

#### **Real-Time Processing** (observe_to_graphiti.py)
Query new events since last processing:

```python
SELECT *
FROM events
WHERE timestamp > :last_processed_timestamp
ORDER BY timestamp ASC
LIMIT 100
```

Track cursor in a state file: `.claude/logs/observe_graphiti_cursor.json`
```json
{
  "last_processed_timestamp": 1731689123456,
  "last_processed_event_id": 12345
}
```

#### **Batch Processing** (existing log_to_graphiti.py)
Process all events for a completed session:

```python
SELECT *
FROM events
WHERE session_id = :session_id
  AND hook_event_type = 'Stop'
ORDER BY timestamp ASC
```

### 3.3 Event Transformation Logic

#### **Stop Event → AgentSession Node**

```python
def transform_stop_event(event: dict) -> dict:
    """Transform Stop hook event into AgentSession node properties."""
    payload = event['payload']

    # Extract transcript for entity extraction
    transcript_path = payload.get('transcript_path')

    return {
        'session_id': event['session_id'],
        'source_app': event['source_app'],
        'agent_id': f"{event['source_app']}:{event['session_id'][:8]}",
        'start_time': get_session_start_time(event['session_id']),  # Query earliest event
        'end_time': datetime.fromtimestamp(event['timestamp'] / 1000),
        'status': 'completed',
        'model_name': event.get('model_name', ''),
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
```

#### **PreToolUse + PostToolUse → ToolInvocation Node**

```python
def transform_tool_events(pre_event: dict, post_event: dict) -> dict:
    """Match PreToolUse and PostToolUse events to create ToolInvocation."""
    pre_payload = pre_event['payload']
    post_payload = post_event['payload']

    tool_call_id = f"{pre_event['session_id']}-{pre_payload['tool_name']}-{pre_event['timestamp']}"

    latency_ms = post_event['timestamp'] - pre_event['timestamp']

    return {
        'tool_call_id': tool_call_id,
        'session_id': pre_event['session_id'],
        'tool_name': pre_payload['tool_name'],
        'start_time': datetime.fromtimestamp(pre_event['timestamp'] / 1000),
        'end_time': datetime.fromtimestamp(post_event['timestamp'] / 1000),
        'latency_ms': latency_ms,
        'status': 'success',  # TODO: detect errors from post_payload
        'input_summary': json.dumps(pre_payload.get('tool_input', {}))[:500],
        'output_summary': str(post_payload.get('result', ''))[:500],
        'sequence_number': get_next_sequence_number(pre_event['session_id']),
        'created_at': datetime.now()
    }
```

#### **SubagentStop → SubagentExecution Node**

```python
def transform_subagent_stop_event(event: dict) -> dict:
    """Transform SubagentStop event into SubagentExecution node."""
    payload = event['payload']

    return {
        'subagent_session_id': event['session_id'],
        'parent_session_id': get_parent_session_id(event['session_id']),  # From context
        'start_time': get_session_start_time(event['session_id']),
        'end_time': datetime.fromtimestamp(event['timestamp'] / 1000),
        'purpose': extract_subagent_purpose(payload),  # From transcript
        'outcome': extract_subagent_outcome(payload),
        'depth_level': calculate_depth(event['session_id']),
        'created_at': datetime.now()
    }
```

### 3.4 Batching Strategy

#### **Real-Time Mode** (for live dashboards)
- Process events every 5 seconds
- Batch up to 50 events per transaction
- Use Cypher UNWIND for bulk inserts

```python
# Pseudo-code
async def process_realtime_events():
    while True:
        events = fetch_new_events(limit=50)
        if events:
            transformed = [transform_event(e) for e in events]
            await batch_insert_to_neo4j(transformed)
            update_cursor(events[-1]['timestamp'])
        await asyncio.sleep(5)
```

#### **Batch Mode** (for historical processing)
- Trigger on session completion (Stop event)
- Process entire session in one transaction
- Run existing log_to_graphiti.py logic

### 3.5 Conflict Resolution

**Duplicate Event Detection**:
```cypher
MERGE (s:AgentSession {session_id: $session_id})
ON CREATE SET s += $properties, s.created_at = datetime()
ON MATCH SET s += $properties, s.updated_at = datetime()
```

**Tool Event Ordering**:
- Use sequence_number for deterministic ordering
- Create NEXT_TOOL relationships during insert
- Detect missing PostToolUse events (timeout after 5 minutes)

---

## 4. Agent Progress Tracking Metrics

### 4.1 Session Timeline Calculation

```cypher
// Calculate session duration and tool statistics
MATCH (s:AgentSession {session_id: $session_id})
OPTIONAL MATCH (s)-[:INVOKED_TOOL]->(t:ToolInvocation)
RETURN
  s.session_id AS session_id,
  s.start_time AS start,
  s.end_time AS end,
  duration.between(s.start_time, s.end_time).milliseconds AS duration_ms,
  count(t) AS total_tools,
  avg(t.latency_ms) AS avg_tool_latency_ms,
  collect(DISTINCT t.tool_name) AS tools_used
```

### 4.2 Tool Count and Average Latency

```cypher
// Tool usage breakdown
MATCH (s:AgentSession)-[:INVOKED_TOOL]->(t:ToolInvocation)
WHERE s.session_id = $session_id
RETURN
  t.tool_name AS tool,
  count(*) AS invocation_count,
  avg(t.latency_ms) AS avg_latency,
  min(t.latency_ms) AS min_latency,
  max(t.latency_ms) AS max_latency,
  sum(CASE WHEN t.status = 'error' THEN 1 ELSE 0 END) AS error_count
ORDER BY invocation_count DESC
```

### 4.3 Entity Discovery Rate

```cypher
// Entities discovered per session
MATCH (s:AgentSession)-[:DISCOVERED_ENTITY]->(e:Entity)
WHERE s.session_id = $session_id
WITH s, count(e) AS entity_count, collect(e.name) AS entities
MATCH (s)-[:INVOKED_TOOL]->(t:ToolInvocation)
WITH s, entity_count, entities, count(t) AS tool_count
RETURN
  s.session_id,
  entity_count,
  tool_count,
  toFloat(entity_count) / tool_count AS entities_per_tool,
  entities[..10] AS sample_entities  // First 10 entities
```

### 4.4 Subagent Hierarchy Depth

```cypher
// Calculate max nesting depth
MATCH path = (root:AgentSession)-[:SPAWNED_SUBAGENT*]->(leaf:AgentSession)
WHERE root.parent_session_id IS NULL
  AND NOT (leaf)-[:SPAWNED_SUBAGENT]->()
RETURN
  root.session_id AS root_session,
  length(path) AS max_depth,
  [node IN nodes(path) | node.session_id] AS hierarchy_chain
ORDER BY max_depth DESC
LIMIT 1
```

### 4.5 Performance Baselines

**Define percentile thresholds per tool**:

```cypher
// Calculate P50, P90, P99 latencies for each tool
MATCH (t:ToolInvocation)
WHERE t.start_time > datetime() - duration('P7D')  // Last 7 days
WITH t.tool_name AS tool, collect(t.latency_ms) AS latencies
RETURN
  tool,
  apoc.coll.percentile(latencies, 0.5) AS p50_latency,
  apoc.coll.percentile(latencies, 0.9) AS p90_latency,
  apoc.coll.percentile(latencies, 0.99) AS p99_latency
```

Store these as baseline metrics for anomaly detection.

---

## 5. Obsidian Export Specification

### 5.1 Note Structure

#### **Daily Summary Template**
Path: `~/obsidian/consulting-co/daily/2025-11-15.md`

```markdown
---
date: 2025-11-15
tags:
  - daily-summary
  - graphiti
  - agent-sessions
total_sessions: 5
total_tools: 127
total_entities: 23
---

# Daily Summary - November 15, 2025

## Sessions Overview

| Session ID | Source App | Duration | Tools | Entities | Status |
|-----------|-----------|----------|-------|----------|--------|
| [[abc12345]] | consulting-co | 12m 34s | 45 | 8 | ✅ Completed |
| [[def67890]] | consulting-co | 3m 12s | 12 | 3 | ✅ Completed |
| [[ghi11213]] | quickstart-nexus | 8m 45s | 34 | 7 | ❌ Failed |

## Entity Discovery

### New Entities (23 total)
- [[log_to_graphiti.py]] - file (mentioned in abc12345, def67890)
- [[Neo4j Schema Design]] - concept (mentioned in abc12345)
- [[Graphiti]] - technology (mentioned in abc12345, def67890, ghi11213)

### Top Referenced Entities
1. [[Graphiti]] - 3 sessions
2. [[log_to_graphiti.py]] - 2 sessions

## Performance Metrics

- **Average Session Duration**: 8m 10s
- **Average Tool Latency**: 234ms
- **Most Used Tool**: Read (34 invocations)
- **Slowest Tool**: Bash (avg 1,234ms)

## Notable Events

- ⚠️ Session ghi11213 failed after 8m 45s (tool error on Bash invocation)
- 🎯 Peak entity discovery in abc12345 (8 entities from 45 tools)

## Graph Insights

```cypher
// Top tools by usage today
MATCH (s:AgentSession)-[:INVOKED_TOOL]->(t:ToolInvocation)
WHERE date(s.start_time) = date('2025-11-15')
RETURN t.tool_name, count(*) AS uses
ORDER BY uses DESC LIMIT 5
```

---
Generated by observe_to_obsidian.py | Last updated: 2025-11-15 23:59:00
```

#### **Session Report Template**
Path: `~/obsidian/consulting-co/sessions/consulting-co_abc12345.md`

```markdown
---
session_id: abc12345678901234567890123456789
agent_id: consulting-co:abc12345
source_app: consulting-co
start_time: 2025-11-15T14:30:22Z
end_time: 2025-11-15T14:42:56Z
duration: 12m 34s
status: completed
model_name: claude-sonnet-4-5-20250929
tags:
  - agent-session
  - consulting-co
---

# Session: consulting-co:abc12345

**Duration**: 12m 34s
**Status**: ✅ Completed
**Model**: claude-sonnet-4-5-20250929
**Start**: 2025-11-15 14:30:22
**End**: 2025-11-15 14:42:56

## Overview

This session involved creating a planning architecture document for integrating the Observability system with Graphiti knowledge graph.

## Tool Invocations (45 total)

| # | Tool | Latency | Status | Summary |
|---|------|---------|--------|---------|
| 1 | Glob | 123ms | ✅ | Search for `**/.claude/hooks/**/*.py` |
| 2 | Read | 234ms | ✅ | Read log_to_graphiti.py |
| 3 | Read | 189ms | ✅ | Read stop.py |
| ... | ... | ... | ... | ... |
| 45 | Write | 456ms | ✅ | Create PLANNING_ARCHITECTURE.md |

**Average Latency**: 234ms
**Total Tool Time**: 10.53s (14% of session duration)

## Entities Discovered (8)

- [[log_to_graphiti.py]] (file)
- [[Neo4j Schema Design]] (concept)
- [[Graphiti]] (technology)
- [[AgentSession]] (concept)
- [[ToolInvocation]] (concept)
- [[SQLite]] (technology)
- [[Obsidian]] (technology)
- [[PLANNING_ARCHITECTURE.md]] (file)

## Subagents

No subagents spawned in this session.

## Performance Analysis

- **Tool Distribution**:
  - Read: 18 invocations (40%)
  - Glob: 12 invocations (27%)
  - Write: 1 invocation (2%)
  - Other: 14 invocations (31%)

- **Latency Breakdown**:
  - P50: 210ms
  - P90: 450ms
  - P99: 890ms

## Knowledge Graph Links

```cypher
MATCH (s:AgentSession {session_id: "abc12345678901234567890123456789"})
OPTIONAL MATCH (s)-[:INVOKED_TOOL]->(t:ToolInvocation)
OPTIONAL MATCH (s)-[:DISCOVERED_ENTITY]->(e:Entity)
RETURN s, collect(t)[..5] AS sample_tools, collect(e) AS entities
```

---
Back to [[2025-11-15]] | Generated by observe_to_obsidian.py
```

#### **Entity Map Template**
Path: `~/obsidian/consulting-co/entities/log_to_graphiti_py.md`

```markdown
---
entity_name: log_to_graphiti.py
entity_type: file
first_seen: 2025-11-10T12:00:00Z
mention_count: 15
tags:
  - entity
  - file
  - graphiti
---

# Entity: log_to_graphiti.py

**Type**: file
**First Seen**: 2025-11-10
**Mentions**: 15 sessions

## Description

Hook script that logs Claude Code conversations to Graphiti knowledge graph using Claude subagent for entity extraction.

## Sessions Mentioning This Entity

- [[consulting-co_abc12345]] (2025-11-15) - Created planning architecture
- [[consulting-co_def67890]] (2025-11-15) - Reviewed existing hooks
- [[quickstart-nexus_ghi11213]] (2025-11-14) - Investigated Neo4j schema

## Related Entities

- [[Graphiti]] - Technology used by this file
- [[Neo4j]] - Database backend
- [[Claude Code Subagent]] - Used for entity extraction

## Code References

```python
# Key function
async def store_in_graphiti(session_id: str, episode_text: str):
    graphiti = Graphiti(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)
    await graphiti.add_episode(name=episode_name, episode_body=episode_text, ...)
```

---
Generated by observe_to_obsidian.py
```

### 5.2 Export Scheduling

#### **Per-Session Export** (triggered by Stop event)
```python
# In observe_to_graphiti.py
async def on_stop_event(event: dict):
    # 1. Transform to Neo4j
    await store_session_in_neo4j(event)

    # 2. Generate session report
    await export_session_to_obsidian(event['session_id'])
```

#### **Hourly Aggregation** (cron job)
```bash
# Crontab entry
0 * * * * cd ~/.claude && python hooks/observe_to_obsidian.py --mode hourly
```

Updates daily summary with latest session data.

#### **Daily Summary** (midnight cron)
```bash
# Crontab entry
0 0 * * * cd ~/.claude && python hooks/observe_to_obsidian.py --mode daily
```

Generates complete daily summary from Neo4j queries.

### 5.3 Backlink Generation

**Session → Daily Summary**:
```markdown
Back to [[2025-11-15]]
```

**Session → Entities**:
```markdown
## Entities Discovered
- [[log_to_graphiti.py]] (file)
- [[Graphiti]] (technology)
```

**Entity → Sessions**:
```markdown
## Sessions Mentioning This Entity
- [[consulting-co_abc12345]] (2025-11-15)
```

**Daily Summary → Sessions**:
```markdown
| Session ID | Source App | ...
| [[abc12345]] | consulting-co | ...
```

### 5.4 Template Patterns

**Frontmatter Standards**:
```yaml
---
date: YYYY-MM-DD          # For daily summaries
session_id: String        # Full session ID
agent_id: String          # Display format (source_app:session_id_short)
source_app: String
entity_name: String       # For entity notes
entity_type: String       # file|function|concept|technology|pattern
tags:
  - agent-session         # Or daily-summary, entity
  - source_app_name
---
```

**Section Order**:
1. Frontmatter
2. Title (H1)
3. Metadata table
4. Overview/Summary
5. Main content (sessions/tools/entities)
6. Performance metrics
7. Knowledge graph queries
8. Footer with backlinks and generation info

---

## 6. Integration Points

### 6.1 observe_to_graphiti.py Hook Integration

**Location**: `C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\hooks\observe_to_graphiti.py`

**Trigger Mechanism**:
- Register as a Stop hook (runs after each agent response)
- Also watch for SubagentStop events
- Poll SQLite events.db for new events (alternative to hook-based)

**Integration with log_to_graphiti.py**:
```python
# observe_to_graphiti.py imports existing logic
from log_to_graphiti import (
    extract_entities_with_claude_subagent,
    format_episode_with_entities,
    store_in_graphiti
)

# Extends with structured telemetry
async def process_stop_event(event: dict):
    # 1. Call existing Graphiti episode creation
    await call_existing_log_to_graphiti(event)

    # 2. Add structured session/tool nodes
    await store_session_nodes(event)

    # 3. Export to Obsidian
    await export_to_obsidian(event)
```

**Backwards Compatibility**:
- log_to_graphiti.py continues to work standalone
- observe_to_graphiti.py is optional enhancement
- Both can run simultaneously (use MERGE to avoid duplicates)

### 6.2 Environment Variables

```bash
# .env file
# Neo4j connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# Project identification
PROJECT_NAME=consulting-co
SOURCE_APP=consulting-co

# Observability database
OBSERVABILITY_DB_PATH=./observability/backend/events.db

# Obsidian vault
OBSIDIAN_VAULT_PATH=~/obsidian/consulting-co

# Processing mode
OBSERVE_MODE=realtime  # or "batch"
OBSERVE_INTERVAL_SECONDS=5

# Feature flags
ENABLE_OBSIDIAN_EXPORT=true
ENABLE_PROGRESS_METRICS=true
ENABLE_ENTITY_EXTRACTION=true
```

### 6.3 Configuration File Structure

**Location**: `.claude/observe_config.yaml`

```yaml
# Observability to Graphiti configuration
neo4j:
  uri: ${NEO4J_URI}
  user: ${NEO4J_USER}
  password: ${NEO4J_PASSWORD}
  database: neo4j

observability:
  db_path: ${OBSERVABILITY_DB_PATH}
  poll_interval_seconds: 5
  batch_size: 50

processing:
  mode: realtime  # realtime | batch
  enable_obsidian_export: true
  enable_progress_metrics: true
  enable_entity_extraction: true

obsidian:
  vault_path: ${OBSIDIAN_VAULT_PATH}
  daily_notes_path: daily
  session_notes_path: sessions
  entity_notes_path: entities
  export_schedule:
    per_session: true
    hourly: true
    daily: true

metrics:
  tool_latency_percentiles: [0.5, 0.9, 0.99]
  baseline_window_days: 7
  anomaly_detection: true

entity_extraction:
  max_entities_per_session: 50
  entity_types:
    - file
    - function
    - concept
    - technology
    - pattern
```

### 6.4 Error Handling and Recovery

**SQLite Connection Errors**:
```python
try:
    events = fetch_new_events()
except sqlite3.OperationalError as e:
    logger.error(f"SQLite error: {e}")
    # Wait and retry with exponential backoff
    await asyncio.sleep(min(retry_count * 2, 30))
```

**Neo4j Connection Errors**:
```python
try:
    await store_in_neo4j(data)
except neo4j.exceptions.ServiceUnavailable:
    logger.error("Neo4j unavailable, queuing for retry")
    # Store in local JSON file for later replay
    queue_for_retry(data)
```

**Partial Event Processing**:
```python
# Track last successfully processed event
cursor = load_cursor()
try:
    for event in events:
        await process_event(event)
        save_cursor(event['timestamp'])  # Checkpoint after each event
except Exception as e:
    logger.error(f"Failed to process event {event['id']}: {e}")
    # Next run will resume from last successful cursor
```

**Obsidian Export Failures**:
```python
try:
    export_to_obsidian(session_data)
except IOError as e:
    logger.warning(f"Obsidian export failed: {e}")
    # Continue processing (Obsidian export is non-critical)
    # Store in export_queue.json for manual retry
```

---

## 7. Implementation Priority & Dependencies

### Phase 1: Core Bridge (observe_to_graphiti.py)
**Duration**: 2-3 days
**Priority**: P0 (Highest)

**Deliverables**:
1. ✅ SQLite event polling mechanism
2. ✅ Event transformation logic (Stop → AgentSession, PreToolUse+PostToolUse → ToolInvocation)
3. ✅ Neo4j schema creation (nodes, relationships, constraints, indexes)
4. ✅ Integration with existing log_to_graphiti.py
5. ✅ Basic error handling and cursor tracking

**Dependencies**:
- Neo4j running at bolt://localhost:7687
- Observability backend SQLite database
- Graphiti library installed (`graphiti-core`)

**Testing**:
```bash
# Run a test agent session
claude -p "List files in current directory"

# Verify events in SQLite
sqlite3 observability/backend/events.db "SELECT * FROM events ORDER BY timestamp DESC LIMIT 10;"

# Verify Neo4j nodes
cypher-shell "MATCH (s:AgentSession) RETURN s LIMIT 5;"

# Test observe_to_graphiti.py
python .claude/hooks/observe_to_graphiti.py --mode batch --session-id abc12345
```

### Phase 2: Progress Tracker
**Duration**: 1-2 days
**Priority**: P1

**Deliverables**:
1. ✅ Progress metrics calculation functions
2. ✅ Neo4j queries for timeline, tool stats, entity discovery
3. ✅ Subagent hierarchy analysis
4. ✅ Performance baseline calculator (P50/P90/P99)

**Dependencies**:
- Phase 1 complete (AgentSession and ToolInvocation nodes exist)
- APOC plugin installed in Neo4j (`apoc.coll.percentile`)

**Testing**:
```cypher
// Test session timeline
MATCH (s:AgentSession {session_id: "abc12345"})
OPTIONAL MATCH (s)-[:INVOKED_TOOL]->(t:ToolInvocation)
RETURN s.session_id, count(t), avg(t.latency_ms);

// Test tool breakdown
MATCH (t:ToolInvocation)
RETURN t.tool_name, count(*), avg(t.latency_ms)
ORDER BY count(*) DESC;
```

### Phase 3: Obsidian Exporter
**Duration**: 2-3 days
**Priority**: P1

**Deliverables**:
1. ✅ Session report generator
2. ✅ Daily summary generator
3. ✅ Entity map generator
4. ✅ Backlink creation logic
5. ✅ Export scheduling (per-session, hourly, daily)

**Dependencies**:
- Phase 1 & 2 complete
- Obsidian vault path configured

**Testing**:
```bash
# Test session export
python .claude/hooks/observe_to_obsidian.py --mode session --session-id abc12345

# Verify Obsidian note created
cat ~/obsidian/consulting-co/sessions/consulting-co_abc12345.md

# Test daily summary
python .claude/hooks/observe_to_obsidian.py --mode daily --date 2025-11-15

# Verify backlinks work in Obsidian
```

### Phase 4: Dashboard Enhancements
**Duration**: 3-4 days
**Priority**: P2

**Deliverables**:
1. ✅ Web dashboard with real-time session list
2. ✅ Session detail view with tool timeline
3. ✅ Entity graph visualization
4. ✅ Performance metrics dashboard
5. ✅ Anomaly detection alerts

**Dependencies**:
- Phase 1-3 complete
- Frontend framework (React or similar)

**Testing**:
```bash
# Start dashboard
cd observability/backend
bun run dev

# Access at http://localhost:4000
# Verify real-time updates as events arrive
```

---

## 8. Migration Path

### 8.1 For Existing log_to_graphiti.py Users

**Step 1**: Install observe_to_graphiti.py alongside existing hook
```bash
# Copy new hook
cp templates/observe_to_graphiti.py .claude/hooks/

# Update .env with new variables
echo "OBSERVABILITY_DB_PATH=./observability/backend/events.db" >> .env
echo "ENABLE_OBSIDIAN_EXPORT=true" >> .env
```

**Step 2**: Run both hooks in parallel (no conflicts)
```bash
# .claude/hooks/stop.py will call both
# log_to_graphiti.py creates episodes
# observe_to_graphiti.py adds session/tool nodes
```

**Step 3**: Verify dual processing
```cypher
// Should see both Episode nodes (Graphiti) and AgentSession nodes (new)
MATCH (ep:Episode)-[:MENTIONS_ENTITY]->(e:Entity)
RETURN ep, e LIMIT 5;

MATCH (s:AgentSession)-[:DISCOVERED_ENTITY]->(e:Entity)
RETURN s, e LIMIT 5;
```

**Step 4**: Eventually migrate to observe_to_graphiti.py only
```bash
# Disable log_to_graphiti.py if desired
# observe_to_graphiti.py calls its functions internally
```

### 8.2 Backfilling Historical Data

```bash
# Backfill all sessions from SQLite
python .claude/hooks/observe_to_graphiti.py --mode backfill --start-date 2025-11-01

# Or backfill specific session
python .claude/hooks/observe_to_graphiti.py --mode backfill --session-id abc12345
```

---

## 9. Sample Queries

### 9.1 Most Active Sessions This Week

```cypher
MATCH (s:AgentSession)
WHERE s.start_time > datetime() - duration('P7D')
OPTIONAL MATCH (s)-[:INVOKED_TOOL]->(t:ToolInvocation)
RETURN
  s.agent_id,
  s.source_app,
  s.start_time,
  count(t) AS tool_count,
  duration.between(s.start_time, s.end_time).seconds AS duration_seconds
ORDER BY tool_count DESC
LIMIT 10
```

### 9.2 Slowest Tool Invocations

```cypher
MATCH (t:ToolInvocation)
WHERE t.latency_ms > 1000  // Slower than 1 second
RETURN
  t.tool_name,
  t.latency_ms,
  t.session_id,
  t.start_time,
  substring(t.input_summary, 0, 100) AS input_preview
ORDER BY t.latency_ms DESC
LIMIT 20
```

### 9.3 Entity Co-occurrence Graph

```cypher
// Find entities that appear together in sessions
MATCH (s:AgentSession)-[:DISCOVERED_ENTITY]->(e1:Entity)
MATCH (s)-[:DISCOVERED_ENTITY]->(e2:Entity)
WHERE e1 <> e2
WITH e1, e2, count(s) AS co_occurrences
WHERE co_occurrences > 2
RETURN e1.name, e2.name, co_occurrences
ORDER BY co_occurrences DESC
LIMIT 50
```

### 9.4 Subagent Dependency Tree

```cypher
// Visualize full subagent hierarchy
MATCH path = (root:AgentSession)-[:SPAWNED_SUBAGENT*]->(leaf:AgentSession)
WHERE root.parent_session_id IS NULL
RETURN path
ORDER BY length(path) DESC
LIMIT 10
```

### 9.5 Daily Tool Usage Trends

```cypher
// Tool usage over time
MATCH (t:ToolInvocation)
WHERE t.start_time > datetime() - duration('P30D')
WITH date(t.start_time) AS day, t.tool_name AS tool, count(*) AS uses
RETURN day, tool, uses
ORDER BY day DESC, uses DESC
```

---

## 10. Performance Considerations

### 10.1 Index Strategy

All indexes defined in Section 2.3. Additional composite indexes:

```cypher
CREATE INDEX session_time_idx FOR (s:AgentSession) ON (s.start_time);
CREATE INDEX tool_time_idx FOR (t:ToolInvocation) ON (t.start_time);
CREATE INDEX entity_first_seen_idx FOR (e:Entity) ON (e.first_seen);
```

### 10.2 Query Optimization

- Use `LIMIT` on all queries
- Add `USING INDEX` hints for large datasets
- Batch inserts with `UNWIND` (50-100 rows per transaction)
- Use `apoc.periodic.iterate` for bulk operations

### 10.3 Data Retention

**Auto-cleanup Policy**:
```cypher
// Delete sessions older than 90 days
MATCH (s:AgentSession)
WHERE s.start_time < datetime() - duration('P90D')
DETACH DELETE s
```

**Archive to JSON**:
```bash
# Monthly archival script
python .claude/hooks/archive_old_sessions.py --before 2025-10-01 --output archive/2025-10.json
```

---

## 11. Security Considerations

### 11.1 Sensitive Data Handling

- **Tool inputs/outputs**: Truncate to 500 chars (prevents secret leakage)
- **Transcript storage**: Optional (use `--add-chat` flag sparingly)
- **Neo4j credentials**: Store in `.env`, never commit to git

### 11.2 Access Control

```cypher
// Create read-only user for dashboard
CREATE USER dashboard SET PASSWORD 'dashboard_password';
GRANT MATCH {*} ON GRAPH neo4j TO dashboard;
DENY WRITE ON GRAPH neo4j TO dashboard;
```

---

## 12. Monitoring and Alerting

### 12.1 Health Checks

```python
# In observe_to_graphiti.py
async def health_check():
    # 1. SQLite readable
    assert sqlite_connection.execute("SELECT 1").fetchone()

    # 2. Neo4j reachable
    assert neo4j_driver.verify_connectivity()

    # 3. Cursor file writable
    save_cursor(int(time.time() * 1000))

    # 4. Last processed event < 5 minutes old
    cursor = load_cursor()
    age_seconds = (time.time() * 1000 - cursor['last_processed_timestamp']) / 1000
    assert age_seconds < 300, f"Processing lag: {age_seconds}s"
```

### 12.2 Alerting Triggers

- Processing lag > 5 minutes
- Neo4j connection failure > 3 retries
- Tool latency > P99 baseline (anomaly detection)
- Session duration > 30 minutes (potential hang)

---

## Summary

This architecture provides a comprehensive blueprint for integrating Observability events with Graphiti knowledge graph and Obsidian vault. The key innovations are:

1. **Structured Telemetry**: Extends Graphiti's entity extraction with agent session tracking, tool invocations, and subagent hierarchies
2. **Real-time Processing**: Polls SQLite events.db and transforms to Neo4j in near-real-time
3. **Backwards Compatible**: Works alongside existing log_to_graphiti.py hook
4. **Obsidian Integration**: Auto-generates daily summaries, session reports, and entity maps
5. **Performance Analytics**: Calculates tool latencies, entity discovery rates, and subagent depths

**Next Steps**:
1. Implement Phase 1 (core bridge)
2. Test with sample agent sessions
3. Iterate on Neo4j schema based on query patterns
4. Implement Phase 2-3 (metrics & Obsidian export)
5. Deploy Phase 4 (dashboard) for visualization

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Author**: Planning Subagent
**Status**: Draft for Review
