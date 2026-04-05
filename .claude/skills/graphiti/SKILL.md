---
name: graphiti
description: Manage Graphiti knowledge graph MCP server for persistent AI memory. Start/stop server, troubleshoot issues, and interact with the knowledge graph.
---

# Graphiti Knowledge Graph

Graphiti MCP server for persistent, temporally-aware knowledge graph memory.

## Quick Reference

| Command | Description |
|---------|-------------|
| `/graphiti start` | Start the Graphiti MCP server |
| `/graphiti stop` | Stop the Graphiti MCP server |
| `/graphiti status` | Check server status and health |
| `/graphiti logs` | View server logs |
| `/graphiti troubleshoot` | Run diagnostics and fix common issues |
| `/graphiti process-queue` | Process pending items from stop hook queue |
| `/graphiti search <query>` | Search the knowledge graph |

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key configured in `.claude/settings.local.json`
- Port 8000 available for MCP server
- Port 6379 available for FalkorDB

## Server Location

```
C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server/
```

## Starting the Server

```bash
cd C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server
docker compose -f docker/docker-compose-falkordb.yml up -d
```

Note: Use `docker-compose-falkordb.yml` (separate containers) instead of `docker-compose.yml` (combined) for better Windows compatibility.

Or use the troubleshooting script:
```bash
uv run .claude/skills/graphiti/scripts/graphiti_server.py start
```

## Stopping the Server

```bash
cd C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server
docker compose -f docker/docker-compose-falkordb.yml down
```

## MCP Tools Available

When connected, these tools are available:

| Tool | Description |
|------|-------------|
| `add_episode` | Add text, JSON, or messages to knowledge graph |
| `search_nodes` | Search for entity summaries |
| `search_facts` | Search for relationships between entities |
| `delete_entity_edge` | Remove a relationship |
| `delete_episode` | Remove an episode |

## FalkorDB Browser Login

Access the graph visualization UI at http://localhost:3000

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `6379` |
| Username | (leave empty) |
| Password | (leave empty) |
| TLS | Off |

**Note**: Port 8000 is the MCP API, port 6379 is the FalkorDB database.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | Required |
| `GRAPHITI_GROUP_ID` | Namespace for graph data | `nci-oa-agent` |
| `SEMAPHORE_LIMIT` | Concurrent episode processing | `5` |
| `FALKORDB_URI` | FalkorDB connection | `redis://localhost:6379` |

### Config Files

- `.env`: `C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server/.env`
- `config.yaml`: `C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server/config/config.yaml`
- MCP config: `C:/Users/gblac/OneDrive/Desktop/afs/nci-oa-agent/.mcp.json`

## Troubleshooting

### Common Issues

#### Server Not Responding

1. Check if Docker containers are running:
   ```bash
   docker ps | grep graphiti
   ```

2. Check container logs:
   ```bash
   docker logs graphiti-mcp_server-graphiti-falkordb-1
   ```

3. Verify port availability:
   ```bash
   netstat -an | grep 8000
   netstat -an | grep 6379
   ```

#### MCP Connection Failed

1. Ensure server is running at `http://localhost:8000/mcp/`
2. Test endpoint manually:
   ```bash
   curl http://localhost:8000/health
   ```

3. Restart Claude Code to reconnect MCP

#### Rate Limit Errors (429)

Reduce `SEMAPHORE_LIMIT` in `.env`:
- OpenAI Tier 1: Use `1-2`
- OpenAI Tier 2-3: Use `5-10`
- Anthropic: Use `5-8`

#### FalkorDB Connection Issues

1. Check Redis is running:
   ```bash
   docker exec -it graphiti-mcp_server-graphiti-falkordb-1 redis-cli ping
   ```

2. Restart containers:
   ```bash
   docker compose -f docker/docker-compose-falkordb.yml restart
   ```

### Diagnostic Scripts

