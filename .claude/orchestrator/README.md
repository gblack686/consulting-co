# Multi-Agent Orchestration Platform

Production-grade orchestration system integrated with your existing observability stack (Langfuse + Neo4j/Graphiti).

## 🎯 What This Is

A complete multi-agent orchestration platform with:
- ✅ **PostgreSQL (Supabase)** - Persistent state and event logging
- ✅ **Real-time WebSocket UI** - Live agent monitoring
- ✅ **Natural language control** - Chat-based agent delegation
- ✅ **Cost tracking** - Per-agent token usage + USD totals
- ✅ **Session resumption** - Continue from any point
- ✅ **Full integration** - Works with existing Langfuse + Neo4j hooks

## 🚀 Quick Start

### 1. Start the Orchestrator

```bash
# From consulting-co root
.claude\orchestrator\start_orchestrator.bat
```

This launches:
- **Backend** (FastAPI) - http://localhost:8000
- **Frontend** (Vue 3) - http://localhost:3001

### 2. Open All Dashboards

```bash
# From consulting-co root
.claude\open_dashboards.bat
```

Opens:
- **Orchestrator UI** - http://localhost:3001
- **Langfuse** - http://localhost:3000
- **Neo4j** - http://localhost:7474

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│         Multi-Agent Orchestrator                │
│  (FastAPI + Vue 3 + WebSocket + PostgreSQL)     │
└─────────────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
┌──────────────┐      ┌──────────────────┐
│  Langfuse    │      │  Neo4j/Graphiti  │
│  (Traces)    │      │  (Knowledge)     │
└──────────────┘      └──────────────────┘
```

### Database Schema

**Supabase Tables:**
- `orchestrator_agents` - Main orchestrator state
- `agents` - Managed agents registry
- `prompts` - Prompt versioning
- `agent_logs` - All agent events
- `system_logs` - System events
- `orchestrator_chat` - Chat interface

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Supabase (PostgreSQL)
SUPABASE_URL=https://unickqnwfheaczccvgbw.supabase.co
SUPABASE_SERVICE_KEY=[your-key]
DATABASE_URL=postgresql://postgres.unickqnwfheaczccvgbw:[password]@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres?sslmode=require

# Anthropic
ANTHROPIC_API_KEY=[your-key]

# Langfuse (existing)
LANGFUSE_PUBLIC_KEY=[your-key]
LANGFUSE_SECRET_KEY=[your-key]
LANGFUSE_BASE_URL=http://localhost:3000

# Neo4j (existing)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword

# OpenAI (for Graphiti)
OPENAI_API_KEY=[your-key]
```

## 📁 Project Structure

```
.claude/orchestrator/
├── orchestrator_db/              # Database layer
│   ├── migrations/               # SQL migrations (✅ completed)
│   ├── models.py                 # Pydantic models
│   └── migrate_with_asyncpg.py  # Migration runner
│
├── orchestrator_3_stream/        # Main application
│   ├── backend/                  # FastAPI server
│   │   ├── main.py              # Entry point
│   │   ├── modules/
│   │   │   ├── config.py        # Environment config
│   │   │   ├── database.py      # PostgreSQL operations
│   │   │   ├── orchestrator_service.py
│   │   │   ├── agent_manager.py
│   │   │   └── websocket_manager.py
│   │   └── logs/                # Hourly rotating logs
│   │
│   └── frontend/                 # Vue 3 UI
│       ├── src/
│       │   ├── components/
│       │   │   ├── AgentList.vue
│       │   │   ├── EventStream.vue
│       │   │   └── OrchestratorChat.vue
│       │   └── stores/
│       │       └── orchestratorStore.ts
│       └── vite.config.ts
│
├── start_orchestrator.bat        # Launch script
└── README.md                     # This file
```

## 🎮 Usage

### Basic Workflow

1. **Start orchestrator:**
   ```bash
   .claude\orchestrator\start_orchestrator.bat
   ```

2. **Open UI:** http://localhost:3001

3. **Send a task:**
   ```
   "Create a React app with 3 agents:
    - Agent 1: Research best practices
    - Agent 2: Build components
    - Agent 3: Write tests"
   ```

