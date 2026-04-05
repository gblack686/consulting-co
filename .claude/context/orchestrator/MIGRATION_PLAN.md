# Multi-Agent Orchestrator Migration Plan

## Executive Summary

Replace the current hooks-based observability system with a production-grade multi-agent orchestration platform featuring PostgreSQL persistence, real-time WebSocket UI, and comprehensive cost tracking.

## Current System Architecture

### Components
```
Observability Stack:
├── Langfuse (localhost:3000)
│   └── Traces, analytics, token usage
├── Neo4j/Graphiti (localhost:7474)
│   └── Knowledge graph, episodic memory
└── Hooks System (.claude/hooks/)
    ├── log_to_langfuse.py       → Trace every event
    ├── log_to_graphiti.py       → Build knowledge graph
    ├── session_start.py         → Track session start
    ├── session_end.py           → Track session end
    ├── pre_tool_use.py          → Before tool execution
    ├── post_tool_use.py         → After tool execution
    ├── stop.py                  → Agent stop events
    └── subagent_stop.py         → Subagent management
```

### Strengths
✅ Comprehensive observability (Langfuse)
✅ Knowledge graph integration (Neo4j/Graphiti)
✅ Real-time hook-based tracking
✅ Established workflow

### Limitations
❌ No persistent database for orchestration state
❌ No real-time UI for agent management
❌ Manual coordination of multi-agent workflows
❌ No cost tracking per agent
❌ Separate, disconnected systems

## New System Architecture

### Components
```
Multi-Agent Orchestration Platform:
├── PostgreSQL Database (NeonDB/local)
│   ├── orchestrator_agents     → Main orchestrator
│   ├── agents                  → Managed agents registry
│   ├── prompts                 → Prompt versioning
│   ├── agent_logs              → All agent events
│   └── system_logs             → System events
├── Backend (FastAPI)
│   ├── WebSocket streaming     → Real-time agent communication
│   ├── REST API                → Management endpoints
│   ├── Agent Manager           → Coordinate multiple agents
│   └── Database Service        → PostgreSQL operations
└── Frontend (Bun + JavaScript)
    ├── Real-time UI            → Live agent monitoring
    ├── Cost Dashboard          → Per-agent token/cost tracking
    └── Event Stream            → Websocket-based updates
```

### Capabilities
✅ **PostgreSQL persistence** - All events, costs, state
✅ **Real-time web UI** - Monitor agents live
✅ **Natural language control** - Orchestrator manages other agents
✅ **Cost tracking** - Per-agent token usage + USD
✅ **Session resumption** - Continue from any point
✅ **Git worktree support** - Parallel agent execution
✅ **Comprehensive observability** - Every event tracked

## Migration Strategy

### Phase 1: Database Setup
**Goal:** Establish PostgreSQL database foundation

**Steps:**
1. Choose database option:
   - **Option A:** NeonDB (Recommended)
     - Free tier available
     - Serverless PostgreSQL
     - Zero maintenance
   - **Option B:** Docker PostgreSQL
     - Local development
     - Full control
   - **Option C:** Local PostgreSQL
     - Already installed

2. Run migrations:
   ```bash
   # Copy .env configuration
   cp ../tac/multi-agent-orchestration/.env.sample .env

   # Set DATABASE_URL and ANTHROPIC_API_KEY

   # Run migrations
   uv run ../tac/multi-agent-orchestration/apps/orchestrator_db/run_migrations.py
   ```

3. Verify tables created:
   - orchestrator_agents
   - agents
   - prompts
   - agent_logs
   - system_logs

### Phase 2: Install Orchestrator
**Goal:** Copy and configure orchestrator apps

**Steps:**
1. Copy orchestrator apps:
   ```bash
   # Create orchestrator directory
   mkdir -p .claude/orchestrator

   # Copy both apps
   cp -r ../tac/multi-agent-orchestration/apps/orchestrator_db .claude/orchestrator/
   cp -r ../tac/multi-agent-orchestration/apps/orchestrator_3_stream .claude/orchestrator/
   ```

