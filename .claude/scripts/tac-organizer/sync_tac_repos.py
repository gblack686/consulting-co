#!/usr/bin/env python3
"""
TAC Repository Sync Script

Detects new repositories from github.com/disler and processes them into the TAC ecosystem.

Usage:
    python sync_tac_repos.py --check              # List new repos only
    python sync_tac_repos.py --sync               # Clone and process new repos
    python sync_tac_repos.py --full <repo-name>   # Full reprocess of specific repo
    python sync_tac_repos.py --list               # List all synced repos with status
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Configuration
TAC_ROOT = Path("C:/Users/gblac/OneDrive/Desktop/tac")
OBSIDIAN_KB = Path("C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB")
STATUS_FILE = Path(".claude/data/tac-repo-sync-status.json")
GITHUB_USER = "disler"
MIN_DATE = "2025-11-01"  # Only process repos updated after Nov 2025

# Known TAC repos (for reference)
KNOWN_TAC_REPOS = {
    "tac-1", "tac-2", "tac-3", "tac-4", "tac-5", "tac-6", "tac-7", "tac-8",
    "agent-experts",
    "agentic-finance-review",
    "agent-sandboxes",
    "agent-sandbox-skill",
    "building-domain-specific-agents",
    "claude-code-damage-control",
    "claude-code-hooks-mastery",
    "fork-repository-skill",
    "multi-agent-orchestration-the-o-agent",
    "orchestrator-agent-with-adws",
    "rd-framework-context-window-mastery",
    "seven-levels-agentic-prompt-formats",
}


@dataclass
class ComponentInventory:
    """Inventory of components found in a repository."""
    agents: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    adws: List[str] = field(default_factory=list)


@dataclass
class RepoInfo:
    """Information about a GitHub repository."""
    name: str
    description: str = ""
    url: str = ""
    pushed_at: str = ""
    cloned: bool = False
    processed: bool = False
    components: ComponentInventory = field(default_factory=ComponentInventory)
    tac_summary_exists: bool = False
    obsidian_note_exists: bool = False
    graphiti_synced: bool = False
    vector_indexed: bool = False


def load_status() -> dict:
    """Load sync status from file."""
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {"last_sync": None, "repositories": {}}


def save_status(status: dict):
    """Save sync status to file."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    status["last_sync"] = datetime.now().isoformat()
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def get_github_repos() -> List[dict]:
    """Fetch public repos from GitHub user."""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", GITHUB_USER, "--public", "--json",
             "name,description,url,pushedAt", "--limit", "100"],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error fetching GitHub repos: {e.stderr}{RESET}")
        return []
    except FileNotFoundError:
        print(f"{RED}Error: 'gh' CLI not found. Install GitHub CLI.{RESET}")
        return []


def filter_repos_by_date(repos: List[dict], min_date: str = MIN_DATE) -> List[dict]:
    """Filter repos to only those updated after min_date (YYYY-MM-DD)."""
    filtered = []
    for repo in repos:
        pushed_at = repo.get('pushedAt', '')
        if pushed_at and pushed_at[:10] >= min_date:
            filtered.append(repo)
    return filtered


def get_local_repos() -> set:
    """Get set of repos already cloned to TAC_ROOT."""
    if not TAC_ROOT.exists():
        return set()
    return {d.name for d in TAC_ROOT.iterdir() if d.is_dir() and not d.name.startswith('.')}


def scan_components(repo_path: Path) -> ComponentInventory:
    """Scan repository for Claude Code components."""
    inventory = ComponentInventory()

    claude_path = repo_path / ".claude"
    if not claude_path.exists():
        return inventory

    # Scan agents
    agents_path = claude_path / "agents"
    if agents_path.exists():
        inventory.agents = [f.stem for f in agents_path.glob("*.md")]

    # Scan commands
    commands_path = claude_path / "commands"
    if commands_path.exists():
        inventory.commands = [f.stem for f in commands_path.glob("*.md")]
        # Also check subdirectories
        for subdir in commands_path.iterdir():
            if subdir.is_dir():
                inventory.commands.extend([f"{subdir.name}/{f.stem}" for f in subdir.glob("*.md")])

    # Scan skills
    skills_path = claude_path / "skills"
    if skills_path.exists():
        for d in skills_path.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                inventory.skills.append(d.name)

    # Scan hooks
    hooks_path = claude_path / "hooks"
    if hooks_path.exists():
        inventory.hooks = [f.stem for f in hooks_path.glob("*.py")]

    # Scan ADWs (multiple possible locations)
    for adw_path in [repo_path / "adws", claude_path / "adws"]:
        if adw_path.exists():
            inventory.adws.extend([f.stem for f in adw_path.glob("*.md")])

    return inventory


