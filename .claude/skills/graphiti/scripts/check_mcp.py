#!/usr/bin/env python3
"""Check MCP server connectivity and configuration."""

import json
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_DIR = Path("C:/Users/gblac/OneDrive/Desktop/afs/nci-oa-agent")
MCP_URL = "http://localhost:8000/mcp/"
HEALTH_URL = "http://localhost:8000/health"


def main():
    print("MCP Server Check")
    print("=" * 40)
    print()

    # Check .mcp.json configuration
    print("Configuration:")
    print("-" * 40)

    mcp_file = PROJECT_DIR / ".mcp.json"
    if mcp_file.exists():
        with open(mcp_file) as f:
            config = json.load(f)

        if "graphiti" in config.get("mcpServers", {}):
            print("[OK] Graphiti configured in .mcp.json")
            server = config["mcpServers"]["graphiti"]
            print(f"     Command: {server.get('command')}")
            print(f"     Args: {server.get('args')}")
        else:
            print("[ERROR] Graphiti not in .mcp.json")
    else:
        print(f"[ERROR] .mcp.json not found at {mcp_file}")

    print()
    print("Connectivity:")
    print("-" * 40)

    # Check health endpoint
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"[OK] Health endpoint: HTTP {response.status}")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Health endpoint: HTTP {e.code}")
    except urllib.error.URLError as e:
        print(f"[ERROR] Health endpoint unreachable: {e.reason}")
    except TimeoutError:
        print("[ERROR] Health endpoint timed out")

    # Check MCP endpoint
    try:
        req = urllib.request.Request(MCP_URL, method="POST")
        req.add_header("Content-Type", "application/json")
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }).encode()

        with urllib.request.urlopen(req, data=data, timeout=10) as response:
            body = response.read().decode()
            print(f"[OK] MCP endpoint: HTTP {response.status}")

            try:
                result = json.loads(body)
                if "result" in result and "tools" in result["result"]:
                    tools = result["result"]["tools"]
                    print(f"     Available tools: {len(tools)}")
                    for tool in tools:
                        print(f"       - {tool.get('name', 'unknown')}")
            except json.JSONDecodeError:
                print(f"     Response: {body[:100]}...")

    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"[ERROR] MCP endpoint: HTTP {e.code}")
        if body:
            print(f"     Response: {body[:200]}")
    except urllib.error.URLError as e:
        print(f"[ERROR] MCP endpoint unreachable: {e.reason}")
        print()
        print("The MCP server may not be running. Start it with:")
        print("  cd C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server")
        print("  docker compose -f docker/docker-compose.yml up -d")
    except TimeoutError:
        print("[ERROR] MCP endpoint timed out")

    print()


if __name__ == "__main__":
    main()