2. Configure environment:
   ```bash
   # Copy .env to both apps
   cp .env .claude/orchestrator/orchestrator_db/.env
   cp .env .claude/orchestrator/orchestrator_3_stream/.env
   ```

3. Install dependencies:
   ```bash
   # Backend dependencies (Python)
   cd .claude/orchestrator/orchestrator_3_stream/backend
   uv sync

   # Frontend dependencies (Bun)
   cd ../frontend
   bun install
   ```

### Phase 3: Hook Integration
**Goal:** Connect existing hooks to new orchestrator

**Options:**

**Option A: Dual System (Recommended for transition)**
- Keep existing Langfuse + Neo4j hooks
- Add new orchestrator alongside
- Gradual migration path

**Option B: Unified System**
- Replace hooks with orchestrator events
- Single source of truth
- Clean architecture

**Integration Points:**

```python
# New hook: .claude/hooks/log_to_orchestrator.py

import asyncio
import httpx
from datetime import datetime

ORCHESTRATOR_API = "http://localhost:8000"

async def log_event(event_data: dict):
    """Send event to orchestrator database"""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{ORCHESTRATOR_API}/events",
            json={
                "event_type": event_data.get("type"),
                "agent_id": event_data.get("agent_id"),
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Called from existing hooks
if __name__ == "__main__":
    import sys
    import json
    event = json.loads(sys.stdin.read())
    asyncio.run(log_event(event))
```

**Modify existing hooks:**
```python
# In log_to_langfuse.py, add:
import subprocess

# ... existing Langfuse code ...

# Also send to orchestrator
subprocess.run(
    ["python", ".claude/hooks/log_to_orchestrator.py"],
    input=json.dumps(event_data),
    text=True
)
```

### Phase 4: Unified Dashboard
**Goal:** Single interface for all observability

**Create:** `.claude/orchestrator/dashboard_launcher.bat`

```batch
@echo off
echo Starting Multi-Agent Orchestration Platform...
echo.

REM Start backend
start "Orchestrator Backend" cmd /c "cd .claude\orchestrator\orchestrator_3_stream\backend && uv run python main.py"
timeout /t 3 /nobreak >nul

REM Start frontend
start "Orchestrator Frontend" cmd /c "cd .claude\orchestrator\orchestrator_3_stream\frontend && bun run dev"
timeout /t 3 /nobreak >nul

REM Start Langfuse (optional - keep existing observability)
start "Langfuse" cmd /c "docker start langfuse-db && docker start langfuse-web"
timeout /t 2 /nobreak >nul

REM Start Neo4j (optional - keep knowledge graph)
start "Neo4j" cmd /c "docker start neo4j-graphiti"

echo.
echo ========================================
echo ORCHESTRATION PLATFORM STARTED
echo ========================================
echo.
echo Orchestrator UI:  http://localhost:3001
echo Orchestrator API: http://localhost:8000
echo Langfuse:         http://localhost:3000
echo Neo4j:            http://localhost:7474
echo.
echo Ready to orchestrate multiple agents!
echo.

REM Open orchestrator UI
timeout /t 5 /nobreak >nul
start http://localhost:3001

pause
```

### Phase 5: Testing & Validation
**Goal:** Verify end-to-end functionality

**Test Cases:**

1. **Single Agent Workflow**
   ```bash
   # Start orchestrator
   .claude/orchestrator/dashboard_launcher.bat

   # Submit task via UI
   # → Verify event logging
   # → Verify cost tracking
   # → Check PostgreSQL tables
   ```

2. **Multi-Agent Coordination**
   ```bash
   # Task: "Create a React app with 3 agents:
   #        - Agent 1: Research best practices
   #        - Agent 2: Build components
   #        - Agent 3: Write tests"

   # Verify:
   # → All agents created in database
   # → Events logged per agent
   # → Cost tracked per agent
   # → Real-time UI updates
   ```

