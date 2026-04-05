# MTG Art Finder Skill

Search for Magic: The Gathering card art using the Scryfall API.

## Usage

```bash
cd .claude/skills/mtg-art-finder
python scripts/mtg_search.py <command> <args>
```

## Commands

### Search by Name
```bash
python scripts/mtg_search.py name "Lightning Bolt"
python scripts/mtg_search.py name "Black Lotus"
```

### Search by Oracle Text (Card Function)
Find cards with specific abilities:
```bash
python scripts/mtg_search.py text "draw a card"
python scripts/mtg_search.py text "destroy target creature" black
python scripts/mtg_search.py text "flying" white,blue
```

### Search by Color
```bash
python scripts/mtg_search.py color red
python scripts/mtg_search.py color blue,black
python scripts/mtg_search.py color green,white
```

### Random Card
```bash
python scripts/mtg_search.py random
python scripts/mtg_search.py random "type:dragon"
python scripts/mtg_search.py random "color:red rarity:mythic"
```

## Color Codes
- **W** = White
- **U** = Blue
- **B** = Black
- **R** = Red
- **G** = Green
- **C** = Colorless

You can use full names (white, blue, black, red, green) or codes (W, U, B, R, G).

## Output

Each card result includes:
- Card name, mana cost, type
- Colors and color identity
- Set name, rarity, artist
- Oracle text (card rules)
- **Art URLs** in multiple sizes:
  - `art_crop` - Just the art, no card frame (best for art reference)
  - `normal` - Standard card image
  - `large` - High-res card image
  - `png` - Highest quality PNG

## Scryfall Search Syntax

For advanced searches, you can use full Scryfall syntax:

```bash
# Creatures with power 5 or greater
python scripts/mtg_search.py text "power>=5 type:creature"

# Mythic rares from a specific set
python scripts/mtg_search.py text "set:neo rarity:mythic"

# Legendary creatures in commander colors
python scripts/mtg_search.py text "type:legendary type:creature color<=wubrg"
```

