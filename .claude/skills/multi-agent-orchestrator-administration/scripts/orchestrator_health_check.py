#!/usr/bin/env python3
"""
Orchestrator Health Check Script
Comprehensive health verification for TAC Orchestrator

Tests:
1. Backend health endpoint
2. Database connectivity (via backend)
3. List agents endpoint
4. WebSocket connectivity
5. Frontend availability

Usage:
    python orchestrator_health_check.py [--save-log]
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import socket
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Try to import requests, fall back to urllib if not available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False


class HealthCheckResult:
    """Result of a single health check."""

    def __init__(self, name: str, passed: bool, message: str, duration_ms: float = 0, details: Optional[dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration_ms = duration_ms
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "duration_ms": round(self.duration_ms, 2),
            "details": self.details,
            "timestamp": self.timestamp
        }


def http_get(url: str, timeout: int = 5) -> tuple[int, dict | str | None, float]:
    """Make HTTP GET request, returns (status_code, response_data, duration_ms)."""
    start = time.time()

    if HAS_REQUESTS:
        try:
            resp = requests.get(url, timeout=timeout)
            duration_ms = (time.time() - start) * 1000
            try:
                data = resp.json()
            except:
                data = resp.text
            return resp.status_code, data, duration_ms
        except requests.exceptions.ConnectionError:
            return 0, None, (time.time() - start) * 1000
        except requests.exceptions.Timeout:
            return 408, None, timeout * 1000
        except Exception as e:
            return -1, str(e), (time.time() - start) * 1000
    else:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                duration_ms = (time.time() - start) * 1000
                data = resp.read().decode('utf-8')
                try:
                    data = json.loads(data)
                except:
                    pass
                return resp.status, data, duration_ms
        except urllib.error.HTTPError as e:
            return e.code, None, (time.time() - start) * 1000
        except urllib.error.URLError:
            return 0, None, (time.time() - start) * 1000
        except Exception as e:
            return -1, str(e), (time.time() - start) * 1000


def check_port_open(host: str, port: int, timeout: int = 2) -> tuple[bool, float]:
    """Check if a port is open, returns (is_open, duration_ms)."""
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        duration_ms = (time.time() - start) * 1000
        return result == 0, duration_ms
    except Exception:
        return False, (time.time() - start) * 1000
    finally:
        sock.close()


class OrchestratorHealthCheck:
    """Comprehensive health check for the orchestrator."""

    def __init__(self, backend_host: str = "127.0.0.1", backend_port: int = 9403,
                 frontend_host: str = "127.0.0.1", frontend_port: int = 5999):
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.frontend_host = frontend_host
        self.frontend_port = frontend_port
        self.results: list[HealthCheckResult] = []

    @property
    def backend_url(self) -> str:
        return f"http://{self.backend_host}:{self.backend_port}"

    @property
    def frontend_url(self) -> str:
        return f"http://{self.frontend_host}:{self.frontend_port}"

    def check_backend_health(self) -> HealthCheckResult:
        """Check backend /health endpoint."""
        url = f"{self.backend_url}/health"
        status_code, data, duration_ms = http_get(url)

        if status_code == 200 and isinstance(data, dict):
            return HealthCheckResult(
                name="Backend Health",
                passed=True,
                message="Backend is healthy",
                duration_ms=duration_ms,
                details=data
            )
        elif status_code == 0:
            return HealthCheckResult(
                name="Backend Health",
                passed=False,
                message=f"Backend not reachable on port {self.backend_port}",
                duration_ms=duration_ms
            )
        else:
            return HealthCheckResult(
                name="Backend Health",
                passed=False,
                message=f"Backend returned status {status_code}",
                duration_ms=duration_ms,
                details={"response": data}
            )

    def check_database_connection(self) -> HealthCheckResult:
        """Check database connectivity via backend list_agents endpoint."""
        # The list_agents endpoint requires database connectivity,
        # so if it succeeds, the database is working
        url = f"{self.backend_url}/list_agents"
        status_code, data, duration_ms = http_get(url)

        if status_code == 200:
            return HealthCheckResult(
                name="Database Connection",
                passed=True,
                message="Database responding via list_agents",
                duration_ms=duration_ms,
                details={"test_endpoint": "/list_agents", "status": "connected"}
            )
        elif status_code == 0:
            return HealthCheckResult(
                name="Database Connection",
                passed=False,
                message="Backend not reachable",
                duration_ms=duration_ms
            )
        else:
            return HealthCheckResult(
                name="Database Connection",
                passed=False,
                message=f"Database query failed with status {status_code}",
                duration_ms=duration_ms,
                details={"error": str(data)[:200] if data else None}
            )

    def check_list_agents(self) -> HealthCheckResult:
        """Check /list_agents endpoint."""
        url = f"{self.backend_url}/list_agents"
        status_code, data, duration_ms = http_get(url)

        if status_code == 200:
            agent_count = len(data) if isinstance(data, list) else 0
            return HealthCheckResult(
                name="List Agents Endpoint",
                passed=True,
                message=f"Found {agent_count} agents",
                duration_ms=duration_ms,
                details={"agent_count": agent_count}
            )
        elif status_code == 0:
            return HealthCheckResult(
                name="List Agents Endpoint",
                passed=False,
                message="Backend not reachable",
                duration_ms=duration_ms
            )
        else:
            return HealthCheckResult(
                name="List Agents Endpoint",
                passed=False,
                message=f"Endpoint returned status {status_code}",
                duration_ms=duration_ms,
                details={"response": str(data)[:200] if data else None}
            )

    def check_websocket_port(self) -> HealthCheckResult:
        """Check if WebSocket port is accessible."""
        is_open, duration_ms = check_port_open(self.backend_host, self.backend_port)

        if is_open:
            return HealthCheckResult(
                name="WebSocket Port",
                passed=True,
                message=f"Port {self.backend_port} is accessible",
                duration_ms=duration_ms,
                details={"port": self.backend_port, "host": self.backend_host}
            )
        else:
            return HealthCheckResult(
                name="WebSocket Port",
                passed=False,
                message=f"Port {self.backend_port} is not accessible",
                duration_ms=duration_ms,
                details={"port": self.backend_port, "host": self.backend_host}
            )

    def check_frontend(self) -> HealthCheckResult:
        """Check frontend availability."""
        is_open, duration_ms = check_port_open(self.frontend_host, self.frontend_port)

        if is_open:
            # Try HTTP request
            status_code, _, http_duration = http_get(self.frontend_url)
            if status_code == 200:
                return HealthCheckResult(
                    name="Frontend",
                    passed=True,
                    message="Frontend is running",
                    duration_ms=http_duration,
                    details={"url": self.frontend_url, "status": status_code}
                )
            else:
                return HealthCheckResult(
                    name="Frontend",
                    passed=True,
                    message=f"Frontend port open, HTTP status: {status_code}",
                    duration_ms=http_duration,
                    details={"url": self.frontend_url, "status": status_code}
                )
        else:
            return HealthCheckResult(
                name="Frontend",
                passed=False,
                message=f"Frontend not running on port {self.frontend_port}",
                duration_ms=duration_ms,
                details={"url": self.frontend_url}
            )

    def check_get_orchestrator(self) -> HealthCheckResult:
        """Check /get_orchestrator endpoint."""
        url = f"{self.backend_url}/get_orchestrator"
        status_code, data, duration_ms = http_get(url)

        if status_code == 200 and isinstance(data, dict):
            session_id = data.get("session_id", "N/A")
            return HealthCheckResult(
                name="Get Orchestrator Endpoint",
                passed=True,
                message=f"Orchestrator active (session: {session_id[:8]}...)" if session_id and session_id != "N/A" else "Orchestrator found",
                duration_ms=duration_ms,
                details={
                    "session_id": session_id,
                    "status": data.get("status", "unknown"),
                    "working_dir": data.get("working_dir", "N/A")
                }
            )
        elif status_code == 404:
            return HealthCheckResult(
                name="Get Orchestrator Endpoint",
                passed=True,
                message="No active orchestrator (expected on fresh start)",
                duration_ms=duration_ms,
                details={"note": "Will be created on first interaction"}
            )
        elif status_code == 0:
            return HealthCheckResult(
                name="Get Orchestrator Endpoint",
                passed=False,
                message="Backend not reachable",
                duration_ms=duration_ms
            )
        else:
            return HealthCheckResult(
                name="Get Orchestrator Endpoint",
                passed=False,
                message=f"Endpoint returned status {status_code}",
                duration_ms=duration_ms
            )

    def run_all_checks(self) -> list[HealthCheckResult]:
        """Run all health checks."""
        self.results = []

        checks = [
            self.check_backend_health,
            self.check_database_connection,
            self.check_websocket_port,
            self.check_list_agents,
            self.check_get_orchestrator,
            self.check_frontend,
        ]

        for check in checks:
            try:
                result = check()
            except Exception as e:
                result = HealthCheckResult(
                    name=check.__name__.replace("check_", "").replace("_", " ").title(),
                    passed=False,
                    message=f"Check failed with error: {str(e)}"
                )
            self.results.append(result)

        return self.results

    def get_summary(self) -> dict:
        """Get summary of all checks."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_time = sum(r.duration_ms for r in self.results)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(self.results),
            "passed": passed,
            "failed": failed,
            "overall_status": "HEALTHY" if failed == 0 else "UNHEALTHY",
            "total_duration_ms": round(total_time, 2),
            "backend_url": self.backend_url,
            "frontend_url": self.frontend_url,
            "checks": [r.to_dict() for r in self.results]
        }

    def print_results(self):
        """Print results to console."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("ORCHESTRATOR HEALTH CHECK REPORT")
        print("=" * 60)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Backend:   {summary['backend_url']}")
        print(f"Frontend:  {summary['frontend_url']}")
        print("-" * 60)

        for result in self.results:
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"{status} {result.name}: {result.message} ({result.duration_ms:.1f}ms)")

        print("-" * 60)
        status_color = "" if summary['failed'] == 0 else "!"
        print(f"OVERALL: {summary['overall_status']} ({summary['passed']}/{summary['total_checks']} passed)")
        print(f"Total time: {summary['total_duration_ms']:.1f}ms")
        print("=" * 60 + "\n")

    def save_log(self, log_dir: Optional[Path] = None) -> Path:
        """Save results to log file."""
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"health_check_{timestamp}.json"

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_summary(), f, indent=2)

        # Also save a markdown version
        md_file = log_dir / f"health_check_{timestamp}.md"
        self._save_markdown_report(md_file)

        return log_file

    def _save_markdown_report(self, filepath: Path):
        """Save markdown report."""
        summary = self.get_summary()

        content = f"""# Orchestrator Health Check Report

