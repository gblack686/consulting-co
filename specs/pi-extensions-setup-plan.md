# Pi Extensions Setup Plan — Greg Trading Workspace
**Version**: 1.0
**Date**: 2026-03-22
**Status**: READY FOR BUILD
**Target**: Mac Mini (192.168.4.94) — `~/.openclaw/workspace/`
**Repo**: `gblack686/greg-trading-workspace` (private)
**Depends On**: Phase 1 of `greg-trading-official-plan.md` (repo exists, Mac Mini workspace cloned)

---

## What This Plan Does

Installs Pi extensions (Disler core stack + community packages) into the Greg Trading Workspace so Sebastian and all subagents run with: orchestration, safety, cost tracking, scheduling, messaging bridges, and eval supervision — all as in-process Pi extensions rather than external scripts.

---

## File Tree (additions to existing workspace)

```
greg-trading-workspace/
├── extensions/                          ← NEW directory
│   ├── core/                            ← always loaded
│   │   ├── minimal.ts                   # context meter footer
│   │   ├── cross-agent.ts               # loads .claude/ commands
│   │   ├── agent-team.ts                # Sebastian dispatcher → 5 agents
│   │   ├── damage-control.ts            # blocks mainnet trades until approved
│   │   └── tool-counter.ts              # cost per skill run → eval JSON
│   ├── optional/                        ← loaded per-session or per-skill
│   │   ├── agent-chain.ts               # sequential pipelines (signal→validate→execute)
│   │   ├── tilldone.ts                  # task discipline for morning-brief
│   │   ├── purpose-gate.ts              # intent declaration before trade execution
│   │   ├── subagent-widget.ts           # parallel scouts with live progress (interactive only)
│   │   ├── session-replay.ts            # debug failed evals (interactive only)
│   │   ├── system-select.ts             # persona swap per agent role
│   │   ├── tool-counter-widget.ts       # persistent cost badge
│   │   └── pure-focus.ts               # zen mode
│   ├── community/                       ← installed from npm/git
│   │   ├── pi-schedule-prompt/          # cron scheduling inside Pi
│   │   ├── pi-messenger-bridge/         # Discord + Telegram bridge
│   │   ├── pi-supervisor/               # eval threshold enforcement
│   │   ├── notify.ts                    # desktop/Telegram completion alerts
│   │   ├── loop.ts                      # iterative self-improve loop
│   │   ├── review.ts                    # code review for skill PRs
│   │   ├── branch-sessions.ts           # session isolation by git branch
│   │   ├── oracle.ts                    # second opinion from alt model
│   │   └── cost-tracker.ts              # 30-day spending analysis
│   ├── shared/
│   │   └── themeMap.ts                  # theme defaults (dependency)
│   └── theme-cycler.ts                  # Ctrl+X/Q cycle themes
│
├── pi-skills/                           ← NEW — official Pi skills (npm)
│   ├── brave-search/                    # web search for news-scout
│   ├── browser-tools/                   # Chrome DevTools for exchange monitoring
│   ├── youtube-transcript/              # YouTube Scout feed
│   ├── gmcli/                           # Gmail delivery for morning brief
│   └── gdcli/                           # Google Drive for report archival
│
├── .pi/                                 ← NEW — Pi agent definitions
│   ├── agents/
│   │   ├── sebastian.md                 # main orchestrator
│   │   ├── signal-scout.md
│   │   ├── risk-guard.md
│   │   ├── quant.md
│   │   ├── chart-maker.md
│   │   ├── news-scout.md
│   │   └── youtube-scout.md
│   ├── teams.yaml                       # agent team definitions
│   └── agent-chain.yaml                 # sequential pipeline definitions
│
├── damage-control.yaml                  ← NEW — safety rules for damage-control.ts
└── justfile                             ← NEW — Pi launch recipes
```

---

## Phase A — Copy Disler Extensions (Local → Repo)

**Source**: `C:\Users\gblac\OneDrive\Desktop\tac\pi-vs-claude-code\extensions\`
**Target**: `greg-trading-workspace/extensions/`

### Step A1: Copy all 16 extensions + themeMap

```bash
# On Greg's Windows machine (or in GitHub Actions @claude build)
SRC="C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions"
DEST="greg-trading-workspace/extensions"