3. **Session Resumption**
   ```bash
   # Stop mid-workflow
   # Resume with: --session <session_id>
   # Verify state restored
   ```

## Migration Checklist

### Pre-Migration
- [ ] Database choice decided (NeonDB/Docker/Local)
- [ ] Backup existing .env file
- [ ] Document current hook configurations
- [ ] Take screenshots of current dashboards

### Database Setup
- [ ] PostgreSQL accessible
- [ ] DATABASE_URL configured
- [ ] Migrations run successfully
- [ ] Tables verified in database

### Orchestrator Installation
- [ ] Apps copied to .claude/orchestrator/
- [ ] .env files configured
- [ ] Backend dependencies installed (uv sync)
- [ ] Frontend dependencies installed (bun install)

### Hook Integration
- [ ] New log_to_orchestrator.py hook created
- [ ] Existing hooks modified (optional)
- [ ] Event flow tested
- [ ] Both systems logging (dual mode)

### Dashboard
- [ ] dashboard_launcher.bat created
- [ ] All services start successfully
- [ ] UI accessible at localhost:3001
- [ ] API accessible at localhost:8000

### Testing
- [ ] Single agent workflow tested
- [ ] Multi-agent coordination tested
- [ ] Session resumption tested
- [ ] Cost tracking verified
- [ ] Event logging verified

### Production
- [ ] Old orchestrator archived
- [ ] Documentation updated
- [ ] Team trained on new UI
- [ ] Monitoring alerts configured

## Rollback Plan

If migration issues occur:

1. **Keep existing hooks running**
   - They remain unchanged
   - Langfuse + Neo4j still work

2. **Disable orchestrator**
   ```bash
   # Stop services
   docker stop postgres-orchestrator

   # Revert hooks if modified
   git checkout .claude/hooks/
   ```

3. **Use archived orchestrator**
   ```bash
   # Old Node.js version still in archive/
   node archive/orchestrator-server.js
   ```

## Benefits Summary

### For Development
- ✅ **Visual monitoring** - See all agents in real-time
- ✅ **Cost control** - Track spending per agent
- ✅ **Debugging** - Complete event log in database
- ✅ **Reproducibility** - Resume any session

### For Production
- ✅ **Scalable** - PostgreSQL handles thousands of events
- ✅ **Reliable** - Database persistence, no data loss
- ✅ **Maintainable** - Single platform vs. scattered hooks
- ✅ **Observable** - Built-in metrics and logging

### For Multi-Agent Workflows
- ✅ **Coordination** - Orchestrator manages agent delegation
- ✅ **Natural language** - Control via chat interface
- ✅ **Git worktrees** - Parallel agent execution
- ✅ **State management** - Database tracks everything

## Timeline Estimate

- **Phase 1 (Database):** 30 minutes
- **Phase 2 (Installation):** 1 hour
- **Phase 3 (Integration):** 2 hours
- **Phase 4 (Dashboard):** 30 minutes
- **Phase 5 (Testing):** 1 hour

**Total:** ~5 hours for complete migration

## Next Steps

1. **Decide on database option** (NeonDB recommended)
2. **Start Phase 1** - Database setup
3. **Test incrementally** - Don't migrate everything at once
4. **Keep existing hooks running** - Dual system during transition
5. **Validate thoroughly** - Ensure no data loss

## Questions to Answer

1. **Database preference?**
   - NeonDB (cloud, free tier)
   - Docker (local, full control)
   - Local PostgreSQL (if installed)

2. **Integration strategy?**
   - Dual system (recommended)
   - Complete replacement

3. **Keep Langfuse/Neo4j?**
   - Yes, alongside orchestrator
   - Migrate to orchestrator only

Ready to proceed with Phase 1? 🚀
