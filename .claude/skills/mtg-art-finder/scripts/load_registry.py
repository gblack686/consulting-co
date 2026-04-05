#!/usr/bin/env python3
"""
Load Registry - Parse _color-registry.md for MTG card assignment rules

This module provides functions to parse the color registry markdown file
and extract card type rules, color mappings, and edition assignments.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


def get_config() -> Dict[str, Any]:
    """Load settings from config/settings.json."""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding='utf-8'))
    return {}


def parse_markdown_table(content: str, header_pattern: str) -> list[dict]:
    """
    Parse a markdown table following a header pattern.

    Args:
        content: Full markdown content
        header_pattern: Regex pattern to match table header row

    Returns:
        List of dicts with column names as keys
    """
    rows = []

    # Find table header
    match = re.search(
        rf'\|[^\n]*{header_pattern}[^\n]*\|\s*\n(\|[^\n]+\|\s*\n)+',
        content,
        re.IGNORECASE
    )

    if not match:
        return rows

    table_text = match.group(0)
    lines = [l.strip() for l in table_text.split('\n') if l.strip()]

    if len(lines) < 3:  # Need header, separator, at least one data row
        return rows

    # Parse header
    headers = [h.strip().strip('*').lower().replace(' ', '_')
               for h in lines[0].split('|') if h.strip()]

    # Skip separator line (index 1)
    # Parse data rows
    for line in lines[2:]:
        if '---' in line:
            continue
        cells = [c.strip().strip('*') for c in line.split('|') if c.strip()]
        if len(cells) >= len(headers):
            row = dict(zip(headers, cells))
            rows.append(row)

    return rows


def load_registry(registry_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and parse _color-registry.md.

    Args:
        registry_path: Path to _color-registry.md, or uses config default

    Returns:
        Dict with parsed registry data:
        - card_type_rules: primitive -> card type
        - color_mappings: service domain -> color
        - edition_assignments: project -> set code
        - creature_types: role -> creature types
    """
    if registry_path is None:
        config = get_config()
        registry_path = config.get('registry_source', '')

    registry_path = Path(registry_path)
    if not registry_path.exists():
        print(f"Warning: Registry not found at {registry_path}")
        return _get_fallback_registry()

    content = registry_path.read_text(encoding='utf-8')

    registry = {
        "card_type_rules": {},
        "color_mappings": {},
        "edition_assignments": {},
        "creature_types": {},
        "raw_tables": {}
    }

    # Parse Card Type Rules
    card_types = parse_markdown_table(content, r'Primitive.*Card Type')
    for row in card_types:
        primitive = row.get('primitive', '').lower()
        card_type = row.get('card_type', '')
        if primitive and card_type:
            registry["card_type_rules"][primitive] = card_type

    registry["raw_tables"]["card_type_rules"] = card_types

    # Parse Service Domain to Color
    color_rows = parse_markdown_table(content, r'Service Domain.*MTG Color')
    for row in color_rows:
        domain = row.get('service_domain', '').lower()
        color = row.get('mtg_color', '')
        if domain and color:
            # Store full domain string
            registry["color_mappings"][domain] = color
            # Also store individual keywords
            for keyword in re.split(r'[,\s]+', domain):
                if keyword:
                    registry["color_mappings"][keyword] = color

    registry["raw_tables"]["color_mappings"] = color_rows

    # Parse Edition Assignments
    edition_rows = parse_markdown_table(content, r'Edition.*Set Code')
    for row in edition_rows:
        project = row.get('project', '').lower()
        set_code = row.get('set_code', '').strip('`')
        if project and set_code:
            registry["edition_assignments"][project] = set_code

    registry["raw_tables"]["edition_assignments"] = edition_rows

    # Parse Agent Creature Types
    creature_rows = parse_markdown_table(content, r'Agent Role.*Creature Type')
    for row in creature_rows:
        role = row.get('agent_role', '').lower()
        types = row.get('creature_types', '')
        if role and types:
            registry["creature_types"][role] = types

    registry["raw_tables"]["creature_types"] = creature_rows

    return registry


