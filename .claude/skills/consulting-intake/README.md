# Consulting Intake — Master README
**GBAutomation OpenClaw Consulting Pipeline**
Last updated: 2026-03-18

---

## What This Is

The consulting intake pipeline transforms a 90-minute client discovery session into a fully-deployed OpenClaw agent workspace. It handles everything from transcript → parsed session data → workspace files → domain expert systems → GitHub repo → deployment.

Three clients have been processed:
- `20260221-greg-trading` — Algorithmic trading, Hyperliquid, Discord signal scraping ✅ Full build
- `20260305-michael-fisch` — Accounting/finance consulting, QuickBooks, Cin7, Airtable ✅ Full build + Session 2
- `20260305-erica-creations` — Creative/content work 🔶 Partial (workspace only, no expert build)

---

## Folder Structure

```
consulting-intake/
├── SKILL.md                    ← Main skill definition (the pipeline brain)
├── README.md                   ← This file
│
├── references/                 ← Pipeline intelligence (read-only, don't modify without reason)
│   ├── session-framework.md    ← 30 discovery questions → file mapping
│   ├── openclaw-workspace-spec.md
│   ├── skill-format-spec.md
│   ├── expert-system-pattern.md ← 8-file expert structure
│   ├── agent-architecture.md
│   ├── multi-agent-patterns.md  ← 5 deployment patterns
│   ├── model-tiers.md           ← Cheap/Mid/Pro tiers with OpenRouter IDs
│   ├── tac-pattern-library.md
│   ├── quality-rubric.md
│   ├── pi-extension-selection.md ← Pi/OpenClaw extension stacks
│   ├── github-repo-strategy.md
│   └── skill-format-spec.md
│
├── templates/                  ← Reusable file templates (fill {placeholders})
│   ├── *.md.tmpl               ← Workspace file templates (SOUL, USER, IDENTITY, etc.)
│   ├── openclaw.json.tmpl      ← Full OpenClaw config template
│   ├── justfile.tmpl           ← Client justfile
│   ├── skill.md.tmpl           ← OpenClaw SKILL.md template
│   ├── mac-mini-install.md     ← Mac Mini deployment guide
│   ├── expert/                 ← 8-file expert system templates
│   ├── agent-workspace/        ← Per-domain agent workspace templates
│   ├── agents/youtube/         ← YouTube agent template (skills: extract-transcript, scan-channel, summarize-video)
│   ├── agentic-coder/          ← Agentic coder workspace template
│   └── skills/
│       ├── setup-openclaw/     ← Universal setup skill (every client gets this)
│       └── domain-discovery/   ← Bootstrap prompts for first-session domain discovery
│
├── client-facing/              ← Client-facing documents
│   ├── welcome-email.md
│   ├── pre-session-prep.md
│   ├── session-agenda.md
│   ├── service-agreement.md
│   └── key-terms.md
│
└── client-sessions/            ← One folder per client session
    ├── YYYYMMDD-{project}/
    │   ├── session_output/     ← Raw parsed data (INTERNAL — never deploy)
    │   │   ├── client_profile.json
    │   │   ├── tool_inventory.json
    │   │   ├── soul_draft.md
    │   │   ├── identity.json
    │   │   ├── mission_statement.md
    │   │   ├── autonomy.json
    │   │   ├── domains/*.json
    │   │   └── workflow-catalog.json  ← 18-27 numbered workflows with priority scores
    │   ├── workspace/          ← Client OpenClaw files (deploy this)
    │   │   ├── SOUL.md, USER.md, IDENTITY.md, MEMORY.md, AGENTS.md, TOOLS.md, HEARTBEAT.md
    │   │   ├── openclaw.json
    │   │   ├── cron-setup.sh
    │   │   └── skills/{domain}/{skill-name}/SKILL.md
    │   ├── experts/{domain}/   ← Claude Code expert systems (8 files each)
    │   ├── agents/youtube/     ← YouTube agent (separate from domain experts)
    │   ├── diagrams/           ← Architecture diagrams (.excalidraw.md + .png)
    │   ├── PACKAGE_SUMMARY.md
    │   ├── VALIDATION_REPORT.md
    │   └── justfile            ← Client runbook
```

---

## Pipeline Summary

```
Session Transcript
      ↓
Step 1: Parse Transcript → session_output/ (client_profile, soul, identity, mission, tool_inventory, domains, autonomy)
      ↓
Step 2: Build Workspace → workspace/ (7 .md files + openclaw.json + cron-setup.sh)
      ↓
Step 2b: Pi Extensions + .pi/agents/ → extensions/ directory + agent definitions
      ↓
Step 3: Build Domain Experts → experts/{domain}/ (8 files each, plan-build-improve-validate)
      ↓
Step 4: Generate Workflow Catalog → session_output/workflow-catalog.json + .md
      ↓
Step 5a: GitHub Repo Setup → gbauto/{client-project} (private, branch: main)
      ↓
Step 5b: Deploy → ZeroClaw CDK / local Windows / SSH / Mac Mini
```

