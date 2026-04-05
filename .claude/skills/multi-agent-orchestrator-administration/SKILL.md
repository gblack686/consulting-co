# Multi-Agent Orchestrator Administration

## Skill Metadata
- **Name:** multi-agent-orchestrator-administration
- **Version:** 3.1.0
- **Description:** Start, stop, diagnose, and manage the TAC Multi-Agent Orchestrator
- **Author:** Claude Code
- **Created:** 2026-01-11
- **Updated:** 2026-01-16

## Overview

This skill manages the TAC Orchestrator which provides a multi-agent orchestration system with:
- Vue.js frontend for chat/agent management
- FastAPI backend with Claude Agent SDK
- PostgreSQL database (Supabase)
- WebSocket real-time communication

**Primary Location:** `.claude/orchestrator/orchestrator_3_stream/`
**Legacy Location:** `tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream/` (deprecated)

## Orchestrator Locations

### Current (Active)
```
.claude/orchestrator/orchestrator_3_stream/
├── .env                    # Environment configuration
├── backend/
│   ├── main.py             # FastAPI server
│   ├── logs/               # Backend logs
│   └── modules/            # Backend modules
└── frontend/
    └── src/                # Vue.js frontend
```

### Access URLs
- **Frontend:** http://127.0.0.1:5999
- **Backend API:** http://127.0.0.1:9403
- **Health Check:** http://127.0.0.1:9403/health
- **WebSocket:** ws://127.0.0.1:9403/ws

## Quick Start

### Start Backend (Windows)

```bash
cd ".claude/orchestrator/orchestrator_3_stream/backend"
python main.py
```

### Start Frontend (Windows)

```bash
cd ".claude/orchestrator/orchestrator_3_stream/frontend"
npm run dev -- --port 5999
```

### Health Check Script

```bash
python ".claude/skills/multi-agent-orchestrator-administration/scripts/orchestrator_health_check.py"
```

## Recent Critical Fix (2026-01-15)

### Issue: "Control request timeout: initialize"

The claude CLI in WSL was outdated (v1.0.35, needed v1.0.88+). This caused subprocess spawn failures.

### Solution Applied

1. Installed claude CLI v2.1.9 to `~/.local/bin/claude` in WSL:
   ```bash
   wsl bash -c "npm install -g @anthropic-ai/claude-code --prefix ~/.local"
   ```

2. Created `start_with_path.py` that prepends `~/.local/bin` to PATH before starting:
   ```python
   #!/usr/bin/env python3
   import os
   import sys
   from dotenv import load_dotenv

   # Prepend ~/.local/bin to PATH for updated claude CLI
   home = os.path.expanduser("~")
   local_bin = os.path.join(home, ".local", "bin")
   current_path = os.environ.get("PATH", "")
   os.environ["PATH"] = f"{local_bin}:{current_path}"

   script_dir = os.path.dirname(os.path.abspath(__file__))
   load_dotenv(os.path.join(script_dir, "..", ".env"))
   os.chdir(script_dir)
   os.execv(sys.executable, [sys.executable, os.path.join(script_dir, "main.py")])
   ```

### Verification
- `/ping` command executed successfully
- Response: "pong"
- Cost: $0.027

## Directory Structure

```
C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws\
├── .claude/
│   ├── agents/           # Agent templates (build-agent, planner, etc.)
│   ├── commands/         # Slash commands (/ping, /plan, /build, etc.)
│   └── skills/           # Skills
├── apps/
│   └── orchestrator_3_stream/
│       ├── .env          # Configuration (ports, API keys, database)
│       ├── backend/
│       │   ├── main.py
│       │   ├── start_with_path.py  # PATH-fixed startup script
│       │   ├── modules/
│       │   └── prompts/
│       └── frontend/
│           ├── .env      # Frontend env (VITE_API_BASE_URL)
│           └── src/
└── adws/                 # AI Developer Workflows
    └── adw_workflows/
```

## Configuration Files

### Backend .env (apps/orchestrator_3_stream/.env)
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

### Frontend .env (apps/orchestrator_3_stream/frontend/.env)
```bash
VITE_API_BASE_URL=http://127.0.0.1:9403
VITE_WEBSOCKET_URL=ws://127.0.0.1:9403/ws
```

## Diagnostic Commands

### Quick Status Check
```bash
# Check backend health
curl -s http://127.0.0.1:9403/health | jq .

# Check frontend
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5999

# Check WSL status
wsl --status
```

### Check Claude CLI Version in WSL
```bash
wsl bash -c "~/.local/bin/claude --version"
# Expected: 2.1.9 or higher
```

### Check SDK Version
```bash
wsl bash -c "source /mnt/c/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream/backend/.venv/bin/activate && pip show claude-agent-sdk"
# Expected: 0.1.19 or higher
```

### Find Processes on Ports
```bash
# Windows
netstat -ano | findstr ":9403"
netstat -ano | findstr ":5999"

# Kill by PID
taskkill /PID <pid> /F
```

## WSL Setup (One-Time)

### 1. Verify WSL Installation
```bash
wsl --status
# Should show: Default Version: 2
```

### 2. Update Claude CLI in WSL
```bash
wsl bash -c "npm install -g @anthropic-ai/claude-code --prefix ~/.local"
wsl bash -c "~/.local/bin/claude --version"
```

### 3. Create Python Virtual Environment
```bash
wsl bash -c "cd /mnt/c/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream/backend && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
```

