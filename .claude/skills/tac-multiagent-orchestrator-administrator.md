# Multi-Agent Orchestration Administration Skill

## Skill Metadata
- **Name:** orchestrator-administration
- **Version:** 1.2.0
- **Description:** Comprehensive administration, diagnostic testing, and management for the TAC Orchestrator-Agent-with-ADWS application
- **Author:** Claude Code
- **Created:** 2026-01-11
- **Updated:** 2026-01-15

## Purpose

This skill provides administrative capabilities for the multi-agent orchestration platform, including:
- **Diagnostics** - Systematic testing to identify configuration and runtime issues
- **Management** - Start, stop, and configure orchestrator components
- **Monitoring** - Check health, logs, and performance metrics
- **Maintenance** - Database operations, cleanup, and updates

## Application Context

**Target Application:** `C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws\apps\orchestrator_3_stream`

**Architecture:**
- **Frontend:** Vue 3 + TypeScript (Port 5999)
- **Backend:** FastAPI + Python 3.12 (Port 9403)
- **Database:** PostgreSQL (Supabase)
- **Agent SDK:** Claude Agent SDK (subprocess-based)

## Usage

```bash
# Start orchestrator (backend + frontend)
claude /orchestrator-administration start

# Stop orchestrator
claude /orchestrator-administration stop

# Check status
claude /orchestrator-administration status

# Run full diagnostic suite
claude /orchestrator-administration diagnose

# Run specific diagnostic category
claude /orchestrator-administration diagnose --category environment

# View logs
claude /orchestrator-administration logs

# Generate diagnostic report only (no fixes)
claude /orchestrator-administration diagnose --report-only

# Run with verbose output
claude /orchestrator-administration --verbose
```

## Administrative Commands

### Start/Stop Management

**Start Backend:**
```bash
cd C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws\apps\orchestrator_3_stream
uv run uvicorn backend.main:app --host 127.0.0.1 --port 9403
```

**Start Frontend:**
```bash
cd C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws\apps\orchestrator_3_stream\frontend
npm run dev -- --port 5999
```

**Stop Processes:**
```bash
# Find and kill specific PIDs rather than blanket kills
netstat -ano | findstr :9403  # Find backend PID
netstat -ano | findstr :5999  # Find frontend PID
taskkill /PID <pid> /F
```

### Health Checks

**Backend Health:**
```bash
curl -s http://127.0.0.1:9403/health | jq .
```

**Frontend Status:**
```bash
curl -s http://127.0.0.1:5999 > /dev/null && echo "Frontend OK" || echo "Frontend DOWN"
```

**WebSocket Connection:**
```bash
# Test WebSocket handshake
websocat ws://127.0.0.1:9403/ws --text --one-message --ping-interval 1
```

## Diagnostic Test Suite

### Test Categories

1. **Environment Tests** - Verify prerequisites and configuration
2. **Database Tests** - Check PostgreSQL connectivity and schema
3. **Backend Tests** - Validate FastAPI server and endpoints
4. **Frontend Tests** - Verify Vue app and WebSocket connection
5. **Claude SDK Tests** - Test Claude Code CLI and subprocess spawning
6. **Integration Tests** - End-to-end message flow testing

## Execution Steps

When invoked, this skill will:

1. **Initialize Diagnostics**
   - Set working directory to orchestrator app
   - Create timestamped diagnostic session
   - Initialize result tracking

2. **Run Test Categories Sequentially**
   - Execute each test category
   - Collect pass/fail results
   - Capture error details and logs
   - Generate category summary

3. **Generate Diagnostic Report**
   - Summarize all test results
   - Identify root cause candidates
   - Provide recommended fixes
   - Save report to `.claude/diagnostics/`

4. **Present Findings**
   - Display summary in terminal
   - Highlight critical issues
   - Suggest next steps

## Test Specifications

### 1. Environment Tests

**Test 1.1: Python Version**
```python
import sys
required = "3.12"
current = f"{sys.version_info.major}.{sys.version_info.minor}"
assert current >= required, f"Python {required}+ required, got {current}"
```

**Test 1.2: Node.js Version**
```bash
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
[[ $node_version -ge 18 ]] || echo "FAIL: Node 18+ required"
```

**Test 1.3: Required Binaries**
- `uv` - Python package manager
- `npm` - Node package manager
- `claude` - Claude Code CLI
- `git` - Version control

**Test 1.4: Environment Variables**
- `ANTHROPIC_API_KEY` - Present and valid format
- `DATABASE_URL` - Present and valid PostgreSQL connection string
- `CLAUDECODE` - Should be "1" (running inside Claude Code)

**Test 1.5: Git Aliases**
```bash
# Check for 'claude' git alias that might interfere
git config --global --get-regexp "alias.claude"
```