**Quality gate:** 80% score on quality-rubric.md before shipping.

---

## Pi Extensions = OpenClaw Extensions

**Yes, they are the same thing.** OpenClaw uses Pi as its runtime. Pi extensions are `.ts` files loaded via `-e` flags. The reference implementations live at:
```
C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions/
```

Every client workspace gets 16 extensions copied at build time. Selection matrix: `references/pi-extension-selection.md`.

Top community extensions (as of March 2026):
- `oh-my-pi` — all-in-one (LSP, browser, web search, subagents, image gen)
- `mitsuhiko/agent-stuff` — reference implementation, cost analytics, review loops
- `badlogic/pi-skills` — official skills (Gmail, Drive, Calendar, YouTube, Brave)
- `hjanuschka/shitty-extensions` — branch-sessions, oracle (2nd opinions), plan-mode

---

## What Needs to Be Built — Meta Skills Backlog

The following meta skills need to be created as **universal skills** that ship with every client workspace. These are not client-specific — they are platform-level infrastructure.

### META-1: Obsidian Sync Skill
**Priority:** High | **Effort:** Medium

Every OpenClaw deployment needs Obsidian as its second brain. The agent should log meaningful events to Obsidian automatically without logging every message.

**Trigger events that should write to Obsidian:**
- File created or modified in workspace
- Domain updated (new workflow added, skill changed)
- Cron job completes
- Weekly performance summary generated
- Error or failure logged
- New client onboarded

**Design:**
- Sub-agent pattern: main agent fires a `sync-obsidian` sub-agent after trigger events
- Sub-agent writes a structured note to the correct Obsidian vault folder
- Note template: date, agent name, event type, summary, linked file(s)
- Vault path: `GBAutomation Clients / {Client} / Agent Log / YYYY-MM-DD.md`
- Append-mode: multiple events per day append to the daily log note
- Change log: every file mutation creates a diff-style entry
- Uses `obsidian-agent-archiver` as reference implementation

**Files to create:**
```
templates/skills/obsidian-sync/SKILL.md
references/obsidian-integration.md
```

**Research needed:**
- Best practices for Obsidian API / local REST plugin
- Frontmatter schema for agent log notes
- Existing `obsidian-agent-archiver` skill (already in this .claude)

---

### META-2: GitHub SDLC Skill
**Priority:** High | **Effort:** Medium

Every coding agent needs a standardized software delivery lifecycle. This skill defines conventions and provides executable commands.

**Components:**

1. **Commit conventions** (Conventional Commits):
   - Format: `type(scope): description`
   - Types: feat, fix, refactor, docs, test, chore, skill, agent
   - Scope = domain name (e.g. `feat(discord-scraping): add signal quality scorer`)

2. **Branch conventions:**
   - `main` — stable, deployed
   - `update/YYYYMMDD-{description}` — client updates
   - `skill/{skill-name}` — new skill development
   - `fix/{issue-slug}` — bug fixes
   - `client/{YYYYMMDD-project}` — client session branches (existing convention)

3. **PR conventions:**
   - Title: `[{client}] {type}: {description}` or `[skill] {skill-name}: {description}`
   - Body: Summary, Test Plan, Screenshots (if UI), Checklist
   - Labels: `skill`, `client-workspace`, `meta`, `bug`, `enhancement`
   - Auto-assign reviewer: Greg (gbauto org owner)

4. **Linear integration:**
   - Every PR references a Linear issue: `Fixes LIN-{id}` or `Refs LIN-{id}`
   - Linear project: GBAutomation Marketplace Ecosystem
   - Issue creation from workflow catalog items (each WF-XXX → Linear issue)
   - Labels match: `skill`, `meta`, `client-{name}`

5. **CI/CD pipeline** (GitHub Actions):
   - On PR: lint + validate SKILL.md frontmatter, check template placeholders filled
   - On merge to main: auto-tag with `v{YYYYMMDD}`
   - On tag: package workspace as `.tar.gz` artifact
   - Validation: run `consulting-intake validate` against changed client sessions

**Files to create:**
```
references/sdlc-conventions.md
templates/skills/github-sdlc/SKILL.md
.github/workflows/validate-intake.yml   (in repo root)
.github/pull_request_template.md
```

---

