---
model: opus
description: Update TAC expertise from new IndyDevDan/disler video content, then sync the canonical expertise.md and tac-expert-agent.md to all registered projects. Run after tac-organizer:sync-tac-repos completes.
argument-hint: [--extract <repo-name-or-path> | --sync-only | --check]
---

# TAC Expertise Updater

## Purpose

Extract new TAC patterns from freshly scraped IndyDevDan videos or disler repos, update the **canonical** expertise files, and propagate them to all registered projects.

**One True Source:** `C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/commands/experts/tac/`
**Propagates to:**
- `C:/Users/gblac/OneDrive/Desktop/afs/sample-multi-tenant-agent-core-app/.claude/commands/experts/tac/`
- `C:/Users/gblac/OneDrive/Desktop/hyperliquid-python-sdk/.claude/commands/experts/tac/` (create if missing)
- All `tac-expert-agent.md` files across registered projects (Primitive Library refresh)

## Variables

MODE: $1 (`--extract` | `--sync-only` | `--check`)
SOURCE: $2 (path to new repo or video transcript, used with `--extract`)

CANONICAL_EXPERTISE: `C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/commands/experts/tac/expertise.md`
CANONICAL_AGENT: `C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/agents/tac-expert-agent.md`
GITHUB_USER: `disler`
GITHUB_ORG: `https://github.com/disler`
LOCAL_CLONE_ROOT: `C:/Users/gblac/OneDrive/Desktop/tac/`

REGISTERED_PROJECTS:
- `C:/Users/gblac/OneDrive/Desktop/afs/sample-multi-tenant-agent-core-app`
- `C:/Users/gblac/OneDrive/Desktop/hyperliquid-python-sdk`
- `C:/Users/gblac/OneDrive/Desktop/consulting-co` (source — skip copy, only update in-place)

## Instructions

- **BIAS**: Prompt/agent markdown files are gold throughout. Coding implementation patterns may be superseded — extract carefully and note version/date of source
- **NEVER overwrite** the canonical expertise.md wholesale — append to the `Learnings` section only, or update existing Part sections if directly contradicted
- **DO overwrite** tac-expert-agent.md files when new ADW patterns or agent patterns are confirmed
- Always validate frontmatter after file writes: `grep -n "^---" {file}`
- Skip sync for a project if its tac expertise is already newer than the canonical (check `last_updated` frontmatter)

## Workflow

### Mode: --check
```
1. Read CANONICAL_EXPERTISE → get last_updated date

2. GITHUB DISCOVERY — find new/updated repos in the disler org:
   gh repo list disler --limit 50 --json name,pushedAt,description \
     --jq '.[] | select(.pushedAt > "{last_updated}") | [.name, .pushedAt] | @tsv' \
     | sort -k2 -r
   → Compare against LOCAL_CLONE_ROOT to identify:
     a) New repos on GitHub not yet cloned to Desktop/tac/
     b) Repos pushed after last_updated (potentially have new patterns)

3. LOCAL SCAN — check already-cloned repos for content newer than last_updated:
   - C:/Users/gblac/OneDrive/Desktop/tac/{repo}/ (cloned repos — check README, .claude/, loot.md)
   - C:/Users/gblac/tac-learning-system/ (quiz loot.md files)

4. VIDEO TRANSCRIPT SCAN — check Graphiti for TAC episodes newer than last_updated:
   - Search Graphiti for TAC-related episodes with date > last_updated

5. Report:
   GitHub: {N} new repos not yet cloned — {names}
   GitHub: {N} repos with updates since {last_updated} — {names}
   Local: {N} unprocessed repos in Desktop/tac/ — {names}
   Videos: {N} new transcripts in Graphiti — {titles}
   Total: {N} new items ready.

   Next steps:
   - Clone new repos: cd Desktop/tac && gh repo clone disler/{name}
   - Then run: /tac-organizer:update-expertise --extract Desktop/tac/{name}
```

### Mode: --extract <source>

SOURCE can be:
- A repo name: `pi-vs-claude-code` — will clone from disler org if not yet local
- A local path: `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code`
- A video transcript path: `C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/context/tac-scan/f8cfH5XX-XU_transcript.txt`