### 4. Verify Dependencies
```bash
wsl bash -c "source /mnt/c/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream/backend/.venv/bin/activate && python -c 'import fastapi, uvicorn, asyncpg, claude_agent_sdk; print(\"All dependencies OK\")'"
```

## Troubleshooting

### Error: "The command line is too long"
- **Cause:** Windows command line limit exceeded by Claude Agent SDK
- **Solution:** Run backend in WSL (see Quick Start above)

### Error: "Control request timeout: initialize"
- **Cause:** Outdated claude CLI in WSL
- **Solution:** Update claude CLI to v2.1.9+:
  ```bash
  wsl bash -c "npm install -g @anthropic-ai/claude-code --prefix ~/.local"
  ```
- **Verify:** Use `start_with_path.py` to ensure PATH includes `~/.local/bin`

### Error: "Disconnected" in Frontend
- **Causes:**
  1. Backend not running
  2. CORS misconfiguration
  3. WebSocket connection failed
- **Fixes:**
  1. Check backend health: `curl http://127.0.0.1:9403/health`
  2. Verify CORS_ORIGINS in .env includes frontend port
  3. Refresh the browser page

### Error: Database Connection Failed
- **Cause:** Wrong password or network issue
- **Fix:** Get correct password from AWS Secrets Manager:
  ```bash
  aws secretsmanager get-secret-value --secret-id "gbautomation/supabase/unickqnwfheaczccvgbw/postgres_password" --query 'SecretString' --output text
  ```

## Code Pattern Reference (Claude Agent SDK)

### CORRECT Pattern
```python
# Store OPTIONS, not CLIENT instance
def __init__(self):
    self.client_options = ClaudeAgentOptions(
        system_prompt=prompt,
        model=model,
        cwd=working_dir
    )

# Create FRESH client for each query
async def execute(self):
    async with ClaudeSDKClient(options=self.client_options) as client:
        await client.query(message)
        async for response in client.receive_response():
            # Process response...
```

### INCORRECT Pattern (causes timeouts)
```python
# DON'T store client instance
def __init__(self):
    self.client = ClaudeSDKClient(options=options)  # Wrong!

# DON'T reuse stored client
async def execute(self):
    async with self.client:  # Causes timeout!
        await self.client.query(message)
```

## Architecture Notes

### Data Flow
```
User -> Frontend (Vue.js, port 5999)
         | WebSocket
       Backend (FastAPI, port 9403) [MUST RUN IN WSL]
         | Claude Agent SDK
       Claude Code subprocess (~/.local/bin/claude)
         | Anthropic API
       Response streams back via WebSocket
```

### Why WSL is Required on Windows

The Claude Agent SDK spawns Claude Code as a subprocess and communicates via stdin/stdout pipes. Windows has two issues:

1. **Command line length limit** (~8191 chars) - The system prompt exceeds this
2. **Subprocess I/O buffering** - Windows ProactorEventLoop has buffering issues with pipes

WSL uses Linux's SelectorEventLoop which handles pipes correctly.

## Administrator Scripts

### Health Check Script

Location: `scripts/orchestrator_health_check.py`

Comprehensive health verification that tests:
- Backend health endpoint
- Database connectivity (via backend)
- List agents endpoint
- WebSocket port accessibility
- Frontend availability
- Get orchestrator endpoint

**Usage:**
```bash
# Basic health check
python scripts/orchestrator_health_check.py

# Save results to log file
python scripts/orchestrator_health_check.py --save-log

# JSON output
python scripts/orchestrator_health_check.py --json

# Quick status only
python scripts/orchestrator_health_check.py --quiet
```

### Logs Directory

All health check and status logs are saved to:
`logs/`

Log files:
- `health_check_YYYYMMDD_HHMMSS.json` - JSON health check results
- `health_check_YYYYMMDD_HHMMSS.md` - Markdown health check report
- `YYYYMMDD_HHMMSS_status_report.md` - Session start status reports

## Startup Hook

This skill includes a session start hook that automatically:
1. Checks backend health on port 9403
2. Checks frontend on port 5999
3. Verifies WSL is installed and running
4. Checks Claude CLI version
5. Logs status to timestamped file in this skill's logs directory

See: `.claude/hooks/orchestrator-session-start.py`

The hook runs automatically when a Claude Code session starts in the consulting-co workspace.

## Authentication Configuration

### OAuth Token (Recommended - Claude Code Max)

The orchestrator uses Claude Code's internal OAuth authentication when no `ANTHROPIC_API_KEY` is set in the `.env` file. This is covered by the Claude Code Max subscription.

**Important:** Do NOT set `ANTHROPIC_API_KEY` in the orchestrator's `.env` file if you want to use the Max subscription billing.

## Related Files

- **This Skill:** `.claude/skills/multi-agent-orchestrator-administration/`
- **Scripts:** `.claude/skills/multi-agent-orchestrator-administration/scripts/`
- **Logs:** `.claude/skills/multi-agent-orchestrator-administration/logs/`
- **Session Start Hook:** `.claude/hooks/orchestrator-session-start.py`
- **Startup Helper:** `.claude/hooks/orchestrator-startup.py`
- **Orchestrator:** `.claude/orchestrator/orchestrator_3_stream/`
- **GitHub Repo:** https://github.com/gblack686/multi-agent-orchestrator-gb

## Contact & Resources

- **GitHub Issue (SDK):** https://github.com/anthropics/claude-agent-sdk-python/issues/208
- **SDK Repository:** https://github.com/anthropics/claude-agent-sdk-python
