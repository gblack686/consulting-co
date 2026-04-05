---
type: expert-file
parent: "[[obsidian/_index]]"
file-type: expertise
human_reviewed: false
source: obsidian-kb-expert + obsidian-agent-archiver + obsidian-schema-generator + obsidian-vault + playwright-validator
last_validated: 2026-02-22
tags: [expert-file, mental-model, obsidian, vault, kb, playwright]
---

# Obsidian Expertise (Complete Mental Model)

> **Sources**: obsidian-kb-expert agent, obsidian-agent-archiver SKILL, obsidian-schema-generator SKILL, obsidian-vault SKILL, playwright-validator testing session

---

## Part 1: Vault Architecture

### Primary Vault
```
C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation
```

### AI-Agent-KB Structure
```
AI-Agent-KB/
├── _Dashboard.md              # Main entry point
├── _SCHEMA.md                 # Entity-relationship model, primary/foreign keys
├── _TAXONOMY.md               # Rules, standards, content structure
├── _MTG-CARD-REGISTRY.md      # Card assignments, uniqueness tracking
├── Dashboard.base             # Master Datacore database
│
├── _assets/
│   ├── banners/               # Folder banner images (agent-banner.png etc.)
│   ├── mtg-cards/             # MTG card images (jpg, 75+ cards)
│   └── scripts/               # Python validators
│
├── 01-ADWs/                   # Agentic Developer Workflows
├── 02-Agents/                 # Claude Code Sub-Agents  ← agents/ maps here
├── 03-Skills/                 # Skills (/skill-name)
├── 04-MCP-Servers/            # MCP integrations
├── 05-Prompts/                # Prompt templates
├── 06-Scripts/                # Automation scripts
├── 07-Experts/                # Domain expert systems
├── 08-Hooks/                  # Lifecycle hooks
├── 09-Commands/               # Slash commands (< 3 steps)
├── 10-Agentic-Prompts/        # Markdown orchestrators (>= 3 steps)
└── 11-AI-Docs/                # External library docs
```

### Obsidian Config
```
C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\.obsidian/
├── snippets/
│   ├── ai-agent-kb-cards.css          # Light GB Automation theme
│   └── ai-agent-kb-dark-angular.css   # Dark angular theme (recommended)
├── plugins/
│   ├── dataview/
│   ├── datacore/              # Install via BRAT: blacksmithgu/datacore
│   ├── templater-obsidian/
│   └── obsidian-banners/
└── themes/Minimal/
```

---

## Part 2: Entity Types & Frontmatter Standards

### Entity Type → Folder Mapping

| Type | Folder | Tag | Complexity |
|------|--------|-----|------------|
| `adw` | `01-ADWs/` | `adw` | Multi-step with infrastructure |
| `agent` | `02-Agents/` | `agent` | Claude Code sub-agent |
| `skill` | `03-Skills/` | `skill` | `/skill-name` invocations |
| `mcp-server` | `04-MCP-Servers/` | `mcp-server` | MCP integrations |
| `prompt` | `05-Prompts/` | `prompt` | Reusable templates |
| `script` | `06-Scripts/` | `script` | Python/Shell automation |
| `expert` | `07-Experts/` | `expert` | Domain expertise systems |
| `hook` | `08-Hooks/` | `hook` | Lifecycle hooks |
| `command` | `09-Commands/` | `command` | Simple commands (< 3 steps) |
| `agentic-prompt` | `10-Agentic-Prompts/` | `agentic-prompt` | Complex commands (>= 3 steps) |
| `ai-doc` | `11-AI-Docs/` | `ai-doc` | External library docs |

### Required Frontmatter by Entity Type

**Agent:**
```yaml
---
name: agent-name
status: active
model: opus|sonnet|haiku
mtg_card: "Card Name"
mtg_color: U|W|R|G|B|Colorless
banner: "[[_assets/mtg-cards/card-name.jpg]]"
tags: [agent]
updated: YYYY-MM-DD
---
```

**Skill:**
```yaml
---
name: skill-name
status: active
category: automation|testing|knowledge|integration
mtg_card: "Card Name"
mtg_color: U
banner: "[[_assets/mtg-cards/card-name.jpg]]"
tags: [skill]
updated: YYYY-MM-DD
---
```

**Expert:**
```yaml
---
name: expert-name
status: active
domain: obsidian|hooks|tac|supabase|aws-org
mtg_card: "Card Name"
banner: "[[_assets/mtg-cards/card-name.jpg]]"
tags: [expert]
updated: YYYY-MM-DD
---
```