```
STEP 1 — RESOLVE AND CLONE (if needed)
  Determine source type:
    - If SOURCE is a bare repo name (no slashes, no .txt):
        local_path = LOCAL_CLONE_ROOT + SOURCE
        If local_path does NOT exist:
          RUN: cd LOCAL_CLONE_ROOT && gh repo clone disler/{SOURCE}
          Wait for clone to complete, verify directory exists
        github_url = https://github.com/disler/{SOURCE}
    - If SOURCE is a local path starting with C:/ or ./:
        local_path = SOURCE
        github_url = derive from path name: https://github.com/disler/{basename}
    - If SOURCE is a .txt file (transcript):
        transcript_mode = true → skip to STEP 2b

STEP 2a — LOAD REPO CONTENT (for cloned repos)
  Read ALL of the following that exist (parallel reads):

  Root documentation:
    - {local_path}/README.md          ← always read
    - {local_path}/CLAUDE.md          ← agent conventions, tooling
    - {local_path}/COMPARISON.md      ← feature comparisons (gold)
    - {local_path}/TOOLS.md           ← tool signatures
    - {local_path}/THEME.md           ← UI/style patterns
    - {local_path}/*.md               ← any other root markdown

  Agent/prompt files (gold throughout):
    - {local_path}/.claude/agents/*.md
    - {local_path}/.pi/agents/*.md
    - {local_path}/.pi/agents/*.yaml  ← teams.yaml, agent-chain.yaml
    - {local_path}/.gemini/agents/*.md
    - {local_path}/ai_docs/*.md

  Commands and skills:
    - {local_path}/.claude/commands/**/*.md
    - {local_path}/.pi/skills/*.md

  Hooks and extensions (list filenames, read selectively):
    - Glob: {local_path}/.claude/hooks/*.py  → list names, read 1-2 most interesting
    - Glob: {local_path}/extensions/*.ts     → list names only (implementation detail)
    - {local_path}/.pi/damage-control-rules.yaml

  Specs and loot:
    - {local_path}/specs/*.md
    - {local_path}/loot.md
    - {local_path}/tac-agent-summary.md

  Get repo push date:
    gh repo view disler/{basename} --json pushedAt --jq '.pushedAt'

STEP 2b — LOAD TRANSCRIPT CONTENT (for video transcripts)
  Read transcript file in full.
  Also read matching _metadata.json and _description.txt for:
    - Video title, date, github_links[]
  If github_links[] present → note repos referenced for future --extract runs

STEP 3 — EXTRACT NEW PATTERNS
  Read CANONICAL_EXPERTISE to know what's already documented.
  Analyze loaded content for what's NEW or UPDATED:

  a) NEW ADW patterns (new adw_*.py structures, new workflow types)
  b) NEW or UPDATED agent patterns (new Calculator/Router/Pipeline/Dispatcher/Chain variants)
  c) NEW hook patterns (new hook events, new handler approaches)
  d) NEW validation approaches (new test commands, YAML rule files, new lint tools)
  e) SUPERSEDED patterns (explicitly flagged outdated in source)
  f) NEW prompt templates or system prompt structures
  g) NEW YAML config formats (teams.yaml, agent-chain.yaml, damage-control-rules.yaml)
  h) NEW strategic framing (IndyDevDan's stated opinions, 80/20 rules, design philosophy)
  i) NEW tool or extension patterns (cross-agent loading, purpose gates, meta-agents)

  For each finding, note:
  - Pattern name and description
  - Source: {repo name or video title}
  - Date: {push date or publish date}
  - Confidence: HIGH if directly demonstrated in working code/files, LOW if inferred

STEP 4 — UPDATE CANONICAL EXPERTISE
  Read: CANONICAL_EXPERTISE

  a) Add/update repo in "Additional Specialized Projects" table (Part 3):
     If repo not yet in table → add row: | `{name}` | {focus} | {github_url} |
     If already in table → update focus description if richer info available

  b) Append new Learnings entry:
     ### {Source Name} ({Date})
     > Source: {local_path} | {github_url}
     > Video: {title if transcript source}
     > Confidence: {HIGH/MIXED/LOW}

     **New patterns confirmed:**
     | Pattern | Description |
     |---------|-------------|
     | {name} | {description} |

     **Code/config formats confirmed:** (if new YAML/JSON formats found)
     {include minimal working example}

     **Superseded patterns:** (only if explicitly called out in source)
     - {old pattern}: replaced by {new pattern}

     **Strategic framing:**
     - {IndyDevDan's stated opinions or design philosophies}

  c) If a finding directly contradicts an existing Part section:
     Update that section with a "⚠️ Updated {date}:" note inline
     Do NOT delete old content — mark it superseded

STEP 5 — UPDATE PRIMITIVE LIBRARY IN CANONICAL_AGENT
  Read CANONICAL_AGENT's ## Primitive Library section.
  Do any new agent patterns, ADW types, hook events, or validation commands
  appear in the extraction that are NOT yet in the tables?
    YES → Add rows to the relevant tables in CANONICAL_AGENT
    NO  → Skip

STEP 6 — UPDATE THIS FILE's KNOWN REPOS TABLE
  Find the "Known repos in org" table in this file (update-expertise.md).
  Update the row for {repo} (or add if new):
    | `{repo}` | ✅ cloned — patterns extracted {YYYY-MM-DD} | {github_url} |

STEP 7 — SYNC TO ALL PROJECTS (calls --sync-only internally)
```