def check_obsidian_note(repo_name: str) -> bool:
    """Check if Obsidian repository note exists."""
    note_path = OBSIDIAN_KB / "repositories" / f"{repo_name}.md"
    return note_path.exists()


def check_tac_summary(repo_path: Path) -> bool:
    """Check if TAC agent summary exists."""
    summary_path = repo_path / "tac-agent-summary.md"
    return summary_path.exists()


def clone_repo(repo_name: str) -> bool:
    """Clone a repository from GitHub."""
    try:
        os.chdir(TAC_ROOT)
        result = subprocess.run(
            ["gh", "repo", "clone", f"{GITHUB_USER}/{repo_name}"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"{RED}Clone failed: {result.stderr}{RESET}")
            return False
        print(f"{GREEN}Cloned {repo_name}{RESET}")
        return True
    except Exception as e:
        print(f"{RED}Error cloning {repo_name}: {e}{RESET}")
        return False


def check_repo_has_updates(repo_path: Path) -> bool:
    """Check if a local repo has updates available from remote."""
    try:
        os.chdir(repo_path)
        # Fetch from remote
        subprocess.run(["git", "fetch", "origin"], capture_output=True, check=True)
        # Get local HEAD
        local = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        # Get remote HEAD (try main, then master)
        remote = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True, text=True)
        if remote.returncode != 0:
            remote = subprocess.run(["git", "rev-parse", "origin/master"], capture_output=True, text=True)

        if remote.returncode != 0:
            return False

        return local.stdout.strip() != remote.stdout.strip()
    except Exception:
        return False


def pull_repo_updates(repo_path: Path) -> bool:
    """Pull updates for a repository."""
    try:
        os.chdir(repo_path)
        # Try main first, then master
        result = subprocess.run(["git", "pull", "origin", "main", "--ff-only"], capture_output=True, text=True)
        if result.returncode != 0:
            result = subprocess.run(["git", "pull", "origin", "master", "--ff-only"], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"{RED}Pull failed: {result.stderr}{RESET}")
            return False
        print(f"{GREEN}Updated {repo_path.name}{RESET}")
        return True
    except Exception as e:
        print(f"{RED}Error pulling {repo_path.name}: {e}{RESET}")
        return False


def get_repos_with_updates(local_repos: set) -> List[str]:
    """Get list of local repos that have remote updates available."""
    repos_with_updates = []
    for name in local_repos:
        repo_path = TAC_ROOT / name
        if repo_path.exists() and check_repo_has_updates(repo_path):
            repos_with_updates.append(name)
    return repos_with_updates


def generate_tac_summary_prompt(repo_name: str) -> str:
    """Generate the prompt for TAC agent analysis."""
    return f"""Analyze the repository at C:/Users/gblac/OneDrive/Desktop/tac/{repo_name}.

Read the README.md and CLAUDE.md (if present). Answer these questions:

## 1. Primary TAC Lesson
What TAC tactic or lesson does this repository primarily demonstrate?
- If tactics 1-8: identify which tactic
- If lesson 9-15: identify which advanced lesson
- If supporting repo: describe its focus

## 2. Component Inventory
List all Claude Code components found:
- Agents: (list with purposes)
- Commands: (list with purposes)
- Hooks: (list with event types)
- Skills: (list with capabilities)
- ADWs: (list with workflow types)

## 3. Agent Patterns
Which patterns from building-specialized-agents does it implement?
- Pong (request-response)
- Echo (event-driven with custom tools)
- Calculator (tool-heavy focused functionality)

## 4. Frameworks Applied
Which TAC frameworks are demonstrated?
- PITER (Prompt, Input, Trigger, Environment, Review)
- R&D (Reduce & Delegate)
- ACT-LEARN-REUSE
- Core Four (Context, Model, Prompt, Tools)

## 5. Recommended Use Case
What is the recommended use case for this repository?
- When should developers use this as a reference?
- What problem does it solve?

Format as structured markdown."""


