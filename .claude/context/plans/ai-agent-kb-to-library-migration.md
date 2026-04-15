# AI-Agent-KB to the-library Migration Plan

**Created:** 2026-04-14
**Status:** Draft
**Source:** `gbauto/second-brain` (git history, pre-wipe commit)
**Target:** `gbauto-tac/the-library` (to be created)

---

## 1. Objectives

1. Recover old AI-Agent-KB content from `gbauto/second-brain` git history (pre-wipe commit)
2. Create `gbauto-tac/the-library` as canonical archive of all agent definitions, skills, scripts, hooks, ADWs, and domain knowledge
3. Restructure from Obsidian-centric format into git-native reference library
4. Deduplicate against content in `consulting-co/.claude/`

---

## 2. Old AI-Agent-KB Structure

```
01-domains/           # automation skills, scripts, MCP servers, agents, hooks, commands, ADWs
03-reference/         # reference materials
05-people/            # personal data (discard)
```

Plus the deeper AI-Agent-KB vault structure:
- `01-ADWs/`, `02-Agents/` (~75), `03-Skills/`, `04-MCP-Servers/`, `05-Prompts/`
- `06-Scripts/`, `07-Experts/`, `08-Hooks/`, `09-Commands/`, `10-Agentic-Prompts/`, `11-AI-Docs/`
- `_SCHEMA.md`, `_TAXONOMY.md`, `_MTG-CARD-REGISTRY.md`

---

## 3. Keep vs Discard

**KEEP:** All agent, skill, ADW, hook, command, expert, MCP server, script, prompt, agentic-prompt, and AI-docs definitions. Schema/taxonomy. Domain knowledge. Reference materials.

**DISCARD:** `*.base` files, `.obsidian/` config, `_assets/banners/`, `_assets/mtg-cards/` (re-downloadable from Scryfall), `_assets/scripts/` (Obsidian validators), CSS themes, `_Dashboard.md`, `05-people/`.

---

## 4. Target Structure

```
the-library/
├── README.md
├── CLAUDE.md
├── library.yaml              # Machine-readable catalog
├── agents/                   # From 02-Agents/
├── skills/                   # From 03-Skills/
├── adws/                     # From 01-ADWs/
├── hooks/                    # From 08-Hooks/
├── commands/                 # From 09-Commands/
├── experts/                  # From 07-Experts/
├── mcp-servers/              # From 04-MCP-Servers/
├── scripts/                  # From 06-Scripts/
├── prompts/                  # From 05-Prompts/
├── agentic-prompts/          # From 10-Agentic-Prompts/
├── ai-docs/                  # From 11-AI-Docs/
├── domains/                  # From 01-domains/
├── reference/                # From 03-reference/
└── schema/
    ├── SCHEMA.md
    ├── TAXONOMY.md
    └── MTG-CARD-REGISTRY.md
```

---

## 5. Content Transformation

1. Strip Obsidian-only frontmatter (`cssclasses`, `banner`, `mtg_color`)
2. Convert wikilinks: `[[Agent Name]]` → `[Agent Name](agents/agent-name.md)`
3. Remove Obsidian embeds: `![[SomeBase.base]]` and `![[image.jpg]]`
4. Preserve all substantive content

---

## 6. Deduplication

- `consulting-co/.claude/` holds **live, actively-used** versions
- AI-Agent-KB held **documentation snapshots** with extra metadata
- Strategy: merge unique AI-Agent-KB content absent from consulting-co. `library.yaml` includes `live_source` field pointing to consulting-co when applicable
- No overlap with `Desktop/tac/` clones (those are disler's upstream repos)

---

## 7. Execution Steps

```
Step 1:  Clone gbauto/second-brain, identify pre-wipe commit SHA
Step 2:  Checkout pre-wipe commit, inventory all files
Step 3:  gh repo create gbauto-tac/the-library --private
Step 4:  Copy content to target structure (drop numeric prefixes, discard artifacts)
Step 5:  Transform (strip Obsidian frontmatter, convert wikilinks, remove embeds)
Step 6:  Generate library.yaml from file inventory
Step 7:  Write README.md and CLAUDE.md
Step 8:  Deduplication audit against consulting-co/.claude/
Step 9:  Commit and push
Step 10: Update consulting-co references (tac-organizer, obsidian expertise, CLAUDE.md)
```

**Estimated effort:** 2-3 hours for a single Claude session.

---

## 8. Acceptance Criteria

1. Pre-wipe commit SHA identified and all content extracted
2. `gbauto-tac/the-library` repo exists with target structure
3. All definitions present with Obsidian formatting stripped
4. Zero `.base` files, zero wikilink embeds, zero `cssclasses`
5. `library.yaml` has entry for every markdown file
6. Entries with consulting-co counterparts have `live_source` field
7. consulting-co references updated
8. README sufficient for developer or Claude agent to find any definition

---

## 9. Files to Update in consulting-co

- `.claude/commands/tac-organizer/sync-tac-repos.md` — update `OBSIDIAN_KB` variable
- `.claude/commands/experts/obsidian/expertise.md` — note AI-Agent-KB moved to the-library
- `CLAUDE.md` — add reference to the-library as canonical archive
