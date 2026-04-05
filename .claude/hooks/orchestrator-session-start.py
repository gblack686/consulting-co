#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Orchestrator Session Start Hook

Automatically checks the TAC Multi-Agent Orchestrator status at session start.
Logs status to timestamped file in the skill logs directory.

Usage (as hook): Runs automatically at session start
Usage (manual): python orchestrator-session-start.py --check-only
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
TAC_ROOT = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws")
ORCH_ROOT = TAC_ROOT / "apps" / "orchestrator_3_stream"
BACKEND_PORT = 9403
FRONTEND_PORT = 5999
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

# Log directory
SKILL_DIR = Path(__file__).parent.parent / "skills" / "multi-agent-orchestrator-administration"
LOG_DIR = SKILL_DIR / "logs"


def check_backend_health() -> dict:
    """Check backend health endpoint."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{BACKEND_URL}/health"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        return {"status": "not_running", "error": str(e)}
    return {"status": "not_running", "error": "Connection failed"}


def check_frontend() -> dict:
    """Check if frontend is responding."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", FRONTEND_URL],
            capture_output=True,
            text=True,
            timeout=5
        )
        http_code = result.stdout.strip()
        if http_code == "200":
            return {"status": "running", "http_code": 200}
        return {"status": "error", "http_code": int(http_code) if http_code.isdigit() else 0}
    except Exception as e:
        return {"status": "not_running", "error": str(e)}


def check_wsl() -> dict:
    """Check WSL status."""
    try:
        result = subprocess.run(
            ["wsl", "--list", "--verbose"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "Ubuntu" in line and "Running" in line:
                    return {"status": "running", "distribution": "Ubuntu", "version": 2}
            return {"status": "stopped", "distribution": "Ubuntu"}
        return {"status": "not_installed"}
    except FileNotFoundError:
        return {"status": "not_installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_claude_cli() -> dict:
    """Check Claude CLI version in WSL."""
    try:
        result = subprocess.run(
            ["wsl", "bash", "-c", "~/.local/bin/claude --version 2>/dev/null || /usr/local/bin/claude --version 2>/dev/null || echo 'not found'"],
            capture_output=True,
            text=True,
            timeout=10
        )
        version = result.stdout.strip()
        if "not found" in version:
            return {"status": "not_installed"}
        return {"status": "installed", "version": version}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def generate_status_report() -> dict:
    """Generate complete status report."""
    backend = check_backend_health()
    frontend = check_frontend()
    wsl = check_wsl()
    claude_cli = check_claude_cli()

    backend_ok = backend.get("status") == "healthy"
    frontend_ok = frontend.get("status") == "running"
    wsl_ok = wsl.get("status") == "running"

    overall = "FULLY_OPERATIONAL" if (backend_ok and frontend_ok) else "DEGRADED" if (backend_ok or frontend_ok) else "DOWN"

    return {
        "timestamp": datetime.now().isoformat(),
        "overall_status": overall,
        "components": {
            "backend": {
                "status": "HEALTHY" if backend_ok else "DOWN",
                "port": BACKEND_PORT,
                "details": backend
            },
            "frontend": {
                "status": "RUNNING" if frontend_ok else "DOWN",
                "port": FRONTEND_PORT,
                "url": FRONTEND_URL,
                "details": frontend
            },
            "wsl": {
                "status": "RUNNING" if wsl_ok else "STOPPED",
                "details": wsl
            },
            "claude_cli": claude_cli
        },
        "urls": {
            "frontend": FRONTEND_URL,
            "backend_api": BACKEND_URL,
            "health_check": f"{BACKEND_URL}/health",
            "websocket": f"ws://127.0.0.1:{BACKEND_PORT}/ws"
        }
    }


def save_log(report: dict) -> Path:
    """Save status report to timestamped log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"{timestamp}_status_report.md"

    # Generate markdown report
    backend = report["components"]["backend"]
    frontend = report["components"]["frontend"]
    wsl = report["components"]["wsl"]
    claude_cli = report["components"]["claude_cli"]

    backend_status = backend["status"]
    frontend_status = frontend["status"]
    wsl_status = wsl["status"]

    md_content = f"""# Orchestrator Status Report
**Generated:** {report['timestamp']}

## Summary

| Component | Status | Details |
|-----------|--------|---------|
| Backend | {'OK' if backend_status == 'HEALTHY' else 'DOWN'} {backend_status} | Port {backend['port']}, {backend['details'].get('websocket_connections', 0)} WebSocket connections |
| Frontend | {'OK' if frontend_status == 'RUNNING' else 'DOWN'} {frontend_status} | Port {frontend['port']}, HTTP {frontend['details'].get('http_code', 'N/A')} |
| WSL | {'OK' if wsl_status == 'RUNNING' else 'STOPPED'} {wsl_status} | {wsl['details'].get('distribution', 'Unknown')}, Version {wsl['details'].get('version', 'Unknown')} |
| Claude CLI | {'OK' if claude_cli.get('status') == 'installed' else 'MISSING'} | {claude_cli.get('version', 'Not installed')} |

**Overall Status:** {'OK' if report['overall_status'] == 'FULLY_OPERATIONAL' else 'WARNING'} {report['overall_status']}

---

## URLs

- **Frontend:** {report['urls']['frontend']}
- **Backend API:** {report['urls']['backend_api']}
- **Health Check:** {report['urls']['health_check']}
- **WebSocket:** {report['urls']['websocket']}

---

## Raw Data

```json
{json.dumps(report, indent=2)}
```
"""

    log_file.write_text(md_content)
    return log_file


def format_status_summary(report: dict) -> str:
    """Format a concise status summary for hook output."""
    backend = report["components"]["backend"]
    frontend = report["components"]["frontend"]

    backend_ok = backend["status"] == "HEALTHY"
    frontend_ok = frontend["status"] == "RUNNING"

    if backend_ok and frontend_ok:
        ws_conns = backend["details"].get("websocket_connections", 0)
        return f"Orchestrator: READY (Backend OK, Frontend OK, {ws_conns} WS connections)"
    elif backend_ok:
        return f"Orchestrator: PARTIAL (Backend OK, Frontend DOWN)"
    elif frontend_ok:
        return f"Orchestrator: PARTIAL (Backend DOWN, Frontend OK)"
    else:
        return "Orchestrator: DOWN (Backend and Frontend not running)"


def main():
    try:
        # Check if running as hook (stdin has JSON) or standalone
        import select

        is_hook = False
        input_data = {}

        # Try to read stdin if available (hook mode)
        if not sys.stdin.isatty():
            try:
                stdin_content = sys.stdin.read()
                if stdin_content.strip():
                    input_data = json.loads(stdin_content)
                    is_hook = True
            except json.JSONDecodeError:
                pass

        # Generate status report
        report = generate_status_report()

        # Save log
        log_file = save_log(report)

        # Generate summary
        summary = format_status_summary(report)

        if is_hook:
            # Hook mode: output JSON response
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": f"{summary}\nLog saved to: {log_file.name}"
                }
            }
            print(json.dumps(output))
        else:
            # Standalone mode: print human-readable output
            print(f"\n{summary}")
            print(f"Log saved to: {log_file}")

        sys.exit(0)

    except Exception as e:
        # Handle errors gracefully
        if '--debug' in sys.argv:
            raise
        sys.exit(0)


if __name__ == '__main__':
    main()
