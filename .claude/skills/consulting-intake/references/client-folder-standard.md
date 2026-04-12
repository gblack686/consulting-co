# Standard Client Folder Structure

All consulting skills that create or upload client files MUST follow this structure.

## Google Drive (`GBAutomation Clients/`)

```
{Client Name}/
├── Onboarding/
│   ├── Welcome Email & Overview          (Google Doc)
│   ├── Service Agreement                 (Google Doc)
│   ├── Pre-Session Prep Guide            (Google Doc)
│   ├── Session Agenda                    (Google Doc)
│   ├── Key Terms Glossary                (Google Doc)
│   └── {Client} — Onboarding Deck.pptx
│
├── {Client} — Session {YYYY-MM-DD}/      ← ONE per session, always
│   ├── deliverables/                     ← PDFs, PNGs, reports
│   ├── diagrams/                         ← Excalidraw + PNG pairs
│   ├── session_output/                   ← JSON profiles, inventories
│   │   └── research/                     ← Answered open questions
│   └── transcript.md                     ← Session transcript (optional)
│
├── Intelligence/                         ← Client research (pre-session)
│   ├── linkedin-profile.md
│   ├── personal-intel.md
│   └── {Client} — Research Deck.pptx
│
└── Proposals/                            ← SOWs, quotes, agreements
    └── {project-slug}-{YYYYMMDD}/
        ├── proposal.md
        ├── scope-of-work.md
        └── timeline.md
```

### Rules

1. **Every session gets its own folder** — never dump into a top-level `deliverables/`
2. Session folders named `{Client} — Session {YYYY-MM-DD}` (em dash `—`, not hyphen)
3. **Deliverables are PDFs** (not HTML/MD — they don't render in Drive)
4. Every `.excalidraw.md` must be paired with a `.png` export
5. `Intelligence/` holds pre-session research (LinkedIn, social recon, research decks)
6. `Proposals/` holds SOWs and engagement expansion docs

### Session Subfolder Contents

| Subfolder | What goes here |
|---|---|
| `deliverables/` | Final PDFs, PNGs, reports the client sees |
| `diagrams/` | Architecture diagrams (excalidraw + PNG) |
| `session_output/` | Machine-readable artifacts (JSON profiles, tool inventories) |
| `session_output/research/` | Answers to open questions from the session |

## Local Repo (`consulting-intake/client-sessions/`)

```
{YYYYMMDD}-{client-slug}/
├── session_output/              ← Parsed transcript artifacts
│   ├── client_profile.json
│   ├── tool_inventory.json
│   ├── transcript-{YYYY-MM-DD}.txt
│   └── research/
├── workspace/                   ← OpenClaw config files
│   ├── SOUL.md, USER.md, IDENTITY.md, MEMORY.md
│   ├── AGENTS.md, TOOLS.md, HEARTBEAT.md
│   └── openclaw.json
├── obsidian/                    ← Client Obsidian vault
│   ├── agents/, contacts/, intelligence/, tasks/
│   ├── workflows/, projects/, resources/
│   ├── daily/
│   ├── Dashboard.md
│   └── CLAUDE.md
├── diagrams/
└── PACKAGE_SUMMARY.md
```

## Second Brain (`gbauto/{client-slug}/`)

```
{client-slug}/
└── second-brain/
    ├── intelligence/              ← IMMUTABLE SOURCES (never edit)
    │   ├── correspondence/          email threads (Gmail pulls)
    │   ├── transcripts/             session recordings (Drive pulls)
    │   ├── decisions/               architecture decisions
    │   ├── calendar/                meeting history
    │   └── _ENGAGEMENT_TIMELINE.md
    ├── knowledge/                 ← COMPILED KNOWLEDGE (LLM-maintained)
    │   ├── index.md                 master catalog — LLM reads this first
    │   ├── log.md                   append-only compilation log
    │   ├── concepts/                single-topic deep articles
    │   ├── connections/             cross-cutting insights (2+ concepts)
    │   └── qa/                      filed query answers
    ├── agents/
    ├── contacts/
    │   ├── team/
    │   └── clients/
    ├── workflows/
    ├── projects/
    ├── resources/
    ├── tasks/
    │   ├── blockers.md
    │   ├── this-week.md
    │   └── backlog.md
    ├── daily/
    ├── Dashboard.md
    ├── CLAUDE.md
    └── SKILL.md
```

### Knowledge Compilation

Run `compile_knowledge.py` to transform raw intelligence into structured knowledge articles:

```bash
cd consulting-admin/scripts
python compile_knowledge.py --config clients/{client-slug}.json          # compile
python compile_knowledge.py --config clients/{client-slug}.json --dry-run # preview
```

The compiler reads `intelligence/` + `daily/`, calls `claude -p` to extract patterns and decisions, and writes articles to `knowledge/concepts/` and `knowledge/connections/`. The `index.md` is the master catalog — agents read it first to find relevant articles.
