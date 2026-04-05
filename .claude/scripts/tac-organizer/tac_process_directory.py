#!/usr/bin/env python3
"""
TAC Directory Processor

Processes TAC repository directories for knowledge base ingestion.
Supports both Graphiti (knowledge graph) and pgvector (vector index).

Usage:
    python tac_process_directory.py tac-3              # Process single directory
    python tac_process_directory.py --all              # Process all directories
    python tac_process_directory.py --list             # List all directories
    python tac_process_directory.py --dry-run tac-3    # Preview without ingesting
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
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
STATUS_FILE = Path(".claude/data/tac-processing-status.json")

# TAC Directory Metadata
TAC_DIRECTORIES = {
    # Core Tactics
    "tac-1": {"lesson": 1, "topic": "Stop Coding"},
    "tac-2": {"lesson": 2, "topic": "Adopt Your Agent's Perspective"},
    "tac-3": {"lesson": 3, "topic": "Template Your Engineering"},
    "tac-4": {"lesson": 4, "topic": "Stay Out The Loop (PITER)"},
    "tac-5": {"lesson": 5, "topic": "Always Add Feedback Loops"},
    "tac-6": {"lesson": 6, "topic": "One Agent, One Prompt, One Purpose"},
    "tac-7": {"lesson": 7, "topic": "Target Zero-Touch Engineering"},
    "tac-8": {"lesson": 8, "topic": "Prioritize Agentics"},
    # Advanced Lessons
    "rd-framework-context-window-mastery": {"lesson": 9, "topic": "Elite Context Engineering (R&D Framework)"},
    "seven-levels-agentic-prompt-formats": {"lesson": 10, "topic": "Agentic Prompt Engineering (7 Levels/HOP)"},
    "building-domain-specific-agents": {"lesson": 11, "topic": "Building Specialized Agents"},
    "multi-agent-orchestration-the-o-agent": {"lesson": 12, "topic": "Multi-Agent Orchestration (O-Agent)"},
    "agent-experts": {"lesson": 13, "topic": "Agent-Experts (ACT-LEARN-REUSE)"},
    "orchestrator-agent-with-adws": {"lesson": 14, "topic": "Orchestrator Agent with ADWs"},
    "agentic-finance-review": {"lesson": 15, "topic": "Software Delivery ADW"},
    # Supporting Repositories
    "claude-code-hooks-mastery": {"lesson": None, "topic": "Lifecycle Hooks Deep Dive"},
    "claude-code-damage-control": {"lesson": None, "topic": "Defense-in-Depth Safety Patterns"},
    "agent-sandboxes": {"lesson": None, "topic": "Environment Isolation Patterns"},
    "agent-sandbox-skill": {"lesson": None, "topic": "Sandbox Skill Template"},
    "fork-repository-skill": {"lesson": None, "topic": "Fork Repository Skill"},
}


@dataclass
class ComponentInventory:
    """Inventory of components found in a TAC directory."""
    commands: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    agents: list = field(default_factory=list)
    adws: list = field(default_factory=list)
    hooks: list = field(default_factory=list)


@dataclass
class TACDirectorySummary:
    """Summary of a processed TAC directory."""
    name: str
    type: str = "tac_repository"
    lesson: Optional[int] = None
    topic: str = ""
    path: str = ""
    summary: str = ""
    key_concepts: list = field(default_factory=list)
    frameworks: list = field(default_factory=list)
    patterns: list = field(default_factory=list)
    components: ComponentInventory = field(default_factory=ComponentInventory)
    readme_content: str = ""
    claude_md_content: str = ""


def load_status() -> dict:
    """Load processing status from file."""
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {"last_updated": None, "directories": {}}


def save_status(status: dict):
    """Save processing status to file."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    status["last_updated"] = datetime.now().isoformat()
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def extract_summary_from_readme(readme_path: Path) -> tuple[str, list]:
    """Extract summary and key concepts from README.md."""
    if not readme_path.exists():
        return "", []

    content = readme_path.read_text(encoding="utf-8", errors="ignore")

    # Extract first meaningful paragraph as summary
    lines = content.split("\n")
    summary_lines = []
    in_summary = False

    for line in lines:
        # Skip headers and empty lines at start
        if line.startswith("#") or line.strip() == "":
            if in_summary:
                break
            continue
        # Skip badges/images
        if line.startswith("![") or line.startswith("<"):
            continue
        in_summary = True
        summary_lines.append(line.strip())
        if len(" ".join(summary_lines)) > 300:
            break

    summary = " ".join(summary_lines)[:500]

    # Extract key concepts (look for headers, bullet points)
    concepts = []
    concept_pattern = r"^##\s+(.+)$"
    for match in re.finditer(concept_pattern, content, re.MULTILINE):
        concept = match.group(1).strip()
        if concept.lower() not in ["installation", "setup", "usage", "license", "contributing"]:
            concepts.append(concept)
            if len(concepts) >= 5:
                break

    return summary, concepts


