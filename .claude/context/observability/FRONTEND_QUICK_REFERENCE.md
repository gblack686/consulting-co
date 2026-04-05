# Observability Frontend - Quick Reference Guide

## Running Services

### 1. Langfuse Dashboard
- **URL:** http://localhost:3000
- **Type:** Full-stack observability platform (traces, costs, evaluations)
- **Port:** 3000
- **Status:** ✓ Running
- **Framework:** Next.js 3.130.0 OSS
- **Purpose:** Comprehensive LLM observability and cost tracking

### 2. Multi-Agent Observability Dashboard
- **URL:** http://localhost:4000
- **Type:** Real-time event monitoring and visualization
- **Port:** 4000
- **Status:** ✓ Running
- **Framework:** Bun + Vue.js 3
- **Purpose:** Live agent activity monitoring with swim lanes and event streams
- **WebSocket:** ws://localhost:4000/stream (real-time updates)

### 3. Neo4j Browser
- **URL:** http://localhost:7474/browser/
- **Type:** Graph database interface (connection required)
- **Port:** 7474
- **Status:** ⚠️ UI running, database not connected
- **Note:** Backend on port 7687 (not running)

---

## Key API Endpoints

### Observability Server (Port 4000)

```
POST   /api/events                  - Submit hook events
GET    /api/events                  - Fetch events
GET    /api/events/:id              - Get event details
PUT    /api/events/:id              - Update event (HITL responses)
GET    /api/filter-options          - Get filter values
GET    /stream                      - WebSocket connection
```

### Theme Management

```
POST   /api/themes                  - Create theme
GET    /api/themes                  - Search themes
GET    /api/themes/:id              - Get theme
PUT    /api/themes/:id              - Update theme
DELETE /api/themes/:id              - Delete theme
POST   /api/themes/import           - Import theme
GET    /api/themes/:id/export       - Export theme
```

---

## Project Structure

```
C:\Users\gblac\OneDrive\Desktop\consulting-co\observability\
├── apps/
│   ├── client/              (Vue.js frontend for port 4000)
│   │   ├── src/
│   │   │   ├── App.vue     (Main component)
│   │   │   ├── components/ (UI components)
│   │   │   ├── composables/(Reactive logic)
│   │   │   └── types.ts    (TypeScript definitions)
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tailwind.config.js
│   │
│   ├── server/              (Bun server for port 4000)
│   │   ├── src/
│   │   │   ├── index.ts    (Main server entry)
│   │   │   ├── db.ts       (SQLite database)
│   │   │   ├── theme.ts    (Theme management)
│   │   │   └── types.ts    (TypeScript definitions)
│   │   ├── events.db       (SQLite database)
│   │   ├── package.json
│   │   └── bun.lock
│   │
│   └── demo-cc-agent/       (Demo agent implementation)
│
├── CLAUDE.md                (Project instructions)
├── README.md                (Setup and overview)
└── scripts/                 (Utility scripts)
```

---

## Technology Stack

### Frontend (Port 4000)
- **Vue.js** 3.5.17
- **Vite** 7.0.4 (dev server)
- **TypeScript** 5.8.3
- **Tailwind CSS** 3.4.16
- **PostCSS** 8.5.3

### Backend (Port 4000)
- **Runtime:** Bun (JavaScript/TypeScript runtime)
- **Server:** Bun.serve() with HTTP & WebSocket
- **Database:** SQLite with bun:sqlite
- **Hot Reload:** `bun --watch src/index.ts`

### Langfuse (Port 3000)
- **Framework:** Next.js (React)
- **Version:** 3.130.0 (OSS)
- **Type:** Full-stack application

---

## Development Commands

### Multi-Agent Observability

```bash
# Client development
cd observability/apps/client
bun install
bun run dev              # Runs on http://localhost:5173 by default

# Server development
cd observability/apps/server
bun install
bun run dev              # Runs on http://localhost:4000

# Build
cd observability/apps/client
bun run build            # Creates production build
```

### Environment Configuration

Create `.env` files:

```bash
# observability/apps/server/.env
SERVER_PORT=4000

# observability/apps/client/.env
VITE_API_URL=http://localhost:4000
```

---

## Data Schema

