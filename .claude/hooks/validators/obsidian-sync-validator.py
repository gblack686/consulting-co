#!/usr/bin/env python3
"""Obsidian sync validator - validates ecosystem sync operations and tracks history."""

import sys
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Output directory and history file location
OUTPUT_DIR = Path(__file__).parent.parent.parent / "sync-claude-ecosystem"
HISTORY_FILE = OUTPUT_DIR / "ecosystem-sync-history.json"

# Quality classification
QUALITY_OFFICIAL = "official"      # Well-formatted, has frontmatter, follows template
QUALITY_NEEDS_REVIEW = "needs_review"  # Missing elements but might be worth keeping
QUALITY_DELETABLE = "deletable"    # AI slop, no structure, low quality

# Obsidian vault paths
OBSIDIAN_VAULT = Path("C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation")
AI_AGENT_KB = OBSIDIAN_VAULT / "AI-Agent-KB"


def count_frontmatter_blocks(content: str) -> int:
    """Count how many frontmatter blocks are at the start of content."""
    count = 0
    pos = 0

    while pos < len(content):
        # Skip whitespace
        while pos < len(content) and content[pos] in '\n\r\t ':
            pos += 1

        if not content[pos:].startswith('---'):
            break

        # Find end of this block
        end_match = re.search(r'\n---\s*\n?', content[pos + 3:])
        if end_match:
            count += 1
            pos = pos + 3 + end_match.end()
        else:
            break

    return count


def validate_obsidian_note(filepath: Path) -> dict:
    """
    Validate an Obsidian note has proper content and MTG card fields.
    Returns validation details.
    """
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"valid": False, "reason": "unreadable"}

    details = {
        "valid": True,
        "has_frontmatter": False,
        "has_mtg_card": False,
        "has_banner": False,
        "has_content": False,
        "has_human_reviewed": False,
        "has_tac_original": False,
        "human_reviewed": None,
        "tac_original": None,
        "is_stub": False,
        "has_duplicate_frontmatter": False,
        "frontmatter_blocks": 1,
        "mtg_card": None,
        "mtg_color": None,
        "issues": [],
    }

    # Check for duplicate frontmatter blocks
    frontmatter_count = count_frontmatter_blocks(content)
    details["frontmatter_blocks"] = frontmatter_count
    if frontmatter_count > 1:
        details["has_duplicate_frontmatter"] = True
        details["issues"].append(f"Duplicate frontmatter ({frontmatter_count} blocks)")

    # Check for YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        details["has_frontmatter"] = True
        frontmatter = frontmatter_match.group(1)

        # Check for MTG card fields
        if "mtg_card:" in frontmatter:
            details["has_mtg_card"] = True
            mtg_match = re.search(r'mtg_card:\s*["\']?([^"\'\n]+)', frontmatter)
            if mtg_match:
                details["mtg_card"] = mtg_match.group(1).strip()

        if "mtg_color:" in frontmatter:
            color_match = re.search(r'mtg_color:\s*["\']?([^"\'\n]+)', frontmatter)
            if color_match:
                details["mtg_color"] = color_match.group(1).strip()

        if "banner:" in frontmatter:
            details["has_banner"] = True

        # Check for human_reviewed field
        if "human_reviewed:" in frontmatter:
            details["has_human_reviewed"] = True
            hr_match = re.search(r'human_reviewed:\s*(true|false)', frontmatter.lower())
            if hr_match:
                details["human_reviewed"] = hr_match.group(1) == "true"

        # Check for tac_original field
        if "tac_original:" in frontmatter:
            details["has_tac_original"] = True
            tac_match = re.search(r'tac_original:\s*(true|false)', frontmatter.lower())
            if tac_match:
                details["tac_original"] = tac_match.group(1) == "true"

    # Check if this is a stub (has Quality Indicators section = bad)
    if "## Quality Indicators" in content or "## Source\n- Repository:" in content:
        details["is_stub"] = True
        details["issues"].append("Contains stub content instead of actual source")

    # Check for actual content (more than just frontmatter)
    content_after_frontmatter = re.sub(r'^---\s*\n.*?\n---\s*\n?', '', content, flags=re.DOTALL)
    if len(content_after_frontmatter.strip()) > 100:
        details["has_content"] = True
    else:
        details["issues"].append("Missing or minimal content")

    # Determine if valid
    if details["is_stub"]:
        details["valid"] = False
    if not details["has_mtg_card"]:
        details["issues"].append("Missing MTG card")
    if not details["has_banner"]:
        details["issues"].append("Missing banner image")
    if not details["has_human_reviewed"]:
        details["issues"].append("Missing human_reviewed field")
    if not details["has_tac_original"]:
        details["issues"].append("Missing tac_original field")

    return details


