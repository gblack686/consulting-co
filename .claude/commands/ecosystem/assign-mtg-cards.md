---
description: Assign unique Magic The Gathering cards to Claude ecosystem components (v2.0 with duplicate prevention)
argument-hint: <inventory-json-path>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run .claude/hooks/validators/obsidian-sync-validator.py"
---

# Assign MTG Cards (v2.0)

## Purpose

Assign **unique** Magic: The Gathering cards to each Claude ecosystem component, following the rules in `_color-registry.md` and preventing duplicate assignments.

## Variables

INVENTORY_FILE: $ARGUMENTS (path to ecosystem-inventory.json)
MTG_SKILL_DIR: .claude/skills/mtg-art-finder
OBSIDIAN_VAULT: CLAUDE.md: OBSIDIAN_VAULT
AI_AGENT_KB: OBSIDIAN_VAULT/AI-Agent-KB
METADATA_FILE: AI_AGENT_KB/_assets/mtg-cards/_card_metadata.json
COLOR_REGISTRY: AI_AGENT_KB/_color-registry.md

## CRITICAL: Duplicate Prevention

**BEFORE assigning ANY card, you MUST check METADATA_FILE.**

### Pre-Assignment Check

```python
# Pseudocode for duplicate prevention
def can_assign_card(card_name, target_file):
    metadata = load_json(METADATA_FILE)
    card = metadata["cards"].get(card_name)

    if card is None:
        return True  # New card, safe to assign

    if card["assigned_to"] is None:
        return True  # Unassigned, safe to assign

    if card["assigned_to"] == target_file:
        return True  # Already assigned to this file

    return False  # DUPLICATE - find alternative
```

### When a Card is Already Taken

1. Log: `Card "{card_name}" already assigned to {assigned_to}`
2. Search for alternative using same color/type rules
3. Exclude all cards where `assigned_to` is not null
4. Pick from results

## Card Type Mapping (from _color-registry.md)

| Component Type | MTG Card Type | Scryfall Query |
|----------------|---------------|----------------|
| **Agent** | Creature | `type:creature` |
| **Expert Agent** | Creature | `(type:dragon OR type:angel)` |
| **Command** | Instant | `type:instant` |
| **Hook** | Enchantment | `type:enchantment` |
| **Skill** | Instant/Enchantment | Based on one-shot vs manager |
| **ADW** | Sorcery | `type:sorcery` |
| **MCP Server** | Artifact | `type:artifact` |

## Color Identity Mapping (from _color-registry.md)

| Service Domain | MTG Color | Scryfall Query |
|----------------|-----------|----------------|
| CI/CD, Git, GitHub | Blue | `color:blue` |
| AWS, Cloud, Infrastructure | Green | `color:green` |
| Documentation, Obsidian, Knowledge | Red | `color:red` |
| Data, Storage, Memory, Database | Black | `color:black` |
| Testing, Validation, Quality | White | `color:white` |
| Universal, Meta, Personal Apps | Colorless | `type:artifact -color:*` |

## Instructions

### 1. Load Metadata

```python
metadata = json.load(open(METADATA_FILE))
assigned_cards = {
    name: card["assigned_to"]
    for name, card in metadata["cards"].items()
    if card.get("assigned_to") is not None
}
```

### 2. Read Inventory

```python
inventory = json.load(open(INVENTORY_FILE))
```

### 3. For Each Component

```python
for component in inventory["components"]:
    # Determine card type from component type
    card_type = get_card_type(component["type"])

    # Determine color from service domain
    color = get_color_for_domain(component)

    # Build search query
    query = f"type:{card_type} color:{color} set:8ed"

    # Exclude already assigned cards
    for taken_card in assigned_cards.keys():
        query += f' -name:"{taken_card}"'

    # Search Scryfall
    results = scryfall_search(query, limit=20)

    # Pick first unassigned result
    for card in results:
        if card["name"] not in assigned_cards:
            assign_card(component, card)
            break
```

### 4. Update Obsidian Note

For each component, update the frontmatter:

```yaml
---
banner: "{{normal_url}}"
mtg_card: "{{card_name}}"
mtg_color: "{{color}}"
mtg_edition: "{{set_name}}"
mtg_set_code: "{{set_code}}"
---
```

> **Note**: Using `normal` format (full card with border) instead of `art_crop` (artwork only).

### 5. Update Metadata

After assigning, update `_card_metadata.json`:

```python
if card_name not in metadata["cards"]:
    metadata["cards"][card_name] = {
        "local_file": f"{slugify(card_name)}.jpg",
        "scryfall_id": card["id"],
        "normal_url": card["image_uris"]["normal"],  # Primary - full card
        "art_crop_url": card["image_uris"]["art_crop"],  # Secondary - artwork only
        "card_data": {
            "colors": card["colors"],
            "type_line": card["type_line"],
            "set": card["set"],
            "rarity": card["rarity"]
        },
        "assigned_to": component_file_path,
        "files_using": [component_file_path],
        "is_duplicate": False
    }
else:
    # Card exists - update assignment
    metadata["cards"][card_name]["assigned_to"] = component_file_path
    if component_file_path not in metadata["cards"][card_name]["files_using"]:
        metadata["cards"][card_name]["files_using"].append(component_file_path)

json.dump(metadata, open(METADATA_FILE, "w"), indent=2)
```

## Using the MTG Skill

### Agent Card Assignment

```bash
cd MTG_SKILL_DIR
python scripts/mtg_search.py agent-file "SOURCE_AGENT_FILE" 20 1
```

### With Exclusion List

```bash
# Build exclusion from metadata
python scripts/mtg_search.py text "color:blue type:creature set:8ed -name:'Arcanis the Omnipotent' -name:'Faerie Mastermind'" 20 1
```

## Output Format

```json
{
  "inventory_file": "path/to/inventory.json",
  "assignment_date": "2026-01-20",
  "duplicate_prevention": true,
  "metadata_version": "2.0.0",
  "assignments": [
    {
      "component_type": "agent",
      "component_name": "normalize-csv-agent",
      "component_file": "02-Agents/normalize-csv-agent.md",
      "mtg_card": "Vedalken Engineer",
      "mtg_color": "Blue",
      "mtg_type": "Creature",
      "mtg_art_url": "https://...",
      "mtg_edition": "Fifth Dawn",
      "was_duplicate_avoided": false,
      "reasoning": "Blue creature for data transformation agent"
    }
  ],
  "skipped": [
    {
      "component_name": "planner",
      "reason": "Already has unique assignment: Arcanis the Omnipotent"
    }
  ],
  "duplicates_prevented": 0,
  "summary": {
    "total_processed": 0,
    "new_assignments": 0,
    "skipped_existing": 0,
    "duplicates_avoided": 0
  }
}
```

## Report Template

```markdown
## MTG Card Assignment Report (v2.0)

### Summary
- **Total Components**: {{TOTAL}}
- **New Assignments**: {{NEW}}
- **Skipped (existing)**: {{SKIPPED}}
- **Duplicates Avoided**: {{AVOIDED}}

### New Assignments
| Component | Type | MTG Card | Color | Duplicate Avoided? |
|-----------|------|----------|-------|-------------------|
| ... | ... | ... | ... | No/Yes |

### Skipped Components
| Component | Reason |
|-----------|--------|
| planner | Already assigned: Arcanis the Omnipotent |

### Color Distribution
```
Blue:      ██████████ 15
Green:     ████████░░ 12
Red:       ██████░░░░ 8
Black:     ████░░░░░░ 6
White:     ██░░░░░░░░ 4
Colorless: █░░░░░░░░░ 2
```

### Metadata Updated
- File: AI_AGENT_KB/_assets/mtg-cards/_card_metadata.json
- Version: 2.0.0
- Total Cards: {{TOTAL_CARDS}}
- Duplicates Remaining: {{DUPLICATES}}
```

## Error Handling

### Card Not Found
If Scryfall returns no results:
1. Broaden search (remove set restriction)
2. Try adjacent color
3. Log warning and skip

### All Cards Taken
If all results from query are already assigned:
1. Expand to random selection from same color
2. Use multicolor cards
3. Log warning about limited options

### API Rate Limit
Scryfall allows 10 req/sec. The skill handles this automatically.

## Related Commands

- `/sync-claude-ecosystem` - Full ecosystem sync (calls this as Phase 6)
- `/resolve-duplicates` - Run duplicate resolution script

## Related Files

- `AI_AGENT_KB/_color-registry.md` - Authoritative rules
- `AI_AGENT_KB/_assets/mtg-cards/_card_metadata.json` - Card database
- `AI_AGENT_KB/_assets/mtg-cards/_MTG-SYSTEM.md` - System documentation
- `.claude/skills/mtg-art-finder/SKILL.md` - Skill documentation