mkdir -p "$DEST/core" "$DEST/optional" "$DEST/shared"

# Core (always loaded)
cp "$SRC/minimal.ts"        "$DEST/core/"
cp "$SRC/cross-agent.ts"    "$DEST/core/"
cp "$SRC/agent-team.ts"     "$DEST/core/"
cp "$SRC/damage-control.ts" "$DEST/core/"
cp "$SRC/tool-counter.ts"   "$DEST/core/"

# Optional (per-session)
cp "$SRC/agent-chain.ts"         "$DEST/optional/"
cp "$SRC/tilldone.ts"            "$DEST/optional/"
cp "$SRC/purpose-gate.ts"        "$DEST/optional/"
cp "$SRC/subagent-widget.ts"     "$DEST/optional/"
cp "$SRC/session-replay.ts"      "$DEST/optional/"
cp "$SRC/system-select.ts"       "$DEST/optional/"
cp "$SRC/tool-counter-widget.ts" "$DEST/optional/"
cp "$SRC/pure-focus.ts"          "$DEST/optional/"

# Shared dependencies
cp "$SRC/themeMap.ts"       "$DEST/shared/"
cp "$SRC/theme-cycler.ts"   "$DEST/"
cp "$SRC/pi-pi.ts"          "$DEST/core/"
```

### Step A2: Create `damage-control.yaml` (safety rules)

```yaml
# damage-control.yaml — Trade execution safety
# Loaded by damage-control.ts extension
# Blocks tool calls matching these patterns

rules:
  # Block mainnet trade execution unless approval-registry says approved
  - name: block-mainnet-trades
    tool: bash
    pattern: "execute_trade.*--env mainnet"
    action: block
    message: "BLOCKED: Mainnet trade execution requires Greg's approval. Use --env testnet."

  # Block rm on critical directories
  - name: protect-evals
    tool: bash
    pattern: "rm.*evals/"
    action: block
    message: "BLOCKED: Cannot delete eval history."

  - name: protect-memory
    tool: bash
    pattern: "rm -rf.*memory/"
    action: block
    message: "BLOCKED: Cannot bulk-delete memory. Use targeted file removal."

  # Block any curl/wget to Hyperliquid order endpoints (redundant safety)
  - name: block-raw-orders
    tool: bash
    pattern: "(curl|wget).*api.hyperliquid.xyz.*(order|cancel)"
    action: block
    message: "BLOCKED: Use execute_trade.py, not raw API calls."

  # Allow everything else
  - name: default-allow
    tool: "*"
    pattern: ".*"
    action: allow
```

---

## Phase B — Install Community Extensions (on Mac Mini)

Run these on the Mac Mini (192.168.4.94) inside the workspace directory.

### Step B1: Install via `pi install`

```bash
cd ~/.openclaw/workspace

# Scheduling
pi install git:github.com/pi-schedule-prompt
# → installs to extensions/community/pi-schedule-prompt/

# Messenger bridge (Discord + Telegram into Pi sessions)
pi install git:github.com/pi-messenger-bridge
# → installs to extensions/community/pi-messenger-bridge/

# Agent supervisor (eval threshold enforcement)
pi install git:github.com/pi-supervisor
# → installs to extensions/community/pi-supervisor/
```

### Step B2: Copy individual .ts files from mitsuhiko/agent-stuff

```bash
# Clone temporarily
cd /tmp && git clone --depth 1 https://github.com/mitsuhiko/agent-stuff.git

# Copy specific extensions
cp agent-stuff/pi-extensions/notify.ts    ~/.openclaw/workspace/extensions/community/
cp agent-stuff/pi-extensions/loop.ts      ~/.openclaw/workspace/extensions/community/
cp agent-stuff/pi-extensions/review.ts    ~/.openclaw/workspace/extensions/community/

rm -rf /tmp/agent-stuff
```

### Step B3: Copy from hjanuschka/shitty-extensions

```bash
cd /tmp && git clone --depth 1 https://github.com/hjanuschka/shitty-extensions.git

