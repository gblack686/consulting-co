#!/usr/bin/env python3
"""
Orchestrator Multi-Agent Troubleshooting Diagnostics

Comprehensive test suite for diagnosing issues with the TAC orchestrator-agent-with-adws application.
Generates detailed diagnostic reports for troubleshooting.

Usage:
    python run_orchestrator_diagnostics.py
    python run_orchestrator_diagnostics.py --category environment
    python run_orchestrator_diagnostics.py --report-only
"""

import asyncio
import sys
import os
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse

# Load environment variables from .env files
try:
    from dotenv import load_dotenv
    # Load global .env first
    global_env = Path.home() / ".claude" / ".env"
    if global_env.exists():
        load_dotenv(global_env)
except ImportError:
    pass  # dotenv not installed, will use system env vars only

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "", details: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details
        self.timestamp = datetime.now()

class DiagnosticSession:
    def __init__(self, app_dir: Path):
        self.app_dir = app_dir
        self.session_id = f"diag_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.results: Dict[str, List[TestResult]] = {}
        self.verbose = False

    def add_result(self, category: str, result: TestResult):
        if category not in self.results:
            self.results[category] = []
        self.results[category].append(result)

        # Print result immediately if verbose
        if self.verbose:
            status = f"{Colors.GREEN}✓{Colors.RESET}" if result.passed else f"{Colors.RED}✗{Colors.RESET}"
            print(f"  {status} {result.name}: {result.message}")

    def print_summary(self):
        total_tests = sum(len(results) for results in self.results.values())
        total_passed = sum(sum(1 for r in results if r.passed) for results in self.results.values())
        total_failed = total_tests - total_passed

        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}DIAGNOSTIC SUMMARY{Colors.RESET}")
        print(f"{'='*70}")
        print(f"Session ID: {Colors.CYAN}{self.session_id}{Colors.RESET}")
        print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.1f}s")
        print(f"Tests: {total_passed}/{total_tests} passed ({total_passed/total_tests*100:.0f}%)")

        if total_failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ {total_failed} TEST(S) FAILED{Colors.RESET}")

        print(f"\n{Colors.BOLD}Test Results by Category:{Colors.RESET}")
        for category, results in self.results.items():
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            status = f"{Colors.GREEN}✓{Colors.RESET}" if passed == total else f"{Colors.RED}✗{Colors.RESET}"
            print(f"  {status} {category}: {passed}/{total} passed")

        print(f"{'='*70}\n")

# Test implementations
class EnvironmentTests:
    @staticmethod
    async def run_all(session: DiagnosticSession):
        print(f"\n{Colors.BOLD}{Colors.BLUE}1. Environment Tests{Colors.RESET}")

        # Test 1.1: Python Version
        try:
            major, minor = sys.version_info.major, sys.version_info.minor
            version = f"{major}.{minor}"
            passed = float(version) >= 3.12
            session.add_result("Environment", TestResult(
                "Python Version",
                passed,
                f"Python {version} {'✓' if passed else '(need 3.12+)'}",
                f"Full version: {sys.version}"
            ))
        except Exception as e:
            session.add_result("Environment", TestResult("Python Version", False, str(e)))

        # Test 1.2: Node.js Version
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                major = int(version.split('.')[0].replace('v', ''))
                passed = major >= 18
                session.add_result("Environment", TestResult(
                    "Node.js Version",
                    passed,
                    f"Node {version} {'✓' if passed else '(need v18+)'}",
                    result.stdout
                ))
            else:
                session.add_result("Environment", TestResult("Node.js Version", False, "Command failed", result.stderr))
        except Exception as e:
            session.add_result("Environment", TestResult("Node.js Version", False, f"Error: {str(e)}"))

        # Test 1.3: Required Binaries
        binaries = ['uv', 'npm', 'claude', 'git']
        for binary in binaries:
            try:
                path = shutil.which(binary)
                session.add_result("Environment", TestResult(
                    f"Binary: {binary}",
                    path is not None,
                    f"Found at {path}" if path else "Not found in PATH"
                ))
            except Exception as e:
                session.add_result("Environment", TestResult(f"Binary: {binary}", False, str(e)))

        # Test 1.4: Environment Variables
        env_vars = {
            'ANTHROPIC_API_KEY': 'API key configuration',
            'DATABASE_URL': 'Database connection',
            'CLAUDECODE': 'Running inside Claude Code'
        }
        for var, desc in env_vars.items():
            value = os.environ.get(var)
            session.add_result("Environment", TestResult(
                f"Env: {var}",
                value is not None and value != "",
                f"{desc}: {'Set' if value else 'Not set'}",
                f"Value: {value[:20]}..." if value and len(value) > 20 else f"Value: {value}"
            ))

        # Test 1.5: Git Aliases
        try:
            result = subprocess.run(
                ['git', 'config', '--global', '--get-regexp', 'alias.claude'],
                capture_output=True, text=True, timeout=5
            )
            has_alias = result.returncode == 0 and result.stdout.strip() != ""
            session.add_result("Environment", TestResult(
                "Git Alias Check",
                not has_alias,  # Pass if NO alias (alias could interfere)
                f"Git alias 'claude' {'found (may interfere)' if has_alias else 'not found'}",
                result.stdout if has_alias else "No alias detected"
            ))
        except Exception as e:
            session.add_result("Environment", TestResult("Git Alias Check", True, "Could not check", str(e)))

