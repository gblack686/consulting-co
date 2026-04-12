# Cole Medin Second Brain / Wiki Pattern Research

**Date:** 2026-04-11
**Repos Analyzed:**
- [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) -- THE wiki/knowledge base repo
- [coleam00/second-brain-starter](https://github.com/coleam00/second-brain-starter) -- PRD generator for building your own second brain
- [coleam00/second-brain-skills](https://github.com/coleam00/second-brain-skills) -- Skill library (pptx, sop, brand, remotion, etc.)
- [coleam00/second-brain-research-dashboard](https://github.com/coleam00/second-brain-research-dashboard) -- Generative UI for research docs
- [coleam00/Archon](https://github.com/coleam00/Archon) -- Agent harness/workflow engine (separate from second brain)

---

## Key Finding: The Wiki IS the Second Brain

Cole Medin's implementation splits the "second brain" into **4 separate repos**, each handling a different concern. The wiki (Karpathy LLM Knowledge Base pattern) lives in `claude-memory-compiler`. It is NOT inside Archon. Archon is a separate coding workflow engine.

---

## 1. Wiki Structure (claude-memory-compiler)

### The Compiler Analogy
```
daily/          = source code    (your conversations - raw material)
LLM             = compiler       (extracts and organizes knowledge)
knowledge/      = executable     (structured, queryable knowledge base)
lint            = test suite     (health checks)
queries         = runtime        (using the knowledge)
```

### Three Layers

**Layer 1: `daily/` -- Conversation Logs (Immutable Source)**
- Append-only daily logs: `daily/YYYY-MM-DD.md`
- Each file has Sessions with: Context, Key Exchanges, Decisions Made, Lessons Learned, Action Items
- Never edited after creation

**Layer 2: `knowledge/` -- Compiled Knowledge (LLM-Owned)**
```
knowledge/
  index.md              # Master catalog -- every article with one-line summary (TABLE format)
  log.md                # Append-only chronological build log
  concepts/             # Atomic knowledge articles (one per topic)
  connections/          # Cross-cutting insights linking 2+ concepts
  qa/                   # Filed query answers (compounding knowledge)
```

**Layer 3: `AGENTS.md` -- The Schema**
- The "compiler specification" that tells the LLM how to compile and maintain everything
- This is NOT CLAUDE.md -- it's AGENTS.md (OpenAI Codex convention, works with both)

### Full Project Structure
```
llm-personal-kb/
  .claude/settings.json          # Hook configuration
  AGENTS.md                      # Schema + full technical reference
  daily/                         # Conversation logs (immutable)
  knowledge/
    index.md                     # Master catalog (THE retrieval mechanism)
    log.md                       # Append-only build log
    concepts/                    # Atomic knowledge articles
    connections/                 # Cross-cutting insights linking 2+ concepts
    qa/                          # Filed query answers
  scripts/
    compile.py                   # daily/ -> knowledge/ articles
    query.py                     # Ask questions (index-guided, NO RAG)
    lint.py                      # 7 health checks
    flush.py                     # Extract memories from conversations (background)
    config.py                    # Path constants
    utils.py                     # Shared helpers
  hooks/
    session-start.py             # Injects knowledge index into every session
    session-end.py               # Extracts conversation -> daily log
    pre-compact.py               # Captures context before compaction
  reports/                       # Lint reports (gitignored)
```

---

## 2. How Agents Read/Write to the Wiki

### Automatic Pipeline: Capture -> Extract -> Compile -> Retrieve -> Maintain

**Reading (session-start.py hook):**
- Fires on SessionStart
- Reads `knowledge/index.md` + most recent daily log
- Injects into conversation context via `hookSpecificOutput`
- Max 20,000 characters
- Pure local I/O, no API calls, <1 second

**Writing (session-end.py + pre-compact.py hooks):**
- Fire on SessionEnd and PreCompact
- Copy raw JSONL transcript to temp file
- Spawn `flush.py` as fully detached background process
- flush.py calls Claude Agent SDK to decide what's worth saving
- Appends structured bullets to `daily/YYYY-MM-DD.md`
- Recursion guard: `CLAUDE_INVOKED_BY` env var prevents infinite loops

**Compiling (compile.py):**
- Uses Claude Agent SDK `query()` with tools: Read, Write, Edit, Glob, Grep
- `permission_mode="acceptEdits"` -- auto-approves all file ops
- Reads: AGENTS.md schema + current index + existing articles + daily log
- Claude decides what concepts to extract, writes files directly
- Auto-triggers after 6 PM if daily log has changed (hash comparison in state.json)
- Cost: ~$0.45-0.65 per daily log

**Querying (query.py):**
- Loads entire KB into context (index + all articles) -- NO RAG
- LLM reads structured index, selects 3-10 relevant articles, synthesizes answer
- `--file-back` flag saves answer as `knowledge/qa/` article and updates index
- Works because at personal scale (50-500 articles), LLM > cosine similarity

### No RAG by Design
At personal scale, an LLM reading `index.md` outperforms vector search. The LLM understands what you're really asking; embeddings just find similar words. RAG only needed at ~2,000+ articles.

---

## 3. Article Formats

### Concept Articles (`knowledge/concepts/`)
```yaml
---
title: "Concept Name"
aliases: [alternate-name]
tags: [domain, topic]
sources: ["daily/2026-04-01.md"]
created: 2026-04-01
updated: 2026-04-03
---
```
Body: 2-4 sentence explanation, Key Points (bullets), Details (paragraphs), Related Concepts ([[wikilinks]]), Sources

### Connection Articles (`knowledge/connections/`)
```yaml
---
title: "Connection: X and Y"
connects: ["concepts/concept-x", "concepts/concept-y"]
sources: ["daily/2026-04-04.md"]
---
```
Body: The Connection, Key Insight, Evidence, Related Concepts

### Q&A Articles (`knowledge/qa/`)
```yaml
---
title: "Q: Original Question"
question: "The exact question asked"
consulted: ["concepts/article-1", "concepts/article-2"]
filed: 2026-04-05
---
```
Body: Answer with [[wikilinks]], Sources Consulted, Follow-Up Questions

---

## 4. Lint System (7 Health Checks)

| Check | Type | Catches |
|-------|------|---------|
| Broken links | Structural | [[wikilinks]] to non-existent articles |
| Orphan pages | Structural | Articles with zero inbound links |
| Orphan sources | Structural | Daily logs not yet compiled |
| Stale articles | Structural | Source logs changed since compilation |
| Missing backlinks | Structural | A links to B but B doesn't link back |
| Sparse articles | Structural | Under 200 words |
| Contradictions | LLM | Conflicting claims across articles |

---

## 5. How Archon Relates (It Doesn't, Really)

Archon is a **separate system** -- a YAML workflow engine for AI coding. It:
- Defines dev processes as YAML workflows in `.archon/workflows/`
- Uses markdown commands in `.archon/commands/`
- Has its own CLAUDE.md focused on TypeScript coding conventions
- Does NOT use the wiki/second-brain pattern
- Does NOT reference claude-memory-compiler

**They are independent projects by the same author.** Archon is for coding workflows; the second brain repos are for personal knowledge management.

---

## 6. The Second Brain Starter (PRD Generator)

The `second-brain-starter` repo is a Claude skill that generates a personalized PRD for building your OWN second brain. Key architectural components it recommends:

### Memory Layer
- `SOUL.md` -- Agent personality and boundaries
- `USER.md` -- User profile, preferences, accounts
- `MEMORY.md` -- Key decisions, active projects (loaded every session)
- `daily/YYYY-MM-DD.md` -- Timestamped session logs
- `HEARTBEAT.md` -- What heartbeat should monitor
- `HABITS.md` -- Daily pillars with auto-detection rules

### Integration Pattern
Each integration is a Python module in `.claude/scripts/integrations/`:
- Data model (dataclass) -> Auth -> Query functions -> Context formatter -> CLI
- Registry tracks available integrations
- Unified CLI: `query.py gmail list`, `query.py asana overdue`
- LLM never sees API tokens -- Python handles auth

### Proactive Systems
- **Heartbeat**: 30-min cycle, Python gathers data BEFORE invoking Claude, Claude reasons over pre-loaded context
- **Daily Reflection**: Reviews yesterday's daily log at 8 AM, promotes important items to MEMORY.md
- **Draft Management**: Active/Sent/Expired lifecycle in `drafts/` folder, voice-matching via RAG on sent drafts

### Security: Three Layers
1. **Sanitize**: Pattern detection + markdown escaping + XML trust boundaries
2. **Guardrails**: Deterministic pre-check + LLM evaluation (pass/fail/suspicious)
3. **API Key Isolation**: Python CLI wrapper handles auth, LLM only sees data

---

## 7. Key Design Principles (Across All Repos)

1. **Local files are king** -- Zero latency, no API auth, no rate limits
2. **Deterministic + LLM hybrid** -- Python gathers data, Claude reasons
3. **Everything is markdown** -- Knowledge, memory, daily logs, all .md files
4. **Progressive disclosure** -- Load only what's needed (metadata -> skill body -> resources)
5. **Skills are modular** -- Self-contained packages: SKILL.md + scripts/ + references/ + assets/
6. **No RAG at personal scale** -- Index-guided retrieval beats vector similarity below ~2K articles
7. **Obsidian-compatible** -- [[wikilinks]], works natively as Obsidian vault
