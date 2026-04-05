#!/usr/bin/env python3
"""
Sync non-TAC .claude directories to Obsidian AI-Agent-KB.
Processes 86 directories, scans components, creates Obsidian notes.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import re

# Key paths
OBSIDIAN_KB = Path("C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB")
TEMPLATE_DIR = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills/obsidian-agent-archiver/templates")
PROGRESS_FILE = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/scripts/non-tac-sync-progress.json")
DIR_LIST_FILE = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/scripts/all-claude-directories.json")

def load_directories():
    """Load the list of directories to process."""
    with open(DIR_LIST_FILE, 'r') as f:
        data = json.load(f)
    return data.get('all_non_tac_directories', [])

def get_existing_obsidian_notes():
    """Get set of existing notes in Obsidian KB."""
    existing = {
        'agents': set(),
        'commands': set(),
        'hooks': set(),
        'skills': set()
    }

    # Agents
    agents_dir = OBSIDIAN_KB / "02-Agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            name = f.stem.lower().replace('-', '_').replace(' ', '_')
            existing['agents'].add(name)

    # Commands
    commands_dir = OBSIDIAN_KB / "08-Commands"
    if commands_dir.exists():
        for f in commands_dir.glob("*.md"):
            name = f.stem.lower().replace('-', '_').replace(' ', '_')
            existing['commands'].add(name)

    # Hooks
    hooks_dir = OBSIDIAN_KB / "08-Hooks"
    if hooks_dir.exists():
        for f in hooks_dir.glob("*.md"):
            name = f.stem.lower().replace('-', '_').replace(' ', '_')
            existing['hooks'].add(name)

    # Skills
    skills_dir = OBSIDIAN_KB / "03-Skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir():
                name = d.name.lower().replace('-', '_').replace(' ', '_')
                existing['skills'].add(name)

    return existing

def normalize_name(name):
    """Normalize component name for comparison."""
    return name.lower().replace('-', '_').replace(' ', '_')

def scan_directory(claude_dir):
    """Scan a .claude directory for components."""
    components = {
        'agents': [],
        'commands': [],
        'hooks': [],
        'skills': []
    }

    dir_path = Path(claude_dir)
    if not dir_path.exists():
        return None

    # Agents
    agents_dir = dir_path / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            components['agents'].append({
                'name': f.stem,
                'path': str(f),
                'type': 'agent'
            })

    # Commands (including nested)
    commands_dir = dir_path / "commands"
    if commands_dir.exists():
        for f in commands_dir.rglob("*.md"):
            # Get relative path within commands
            rel_path = f.relative_to(commands_dir)
            name = f.stem if len(rel_path.parts) == 1 else '/'.join(rel_path.parts[:-1]) + '/' + f.stem
            components['commands'].append({
                'name': name,
                'path': str(f),
                'type': 'command'
            })

    # Hooks
    hooks_dir = dir_path / "hooks"
    if hooks_dir.exists():
        for f in hooks_dir.glob("*.py"):
            if f.name != "__init__.py" and not f.name.startswith("utils"):
                components['hooks'].append({
                    'name': f.stem,
                    'path': str(f),
                    'type': 'hook'
                })

    # Skills
    skills_dir = dir_path / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir():
                skill_md = d / "SKILL.md"
                components['skills'].append({
                    'name': d.name,
                    'path': str(d),
                    'has_skill_md': skill_md.exists(),
                    'type': 'skill'
                })

    return components

def get_source_project(claude_dir):
    """Extract project name from path."""
    parts = Path(claude_dir).parts
    # Find the folder before .claude
    for i, part in enumerate(parts):
        if part == '.claude' and i > 0:
            return parts[i-1]
    return "unknown"

def create_obsidian_note(component, source_dir, existing):
    """Create an Obsidian note for a component if it doesn't exist."""
    comp_type = component['type']
    name = component['name']
    normalized = normalize_name(name)

    # Check if exists
    if normalized in existing.get(comp_type + 's', set()):
        return {'status': 'exists', 'name': name, 'type': comp_type}

    # Get target path
    target_dirs = {
        'agent': OBSIDIAN_KB / "02-Agents",
        'command': OBSIDIAN_KB / "08-Commands",
        'hook': OBSIDIAN_KB / "08-Hooks",
        'skill': OBSIDIAN_KB / "03-Skills"
    }

    target_dir = target_dirs.get(comp_type)
    if not target_dir:
        return {'status': 'error', 'name': name, 'type': comp_type, 'error': 'Unknown type'}

    # Clean name for file
    clean_name = name.replace('/', '-').replace('\\', '-')

    if comp_type == 'skill':
        target_path = target_dir / clean_name / f"{clean_name}.md"
        target_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        target_path = target_dir / f"{clean_name}.md"

    # Read source content
    source_path = Path(component['path'])
    source_content = ""
    if source_path.exists():
        try:
            if source_path.is_file():
                source_content = source_path.read_text(encoding='utf-8', errors='ignore')
        except:
            pass

    # Get project name
    project = get_source_project(source_dir)

    # Create frontmatter
    today = datetime.now().strftime("%Y-%m-%d")
    frontmatter = f"""---
type: {comp_type}
name: "{clean_name}"
source_repo: "{project}"
source_path: "{component['path']}"
status: active
created: {today}
updated: {today}
human_reviewed: false
tac_original: false
tags: [{comp_type}, non-tac, {project}]
cssclasses: [ai-agent-kb]
---

"""

    # Build note content
    content = frontmatter
    content += f"# {clean_name}\n\n"
    content += f"> Source: `{component['path']}`\n\n"

    if source_content:
        # If it's a markdown file, include the content
        if source_path.suffix == '.md':
            # Strip any existing frontmatter from source
            if source_content.startswith('---'):
                parts = source_content.split('---', 2)
                if len(parts) >= 3:
                    source_content = parts[2].strip()
            content += "## Original Content\n\n"
            content += source_content
        elif source_path.suffix == '.py':
            content += "## Script Overview\n\n"
            # Extract docstring if present
            docstring_match = re.search(r'"""(.*?)"""', source_content, re.DOTALL)
            if docstring_match:
                content += docstring_match.group(1).strip() + "\n\n"
            content += "```python\n"
            content += source_content[:2000]  # Limit size
            if len(source_content) > 2000:
                content += "\n# ... (truncated)"
            content += "\n```\n"

    content += f"\n## Changelog\n- {today}: Auto-synced from non-TAC directory\n"

    # Write file
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding='utf-8')
        return {'status': 'created', 'name': name, 'type': comp_type, 'path': str(target_path)}
    except Exception as e:
        return {'status': 'error', 'name': name, 'type': comp_type, 'error': str(e)}