### 2. Database Tests

**Test 2.1: Connection**
```python
import asyncpg
conn = await asyncpg.connect(DATABASE_URL)
await conn.close()
```

**Test 2.2: Schema Validation**
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'orchestrator_agents', 'agents', 'prompts',
  'agent_logs', 'system_logs', 'orchestrator_chat'
);
```

**Test 2.3: Orchestrator Record**
```sql
SELECT id, session_id, status, created_at
FROM orchestrator_agents
WHERE archived = false
ORDER BY created_at DESC LIMIT 1;
```

**Test 2.4: Chat History Count**
```sql
SELECT COUNT(*) as message_count
FROM orchestrator_chat;
```

### 3. Backend Tests

**Test 3.1: Port Availability**
```bash
netstat -ano | findstr :9403 || echo "Port 9403 available"
```

**Test 3.2: Process Running**
```bash
wmic process where "commandline like '%uvicorn%main:app%'" get processid,commandline
```

**Test 3.3: Health Endpoint**
```bash
curl -s http://127.0.0.1:9403/health | jq .
```

**Test 3.4: Orchestrator Metadata**
```bash
curl -s http://127.0.0.1:9403/get_orchestrator | jq .
```

**Test 3.5: Backend Logs**
```bash
# Check for errors in latest log
tail -100 backend/logs/$(ls -t backend/logs/ | head -1) | grep -i error
```

**Test 3.6: Claude SDK Import**
```python
import claude_agent_sdk
print(f"SDK Version: {claude_agent_sdk.__version__}")
```

### 4. Frontend Tests

**Test 4.1: Port Availability**
```bash
netstat -ano | findstr :5999 || echo "Port 5999 available"
```

**Test 4.2: Process Running**
```bash
wmic process where "commandline like '%vite%'" get processid,commandline
```

**Test 4.3: HTTP Response**
```bash
curl -s http://127.0.0.1:5999 | grep -q "Multi-Agent Orchestration"
```

**Test 4.4: WebSocket Connection**
```bash
# Attempt WebSocket handshake
websocat ws://127.0.0.1:9403/ws --text --one-message --ping-interval 1
```

**Test 4.5: Console Errors**
```javascript
// Check for console errors (via Chrome DevTools MCP if available)
// Look for CORS, WebSocket, or API errors
```

### 5. Claude SDK Tests

**Test 5.1: Claude CLI Location**
```python
import shutil
claude_path = shutil.which('claude')
assert claude_path, "Claude CLI not found in PATH"
print(f"Claude CLI: {claude_path}")
```

**Test 5.2: Claude Version**
```bash
claude --version
```

**Test 5.3: Basic Subprocess Spawn**
```python
import subprocess
result = subprocess.run(['claude', '--version'],
                       capture_output=True, text=True, timeout=5)
assert result.returncode == 0, f"Failed: {result.stderr}"
```

**Test 5.4: Subprocess with SDK Flags**
```python
import subprocess
result = subprocess.run([
    'claude',
    '--output-format', 'stream-json',
    '--verbose',
    '--system-prompt', 'Test prompt',
    '--model', 'claude-haiku-4-5-20251001'
], capture_output=True, text=True, timeout=3, input='test\n')
# Note: This might fail or hang - that's what we're diagnosing
```

**Test 5.5: Claude Agent SDK Client Init**
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
options = ClaudeAgentOptions(
    system_prompt="Test",
    model="claude-haiku-4-5-20251001",
    cwd="."
)
async with ClaudeSDKClient(options=options) as client:
    print("SDK client initialized")
```

**Test 5.6: Environment in Subprocess**
```python
import subprocess
import os
# Test if subprocess inherits ANTHROPIC_API_KEY
env = os.environ.copy()
result = subprocess.run(
    ['python', '-c', 'import os; print("ANTHROPIC_API_KEY" in os.environ)'],
    env=env, capture_output=True, text=True
)
```

### 6. Integration Tests

**Test 6.1: End-to-End Message Flow**
```python
# Send test message via API
import httpx
response = httpx.post('http://127.0.0.1:9403/send_chat', json={
    'message': 'test',
    'orchestrator_agent_id': '<orchestrator_id>'
})
assert response.status_code == 200
```

**Test 6.2: WebSocket Message Receipt**
```python
import asyncio
import websockets

async def test_ws():
    async with websockets.connect('ws://127.0.0.1:9403/ws') as ws:
        message = await asyncio.wait_for(ws.recv(), timeout=2)
        print(f"Received: {message}")

asyncio.run(test_ws())
```

**Test 6.3: Database Persistence**
```sql
-- Check if test message was saved
SELECT sender_type, message, created_at
FROM orchestrator_chat
ORDER BY created_at DESC
LIMIT 1;
```