### META-3: YouTube Intelligence Skill (Universal)
**Priority:** High | **Effort:** Low (template already exists)

YouTube scraping is a **core domain** that ships with every OpenClaw workspace, not just Greg's. Every client benefits from competitive intelligence, tutorial discovery, and market research via YouTube.

**Already built (Greg's workspace):**
- `templates/agents/youtube/` — full agent template with 3 skills
- `agents/youtube/skills/youtube/extract-transcript/SKILL.md`
- `agents/youtube/skills/youtube/scan-channel/SKILL.md`
- `agents/youtube/skills/youtube/summarize-video/SKILL.md`

**What's missing:**
- Not yet promoted to universal template (currently Greg-specific with trading context)
- No `references/youtube-agent.md` documenting the pattern
- `yt-dlp` dependency not documented in setup
- No channel registry concept (client-specific tracked channels)

**Upgrades needed:**
- Generalize SOUL/IDENTITY from trading context to universal
- Add `channel-registry` skill: manage a list of tracked channels per client
- Add `market-research` mode: search by topic/keyword, not just followed channels
- Document yt-dlp install path: `C:/Users/gblac/AppData/Local/Programs/Python/Python312/Scripts/yt-dlp`
- Connection to Obsidian: summaries write to `Obsidian/Research/YouTube/{YYYY-MM}/`

**Files to create/update:**
```
templates/agents/youtube/SOUL.md         ← generalize from trading context
templates/agents/youtube/IDENTITY.md     ← generalize
references/youtube-agent.md             ← setup, yt-dlp, channel registry pattern
templates/skills/youtube/channel-registry/SKILL.md  ← new
```

**Pi extensions note:** `badlogic/pi-skills` includes a YouTube transcript skill. `nicobailon/pi-web-access` includes YouTube with Gemini visual descriptions. Both are available as extensions and complement the agent-level skills.

---

### META-4: Web Research / Market Intelligence Skill
**Priority:** Medium | **Effort:** Medium

General-purpose web scraping and market research. Used for competitive intel, trend tracking, API documentation discovery, and signal enrichment.

**Components:**

1. **Web search** (via OpenRouter/Brave/Perplexity):
   - `web-search` skill: query → structured results with citations
   - Available via `oh-my-pi` extension or `badlogic/pi-skills` (Brave)
   - Perplexity option via `mitsuhiko/agent-stuff`

2. **Page fetcher:**
   - `fetch-page` skill: URL → cleaned markdown (via Jina Reader or Readability)
   - `nicobailon/pi-web-access` covers this with smart fallback chain

3. **Market research agent:**
   - Scheduled: weekly competitive scan for a configured set of topics
   - Output: structured report → Obsidian note → Telegram summary
   - Sources: web search + YouTube + RSS (if configured)

4. **Reddit monitor** (optional):
   - Watch specific subreddits for relevant discussions
   - Useful for: Greg (r/algotrading, r/hyperliquid), Fisch (r/accounting)

**Files to create:**
```
templates/agents/research/SOUL.md
templates/agents/research/IDENTITY.md
templates/agents/research/skills/web-search/SKILL.md
templates/agents/research/skills/fetch-page/SKILL.md
templates/agents/research/skills/market-scan/SKILL.md
references/research-agent.md
```

---

### META-5: Mission Control Dashboard
**Priority:** High | **Effort:** High

A web-based command center for the client to monitor their OpenClaw deployment. Based on concepts from a forthcoming video — **need to fetch the source video first**.

**Pending:** Fetch transcript for the mission control reference video before planning this.

**Known components (from existing frontend work):**
- `gb-automation-landing` already has a customer dashboard at `/dashboard`
- 3-panel layout: Sessions | EventStream | Chat
- WebSocket via `customer-gateway-proxy` (port 3050 → OpenClaw :18789)

**Pages to build:**
- Mission Control (main status dashboard — agents, crons, last activity)
- Agent Cards (per-agent status, last heartbeat, skill list)
- Workflow Catalog (browsable WF-XXX list with status)
- Skill Runner (invoke user-invocable skills from browser)
- Log Viewer (event stream + Obsidian changelog)

**Files to plan (after video fetch):**
```
specs/mission-control-plan.md
```

---

## Keep vs. Exclude Decisions

### KEEP — Core, actively used
| Item | Why |
|------|-----|
| `SKILL.md` | The pipeline brain — well-maintained, comprehensive |
| `references/` (all 11 files) | Active knowledge base, referenced in pipeline |
| `templates/workspace/` (7 .md.tmpl + openclaw.json.tmpl + justfile.tmpl) | Used every session |
| `templates/expert/` (6 files) | Used for domain expert build |
| `templates/agents/youtube/` | Universal YouTube agent — promote to meta |
| `templates/skills/setup-openclaw/` | Ships with every client |
| `templates/skills/domain-discovery/` | First-session bootstrap |
| `client-facing/` (5 files) | Client communication templates |
| `client-sessions/20260221-greg-trading/` | Active client |
| `client-sessions/20260305-michael-fisch/` | Active client |

### REVIEW — May need update or promotion
| Item | Issue | Action |
|------|-------|--------|
| `templates/agents/youtube/` | Tied to Greg's trading context | Generalize + add to universal stack |
| `templates/agentic-coder/` | Good pattern but undocumented | Add to SKILL.md references or document purpose |
| `templates/agent-workspace/` vs `templates/` | Two sets of workspace templates — redundant? | Audit which is canonical |
| `references/pi-extension-selection.md` | Pi extensions evolving fast | Refresh with oh-my-pi, mitsuhiko findings |
| `templates/openclaw-md-viewer-playground.html` | Useful dev tool | Keep but move to `tools/` subfolder |
| `templates/openclaw-wizard-playground.html` | Useful dev tool | Keep but move to `tools/` subfolder |

### EXCLUDE / ARCHIVE
| Item | Reason |
|------|--------|
| `client-sessions/20260305-erica-creations/` | Incomplete — workspace only, no experts or workflow catalog. Either complete or archive. |
| `templates/mac-mini-install.md` | Good but better in `references/` not `templates/` — move it |

---

## Sub-Plans for Linear Agent

The following sub-plans should each become a **Linear issue** in the GBAutomation Marketplace Ecosystem project for the autonomous coding agent to build:

| Linear Issue | Title | Effort | Depends On |
|---|---|---|---|
| LIN-A | Build META-1: Obsidian Sync Skill | M | — |
| LIN-B | Build META-2: GitHub SDLC Skill + conventions | M | — |
| LIN-C | Generalize META-3: YouTube agent to universal template | S | — |
| LIN-D | Build META-4: Web Research / Market Intelligence Skill | M | META-3 |
| LIN-E | Fetch mission control reference video + write META-5 plan | S | — |
| LIN-F | Build META-5: Mission Control Dashboard | L | LIN-E, existing `/dashboard` |
| LIN-G | Complete erica-creations session (experts + workflow catalog) | M | — |
| LIN-H | Add workflow catalog generation to SKILL.md pipeline (Step 4 currently manual) | S | — |
| LIN-I | Refresh pi-extension-selection.md with March 2026 findings | S | — |
| LIN-J | Generate workflow catalog → Linear issues automation | M | LIN-B, LIN-H |

### Prompt Template for Linear Agent

For each sub-plan, use this format when creating the Linear issue:

```
Title: [consulting-intake] {META-N}: {Short Description}

Context:
- Skill location: .claude/skills/consulting-intake/
- Reference: README.md → "META-N" section
- Existing patterns to follow: [list relevant existing files]

Acceptance Criteria:
- [ ] Files created at specified paths
- [ ] SKILL.md frontmatter valid (passes skill-format-spec.md)
- [ ] Integrated into SKILL.md pipeline reference table
- [ ] Tested against one client session (greg-trading or michael-fisch)
- [ ] README.md updated to reflect new skill

Do NOT:
- Modify existing client sessions without a separate issue
- Change openclaw.json.tmpl structure without reviewing all 3 client workspaces
```

---

## Quick Reference: Current Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Agent runtime | OpenClaw + Pi | Pi extensions = OpenClaw extensions |
| LLM (cheap) | GLM-4.7 via Z.AI subscription | $90/quarter, JWT auth |
| LLM (mid brain) | Gemini 2.0 Flash via OpenRouter | Fast, long context |
| LLM (mid coder) | DeepSeek V3 via OpenRouter | Best-in-class coding |
| LLM (pro brain) | Gemini 2.5 Pro via OpenRouter | Near-Claude quality |
| Task management | Linear | GBAutomation Marketplace Ecosystem project |
| Second brain | Obsidian | `C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation` |
| Repo host | GitHub | `github.com/gbauto/` |
| Deploy (cloud) | ZeroClaw CDK (AWS Lightsail) | $3.50/mo nano |
| Deploy (local) | Mac Mini (192.168.4.94) | OpenClaw v2026.3.13 + Z.AI GLM |
| YouTube scraping | yt-dlp | `C:/Users/gblac/AppData/Local/Programs/Python/Python312/Scripts/yt-dlp` |
| Prompt inheritance | Canopy (Jaymin West / Overstory) | Mixin + variable + section-override pattern |