def classify_workflow(components):
    """Classify whether this is Command, Agentic Prompt, or ADW."""
    total_steps = len(components.get('agents', [])) + len(components.get('commands', []))
    has_hooks = len(components.get('hooks', [])) > 0
    has_skills = len(components.get('skills', [])) > 0

    # Check for orchestrator/Python infrastructure
    has_infra = has_hooks and has_skills

    if has_infra:
        return "ADW"
    elif total_steps >= 3:
        return "Agentic Prompt"
    else:
        return "Command"

def process_directory(claude_dir, existing, progress):
    """Process a single .claude directory."""
    result = {
        'directory': claude_dir,
        'exists': False,
        'components': None,
        'notes_created': [],
        'notes_skipped': [],
        'workflow_type': None,
        'errors': []
    }

    # Check if directory exists
    if not Path(claude_dir).exists():
        result['errors'].append("Directory not found")
        return result

    result['exists'] = True

    # Scan for components
    components = scan_directory(claude_dir)
    if not components:
        result['errors'].append("Failed to scan")
        return result

    result['components'] = {
        'agents_count': len(components.get('agents', [])),
        'commands_count': len(components.get('commands', [])),
        'hooks_count': len(components.get('hooks', [])),
        'skills_count': len(components.get('skills', []))
    }

    # Check if there are any components
    total = sum(result['components'].values())
    if total == 0:
        result['workflow_type'] = "Empty"
        return result

    # Classify workflow
    result['workflow_type'] = classify_workflow(components)

    # Create Obsidian notes for each component
    for comp_type in ['agents', 'commands', 'hooks', 'skills']:
        for comp in components.get(comp_type, []):
            note_result = create_obsidian_note(comp, claude_dir, existing)
            if note_result['status'] == 'created':
                result['notes_created'].append(note_result)
                # Update existing set
                normalized = normalize_name(comp['name'])
                existing[comp_type].add(normalized)
            elif note_result['status'] == 'exists':
                result['notes_skipped'].append(note_result)
            else:
                result['errors'].append(note_result)

    return result

def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def main():
    print("=" * 60)
    print("Non-TAC .claude Directory Sync to Obsidian")
    print("=" * 60)

    # Load directories
    directories = load_directories()
    print(f"\nLoaded {len(directories)} directories to process")

    # Get existing Obsidian notes
    print("\nScanning existing Obsidian notes...")
    existing = get_existing_obsidian_notes()
    print(f"  Existing agents: {len(existing['agents'])}")
    print(f"  Existing commands: {len(existing['commands'])}")
    print(f"  Existing hooks: {len(existing['hooks'])}")
    print(f"  Existing skills: {len(existing['skills'])}")

    # Initialize progress
    progress = {
        'started': datetime.now().isoformat(),
        'current_index': 0,
        'current_directory': '',
        'completed': [],
        'skipped': [],
        'failed': [],
        'components_found': 0,
        'notes_created': 0,
        'total': len(directories)
    }

    # Process each directory
    all_results = []
    for i, claude_dir in enumerate(directories):
        progress['current_index'] = i
        progress['current_directory'] = claude_dir

        # Log progress every 10 directories
        if i % 10 == 0:
            print(f"\n[{i}/{len(directories)}] Processing batch...")

        # Process directory
        result = process_directory(claude_dir, existing, progress)
        all_results.append(result)

        # Update progress
        if result['exists']:
            if result['components']:
                progress['components_found'] += sum(result['components'].values())
            progress['notes_created'] += len(result.get('notes_created', []))
            if len(result.get('errors', [])) == 0:
                progress['completed'].append(claude_dir)
            else:
                progress['failed'].append(claude_dir)
        else:
            progress['skipped'].append(claude_dir)

        # Print status for directories with components
        if result.get('notes_created'):
            print(f"  [{i}] {Path(claude_dir).parent.name}: Created {len(result['notes_created'])} notes")

        # Save progress periodically
        if i % 20 == 0:
            save_progress(progress)

    # Final save
    progress['completed_at'] = datetime.now().isoformat()
    save_progress(progress)

    # Summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total directories: {len(directories)}")
    print(f"Completed: {len(progress['completed'])}")
    print(f"Skipped (not found): {len(progress['skipped'])}")
    print(f"Failed: {len(progress['failed'])}")
    print(f"Components found: {progress['components_found']}")
    print(f"Notes created: {progress['notes_created']}")

    # Save detailed results
    results_file = PROGRESS_FILE.parent / "non-tac-sync-results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'summary': progress,
            'details': all_results
        }, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")

    return progress

if __name__ == "__main__":
    main()