def scan_claude_folder(claude_path: Path) -> ComponentInventory:
    """Scan .claude folder for commands, skills, agents, hooks."""
    inventory = ComponentInventory()

    if not claude_path.exists():
        return inventory

    # Scan commands
    commands_path = claude_path / "commands"
    if commands_path.exists():
        for f in commands_path.glob("*.md"):
            inventory.commands.append(f.stem)

    # Scan skills
    skills_path = claude_path / "skills"
    if skills_path.exists():
        for d in skills_path.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                inventory.skills.append(d.name)

    # Scan agents
    agents_path = claude_path / "agents"
    if agents_path.exists():
        for f in agents_path.glob("*.md"):
            inventory.agents.append(f.stem)

    # Scan hooks
    hooks_path = claude_path / "hooks"
    if hooks_path.exists():
        for f in hooks_path.glob("*.py"):
            inventory.hooks.append(f.stem)
        for f in hooks_path.glob("*.md"):
            inventory.hooks.append(f.stem)

    return inventory


def scan_adws_folder(adws_path: Path) -> list:
    """Scan adws folder for ADW definitions."""
    adws = []
    if not adws_path.exists():
        return adws

    for f in adws_path.glob("*.md"):
        adws.append(f.stem)

    return adws


def process_directory(dir_name: str, dry_run: bool = False) -> Optional[TACDirectorySummary]:
    """Process a single TAC directory."""
    dir_path = TAC_ROOT / dir_name

    if not dir_path.exists():
        print(f"{RED}Directory not found: {dir_path}{RESET}")
        return None

    # Get metadata
    meta = TAC_DIRECTORIES.get(dir_name, {"lesson": None, "topic": dir_name})

    # Create summary
    summary = TACDirectorySummary(
        name=dir_name,
        lesson=meta.get("lesson"),
        topic=meta.get("topic", ""),
        path=str(dir_path),
    )

    # Extract from README
    readme_path = dir_path / "README.md"
    summary.summary, summary.key_concepts = extract_summary_from_readme(readme_path)
    if readme_path.exists():
        summary.readme_content = readme_path.read_text(encoding="utf-8", errors="ignore")[:5000]

    # Extract from CLAUDE.md
    claude_md_path = dir_path / "CLAUDE.md"
    if claude_md_path.exists():
        summary.claude_md_content = claude_md_path.read_text(encoding="utf-8", errors="ignore")[:2000]

    # Scan .claude folder
    claude_path = dir_path / ".claude"
    summary.components = scan_claude_folder(claude_path)

    # Scan adws folder
    adws_path = dir_path / "adws"
    summary.components.adws = scan_adws_folder(adws_path)

    # Detect frameworks and patterns from content
    content_lower = (summary.readme_content + summary.claude_md_content).lower()

    frameworks = []
    if "piter" in content_lower:
        frameworks.append("PITER")
    if "r&d" in content_lower or "reduce" in content_lower and "delegate" in content_lower:
        frameworks.append("R&D")
    if "act" in content_lower and "learn" in content_lower and "reuse" in content_lower:
        frameworks.append("ACT-LEARN-REUSE")
    if "core four" in content_lower:
        frameworks.append("Core Four")
    summary.frameworks = frameworks

    patterns = []
    if "pong" in content_lower:
        patterns.append("Pong")
    if "echo" in content_lower and "pattern" in content_lower:
        patterns.append("Echo")
    if "calculator" in content_lower and "pattern" in content_lower:
        patterns.append("Calculator")
    if "orchestrator" in content_lower or "o-agent" in content_lower:
        patterns.append("Orchestrator")
    summary.patterns = patterns

    return summary


def format_summary_for_display(summary: TACDirectorySummary) -> str:
    """Format summary for terminal display."""
    lesson_str = f"Lesson {summary.lesson}" if summary.lesson else "Supporting"

    output = []
    output.append(f"\n{BOLD}## TAC Directory: {summary.name}{RESET}")
    output.append(f"{DIM}{lesson_str} - {summary.topic}{RESET}\n")

    output.append(f"{BOLD}### Summary{RESET}")
    output.append(summary.summary[:300] + "..." if len(summary.summary) > 300 else summary.summary)
    output.append("")

    if summary.key_concepts:
        output.append(f"{BOLD}### Key Concepts{RESET}")
        for concept in summary.key_concepts[:5]:
            output.append(f"  - {concept}")
        output.append("")

    if summary.frameworks:
        output.append(f"{BOLD}### Frameworks{RESET}")
        output.append(f"  {', '.join(summary.frameworks)}")
        output.append("")

    if summary.patterns:
        output.append(f"{BOLD}### Patterns{RESET}")
        output.append(f"  {', '.join(summary.patterns)}")
        output.append("")

    output.append(f"{BOLD}### Components Found{RESET}")
    output.append(f"  Commands: {len(summary.components.commands)} - {', '.join(summary.components.commands) or '-'}")
    output.append(f"  Skills:   {len(summary.components.skills)} - {', '.join(summary.components.skills) or '-'}")
    output.append(f"  Agents:   {len(summary.components.agents)} - {', '.join(summary.components.agents) or '-'}")
    output.append(f"  ADWs:     {len(summary.components.adws)} - {', '.join(summary.components.adws) or '-'}")
    output.append(f"  Hooks:    {len(summary.components.hooks)} - {', '.join(summary.components.hooks) or '-'}")

    return "\n".join(output)