## Configuration Files

### Environment (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://postgres.xxx:password@aws-0-us-west-1.pooler.supabase.com:5432/postgres
BACKEND_HOST=127.0.0.1
BACKEND_PORT=9403
FRONTEND_HOST=127.0.0.1
FRONTEND_PORT=5999
VITE_API_BASE_URL=http://127.0.0.1:9403
WEBSOCKET_URL=ws://127.0.0.1:9403/ws
CORS_ORIGINS=http://127.0.0.1:5999,http://localhost:5999
```

## Implementation Notes

### File Structure
```
.claude/
├── skills/
│   └── orchestrator-administration.md  # This file
├── diagnostics/
│   ├── diag_20260111_114730.md          # Generated reports
│   └── latest.md                         # Symlink to latest report
└── scripts/
    └── run_orchestrator_diagnostics.py   # Test runner
```

### Dependencies
- Python 3.12+
- asyncpg (database testing)
- httpx (HTTP testing)
- websockets (WebSocket testing)
- Chrome DevTools MCP (frontend testing)

## Cost & Context Updates

### How Cost/Context Updates Work

Cost and context (token) updates happen **at the end of each orchestrator turn**, not during streaming. This is by design.

**Data Flow:**
```
Backend (orchestrator_service.py)
    ↓ POST-EXECUTION (after response completes)
    ↓ update_orchestrator_costs()
    ↓
Database (update_orchestrator_costs in database.py)
    ↓ Returns updated totals
    ↓
WebSocket (broadcast_orchestrator_updated)
    ↓ {"type": "orchestrator_updated", "orchestrator": {...}}
    ↓
Frontend (chatService.ts → orchestratorStore.ts)
    ↓ handleOrchestratorUpdated()
    ↓
UI (AppHeader.vue, ChatPanel.vue)
    ↓ Displays updated cost/context
```

### Key Code Locations

| Component | File | Lines |
|-----------|------|-------|
| Cost calculation | `backend/modules/orchestrator_service.py` | 964-1012 |
| Database update | `backend/modules/database.py` | `update_orchestrator_costs()` |
| WebSocket broadcast | `backend/modules/websocket_manager.py` | 162-166 |
| Frontend handler | `frontend/src/stores/orchestratorStore.ts` | 952-970 |
| Header display | `frontend/src/components/AppHeader.vue` | stat-pill Cost |
| Chat panel display | `frontend/src/components/ChatPanel.vue` | O-Agent header |

### Verifying Updates Are Working

**1. Check Browser Console:**
```javascript
// Should see after each turn completes:
"Orchestrator updated:" {orchestrator: {...}}
"✅ Updated orchestrator cost: $X.XXXX | Tokens: XXXXX"
```

**2. Check Backend Logs:**
```
✅ Updated orchestrator costs successfully:
   Rows Updated: 1
   Orchestrator ID: <uuid>
   New Total Tokens: XXXXX
   New Total Cost: $X.XXXXXX
📡 Broadcast orchestrator cost update via WebSocket
```

**3. Use Chrome DevTools MCP:**
```bash
# List console messages
mcp__chrome-devtools__list_console_messages
# Look for "Orchestrator updated:" entries
```

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Cost shows $0.00 | No messages sent yet | Send a test message |
| Cost not updating during stream | By design | Updates happen after turn completes |
| No "Orchestrator updated:" in console | WebSocket not connected | Check connection status indicator |
| Backend not broadcasting | `update_result.get("success")` is False | Check database logs |

### Token Pricing Reference

| Model | Input (per 1M) | Output (per 1M) |
|-------|----------------|-----------------|
| Claude Haiku 4.5 | $0.25 | $1.25 |
| Claude Sonnet 4 | $3.00 | $15.00 |
| Claude Opus 4 | $15.00 | $75.00 |

Cost calculation: `(input_tokens × rate / 1M) + (output_tokens × rate / 1M)`

## Success Criteria

A successful administration run should:
1. Execute all requested operations
2. Generate comprehensive logs/reports when applicable
3. Identify issues or confirm healthy status
4. Provide actionable recommendations
5. Save results for comparison across runs

## Version History

- **v1.2.0** (2026-01-15) - Added Cost & Context Updates documentation
  - Data flow diagram from backend to UI
  - Key code locations reference table
  - Verification steps using console and Chrome DevTools MCP
  - Common issues troubleshooting table
  - Token pricing reference
- **v1.1.0** (2026-01-15) - Renamed from troubleshooting to administration
  - Added management commands (start/stop/status)
  - Updated ports to match current configuration (5999/9403)
  - Added Windows-specific commands
- **v1.0.0** (2026-01-11) - Initial diagnostic suite creation
  - 6 test categories
  - 26 individual tests
  - Comprehensive reporting format