cp shitty-extensions/extensions/branch-sessions.ts  ~/.openclaw/workspace/extensions/community/
cp shitty-extensions/extensions/oracle.ts            ~/.openclaw/workspace/extensions/community/
cp shitty-extensions/extensions/cost-tracker.ts      ~/.openclaw/workspace/extensions/community/

rm -rf /tmp/shitty-extensions
```

---

## Phase C — Install Official Pi Skills

```bash
cd ~/.openclaw/workspace

# Official skills from badlogic/pi-skills
pi install git:github.com/badlogic/pi-skills -s brave-search
pi install git:github.com/badlogic/pi-skills -s browser-tools
pi install git:github.com/badlogic/pi-skills -s youtube-transcript
pi install git:github.com/badlogic/pi-skills -s gmcli
pi install git:github.com/badlogic/pi-skills -s gdcli
```

---

## Phase D — Create `.pi/agents/` Definitions

### D1: `sebastian.md`

```markdown
---
name: sebastian
description: Lead trading orchestrator — dispatches to specialist agents
tools: read,write,edit,bash,grep,find,ls
model: zai/glm-5-turbo
---
You are Sebastian, Greg's lead trading analyst. You coordinate Signal Scout, Risk Guard, Quant, Chart Maker, News Scout, and YouTube Scout.

Dispatch rules:
- Signal/Discord tasks → Signal Scout
- Risk/SL/drawdown tasks → Risk Guard
- Backtest/optimize tasks → Quant
- Chart/visualization tasks → Chart Maker
- News/macro tasks → News Scout
- YouTube content tasks → YouTube Scout

Before dispatching, check memory/signals/ and evals/ for recent context.
After receiving results, synthesize for Greg — lead with the actionable insight.
```

### D2: `signal-scout.md`

```markdown
---
name: signal-scout
description: Scrapes Discord channels and X for trade signals
tools: read,write,bash,grep
model: zai/glm-4.7-flash
---
You are Signal Scout. Monitor configured Discord channels for trade signals.
Parse: ticker, direction, entry, TP, SL, confidence.
Score each signal 0.0-1.0 based on: specificity, risk:reward, source reliability.
Write parsed signals to memory/signals/YYYY-MM-DD.json.
Only alert Sebastian for signals scoring > 0.7.
```

### D3: `risk-guard.md`

```markdown
---
name: risk-guard
description: Monitors positions and portfolio health on Hyperliquid
tools: read,write,bash,grep
model: zai/glm-5-turbo
---
You are Risk Guard. Every 15 minutes:
1. Fetch all open positions from Hyperliquid
2. Verify each has an active stop-loss order
3. Calculate portfolio drawdown vs configured threshold (5%)
4. If any position is unprotected or drawdown exceeds limit → fire Telegram alert
5. Write results to evals/risk-guard-sl-audit/run-{timestamp}.json
Never place orders. Report only.
```

### D4: `quant.md`

```markdown
---
name: quant
description: Runs backtests and strategy optimization
tools: read,write,bash,grep,find
model: zai/glm-5-turbo
---
You are Quant. Run backtests using quantpylib against historical data.
Output: Sharpe ratio, max drawdown, win rate, profit factor, equity curve.
Save results to memory/ and generate charts via Chart Maker.
Use vectorbt patterns when applicable. Always include transaction costs.
```

### D5: `chart-maker.md`

```markdown
---
name: chart-maker
description: Generates trading charts and visualizations
tools: read,write,bash
model: zai/glm-4.7-flash
---
You are Chart Maker. Generate charts using matplotlib/plotly.
Standard outputs: price + indicator overlays, equity curves, drawdown plots.
Save PNGs to memory/charts/. Include title, date range, and data source.
```

### D6: `news-scout.md`

```markdown
---
name: news-scout
description: Scans crypto news and macro headlines
tools: read,write,bash,grep
model: zai/glm-4.7-flash
---
You are News Scout. Daily at Asian open (5pm PT):
1. Search crypto news via brave-search skill
2. Parse Fear & Greed Index
3. Summarize top 7 headlines with sentiment tags
4. Write to memory/news/YYYY-MM-DD.json
```

### D7: `youtube-scout.md`

```markdown
---
name: youtube-scout
description: Monitors trading YouTube channels for new content
tools: read,write,bash,grep
model: zai/glm-4.7-flash
---
You are YouTube Scout. Daily at 10pm PT:
1. Check configured YouTube channels for new videos (last 24h)
2. Fetch transcripts via youtube-transcript skill
3. Extract: tickers mentioned, sentiment, key claims
4. Write summaries to memory/youtube/YYYY-MM-DD.json
```

### D8: `teams.yaml`

```yaml
full:
  - sebastian
  - signal-scout
  - risk-guard
  - quant
  - chart-maker
  - news-scout
  - youtube-scout