def _get_fallback_registry() -> Dict[str, Any]:
    """Return fallback registry if file not found."""
    return {
        "card_type_rules": {
            "agent": "Creature",
            "expert agent": "Creature",
            "skill (one-shot)": "Instant",
            "skill (manager)": "Enchantment",
            "adw": "Sorcery",
            "hook": "Enchantment",
            "mcp server": "Artifact"
        },
        "color_mappings": {
            "github": "Blue",
            "git": "Blue",
            "ci/cd": "Blue",
            "aws": "Green",
            "cloud": "Green",
            "documentation": "Red",
            "obsidian": "Red",
            "data": "Black",
            "database": "Black",
            "memory": "Black",
            "testing": "White",
            "validation": "White",
            "universal": "Colorless",
            "meta": "Colorless"
        },
        "edition_assignments": {
            "gbautomation core": "7ed",
            "consulting-co": "8ed",
            "revstar quickstart": "9ed"
        },
        "creature_types": {}
    }


def get_card_type_for_primitive(primitive: str, registry: Optional[Dict] = None) -> str:
    """
    Get the appropriate MTG card type for a primitive type.

    Args:
        primitive: The primitive type (agent, skill, hook, etc.)
        registry: Optional pre-loaded registry

    Returns:
        MTG card type (Creature, Instant, etc.)
    """
    if registry is None:
        registry = load_registry()

    primitive_lower = primitive.lower().strip()
    return registry.get("card_type_rules", {}).get(primitive_lower, "Creature")


def get_color_for_domain(domain: str, registry: Optional[Dict] = None) -> str:
    """
    Get the appropriate MTG color for a service domain.

    Args:
        domain: The service domain (github, aws, obsidian, etc.)
        registry: Optional pre-loaded registry

    Returns:
        MTG color name (Blue, Green, etc.)
    """
    if registry is None:
        registry = load_registry()

    domain_lower = domain.lower().strip()
    color_mappings = registry.get("color_mappings", {})

    # Direct match
    if domain_lower in color_mappings:
        return color_mappings[domain_lower]

    # Partial match
    for key, color in color_mappings.items():
        if domain_lower in key or key in domain_lower:
            return color

    return "Colorless"


def get_edition_for_project(project: str, registry: Optional[Dict] = None) -> str:
    """
    Get the appropriate MTG edition/set code for a project.

    Args:
        project: The project name
        registry: Optional pre-loaded registry

    Returns:
        Set code (7ed, 8ed, etc.)
    """
    if registry is None:
        registry = load_registry()

    project_lower = project.lower().strip()
    editions = registry.get("edition_assignments", {})

    # Direct match
    if project_lower in editions:
        return editions[project_lower]

    # Partial match
    for key, code in editions.items():
        if project_lower in key or key in project_lower:
            return code

    # Default to 8ed (consulting-co)
    return "8ed"


def color_to_scryfall_code(color: str) -> str:
    """Convert color name to Scryfall color code."""
    mapping = {
        'white': 'W',
        'blue': 'U',
        'black': 'B',
        'red': 'R',
        'green': 'G',
        'colorless': ''
    }
    return mapping.get(color.lower(), '')


def build_scryfall_query(
    primitive_type: str,
    service_domain: str,
    edition: Optional[str] = None,
    registry: Optional[Dict] = None
) -> str:
    """
    Build a Scryfall query based on registry rules.

    Args:
        primitive_type: Type of primitive (agent, skill, etc.)
        service_domain: Service domain for color
        edition: Optional edition override
        registry: Optional pre-loaded registry

    Returns:
        Scryfall query string
    """
    if registry is None:
        registry = load_registry()

    parts = []

    # Card type
    card_type = get_card_type_for_primitive(primitive_type, registry)
    parts.append(f"type:{card_type.lower()}")

    # Color
    color = get_color_for_domain(service_domain, registry)
    color_code = color_to_scryfall_code(color)
    if color_code:
        parts.append(f"color:{color_code}")

    # Edition
    if edition:
        parts.append(f"set:{edition}")
    else:
        default_edition = get_edition_for_project("consulting-co", registry)
        parts.append(f"set:{default_edition}")

    return ' '.join(parts)


# CLI interface
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Testing load_registry...")
        registry = load_registry()

        print("\nCard Type Rules:")
        for k, v in registry.get("card_type_rules", {}).items():
            print(f"  {k} -> {v}")

        print("\nColor Mappings:")
        for k, v in list(registry.get("color_mappings", {}).items())[:10]:
            print(f"  {k} -> {v}")

        print("\nEdition Assignments:")
        for k, v in registry.get("edition_assignments", {}).items():
            print(f"  {k} -> {v}")

        print("\nSample queries:")
        print(f"  Agent + GitHub: {build_scryfall_query('agent', 'github')}")
        print(f"  Hook + Data: {build_scryfall_query('hook', 'data')}")
        print(f"  Skill + AWS: {build_scryfall_query('skill (one-shot)', 'aws')}")

    else:
        print("Usage: python load_registry.py --test")
