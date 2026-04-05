"""
Extract all entities from a TAC repository and save to JSON

Outputs:
- prompts.json: All prompt entities
- scripts.json: All ADW script entities
- catalog.json: Combined catalog with metadata
"""

import json
from pathlib import Path
from datetime import datetime
from prompt_parser import parse_tac_directory, PromptEntity
from adw_script_parser import parse_adw_scripts, ADWScriptEntity
from dataclasses import asdict


def entity_to_dict(entity):
    """Convert entity to dict for JSON serialization"""
    return asdict(entity)


def extract_tac_repo(repo_path: Path, output_dir: Path):
    """
    Extract all entities from TAC repo and save to JSON files

    Args:
        repo_path: Path to TAC repository root
        output_dir: Where to save output files
    """
    repo_path = Path(repo_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting from: {repo_path}")
    print(f"Output directory: {output_dir}")

    # Extract prompts
    print("\n" + "=" * 60)
    print("EXTRACTING PROMPTS")
    print("=" * 60)
    prompts = parse_tac_directory(repo_path)
    print(f"Found {len(prompts)} prompts")

    # Extract ADW scripts
    print("\n" + "=" * 60)
    print("EXTRACTING ADW SCRIPTS")
    print("=" * 60)
    scripts = parse_adw_scripts(repo_path)
    print(f"Found {len(scripts)} ADW scripts")

    # Convert to dicts
    prompts_data = [entity_to_dict(p) for p in prompts]
    scripts_data = [entity_to_dict(s) for s in scripts]

    # Save individual files
    prompts_file = output_dir / "prompts.json"
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(prompts_data, f, indent=2)
    print(f"\nSaved prompts to: {prompts_file}")

    scripts_file = output_dir / "scripts.json"
    with open(scripts_file, 'w', encoding='utf-8') as f:
        json.dump(scripts_data, f, indent=2)
    print(f"Saved scripts to: {scripts_file}")

    # Create combined catalog
    catalog = {
        "metadata": {
            "repo_path": str(repo_path),
            "repo_name": repo_path.name,
            "extracted_at": datetime.now().isoformat(),
            "prompt_count": len(prompts),
            "script_count": len(scripts),
        },
        "prompts": prompts_data,
        "scripts": scripts_data,
        "statistics": {
            "prompt_types": count_prompt_types(prompts),
            "total_delegations": sum(len(p.delegations) for p in prompts),
            "total_workflow_steps": sum(len(p.workflow_steps) for p in prompts),
        }
    }

    catalog_file = output_dir / "catalog.json"
    with open(catalog_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    print(f"Saved catalog to: {catalog_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Repository: {repo_path.name}")
    print(f"Prompts: {len(prompts)}")
    print(f"  - Simple tasks: {catalog['statistics']['prompt_types'].get('simple-task', 0)}")
    print(f"  - Simple workflows: {catalog['statistics']['prompt_types'].get('simple-workflow', 0)}")
    print(f"  - Complex workflows: {catalog['statistics']['prompt_types'].get('complex-workflow', 0)}")
    print(f"  - Orchestration: {catalog['statistics']['prompt_types'].get('orchestration', 0)}")
    print(f"  - Meta-prompts: {catalog['statistics']['prompt_types'].get('meta-prompt', 0)}")
    print(f"Scripts: {len(scripts)}")
    print(f"Total delegations: {catalog['statistics']['total_delegations']}")
    print(f"Total workflow steps: {catalog['statistics']['total_workflow_steps']}")

    # Print prompt details
    print("\n" + "=" * 60)
    print("PROMPT DETAILS")
    print("=" * 60)
    for prompt in prompts:
        print(f"\n📄 {prompt.name}")
        print(f"   Type: {prompt.prompt_type}")
        print(f"   File: {Path(prompt.file_path).relative_to(repo_path)}")
        if prompt.delegations:
            print(f"   Delegates to: {', '.join(prompt.delegations[:5])}")
        if prompt.workflow_steps:
            print(f"   Workflow: {len(prompt.workflow_steps)} steps")
        if prompt.tools_mentioned:
            print(f"   Tools: {', '.join(prompt.tools_mentioned)}")

    if scripts:
        print("\n" + "=" * 60)
        print("SCRIPT DETAILS")
        print("=" * 60)
        for script in scripts:
            print(f"\n🔧 {script.name}")
            print(f"   File: {Path(script.file_path).relative_to(repo_path)}")
            if script.purpose:
                print(f"   Purpose: {script.purpose[:80]}...")
            if script.prompts_invoked:
                print(f"   Invokes: {', '.join(script.prompts_invoked)}")

    return catalog


def count_prompt_types(prompts: list[PromptEntity]) -> dict:
    """Count prompts by type"""
    counts = {}
    for prompt in prompts:
        counts[prompt.prompt_type] = counts.get(prompt.prompt_type, 0) + 1
    return counts


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
    else:
        repo_path = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")

    # Output to tac-learning-system/data/
    output_dir = Path(__file__).parent.parent / "data" / repo_path.name

    catalog = extract_tac_repo(repo_path, output_dir)
