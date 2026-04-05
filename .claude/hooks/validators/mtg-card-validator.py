#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "requests"]
# ///
"""
MTG Card Validator for Claude Ecosystem Sync

Validates that MTG cards were assigned correctly:
- All components have mtg_card field in frontmatter
- Card names are valid (exist in Scryfall)
- Art URLs are accessible (optional check)

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Log file in same directory as this script
LOG_FILE = Path(__file__).parent / "mtg-card-validator.log"

# Scryfall API
SCRYFALL_NAMED_URL = "https://api.scryfall.com/cards/named"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None
    
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return None
    
    yaml_content = content[3:end_match.start() + 3]
    
    try:
        import yaml
        return yaml.safe_load(yaml_content)
    except Exception as e:
        log(f"  ✗ Failed to parse frontmatter: {e}")
        return None


def validate_card_name(card_name: str) -> bool:
    """Check if card name exists in Scryfall."""
    try:
        import requests
        response = requests.get(
            SCRYFALL_NAMED_URL,
            params={"exact": card_name},
            timeout=5
        )
        if response.status_code == 200:
            log(f"  ✓ Card exists: {card_name}")
            return True
        elif response.status_code == 404:
            log(f"  ✗ Card not found: {card_name}")
            return False
        else:
            log(f"  ⚠ Scryfall API error: {response.status_code}")
            return True  # Don't block on API errors
    except Exception as e:
        log(f"  ⚠ Scryfall API exception: {e}")
        return True  # Don't block on network errors


def validate_mtg_assignment(file_path: Path, validate_scryfall: bool = False) -> list[str]:
    """Validate MTG card assignment in a note. Returns list of error messages."""
    errors = []
    
    if not file_path.exists():
        return [f"File not found: {file_path}"]
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        return [f"Encoding error in {file_path}: {e}"]
    
    frontmatter = extract_frontmatter(content)
    if frontmatter is None:
        log(f"  ✗ No frontmatter in {file_path.name}")
        return [f"{file_path.name}: No frontmatter found"]
    
    # Check for mtg_card field
    mtg_card = frontmatter.get("mtg_card")
    if not mtg_card or mtg_card in ["{{mtg_card}}", "", None]:
        log(f"  ✗ Missing mtg_card in {file_path.name}")
        errors.append(f"{file_path.name}: Missing mtg_card assignment")
    else:
        log(f"  ✓ Has mtg_card: {mtg_card}")
        
        # Optionally validate card exists in Scryfall
        if validate_scryfall and not validate_card_name(mtg_card):
            errors.append(f"{file_path.name}: Invalid card name '{mtg_card}'")
    
    # Check for mtg_color field
    mtg_color = frontmatter.get("mtg_color")
    if not mtg_color or mtg_color in ["{{mtg_color}}", "", None]:
        log(f"  ⚠ Missing mtg_color in {file_path.name} (warning)")
        # Not blocking, just a warning
    else:
        valid_colors = ["White", "Blue", "Black", "Red", "Green", "Colorless", "Multicolor"]
        if mtg_color not in valid_colors:
            log(f"  ⚠ Unknown mtg_color: {mtg_color}")
    
    return errors


def validate_assignments_file(assignments_file: Path) -> list[str]:
    """Validate MTG assignments JSON file."""
    errors = []
    
    if not assignments_file.exists():
        return [f"Assignments file not found: {assignments_file}"]
    
    try:
        assignments = json.loads(assignments_file.read_text())
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in assignments file: {e}"]
    
    assignment_list = assignments.get("assignments", [])
    
    if not assignment_list:
        errors.append("No MTG card assignments found in results")
        return errors
    
    for item in assignment_list:
        component_name = item.get("component_name", "unknown")
        mtg_card = item.get("mtg_card")
        
        if not mtg_card:
            errors.append(f"{component_name}: No MTG card assigned")
        else:
            log(f"  ✓ {component_name}: {mtg_card}")
    
    return errors


def main():
    log("=" * 50)
    log("MTG CARD VALIDATOR STOP HOOK TRIGGERED")
    
    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
        else:
            hook_input = {}
    except json.JSONDecodeError:
        hook_input = {}
    
    errors = []
    validate_scryfall = "--validate-scryfall" in sys.argv
    
    # Get target from command line
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.name.startswith("--"):
            target = None
    else:
        target = None
    
    if target is None:
        # Look for mtg-assignments.json
        possible_paths = [
            Path("mtg-assignments.json"),
            Path(".claude/mtg-assignments.json"),
        ]
        for p in possible_paths:
            if p.exists():
                target = p
                break
        
        if target is None:
            log("No mtg-assignments.json found - skipping validation")
            print(json.dumps({}))
            return
    
    log(f"Validating: {target}")
    log(f"Scryfall validation: {validate_scryfall}")
    
    if target.suffix == ".json":
        # Validate assignments JSON file
        errors = validate_assignments_file(target)
    elif target.suffix == ".md":
        # Validate single markdown file
        errors = validate_mtg_assignment(target, validate_scryfall)
    elif target.is_dir():
        # Validate all .md files in directory
        for md_file in target.glob("**/*.md"):
            if not md_file.name.startswith("_"):
                log(f"Checking: {md_file.name}")
                file_errors = validate_mtg_assignment(md_file, validate_scryfall)
                errors.extend(file_errors)
    
    # Output decision JSON
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors:
            log(f"  ✗ {err}")
        print(json.dumps({
            "decision": "block",
            "reason": "MTG card validation failed:\n" + "\n".join(errors)
        }))
    else:
        log("RESULT: PASS - MTG card validation successful")
        print(json.dumps({}))


if __name__ == "__main__":
    main()

