#!/usr/bin/env python3
"""Check Docker and container status for Graphiti."""

import json
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
    print("Docker Status Check")
    print("=" * 40)
    print()

    # Docker version
    code, stdout, stderr = run_cmd(["docker", "--version"])
    if code == 0:
        print(f"[OK] Docker: {stdout.strip()}")
    else:
        print("[ERROR] Docker not installed or not in PATH")
        sys.exit(1)

    # Docker daemon
    code, stdout, stderr = run_cmd(["docker", "info", "--format", "{{.ServerVersion}}"])
    if code == 0:
        print(f"[OK] Docker daemon running: v{stdout.strip()}")
    else:
        print("[ERROR] Docker daemon not running")
        print("       Start Docker Desktop and try again")
        sys.exit(1)

    # Docker Compose
    code, stdout, stderr = run_cmd(["docker", "compose", "version", "--short"])
    if code == 0:
        print(f"[OK] Docker Compose: v{stdout.strip()}")
    else:
        print("[WARN] Docker Compose not available")

    print()
    print("Graphiti Containers")
    print("-" * 40)

    # List containers
    code, stdout, stderr = run_cmd([
        "docker", "ps", "-a",
        "--filter", "name=graphiti",
        "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ])

    if code == 0 and stdout.strip():
        print(stdout)
    else:
        print("No Graphiti containers found")
        print()
        print("To start the server:")
        print("  cd C:/Users/gblac/OneDrive/Desktop/afs/graphiti/mcp_server")
        print("  docker compose -f docker/docker-compose.yml up -d")

    print()


if __name__ == "__main__":
    main()