---

## Part 3: Bases (Database Views)

### Bases File Format (.base)
```yaml
filters:
  and:
    - file.hasTag("agent")
    - file.inFolder("AI-Agent-KB/agents")
    - not:
        - file.name.startsWith("_")
        - file.name.startsWith("Sample")

properties:
  name:
    displayName: Name
  status:
    displayName: Status
  mtg_card:
    displayName: MTG Card
  banner:
    displayName: Image

views:
  - type: cards
    name: Cards
    image: banner
    cardSize: 220
    coverHeight: 255
    coverPosition: top
  - type: table
    name: All Agents
    order:
      - name
      - mtg_card
      - status
```

### Bases Per Category
```
Dashboard.base          # Master "base of bases"
01-ADWs/ADWs.base
02-Agents/Agents.base   ← live agents gallery (75 agents)
03-Skills/Skills.base
04-MCP-Servers/MCP-Servers.base
05-Prompts/Prompts.base
06-Scripts/Scripts.base
07-Experts/Experts.base
```

### Embedding Bases in Notes
```markdown
![[Agents.base]]            # Embed full base
![[Agents.base#Cards]]      # Embed specific view
```

### Enable Bases Plugin
Settings → Core Plugins → Enable "Bases"

---

## Part 4: Themes & CSS

### Dark Angular Theme (Recommended)
- File: `.obsidian/snippets/ai-agent-kb-dark-angular.css`
- Backgrounds: `#0d0d0d`, `#1a1a1a`, `#242424`
- NO rounded corners — sharp angular aesthetic
- Accent: Terracotta `#D97757`
- Zero border-radius on cards

### Light GB Automation Theme
- File: `.obsidian/snippets/ai-agent-kb-cards.css`
- Background: `#F3F1E7` (warm cream)
- Panel: `#E6E4D9`
- Text: `#191919`
- Accent: `#D97757` (terracotta)
- Border: `#D6D4C8`

### MTG Color → CSS Color Mapping
| MTG Code | Color Name | Hex |
|----------|-----------|-----|
| `W` | White | `#f9faf5` |
| `U` | Blue | `#0ea5e9` |
| `B` | Black | `#1e1e2e` |
| `R` | Red | `#ef4444` |
| `G` | Green | `#22c55e` |
| `Colorless` | Gray | `#94a3b8` |

---

## Part 5: MTG Card System

### Registry File
`AI-Agent-KB/_MTG-CARD-REGISTRY.md` — tracks all assigned cards, prevents duplicates

### Card Image Location
`AI-Agent-KB/_assets/mtg-cards/*.jpg` — 75+ card images stored locally

### Card Name → File Path Convention
`"Stormtide Leviathan"` → `stormtide-leviathan.jpg`
`"Adeline, Resplendent Cathar"` → `adeline-resplendent-cathar.jpg`

### Wikilink Format in Banner Field
```yaml
banner: "[[_assets/mtg-cards/adeline-resplendent-cathar.jpg]]"
```
Note: Obsidian resolves this relative to vault root. The `AI-Agent-KB/` prefix is **not** needed — Obsidian resolves wikilinks by filename match.

---

## Part 6: Schema & Analysis Tools

### Vault Parser
```bash
uv run .claude/skills/obsidian-schema-generator/vault_parser.py \
  --vault-path "C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation" \
  --schema-type complete \
  --output-format all \
  --output-dir "./vault-schema-output"
```

### Schema Types
| Type | What It Extracts |
|------|-----------------|
| `structure` | Folder hierarchy, file counts |
| `links` | Wikilink connections, backlinks |
| `metadata` | Frontmatter, tags, properties |
| `complete` | All of the above |

### Output Formats
| Format | Use Case |
|--------|---------|
| `json` | Programmatic processing, RAG |
| `yaml` | Human-readable |
| `graphml` | 3D Graph plugin, Gephi, yEd |
| `markdown` | Reports |

---

## Part 7: Archiving Workflow (obsidian-agent-archiver)

### Steps to Archive a New Component
1. Scan source repo: identify type (agent/skill/ADW/expert/hook/command)
2. Pick template from `.claude/skills/obsidian-agent-archiver/templates/`
3. Assign MTG card (check registry for uniqueness)
4. Create note in correct folder with required frontmatter
5. Update base files if needed (bases auto-query by tag)
6. Generate banner if missing: `python scripts/create_banners.py`

