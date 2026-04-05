#!/usr/bin/env python3
"""Comprehensive Graphiti MCP server troubleshooting script."""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

GRAPHITI_DIR = Path("C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server")
PROJECT_DIR = Path("C:/Users/gblac/OneDrive/Desktop/afs/nci-oa-agent")

CHECKS = []
WARNINGS = []
ERRORS = []


def print_header(title: str):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    print()
    print(f"--- {title} ---")


def ok(msg: str):
    CHECKS.append(("OK", msg))
    print(f"  [OK] {msg}")


def warn(msg: str):
    WARNINGS.append(msg)
    print(f"  [WARN] {msg}")


def error(msg: str):
    ERRORS.append(msg)
    print(f"  [ERROR] {msg}")


def info(msg: str):
    print(f"  [INFO] {msg}")


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True if sys.platform == "win32" else False,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_docker():
    """Check Docker installation and status."""
    print_section("Docker")

    # Check Docker CLI
    code, stdout, stderr = run_cmd(["docker", "--version"])
    if code == 0:
        ok(f"Docker installed: {stdout.strip()}")
    else:
        error("Docker not installed or not in PATH")
        return False

    # Check Docker daemon
    code, stdout, stderr = run_cmd(["docker", "info"])
    if code == 0:
        ok("Docker daemon is running")
    else:
        error("Docker daemon not running. Start Docker Desktop.")
        return False

    # Check Docker Compose
    code, stdout, stderr = run_cmd(["docker", "compose", "version"])
    if code == 0:
        ok(f"Docker Compose: {stdout.strip()}")
    else:
        error("Docker Compose not available")
        return False

    return True


def check_containers():
    """Check Graphiti container status."""
    print_section("Containers")

    code, stdout, stderr = run_cmd(["docker", "ps", "-a", "--filter", "name=graphiti", "--format", "json"])

    if code != 0:
        error(f"Failed to list containers: {stderr}")
        return False

    if not stdout.strip():
        warn("No Graphiti containers found. Server may not have been started.")
        return False

    for line in stdout.strip().split("\n"):
        if line:
            container = json.loads(line)
            name = container.get("Names", "unknown")
            state = container.get("State", "unknown")
            status = container.get("Status", "unknown")

            if state == "running":
                ok(f"Container {name}: {status}")
            else:
                error(f"Container {name}: {state} - {status}")
                return False

    return True


def check_ports():
    """Check required ports."""
    print_section("Ports")

    ports = [
        (8000, "MCP Server HTTP"),
        (6379, "FalkorDB/Redis"),
        (3000, "FalkorDB Web UI"),
    ]

    all_ok = True
    for port, desc in ports:
        code, stdout, stderr = run_cmd(["netstat", "-an"])
        if f":{port}" in stdout or f".{port}" in stdout:
            info(f"Port {port} ({desc}): In use")
        else:
            info(f"Port {port} ({desc}): Available")

    return all_ok


