---
type: expert-file
parent: "[[obsidian/_index]]"
file-type: command
command-name: "self-improve"
human_reviewed: false
tags: [expert-file, command, self-improve, obsidian]
---

# Obsidian Expert - Self-Improve Mode

> Validate and update the Obsidian expertise by scanning the live vault, running Playwright checks, and reconciling with what's documented.

## Purpose
Scan the actual Gbautomation vault, check for drift from the expertise mental model, run Playwright visual validation on key `.base` views, and update `expertise.md` with any new patterns or corrections found.

## Usage
```
/experts:obsidian:self-improve
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Bash`, `Edit`

---

## Workflow

### Step 1: Scan Vault Structure

```
Glob: C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\**\*.base
Glob: C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\**\*.md
Glob: C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\.obsidian\snippets\*.css
```

Count entities per type, compare against expertise Part 1 (vault structure).

### Step 2: Validate Entity Counts

```bash
python - << 'EOF'
import os, re

agents_dir = r"C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\agents"
counts = {}
for fname in os.listdir(agents_dir):
    if not fname.endswith(".md") or fname.startswith("_"):
        continue
    # parse tag from frontmatter
    with open(os.path.join(agents_dir, fname), encoding="utf-8") as f:
        m = re.match(r"^---\n(.*?)\n---", f.read(), re.DOTALL)
    if m:
        tags_line = [l for l in m.group(1).splitlines() if "tags" in l.lower()]
        # count each entity type
print(counts)
EOF
```

### Step 3: Check Frontmatter Completeness

For each entity type, verify required fields exist:
- agents: `name`, `status`, `mtg_card`, `banner`, `tags`
- skills: `name`, `status`, `category`, `tags`
- experts: `name`, `domain`, `tags`

Report missing fields as issues.

### Step 4: Run Playwright Visual Validation

```bash
python .claude/context/testing/test-obsidian-playwright.py
```

Check:
- [ ] `agents-base-view.png` renders correctly (all 75 agents visible)
- [ ] No broken card images (missing MTG card files)
- [ ] Banner images load from `_assets/mtg-cards/`

### Step 5: Check MTG Registry for Duplicates

```bash
python - << 'EOF'
import os, re

agents_dir = r"C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\agents"
cards = {}
for fname in os.listdir(agents_dir):
    if not fname.endswith(".md"):
        continue
    with open(os.path.join(agents_dir, fname), encoding="utf-8") as f:
        m = re.match(r"^---\n(.*?)\n---", f.read(), re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if line.startswith("mtg_card:"):
                card = line.split(":", 1)[1].strip().strip('"')
                if card:
                    cards.setdefault(card, []).append(fname)

dupes = {k: v for k, v in cards.items() if len(v) > 1}
if dupes:
    print("DUPLICATE CARDS:", dupes)
else:
    print("No duplicate cards found")
EOF
```

### Step 6: Compare Against Expertise

| Check | Action |
|-------|--------|
| New entity types found | Add to Part 2 table |
| New `.base` file patterns | Update Part 3 |
| CSS changes | Update Part 4 |
| New skills/agents in source | Update Part 7 counts |
| Playwright test failures | Update Part 8 notes |
| New hook files | Update Part 9 |

### Step 7: Update Expertise

`Edit expertise.md` with:
- Updated entity counts (current as of scan date)
- Any new frontmatter fields discovered
- Corrected vault paths
- New `.base` patterns or view types
- Playwright test results and known issues
- Update `last_validated` date in frontmatter

---

## Self-Improve Report Format

```markdown
## Self-Improve Report — {date}

### Vault Scan
- Agents: {N} (was {M} in expertise)
- Skills: {N}
- ADWs: {N}
- Experts: {N}
- Base files: {N}

### Frontmatter Issues
- {N} agents missing `status` field
- {N} skills missing `category` field
- Files with issues: {list}

### Playwright Validation
- Cards rendered: {N}/{total}
- Broken images: {N} ({list})
- Screenshot: `.claude/context/testing/agents-base-view.png`

### MTG Registry
- Total cards assigned: {N}
- Duplicates found: {N} ({list or "none"})

### Expertise Updates
- Updated: Part {N} — {what changed}
- Added: {new section or entry}
- Flagged: {items for human review}

### Coverage Check
| Area | In Vault | In Expertise |
|------|----------|--------------|
| Agents.base | Yes | Yes |
| Experts.base | Yes/No | Yes/No |
| Dark angular CSS | Yes | Yes |
| vault_parser.py | Yes | Yes |
```
