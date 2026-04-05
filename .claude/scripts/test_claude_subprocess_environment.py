#!/usr/bin/env python3
"""
Comprehensive Claude CLI Subprocess Environment Test
Documents exact runtime environment, paths, and behavior
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def test_environment():
    """Document complete environment"""

    print_section("SYSTEM INFORMATION")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Script Location: {__file__}")

    print_section("ENVIRONMENT VARIABLES")

    # Key variables for Claude
    env_vars = [
        'ANTHROPIC_API_KEY',
        'CLAUDE_CODE_OAUTH_TOKEN',
        'DATABASE_URL',
        'CLAUDECODE',
        'PATH',
        'USERPROFILE',
        'HOME',
        'SHELL',
        'COMSPEC'
    ]

    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        if 'KEY' in var or 'TOKEN' in var or 'DATABASE' in var:
            # Mask sensitive data
            if value != 'NOT SET':
                masked = value[:15] + '...' if len(value) > 15 else value
                print(f"{var}: {masked} (length: {len(value)})")
            else:
                print(f"{var}: NOT SET")
        else:
            if var == 'PATH':
                print(f"\n{var}:")
                for path in value.split(os.pathsep):
                    print(f"  - {path}")
            else:
                print(f"{var}: {value}")

    print_section("CLAUDE EXECUTABLE LOCATION")

    # Find claude executable
    claude_path = shutil.which('claude')
    print(f"which('claude'): {claude_path}")

    if claude_path:
        print(f"Resolved Path: {Path(claude_path).resolve()}")
        print(f"File Exists: {Path(claude_path).exists()}")
        print(f"Is File: {Path(claude_path).is_file()}")

        # Check if it's a CMD file
        if claude_path.endswith('.CMD'):
            print(f"\n⚠️  Claude is a Windows CMD file (.CMD)")
            print(f"Reading CMD file contents:")
            try:
                with open(claude_path, 'r') as f:
                    contents = f.read()
                    print(contents)
            except Exception as e:
                print(f"Error reading CMD file: {e}")

    print_section("GIT ALIASES")

    # Check for git aliases
    try:
        result = subprocess.run(
            ['git', 'config', '--get-regexp', '^alias\\.'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout:
            print("Git aliases found:")
            print(result.stdout)
        else:
            print("No git aliases found")
    except Exception as e:
        print(f"Error checking git aliases: {e}")

    print_section("CLAUDE VERSION TEST")

    # Test basic claude command
    try:
        result = subprocess.run(
            [claude_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5,
            env=os.environ.copy()
        )
        print(f"Exit Code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  TIMEOUT after 5 seconds")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print_section("CLAUDE STREAM-JSON TEST (3s timeout)")

    # Test with stream-json flag
    try:
        cmd = [claude_path, '--output-format', 'stream-json']
        print(f"Command: {' '.join(cmd)}")
        print(f"Input: 'test\\n'")
        print(f"Environment: ANTHROPIC_API_KEY set: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
        print(f"\nExecuting...")

        result = subprocess.run(
            cmd,
            input='test\n',
            capture_output=True,
            text=True,
            timeout=3,
            env=os.environ.copy(),
            shell=False
        )
        print(f"✅ SUCCESS!")
        print(f"Exit Code: {result.returncode}")
        print(f"STDOUT (first 500 chars): {result.stdout[:500]}")
        print(f"STDERR (first 500 chars): {result.stderr[:500]}")
    except subprocess.TimeoutExpired as e:
        print(f"⚠️  TIMEOUT after 3 seconds")
        print(f"Partial STDOUT: {e.stdout[:200] if e.stdout else 'None'}")
        print(f"Partial STDERR: {e.stderr[:200] if e.stderr else 'None'}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

    print_section("SUBPROCESS MODULE DETAILS")

    print(f"subprocess module: {subprocess.__file__}")
    print(f"Python subprocess.run available: {hasattr(subprocess, 'run')}")

    # Test different shell modes
    print_section("SHELL MODE COMPARISON")

    for shell_mode in [False, True]:
        print(f"\n--- Testing with shell={shell_mode} ---")
        try:
            cmd = [claude_path, '--version'] if not shell_mode else f'"{claude_path}" --version'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3,
                shell=shell_mode,
                env=os.environ.copy()
            )
            print(f"✅ Exit Code: {result.returncode}")
            print(f"Output: {result.stdout.strip()[:100]}")
        except subprocess.TimeoutExpired:
            print(f"⚠️  TIMEOUT")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    print_section("TEST COMPLETE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Report saved to: {Path.home() / '.claude' / 'subprocess_test_report.txt'}")

if __name__ == '__main__':
    # Load environment from .env files
    try:
        from dotenv import load_dotenv
        global_env = Path.home() / ".claude" / ".env"
        if global_env.exists():
            load_dotenv(global_env)
            print(f"✓ Loaded: {global_env}")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system env only")

    # Run tests
    test_environment()