### Hook Event Structure
```typescript
{
  id: string;
  source_app: string;           // e.g., "revstar-quickstart"
  session_id: string;            // Unique session identifier
  event_type: string;            // e.g., "PreToolUse", "PostToolUse"
  timestamp: number;             // Unix timestamp
  data: {
    tool_name?: string;
    tool_input?: any;
    tool_output?: any;
    duration?: number;
    error?: string;
  };
  humanInTheLoop?: {
    required: boolean;
    prompt: string;
    responseWebSocketUrl?: string;
  };
}
```

### Theme Structure
```typescript
{
  id: string;
  name: string;
  description?: string;
  isPublic: boolean;
  authorId: string;
  theme: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    // ... more color definitions
  };
  createdAt: number;
  updatedAt: number;
}
```

---

## Important Features

### Langfuse Dashboard
- ✓ Real-time trace ingestion
- ✓ Cost tracking per model
- ✓ Latency analysis
- ✓ User session tracking
- ✓ Prompt management
- ✓ Evaluation scoring
- ✓ Human annotation workflows
- ✓ Dataset management
- ✓ Advanced filtering and search

### Multi-Agent Observability
- ✓ Real-time event streaming
- ✓ Multi-agent swim lane view
- ✓ Event timeline visualization
- ✓ Live pulse chart
- ✓ Custom theme system
- ✓ Filter panel for event exploration
- ✓ Human-in-the-loop responses
- ✓ WebSocket-based updates

---

## Common Issues & Solutions

### Port Already in Use
```bash
# Find and kill process using port
netstat -ano | findstr ":4000"      # Windows
lsof -i :4000                       # Mac/Linux
kill -9 <PID>                       # Kill process
```

### Database Connection Issues
- Check that sqlite3 is installed: `bun pm list`
- Verify events.db file exists and has write permissions
- Check database size: `ls -lh observability/apps/server/events.db`

### WebSocket Connection Refused
- Ensure server is running on port 4000
- Check firewall settings
- Verify WebSocket endpoint: `ws://localhost:4000/stream`

### Neo4j Connection
- Neo4j server not required for observability to function
- To enable: Install Neo4j and run `neo4j console`
- Will listen on port 7687 (Bolt) and 7474 (HTTP)

---

## Monitoring & Health Checks

### Server Health
```bash
# Test API endpoint
curl http://localhost:4000/api/events

# Expected response: JSON array of events

# Test WebSocket
wscat -c ws://localhost:4000/stream
```

### Database Health
```bash
# Check database file
ls -lh observability/apps/server/events.db

# Expected:
# - events.db exists (4-10 KB base, grows with data)
# - events.db-shm exists (shared memory file)
# - events.db-wal exists (write-ahead log)
```

### Frontend Health
- Visit http://localhost:4000 in browser
- Check browser console for errors (should be empty)
- Verify WebSocket connection indicator shows "Connected"

---

## Integration with Claude Code

### Hook Configuration
Agents send events to observability via hooks:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app your-app-name --event-type PostToolUse --summarize"
        }
      ]
    }]
  }
}
```

### Event Submission Format
```bash
# POST to observability server
curl -X POST http://localhost:4000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "source_app": "your-app-name",
    "session_id": "abc123def",
    "event_type": "PostToolUse",
    "data": {
      "tool_name": "grep",
      "tool_input": {"pattern": "search-term"},
      "tool_output": ["results..."],
      "duration": 150
    }
  }'
```

---

## Performance Characteristics

### Langfuse
- **Page Load:** ~2 seconds
- **Bundle Size:** ~300 KB (gzipped)
- **API Response:** <100ms
- **Concurrent Users:** Scales with server resources

### Multi-Agent Observability
- **WebSocket Latency:** <50ms
- **Event Processing:** Real-time
- **Database Query:** <5ms typical
- **Max Events:** Limited by storage (SQLite can handle 100k+ events)

---

## References

- **Observability Repo:** `C:\Users\gblac\OneDrive\Desktop\consulting-co\observability\`
- **README:** `observability/README.md`
- **Claude Instructions:** `observability/CLAUDE.md`
- **Full QA Report:** `observability/FRONTEND_QA_REVIEW.md`