def scan_obsidian_notes() -> dict:
    """Scan Obsidian AI-Agent-KB for note validation."""
    results = {
        "agents": {"total": 0, "with_mtg": 0, "stubs": 0, "tac_originals": 0, "human_reviewed": 0, "missing_tac_field": 0, "duplicate_frontmatter": 0, "notes": []},
        "commands": {"total": 0, "with_mtg": 0, "stubs": 0, "tac_originals": 0, "human_reviewed": 0, "missing_tac_field": 0, "duplicate_frontmatter": 0, "notes": []},
        "hooks": {"total": 0, "with_mtg": 0, "stubs": 0, "tac_originals": 0, "human_reviewed": 0, "missing_tac_field": 0, "duplicate_frontmatter": 0, "notes": []},
        "skills": {"total": 0, "with_mtg": 0, "stubs": 0, "tac_originals": 0, "human_reviewed": 0, "missing_tac_field": 0, "duplicate_frontmatter": 0, "notes": []},
    }

    folder_mapping = {
        "agents": [AI_AGENT_KB / "02-Agents"],
        "commands": [AI_AGENT_KB / "08-Commands", AI_AGENT_KB / "09-Commands"],
        "hooks": [AI_AGENT_KB / "08-Hooks", AI_AGENT_KB / "09-Hooks"],
        "skills": [AI_AGENT_KB / "03-Skills"],
    }

    for comp_type, folders in folder_mapping.items():
        for folder in folders:
            if not folder.exists():
                continue

            for f in folder.rglob("*.md"):
                # Skip templates, index files, .base files, and to-delete files
                if f.name.startswith("_") or "template" in f.name.lower():
                    continue
                if f.suffix == ".base":
                    continue
                if "-to-delete" in f.name:
                    continue

                validation = validate_obsidian_note(f)
                results[comp_type]["total"] += 1

                if validation["has_mtg_card"]:
                    results[comp_type]["with_mtg"] += 1

                if validation["is_stub"]:
                    results[comp_type]["stubs"] += 1

                if validation.get("tac_original") is True:
                    results[comp_type]["tac_originals"] += 1

                if validation.get("human_reviewed") is True:
                    results[comp_type]["human_reviewed"] += 1

                if not validation.get("has_tac_original"):
                    results[comp_type]["missing_tac_field"] += 1

                if validation.get("has_duplicate_frontmatter"):
                    results[comp_type]["duplicate_frontmatter"] += 1

                results[comp_type]["notes"].append({
                    "name": f.stem,
                    "path": str(f.relative_to(AI_AGENT_KB)),
                    **validation
                })

    return results