def print_check_results(github_repos: List[dict], local_repos: set):
    """Print results of --check operation."""
    # Filter to repos updated after MIN_DATE
    recent_repos = filter_repos_by_date(github_repos)

    print(f"\n{BOLD}TAC Repository Check{RESET}")
    print(f"{DIM}GitHub User: {GITHUB_USER}{RESET}")
    print(f"{DIM}TAC Root: {TAC_ROOT}{RESET}")
    print(f"{DIM}Filter: repos updated after {MIN_DATE}{RESET}\n")

    # Find new repos (only from recent repos)
    github_names = {r['name'] for r in recent_repos}
    new_repos = github_names - local_repos

    # Status table
    print(f"{BOLD}Repository Status (Nov 2025+):{RESET}\n")
    print(f"{'Repository':<45} {'Status':<12} {'Last Push':<12}")
    print("-" * 70)

    for repo in sorted(recent_repos, key=lambda x: x['name']):
        name = repo['name']
        pushed = repo.get('pushedAt', '')[:10] if repo.get('pushedAt') else 'Unknown'

        if name in local_repos:
            repo_path = TAC_ROOT / name
            has_summary = check_tac_summary(repo_path)
            has_obsidian = check_obsidian_note(name)

            if has_summary and has_obsidian:
                status = f"{GREEN}SYNCED{RESET}"
            elif name in local_repos:
                status = f"{YELLOW}PARTIAL{RESET}"
            else:
                status = f"{BLUE}CLONED{RESET}"
        else:
            status = f"{RED}NEW{RESET}"

        print(f"{name:<45} {status:<20} {pushed:<12}")

    # Check for repos with updates (only check those in the recent filter)
    local_in_filter = local_repos & github_names
    print(f"\n{DIM}Checking for updates...{RESET}")
    repos_with_updates = []
    for name in local_in_filter:
        repo_path = TAC_ROOT / name
        if check_repo_has_updates(repo_path):
            repos_with_updates.append(name)

    print("\n" + "-" * 70)
    print(f"{BOLD}Summary:{RESET}")
    print(f"  Total GitHub repos: {len(github_repos)}")
    print(f"  After Nov 2025 filter: {len(recent_repos)}")
    print(f"  Local repos: {len(local_repos)}")
    print(f"  New repos to sync: {len(new_repos)}")
    print(f"  Repos with updates: {len(repos_with_updates)}")

    if new_repos:
        print(f"\n{BOLD}New Repos:{RESET}")
        for name in sorted(new_repos):
            repo = next((r for r in recent_repos if r['name'] == name), {})
            desc = repo.get('description', '')[:50] + '...' if len(repo.get('description', '')) > 50 else repo.get('description', '')
            print(f"  {CYAN}{name}{RESET}: {desc}")

    if repos_with_updates:
        print(f"\n{BOLD}Repos with Updates:{RESET}")
        for name in sorted(repos_with_updates):
            print(f"  {YELLOW}{name}{RESET}")


def print_list_results(local_repos: set):
    """Print detailed status of all synced repos."""
    print(f"\n{BOLD}TAC Repository Inventory{RESET}")
    print(f"{DIM}TAC Root: {TAC_ROOT}{RESET}\n")

    status = load_status()

    print(f"{'Repository':<40} {'Components':<15} {'Summary':<10} {'Obsidian':<10}")
    print("-" * 80)

    for name in sorted(local_repos):
        repo_path = TAC_ROOT / name
        components = scan_components(repo_path)
        total_components = (len(components.agents) + len(components.commands) +
                          len(components.hooks) + len(components.skills) +
                          len(components.adws))

        has_summary = "✓" if check_tac_summary(repo_path) else "✗"
        has_obsidian = "✓" if check_obsidian_note(name) else "✗"

        summary_color = GREEN if has_summary == "✓" else RED
        obsidian_color = GREEN if has_obsidian == "✓" else RED

        print(f"{name:<40} {total_components:<15} {summary_color}{has_summary}{RESET:<10} {obsidian_color}{has_obsidian}{RESET}")

    print("\n" + "-" * 80)
    print(f"Total: {len(local_repos)} repositories")