### Mode: --sync-only
```
STEP 1 — READ CANONICAL
  Read: CANONICAL_EXPERTISE
  Read: CANONICAL_AGENT
  Get canonical last_updated date from frontmatter

STEP 2 — FOR EACH REGISTERED PROJECT (excluding consulting-co):
  a) Check if .claude/commands/experts/tac/ exists
     NO → mkdir -p {project}/.claude/commands/experts/tac/

  b) Check existing expertise.md last_updated (if exists)
     If existing >= canonical last_updated → SKIP (already current)
     If missing or older → COPY canonical

  c) Copy: CANONICAL_EXPERTISE → {project}/.claude/commands/experts/tac/expertise.md

  d) Find tac-expert-agent.md in {project}/.claude/agents/
     Exists? → Overwrite with CANONICAL_AGENT content
     Missing? → Copy CANONICAL_AGENT to {project}/.claude/agents/tac-expert-agent.md

STEP 3 — VALIDATE EACH WRITTEN FILE
  grep -n "^---" {expertise_file}  → expect line 1 + closing line
  grep "^model:" {agent_file}      → expect: model: opus
  grep "TAC BLUEPRINT" {agent_file} → expect: blueprint format present
```

## Project Registration

To add a new project to propagation, add its root path here:
```
REGISTERED_PROJECTS (add new entries below):
- C:/Users/gblac/OneDrive/Desktop/afs/sample-multi-tenant-agent-core-app
- C:/Users/gblac/OneDrive/Desktop/hyperliquid-python-sdk
```

## GitHub Org Reference

**GitHub User**: `disler` (IndyDevDan)
**All repos**: https://github.com/disler
**Local clones**: `C:/Users/gblac/OneDrive/Desktop/tac/`

### Quick discovery commands
```bash
# List all public disler repos, sorted by most recently pushed
gh repo list disler --limit 50 --json name,pushedAt,description --jq '.[] | [.pushedAt, .name, .description] | @tsv' | sort -r

# Check which are not yet cloned locally
gh repo list disler --limit 50 --json name --jq '.[].name' | while read repo; do
  [ ! -d "C:/Users/gblac/OneDrive/Desktop/tac/$repo" ] && echo "NOT CLONED: $repo"
done

# Clone a specific new repo
cd "C:/Users/gblac/OneDrive/Desktop/tac" && gh repo clone disler/{repo-name}
```

### Known repos in org (as of 2026-02-23)
| Repo | Status | GitHub |
|------|--------|--------|
| `agentic-finance-review` | ✅ cloned — NOT in expertise | https://github.com/disler/agentic-finance-review |
| `agent-experts` | ✅ cloned — L13 in expertise | https://github.com/disler/agent-experts |
| `beyond-mcp` | ✅ cloned — NOT in expertise | https://github.com/disler/beyond-mcp |
| `install-and-maintain` | ✅ cloned — NOT in expertise | https://github.com/disler/install-and-maintain |
| `claude-code-hooks-mastery` | ✅ cloned — listed but no patterns extracted | https://github.com/disler/claude-code-hooks-mastery |
| `claude-code-hooks-multi-agent-observability` | ✅ cloned — NOT in expertise | https://github.com/disler/claude-code-hooks-multi-agent-observability |
| `bowser` | ✅ cloned — NOT in expertise | https://github.com/disler/bowser |
| `orchestrator-agent-with-adws` | ✅ cloned — L14 in expertise | https://github.com/disler/orchestrator-agent-with-adws |
| `pi-vs-claude-code` | ✅ cloned — patterns extracted 2026-02-25 | https://github.com/disler/pi-vs-claude-code |

## Integration with tac-organizer:sync-tac-repos

After `sync-tac-repos --sync` completes, chain this command:
```bash
# In sync-tac-repos, add at the end:
# "After processing new repos, run tac-organizer:update-expertise --extract {repo_path}"
```

Or invoke manually after seeing new content in the sync report:
```
/tac-organizer:update-expertise --extract C:/Users/gblac/OneDrive/Desktop/tac/{new-repo-name}
```

## Report Format

```
TAC EXPERTISE UPDATE REPORT
============================
Source: {repo/video name} ({date})
Mode: {extract | sync-only | check}

Extraction Results:
  New ADW patterns: {count} — {names}
  Updated agent patterns: {count} — {names}
  Superseded patterns: {count} — {old → new}
  New validation approaches: {count}
  New prompt templates: {count}

Canonical Updated:
  File: consulting-co/.claude/commands/experts/tac/expertise.md
  Learnings section: {N lines added}
  Parts updated: {list or "none"}

Agent Primitive Library Updated:
  File: consulting-co/.claude/agents/tac-expert-agent.md
  Tables updated: {ADW | Agent Pattern | Hook | Validation | "none"}

Sync Results:
  afs/sample-multi-tenant-agent-core-app: {synced | skipped (already current) | created}
  hyperliquid-python-sdk: {synced | created | skipped}
  {additional projects}: {status}

Validation:
  All frontmatter checks: {pass | fail — list issues}
  All blueprint format checks: {pass | fail}

Next Run: tac-organizer:update-expertise --check
```