def classify_markdown_file(filepath: Path) -> tuple[str, dict]:
    """
    Classify a markdown file's quality.
    Returns (classification, details_dict)
    """
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return QUALITY_DELETABLE, {"reason": "unreadable"}

    details = {
        "has_frontmatter": False,
        "has_purpose": False,
        "has_instructions": False,
        "has_examples": False,
        "line_count": len(content.splitlines()),
        "word_count": len(content.split()),
        "issues": [],
    }

    # Check for YAML frontmatter (between --- markers)
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        details["has_frontmatter"] = True
        frontmatter = frontmatter_match.group(1)
        # Check for key frontmatter fields
        details["has_description"] = "description:" in frontmatter.lower()
        details["has_model"] = "model:" in frontmatter.lower()

    # Check for standard sections
    content_lower = content.lower()
    details["has_purpose"] = "## purpose" in content_lower or "# purpose" in content_lower
    details["has_instructions"] = "## instructions" in content_lower or "## workflow" in content_lower
    details["has_examples"] = "## example" in content_lower or "```" in content

    # Check for AI slop indicators
    slop_phrases = [
        "i'll help you",
        "i can help",
        "here's how",
        "let me explain",
        "certainly!",
        "absolutely!",
        "great question",
        "happy to help",
    ]
    slop_count = sum(1 for phrase in slop_phrases if phrase in content_lower)
    if slop_count >= 2:
        details["issues"].append(f"AI slop detected ({slop_count} phrases)")

    # Classify based on criteria
    score = 0
    if details["has_frontmatter"]:
        score += 3
    if details["has_purpose"]:
        score += 2
    if details["has_instructions"]:
        score += 2
    if details["has_examples"]:
        score += 1
    if details["line_count"] > 20:
        score += 1
    if slop_count >= 2:
        score -= 3

    # Determine classification
    if score >= 6:
        return QUALITY_OFFICIAL, details
    elif score >= 3:
        return QUALITY_NEEDS_REVIEW, details
    else:
        return QUALITY_DELETABLE, details


def classify_python_file(filepath: Path) -> tuple[str, dict]:
    """
    Classify a Python hook file's quality.
    Returns (classification, details_dict)
    """
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return QUALITY_DELETABLE, {"reason": "unreadable"}

    details = {
        "has_docstring": False,
        "has_main": False,
        "has_functions": False,
        "line_count": len(content.splitlines()),
        "issues": [],
    }

    # Check for module docstring
    details["has_docstring"] = content.strip().startswith('"""') or content.strip().startswith("'''")

    # Check for main block
    details["has_main"] = 'if __name__' in content

    # Check for function definitions
    details["has_functions"] = "def " in content

    # Check for proper imports
    details["has_imports"] = "import " in content

    # Classify
    score = 0
    if details["has_docstring"]:
        score += 2
    if details["has_main"]:
        score += 2
    if details["has_functions"]:
        score += 2
    if details["has_imports"]:
        score += 1
    if details["line_count"] > 20:
        score += 1

    if score >= 5:
        return QUALITY_OFFICIAL, details
    elif score >= 3:
        return QUALITY_NEEDS_REVIEW, details
    else:
        return QUALITY_DELETABLE, details


def classify_skill_directory(dirpath: Path) -> tuple[str, dict]:
    """
    Classify a skill directory's quality.
    Returns (classification, details_dict)
    """
    details = {
        "has_readme": False,
        "has_main_file": False,
        "file_count": 0,
        "issues": [],
    }

    if not dirpath.is_dir():
        return QUALITY_DELETABLE, {"reason": "not a directory"}

    files = list(dirpath.iterdir())
    details["file_count"] = len(files)

    # Check for README
    details["has_readme"] = any(f.name.lower() in ["readme.md", "readme.txt"] for f in files)

    # Check for main skill file
    details["has_main_file"] = any(
        f.suffix in [".md", ".py", ".skill"] for f in files if f.is_file()
    )

    # Check for proper structure
    details["has_templates"] = (dirpath / "templates").is_dir()

    score = 0
    if details["has_readme"]:
        score += 2
    if details["has_main_file"]:
        score += 2
    if details["file_count"] > 1:
        score += 1
    if details["has_templates"]:
        score += 2

    if score >= 4:
        return QUALITY_OFFICIAL, details
    elif score >= 2:
        return QUALITY_NEEDS_REVIEW, details
    else:
        return QUALITY_DELETABLE, details