def main():
    parser = argparse.ArgumentParser(description="Sync TAC repositories from GitHub")
    parser.add_argument("--check", action="store_true", help="Check for new repos and updates")
    parser.add_argument("--sync", action="store_true", help="Clone new repos and pull updates")
    parser.add_argument("--update", action="store_true", help="Only pull updates for existing repos")
    parser.add_argument("--full", metavar="REPO", help="Full reprocess of specific repo")
    parser.add_argument("--list", action="store_true", help="List all synced repos with status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.list:
        local_repos = get_local_repos()
        print_list_results(local_repos)
        return

    if args.check or args.sync or args.update:
        github_repos = get_github_repos()
        local_repos = get_local_repos()

        if args.check:
            print_check_results(github_repos, local_repos)
            return

        if args.update:
            # Only pull updates for existing repos
            recent_repos = filter_repos_by_date(github_repos)
            github_names = {r['name'] for r in recent_repos}
            local_in_filter = local_repos & github_names

            print(f"\n{BOLD}Checking for updates in {len(local_in_filter)} repos...{RESET}\n")
            updated = 0
            for name in sorted(local_in_filter):
                repo_path = TAC_ROOT / name
                if check_repo_has_updates(repo_path):
                    print(f"{BLUE}Updating: {name}{RESET}")
                    if pull_repo_updates(repo_path):
                        updated += 1

            print(f"\n{GREEN}Updated {updated} repositories{RESET}")
            print(f"{DIM}Run /sync-tac-repos --full <repo> to reprocess updated repos{RESET}")
            return

        if args.sync:
            # Filter to repos updated after MIN_DATE and find new ones
            recent_repos = filter_repos_by_date(github_repos)
            github_names = {r['name'] for r in recent_repos}
            new_repos = github_names - local_repos

            if not new_repos:
                print(f"{GREEN}All repositories are synced!{RESET}")
                return

            print(f"\n{BOLD}Syncing {len(new_repos)} new repositories...{RESET}\n")

            for name in sorted(new_repos):
                print(f"\n{BLUE}Processing: {name}{RESET}")

                # Step 1: Clone
                if clone_repo(name):
                    repo_path = TAC_ROOT / name

                    # Step 2: Scan components
                    components = scan_components(repo_path)
                    total = (len(components.agents) + len(components.commands) +
                            len(components.hooks) + len(components.skills) +
                            len(components.adws))
                    print(f"  Found {total} components")

                    # Step 3: Generate prompt for TAC summary
                    prompt = generate_tac_summary_prompt(name)
                    print(f"  TAC summary prompt generated")
                    print(f"  {DIM}Run: Task(subagent_type='tac', prompt=...){RESET}")

                    # Note: Actual TAC agent invocation, vector indexing,
                    # Graphiti sync, and Obsidian note creation should be
                    # done by the agentic command, not this script

            print(f"\n{GREEN}Clone complete. Run /sync-tac-repos --full <repo> for each to complete processing.{RESET}")
            return

    if args.full:
        repo_name = args.full
        repo_path = TAC_ROOT / repo_name

        if not repo_path.exists():
            print(f"{RED}Repository not found: {repo_path}{RESET}")
            return

        print(f"\n{BOLD}Full Processing: {repo_name}{RESET}\n")

        # Scan components
        components = scan_components(repo_path)

        if args.json:
            output = {
                "name": repo_name,
                "path": str(repo_path),
                "components": asdict(components),
                "tac_summary_exists": check_tac_summary(repo_path),
                "obsidian_note_exists": check_obsidian_note(repo_name),
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Path: {repo_path}")
            print(f"\n{BOLD}Components:{RESET}")
            print(f"  Agents:   {len(components.agents):3d} - {', '.join(components.agents) or '-'}")
            print(f"  Commands: {len(components.commands):3d} - {', '.join(components.commands[:5]) or '-'}{'...' if len(components.commands) > 5 else ''}")
            print(f"  Hooks:    {len(components.hooks):3d} - {', '.join(components.hooks) or '-'}")
            print(f"  Skills:   {len(components.skills):3d} - {', '.join(components.skills) or '-'}")
            print(f"  ADWs:     {len(components.adws):3d} - {', '.join(components.adws) or '-'}")

            print(f"\n{BOLD}Status:{RESET}")
            summary_status = f"{GREEN}✓{RESET}" if check_tac_summary(repo_path) else f"{RED}✗{RESET}"
            obsidian_status = f"{GREEN}✓{RESET}" if check_obsidian_note(repo_name) else f"{RED}✗{RESET}"
            print(f"  TAC Summary: {summary_status}")
            print(f"  Obsidian Note: {obsidian_status}")

            # Print TAC summary prompt
            print(f"\n{BOLD}TAC Analysis Prompt:{RESET}")
            print(f"{DIM}Use with: Task(subagent_type='tac', ...){RESET}\n")
            prompt = generate_tac_summary_prompt(repo_name)
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

        return

    parser.print_help()


if __name__ == "__main__":
    main()
