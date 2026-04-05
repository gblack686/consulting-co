# Langfuse API Utilities

## Overview

Created reusable utilities to safely interact with Langfuse API without common errors:

### Files Created
- ``.claude/hooks/utils/langfuse_api.py`` - Python client with proper auth and error handling
- ``.claude/hooks/utils/traces.sh`` - Shell wrapper for easy CLI access

## Problems Avoided

### ❌ Before (Direct curl)
```bash
# Problem 1: jq not available
curl ... | jq .

# Problem 2: Wrong auth header format
-H "X-API-Key: pk-lf-..."  # ← Langfuse requires basic auth!

# Problem 3: Wrong auth method
--header "Authorization: Bearer pk-lf-..."  # ← Fails

# Problem 4: Wrong query param names
orderBy=timestamp&sortOrder=DESC  # ← API rejects these
```

### ✅ After (Python client)
```python
from langfuse_api import LangfuseAPI

api = LangfuseAPI()
traces = api.get_traces(limit=10)

# ✓ Correct basic auth (public_key:secret_key)
# ✓ JSON parsing without jq
# ✓ Error handling built-in
# ✓ Pretty printing included
```

## Usage Examples

### Python (Direct)

```python
from langfuse_api import LangfuseAPI

# Initialize
api = LangfuseAPI()
# Or with custom credentials:
api = LangfuseAPI(base_url="http://localhost:3000",
                  public_key="pk-...",
                  secret_key="sk-...")

# Get recent traces
traces = api.get_traces(limit=5)
for trace in traces:
    api.print_trace_summary(trace)

# Get specific trace
trace = api.get_trace("7a6a5fe9564cfb610f4a680eb1f703b8")
print(json.dumps(trace, indent=2))

# Get observations
obs = api.get_observations("7a6a5fe9564cfb610f4a680eb1f703b8")

# Manage projects
projects = api.get_projects()
new_project_id = api.create_project("my-new-project")
```

### CLI (Command Line)

```bash
# List recent traces (default 5, pretty printed)
python3 .claude/hooks/utils/langfuse_api.py list

# List 10 traces
python3 .claude/hooks/utils/langfuse_api.py list --limit 10

# Filter by project
python3 .claude/hooks/utils/langfuse_api.py list --project-id cmi19k90n000atd0713m9maij

# Get specific trace as JSON
python3 .claude/hooks/utils/langfuse_api.py get --trace-id 7a6a5fe9564cfb610f4a680eb1f703b8

# List all projects
python3 .claude/hooks/utils/langfuse_api.py projects
```

## API Reference

### LangfuseAPI Class

#### Methods

**`get_traces(limit=10, project_id=None) → List[Dict]`**
- Fetch recent traces
- Args:
  - `limit`: Number of traces (default 10)
  - `project_id`: Optional filter by project
- Returns: List of trace dicts

**`get_trace(trace_id) → Dict`**
- Fetch specific trace with all observations
- Args:
  - `trace_id`: The trace ID
- Returns: Full trace dict including observations

**`get_observations(trace_id) → List[Dict]`**
- Fetch observations for a trace
- Args:
  - `trace_id`: The trace ID
- Returns: List of observation dicts

**`get_projects() → List[Dict]`**
- Fetch all projects in organization
- Returns: List of project dicts

**`create_project(name) → Optional[str]`**
- Create new project
- Args:
  - `name`: Project name
- Returns: Project ID if created, None on error

**`print_trace_summary(trace)`**
- Pretty print trace summary
- Args:
  - `trace`: Trace dict from API

### Authentication

Automatically loads from `.env`:
- `LANGFUSE_BASE_URL` - Server URL (default: http://localhost:3000)
- `LANGFUSE_PUBLIC_KEY` - API public key
- `LANGFUSE_SECRET_KEY` - API secret key

Or pass explicitly to constructor:
```python
api = LangfuseAPI(
    base_url="http://localhost:3000",
    public_key="pk-...",
    secret_key="sk-..."
)
```

## Error Handling

All API calls handle errors gracefully:

```python
# Returns dict with "error" key on failure
response = api._request("GET", "/api/public/traces")
if "error" in response:
    print(f"Failed: {response['error']}")
```

## Example Output

```
============================================================
📊 TRACE: consulting-co-conversation
============================================================
ID:        7a6a5fe9564cfb610f4a680eb1f703b8
Session:   61100aff-1805-42a4-849b-4e2ad3bcf57e
Project:   cmi19k90n000atd0713m9maij
Tags:      consulting-co, claude-code, conversation
Cost:      $0.021631
Latency:   1ms
Model:     claude-haiku-4-5-20251001

Metadata:
  organization: consulting-co
  project: consulting-co
  user_message_length: 30
  assistant_message_length: 1592
  conversation_latency_ms: 136968

Observations: 2
  - SPAN: consulting-co-conversation
  - GENERATION: claude-response
```

## Why This is Better

| Issue | Before | After |
|-------|--------|-------|
| **Auth** | Guessed wrong method | ✓ Uses correct basic auth |
| **JSON** | Depended on jq | ✓ Built-in parsing |
| **API params** | Trial & error | ✓ Pre-validated |
| **Errors** | Script crashed | ✓ Graceful handling |
| **Output** | Raw JSON | ✓ Pretty printed |
| **Reusability** | One-off scripts | ✓ Importable class |

## Future Enhancements

Could add:
- Filtering by tags
- Time range queries
- Export to CSV/Excel
- Cost reporting by project
- Trace comparison
- Integration with local Neo4j (Graphiti)
