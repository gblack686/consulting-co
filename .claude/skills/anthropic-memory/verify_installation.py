#!/usr/bin/env python3
"""
Verify Anthropic Memory Tool Installation

Checks that all components are installed correctly and ready to use.
"""

import os
import sys
from pathlib import Path
import json


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_file(path: Path, name: str) -> bool:
    """Check if a file exists"""
    if path.exists():
        print(f"✅ {name}: {path}")
        return True
    else:
        print(f"❌ {name}: NOT FOUND - {path}")
        return False


def check_directory(path: Path, name: str) -> bool:
    """Check if a directory exists"""
    if path.is_dir():
        print(f"✅ {name}: {path}")
        return True
    else:
        print(f"❌ {name}: NOT FOUND - {path}")
        return False


def check_env_var(name: str) -> bool:
    """Check if environment variable is set"""
    value = os.environ.get(name)
    if value:
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"✅ {name}: {masked}")
        return True
    else:
        print(f"❌ {name}: NOT SET")
        return False


def check_settings_file(path: Path) -> bool:
    """Check if settings file has Stop hook configured"""
    if not path.exists():
        print(f"❌ Settings file not found: {path}")
        return False

    try:
        with open(path, 'r') as f:
            settings = json.load(f)

        if "hooks" in settings and "Stop" in settings["hooks"]:
            stop_hooks = settings["hooks"]["Stop"]
            if isinstance(stop_hooks, list) and len(stop_hooks) > 0:
                for hook in stop_hooks:
                    if "memory_ingest_hook.py" in hook.get("command", ""):
                        print(f"✅ Stop hook configured: {path}")
                        return True

        print(f"⚠️  Settings file exists but Stop hook not configured: {path}")
        return False
    except Exception as e:
        print(f"❌ Error reading settings: {e}")
        return False


def main():
    """Main verification"""
    print_header("Anthropic Memory Tool - Installation Verification")

    # Determine if Windows or Unix
    is_windows = sys.platform == "win32"
    home = Path.home()

    # Define paths
    if is_windows:
        claude_dir = home / ".claude"
    else:
        claude_dir = home / ".claude"

    skill_dir = claude_dir / "skills" / "anthropic-memory"
    hook_file = claude_dir / "hooks" / "memory_ingest_hook.py"
    memories_dir = claude_dir / "memories"
    settings_file = claude_dir / "settings.json"

    # Track results
    checks_passed = 0
    checks_total = 0

    # Check 1: Skill Directory
    print_header("1. Skill Files")
    checks = [
        (skill_dir, "Skill directory"),
        (skill_dir / "skill.md", "Skill definition"),
        (skill_dir / "README.md", "README"),
        (skill_dir / "config" / "memory-config.yaml", "Configuration"),
        (skill_dir / "scripts" / "memory_executor.py", "Memory executor"),
        (skill_dir / "scripts" / "entity_extractor.py", "Entity extractor"),
    ]

    for path, name in checks:
        checks_total += 1
        if path.is_file():
            if check_file(path, name):
                checks_passed += 1
        elif path.is_dir():
            if check_directory(path, name):
                checks_passed += 1
        else:
            print(f"❌ {name}: NOT FOUND - {path}")

    # Check 2: Stop Hook
    print_header("2. Stop Hook")
    checks_total += 1
    if check_file(hook_file, "Stop hook"):
        checks_passed += 1

    # Check 3: Memories Directory
    print_header("3. Memories Directory")
    checks = [
        (memories_dir, "Memories base"),
        (memories_dir / "sessions", "Sessions directory"),
        (memories_dir / "patterns", "Patterns directory"),
        (memories_dir / "entities", "Entities directory"),
    ]

    for path, name in checks:
        checks_total += 1
        if check_directory(path, name):
            checks_passed += 1

    # Check 4: Settings File
    print_header("4. Global Settings")
    checks_total += 1
    if check_settings_file(settings_file):
        checks_passed += 1

    # Check 5: Environment Variables
    print_header("5. Environment Variables")
    checks_total += 1
    if check_env_var("ANTHROPIC_API_KEY"):
        checks_passed += 1

    # Check 6: Dependencies
    print_header("6. Python Dependencies")
    required_packages = ["anthropic", "frontmatter", "yaml"]

    for package in required_packages:
        checks_total += 1
        try:
            __import__(package)
            print(f"✅ {package}: installed")
            checks_passed += 1
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            print(f"   Install with: pip install {package}")

    # Summary
    print_header("Verification Summary")
    print(f"Checks passed: {checks_passed}/{checks_total}")

    if checks_passed == checks_total:
        print("\n🎉 All checks passed! Installation is complete.")
        print("\nNext steps:")
        print("1. Open a new Claude Code terminal (in any directory)")
        print("2. Have a conversation and use some tools")
        print("3. Exit the session (Ctrl+C)")
        print(f"4. Check: {memories_dir / 'sessions'}")
        print("\nYou should see a new session file created!")
        return 0
    else:
        print(f"\n⚠️  {checks_total - checks_passed} check(s) failed.")
        print("\nReview the errors above and:")
        print("1. Ensure you ran the install script")
        print("2. Check file permissions")
        print("3. Install missing dependencies")
        print("\nRun this script again after fixing issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