def format_summary_for_ingestion(summary: TACDirectorySummary) -> str:
    """Format summary as structured text for knowledge base ingestion."""
    parts = []

    parts.append(f"TAC Repository: {summary.name}")
    if summary.lesson:
        parts.append(f"Lesson {summary.lesson}: {summary.topic}")
    else:
        parts.append(f"Topic: {summary.topic}")

    parts.append(f"\nSummary:\n{summary.summary}")

    if summary.key_concepts:
        parts.append(f"\nKey Concepts:")
        for concept in summary.key_concepts:
            parts.append(f"- {concept}")

    if summary.frameworks:
        parts.append(f"\nFrameworks: {', '.join(summary.frameworks)}")

    if summary.patterns:
        parts.append(f"\nPatterns: {', '.join(summary.patterns)}")

    parts.append(f"\nComponents:")
    if summary.components.commands:
        parts.append(f"- Commands: {', '.join(summary.components.commands)}")
    if summary.components.skills:
        parts.append(f"- Skills: {', '.join(summary.components.skills)}")
    if summary.components.agents:
        parts.append(f"- Agents: {', '.join(summary.components.agents)}")
    if summary.components.adws:
        parts.append(f"- ADWs: {', '.join(summary.components.adws)}")
    if summary.components.hooks:
        parts.append(f"- Hooks: {', '.join(summary.components.hooks)}")

    parts.append(f"\nPath: {summary.path}")

    return "\n".join(parts)


def list_directories():
    """List all TAC directories with their status."""
    status = load_status()

    print(f"\n{BOLD}TAC Directory Inventory{RESET}")
    print(f"{DIM}Root: {TAC_ROOT}{RESET}\n")

    # Check which directories exist
    existing = []
    for name in sorted(TAC_DIRECTORIES.keys()):
        dir_path = TAC_ROOT / name
        exists = dir_path.exists()
        processed = status.get("directories", {}).get(name, {}).get("processed", False)

        meta = TAC_DIRECTORIES[name]
        lesson = f"L{meta['lesson']:02d}" if meta['lesson'] else "---"

        status_icon = f"{GREEN}[x]{RESET}" if processed else f"{YELLOW}[ ]{RESET}"
        exists_icon = f"{GREEN}OK{RESET}" if exists else f"{RED}MISSING{RESET}"

        print(f"  {status_icon} {lesson} {name:<45} {exists_icon}")

        if exists:
            existing.append(name)

    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Total defined: {len(TAC_DIRECTORIES)}")
    print(f"  Existing:      {len(existing)}")
    processed_count = sum(1 for d in status.get("directories", {}).values() if d.get("processed"))
    print(f"  Processed:     {processed_count}")


def main():
    parser = argparse.ArgumentParser(description="Process TAC directories for KB ingestion")
    parser.add_argument("directory", nargs="?", help="Directory name to process")
    parser.add_argument("--all", action="store_true", help="Process all directories")
    parser.add_argument("--list", action="store_true", help="List all directories")
    parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--force", action="store_true", help="Re-process even if already done")
    args = parser.parse_args()

    if args.list:
        list_directories()
        return

    if args.all:
        # Process all directories
        status = load_status()
        summaries = []

        for dir_name in sorted(TAC_DIRECTORIES.keys()):
            if not args.force and status.get("directories", {}).get(dir_name, {}).get("processed"):
                print(f"{DIM}Skipping {dir_name} (already processed){RESET}")
                continue

            dir_path = TAC_ROOT / dir_name
            if not dir_path.exists():
                print(f"{YELLOW}Skipping {dir_name} (not found){RESET}")
                continue

            print(f"{BLUE}Processing {dir_name}...{RESET}")
            summary = process_directory(dir_name, dry_run=args.dry_run)
            if summary:
                summaries.append(summary)
                if not args.dry_run:
                    status["directories"][dir_name] = {
                        "processed": True,
                        "last_processed": datetime.now().isoformat(),
                        "components": len(summary.components.commands) + len(summary.components.skills) +
                                     len(summary.components.agents) + len(summary.components.adws)
                    }

        if not args.dry_run:
            save_status(status)

        print(f"\n{GREEN}Processed {len(summaries)} directories{RESET}")

        if args.json:
            output = [asdict(s) for s in summaries]
            print(json.dumps(output, indent=2, default=str))

    elif args.directory:
        # Process single directory
        summary = process_directory(args.directory, dry_run=args.dry_run)
        if summary:
            if args.json:
                print(json.dumps(asdict(summary), indent=2, default=str))
            else:
                print(format_summary_for_display(summary))
                print(f"\n{DIM}--- Ingestion Content ---{RESET}")
                print(format_summary_for_ingestion(summary))

            if not args.dry_run:
                status = load_status()
                status["directories"][args.directory] = {
                    "processed": True,
                    "last_processed": datetime.now().isoformat(),
                }
                save_status(status)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
