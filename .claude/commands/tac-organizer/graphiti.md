---
description: Manage Graphiti knowledge graph MCP server - start, stop, troubleshoot
argument: command (start|stop|status|logs|troubleshoot|process-queue|search|report)
---

# Graphiti Command

Manage the Graphiti MCP server for persistent AI memory.

## Usage

- `/graphiti` or `/graphiti status` - Check server status
- `/graphiti start` - Start the server
- `/graphiti stop` - Stop the server
- `/graphiti logs` - View recent logs
- `/graphiti troubleshoot` - Run full diagnostics
- `/graphiti process-queue` - Process pending queue items from stop hook
- `/graphiti search <query>` - Search the knowledge graph
- `/graphiti report` - Generate aggregate report of knowledge graph

## Instructions

Based on the argument provided, execute the appropriate action:

### No argument or "status"
Run the status check:
```bash
uv run .claude/skills/graphiti/scripts/graphiti_server.py status
```

### "start"
Start the Graphiti MCP server:
```bash
uv run .claude/skills/graphiti/scripts/graphiti_server.py start
```

After starting, remind the user to restart Claude Code to connect to the MCP server.

### "stop"
Stop the Graphiti MCP server:
```bash
uv run .claude/skills/graphiti/scripts/graphiti_server.py stop
```

### "logs"
Show recent server logs:
```bash
uv run .claude/skills/graphiti/scripts/graphiti_server.py logs
```

### "troubleshoot"
Run comprehensive diagnostics:
```bash
uv run .claude/skills/graphiti/scripts/troubleshoot.py
```

### "process-queue"
Process pending items from the stop hook queue:

1. First, list the queue files:
```bash
ls -la logs/graphiti_queue/
```

2. For each `.json` file in the queue:
   - Read the file to get the payload
   - Extract the `params.arguments` from the payload
   - Call `mcp__graphiti__add_memory` with those arguments
   - Delete the file after successful ingestion

Example processing:
```python
# Read queue file
payload = json.load(open("logs/graphiti_queue/session_timestamp.json"))
args = payload["params"]["arguments"]

# Ingest via MCP
mcp__graphiti__add_memory(
    name=args["name"],
    episode_body=args["episode_body"],
    source=args["source"],
    source_description=args["source_description"],
    group_id=args["group_id"]
)

# Delete processed file
rm logs/graphiti_queue/session_timestamp.json
```

### "search <query>"
Search the knowledge graph for relevant information:

1. Search for nodes (entities):
```python
mcp__graphiti__search_nodes(query="<user's query>", max_nodes=10)
```

2. Search for facts (relationships):
```python
mcp__graphiti__search_memory_facts(query="<user's query>", max_facts=10)
```

3. Filter by project if needed:
```python
mcp__graphiti__search_nodes(
    query="<query>",
    group_ids=["claude-code-nci-oa-agent"],
    max_nodes=10
)
```

### "report"
Generate an aggregate report of the knowledge graph.

Since Graphiti uses MCP protocol, Claude must fetch the data first, then pass to the script:

1. Fetch data via MCP tools:
```python
# Get episodes
episodes_result = mcp__graphiti__get_episodes(
    group_ids=["claude-code-nci-oa-agent"],
    max_episodes=100
)

# Search nodes (use broad terms)
nodes_result = mcp__graphiti__search_nodes(
    query="hook queue process session memory",
    group_ids=["claude-code-nci-oa-agent"],
    max_nodes=50
)

# Search facts
facts_result = mcp__graphiti__search_memory_facts(
    query="hook queue process triggers creates",
    group_ids=["claude-code-nci-oa-agent"],
    max_facts=50
)
```

2. Combine and generate report:
```python
import json
data = {
    "group_id": "claude-code-nci-oa-agent",
    "episodes": episodes_result["result"]["episodes"],
    "nodes": nodes_result["result"]["nodes"],
    "facts": facts_result["result"]["facts"]
}
# Write to temp file and run script
with open("/tmp/graphiti_data.json", "w") as f:
    json.dump(data, f)
```

```bash
uv run .claude/skills/graphiti/scripts/generate_report.py --input /tmp/graphiti_data.json
```

The report includes:
- Episode count and timeline
- Session breakdown with turn counts
- Token usage statistics
- Tool usage patterns
- Entity catalog grouped by type
- Relationship/fact summary
- Active vs expired facts

## Server Details

- **Location**: `C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server/`
- **MCP Endpoint**: `http://localhost:8000/mcp/`
- **Health Check**: `http://localhost:8000/health`
- **FalkorDB UI**: `http://localhost:3000`

## Quick Troubleshooting

If the server won't start:
1. Ensure Docker Desktop is running
2. Check port 8000 and 6379 are available
3. Verify OPENAI_API_KEY is set in `.claude/settings.local.json`

If MCP connection fails:
1. Restart Claude Code after starting the server
2. Check `.mcp.json` has graphiti configured
3. Run `/graphiti troubleshoot` for full diagnostics
