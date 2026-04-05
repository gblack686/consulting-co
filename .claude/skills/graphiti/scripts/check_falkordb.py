#!/usr/bin/env python3
"""Check FalkorDB (Redis) connectivity."""

import subprocess
import sys


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
    except Exception as e:
        return -1, "", str(e)


def main():
    print("FalkorDB Check")
    print("=" * 40)
    print()

    # Find Graphiti container
    code, stdout, stderr = run_cmd([
        "docker", "ps", "--filter", "name=graphiti",
        "--format", "{{.Names}}"
    ])

    if code != 0 or not stdout.strip():
        print("[ERROR] No Graphiti container running")
        print()
        print("Start the server first:")
        print("  cd C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server")
        print("  docker compose -f docker/docker-compose.yml up -d")
        sys.exit(1)

    container = stdout.strip().split("\n")[0]
    print(f"Container: {container}")
    print()

    # Ping Redis
    print("Redis Connectivity:")
    print("-" * 40)

    code, stdout, stderr = run_cmd([
        "docker", "exec", container,
        "redis-cli", "-p", "6379", "ping"
    ])

    if code == 0 and "PONG" in stdout:
        print("[OK] Redis ping: PONG")
    else:
        print(f"[ERROR] Redis ping failed: {stderr or stdout}")
        sys.exit(1)

    # Get Redis info
    code, stdout, stderr = run_cmd([
        "docker", "exec", container,
        "redis-cli", "-p", "6379", "info", "server"
    ])

    if code == 0:
        for line in stdout.split("\n"):
            if line.startswith("redis_version:"):
                print(f"[OK] Redis version: {line.split(':')[1].strip()}")
            elif line.startswith("uptime_in_seconds:"):
                uptime = int(line.split(":")[1].strip())
                print(f"[OK] Uptime: {uptime // 60} minutes")

    # Check FalkorDB graph
    print()
    print("Graph Status:")
    print("-" * 40)

    code, stdout, stderr = run_cmd([
        "docker", "exec", container,
        "redis-cli", "-p", "6379", "GRAPH.LIST"
    ])

    if code == 0:
        graphs = [g.strip() for g in stdout.strip().split("\n") if g.strip() and not g.startswith("(")]
        if graphs:
            print(f"[OK] Graphs found: {len(graphs)}")
            for g in graphs[:5]:  # Show first 5
                print(f"     - {g}")
            if len(graphs) > 5:
                print(f"     ... and {len(graphs) - 5} more")
        else:
            print("[INFO] No graphs created yet (this is OK for new setup)")

    # Memory usage
    code, stdout, stderr = run_cmd([
        "docker", "exec", container,
        "redis-cli", "-p", "6379", "info", "memory"
    ])

    if code == 0:
        for line in stdout.split("\n"):
            if line.startswith("used_memory_human:"):
                print(f"[INFO] Memory used: {line.split(':')[1].strip()}")

    print()


if __name__ == "__main__":
    main()