See [Scryfall Search Reference](https://scryfall.com/docs/syntax) for full syntax.

## Python API

```python
from scripts.mtg_search import MTGArtFinder

finder = MTGArtFinder()

# Search by name
cards = finder.search_by_name("Sol Ring")

# Search by ability text + color
cards = finder.search_by_text("draw a card", colors=["blue"])

# Get art URL
for card in cards:
    print(card.name, card.image_art_crop)

# Download art
finder.download_art(cards[0], "sol_ring_art.jpg", size="art_crop")
```

## Rate Limits

Scryfall asks for 50-100ms between requests. The client handles this automatically.

---

## Agent Art Search

The most powerful feature: automatically find MTG art for Claude Code agents based on their purpose.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  agent-file build-agent.md                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Extract Purpose Section from markdown                    │
│     "Specialist for implementing one specific file..."       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Keyword Detection → MTG Concepts                         │
│     "implement" → oracle:create type:creature                │
│     "build" → Red color                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Scryfall Search (top 20 by EDHREC popularity)            │
│     GET /cards/search?q=...&order=edhrec                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Pick 1 Random from Top 20                                │
│     → Adds variety for similar agent purposes                │
└─────────────────────────────────────────────────────────────┘
```

### Search by Agent File

```bash
# Basic usage - reads agent .md file, extracts purpose, returns 1 card
python scripts/mtg_search.py agent-file /path/to/agent.md

# Custom parameters: top_n=30, pick_random=3
python scripts/mtg_search.py agent-file /path/to/agent.md 30 3
```

### Search by Purpose Text

```bash
# Direct purpose text input
python scripts/mtg_search.py agent "specialized file implementation engineer"

# With custom parameters
python scripts/mtg_search.py agent "strategic planning and analysis" 20 1
```

### Keyword → MTG Query Mapping

| Agent Keywords | MTG Query Generated |
|---------------|---------------------|
| create, write, build, implement | `oracle:create type:creature` |
| engineer, artificer, builder | `(type:artificer OR type:engineer)` |
| plan, strategic, analyze, design | `(oracle:scry OR oracle:"look at")` |
| research, investigate, explore | `(oracle:scry OR oracle:"search your library")` |
| validate, test, verify, protect | `(oracle:prevent OR oracle:indestructible)` |
| fast, quick, rapid | `oracle:haste` |
| memory, store, persist | `(oracle:graveyard OR oracle:"return from")` |
| copy, spawn, clone, meta | `oracle:"create a copy"` |
| scrape, fetch, gather, draw | `oracle:"draw a card"` |

### Color Detection

| Detected Color | Keywords in Purpose |
|---------------|---------------------|
| White | validate, protect, rule, permission, safe |
| Blue | plan, analyze, research, strategy, optimize |
| Black | memory, persist, store, retrieve, data |
| Red | fast, quick, build, execute, deploy |
| Green | grow, adapt, learn, scale, improve |

### Batch Update Script

Update all agents in a directory:

```bash
#!/bin/bash
# update_agent_art.sh

AGENTS_DIR="C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB/02-Agents"
SKILL_DIR="C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills/mtg-art-finder"

for agent_file in "$AGENTS_DIR"/*.md; do
    if [[ $(basename "$agent_file") != _* ]]; then
        echo "Processing: $(basename "$agent_file")"
        python "$SKILL_DIR/scripts/mtg_search.py" agent-file "$agent_file"
        echo "---"
    fi
done
```

### Python API

```python
from scripts.mtg_search import MTGArtFinder

finder = MTGArtFinder()

# Search by purpose text
purpose = "Specialized file implementation engineer focused on writing production code"
cards = finder.search_for_agent(purpose, top_n=20, pick_random=1)

if cards:
    card = cards[0]
    print(f"Card: {card.name}")
    print(f"Art URL: {card.image_art_crop}")

# Get color from purpose
color = finder.extract_agent_color(purpose)
print(f"Detected Color: {color}")
```

---

## Claude Code → MTG Concept Mapping

Use this mapping to find thematic art for Claude Code primitives:

### Card Type Mappings

| Claude Primitive | MTG Card Type | Search Strategy |
|-----------------|---------------|-----------------|
| **Agent** | Creature | Search by creature abilities that match agent function |
| **Skill** | Instant | Fast, reactive spells |
| **ADW (Workflow)** | Sorcery | Multi-step, complex spells |
| **Hook** | Enchantment | Persistent triggered effects |
| **MCP Server** | Artifact | Colorless utility tools |
| **Expert** | Planeswalker | Powerful entities with multiple abilities |
| **Infrastructure** | Land | Resource providers |

### Color Identity Mappings

| Color | Claude Domain | Use When Agent Does... |
|-------|--------------|----------------------|
| **White (W)** | Governance & Safety | Validation, permissions, rules |
| **Blue (U)** | Intelligence & Analysis | Planning, research, optimization |
| **Black (B)** | Persistence & Memory | Data storage, retrieval, state |
| **Red (R)** | Speed & Execution | Fast builds, deployments |
| **Green (G)** | Growth & Adaptation | Learning, scaling, improvement |
| **Colorless** | Universal Tools | Cross-domain utilities |

### Example: Finding Art for Agents

```bash
# build-agent (Red - creates files quickly)
python scripts/mtg_search.py text "create a token" red

# planner (Blue - strategic thinking)
python scripts/mtg_search.py text "search your library" blue

# meta-agent (Planeswalker - creates other agents)
python scripts/mtg_search.py name "Jace"
python scripts/mtg_search.py text "create a copy" blue

# docs-scraper (Blue/Black - gathers information)
python scripts/mtg_search.py text "draw cards" blue,black

# playwright-validator (White - tests and validates)
python scripts/mtg_search.py text "prevent" white

# memory-hook (Black - persistence)
python scripts/mtg_search.py text "return from graveyard" black
```

### Database Reference

Full mapping stored in Supabase table `mtg_concept_mapping` with:
- Card type mappings (7 entries)
- Color identity mappings (6 entries)
- Game mechanic mappings (12 entries)

Query with:
```sql
SELECT mtg_concept, claude_primitive, description
FROM mtg_concept_mapping
WHERE primitive_type = 'card_type';
```

### Obsidian Reference

Full documentation: `AI-Agent-KB/MTG-Concept-Mapping.md`