morning-brief:
  - sebastian
  - news-scout
  - signal-scout
  - risk-guard

research:
  - signal-scout
  - news-scout
  - youtube-scout
  - quant

risk-check:
  - risk-guard
  - quant
```

### D9: `agent-chain.yaml`

```yaml
signal-to-trade:
  description: "Full signal pipeline: detect → validate → recommend"
  steps:
    - agent: signal-scout
      prompt: "Scan Discord for new signals in the last 15 minutes. Parse and score. $ORIGINAL"
    - agent: quant
      prompt: |
        SIGNALS FOUND: $INPUT
        Run quick backtest on each ticker (7-day lookback). Confirm or reject.
    - agent: risk-guard
      prompt: |
        VALIDATED SIGNALS: $INPUT
        Check current portfolio exposure. Can we take this trade within risk limits?
    - agent: sebastian
      prompt: |
        ORIGINAL REQUEST: $ORIGINAL
        RISK-CHECKED SIGNALS: $INPUT
        Synthesize recommendation for Greg. Include: entry, SL, TP, position size, confidence.

morning-brief-assembly:
  description: "Assemble daily morning brief from all sources"
  steps:
    - agent: news-scout
      prompt: "Fetch today's crypto news and Fear & Greed index."
    - agent: signal-scout
      prompt: "Summarize yesterday's signals and their outcomes."
    - agent: risk-guard
      prompt: "Current portfolio snapshot: positions, SLs, drawdown."
    - agent: sebastian
      prompt: |
        NEWS: $INPUT[0]
        SIGNALS: $INPUT[1]
        PORTFOLIO: $INPUT[2]
        Assemble the morning brief. Deliver to Telegram and #morning-brief.
```

---

## Phase E — Create Justfile

```just
set shell := ["bash", "-cu"]

workspace := `pwd`

# ─── Core Sessions ────────────────────────────────────────────────────────────

# Default: Sebastian with full core stack (headless-safe)
default:
    pi \
      -e extensions/core/minimal.ts \
      -e extensions/core/cross-agent.ts \
      -e extensions/core/agent-team.ts \
      -e extensions/core/damage-control.ts \
      -e extensions/core/tool-counter.ts \
      -e extensions/core/pi-pi.ts \
      -e extensions/theme-cycler.ts

# Headless mode for OpenClaw (no TUI extensions)
headless:
    pi \
      -e extensions/core/cross-agent.ts \
      -e extensions/core/agent-team.ts \
      -e extensions/core/damage-control.ts \
      -e extensions/core/tool-counter.ts

# ─── Specialized Sessions ────────────────────────────────────────────────────

# Signal pipeline: scout → validate → risk-check → recommend
signal-pipeline:
    pi \
      -e extensions/core/agent-team.ts \
      -e extensions/core/damage-control.ts \
      -e extensions/optional/agent-chain.ts \
      -e extensions/core/tool-counter.ts \
      -e extensions/theme-cycler.ts

# Morning brief assembly with task discipline
morning-brief:
    pi \
      -e extensions/core/agent-team.ts \
      -e extensions/optional/tilldone.ts \
      -e extensions/core/tool-counter.ts \
      -e extensions/theme-cycler.ts

# Debug session: full observability
debug:
    pi \
      -e extensions/core/minimal.ts \
      -e extensions/core/agent-team.ts \
      -e extensions/optional/session-replay.ts \
      -e extensions/optional/subagent-widget.ts \
      -e extensions/core/tool-counter.ts \
      -e extensions/theme-cycler.ts

# Self-improve loop (review PR, iterate, re-eval)
self-improve:
    pi \
      -e extensions/core/cross-agent.ts \
      -e extensions/community/loop.ts \
      -e extensions/community/review.ts \
      -e extensions/community/branch-sessions.ts \
      -e extensions/core/tool-counter.ts