Run full diagnostics:
```bash
uv run .claude/skills/graphiti/scripts/troubleshoot.py
```

Check specific components:
```bash
uv run .claude/skills/graphiti/scripts/check_docker.py
uv run .claude/skills/graphiti/scripts/check_mcp.py
uv run .claude/skills/graphiti/scripts/check_falkordb.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MCP Client (mcp-remote)                               │ │
│  └──────────────────────┬─────────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Docker Container (zepai/knowledge-graph-mcp)               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Graphiti MCP Server (:8000/mcp/)                      │ │
│  │    - add_episode, search_nodes, search_facts           │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐ │
│  │  FalkorDB (Redis-based Graph DB) (:6379)               │ │
│  │    - Stores entities, relationships, episodes          │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐ │
│  │  OpenAI API                                            │ │
│  │    - Entity extraction (gpt-4o-mini)                   │ │
│  │    - Embeddings (text-embedding-3-small)               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Automatic Memory Ingestion

The stop hook automatically queues conversation turns for Graphiti ingestion.

### How It Works

```
User ends turn → Stop hook fires → Turn queued to logs/graphiti_queue/
Next session → SessionStart detects queue → Claude processes via MCP
```

### Queue Location

```
logs/graphiti_queue/
├── {session_id}_{timestamp}.json
└── ...
```

### Processing the Queue

**Automatic**: SessionStart hook injects context telling Claude to process pending items.

**Manual**: Run the queue processor script:
```bash
uv run .claude/skills/graphiti/scripts/process_queue.py
```

Then for each item, call:
```python
mcp__graphiti__add_memory(
    name="...",
    episode_body="...",
    source="json",
    source_description="Claude Code transcript turn",
    group_id="claude-code-{project}"
)
```

### Episode Format

Each queued turn contains:
```json
{
  "timestamp": "2026-01-23T...",
  "session_id": "uuid",
  "project": "nci-oa-agent",
  "user_message": "the user's prompt",
  "assistant_response": "Claude's response",
  "tools_used": ["Bash", "Read", "Edit"],
  "model": "claude-opus-4-5-20251101",
  "token_usage": {...},
  "user": "gblac"
}
```

### Group IDs

Episodes are grouped by project:
- `claude-code-nci-oa-agent`
- `claude-code-consulting-co`
- `claude-code-quickstart-nexus`
- etc.

## Source Files

```
.claude/skills/graphiti/
├── SKILL.md                    # This file
└── scripts/
    ├── graphiti_server.py      # Start/stop/status commands
    ├── process_queue.py        # Queue processor for stop hook
    ├── generate_report.py      # Aggregate report generator
    ├── troubleshoot.py         # Full diagnostics
    ├── check_docker.py         # Docker health check
    ├── check_mcp.py            # MCP endpoint check
    └── check_falkordb.py       # FalkorDB connection check
```

## Report Generation

Generate an aggregate report of the knowledge graph:

```bash
uv run .claude/skills/graphiti/scripts/generate_report.py
```

### Options

| Flag | Description |
|------|-------------|
| `--group-id <id>` | Report on specific group (default: claude-code-nci-oa-agent) |
| `--output <file>` | Save to file instead of stdout |
| `--json` | Output raw JSON data instead of markdown |

### Report Contents

- **Summary**: Episode, entity, and fact counts
- **Episodes**: Session breakdown, token usage, tool usage, recent turns
- **Entities**: Catalog grouped by type (Procedure, Topic, Organization, etc.)
- **Facts**: Relationship types, active vs expired, sample facts

## Related Hooks

| Hook | File | Purpose |
|------|------|---------|
| Stop | `.claude/hooks/stop.py` | Queues turns after each response |
| SessionStart | `.claude/hooks/session_start.py` | Checks queue, notifies Claude |
| Utils | `.claude/hooks/utils/graphiti_ingest.py` | Turn extraction and queuing |
| Utils | `.claude/hooks/utils/graphiti.py` | Server health check |