class DatabaseTests:
    @staticmethod
    async def run_all(session: DiagnosticSession):
        print(f"\n{Colors.BOLD}{Colors.BLUE}2. Database Tests{Colors.RESET}")

        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            session.add_result("Database", TestResult("Connection", False, "DATABASE_URL not set"))
            return

        try:
            import asyncpg

            # Test 2.1: Connection
            try:
                conn = await asyncpg.connect(database_url)
                session.add_result("Database", TestResult(
                    "Connection",
                    True,
                    "Successfully connected to PostgreSQL",
                    f"Host: {conn.get_server_pid()}"
                ))

                # Test 2.2: Schema Validation
                tables = await conn.fetch("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN (
                        'orchestrator_agents', 'agents', 'prompts',
                        'agent_logs', 'system_logs', 'orchestrator_chat'
                    )
                """)
                expected_tables = 6
                found_tables = len(tables)
                session.add_result("Database", TestResult(
                    "Schema Validation",
                    found_tables == expected_tables,
                    f"Found {found_tables}/{expected_tables} required tables",
                    ", ".join([t['table_name'] for t in tables])
                ))

                # Test 2.3: Orchestrator Record
                orch = await conn.fetchrow("""
                    SELECT id, session_id, status, created_at
                    FROM orchestrator_agents
                    WHERE archived = false
                    ORDER BY created_at DESC LIMIT 1
                """)
                session.add_result("Database", TestResult(
                    "Orchestrator Record",
                    orch is not None,
                    f"Found orchestrator: {orch['id'][:8]}..." if orch else "No orchestrator found",
                    f"Session: {orch['session_id']}, Status: {orch['status']}" if orch else ""
                ))

                # Test 2.4: Chat History
                count = await conn.fetchval("SELECT COUNT(*) FROM orchestrator_chat")
                session.add_result("Database", TestResult(
                    "Chat History",
                    True,
                    f"{count} messages in chat history"
                ))

                await conn.close()

            except Exception as e:
                session.add_result("Database", TestResult("Connection", False, f"Failed: {str(e)}", str(e)))

        except ImportError:
            session.add_result("Database", TestResult("Connection", False, "asyncpg not installed"))

class BackendTests:
    @staticmethod
    async def run_all(session: DiagnosticSession):
        print(f"\n{Colors.BOLD}{Colors.BLUE}3. Backend Tests{Colors.RESET}")

        # Test 3.1: Port Check
        try:
            result = subprocess.run(['lsof', '-ti:9403'], capture_output=True, text=True, timeout=5)
            port_in_use = result.returncode == 0 and result.stdout.strip() != ""
            session.add_result("Backend", TestResult(
                "Port 9403",
                port_in_use,
                f"Port {'in use (backend running)' if port_in_use else 'available (backend not running)'}",
                f"PID: {result.stdout.strip()}" if port_in_use else ""
            ))
        except Exception as e:
            session.add_result("Backend", TestResult("Port 9403", False, f"Check failed: {str(e)}"))

        # Test 3.2: Process Running
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True, text=True, timeout=5
            )
            has_uvicorn = 'uvicorn' in result.stdout and 'main:app' in result.stdout
            session.add_result("Backend", TestResult(
                "Uvicorn Process",
                has_uvicorn,
                f"Uvicorn {'running' if has_uvicorn else 'not running'}"
            ))
        except Exception as e:
            session.add_result("Backend", TestResult("Uvicorn Process", False, str(e)))

        # Test 3.3: Health Endpoint
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get('http://127.0.0.1:9403/health')
                session.add_result("Backend", TestResult(
                    "Health Endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}",
                    response.text[:200]
                ))
        except Exception as e:
            session.add_result("Backend", TestResult("Health Endpoint", False, f"Request failed: {str(e)}"))

        # Test 3.4: Claude SDK Import
        try:
            import claude_agent_sdk
            version = getattr(claude_agent_sdk, '__version__', 'unknown')
            session.add_result("Backend", TestResult(
                "Claude SDK Import",
                True,
                f"Imported successfully, version: {version}"
            ))
        except ImportError as e:
            session.add_result("Backend", TestResult("Claude SDK Import", False, f"Import failed: {str(e)}"))

class ClaudeSDKTests:
    @staticmethod
    async def run_all(session: DiagnosticSession):
        print(f"\n{Colors.BOLD}{Colors.BLUE}4. Claude SDK Tests{Colors.RESET}")

        # Test 5.1: Claude CLI Location
        claude_path = shutil.which('claude')
        session.add_result("Claude SDK", TestResult(
            "CLI Location",
            claude_path is not None,
            f"Found at: {claude_path}" if claude_path else "Not found in PATH"
        ))

        if not claude_path:
            return

        # Test 5.2: Version Check
        try:
            result = subprocess.run([claude_path, '--version'], capture_output=True, text=True, timeout=5)
            session.add_result("Claude SDK", TestResult(
                "Version Check",
                result.returncode == 0,
                result.stdout.strip() if result.returncode == 0 else "Failed",
                result.stderr if result.returncode != 0 else ""
            ))
        except Exception as e:
            session.add_result("Claude SDK", TestResult("Version Check", False, str(e)))

        # Test 5.3: Basic Subprocess
        try:
            result = subprocess.run(
                [claude_path, '--version'],
                capture_output=True, text=True, timeout=5
            )
            session.add_result("Claude SDK", TestResult(
                "Basic Subprocess",
                result.returncode == 0,
                "Successfully spawned subprocess",
                result.stdout
            ))
        except Exception as e:
            session.add_result("Claude SDK", TestResult("Basic Subprocess", False, str(e)))

        # Test 5.4: Subprocess with SDK Flags (CRITICAL TEST)
        try:
            result = subprocess.run(
                [
                    claude_path,
                    '--output-format', 'stream-json',
                    '--verbose',
                    '--system-prompt', 'Test prompt',
                    '--model', 'claude-haiku-4-5-20251001'
                ],
                capture_output=True,
                text=True,
                timeout=3,
                input='test\n'
            )
            session.add_result("Claude SDK", TestResult(
                "SDK Flags Subprocess",
                result.returncode == 0,
                "Subprocess with SDK flags succeeded",
                f"stdout: {result.stdout[:100]}, stderr: {result.stderr[:100]}"
            ))
        except subprocess.TimeoutExpired:
            session.add_result("Claude SDK", TestResult(
                "SDK Flags Subprocess",
                False,
                "⚠️ TIMEOUT - Subprocess hung (this is the root issue!)",
                "Command timed out after 3 seconds - likely waiting for input or stream issue"
            ))
        except Exception as e:
            session.add_result("Claude SDK", TestResult(
                "SDK Flags Subprocess",
                False,
                f"Failed: {str(e)}",
                str(e)
            ))

async def run_diagnostics(app_dir: Path, category: Optional[str] = None, verbose: bool = False):
    """Run full diagnostic suite"""

    session = DiagnosticSession(app_dir)
    session.verbose = verbose

    # Load app-specific .env file
    try:
        from dotenv import load_dotenv
        app_env = app_dir / ".env"
        if app_env.exists():
            load_dotenv(app_env, override=True)
    except ImportError:
        pass

    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 70)
    print("ORCHESTRATOR MULTI-AGENT TROUBLESHOOTING DIAGNOSTICS")
    print("=" * 70)
    print(f"{Colors.RESET}")
    print(f"Session ID: {session.session_id}")
    print(f"App Directory: {app_dir}")
    print(f"Timestamp: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Run test categories
    if not category or category == 'environment':
        await EnvironmentTests.run_all(session)

    if not category or category == 'database':
        await DatabaseTests.run_all(session)

    if not category or category == 'backend':
        await BackendTests.run_all(session)

    if not category or category == 'claude-sdk':
        await ClaudeSDKTests.run_all(session)

    # Print summary
    session.print_summary()

    # Generate report
    report_path = Path.home() / ".claude" / "diagnostics" / f"{session.session_id}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # TODO: Generate markdown report
    print(f"{Colors.CYAN}Report saved to: {report_path}{Colors.RESET}")

    return session

def main():
    parser = argparse.ArgumentParser(description='Run orchestrator diagnostics')
    parser.add_argument('--category', choices=['environment', 'database', 'backend', 'claude-sdk'],
                       help='Run specific test category only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--app-dir', default='C:\\Users\\gblac\\OneDrive\\Desktop\\tac\\orchestrator-agent-with-adws\\apps\\orchestrator_3_stream',
                       help='Path to orchestrator app directory')

    args = parser.parse_args()

    app_dir = Path(args.app_dir)
    if not app_dir.exists():
        print(f"{Colors.RED}Error: App directory not found: {app_dir}{Colors.RESET}")
        sys.exit(1)

    # Run diagnostics
    asyncio.run(run_diagnostics(app_dir, args.category, args.verbose))

if __name__ == '__main__':
    main()