def scan_and_classify(source_folder: str) -> dict:
    """Scan folder and classify all components."""
    source = Path(source_folder)
    result = {
        "agents": {"official": [], "needs_review": [], "deletable": []},
        "commands": {"official": [], "needs_review": [], "deletable": []},
        "hooks": {"official": [], "needs_review": [], "deletable": []},
        "skills": {"official": [], "needs_review": [], "deletable": []},
        "adws": {"official": [], "needs_review": [], "deletable": []},
    }

    # Scan agents
    agents_dir = source / "agents"
    if agents_dir.exists():
        for f in agents_dir.rglob("*.md"):
            if f.name == "README.md":
                continue
            quality, details = classify_markdown_file(f)
            result["agents"][quality].append({
                "path": str(f.relative_to(source)),
                "name": f.stem,
                **details
            })

    # Scan commands
    commands_dir = source / "commands"
    if commands_dir.exists():
        for f in commands_dir.rglob("*.md"):
            quality, details = classify_markdown_file(f)
            result["commands"][quality].append({
                "path": str(f.relative_to(source)),
                "name": f.stem,
                **details
            })

    # Scan hooks
    hooks_dir = source / "hooks"
    if hooks_dir.exists():
        for f in hooks_dir.glob("*.py"):
            quality, details = classify_python_file(f)
            result["hooks"][quality].append({
                "path": str(f.relative_to(source)),
                "name": f.stem,
                **details
            })

    # Scan skills
    skills_dir = source / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir():
                quality, details = classify_skill_directory(d)
                result["skills"][quality].append({
                    "path": str(d.relative_to(source)),
                    "name": d.name,
                    **details
                })

    # Scan ADWs
    adws_dir = source / "adws"
    if adws_dir.exists():
        for f in adws_dir.glob("*.md"):
            if f.name == "README.md":
                continue
            quality, details = classify_markdown_file(f)
            result["adws"][quality].append({
                "path": str(f.relative_to(source)),
                "name": f.stem,
                **details
            })

    return result


def count_components(source_folder: str) -> dict:
    """Count components in a .claude folder."""
    source = Path(source_folder)
    counts = {
        "agents": 0,
        "commands": 0,
        "hooks": 0,
        "skills": 0,
        "adws": 0,
    }

    # Count agents (*.md files, excluding README)
    agents_dir = source / "agents"
    if agents_dir.exists():
        counts["agents"] = len([f for f in agents_dir.rglob("*.md") if f.name != "README.md"])

    # Count commands (*.md files)
    commands_dir = source / "commands"
    if commands_dir.exists():
        counts["commands"] = len(list(commands_dir.rglob("*.md")))

    # Count hooks (*.py files in hooks root)
    hooks_dir = source / "hooks"
    if hooks_dir.exists():
        counts["hooks"] = len([f for f in hooks_dir.glob("*.py")])

    # Count skills (directories)
    skills_dir = source / "skills"
    if skills_dir.exists():
        counts["skills"] = len([d for d in skills_dir.iterdir() if d.is_dir()])

    # Count ADWs
    adws_dir = source / "adws"
    if adws_dir.exists():
        counts["adws"] = len([f for f in adws_dir.glob("*.md") if f.name != "README.md"])

    return counts


def load_history() -> dict:
    """Load sync history from file."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"directories": {}, "sync_runs": []}


def save_history(history: dict):
    """Save sync history to file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def update_history(source_folder: str, dry_run: bool, components: dict, session_id: str, quality_summary: dict = None):
    """Update sync history with this run."""
    history = load_history()
    now = datetime.now().isoformat()

    # Normalize path for consistent keys
    source_key = str(Path(source_folder).resolve())

    # Update directory entry
    if source_key not in history["directories"]:
        history["directories"][source_key] = {
            "first_synced": now,
            "sync_count": 0,
            "components": {},
        }

    dir_entry = history["directories"][source_key]
    dir_entry["last_synced"] = now
    dir_entry["sync_count"] += 1
    dir_entry["components"] = components
    dir_entry["last_dry_run"] = dry_run
    if quality_summary:
        dir_entry["quality_summary"] = quality_summary

    # Add to sync runs log (keep last 50)
    run_entry = {
        "timestamp": now,
        "directory": source_key,
        "dry_run": dry_run,
        "components": components,
        "session_id": session_id,
    }
    if quality_summary:
        run_entry["quality_summary"] = quality_summary

    history["sync_runs"].append(run_entry)
    history["sync_runs"] = history["sync_runs"][-50:]  # Keep last 50 runs

    save_history(history)
    return history


