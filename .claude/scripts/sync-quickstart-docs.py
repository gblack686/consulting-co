#!/usr/bin/env python3
"""
Sync QuickStart Documentation and Code

This script syncs documentation and supporting code from all QuickStart repos to the current directory.
Syncs:
- Documentation files (.md, .txt)
- Python scripts (.py) from commands, agents, skills, scripts, and hooks
- Python dependencies (requirements.txt, pyproject.toml, uv.lock)
- Shell scripts (.sh, .bat) from relevant directories

Excludes cloud folders and build artifacts.
"""

import os
import shutil
from pathlib import Path

# Configuration
SOURCE_DIR = Path("claude-repos")
TARGET_BASE = Path(".")

QUICKSTARTS = [
    "quickstart-acme-test-claude",
    "quickstart-agentcore-claude",
    "quickstart-board-director-claude",
    "quickstart-compcorrect-claude",
    "quickstart-nexus-claude",
    "quickstart-parenting-autism-claude",
    "quickstart-perl-street-claude",
    "quickstart-word-collections-claude",
]

EXCLUDE_DIRS = {"cloud", ".git", "node_modules", "__pycache__", ".next", "dist", "build", "venv", ".venv"}
INCLUDE_EXTENSIONS = {".md", ".txt", ".py", ".sh", ".bat"}
INCLUDE_FILENAMES = {"requirements.txt", "pyproject.toml", "uv.lock", "Dockerfile"}

# Only sync Python files from these specific directories
PYTHON_SYNC_DIRS = {"commands", "agents", "skills", "scripts", "hooks"}

def should_skip_path(path: Path) -> bool:
    """Check if path should be skipped based on exclusion rules."""
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)

def should_sync_python_file(file_path: Path, source_root: Path) -> bool:
    """Check if a Python file should be synced based on its location."""
    try:
        rel_path = file_path.relative_to(source_root)
        # Check if file is in one of the allowed Python sync directories
        for allowed_dir in PYTHON_SYNC_DIRS:
            if allowed_dir in rel_path.parts:
                return True
        return False
    except ValueError:
        return False

def should_sync_file(file_path: Path, source_root: Path) -> bool:
    """Determine if a file should be synced."""
    filename = file_path.name
    suffix = file_path.suffix

    # Always sync specific important files
    if filename in INCLUDE_FILENAMES:
        return True

    # Always sync markdown and txt files
    if suffix in {".md", ".txt"}:
        return True

    # Sync Python files only from specific directories
    if suffix == ".py":
        return should_sync_python_file(file_path, source_root)

    # Sync shell scripts from specific directories
    if suffix in {".sh", ".bat"}:
        return should_sync_python_file(file_path, source_root)

    return False

def sync_quickstart_docs(qs_name: str) -> dict:
    """Sync documentation and code from a single QuickStart."""
    source_path = SOURCE_DIR / qs_name
    target_path = TARGET_BASE / qs_name

    if not source_path.exists():
        print(f"⚠️  Skipping {qs_name} - directory not found")
        return {"total": 0, "by_type": {}}

    print(f"\n📦 Syncing: {qs_name}")
    print(f"   Source: {source_path}")
    print(f"   Target: {target_path}")

    file_counts = {"total": 0, "by_type": {".md": 0, ".txt": 0, ".py": 0, ".sh": 0, ".bat": 0, "other": 0}}

    # Walk through source directory
    for root, dirs, files in os.walk(source_path):
        root_path = Path(root)

        # Skip excluded directories
        if should_skip_path(root_path.relative_to(source_path)):
            continue

        # Filter out excluded directories from traversal
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        # Process files
        for file in files:
            file_path = root_path / file

            # Check if file should be synced
            if not should_sync_file(file_path, source_path):
                continue

            # Calculate relative path and target
            rel_path = file_path.relative_to(source_path)
            target_file = target_path / rel_path

            # Create parent directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            try:
                shutil.copy2(file_path, target_file)
                file_counts["total"] += 1

                # Track by extension
                suffix = file_path.suffix
                if suffix in file_counts["by_type"]:
                    file_counts["by_type"][suffix] += 1
                elif file_path.name in INCLUDE_FILENAMES:
                    file_counts["by_type"]["other"] += 1

            except Exception as e:
                print(f"   ⚠️  Error copying {rel_path}: {e}")

    # Print summary
    print(f"   ✅ Copied {file_counts['total']} files:")
    if file_counts["by_type"][".md"] > 0:
        print(f"      - {file_counts['by_type']['.md']} markdown files")
    if file_counts["by_type"][".txt"] > 0:
        print(f"      - {file_counts['by_type']['.txt']} text files")
    if file_counts["by_type"][".py"] > 0:
        print(f"      - {file_counts['by_type']['.py']} Python scripts")
    if file_counts["by_type"][".sh"] > 0:
        print(f"      - {file_counts['by_type']['.sh']} shell scripts")
    if file_counts["by_type"][".bat"] > 0:
        print(f"      - {file_counts['by_type']['.bat']} batch scripts")
    if file_counts["by_type"]["other"] > 0:
        print(f"      - {file_counts['by_type']['other']} dependency files")

    return file_counts

def main():
    """Main sync function."""
    print("Starting QuickStart documentation and code sync...")
    print("=" * 60)

    total_counts = {"total": 0, "by_type": {".md": 0, ".txt": 0, ".py": 0, ".sh": 0, ".bat": 0, "other": 0}}
    synced_projects = []

    for qs in QUICKSTARTS:
        file_counts = sync_quickstart_docs(qs)

        total_counts["total"] += file_counts["total"]
        for ext, count in file_counts.get("by_type", {}).items():
            total_counts["by_type"][ext] += count

        if file_counts["total"] > 0:
            synced_projects.append(qs)

    print("\n" + "=" * 60)
    print(f"✅ QuickStart sync complete!")
    print(f"\n   Total files synced: {total_counts['total']}")
    print(f"   - {total_counts['by_type']['.md']} markdown files")
    print(f"   - {total_counts['by_type']['.txt']} text files")
    print(f"   - {total_counts['by_type']['.py']} Python scripts")
    print(f"   - {total_counts['by_type']['.sh']} shell scripts")
    print(f"   - {total_counts['by_type']['.bat']} batch scripts")
    print(f"   - {total_counts['by_type']['other']} dependency files")

    print(f"\n   Content synced to:")
    for qs in synced_projects:
        target_path = TARGET_BASE / qs
        if target_path.exists():
            print(f"   - {qs}/")

if __name__ == "__main__":
    main()
