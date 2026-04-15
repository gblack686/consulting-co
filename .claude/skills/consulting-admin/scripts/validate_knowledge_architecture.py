#!/usr/bin/env python3
"""
Happy-path validator for the Knowledge Architecture Consolidation plan.
Checks all 6 phases of buzzing-splashing-dawn.md are correctly implemented.

Usage:
  python validate_knowledge_architecture.py              # all phases
  python validate_knowledge_architecture.py --phase 1    # single phase
  python validate_knowledge_architecture.py --phase 1 3  # specific phases
  python validate_knowledge_architecture.py --mac-mini 192.168.4.94  # custom host
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

MAC_MINI_HOST = "100.88.4.114"
MAC_MINI_USER = "greg"

# Detect environment
IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

# Path resolution
def find_project_root() -> Path:
    """Find consulting-co root by walking up from script location."""
    # Script is at .claude/skills/consulting-admin/scripts/
    script_dir = Path(__file__).resolve().parent
    # Walk up to find .claude/ parent
    for parent in [script_dir] + list(script_dir.parents):
        if (parent / ".claude").is_dir() and (parent / "CLAUDE.md").is_file():
            return parent
        # Also check if we're already at the .claude level
        if parent.name == "scripts" and (parent.parent.name == "consulting-admin"):
            root = parent.parent.parent.parent.parent
            if (root / "CLAUDE.md").is_file():
                return root
    # Fallback
    return Path("C:/Users/gblac/OneDrive/Desktop/consulting-co")


PROJECT_ROOT = find_project_root()

# Second brain paths — local (Windows)
LOCAL_SECOND_BRAINS = {
    "fisch-group": Path("C:/Users/gblac/OneDrive/Desktop/gbauto/fisch-group/second-brain"),
    "gbautomation": Path("C:/Users/gblac/OneDrive/Desktop/gbauto/gbautomation/second-brain"),
}

# Second brain paths — Mac Mini
REMOTE_SECOND_BRAINS = {
    "fisch-group": "~/repos/fisch-group/second-brain",
    "gbautomation": "~/repos/gbautomation/second-brain",
}


# ── Output helpers ────────────────────────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def ok(msg: str) -> str:
    return f"  {GREEN}✓{RESET} {msg}"


def fail(msg: str) -> str:
    return f"  {RED}✗{RESET} {msg}"


def warn(msg: str) -> str:
    return f"  {YELLOW}⚠{RESET} {msg}"


def phase_header(num: int, name: str, passed: bool) -> str:
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    label = f"Phase {num}: {name}"
    dots = "." * (42 - len(label))
    return f"\n{BOLD}{label}{RESET} {DIM}{dots}{RESET} {status}"


# ── SSH helper ────────────────────────────────────────────────────────────────

def ssh_check(host: str, cmd: str, timeout: int = 10) -> tuple[bool, str]:
    """Run a command on Mac Mini via SSH. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["ssh", f"{MAC_MINI_USER}@{host}", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "SSH timeout"
    except FileNotFoundError:
        return False, "ssh not found"
    except Exception as e:
        return False, str(e)


def file_exists_local(path: Path) -> bool:
    return path.is_file()


def dir_exists_local(path: Path) -> bool:
    return path.is_dir()


def file_contains(path: Path, needle: str) -> bool:
    try:
        return needle.lower() in path.read_text(encoding="utf-8").lower()
    except Exception:
        return False


def script_importable(path: Path) -> tuple[bool, str]:
    """Check if a Python script can be compiled (no syntax errors)."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import py_compile; py_compile.compile(r'{path}', doraise=True)"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def script_help(path: Path) -> tuple[bool, str]:
    """Check if script --help works."""
    try:
        result = subprocess.run(
            [sys.executable, str(path), "--help"],
            capture_output=True, text=True, timeout=10,
            cwd=str(path.parent),
        )
        return result.returncode == 0, result.stdout[:200]
    except Exception as e:
        return False, str(e)


# ── Phase validators ──────────────────────────────────────────────────────────

def validate_phase_1(mac_mini_host: str) -> tuple[bool, list[str]]:
    """Phase 1: Knowledge layer added to per-client second brains."""
    details = []
    all_pass = True

    knowledge_files = ["index.md", "log.md"]
    knowledge_dirs = ["concepts", "connections", "qa"]

    for client, local_path in LOCAL_SECOND_BRAINS.items():
        kb_path = local_path / "knowledge"

        # Check local first
        if dir_exists_local(kb_path):
            details.append(ok(f"{client} knowledge/ exists (local)"))

            for f in knowledge_files:
                if file_exists_local(kb_path / f):
                    details.append(ok(f"{client} knowledge/{f} exists"))
                else:
                    details.append(fail(f"{client} knowledge/{f} missing"))
                    all_pass = False

            for d in knowledge_dirs:
                if dir_exists_local(kb_path / d):
                    details.append(ok(f"{client} knowledge/{d}/ exists"))
                else:
                    details.append(fail(f"{client} knowledge/{d}/ missing"))
                    all_pass = False
        else:
            # Try Mac Mini
            remote_path = REMOTE_SECOND_BRAINS.get(client, "")
            if remote_path:
                success, output = ssh_check(
                    mac_mini_host,
                    f"ls {remote_path}/knowledge/index.md {remote_path}/knowledge/log.md 2>/dev/null && echo OK"
                )
                if success and "OK" in output:
                    details.append(ok(f"{client} knowledge/ exists (Mac Mini)"))
                    # Check subdirs
                    for d in knowledge_dirs:
                        s2, _ = ssh_check(mac_mini_host, f"test -d {remote_path}/knowledge/{d} && echo YES")
                        if s2 and "YES" in _:
                            details.append(ok(f"{client} knowledge/{d}/ exists (Mac Mini)"))
                        else:
                            details.append(fail(f"{client} knowledge/{d}/ missing (Mac Mini)"))
                            all_pass = False
                else:
                    details.append(fail(f"{client} knowledge/ not found (local or Mac Mini)"))
                    all_pass = False
            else:
                details.append(fail(f"{client} knowledge/ missing"))
                all_pass = False

        # Check CLAUDE.md references knowledge
        claude_md = local_path / "CLAUDE.md"
        if file_exists_local(claude_md):
            if file_contains(claude_md, "knowledge"):
                details.append(ok(f"{client} CLAUDE.md references knowledge layer"))
            else:
                details.append(fail(f"{client} CLAUDE.md missing knowledge references"))
                all_pass = False
        else:
            details.append(warn(f"{client} CLAUDE.md not found locally"))

    return all_pass, details


def validate_phase_2(mac_mini_host: str) -> tuple[bool, list[str]]:
    """Phase 2: Knowledge compiler script."""
    details = []
    all_pass = True

    script = PROJECT_ROOT / ".claude" / "skills" / "consulting-admin" / "scripts" / "compile_knowledge.py"

    if file_exists_local(script):
        details.append(ok("compile_knowledge.py exists"))
    else:
        details.append(fail("compile_knowledge.py missing"))
        return False, details

    # Syntax check
    importable, err = script_importable(script)
    if importable:
        details.append(ok("compile_knowledge.py has valid syntax"))
    else:
        details.append(fail(f"compile_knowledge.py syntax error: {err[:100]}"))
        all_pass = False

    # --help check
    helps, output = script_help(script)
    if helps:
        details.append(ok("compile_knowledge.py --help succeeds"))
    else:
        details.append(warn(f"compile_knowledge.py --help failed: {output[:100]}"))

    # Check for --dry-run flag in source
    if file_contains(script, "dry-run") or file_contains(script, "dry_run"):
        details.append(ok("compile_knowledge.py supports --dry-run"))
    else:
        details.append(warn("compile_knowledge.py may not support --dry-run"))

    return all_pass, details


def validate_phase_3(mac_mini_host: str) -> tuple[bool, list[str]]:
    """Phase 3: Claude Code hooks."""
    details = []
    all_pass = True

    hooks_dir = PROJECT_ROOT / ".claude" / "hooks"
    hook_files = [
        "session-start-context.py",
        "pre-compact-flush.py",
        "session-end-flush.py",
    ]

    for hf in hook_files:
        path = hooks_dir / hf
        if file_exists_local(path):
            details.append(ok(f"{hf} exists"))
            importable, err = script_importable(path)
            if importable:
                details.append(ok(f"{hf} has valid syntax"))
            else:
                details.append(fail(f"{hf} syntax error: {err[:80]}"))
                all_pass = False
        else:
            details.append(fail(f"{hf} missing"))
            all_pass = False

    # Check settings.json for hook references
    settings_paths = [
        PROJECT_ROOT / ".claude" / "settings.json",
        PROJECT_ROOT / ".claude" / "settings.local.json",
    ]

    hook_config_found = False
    for sp in settings_paths:
        if file_exists_local(sp):
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
                hooks = data.get("hooks", {})
                # Check if any hook events reference our files
                hooks_str = json.dumps(hooks).lower()
                if "session-start" in hooks_str or "session_start" in hooks_str:
                    hook_config_found = True
                    details.append(ok(f"Hook config found in {sp.name}"))
                    break
            except Exception:
                pass

    if not hook_config_found:
        # Also check hooks.json
        hooks_json = PROJECT_ROOT / ".claude" / "hooks.json"
        if file_exists_local(hooks_json):
            try:
                data = json.loads(hooks_json.read_text(encoding="utf-8"))
                hooks_str = json.dumps(data).lower()
                if "session-start" in hooks_str or "compact" in hooks_str:
                    hook_config_found = True
                    details.append(ok("Hook config found in hooks.json"))
            except Exception:
                pass

    if not hook_config_found:
        details.append(fail("No hook configuration found in settings.json/hooks.json"))
        all_pass = False

    return all_pass, details


def validate_phase_4(mac_mini_host: str) -> tuple[bool, list[str]]:
    """Phase 4: Consulting agent updated."""
    details = []
    all_pass = True

    agent_md = PROJECT_ROOT / ".claude" / "agents" / "consulting-agent.md"

    if file_exists_local(agent_md):
        details.append(ok("consulting-agent.md exists"))
        if file_contains(agent_md, "knowledge/") or file_contains(agent_md, "knowledge layer"):
            details.append(ok("consulting-agent.md references knowledge/ structure"))
        else:
            details.append(fail("consulting-agent.md missing knowledge/ references"))
            all_pass = False
    else:
        details.append(fail("consulting-agent.md not found"))
        all_pass = False

    return all_pass, details


def validate_phase_5(mac_mini_host: str) -> tuple[bool, list[str]]:
    """Phase 5: Client folder standard updated."""
    details = []
    all_pass = True

    standard_md = (
        PROJECT_ROOT / ".claude" / "skills" / "consulting-intake"
        / "references" / "client-folder-standard.md"
    )

    if file_exists_local(standard_md):
        details.append(ok("client-folder-standard.md exists"))
        if file_contains(standard_md, "knowledge/") or file_contains(standard_md, "knowledge layer"):
            details.append(ok("client-folder-standard.md references knowledge/ structure"))
        else:
            details.append(fail("client-folder-standard.md missing knowledge/ references"))
            all_pass = False
    else:
        details.append(fail("client-folder-standard.md not found"))
        all_pass = False

    return all_pass, details


def validate_phase_6(mac_mini_host: str) -> tuple[bool, list[str]]:
    """Phase 6: Wiki compiler."""
    details = []
    all_pass = True

    script = PROJECT_ROOT / ".claude" / "skills" / "consulting-admin" / "scripts" / "compile_wiki.py"
    wiki_index = PROJECT_ROOT / "wiki" / "index.md"

    if file_exists_local(script):
        details.append(ok("compile_wiki.py exists"))
        importable, err = script_importable(script)
        if importable:
            details.append(ok("compile_wiki.py has valid syntax"))
        else:
            details.append(fail(f"compile_wiki.py syntax error: {err[:80]}"))
            all_pass = False
    else:
        details.append(fail("compile_wiki.py missing"))
        all_pass = False

    if file_exists_local(wiki_index):
        details.append(ok("wiki/index.md exists"))
    else:
        details.append(warn("wiki/index.md not found"))

    return all_pass, details


# ── Main ──────────────────────────────────────────────────────────────────────

VALIDATORS = {
    1: ("Knowledge Layer", validate_phase_1),
    2: ("Compiler Script", validate_phase_2),
    3: ("Hooks", validate_phase_3),
    4: ("Consulting Agent", validate_phase_4),
    5: ("Folder Standard", validate_phase_5),
    6: ("Wiki Compiler", validate_phase_6),
}


def main():
    parser = argparse.ArgumentParser(description="Validate Knowledge Architecture Consolidation")
    parser.add_argument("--phase", nargs="*", type=int, help="Validate specific phases (e.g., --phase 1 3)")
    parser.add_argument("--mac-mini", default=MAC_MINI_HOST, help=f"Mac Mini host (default: {MAC_MINI_HOST})")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()

    if args.no_color:
        global GREEN, RED, YELLOW, BOLD, DIM, RESET
        GREEN = RED = YELLOW = BOLD = DIM = RESET = ""

    phases_to_run = args.phase if args.phase else list(VALIDATORS.keys())

    print(f"\n{'═' * 45}")
    print(f"  Knowledge Architecture Validator")
    print(f"  Project: {PROJECT_ROOT}")
    print(f"  Mac Mini: {args.mac_mini}")
    print(f"{'═' * 45}")

    results = {}
    for phase_num in sorted(phases_to_run):
        if phase_num not in VALIDATORS:
            print(f"\n{RED}Unknown phase: {phase_num}{RESET}")
            continue

        name, validator = VALIDATORS[phase_num]
        passed, details = validator(args.mac_mini)
        results[phase_num] = passed

        print(phase_header(phase_num, name, passed))
        for line in details:
            print(line)

    # Summary
    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\n{'═' * 45}")
    if passed == total:
        print(f"  {GREEN}{BOLD}Result: {passed}/{total} phases passed{RESET}")
    else:
        print(f"  {RED}{BOLD}Result: {passed}/{total} phases passed{RESET}")
        failed_phases = [str(k) for k, v in results.items() if not v]
        print(f"  Failed: Phase(s) {', '.join(failed_phases)}")
    print(f"{'═' * 45}\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
