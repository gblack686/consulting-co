# MTG Art Finder Skill

## Overview

The **MTG Art Finder** skill provides Magic: The Gathering card search and assignment capabilities for the Claude Code ecosystem. It integrates with the Scryfall API to find thematically appropriate cards for agents, commands, hooks, and skills.

## Official Standard

This skill follows the card assignment rules defined in:

```
AI-Agent-KB/_color-registry.md
```

All card assignments MUST comply with the registry's rules for:
- **Card Types** (Creature, Instant, Sorcery, Enchantment, Artifact)
- **Color Identity** (Blue, Green, Red, Black, White, Colorless)
- **Edition Assignments** (7ed, 8ed, 9ed, 10e)

## Card Type Rules

| Primitive | MTG Card Type | Search Strategy |
|-----------|---------------|-----------------|
| **Agent** | Creature | Role-specific creature type |
| **Expert Agent** | Creature | Angel or Dragon |
| **Skill (one-shot)** | Instant | Fast actions |
| **Skill (manager)** | Enchantment | Persistent effects |
| **ADW** | Sorcery | Multi-step workflows |
| **Hook** | Enchantment | Triggered abilities |
| **MCP Server** | Artifact | Colorless tools |

## Service Domain to Color

| Service Domain | MTG Color | Scryfall Query |
|----------------|-----------|----------------|
| CI/CD, Git, GitHub | Blue | `color:blue` |
| AWS, Cloud, Infrastructure | Green | `color:green` |
| Documentation, Obsidian, Knowledge | Red | `color:red` |
| Data, Storage, Memory, Database | Black | `color:black` |
| Testing, Validation, Quality | White | `color:white` |
| Universal, Meta, Personal Apps | Colorless | `type:artifact` |

## CRITICAL: Duplicate Prevention

**Each Claude ecosystem component MUST have a UNIQUE card.**

Before assigning a card:
1. Check `AI-Agent-KB/_assets/mtg-cards/_card_metadata.json`
2. If `assigned_to` is set, the card is TAKEN - find an alternative
3. Update metadata with new assignment after confirming uniqueness

## Usage

### Search by Agent File

```bash
python scripts/mtg_search.py agent-file "/path/to/agent.md"
```

### Search by Purpose Text

```bash
python scripts/mtg_search.py agent "file implementation engineer"
```

### Search by Card Type + Color

```bash
# Blue creatures for a GitHub agent
python scripts/mtg_search.py text "color:blue type:creature" 20 1

# Red instants for a documentation command
python scripts/mtg_search.py text "color:red type:instant" 20 1
```

## Configuration

Settings are loaded from `config/settings.json`:

```json
{
  "registry_source": "AI-Agent-KB/_color-registry.md",
  "default_edition": "8ed",
  "scryfall_rate_limit_ms": 100,
  "top_n_results": 20,
  "pick_random": 1
}
```

## API Reference

### MTGArtFinder Class

```python
from scripts.mtg_search import MTGArtFinder

finder = MTGArtFinder()

# Search for agent card
cards = finder.search_for_agent(
    purpose="Strategic planning agent",
    top_n=20,
    pick_random=1
)

# Detect color from purpose
color = finder.extract_agent_color(purpose)

# Search by oracle text
cards = finder.search_by_text("draw a card", colors=["blue"])

# Search by name
cards = finder.search_by_name("Lightning Bolt")
```

### Card Object Properties

```python
card.name          # "Lightning Bolt"
card.type_line     # "Instant"
card.colors        # ["R"]
card.set_code      # "sta"
card.image_art_crop  # URL to art crop image
card.image_normal    # URL to normal card image
```

## Integration with Obsidian

After finding a card, update the Obsidian note's frontmatter:

```yaml
---
type: agent
name: "planner"
banner: "https://cards.scryfall.io/art_crop/front/..."
mtg_card: "Arcanis the Omnipotent"
mtg_color: "Blue"
mtg_edition: "10th Edition"
mtg_set_code: "10e"
---
```

## File Structure

```
.claude/skills/mtg-art-finder/
├── SKILL.md                      # This document
├── skill.json                    # Skill metadata
├── instructions.md               # Detailed usage guide
├── config/
│   └── settings.json             # Configuration
├── scripts/
│   ├── mtg_search.py             # Main Scryfall client
│   ├── update_agents.py          # Batch update utility
│   └── load_registry.py          # Registry parser
└── templates/
    └── assignment-result.md      # Output template
```

## Related Resources

- **Color Registry**: `AI-Agent-KB/_color-registry.md`
- **Card Metadata**: `AI-Agent-KB/_assets/mtg-cards/_card_metadata.json`
- **Duplicate Resolver**: `AI-Agent-KB/_assets/mtg-cards/resolve_duplicates.py`
- **Assign Command**: `.claude/commands/ecosystem/assign-mtg-cards.md`
- **Scryfall API Docs**: https://scryfall.com/docs/api

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-20 | Added duplicate prevention, registry integration |
| 1.0.0 | 2026-01-15 | Initial release |
