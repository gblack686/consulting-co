#!/usr/bin/env python3
"""
Generate ecosystem-inventory.json and workflow-analysis.json for each source directory.
"""
import json
import os
from datetime import datetime
from pathlib import Path

# Load results
RESULTS_FILE = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/scripts/non-tac-sync-results.json")

def main():
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

    details = data.get('details', [])

    created_dirs = 0
    created_inventories = 0
    created_analyses = 0

    for item in details:
        dir_path = Path(item['directory'])
        if not item.get('exists'):
            continue

        components = item.get('components', {})
        total = sum(components.values()) if components else 0
        if total == 0:
            continue

        # Create sync-claude-ecosystem directory
        sync_dir = dir_path / "sync-claude-ecosystem"
        sync_dir.mkdir(parents=True, exist_ok=True)
        created_dirs += 1

        # Get project name
        project = dir_path.parent.name

        # Build ecosystem inventory
        inventory = {
            "generated": datetime.now().isoformat(),
            "source_directory": str(dir_path),
            "project_name": project,
            "tac_original": False,
            "human_reviewed": False,
            "components": {
                "agents": components.get('agents_count', 0),
                "commands": components.get('commands_count', 0),
                "hooks": components.get('hooks_count', 0),
                "skills": components.get('skills_count', 0)
            },
            "total_components": total,
            "notes_created": len(item.get('notes_created', [])),
            "notes_skipped": len(item.get('notes_skipped', [])),
            "created_notes": [n.get('name') for n in item.get('notes_created', [])],
            "skipped_notes": [n.get('name') for n in item.get('notes_skipped', [])]
        }

        inventory_path = sync_dir / "ecosystem-inventory.json"
        with open(inventory_path, 'w') as f:
            json.dump(inventory, f, indent=2)
        created_inventories += 1

        # Classify workflow type
        has_hooks = components.get('hooks_count', 0) > 0
        has_skills = components.get('skills_count', 0) > 0
        total_steps = components.get('agents_count', 0) + components.get('commands_count', 0)

        if has_hooks and has_skills:
            workflow_type = "ADW"
            description = "Autonomous Developer Workflow with hooks and skills infrastructure"
        elif total_steps >= 3:
            workflow_type = "Agentic Prompt"
            description = "Multi-step agentic workflow with 3+ steps"
        else:
            workflow_type = "Command"
            description = "Simple command or utility with fewer than 3 steps"

        # Build workflow analysis
        analysis = {
            "generated": datetime.now().isoformat(),
            "source_directory": str(dir_path),
            "project_name": project,
            "workflow_classification": {
                "type": workflow_type,
                "description": description,
                "criteria": {
                    "has_hooks": has_hooks,
                    "has_skills": has_skills,
                    "total_steps": total_steps,
                    "agents_count": components.get('agents_count', 0),
                    "commands_count": components.get('commands_count', 0)
                }
            },
            "recommendation": f"This project is classified as a {workflow_type}. " + (
                "Consider documenting the orchestration flow and hook behaviors." if workflow_type == "ADW" else
                "Consider breaking down into reusable components." if workflow_type == "Agentic Prompt" else
                "Simple utility - well-suited for single-purpose use."
            )
        }

        analysis_path = sync_dir / "workflow-analysis.json"
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        created_analyses += 1

    print(f"Created {created_dirs} sync-claude-ecosystem directories")
    print(f"Created {created_inventories} ecosystem-inventory.json files")
    print(f"Created {created_analyses} workflow-analysis.json files")

if __name__ == "__main__":
    main()