def check_health_endpoint():
    """Check MCP server health endpoint."""
    print_section("Health Endpoint")

    try:
        req = urllib.request.Request("http://localhost:8000/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            ok(f"Health endpoint: HTTP {response.status}")
            return True
    except urllib.error.HTTPError as e:
        error(f"Health endpoint returned HTTP {e.code}")
        return False
    except urllib.error.URLError as e:
        error(f"Cannot connect to health endpoint: {e.reason}")
        return False
    except TimeoutError:
        error("Health endpoint timed out")
        return False


def check_mcp_endpoint():
    """Check MCP endpoint."""
    print_section("MCP Endpoint")

    try:
        req = urllib.request.Request("http://localhost:8000/mcp/", method="POST")
        req.add_header("Content-Type", "application/json")
        # Send a minimal JSON-RPC request
        data = json.dumps({"jsonrpc": "2.0", "method": "ping", "id": 1}).encode()
        with urllib.request.urlopen(req, data=data, timeout=10) as response:
            ok(f"MCP endpoint responding: HTTP {response.status}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 400:
            # Bad request might mean server is up but request format wrong
            warn(f"MCP endpoint reachable but returned {e.code} (may be expected)")
            return True
        error(f"MCP endpoint error: HTTP {e.code}")
        return False
    except urllib.error.URLError as e:
        error(f"Cannot connect to MCP endpoint: {e.reason}")
        return False
    except TimeoutError:
        error("MCP endpoint timed out")
        return False


def check_env_vars():
    """Check required environment variables."""
    print_section("Environment Variables")

    # Check settings.local.json
    settings_file = PROJECT_DIR / ".claude" / "settings.local.json"
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
            env = settings.get("env", {})

            if env.get("OPENAI_API_KEY"):
                ok("OPENAI_API_KEY configured in settings.local.json")
            else:
                error("OPENAI_API_KEY not found in settings.local.json")

            if env.get("ANTHROPIC_API_KEY"):
                info("ANTHROPIC_API_KEY also available (can use as alternative)")
    else:
        error(f"Settings file not found: {settings_file}")

    # Check .env file
    env_file = GRAPHITI_DIR / ".env"
    if env_file.exists():
        ok(f"Graphiti .env file exists: {env_file}")
    else:
        warn(f"Graphiti .env file not found: {env_file}")


def check_mcp_config():
    """Check MCP configuration."""
    print_section("MCP Configuration")

    mcp_file = PROJECT_DIR / ".mcp.json"
    if mcp_file.exists():
        with open(mcp_file) as f:
            config = json.load(f)

        if "graphiti" in config.get("mcpServers", {}):
            ok("Graphiti MCP server configured in .mcp.json")
            server_config = config["mcpServers"]["graphiti"]
            info(f"  Command: {server_config.get('command')} {' '.join(server_config.get('args', []))}")
        else:
            error("Graphiti not found in .mcp.json mcpServers")
    else:
        error(f"MCP config not found: {mcp_file}")


def check_falkordb():
    """Check FalkorDB connectivity."""
    print_section("FalkorDB")

    # Try to ping Redis via docker exec
    code, stdout, stderr = run_cmd([
        "docker", "exec", "graphiti-mcp_server-graphiti-falkordb-1",
        "redis-cli", "-p", "6379", "ping"
    ])

    if code == 0 and "PONG" in stdout:
        ok("FalkorDB responding to ping")
        return True
    else:
        # Try alternate container name
        code, stdout, stderr = run_cmd([
            "docker", "exec", "mcp_server-graphiti-falkordb-1",
            "redis-cli", "-p", "6379", "ping"
        ])
        if code == 0 and "PONG" in stdout:
            ok("FalkorDB responding to ping")
            return True

        error(f"Cannot ping FalkorDB: {stderr or stdout}")
        return False


def print_summary():
    """Print troubleshooting summary."""
    print_header("SUMMARY")

    if ERRORS:
        print()
        print("ERRORS (must fix):")
        for e in ERRORS:
            print(f"  - {e}")

    if WARNINGS:
        print()
        print("WARNINGS (may need attention):")
        for w in WARNINGS:
            print(f"  - {w}")

    print()
    if not ERRORS:
        print("All critical checks passed!")
    else:
        print(f"Found {len(ERRORS)} error(s) and {len(WARNINGS)} warning(s)")
        print()
        print("SUGGESTED ACTIONS:")
        if any("Docker" in e for e in ERRORS):
            print("  1. Start Docker Desktop")
        if any("container" in e.lower() for e in ERRORS):
            print("  2. Start server: uv run .claude/skills/graphiti/scripts/graphiti_server.py start")
        if any("OPENAI_API_KEY" in e for e in ERRORS):
            print("  3. Add OPENAI_API_KEY to .claude/settings.local.json")


def main():
    print_header("GRAPHITI MCP SERVER TROUBLESHOOTING")

    check_docker()
    check_containers()
    check_ports()
    check_env_vars()
    check_mcp_config()
    check_health_endpoint()
    check_mcp_endpoint()
    check_falkordb()

    print_summary()

    sys.exit(1 if ERRORS else 0)


if __name__ == "__main__":
    main()
