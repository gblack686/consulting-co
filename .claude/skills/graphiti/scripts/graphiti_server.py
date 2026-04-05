#!/usr/bin/env python3
"""Graphiti MCP Server management script."""

import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

GRAPHITI_DIR = Path("C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server")
COMPOSE_FILE = GRAPHITI_DIR / "docker" / "docker-compose-falkordb.yml"
HEALTH_URL = "http://localhost:8000/health"
MCP_URL = "http://localhost:8000/mcp/"


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=True if sys.platform == "win32" else False,
    )
    return result.returncode, result.stdout, result.stderr


def check_health() -> bool:
    """Check if server is healthy."""
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def start_server():
    """Start the Graphiti MCP server."""
    print("Starting Graphiti MCP server...")

    if check_health():
        print("Server is already running!")
        return True

    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"]
    code, stdout, stderr = run_command(cmd, cwd=GRAPHITI_DIR)

    if code != 0:
        print(f"Failed to start server: {stderr}")
        return False

    print("Waiting for server to be ready...")
    for i in range(30):
        time.sleep(2)
        if check_health():
            print(f"Server is ready! (took {(i+1)*2}s)")
            print(f"MCP endpoint: {MCP_URL}")
            return True
        print(f"  Waiting... ({(i+1)*2}s)")

    print("Server failed to become healthy within 60s")
    return False


def stop_server():
    """Stop the Graphiti MCP server."""
    print("Stopping Graphiti MCP server...")

    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), "down"]
    code, stdout, stderr = run_command(cmd, cwd=GRAPHITI_DIR)

    if code != 0:
        print(f"Failed to stop server: {stderr}")
        return False

    print("Server stopped.")
    return True


def server_status():
    """Check server status."""
    print("Checking Graphiti MCP server status...")
    print()

    # Check Docker containers
    cmd = ["docker", "ps", "--filter", "name=graphiti", "--format", "{{.Names}}\t{{.Status}}"]
    code, stdout, stderr = run_command(cmd)

    if stdout.strip():
        print("Docker containers:")
        for line in stdout.strip().split("\n"):
            print(f"  {line}")
    else:
        print("Docker containers: None running")
    print()

    # Check health endpoint
    if check_health():
        print(f"Health endpoint ({HEALTH_URL}): OK")
    else:
        print(f"Health endpoint ({HEALTH_URL}): UNREACHABLE")
    print()

    # Check MCP endpoint
    try:
        req = urllib.request.Request(MCP_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"MCP endpoint ({MCP_URL}): OK (status {response.status})")
    except urllib.error.HTTPError as e:
        # 405 is expected for GET on MCP endpoint
        if e.code == 405:
            print(f"MCP endpoint ({MCP_URL}): OK (method not allowed, but reachable)")
        else:
            print(f"MCP endpoint ({MCP_URL}): Error {e.code}")
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"MCP endpoint ({MCP_URL}): UNREACHABLE - {e}")


def show_logs():
    """Show server logs."""
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), "logs", "--tail", "100"]
    code, stdout, stderr = run_command(cmd, cwd=GRAPHITI_DIR)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr)


def main():
    if len(sys.argv) < 2:
        print("Usage: graphiti_server.py [start|stop|status|logs]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        success = start_server()
        sys.exit(0 if success else 1)
    elif command == "stop":
        success = stop_server()
        sys.exit(0 if success else 1)
    elif command == "status":
        server_status()
    elif command == "logs":
        show_logs()
    else:
        print(f"Unknown command: {command}")
        print("Usage: graphiti_server.py [start|stop|status|logs]")
        sys.exit(1)


if __name__ == "__main__":
    main()