### Available Templates
```
templates/
├── agent-template.md
├── adw-template.md
├── skill-template.md
├── expert-template.md
├── command-template.md
├── hook-template.md
├── prompt-template.md
├── script-template.md
├── mcp-template.md
├── agentic-prompt-template.md
├── base-template.base
└── dashboard-base-template.base
```

### Populate KB Script
```bash
python scripts/populate_kb.py \
  --source-repo "/path/to/agent-repo" \
  --obsidian-vault "C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation"
```

---

## Part 8: Playwright Testing (Vault Validation)

### What Can Be Tested With Playwright

| Target | Testable? | Method |
|--------|-----------|--------|
| Obsidian Publish sites | ✅ Yes | Standard `page.goto(url)` |
| Exported HTML notes | ✅ Yes | `file:///path/to/export.html` |
| Local Obsidian app | ❌ No | Electron blocks CDP by default |
| Rendered `.base` views | ✅ Yes | Build HTML replica from frontmatter data |

### Pattern: Render Base as HTML + Screenshot

```python
from playwright.sync_api import sync_playwright
import os, re

# 1. Parse agent frontmatter from vault
agents_dir = r"C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\agents"
assets_dir = r"C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\_assets\mtg-cards"

# 2. Build HTML card gallery from real data
# 3. Screenshot with Playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(f"file:///{html_path}")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=output_png, full_page=True)
    browser.close()
```

### Pattern: Validate Frontmatter Completeness

```python
# Check all agents have required fields
required = ["name", "status", "mtg_card", "banner"]
issues = []
for agent in agents:
    for field in required:
        if not agent.get(field):
            issues.append(f"{agent['file']}: missing {field}")
```

### Pattern: Visual Regression Testing

```python
# Capture baseline, then compare
page.screenshot(path="baseline.png")
# Later...
page.screenshot(path="current.png")
# Use Playwright's built-in comparison:
expect(page).to_have_screenshot("baseline.png")
```

### Playwright Installation
```bash
# Python (installed on this machine)
pip install playwright
playwright install chromium

# Verify
playwright --version  # 1.58.2
```

### Test Scripts Location
```
.claude/context/testing/
├── test-obsidian-playwright.py      # Main test suite
├── agents-base-view.html            # Rendered Agents.base
├── agents-base-view.png             # Screenshot of 75-agent gallery
├── obsidian-publish.png             # Obsidian Publish screenshot
└── obsidian-export-test.png         # Export HTML test
```

---

## Part 9: Hooks Integration

### SessionStart Hook → Vault Sync
```python
# Inject daily note context at session start
def handle(session_data):
    daily = read_daily_note()
    pending_tasks = extract_tasks(daily)
    return {
        "hookSpecificOutput": {
            "additionalContext": f"Pending tasks: {pending_tasks}"
        }
    }
```

### Stop Hook → Session Archive
```python
# Append session summary to daily note on session end
def handle(data):
    summary = extract_session_summary(data["transcript_path"])
    append_to_daily_note(summary)
    update_vault_index()
```

### Hook Files
```
.claude/hooks/obsidian_ecosystem_sync.py      # Main sync hook
.claude/hooks/validators/obsidian-sync-validator.py
```

---

## Part 10: Common Operations Quick Reference

### Find where to file a new component
1. Identify type → use entity type table (Part 2)
2. Check `_TAXONOMY.md` for naming conventions
3. Use template from `obsidian-agent-archiver/templates/`
4. Assign unique MTG card from `_MTG-CARD-REGISTRY.md`

### Add a new agent to the vault
```python
# Template frontmatter
name: my-new-agent
status: active
model: sonnet
mtg_card: "Unique Card Name"
mtg_color: U
banner: "[[_assets/mtg-cards/unique-card-name.jpg]]"
tags: [agent]
updated: 2026-02-22
```
File goes in: `AI-Agent-KB/agents/my-new-agent.md`
Auto-appears in `Agents.base` because it has `agent` tag + is in agents folder.

### Screenshot a .base view
```bash
python .claude/context/testing/test-obsidian-playwright.py
# Or run the render pattern from Part 8
```

### Generate vault schema
```bash
uv run .claude/skills/obsidian-schema-generator/vault_parser.py \
  --vault-path "C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation" \
  --schema-type complete --output-format markdown
```