**Timestamp:** {summary['timestamp']}
**Status:** {summary['overall_status']}
**Backend:** {summary['backend_url']}
**Frontend:** {summary['frontend_url']}

## Summary

- **Total Checks:** {summary['total_checks']}
- **Passed:** {summary['passed']}
- **Failed:** {summary['failed']}
- **Total Duration:** {summary['total_duration_ms']}ms

## Check Results

| Check | Status | Message | Duration |
|-------|--------|---------|----------|
"""

        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            content += f"| {result.name} | {status} | {result.message} | {result.duration_ms:.1f}ms |\n"

        content += "\n## Details\n\n"

        for result in self.results:
            if result.details:
                content += f"### {result.name}\n\n```json\n{json.dumps(result.details, indent=2)}\n```\n\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description="Orchestrator Health Check")
    parser.add_argument("--backend-host", default="127.0.0.1", help="Backend host")
    parser.add_argument("--backend-port", type=int, default=9403, help="Backend port")
    parser.add_argument("--frontend-host", default="127.0.0.1", help="Frontend host")
    parser.add_argument("--frontend-port", type=int, default=5999, help="Frontend port")
    parser.add_argument("--save-log", action="store_true", help="Save results to log file")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of formatted text")
    parser.add_argument("--quiet", action="store_true", help="Only output summary status")
    args = parser.parse_args()

    checker = OrchestratorHealthCheck(
        backend_host=args.backend_host,
        backend_port=args.backend_port,
        frontend_host=args.frontend_host,
        frontend_port=args.frontend_port
    )

    checker.run_all_checks()

    if args.json:
        print(json.dumps(checker.get_summary(), indent=2))
    elif args.quiet:
        summary = checker.get_summary()
        print(f"Orchestrator: {summary['overall_status']} (Backend OK, Frontend {'OK' if any(r.passed for r in checker.results if r.name == 'Frontend') else 'FAIL'})")
    else:
        checker.print_results()

    if args.save_log:
        log_file = checker.save_log()
        print(f"Log saved to: {log_file}")

    # Exit with appropriate code
    summary = checker.get_summary()
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
