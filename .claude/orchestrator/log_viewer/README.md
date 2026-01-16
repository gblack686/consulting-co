# Log Viewer - Unified Orchestrator Log Browser

A FastAPI-based log viewer that queries all three orchestrator log tables and provides a unified view with filtering and search capabilities.

## Quick Start

```bash
# Navigate to log_viewer directory
cd .claude/orchestrator/log_viewer

# Install dependencies (if not already installed)
pip install fastapi uvicorn psycopg2-binary python-dotenv jinja2

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 5998

# Open in browser
http://localhost:5998
```

## What Logs Are Available

The log viewer queries three database tables and presents them in a unified view:

### Source: `agent_logs` (Cyan)
- **Hook Events**: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact
- **Response Blocks**: TextBlock, ThinkingBlock, ToolUseBlock
- **Fields**: agent_id, session_id, task_slug, event_type, event_category, content, payload

### Source: `system_logs` (Purple)
- **Orchestrator Thinking**: Reasoning and planning blocks
- **Orchestrator Tool Use**: Tool invocations by the orchestrator
- **Fields**: level (DEBUG/INFO/WARNING/ERROR), message, metadata

### Source: `orchestrator_chat` (Green)
- **User → Orchestrator**: User prompts and requests
- **Orchestrator → User**: Orchestrator responses
- **Orchestrator → Agent**: Task delegations
- **Agent → Orchestrator**: Task completions and reports
- **Fields**: sender_type, receiver_type, message, agent_id, metadata

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATOR LOGGING FLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER PROMPT                                                                │
│      │                                                                      │
│      ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ orchestrator_chat (sender=user, receiver=orchestrator)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│      │                                                                      │
│      ▼                                                                      │
│  ORCHESTRATOR PROCESSING                                                    │
│      │                                                                      │
│      ├──► ThinkingBlock ──► system_logs (metadata.type="thinking_block")   │
│      │                                                                      │
│      ├──► ToolUseBlock ──► system_logs (metadata.type="tool_use_block")    │
│      │         │                                                            │
│      │         └──► PreToolUse hook ──► orchestrator_chat (type="tool_use")│
│      │                                                                      │
│      └──► TextBlock ──► orchestrator_chat (sender=orchestrator)            │
│                                                                             │
│  SUBAGENT EXECUTION (if spawned)                                           │
│      │                                                                      │
│      ├──► Hook Events ──► agent_logs (event_category="hook")               │
│      │    - PreToolUse                                                      │
│      │    - PostToolUse                                                     │
│      │    - UserPromptSubmit                                                │
│      │    - Stop                                                            │
│      │    - SubagentStop                                                    │
│      │    - PreCompact                                                      │
│      │                                                                      │
│      └──► Response Blocks ──► agent_logs (event_category="response")       │
│           - TextBlock                                                       │
│           - ThinkingBlock                                                   │
│           - ToolUseBlock                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Database Schema

### `orchestrator_chat`
| Column                | Type      | Description                              |
|-----------------------|-----------|------------------------------------------|
| id                    | UUID      | Primary key                              |
| orchestrator_agent_id | UUID      | FK to orchestrator_agents                |
| sender_type           | TEXT      | "user" \| "orchestrator" \| "agent"      |
| receiver_type         | TEXT      | "user" \| "orchestrator" \| "agent"      |
| message               | TEXT      | The message content                      |
| agent_id              | UUID      | FK to agents (if sender/receiver=agent)  |
| metadata              | JSONB     | {type, tool_name, tool_input, etc.}      |
| summary               | TEXT      | AI-generated summary                     |
| created_at            | TIMESTAMP | When created                             |

### `system_logs`
| Column    | Type      | Description                                    |
|-----------|-----------|------------------------------------------------|
| id        | UUID      | Primary key                                    |
| file_path | TEXT      | Source file (optional)                         |
| adw_id    | TEXT      | AI Developer Workflow ID (optional)            |
| adw_step  | TEXT      | ADW step (optional)                            |
| level     | TEXT      | "DEBUG" \| "INFO" \| "WARNING" \| "ERROR"      |
| message   | TEXT      | Log message                                    |
| metadata  | JSONB     | {type, thinking, tool_name, tool_input, etc.}  |
| summary   | TEXT      | AI-generated summary                           |
| timestamp | TIMESTAMP | When logged                                    |

### `agent_logs`
| Column         | Type      | Description                              |
|----------------|-----------|------------------------------------------|
| id             | UUID      | Primary key                              |
| agent_id       | UUID      | FK to agents                             |
| session_id     | TEXT      | Claude SDK session ID                    |
| task_slug      | TEXT      | Task identifier                          |
| adw_id         | TEXT      | AI Developer Workflow ID                 |
| adw_step       | TEXT      | ADW step                                 |
| entry_index    | INTEGER   | Sequential order within task             |
| event_category | TEXT      | "hook" \| "response"                     |
| event_type     | TEXT      | See event types below                    |
| content        | TEXT      | Human-readable content                   |
| payload        | JSONB     | Full event data                          |
| summary        | TEXT      | AI-generated summary                     |
| timestamp      | TIMESTAMP | When logged                              |

## API Reference

### GET /api/logs
Get unified logs from all sources.

