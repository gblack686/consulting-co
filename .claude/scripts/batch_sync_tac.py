#!/usr/bin/env python3
"""
Batch sync TAC .claude directories to Obsidian AI-Agent-KB
Processes 24 TAC directories and creates Obsidian notes for Claude ecosystem components.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import re

# Configuration
OBSIDIAN_KB = Path("C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB")
TEMPLATES_DIR = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills/obsidian-agent-archiver/templates")
PROGRESS_FILE = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/scripts/batch-sync-progress.json")

# TAC Directories to process
TAC_DIRS = [
    # TAC Course Projects (12)
    "C:/Users/gblac/OneDrive/Desktop/tac/agent-experts/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/agent-sandbox-skill/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/agent-sandboxes/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/agentic-finance-review/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/building-domain-specific-agents/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/claude-code-damage-control/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/claude-code-hooks-mastery/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/fork-repository-skill/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration-the-o-agent/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/rd-framework-context-window-mastery/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/seven-levels-agentic-prompt-formats/.claude",
    # TAC Numbered Projects (7)
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-1/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-2/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-5/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-6/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-7/.claude",
    # TAC-8 Sub-Projects (5)
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app1__agent_layer_primitives/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app2__multi_agent_todone/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app3__out_loop_multi_agent_task_board/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app4__agentic_prototyping/.claude",
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app5__nlq_to_sql_aea/.claude",
]

# Obsidian folder mapping
OBSIDIAN_FOLDERS = {
    "agents": "02-Agents",
    "commands": "08-Commands",  # Note: There's also 09-Commands, using 08
    "hooks": "08-Hooks",
    "skills": "03-Skills",
    "experts": "07-Experts",
}


def get_project_name(claude_dir: str) -> str:
    """Extract project name from .claude directory path."""
    parent = Path(claude_dir).parent.name
    return parent


def scan_claude_folder(claude_dir: Path) -> dict:
    """Scan a .claude folder for ecosystem components."""
    components = {
        "agents": [],
        "commands": [],
        "hooks": [],
        "skills": [],
        "experts": [],
    }

    if not claude_dir.exists():
        return components

    # Scan agents
    agents_dir = claude_dir / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            if not f.name.startswith("_"):
                components["agents"].append({
                    "name": f.stem,
                    "path": str(f),
                    "type": "agent"
                })

    # Scan commands (could be in commands/ or commands/subfolders)
    commands_dir = claude_dir / "commands"
    if commands_dir.exists():
        for f in commands_dir.rglob("*.md"):
            if not f.name.startswith("_"):
                # Check if it's an expert
                if "experts" in str(f.parent):
                    components["experts"].append({
                        "name": f.stem,
                        "path": str(f),
                        "type": "expert",
                        "parent_folder": f.parent.name
                    })
                else:
                    components["commands"].append({
                        "name": f.stem,
                        "path": str(f),
                        "type": "command"
                    })

    # Scan hooks
    hooks_dir = claude_dir / "hooks"
    if hooks_dir.exists():
        for f in hooks_dir.glob("*.py"):
            if not f.name.startswith("_") and f.name != "__init__.py":
                components["hooks"].append({
                    "name": f.stem,
                    "path": str(f),
                    "type": "hook"
                })

    # Scan skills
    skills_dir = claude_dir / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir() and not d.name.startswith("_"):
                skill_md = d / "SKILL.md"
                if skill_md.exists():
                    components["skills"].append({
                        "name": d.name,
                        "path": str(d),
                        "type": "skill"
                    })

    return components


def check_obsidian_exists(component_name: str, component_type: str) -> bool:
    """Check if a component already exists in Obsidian."""
    folder = OBSIDIAN_FOLDERS.get(component_type + "s", OBSIDIAN_FOLDERS.get(component_type))
    if not folder:
        return False

    obsidian_path = OBSIDIAN_KB / folder / f"{component_name}.md"
    return obsidian_path.exists()


def classify_workflow(content: str) -> str:
    """Classify a workflow based on step count and infrastructure markers."""
    # Count workflow steps
    step_patterns = [
        r'^\d+\.',  # 1. Step
        r'^- ',      # - Step
        r'## Step \d+',
        r'### \d+\.',
    ]

    step_count = 0
    for line in content.split('\n'):
        for pattern in step_patterns:
            if re.match(pattern, line.strip()):
                step_count += 1
                break

    # Check for ADW markers
    adw_markers = ['orchestrator', 'docker', 'subprocess', 'asyncio', 'logs/', 'background']
    has_adw_markers = any(marker in content.lower() for marker in adw_markers)

    if has_adw_markers:
        return "ADW"
    elif step_count >= 3:
        return "Agentic Prompt"
    else:
        return "Command"


def create_obsidian_note(component: dict, project_name: str, content: str = None) -> str:
    """Create an Obsidian note for a component."""
    comp_type = component["type"]
    comp_name = component["name"]
    today = datetime.now().strftime("%Y-%m-%d")

    # Build frontmatter
    frontmatter = f"""---
type: {comp_type}
name: "{comp_name}"
source_repo: "tac/{project_name}"
source_path: "{component['path']}"
status: active
created: {today}
updated: {today}
human_reviewed: false
tac_original: true
tags: [{comp_type}, tac-course]
cssclasses: [ai-agent-kb]
---

