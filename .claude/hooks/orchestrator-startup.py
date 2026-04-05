#!/usr/bin/env python3
"""
Orchestrator Startup Hook

This script runs at session start to check/start the TAC orchestrator.
It performs health checks and reports status to the user.

Usage:
  python orchestrator-startup.py [--start] [--check-only]

Options:
  --start       Start the orchestrator if not running
  --check-only  Only check status, don't start anything
"""

import subprocess
import sys
import os
import time
import json
import argparse
from pathlib import Path

# Configuration
TAC_ROOT = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws")
ORCH_ROOT = TAC_ROOT / "apps" / "orchestrator_3_stream"
BACKEND_PORT = 9403
FRONTEND_PORT = 5999
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"


def check_port(port: int) -> bool:
    """Check if a port is in use."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return f":{port}" in result.stdout and "LISTENING" in result.stdout
    except Exception:
        return False


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
        pass
    return {"status": "not_running", "error": str(e) if 'e' in dir() else "Connection failed"}


def check_frontend() -> bool:
    """Check if frontend is responding."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", FRONTEND_URL],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() == "200"
    except Exception:
        return False


def check_wsl() -> dict:
    """Check WSL status."""
    try:
        result = subprocess.run(
            ["wsl", "--status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        is_running = "Default Version: 2" in result.stdout or result.returncode == 0

        # Check if venv exists
        venv_check = subprocess.run(
            ["wsl", "bash", "-c", f"test -d /mnt/c/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream/backend/.venv && echo 'yes' || echo 'no'"],
            capture_output=True,
            text=True,
            timeout=10
        )
        venv_exists = "yes" in venv_check.stdout

        return {
            "installed": True,
            "running": is_running,
            "venv_exists": venv_exists
        }
    except FileNotFoundError:
        return {"installed": False, "running": False, "venv_exists": False}
    except Exception as e:
        return {"installed": True, "running": False, "error": str(e), "venv_exists": False}


def start_backend_wsl() -> bool:
    """Start backend in WSL."""
    print("Starting backend in WSL...")

    wsl_cmd = """
cd /mnt/c/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream
source backend/.venv/bin/activate
cd backend
export $(cat ../.env | grep -v '^#' | xargs)
nohup python main.py > /tmp/orchestrator-backend.log 2>&1 &
echo "Backend started with PID $!"
"""

    try:
        result = subprocess.run(
            ["wsl", "bash", "-c", wsl_cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print(f"WSL stderr: {result.stderr}")

        # Wait for backend to start
        for i in range(10):
            time.sleep(1)
            health = check_backend_health()
            if health.get("status") == "healthy":
                return True
        return False
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return False


def start_frontend() -> bool:
    """Start frontend in background."""
    print("Starting frontend...")

    frontend_dir = ORCH_ROOT / "frontend"

    try:
        # Use subprocess.Popen for background process
        process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--port", str(FRONTEND_PORT)],
            cwd=str(frontend_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )

        # Wait for frontend to start
        for i in range(10):
            time.sleep(1)
            if check_frontend():
                return True
        return False
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return False


def setup_wsl_venv() -> bool:
    """Set up Python virtual environment in WSL."""
    print("Setting up WSL Python environment...")

    setup_cmd = """
cd /mnt/c/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/apps/orchestrator_3_stream/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "WSL environment setup complete"
"""

    try:
        result = subprocess.run(
            ["wsl", "bash", "-c", setup_cmd],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for pip install
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to setup WSL environment: {e}")
        return False


def print_status_report(backend_health: dict, frontend_ok: bool, wsl_status: dict):
    """Print formatted status report."""
    print("\n" + "=" * 60)
    print("ORCHESTRATOR STATUS REPORT")
    print("=" * 60)

    # Backend status
    backend_ok = backend_health.get("status") == "healthy"
    print(f"\nBackend (port {BACKEND_PORT}):")
    if backend_ok:
        ws_conns = backend_health.get("websocket_connections", 0)
        print(f"  Status: HEALTHY")
        print(f"  WebSocket Connections: {ws_conns}")
    else:
        print(f"  Status: NOT RUNNING")
        if "error" in backend_health:
            print(f"  Error: {backend_health['error']}")

    # Frontend status
    print(f"\nFrontend (port {FRONTEND_PORT}):")
    print(f"  Status: {'RUNNING' if frontend_ok else 'NOT RUNNING'}")
    if frontend_ok:
        print(f"  URL: {FRONTEND_URL}")

    # WSL status
    print(f"\nWSL Environment:")
    if wsl_status.get("installed"):
        print(f"  Installed: Yes")
        print(f"  Running: {'Yes' if wsl_status.get('running') else 'No'}")
        print(f"  Python venv: {'Ready' if wsl_status.get('venv_exists') else 'NOT SET UP'}")
    else:
        print(f"  Installed: No (REQUIRED for orchestrator)")

    # Overall status
    print("\n" + "-" * 60)
    if backend_ok and frontend_ok:
        print("OVERALL: READY")
        print(f"Open {FRONTEND_URL} to use the orchestrator")
    elif not wsl_status.get("installed"):
        print("OVERALL: WSL NOT INSTALLED")
        print("Run: wsl --install")
    elif not wsl_status.get("venv_exists"):
        print("OVERALL: WSL ENVIRONMENT NOT SET UP")
        print("Run: orchestrator-startup.py --setup-wsl")
    else:
        print("OVERALL: NOT READY")
        print("Run: orchestrator-startup.py --start")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Orchestrator Startup Hook")
    parser.add_argument("--start", action="store_true", help="Start orchestrator if not running")
    parser.add_argument("--check-only", action="store_true", help="Only check status")
    parser.add_argument("--setup-wsl", action="store_true", help="Set up WSL Python environment")
    args = parser.parse_args()

    # Check current status
    backend_health = check_backend_health()
    frontend_ok = check_frontend()
    wsl_status = check_wsl()

    # Setup WSL if requested
    if args.setup_wsl:
        if not wsl_status.get("installed"):
            print("ERROR: WSL is not installed. Run 'wsl --install' first.")
            sys.exit(1)
        setup_wsl_venv()
        wsl_status = check_wsl()  # Re-check

    # Start if requested
    if args.start and not args.check_only:
        if backend_health.get("status") != "healthy":
            if not wsl_status.get("venv_exists"):
                print("WSL environment not set up. Running setup...")
                setup_wsl_venv()
                wsl_status = check_wsl()

            if start_backend_wsl():
                backend_health = check_backend_health()
            else:
                print("Failed to start backend")

        if not frontend_ok:
            if start_frontend():
                frontend_ok = True
            else:
                print("Failed to start frontend")

    # Print status report
    print_status_report(backend_health, frontend_ok, wsl_status)

    # Exit code
    if backend_health.get("status") == "healthy" and frontend_ok:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