**Query Parameters:**
| Parameter             | Type   | Description                                    |
|-----------------------|--------|------------------------------------------------|
| limit                 | int    | Max results (default: 100, max: 1000)          |
| offset                | int    | Pagination offset (default: 0)                 |
| source                | string | Filter: agent_logs, system_logs, orchestrator_chat |
| event_type            | string | Filter by event type                           |
| event_category        | string | Filter: hook, response, system, chat           |
| level                 | string | Filter by log level (system_logs only)         |
| sender_type           | string | Filter: user, orchestrator, agent (chat only)  |
| agent_id              | string | Filter by agent UUID                           |
| orchestrator_agent_id | string | Filter by orchestrator agent UUID              |
| search                | string | Search in message content                      |
| hours                 | int    | Only show logs from last N hours               |

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid",
      "source": "agent_logs",
      "timestamp": "2024-01-15T10:30:00",
      "message": "Executing tool Read...",
      "event_type": "PreToolUse",
      "event_category": "hook",
      "agent_id": "uuid",
      "agent_name": "builder-agent",
      "payload": {...}
    }
  ],
  "count": 100
}
```

### GET /api/logs/stats
Get statistics about logs from all tables.

**Response:**
```json
{
  "total_count": 15432,
  "agent_logs_count": 12000,
  "system_logs_count": 2432,
  "chat_count": 1000,
  "event_types": {
    "PreToolUse": 5000,
    "PostToolUse": 5000,
    "TextBlock": 2000
  },
  "sources": {
    "agent_logs": 12000,
    "system_logs": 2432,
    "orchestrator_chat": 1000
  }
}
```

### GET /api/logs/filter-options
Get available filter options for the UI.

**Response:**
```json
{
  "sources": ["agent_logs", "system_logs", "orchestrator_chat"],
  "event_types": ["PreToolUse", "PostToolUse", "TextBlock", ...],
  "event_categories": ["hook", "response"],
  "levels": ["DEBUG", "INFO", "WARNING", "ERROR"],
  "sender_types": ["user", "orchestrator", "agent"],
  "agents": [{"id": "uuid", "name": "builder-agent"}, ...],
  "orchestrator_agents": [{"id": "uuid", "session_id": "abc123"}, ...]
}
```

### GET /api/chat
Get orchestrator chat messages only.

### GET /api/agent-logs
Get agent logs only.

### GET /api/system-logs
Get system logs only (includes orchestrator thinking/tool use).

### GET /health
Health check endpoint.

## Filtering Guide

### Filter by Source
Use the Source dropdown to view logs from a specific table:
- **Agent**: Hook events and response blocks from subagents
- **System**: Orchestrator thinking blocks and internal events
- **Chat**: Three-way conversation between user, orchestrator, and agents

### Filter by Event Type
Common event types:
- `PreToolUse`: Before a tool is executed
- `PostToolUse`: After a tool completes
- `TextBlock`: Text response from agent
- `ThinkingBlock`: Agent reasoning
- `ToolUseBlock`: Tool invocation
- `thinking_block`: Orchestrator thinking (in system_logs)
- `tool_use_block`: Orchestrator tool use (in system_logs)

### Filter by Sender (Chat only)
- **User**: Messages from the user
- **Orchestrator**: Orchestrator responses and delegations
- **Agent**: Agent reports and completions

### Filter by Level (System logs only)
- **DEBUG**: Detailed debugging information
- **INFO**: General information
- **WARNING**: Warning conditions
- **ERROR**: Error conditions

### Time Range
Filter logs by recency:
- Last 1 hour
- Last 6 hours
- Last 24 hours
- Last 48 hours
- Last 7 days

### Search
Full-text search across message content.

## Troubleshooting

### Database Connection Issues
1. Ensure the DATABASE_URL environment variable is set
2. Check that PostgreSQL is running and accessible
3. Verify the database has the required tables

### Missing Orchestrator Prompts
If orchestrator prompts aren't appearing:
1. Check `orchestrator_chat` table for user messages
2. Check `system_logs` for thinking_block and tool_use_block entries
3. Verify the orchestrator_agent_id filter is correct

### Performance Issues
- Reduce the limit parameter for large datasets
- Use time range filters to narrow results
- Add specific filters before searching

## Development

### Project Structure
```
log_viewer/
├── main.py              # FastAPI application
├── README.md            # This file
├── static/
│   ├── app.js           # Frontend JavaScript
│   └── styles.css       # CSS styles
└── templates/
    └── index.html       # HTML template
```

### Environment Variables
| Variable        | Default                                    | Description          |
|-----------------|--------------------------------------------|-----------------------|
| DATABASE_URL    | postgresql://localhost:5432/orchestrator   | PostgreSQL connection |
| LOG_VIEWER_PORT | 5998                                       | Server port           |
| LOG_VIEWER_HOST | 0.0.0.0                                    | Server host           |

### Adding New Features
1. Add new database queries in `fetch_*` functions
2. Add new API endpoints in the FastAPI app
3. Update frontend in `app.js` and `styles.css`
4. Update this README

## Color Legend
- **Cyan (#06b6d4)**: Agent logs - subagent events
- **Purple (#a855f7)**: System logs - orchestrator internal events
- **Green (#22c55e)**: Chat - user/orchestrator/agent conversations