def main():
    """Validate obsidian sync results and track history."""
    # Read input from stdin (Claude hook format)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    session_id = input_data.get("session_id", "unknown")

    # Try to extract source folder and dry-run from transcript context
    # Default to .claude/ if not specified
    source_folder = ".claude"
    dry_run = True  # Assume dry-run unless we can determine otherwise

    # Check for common patterns in transcript
    transcript = input_data.get("transcript", "")
    if isinstance(transcript, str):
        if "--dry-run" in transcript:
            dry_run = True
        elif "/sync-claude-ecosystem" in transcript and "--dry-run" not in transcript:
            dry_run = False

    # Count components
    components = count_components(source_folder)
    total = sum(components.values())

    # Classify all components
    classification = scan_and_classify(source_folder)

    # Count by quality
    quality_summary = {}
    for comp_type, by_quality in classification.items():
        quality_summary[comp_type] = {
            "official": len(by_quality["official"]),
            "needs_review": len(by_quality["needs_review"]),
            "deletable": len(by_quality["deletable"]),
        }

    # Update history with classification
    history = update_history(source_folder, dry_run, components, session_id, quality_summary)
    dir_entry = history["directories"].get(str(Path(source_folder).resolve()), {})

    # Save detailed classification to separate file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    classification_file = OUTPUT_DIR / "ecosystem-classification.json"
    with open(classification_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source_folder": source_folder,
            "quality_summary": quality_summary,
            "components": classification,
        }, f, indent=2)

    # Validate Obsidian notes for MTG cards and proper content
    obsidian_validation = scan_obsidian_notes()

    # Calculate MTG coverage and TAC stats
    mtg_coverage = {}
    stubs_found = {}
    tac_stats = {}
    review_stats = {}
    frontmatter_issues = {}
    for comp_type, data in obsidian_validation.items():
        if data["total"] > 0:
            mtg_coverage[comp_type] = {
                "total": data["total"],
                "with_mtg": data["with_mtg"],
                "coverage_pct": round(data["with_mtg"] / data["total"] * 100, 1),
            }
            stubs_found[comp_type] = data["stubs"]
            tac_stats[comp_type] = {
                "tac_originals": data["tac_originals"],
                "missing_tac_field": data["missing_tac_field"],
                "tac_pct": round(data["tac_originals"] / data["total"] * 100, 1) if data["total"] > 0 else 0,
            }
            review_stats[comp_type] = {
                "human_reviewed": data["human_reviewed"],
                "review_pct": round(data["human_reviewed"] / data["total"] * 100, 1) if data["total"] > 0 else 0,
            }
            frontmatter_issues[comp_type] = {
                "duplicate_frontmatter": data["duplicate_frontmatter"],
            }

    # Save Obsidian validation to separate file
    obsidian_validation_file = OUTPUT_DIR / "obsidian-validation.json"
    with open(obsidian_validation_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "mtg_coverage": mtg_coverage,
            "stubs_found": stubs_found,
            "tac_stats": tac_stats,
            "review_stats": review_stats,
            "frontmatter_issues": frontmatter_issues,
            "details": obsidian_validation,
        }, f, indent=2)

    # Output success with details
    result = {
        "status": "ok",
        "message": f"Ecosystem sync {'validated' if not dry_run else 'dry-run completed'}",
        "source_folder": source_folder,
        "dry_run": dry_run,
        "components_found": components,
        "total_components": total,
        "quality_summary": quality_summary,
        "mtg_coverage": mtg_coverage,
        "stubs_found": stubs_found,
        "tac_stats": tac_stats,
        "review_stats": review_stats,
        "frontmatter_issues": frontmatter_issues,
        "sync_count": dir_entry.get("sync_count", 1),
        "first_synced": dir_entry.get("first_synced"),
        "last_synced": dir_entry.get("last_synced"),
        "history_file": str(HISTORY_FILE),
        "classification_file": str(classification_file),
        "obsidian_validation_file": str(obsidian_validation_file),
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