"""

    # Build content
    if content:
        # Strip any existing frontmatter from source content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        return frontmatter + f"# {comp_name}\n\n> **Source**: TAC Course - {project_name}\n\n" + content
    else:
        return frontmatter + f"# {comp_name}\n\n> **Source**: TAC Course - {project_name}\n\n*Content to be extracted from source.*\n"


def process_directory(claude_dir: str, progress: dict) -> dict:
    """Process a single .claude directory."""
    dir_path = Path(claude_dir)
    project_name = get_project_name(claude_dir)

    result = {
        "directory": claude_dir,
        "project_name": project_name,
        "exists": dir_path.exists(),
        "components_found": 0,
        "components_new": 0,
        "components_existing": 0,
        "created_notes": [],
        "existing_notes": [],
        "errors": [],
        "workflow_analysis": []
    }

    if not dir_path.exists():
        result["errors"].append("Directory does not exist")
        return result

    # Create output directory
    output_dir = dir_path / "sync-claude-ecosystem"
    output_dir.mkdir(exist_ok=True)

    # Scan components
    components = scan_claude_folder(dir_path)

    inventory = {
        "project": project_name,
        "source_path": claude_dir,
        "scanned_at": datetime.now().isoformat(),
        "tac_original": True,
        "components": components
    }

    # Count and process components
    for comp_type, comp_list in components.items():
        for comp in comp_list:
            result["components_found"] += 1

            # Check if exists in Obsidian
            exists = check_obsidian_exists(comp["name"], comp["type"])
            comp["exists_in_obsidian"] = exists

            if exists:
                result["components_existing"] += 1
                result["existing_notes"].append(comp["name"])
            else:
                result["components_new"] += 1

                # Read source content if available
                source_content = None
                try:
                    if Path(comp["path"]).exists():
                        source_content = Path(comp["path"]).read_text(encoding='utf-8')
                except Exception as e:
                    result["errors"].append(f"Error reading {comp['path']}: {str(e)}")

                # Classify workflow
                if source_content:
                    workflow_type = classify_workflow(source_content)
                    comp["workflow_classification"] = workflow_type
                    result["workflow_analysis"].append({
                        "name": comp["name"],
                        "type": comp["type"],
                        "classification": workflow_type
                    })

                # Create Obsidian note
                try:
                    folder = OBSIDIAN_FOLDERS.get(comp_type, "08-Commands")

                    # Handle skills as folders
                    if comp_type == "skills":
                        skill_dir = OBSIDIAN_KB / folder / comp["name"]
                        skill_dir.mkdir(exist_ok=True)
                        note_path = skill_dir / f"{comp['name']}.md"
                    else:
                        note_path = OBSIDIAN_KB / folder / f"{comp['name']}.md"

                    note_content = create_obsidian_note(comp, project_name, source_content)
                    note_path.write_text(note_content, encoding='utf-8')
                    result["created_notes"].append(str(note_path))
                except Exception as e:
                    result["errors"].append(f"Error creating note for {comp['name']}: {str(e)}")

    # Save inventory
    inventory_path = output_dir / "ecosystem-inventory.json"
    with open(inventory_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2)

    # Save workflow analysis
    if result["workflow_analysis"]:
        analysis_path = output_dir / "workflow-analysis.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump({
                "project": project_name,
                "analyzed_at": datetime.now().isoformat(),
                "workflows": result["workflow_analysis"]
            }, f, indent=2)

    return result


def main():
    """Main batch processing function."""
    # Initialize progress
    progress = {
        "started": datetime.now().isoformat(),
        "current_index": 0,
        "completed": [],
        "failed": [],
        "skipped": [],
        "total": len(TAC_DIRS),
        "results": []
    }

    print(f"Starting batch sync of {len(TAC_DIRS)} TAC directories...")
    print(f"Obsidian KB: {OBSIDIAN_KB}")
    print("-" * 60)

    for idx, claude_dir in enumerate(TAC_DIRS):
        progress["current_index"] = idx + 1
        project_name = get_project_name(claude_dir)

        print(f"\n[{idx + 1}/{len(TAC_DIRS)}] Processing: {project_name}")

        try:
            result = process_directory(claude_dir, progress)

            if result["exists"]:
                progress["completed"].append(claude_dir)
                status = "OK"
            else:
                progress["skipped"].append(claude_dir)
                status = "SKIPPED (not found)"

            progress["results"].append(result)

            print(f"  Status: {status}")
            print(f"  Components: {result['components_found']} found, {result['components_new']} new, {result['components_existing']} existing")
            if result["created_notes"]:
                print(f"  Created: {len(result['created_notes'])} notes")
            if result["errors"]:
                print(f"  Errors: {len(result['errors'])}")
                for err in result["errors"][:3]:
                    print(f"    - {err}")

        except Exception as e:
            progress["failed"].append(claude_dir)
            progress["results"].append({
                "directory": claude_dir,
                "project_name": project_name,
                "error": str(e)
            })
            print(f"  ERROR: {str(e)}")

        # Save progress after each directory
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)

    # Final summary
    progress["completed_at"] = datetime.now().isoformat()

    print("\n" + "=" * 60)
    print("BATCH SYNC COMPLETE")
    print("=" * 60)
    print(f"Total directories: {progress['total']}")
    print(f"Completed: {len(progress['completed'])}")
    print(f"Skipped: {len(progress['skipped'])}")
    print(f"Failed: {len(progress['failed'])}")

    # Calculate totals
    total_found = sum(r.get("components_found", 0) for r in progress["results"])
    total_new = sum(r.get("components_new", 0) for r in progress["results"])
    total_existing = sum(r.get("components_existing", 0) for r in progress["results"])
    total_created = sum(len(r.get("created_notes", [])) for r in progress["results"])

    print(f"\nComponents found: {total_found}")
    print(f"  New: {total_new}")
    print(f"  Existing: {total_existing}")
    print(f"Notes created: {total_created}")

    # Save final progress
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)

    print(f"\nProgress saved to: {PROGRESS_FILE}")

    return progress


if __name__ == "__main__":
    main()