4. **Watch agents work in real-time:**
   - Left panel: Agent status
   - Center: Event stream
   - Right: Chat interface

5. **Track costs:**
   - Per-agent token usage
   - Real-time USD totals
   - Full event history

### Advanced Features

**Session Resumption:**
```bash
# Resume previous session
cd .claude/orchestrator/orchestrator_3_stream/backend
uv run python main.py --session <session-id>
```

**Custom Working Directory:**
```bash
uv run python main.py --cwd /path/to/project
```

**API Access:**
```bash
# Health check
curl http://localhost:8000/health

# Get orchestrator info
curl http://localhost:8000/get_orchestrator
```

## 🔗 Integration with Existing Hooks

Your existing hooks continue working alongside the orchestrator:

```
.claude/hooks/
├── log_to_langfuse.py      # ✅ Still logs to Langfuse
├── log_to_graphiti.py      # ✅ Still builds knowledge graph
├── session_start.py         # ✅ Still tracks sessions
└── ... (all other hooks)
```

**Future integration options:**
1. **Dual logging** - Send events to both systems
2. **Unified view** - Orchestrator UI shows Langfuse data
3. **Knowledge graph** - Import Neo4j relationships

## 📊 Monitoring

### Orchestrator UI (http://localhost:3001)
- Real-time agent monitoring
- Event stream with filtering
- Cost tracking dashboard
- Chat-based control

### Langfuse (http://localhost:3000)
- Detailed traces
- Token usage analytics
- Performance metrics
- Error tracking

### Neo4j (http://localhost:7474)
- Knowledge graph
- Episodic memory
- Entity relationships

## 🧪 Testing

### Test Database Connection

```bash
cd .claude/orchestrator/orchestrator_db
uv run migrate_with_asyncpg.py
```

### Test Backend

```bash
cd .claude/orchestrator/orchestrator_3_stream/backend
uv run python main.py
```

Visit: http://localhost:8000/health

### Test Frontend

```bash
cd .claude/orchestrator/orchestrator_3_stream/frontend
bun run dev
```

Visit: http://localhost:3001

## 🔧 Troubleshooting

### Backend won't start

**Check environment:**
```bash
# Verify DATABASE_URL is set
grep DATABASE_URL .env

# Test database connection
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('your-db-url'))"
```

**Check dependencies:**
```bash
cd .claude/orchestrator/orchestrator_3_stream/backend
uv sync
```

### Frontend won't start

**Install dependencies:**
```bash
cd .claude/orchestrator/orchestrator_3_stream/frontend
bun install
```

**Check port availability:**
```bash
# Frontend uses port 3001
netstat -ano | findstr :3001
```

### Database connection errors

**Use direct connection instead of pooler:**
```bash
# In .env, change from:
DATABASE_URL=postgresql://postgres.xxx:pass@aws-0-us-west-1.pooler.supabase.com:6543/postgres

# To:
DATABASE_URL=postgresql://postgres.xxx:pass@db.xxx.supabase.co:5432/postgres?sslmode=require
```

## 📚 Next Steps

1. ✅ **Migrations completed** - All tables created in Supabase
2. ✅ **Apps configured** - Backend + Frontend ready
3. ✅ **Dashboards integrated** - Single launcher for all tools
4. 🎯 **Test workflow** - Try orchestrating multiple agents
5. 🔄 **Hook integration** - Optional: Send events to orchestrator
6. 📊 **Custom views** - Build custom analytics on PostgreSQL data

## 🆘 Support

**Documentation:**
- Backend: `.claude/orchestrator/orchestrator_3_stream/CLAUDE.md`
- Database: `.claude/orchestrator/orchestrator_db/README.md`
- Migration Plan: `.claude/context/orchestrator/MIGRATION_PLAN.md`

**Quick links:**
- Supabase Dashboard: https://supabase.com/dashboard/project/unickqnwfheaczccvgbw
- API Docs: http://localhost:8000/docs (when running)
- WebSocket: ws://localhost:8000/ws

## 🎉 You're Ready!

Start the orchestrator and begin coordinating multiple agents through a beautiful real-time interface backed by PostgreSQL!

```bash
.claude\orchestrator\start_orchestrator.bat
```

Then open: http://localhost:3001