# Second opinion on a signal (oracle queries alt model)
oracle-check:
    pi \
      -e extensions/core/minimal.ts \
      -e extensions/community/oracle.ts \
      -e extensions/theme-cycler.ts

# ─── Maintenance ─────────────────────────────────────────────────────────────

# 30-day cost report
cost-report:
    pi -e extensions/community/cost-tracker.ts -e extensions/theme-cycler.ts

# Health check: verify all extensions load
health:
    pi --check-extensions extensions/core/*.ts extensions/optional/*.ts
```

---

## Phase F — Update `openclaw.json`

Add to the existing `openclaw.json` `plugins.entries`:

```jsonc
plugins: {
  entries: {
    "damage-control":      { enabled: true },
    "telegram":            { enabled: true },
    "discord":             { enabled: true },
    // NEW — Pi extensions loaded at gateway start
    "pi-extensions": {
      enabled: true,
      extensions: [
        "extensions/core/cross-agent.ts",
        "extensions/core/agent-team.ts",
        "extensions/core/damage-control.ts",
        "extensions/core/tool-counter.ts",
        "extensions/community/pi-schedule-prompt/index.ts",
        "extensions/community/pi-messenger-bridge/index.ts",
        "extensions/community/pi-supervisor/index.ts",
        "extensions/community/notify.ts",
      ],
    },
  },
},
```

Add to `skills.entries`:

```jsonc
skills: {
  entries: {
    // ... existing skills ...
    // NEW — official Pi skills
    "brave-search":        { enabled: true },
    "browser-tools":       { enabled: true },
    "youtube-transcript":  { enabled: true },
    "gmcli":               { enabled: true },
    "gdcli":               { enabled: true },
  },
},
```

---

## Phase G — Sebastian System Prompt Addition

Add this block to the **end** of `SOUL.md` (or as a new file `EXTENSIONS.md` loaded by AGENTS.md):

```markdown
## Extensions

You run with Pi extensions. They are in-process — you don't call them, they observe and modify your behavior automatically.

Active always:
- **agent-team** — dispatches to Signal Scout, Risk Guard, Quant, Chart Maker, News Scout, YouTube Scout. Use `/team full` to activate all, `/team morning-brief` for brief assembly.
- **damage-control** — blocks mainnet trades, rm on evals/, raw API order calls. If blocked, tell Greg why.
- **tool-counter** — tracks cost per turn. Reference `cost_total` in eval JSON.
- **cross-agent** — loads .claude/ commands. Your existing skills work.
- **pi-supervisor** — if your eval score drops below threshold, it opens a self-improve issue. Respond to these issues with a fix PR.
- **pi-messenger-bridge** — Discord and Telegram messages arrive as Pi events. Reply inline.
- **pi-schedule-prompt** — your cron runs are managed by this extension. Check `config/schedules.json` for timing.

Available on request:
- `/chain signal-to-trade` — runs the full signal pipeline (scout→quant→risk→you).
- `/chain morning-brief-assembly` — assembles brief from all agents.
- `/oracle` — get a second opinion from an alt model on a signal or trade idea.

Pi skills available:
- `brave-search` — web search (use for news-scout tasks)
- `browser-tools` — Chrome DevTools (use for exchange dashboard monitoring)
- `youtube-transcript` — fetch video transcripts (use for youtube-scout tasks)
- `gmcli` / `gdcli` — Gmail and Google Drive (use for report delivery/archival)
```

**That's it.** No other system prompt changes. Sebastian already knows his role from SOUL.md — this just tells him what tools are loaded.

---

## Run-Till-Done Checklist

Sebastian (or Greg via `@claude`) should execute these in order. Each step has a **done-when** gate.

### Round 1: Repo Structure (GitHub Actions or local)

| # | Task | Command | Done When |
|---|------|---------|-----------|
| 1 | Create `extensions/` tree | `mkdir -p extensions/{core,optional,community,shared}` | dirs exist |
| 2 | Copy Disler extensions | Phase A1 commands above | 16 .ts files in place |
| 3 | Create `damage-control.yaml` | Write Phase A2 content | file at repo root |
| 4 | Create `.pi/agents/` | Write D1-D7 agent .md files | 7 agent files |
| 5 | Create `.pi/teams.yaml` | Write D8 content | file exists |
| 6 | Create `.pi/agent-chain.yaml` | Write D9 content | file exists |
| 7 | Create `justfile` | Write Phase E content | file at repo root |
| 8 | Commit + push to main | `git add . && git commit -m "feat: add Pi extensions, agent defs, justfile"` | commit on main |

### Round 2: Mac Mini Install (SSH into 192.168.4.94)

| # | Task | Command | Done When |
|---|------|---------|-----------|
| 9 | Pull latest | `cd ~/.openclaw/workspace && git pull` | extensions/ exists on Mac Mini |
| 10 | Install pi-schedule-prompt | `pi install git:github.com/pi-schedule-prompt` | dir in extensions/community/ |
| 11 | Install pi-messenger-bridge | `pi install git:github.com/pi-messenger-bridge` | dir in extensions/community/ |
| 12 | Install pi-supervisor | `pi install git:github.com/pi-supervisor` | dir in extensions/community/ |
| 13 | Copy mitsuhiko extensions | Phase B2 commands | notify.ts, loop.ts, review.ts present |
| 14 | Copy shitty-extensions | Phase B3 commands | branch-sessions.ts, oracle.ts, cost-tracker.ts present |
| 15 | Install pi-skills | Phase C commands | brave-search/, browser-tools/, etc. present |

### Round 3: Configuration

| # | Task | Command | Done When |
|---|------|---------|-----------|
| 16 | Update openclaw.json plugins | Add Phase F plugin entries | pi-extensions block present |
| 17 | Update openclaw.json skills | Add Phase F skill entries | brave-search etc. listed |
| 18 | Add Extensions block to SOUL.md | Append Phase G content | block at end of SOUL.md |
| 19 | Update AGENTS.md | Add `6. Read extensions/ for loaded capabilities` to session start | line present |

### Round 4: Verify

| # | Task | Command | Done When |
|---|------|---------|-----------|
| 20 | Smoke test: load all core extensions | `just headless` (should start without errors) | Pi starts, no TypeScript errors |
| 21 | Smoke test: agent-team dispatch | Ask Sebastian "check BTC risk" → should dispatch to Risk Guard | Risk Guard responds |
| 22 | Smoke test: damage-control block | Try `bash execute_trade.py --env mainnet` → should be blocked | BLOCKED message appears |
| 23 | Smoke test: agent chain | `/chain signal-to-trade "check latest Discord signals"` | Pipeline completes 4 steps |
| 24 | Smoke test: brave-search skill | Ask News Scout to search for BTC news | Search results returned |
| 25 | Commit config changes | `git add . && git commit -m "feat: configure extensions in openclaw.json + SOUL.md"` | committed |

### Round 5: Final

| # | Task | Done When |
|---|------|-----------|
| 26 | AlphaClaw picks up changes via git sync | Next hourly sync shows new files |
| 27 | Verify claw-roam pulls extensions on merge | Extensions dir present after push |
| 28 | Run `just cost-report` — confirm cost tracking works | 30-day report displayed |
| 29 | Tag release | `git tag v0.2.0-extensions && git push --tags` | Tag visible on GitHub |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Community extensions break on Pi version update | Pin `@mariozechner/pi-coding-agent` version in package.json |
| TUI-dependent extensions crash in headless OpenClaw | Core stack avoids TUI widgets; `headless` justfile recipe omits them |
| `pi install` path differs from expected | Verify install paths; fallback to manual `git clone` + `cp` |
| GLM models struggle with extension-injected system prompts | Extensions inject minimal context; test with `just headless` first |
| damage-control.yaml regex false-positives | Test each pattern against known good commands before deploying |

---

## What NOT To Do

- Do NOT install `oh-my-pi` — it's an all-in-one distribution that conflicts with our selective approach
- Do NOT install `pi-listen` (voice) or `pi-mobile` (Android) — irrelevant for headless trading
- Do NOT load `subagent-widget.ts` or `session-replay.ts` in headless mode — TUI only
- Do NOT modify Disler extension source code — copy and configure via YAML/env vars instead
