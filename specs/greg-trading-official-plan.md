# Greg Trading Workspace — Official Implementation Plan
**Version**: 2.0
**Date**: 2026-03-19
**Status**: APPROVED FOR BUILD
**Repo**: `gblack686/greg-trading-workspace` (private — IS the OpenClaw workspace)
**Auth**: Claude Code OAuth token via `secrets.CLAUDE_ACCESS_TOKEN`
**Runtime**: Mac Mini (192.168.4.94) via AlphaClaw + Docker
**Sync**: AlphaClaw Git Sync (auto-commit) + claw-roam (multi-machine pull)

---

## Overview

A self-improving, eval-scored, Discord-gated multi-agent trading system built on GitHub Actions + Claude Code + OpenClaw. Every skill execution produces a structured eval. First runs require Greg's Discord approval before going autonomous. Skills that score below threshold self-improve via `@claude` issues.

**Key architectural insight**: The OpenClaw workspace IS the GitHub repo. There is no separate deploy pipeline. AlphaClaw handles Git sync automatically. `claw-roam` handles pulling changes to the Mac Mini after GitHub Actions merges new skills.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUILD (GitHub Actions)                        │
│                                                                  │
│  @claude build skill  →  claude-code-action (ubuntu runner)     │
│  Claude writes code   →  worktree branch   →  PR opened         │
│  Greg reviews PR      →  merges to main                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │  push to main
                               ▼
              gblack686/greg-trading-workspace  (private)
              ════════════════════════════════════════════
              This IS the OpenClaw workspace git repo.
              Skills live at workspace/skills/
              AlphaClaw auto-commits changes back hourly.
                               │
                               │  claw-roam pulls on merge
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RUNTIME (Mac Mini)                            │
│                                                                  │
│  ~/.openclaw/workspace  =  cloned greg-trading-workspace repo    │
│                                                                  │
│  AlphaClaw (Docker):                                             │
│    • Watchdog — crash detection + auto-restart                   │
│    • Git Sync — hourly auto-commit of workspace changes          │
│    • Web dashboard — password-protected management UI            │
│    • Discord/Telegram alerts on crash or recovery                │
│                                                                  │
│  claw-roam skill:                                                │
│    • Pulls latest from GitHub after merge                        │
│    • Reloads skills into running OpenClaw instance               │
│                                                                  │
│  OpenClaw v2026.3.13:                                            │
│    • Sebastian, Risk Guard, Quant, Signal Scout, Chart Maker     │
│    • Reads skills from workspace/skills/ (live)                  │
│    • Cron scheduler, WebSocket connections, Telegram/Discord     │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │  eval JSON + outputs
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EVAL + NOTIFY (GitHub Actions)                │
│                                                                  │
│  eval-reporter.yml triggered post-run:                           │
│    • Reads eval JSON from workspace/evals/                       │
│    • Scores via eval-scorer.py                                   │
│    • Routes to Discord channel via discord-notify.py             │
│    • Opens self-improve GitHub issue if score < threshold        │
└─────────────────────────────────────────────────────────────────┘
```

### What runs where

| Task | GitHub Actions (ephemeral) | Mac Mini / OpenClaw (persistent) |
|------|---------------------------|----------------------------------|
| `@claude build skill` | ✅ | — |
| Eval scoring + Discord routing | ✅ | — |
| Self-improve issue creation | ✅ | — |
| Risk Guard SL audit (every 15m) | — | ✅ |
| Apex WebSocket fill monitor | — | ✅ |
| Signal Scout Discord watch | — | ✅ |
| Morning brief assembly + delivery | — | ✅ |
| Nightly backtest (quantpylib) | — | ✅ |
| AlphaClaw Git Sync (hourly commit) | — | ✅ (Docker) |
| claw-roam workspace pull | — | ✅ (on merge) |

### Note on AlphaClaw + Mac Mini
AlphaClaw currently targets Docker/Linux deployments. The Mac Mini runs macOS but supports Docker Desktop and OrbStack. Run AlphaClaw in a Docker container on the Mac Mini — this is the recommended path. If Docker is unavailable, the fallback is a simple `git pull` cron via launchd (macOS native scheduler).

---

## Part 1 — File Path Structure

### 1.1 GitHub Repo = OpenClaw Workspace (`gblack686/greg-trading-workspace` private)

> This repo IS the Mac Mini's OpenClaw workspace. Cloned to `~/.openclaw/workspace/` on the Mac Mini. OpenClaw reads skills directly from `workspace/skills/`. AlphaClaw auto-commits changes back. GitHub Actions writes new skills here via PRs.

```
greg-trading-workspace/               ← cloned to ~/.openclaw/workspace/ on Mac Mini
│
├── .github/
│   ├── workflows/
│   │   ├── claude.yml                    # @claude interactive + manual skill build
│   │   ├── skill-runner.yml              # Cron + manual execution with eval (lightweight only)
│   │   └── eval-reporter.yml             # Post-run Discord routing + self-improve trigger
│   ├── CODEOWNERS                        # Greg = only approver for main
│   └── pull_request_template.md
│
├── alphaclaw/                            # AlphaClaw Docker config (runs on Mac Mini)
│   ├── docker-compose.yml               # AlphaClaw + OpenClaw stack
│   ├── .env.example                     # Env var template (secrets never committed)
│   └── config.json                      # AlphaClaw: git sync schedule, watchdog settings
│
├── config/
│   ├── discord-channels.json             # skill → channel → webhook secret name
│   ├── eval-criteria.json                # per-skill-type criteria weights
│   ├── schedules.json                    # cron registry (source of truth for timing)
│   └── approval-registry.json           # which skills are approved + when + by whom
│
├── evals/
│   ├── _aggregate/
│   │   ├── weekly-2026-03-16.json        # rolled-up weekly scores
│   │   └── weekly-2026-03-23.json
│   ├── risk-guard-sl-audit/
│   │   ├── draft.json                    # created at build time, criteria null
│   │   ├── run-20260318-130012.json      # first run (unapproved)
│   │   └── run-20260318-144532.json      # subsequent run
│   ├── morning-brief/
│   │   └── run-20260318-130001.json
│   ├── apex-trade-executor/
│   │   └── draft.json
│   └── signal-scout/
│       └── run-20260318-150015.json
│
├── scripts/
│   ├── eval-scorer.py                    # compute weighted eval_score from criteria
│   ├── discord-notify.py                 # post embed to Discord channel via webhook
│   ├── approval-gate.py                  # first-run check, post approval card, block if rejected
│   └── self-improve.py                   # open GitHub issue for low-scoring skills
│
├── skills/                               ← OpenClaw reads this directly (highest precedence)
│   ├── _infra/
│   │   └── claw-roam/                   # Installed from ClawHub — syncs workspace on merge
│   │       └── SKILL.md                 # clawhub install claw-roam
│   ├── execution/
│   │   └── apex-trade-executor/
│   │       ├── SKILL.md
│   │       └── scripts/
│   │           └── execute_trade.py
│   ├── risk/
│   │   ├── risk-guard-sl-audit/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       └── sl_audit.py
│   │   └── manage-risk/
│   │       └── SKILL.md
│   ├── intelligence/
│   │   ├── signal-scout/
│   │   │   └── SKILL.md
│   │   ├── news-scout/
│   │   │   └── SKILL.md
│   │   └── youtube-scout/
│   │       └── SKILL.md
│   ├── analytics/
│   │   ├── quant-backtest/
│   │   │   └── SKILL.md
│   │   └── chart-maker/
│   │       └── SKILL.md
│   └── operations/
│       ├── morning-brief/
│       │   └── SKILL.md
│       ├── paper-trader/
│       │   └── SKILL.md
│       └── health-check/
│           └── SKILL.md
│
├── memory/
│   ├── signals/                          # parsed signals from Signal Scout
│   ├── fills/                            # confirmed fills from Apex
│   ├── slippage-log.json
│   └── execution-plans/                  # active/closed Apex plans
│
├── CLAUDE.md                             # repo-level Claude Code conventions
└── README.md
```

---

### 1.2 Local Mirror (`consulting-co/.claude/skills/consulting-intake/client-sessions/20260221-greg-trading/`)

```
20260221-greg-trading/
│
├── workspace/                            # OpenClaw deployment copy
│   ├── openclaw.json                     # agent registry
│   ├── AGENTS.md
│   ├── IDENTITY.md
│   ├── SOUL.md
│   ├── MEMORY.md
│   ├── TOOLS.md
│   ├── USER.md
│   ├── HEARTBEAT.md
│   ├── cron-setup.sh
│   └── skills/                           # mirrors github repo skills/
│       ├── execution/
│       ├── risk/
│       ├── intelligence/
│       ├── analytics/
│       └── operations/
│
├── experts/
│   └── trade-executor/
│       ├── _index.md
│       ├── expertise.md
│       ├── question.md
│       ├── plan.md
│       ├── plan_build_improve.md
│       ├── self-improve.md
│       └── execute-trade-session.md
│
└── specs/
    ├── github-actions-ci-eval-plan.md    # previous spec (reference)
    └── greg-trading-official-plan.md     # THIS FILE
```

---

### 1.3 Obsidian Vault (`obsidian/Gbautomation/crypto/hyperliquid/`)

```
hyperliquid/
├── agent-configuration.md               # master hierarchy + schedule + SDK annotation
├── workflows/
│   ├── WF-001-morning-brief.md
│   ├── WF-002-discord-signal.md
│   └── ... (WF-003 through WF-018)
└── evals/
    └── dashboard.md                      # Obsidian Dataview of latest eval scores
```

---

## Part 2 — Config Files

### `config/discord-channels.json`

```json
{
  "channels": {
    "execution-approvals": {
      "webhook_secret": "DISCORD_WEBHOOK_EXECUTION",
      "description": "Apex trade execution reports + first-run approval gate",
      "skills": ["apex-trade-executor", "paper-trader"],
      "color": 15158332
    },
    "risk-alerts": {
      "webhook_secret": "DISCORD_WEBHOOK_RISK",
      "description": "Risk Guard SL audit failures, drawdown, funding alerts",
      "skills": ["risk-guard-sl-audit", "manage-risk"],
      "color": 15548997
    },
    "morning-brief": {
      "webhook_secret": "DISCORD_WEBHOOK_MORNING_BRIEF",
      "description": "Daily morning brief from Sebastian",
      "skills": ["morning-brief"],
      "color": 3447003
    },
    "signal-feed": {
      "webhook_secret": "DISCORD_WEBHOOK_SIGNAL_FEED",
      "description": "Signal Scout outputs and parsed Discord signals",
      "skills": ["signal-scout"],
      "color": 10181046
    },
    "analytics": {
      "webhook_secret": "DISCORD_WEBHOOK_ANALYTICS",
      "description": "Quant backtest results and Chart Maker outputs",
      "skills": ["quant-backtest", "chart-maker"],
      "color": 1752220
    },
    "news-feed": {
      "webhook_secret": "DISCORD_WEBHOOK_NEWS_FEED",
      "description": "News Scout summaries and Fear and Greed updates",
      "skills": ["news-scout", "youtube-scout"],
      "color": 16776960
    },
    "build-log": {
      "webhook_secret": "DISCORD_WEBHOOK_BUILD_LOG",
      "description": "Skill build results, self-improve completions, PR links",
      "skills": ["_build", "_self-improve"],
      "color": 9807270
    },
    "approval-queue": {
      "webhook_secret": "DISCORD_WEBHOOK_APPROVAL_QUEUE",
      "description": "ALL first-run skills awaiting Greg approval",
      "skills": ["_first-run"],
      "color": 16745728
    }
  }
}
```

---

### `config/eval-criteria.json`

```json
{
  "skill_types": {
    "execution": {
      "description": "Skills that place orders on Hyperliquid",
      "pass_threshold": 0.95,
      "criteria": {
        "sl_placed_within_5s":    { "weight": 0.30, "description": "SL order placed within 5s of fill" },
        "slippage_within_threshold": { "weight": 0.20, "description": "Slippage <= configured max_bps" },
        "plan_saved_to_supabase": { "weight": 0.20, "description": "Execution plan persisted to DB" },
        "fill_detected_via_ws":   { "weight": 0.15, "description": "Fill detected via WebSocket not polling" },
        "telegram_alert_sent":    { "weight": 0.10, "description": "Greg notified within 10s of fill" },
        "reduce_only_on_sl":      { "weight": 0.05, "description": "All SL orders have reduce_only=true" }
      }
    },
    "risk": {
      "description": "Skills that monitor positions and portfolio health",
      "pass_threshold": 0.90,
      "criteria": {
        "all_positions_have_sl":  { "weight": 0.40, "description": "Zero positions found without active SL" },
        "drawdown_within_limits": { "weight": 0.25, "description": "Portfolio drawdown < configured threshold" },
        "alerts_fired_correctly": { "weight": 0.20, "description": "Correct alert channels notified on threshold breach" },
        "no_false_positives":     { "weight": 0.15, "description": "No alerts fired when thresholds not breached" }
      }
    },
    "intelligence": {
      "description": "Skills that gather and parse signals",
      "pass_threshold": 0.85,
      "criteria": {
        "signals_parsed":         { "weight": 0.35, "description": "At least one signal successfully parsed" },
        "score_above_threshold":  { "weight": 0.30, "description": "Signal quality score > 0.7" },
        "output_saved_to_memory": { "weight": 0.20, "description": "Results written to memory/" },
        "telegram_delivered":     { "weight": 0.15, "description": "High-quality signals delivered to Telegram" }
      }
    },
    "analytics": {
      "description": "Skills that run backtests or generate charts",
      "pass_threshold": 0.85,
      "criteria": {
        "output_generated":       { "weight": 0.40, "description": "Chart or backtest report produced" },
        "data_complete":          { "weight": 0.30, "description": "Full requested time range covered" },
        "no_data_errors":         { "weight": 0.20, "description": "No NaN / missing data in output" },
        "saved_to_memory":        { "weight": 0.10, "description": "Output saved to memory/ dir" }
      }
    },
    "operations": {
      "description": "Skills that assemble and deliver reports",
      "pass_threshold": 0.85,
      "criteria": {
        "report_assembled":       { "weight": 0.35, "description": "All report sections populated" },
        "delivered_on_schedule":  { "weight": 0.30, "description": "Delivered within 5 min of scheduled time" },
        "telegram_delivered":     { "weight": 0.25, "description": "Successfully sent to Telegram" },
        "no_empty_sections":      { "weight": 0.10, "description": "No placeholder text in output" }
      }
    },
    "build": {
      "description": "Skills that build or improve other skills",
      "pass_threshold": 0.90,
      "criteria": {
        "no_hardcoded_secrets":   { "weight": 0.30, "description": "Zero hardcoded keys or wallet addresses" },
        "approval_gate_present":  { "weight": 0.25, "description": "[APPROVAL GATE] present on order-placing steps" },
        "required_sections":      { "weight": 0.20, "description": "SKILL.md has all required frontmatter sections" },
        "testnet_validated":      { "weight": 0.15, "description": "Testnet run completed before mainnet flag" },
        "eval_draft_created":     { "weight": 0.10, "description": "evals/skill-name/draft.json created" }
      }
    }
  }
}
```

---

### `config/schedules.json`

```json
{
  "schedules": [
    {
      "cron": "*/15 * * * *",
      "skill": "risk-guard-sl-audit",
      "label": "Every 15 min",
      "pt_label": "Continuous",
      "agents": ["Risk Guard"]
    },
    {
      "cron": "*/15 * * * *",
      "skill": "signal-scout",
      "label": "Every 15 min",
      "pt_label": "Continuous",
      "agents": ["Signal Scout"]
    },
    {
      "cron": "0 0 * * *",
      "skill": "news-scout",
      "label": "Daily 00:00 UTC",
      "pt_label": "5:00 PM PT (Asian open)",
      "agents": ["News Scout"]
    },
    {
      "cron": "0 4 * * *",
      "skill": "quant-backtest",
      "label": "Daily 04:00 UTC",
      "pt_label": "9:00 PM PT",
      "agents": ["Quant"]
    },
    {
      "cron": "0 5 * * *",
      "skill": "youtube-scout",
      "label": "Daily 05:00 UTC",
      "pt_label": "10:00 PM PT",
      "agents": ["YouTube Scout"]
    },
    {
      "cron": "0 10 * * 1-5",
      "skill": "morning-brief",
      "label": "Weekdays 10:00 UTC (assembly)",
      "pt_label": "3:00 AM PT",
      "agents": ["Sebastian"]
    },
    {
      "cron": "0 13 * * 1-5",
      "skill": "morning-brief",
      "label": "Weekdays 13:00 UTC (delivery)",
      "pt_label": "6:00 AM PT",
      "agents": ["Sebastian"]
    },
    {
      "cron": "0 3 * * 0",
      "skill": "quant-backtest",
      "label": "Sunday 03:00 UTC (weekly)",
      "pt_label": "Sunday 8:00 PM PT",
      "agents": ["Quant"]
    }
  ]
}
```

---

## Part 3 — Eval JSON Schema

Every skill run writes to `evals/{skill-name}/run-{YYYYMMDD-HHmmss}.json`.

```typescript
interface EvalReport {
  // Identity
  run_id:       string;           // "run-20260318-130012"
  skill:        string;           // "risk-guard-sl-audit"
  skill_type:   SkillType;        // "risk" | "execution" | "intelligence" | ...
  agent:        string;           // "Risk Guard"
  workflow:     string | null;    // "WF-003" if mapped
  github_run:   string;           // GitHub Actions run URL

  // Timing
  triggered_at: string;           // ISO 8601 UTC
  trigger_type: "cron" | "manual" | "event";
  duration_ms:  number;

  // Approval state
  first_run:    boolean;          // true if no prior approved run exists
  approved:     boolean | null;   // null = pending, true = approved, false = rejected
  approved_by:  string | null;    // "greg" or null
  approved_at:  string | null;    // ISO 8601 UTC

  // Inputs / Outputs
  inputs:       Record<string, unknown>;
  outputs:      Record<string, unknown>;

  // Eval
  criteria:     Record<string, CriterionResult>;
  eval_score:   number;           // 0.0 - 1.0 weighted average
  passed:       boolean;          // eval_score >= skill_type threshold
  notes:        string[];         // any warnings or edge cases

  // Self-improve
  improvement_issue: string | null;   // GitHub issue URL if opened
  improvement_pr:    string | null;   // GitHub PR URL if merged
}

interface CriterionResult {
  score:       number | null;   // 0.0, 0.5, or 1.0 (null = not evaluated)
  passed:      boolean | null;
  actual:      unknown;         // observed value
  expected:    unknown;         // target value
  note:        string | null;
}

type SkillType = "execution" | "risk" | "intelligence" | "analytics" | "operations" | "build";
```

---

## Part 4 — Full Dry Run Examples

### Dry Run A: First-Ever Run of `risk-guard-sl-audit`

**Scenario**: Risk Guard's SL audit runs for the first time at 00:00 UTC (5pm PT) via cron. No prior eval exists. One position has a missing SL.

---

#### Step 1 — GitHub Actions triggers `skill-runner.yml`

```
Trigger:    cron "*/15 * * * *"  →  03-18-2026 13:00 UTC
Job:        skill-runner
Runner:     ubuntu-latest
Skill:      risk-guard-sl-audit (resolved from schedule mapping)
```

---

#### Step 2 — `approval-gate.py` checks `evals/risk-guard-sl-audit/`

```
$ python scripts/approval-gate.py --skill risk-guard-sl-audit

[approval-gate] Checking evals/risk-guard-sl-audit/ ...
[approval-gate] No approved runs found.
[approval-gate] first_run = TRUE
[approval-gate] Posting approval card to #approval-queue ...
[approval-gate] Discord response: 204 No Content
[approval-gate] Blocking execution. Awaiting Greg approval.
[approval-gate] EXIT 2  (first-run-blocked)
```

---

#### Step 3 — Discord message sent to `#approval-queue`

```
╔══════════════════════════════════════════════════════════╗
║  🟡 FIRST RUN — APPROVAL REQUIRED                       ║
╠══════════════════════════════════════════════════════════╣
║  Skill:    risk-guard-sl-audit                          ║
║  Agent:    Risk Guard                                   ║
║  Type:     risk                                         ║
║  Trigger:  cron */15 * * * *  (03-18-2026 13:00 UTC)   ║
║  Repo:     gblack686/greg-trading-workspace             ║
╠══════════════════════════════════════════════════════════╣
║  DESCRIPTION                                            ║
║  Audits all open positions on Hyperliquid and verifies  ║
║  each has an active stop-loss order. Fires Telegram     ║
║  alert if any position is unprotected.                  ║
╠══════════════════════════════════════════════════════════╣
║  PASS THRESHOLD                                         ║
║  ≥ 0.90 to auto-approve future runs                     ║
╠══════════════════════════════════════════════════════════╣
║  EVAL CRITERIA                                          ║
║  • all_positions_have_sl  (40% weight)                  ║
║  • drawdown_within_limits (25% weight)                  ║
║  • alerts_fired_correctly (20% weight)                  ║
║  • no_false_positives     (15% weight)                  ║
╠══════════════════════════════════════════════════════════╣
║  ACTIONS                                                ║
║  [✅ Approve — Run Now]  [❌ Reject]  [⚠️ Modify First]  ║
╚══════════════════════════════════════════════════════════╝
```

---

#### Step 4 — Greg taps ✅ on mobile

```
Event:      interaction  type=button  custom_id=approve:risk-guard-sl-audit:run-20260318-130012
Handler:    approval-gate webhook listener
Action:     Set approved=true in config/approval-registry.json
            Trigger workflow_dispatch: skill-runner.yml  skill=risk-guard-sl-audit
```

`config/approval-registry.json` updated:
```json
{
  "risk-guard-sl-audit": {
    "approved": true,
    "approved_by": "greg",
    "approved_at": "2026-03-18T13:04:22Z",
    "first_approved_run": "run-20260318-130012"
  }
}
```

---

#### Step 5 — Skill actually runs

```
$ python skills/risk/risk-guard-sl-audit/scripts/sl_audit.py

[sl-audit] Fetching positions from Hyperliquid...
[sl-audit] Found 2 open positions:
  BTC-PERP  long  0.11 BTC  entry 84,200  unrealized +$312
  ETH-PERP  long  1.20 ETH  entry 3,940   unrealized -$48

[sl-audit] Checking open orders for SL coverage...
  BTC-PERP → SL found: order #7821  trigger 82,000  sz 0.11  ✅
  ETH-PERP → SL found: NONE ❌

[sl-audit] CRITICAL: ETH-PERP has no stop-loss!
[sl-audit] Firing Telegram alert...
[sl-audit] Telegram delivered: message_id 4921
[sl-audit] Portfolio drawdown: 0.8% (limit: 5.0%) ✅
[sl-audit] Run complete. Duration: 3,241 ms
```

---

#### Step 6 — `eval-scorer.py` grades the run

```
$ python scripts/eval-scorer.py \
    --skill risk-guard-sl-audit \
    --run-id run-20260318-130012

Criteria results:
  all_positions_have_sl:    0.0  (FAIL — ETH-PERP unprotected)  weight 0.40
  drawdown_within_limits:   1.0  (PASS — 0.8% < 5.0%)           weight 0.25
  alerts_fired_correctly:   1.0  (PASS — Telegram sent)          weight 0.20
  no_false_positives:       1.0  (PASS — alert was real)         weight 0.15

Weighted score:
  (0.0 × 0.40) + (1.0 × 0.25) + (1.0 × 0.20) + (1.0 × 0.15)
  = 0.00 + 0.25 + 0.20 + 0.15
  = 0.60

Pass threshold: 0.90
Result: FAIL  (0.60 < 0.90)
```

---

#### Step 7 — Eval JSON written to disk

**`evals/risk-guard-sl-audit/run-20260318-130012.json`**

```json
{
  "run_id": "run-20260318-130012",
  "skill": "risk-guard-sl-audit",
  "skill_type": "risk",
  "agent": "Risk Guard",
  "workflow": "WF-003",
  "github_run": "https://github.com/gblack686/greg-trading-workspace/actions/runs/14821093",
  "triggered_at": "2026-03-18T13:00:12Z",
  "trigger_type": "cron",
  "duration_ms": 3241,
  "first_run": true,
  "approved": true,
  "approved_by": "greg",
  "approved_at": "2026-03-18T13:04:22Z",
  "inputs": {
    "wallet": "0x...redacted",
    "env": "mainnet"
  },
  "outputs": {
    "positions_checked": 2,
    "positions_with_sl": 1,
    "positions_missing_sl": ["ETH-PERP"],
    "portfolio_drawdown_pct": 0.8,
    "telegram_message_id": 4921,
    "alert_fired": true
  },
  "criteria": {
    "all_positions_have_sl": {
      "score": 0.0,
      "passed": false,
      "actual": "ETH-PERP missing SL",
      "expected": "all positions have active SL",
      "note": "ETH-PERP long 1.20 ETH has no stop-loss order on exchange"
    },
    "drawdown_within_limits": {
      "score": 1.0,
      "passed": true,
      "actual": 0.008,
      "expected": "< 0.05",
      "note": null
    },
    "alerts_fired_correctly": {
      "score": 1.0,
      "passed": true,
      "actual": "Telegram message_id 4921 delivered",
      "expected": "alert on unprotected position",
      "note": null
    },
    "no_false_positives": {
      "score": 1.0,
      "passed": true,
      "actual": "alert matched real missing SL",
      "expected": "alerts match actual state",
      "note": null
    }
  },
  "eval_score": 0.60,
  "passed": false,
  "notes": [
    "ETH-PERP is missing a stop-loss — this is a real risk event, not a skill failure.",
    "Skill correctly detected and reported the gap. Score penalized because the invariant failed."
  ],
  "improvement_issue": "https://github.com/gblack686/greg-trading-workspace/issues/14",
  "improvement_pr": null
}
```

---

#### Step 8 — `eval-reporter.yml` routes to Discord

Two messages fire:

**To `#risk-alerts`:**
```
╔═══════════════════════════════════════════════════════════╗
║  🔴 RISK ALERT — ETH-PERP HAS NO STOP-LOSS              ║
╠═══════════════════════════════════════════════════════════╣
║  Skill:    risk-guard-sl-audit                           ║
║  Run:      run-20260318-130012                           ║
║  Time:     13:00:12 UTC  (6:00 AM PT)                   ║
╠═══════════════════════════════════════════════════════════╣
║  POSITIONS CHECKED:  2                                   ║
║  ✅ BTC-PERP   SL @ 82,000   covers 0.11 BTC            ║
║  ❌ ETH-PERP   NO STOP-LOSS  1.20 ETH exposed           ║
╠═══════════════════════════════════════════════════════════╣
║  DRAWDOWN:     0.8%  ✅  (limit 5.0%)                   ║
║  EVAL SCORE:   0.60 / 1.0  ❌  (threshold 0.90)         ║
╠═══════════════════════════════════════════════════════════╣
║  [📋 View Full Eval]  [🔧 Fix ETH-PERP SL]              ║
╚═══════════════════════════════════════════════════════════╝
```

**To `#build-log` (self-improve triggered):**
```
╔═══════════════════════════════════════════════════════════╗
║  ⚙️ SELF-IMPROVE TRIGGERED                               ║
╠═══════════════════════════════════════════════════════════╣
║  Skill:    risk-guard-sl-audit                           ║
║  Score:    0.60  (below 0.90 threshold)                  ║
║  Issue:    github.com/.../issues/14                      ║
║  @claude will review and improve this skill.             ║
╚═══════════════════════════════════════════════════════════╝
```

---

#### Step 9 — `self-improve.py` opens GitHub Issue #14

**Issue Title**: `[self-improve] risk-guard-sl-audit scored 0.60 (below 0.90 threshold)`

**Issue Body**:
```markdown
## Skill Eval Below Threshold

**Skill**: `risk-guard-sl-audit`
**Run**: `run-20260318-130012`
**Score**: 0.60 / 1.0
**Threshold**: 0.90

### Failing Criterion

**`all_positions_have_sl`** — score 0.0 (weight 40%)

Observed: ETH-PERP long 1.20 ETH has no stop-loss order on exchange
Expected: All positions have an active SL order

### Context

The skill correctly *detected* the missing SL and *alerted* Greg. The
invariant failure is real — ETH-PERP was unprotected. The skill itself
behaved correctly but the position state failed the criterion.

**Possible improvements**:
1. Separate "detection & alert" score from "invariant health" score
2. Add a skill action: auto-place emergency SL when gap detected (if Greg unlocks)
3. Update eval notes to distinguish "skill failed" vs "invariant breach"

@claude Please review `skills/risk/risk-guard-sl-audit/SKILL.md` and
`config/eval-criteria.json` and propose improvements. Open a PR.

/cc Greg
```

---

### Dry Run B: Passing Run (no issues, already approved)

**Scenario**: Risk Guard runs again at 13:15 UTC. ETH-PERP SL has been manually placed by Greg. Both positions protected.

---

#### Execution output

```
[sl-audit] Found 2 open positions:
  BTC-PERP  long  0.11 BTC  ✅  SL @ 82,000
  ETH-PERP  long  1.20 ETH  ✅  SL @ 3,800

[sl-audit] All positions protected.
[sl-audit] Portfolio drawdown: 0.8% ✅
[sl-audit] No alerts needed.
[sl-audit] Duration: 2,188 ms
```

#### Eval result

```json
{
  "run_id": "run-20260318-131512",
  "eval_score": 1.0,
  "passed": true,
  "criteria": {
    "all_positions_have_sl":    { "score": 1.0, "passed": true },
    "drawdown_within_limits":   { "score": 1.0, "passed": true },
    "alerts_fired_correctly":   { "score": 1.0, "passed": true, "note": "no alert needed, none fired" },
    "no_false_positives":       { "score": 1.0, "passed": true }
  },
  "improvement_issue": null
}
```

#### Discord — `#risk-alerts` (silent pass, compact)

```
✅  risk-guard-sl-audit  |  13:15 UTC (6:15 AM PT)
    2 positions  |  2/2 protected  |  drawdown 0.8%  |  score 1.0
```

*(No `#build-log` message — skill passed, self-improve not triggered)*

---

### Dry Run C: `morning-brief` first run

**Scenario**: Sebastian assembles the morning brief for the first time. Brief contains 3 sections: news summary, signals from yesterday, portfolio snapshot.

---

#### Execution output

```
[morning-brief] Assembling brief for 2026-03-18...
[morning-brief] Section 1: News Scout cache → 7 headlines loaded
[morning-brief] Section 2: Signal Scout memory/signals/2026-03-17.json → 3 signals
[morning-brief] Section 3: Hyperliquid positions → BTC-PERP, ETH-PERP
[morning-brief] Fear & Greed: 62 (Greed)
[morning-brief] Brief assembled. 847 characters.
[morning-brief] Delivering to Telegram...
[morning-brief] Telegram delivered: message_id 5102
[morning-brief] Duration: 8,441 ms
```

#### Discord — `#approval-queue` (first run gate)

```
╔═══════════════════════════════════════════════════════════╗
║  🟡 FIRST RUN — APPROVAL REQUIRED                        ║
╠═══════════════════════════════════════════════════════════╣
║  Skill:    morning-brief                                 ║
║  Agent:    Sebastian                                     ║
║  Schedule: Weekdays 6:00 AM PT (13:00 UTC)              ║
╠═══════════════════════════════════════════════════════════╣
║  PREVIEW — today's brief:                               ║
║                                                          ║
║  📰 MARKET: BTC -1.2% · ETH +0.8% · F&G 62 (Greed)    ║
║                                                          ║
║  📡 SIGNALS (yesterday):                                ║
║    • BTC long 84,500 → TP 87,000  SL 82,500  (score 0.91) ║
║    • SOL long 145.2  → TP 158     SL 140     (score 0.85) ║
║    • ETH long 3,960  → (pending)             (score 0.73) ║
║                                                          ║
║  🛡️ POSITIONS: BTC ✅  ETH ✅  Drawdown 0.8%           ║
╠═══════════════════════════════════════════════════════════╣
║  [✅ Approve — Run Daily]  [❌ Reject]  [⚠️ Modify]      ║
╚═══════════════════════════════════════════════════════════╝
```

After Greg taps ✅, `morning-brief` runs autonomously every weekday at 6am PT and posts to `#morning-brief`:

```
╔═══════════════════════════════════════════════════════════╗
║  ☀️ MORNING BRIEF — Wed Mar 18 2026  6:00 AM PT          ║
╠═══════════════════════════════════════════════════════════╣
║  MARKET  BTC 84,412 (-1.2%)  ETH 3,951 (+0.8%)          ║
║  F&G Index: 62 — Greed                                   ║
╠═══════════════════════════════════════════════════════════╣
║  TOP SIGNALS (last 24h)                                  ║
║  1. BTC long @ 84,500  TP 87,000  SL 82,500  ★★★★★      ║
║  2. SOL long @ 145.2   TP 158     SL 140     ★★★★☆      ║
╠═══════════════════════════════════════════════════════════╣
║  YOUR POSITIONS                                          ║
║  BTC-PERP  +0.11 BTC  entry 84,200  P&L +$23  SL ✅     ║
║  ETH-PERP  +1.20 ETH  entry 3,940   P&L -$11  SL ✅     ║
╠═══════════════════════════════════════════════════════════╣
║  eval: 0.96 ✅  |  run-20260318-130001                   ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Part 5 — Build Phases

### Phase 1 — Repo + Mac Mini Foundation (Day 1)
**Goal**: Repo exists, Mac Mini workspace cloned, AlphaClaw running, `@claude` responds.

| Task | Where | Done when |
|------|-------|-----------|
| Create private repo `gblack686/greg-trading-workspace` | GitHub | Repo visible, private |
| Add `CLAUDE.md`, `config/` skeleton, `AGENTS.md`, `SOUL.md` | GitHub | Files committed to main |
| Add `claude.yml` workflow | GitHub | `@claude hello` responds in issue |
| Store OAuth token as GitHub secret | GitHub | `gh secret list` shows `CLAUDE_ACCESS_TOKEN` |
| Clone repo to Mac Mini as OpenClaw workspace | Mac Mini | `~/.openclaw/workspace/` is the repo |
| Point OpenClaw at cloned path | Mac Mini | `openclaw.json` `agents.defaults.workspace` updated |
| Run `openclaw setup --workspace ~/.openclaw/workspace` | Mac Mini | Seeds any missing workspace files |
| Install AlphaClaw via Docker on Mac Mini | Mac Mini | AlphaClaw dashboard reachable at `192.168.4.94:PORT` |
| Configure AlphaClaw git sync → `gblack686/greg-trading-workspace` | AlphaClaw UI | Hourly commits visible on GitHub |
| Install `claw-roam` from ClawHub | Mac Mini | `clawhub install claw-roam` succeeds |
| Store all secrets (Hyperliquid, Supabase, Telegram, Discord) | GitHub Secrets + AlphaClaw | `gh secret list` complete |

---

### Phase 2 — Eval Infrastructure (Day 1–2)
**Goal**: Eval JSON gets written on every run.

| Task | File | Done when |
|------|------|-----------|
| `eval-scorer.py` | `scripts/eval-scorer.py` | Produces valid JSON from mock inputs |
| `discord-notify.py` | `scripts/discord-notify.py` | Test message appears in Discord |
| `approval-gate.py` | `scripts/approval-gate.py` | Blocks first run, posts approval card |
| `self-improve.py` | `scripts/self-improve.py` | Opens GitHub issue with correct body |
| `evals/` directory + draft schema | `evals/.gitkeep` | Merged to main |

---

### Phase 3 — First Skill: `risk-guard-sl-audit` (Day 2–3)
**Goal**: Full dry run A above executes end-to-end.

| Task | File | Done when |
|------|------|-----------|
| Build skill | `skills/risk/risk-guard-sl-audit/` | SKILL.md + script present |
| Add to `skill-runner.yml` cron | `.github/workflows/skill-runner.yml` | Cron entry at `*/15 * * * *` |
| First run → approval card → Greg approves | Discord `#approval-queue` | `approval-registry.json` updated |
| Passing run → compact Discord message | Discord `#risk-alerts` | ✅ message appears |
| Eval JSON on disk | `evals/risk-guard-sl-audit/` | File exists with score |

---

### Phase 4 — Morning Brief + Signal Scout (Day 3–4)
**Goal**: Greg gets first morning brief via Telegram AND Discord preview.

| Task | File | Done when |
|------|------|-----------|
| Build `morning-brief` skill | `skills/operations/morning-brief/` | SKILL.md present |
| Build `signal-scout` skill | `skills/intelligence/signal-scout/` | SKILL.md present |
| Add both to `skill-runner.yml` | — | Cron entries present |
| Morning brief approval → runs daily | Discord `#approval-queue` | Greg approves |
| Brief delivered to Telegram + `#morning-brief` | Both channels | Message appears |

---

### Phase 5 — Self-Improve Loop + Remaining Skills (Week 2)
**Goal**: All 9 skills deployed. Self-improve loop closes an issue end-to-end.

| Task | Done when |
|------|-----------|
| All 9 skills have SKILL.md + evals | `evals/*/draft.json` present for each |
| `eval-reporter.yml` routes all channels correctly | Each skill posts to mapped channel |
| Self-improve: `@claude` responds to issue, opens PR | PR visible on GitHub |
| Greg reviews + merges PR → re-run passes | Score improves above threshold |
| `_aggregate/` weekly rollup runs Sunday | JSON file committed |

---

## Part 6 — GitHub Secrets Required

```bash
# Claude Code OAuth token
gh secret set CLAUDE_ACCESS_TOKEN \
  --repo gblack686/greg-trading-workspace

# Discord webhook URLs (one per channel)
gh secret set DISCORD_WEBHOOK_EXECUTION      --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_RISK           --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_MORNING_BRIEF  --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_SIGNAL_FEED    --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_ANALYTICS      --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_NEWS_FEED      --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_BUILD_LOG      --repo gblack686/greg-trading-workspace
gh secret set DISCORD_WEBHOOK_APPROVAL_QUEUE --repo gblack686/greg-trading-workspace

# Hyperliquid (for skills that call the exchange)
gh secret set HYPERLIQUID_PRIVATE_KEY        --repo gblack686/greg-trading-workspace
gh secret set HYPERLIQUID_WALLET_ADDRESS     --repo gblack686/greg-trading-workspace

# Supabase
gh secret set SUPABASE_URL                   --repo gblack686/greg-trading-workspace
gh secret set SUPABASE_KEY                   --repo gblack686/greg-trading-workspace

# Telegram
gh secret set TELEGRAM_BOT_TOKEN             --repo gblack686/greg-trading-workspace
gh secret set TELEGRAM_CHAT_ID               --repo gblack686/greg-trading-workspace
```

---

## Part 7 — CLAUDE.md for the Repo

```markdown
# Greg Trading Workspace — Claude Code Rules

## Project
Multi-agent Hyperliquid trading system. Sebastian is supervisor.
Apex executes trades. All other agents are read-only or alert-only.

## Hard Rules
1. NEVER hardcode private keys, wallet addresses, or API keys.
   Always use os.environ["SECRET_NAME"].
2. ALWAYS include [APPROVAL GATE] comment before any order-placing code.
3. ALWAYS use reduce_only=True on SL and TP orders.
4. ALWAYS start on testnet (HYPERLIQUID_ENV=testnet) before mainnet.
5. NEVER create self-improving issues that trigger more self-improving
   issues. Max 1 improvement cycle per skill per day.

## File Layout
- Skills:  skills/{type}/{skill-name}/SKILL.md
- Evals:   evals/{skill-name}/run-{YYYYMMDD-HHmmss}.json
- Scripts: scripts/ (eval-scorer, discord-notify, approval-gate, self-improve)
- Config:  config/ (discord-channels.json, eval-criteria.json, schedules.json)

## When Building a Skill
1. Read config/eval-criteria.json for criteria this skill must satisfy.
2. Read an existing skill in skills/ for format reference.
3. Create evals/{skill-name}/draft.json with all criteria set to null.
4. Update config/schedules.json if the skill has a cron trigger.
5. Update config/discord-channels.json to map the skill to its channel.

## Eval Scoring
- Execution skills require 0.95 to auto-approve
- Risk skills require 0.90
- All others require 0.85
- Scores below threshold open a self-improve GitHub issue automatically

## Timezone
All cron schedules are UTC. Greg is in Los Angeles (UTC-7 during DST).
Always comment cron lines with the PT equivalent.
```

---

## Part 8 — Mac Mini Setup Commands

One-time setup on the Mac Mini (`ssh greg@192.168.4.94`):

```bash
# 1. Clone the workspace repo
git clone git@github.com:gblack686/greg-trading-workspace.git ~/.openclaw/workspace

# 2. Point OpenClaw at it
openclaw config set agents.defaults.workspace ~/.openclaw/workspace

# 3. Seed any missing workspace files
openclaw setup --workspace ~/.openclaw/workspace

# 4. Install claw-roam from ClawHub
cd ~/.openclaw/workspace
clawhub install claw-roam

# 5. Start AlphaClaw via Docker
cd ~/.openclaw/workspace/alphaclaw
docker compose up -d

# 6. Verify OpenClaw picks up skills
openclaw agents list
# Should show: Sebastian, Risk Guard, Quant, Signal Scout, Chart Maker

# 7. Test claw-roam pull
openclaw run --agent Sebastian "sync workspace from GitHub"
```

After a PR merges to `main`, claw-roam pulls the update:
```bash
# Triggered automatically by claw-roam on merge webhook, or manually:
openclaw run --agent Sebastian "claw-roam pull"
# OpenClaw reloads skills from workspace/skills/ in next session
```

AlphaClaw auto-commits any workspace changes (MEMORY.md updates, fill logs, eval JSONs) back to the repo hourly — every agent action is version-controlled.

---

## Part 9 — Pi Extensions

Pi is the interactive terminal layer that sits on top of OpenClaw. Extensions are `.ts` files that modify what Pi sees, does, and shows. All 16 extensions ship with the Greg trading workspace — loaded from `extensions/` in the repo root.

**Source**: `C:\Users\gblac\OneDrive\Desktop\tac\pi-vs-claude-code\extensions\`
**Copy to**: `~/.openclaw/workspace/extensions/` on Mac Mini (committed to repo)

---

### Full Extension Reference

| Extension | Category | What it does | Key commands / hooks |
|-----------|----------|-------------|----------------------|
| `minimal.ts` | UI | Compact single-line footer: model + 10-block context meter | `session_start` |
| `theme-cycler.ts` | UI | Cycle 51 themes · `Ctrl+X` forward, `Ctrl+Q` back, `/theme` picker | `Ctrl+X`, `Ctrl+Q`, `/theme` |
| `pure-focus.ts` | UI | Strips all footer/status — full zen mode | `session_start` |
| `themeMap.ts` | Infra | Maps extension → default theme, sets terminal title `π - <name>` · used by all extensions | `applyExtensionDefaults()` |
| `cross-agent.ts` | Integration | Loads commands from `.claude/`, `.gemini/`, `.codex/` · auto-registers `/name` commands | `session_start` scan |
| `pi-pi.ts` | Meta-builder | Parallel expert researchers (ext, theme, skill, config, tui, prompt, agent, keybinding) · synthesizes + writes files | `query_experts` tool, `/experts`, `/experts-grid` |
| `agent-team.ts` | Orchestrator | Dispatcher-only with team grid dashboard · primary agent has NO tools, only `dispatch_agent` · team defined in `teams.yaml` | `dispatch_agent`, `/agents-team`, `/agents-list`, `/agents-grid` |
| `agent-chain.ts` | Orchestrator | Sequential pipeline · each agent passes output to next · `$INPUT` / `$ORIGINAL` vars · chains from `agent-chain.yaml` | `run_chain`, `/chain`, `/chain-list` |
| `subagent-widget.ts` | Background agents | Spawn persistent background Pi agents · each has live widget (task, status, elapsed, tool count) · multi-turn via `/subcont` | `/sub`, `/subcont`, `/subrm`, `/subclear` |
| `system-select.ts` | Role switching | Swap system prompt + tool restrictions per role · scans `.pi/agents/`, `.claude/agents/` · frontmatter gates tools | `/system`, `/system <name>` |
| `tilldone.ts` | Discipline | Agent MUST define tasks before using any tools · three-state: idle → inprogress → done · auto-nudges at turn end if incomplete | `tilldone` tool (blocks all others), `/tilldone` overlay |
| `purpose-gate.ts` | Discipline | Blocks ALL input until agent declares intent · injects declared purpose into every system prompt | `input` blocker, `before_agent_start` injection |
| `damage-control.ts` | Safety | Blocks dangerous ops via rules in `damage-control-rules.yaml` · zero-access paths, read-only paths, banned bash patterns | `tool_call` interceptor (silent guardian) |
| `tool-counter.ts` | Metrics | Rich two-line footer: model + context meter + tokens in/out + cost + cwd + git branch + tool tally | `tool_execution_end` |
| `tool-counter-widget.ts` | Metrics | Live widget showing per-tool call counts with colored badges `[Bash 3] [Read 7] [Write 2]` | `tool_execution_end` |
| `session-replay.ts` | Audit | Scrollable session timeline · timestamps, elapsed per turn, expandable content · `/replay` opens overlay | `/replay`, ↑/↓ navigate, Enter expand |

---

### Greg Trading — Launch Stack

All 16 extensions loaded. Grouped by role in the launch command:

```bash
pi \
  # ── UI ─────────────────────────────────────────────────────────────
  -e extensions/theme-cycler.ts \
  -e extensions/themeMap.ts \
  \
  # ── Integration ────────────────────────────────────────────────────
  -e extensions/cross-agent.ts \
  \
  # ── Orchestration ──────────────────────────────────────────────────
  -e extensions/agent-team.ts \
  -e extensions/agent-chain.ts \
  -e extensions/subagent-widget.ts \
  -e extensions/pi-pi.ts \
  \
  # ── Role & Discipline ──────────────────────────────────────────────
  -e extensions/system-select.ts \
  -e extensions/tilldone.ts \
  -e extensions/purpose-gate.ts \
  \
  # ── Safety ─────────────────────────────────────────────────────────
  -e extensions/damage-control.ts \
  \
  # ── Metrics & Audit ────────────────────────────────────────────────
  -e extensions/tool-counter.ts \
  -e extensions/tool-counter-widget.ts \
  -e extensions/session-replay.ts \
  \
  # ── Situational (swap minimal/pure-focus per context) ──────────────
  -e extensions/minimal.ts
```

Add to `justfile` as named recipes:

```just
# Full trading desk — all extensions
pi-trading:
    pi \
      -e extensions/theme-cycler.ts \
      -e extensions/themeMap.ts \
      -e extensions/cross-agent.ts \
      -e extensions/agent-team.ts \
      -e extensions/agent-chain.ts \
      -e extensions/subagent-widget.ts \
      -e extensions/pi-pi.ts \
      -e extensions/system-select.ts \
      -e extensions/tilldone.ts \
      -e extensions/purpose-gate.ts \
      -e extensions/damage-control.ts \
      -e extensions/tool-counter.ts \
      -e extensions/tool-counter-widget.ts \
      -e extensions/session-replay.ts \
      -e extensions/minimal.ts

# Execution session — discipline + safety only
pi-execute:
    pi \
      -e extensions/theme-cycler.ts \
      -e extensions/themeMap.ts \
      -e extensions/cross-agent.ts \
      -e extensions/system-select.ts \
      -e extensions/tilldone.ts \
      -e extensions/purpose-gate.ts \
      -e extensions/damage-control.ts \
      -e extensions/tool-counter.ts \
      -e extensions/session-replay.ts \
      -e extensions/minimal.ts

# Research session — chain + subagents + meta-builder
pi-research:
    pi \
      -e extensions/theme-cycler.ts \
      -e extensions/themeMap.ts \
      -e extensions/cross-agent.ts \
      -e extensions/agent-chain.ts \
      -e extensions/subagent-widget.ts \
      -e extensions/pi-pi.ts \
      -e extensions/tool-counter.ts \
      -e extensions/session-replay.ts

# Risk review — safety-first, read-heavy
pi-risk:
    pi \
      -e extensions/theme-cycler.ts \
      -e extensions/themeMap.ts \
      -e extensions/damage-control.ts \
      -e extensions/purpose-gate.ts \
      -e extensions/tool-counter.ts \
      -e extensions/session-replay.ts \
      -e extensions/minimal.ts

# Focus mode — build a single skill, no distractions
pi-focus:
    pi \
      -e extensions/pure-focus.ts \
      -e extensions/themeMap.ts \
      -e extensions/cross-agent.ts \
      -e extensions/tilldone.ts \
      -e extensions/tool-counter.ts
```

---

### Extension-to-Agent Mapping

Which extensions matter most per Sebastian department:

| Agent / Dept | Critical extensions | Why |
|-------------|-------------------|-----|
| 🦁 Sebastian (Supervisor) | `agent-team`, `system-select`, `purpose-gate` | Dispatches departments, switches persona per task, declares mandate |
| 🎯 Apex (Execution) | `tilldone`, `damage-control`, `purpose-gate` | Every trade must be a declared task, safety blocks protect order logs |
| 🛡️ Risk Guard | `damage-control`, `tilldone`, `subagent-widget` | Can't delete risk records, runs background position watchers |
| 📊 Quant | `agent-chain`, `subagent-widget`, `tool-counter` | Research→Backtest→Report chains, background data agents, cost tracking |
| 🔍 Signal Scout | `subagent-widget`, `system-select` | Background Discord watchers as subagents, swap persona per channel |
| 📰 News Scout | `agent-chain`, `subagent-widget` | News→Sentiment→Alert chain, parallel source subagents |
| 📈 Chart Maker | `session-replay`, `tool-counter-widget` | Audit chart generation steps, see tool usage at a glance |
| 🔧 Coder Agent | `pi-pi`, `agent-chain`, `tilldone` | Meta-builds new skills, plan→build→review chain, task-gated |

---

### Pi Agent Definitions (`.pi/agents/`)

Generated files that ship with the workspace:

```
.pi/agents/
├── sebastian.md         # Supervisor persona — orchestrator, no execution tools
├── apex.md              # Execution persona — trade tools only, reduce_only enforced
├── risk-guard.md        # Risk persona — read-only, alert-only, no write to positions
├── quant.md             # Analytics persona — backtesting + quantpylib tools
├── signal-scout.md      # Intelligence persona — Discord read, signal parse
├── news-scout.md        # News persona — web fetch, sentiment, free APIs only
├── chart-maker.md       # Analytics persona — charting tools
├── coder.md             # Builder persona — full file access, testnet only
├── teams.yaml           # Team groupings (full-desk, risk-review, research, execution)
└── agent-chain.yaml     # Named chains (morning-brief, plan-build-review, news-pipeline)
```

**`teams.yaml`**:
```yaml
full-desk:
  - sebastian
  - apex
  - risk-guard
  - quant
  - signal-scout

risk-review:
  - risk-guard
  - quant

research:
  - quant
  - signal-scout
  - news-scout

execution:
  - apex
  - risk-guard
```

**`agent-chain.yaml`**:
```yaml
morning-brief:
  description: "Assemble and deliver Greg's morning brief"
  steps:
    - agent: news-scout
      prompt: "Gather top headlines, Fear & Greed, trending coins"
    - agent: signal-scout
      prompt: "Summarize yesterday's signals: $INPUT"
    - agent: quant
      prompt: "Pull portfolio snapshot and overnight P&L: $INPUT"
    - agent: sebastian
      prompt: "Assemble morning brief from: $INPUT. Deliver to Telegram."

plan-build-review:
  description: "Build a new skill end-to-end"
  steps:
    - agent: coder
      prompt: "Plan implementation for: $ORIGINAL"
    - agent: coder
      prompt: "Build following plan: $INPUT"
    - agent: coder
      prompt: "Review and validate: $INPUT. Run testnet check."

news-pipeline:
  description: "News → sentiment → trading signal"
  steps:
    - agent: news-scout
      prompt: "Scan all sources for: $ORIGINAL"
    - agent: quant
      prompt: "Score market impact of headlines: $INPUT"
    - agent: sebastian
      prompt: "Decide if any signal warrants a trade proposal: $INPUT"
```

---

### `damage-control-rules.yaml` for Trading

```yaml
zero_access:
  - path: "memory/fills/**"
    reason: "Trade fill records are immutable audit log"
  - path: "memory/execution-plans/**"
    reason: "Active execution plans must not be modified mid-run"
  - path: "evals/**"
    reason: "Eval history is append-only"
  - path: ".env"
    reason: "Never touch env file — secrets must stay in GitHub Secrets"

read_only:
  - path: "config/**"
    reason: "Config changes require PR review, not direct edit"
  - path: "AGENTS.md"
    reason: "Agent behavior changes require Greg approval"
  - path: "SOUL.md"
    reason: "Agent values are set by consulting intake, not runtime"

banned_bash_patterns:
  - pattern: "rm -rf"
    reason: "Never bulk delete in trading workspace"
  - pattern: "HYPERLIQUID_ENV=mainnet"
    reason: "Mainnet flag must be set explicitly by Greg, not by agent"
  - pattern: "exchange.market_open"
    reason: "Direct SDK calls outside SKILL.md are not permitted"
  - pattern: "exchange.order"
    reason: "All orders must go through approved Apex skill flow"
```

---

## Part 10 — Feedback UX (Discord Modal)

The thumbs up / thumbs down pattern is too coarse for self-improvement. Every approval, rejection, or review interaction opens a **Discord Modal** — a native pop-up form — so Greg can leave structured, descriptive feedback that flows directly into the eval JSON and the GitHub self-improve issue.

Discord Modals support up to 5 text input rows (short or paragraph style). No extra bot permissions required.

---

### 10.1 Feedback Modal — Skill Eval Review

Triggered when Greg taps any action button on an eval card (approve, reject, or flag).

```
╔══════════════════════════════════════════════════╗
║  📋 Skill Feedback — risk-guard-sl-audit         ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Overall Rating                                  ║
║  ┌────────────────────────────────────────────┐  ║
║  │ excellent / good / needs-work / reject     │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  What specifically went wrong? (optional)        ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  What should it do differently?                  ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Category (logic / format / speed / output / other) ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║              [Submit]    [Cancel]                ║
╚══════════════════════════════════════════════════╝
```

**Modal fields:**

| Field | Style | Required | Purpose |
|-------|-------|----------|---------|
| Overall Rating | Short (`excellent/good/needs-work/reject`) | Yes | Maps to pass/fail + priority |
| What went wrong | Paragraph (max 500 chars) | No | Human description of the failure |
| What to do differently | Paragraph (max 500 chars) | No | Direct instruction for self-improve |
| Category | Short (`logic/format/speed/output/other`) | No | Tags the issue type in eval JSON |

**On submit:** All fields written to eval JSON under `greg_feedback`:

```json
"greg_feedback": {
  "rating": "needs-work",
  "what_went_wrong": "It detected the missing SL but didn't suggest a price level to place it at. I want it to recommend the SL level based on ATR.",
  "what_to_do_differently": "After detecting a missing SL, call hyp-atr to compute a suggested SL distance and include it in the Telegram alert.",
  "category": "output",
  "submitted_at": "2026-03-19T13:08:44Z"
}
```

This feedback becomes the **body** of the self-improve GitHub issue — verbatim, quoted, with the eval score alongside it. `@claude` gets Greg's exact words, not just a score.

---

### 10.2 First-Run Approval Modal

Triggered when Greg taps ✅ **Approve**, ❌ **Reject**, or ⚠️ **Modify** on the first-run approval card.

#### ✅ Approve modal
```
╔══════════════════════════════════════════════════╗
║  ✅ Approve — morning-brief                      ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Any conditions for this approval? (optional)    ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "Only run on weekdays" or "Skip if    │  ║
║  │ portfolio drawdown > 3%"                   │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Notes for the agent (optional)                  ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║              [Approve]   [Cancel]                ║
╚══════════════════════════════════════════════════╝
```

#### ❌ Reject modal
```
╔══════════════════════════════════════════════════╗
║  ❌ Reject — morning-brief                       ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Why are you rejecting this? (required)          ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  What should it do instead? (optional)           ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║              [Reject]    [Cancel]                ║
╚══════════════════════════════════════════════════╝
```

#### ⚠️ Modify modal
```
╔══════════════════════════════════════════════════╗
║  ⚠️ Request Modification — morning-brief         ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  What needs to change before I approve?          ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Priority (low / normal / urgent)                ║
║  ┌────────────────────────────────────────────┐  ║
║  │ normal                                     │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║          [Request Modify]   [Cancel]             ║
╚══════════════════════════════════════════════════╝
```

---

### 10.3 Feedback → Self-Improve Issue Body

When Greg submits a Reject or Modify modal, the self-improve GitHub issue body is built from his exact words:

```markdown
## Self-Improve Request — morning-brief

**Run**: run-20260319-130001
**Eval score**: 0.72 / 1.0 (threshold: 0.85)
**Greg's rating**: needs-work
**Category**: output

---

### What went wrong (Greg's words)

> "The brief didn't include yesterday's signal scores.
> I want to see which signals from yesterday hit their TP or SL."

### What to do differently (Greg's words)

> "Pull from memory/signals/YYYY-MM-DD.json and check
> each signal against final price. Show outcome: TP hit / SL hit / still open."

---

### Eval criteria that failed

- `report_assembled`: 0.5 — missing signal outcomes section
- `no_empty_sections`: 0.0 — signals section had placeholder text

---

@claude Please update `skills/operations/morning-brief/SKILL.md` to address
Greg's feedback above. Open a PR when done. Target: eval_score ≥ 0.85.
```

---

## Part 11 — Trade Proposal Flow (Risk + Charts + Files)

Every trade proposal is a structured Discord message with:
1. **Chart image** — generated on-demand by Chart Maker, attached to the message
2. **Risk metrics block** — R:R, drawdown exposure, position size %, funding cost
3. **Proposal details** — entry, tranches, TP levels, SL
4. **Action buttons** — Approve / Reject / Modify (all open modals)

---

### 11.1 Chart Maker Agent

**Agent**: 📈 Chart Maker (`chart-maker`)
**Department**: Analytics
**Model**: DeepSeek V3
**Trigger**: On-demand — fired by Signal Scout, trade proposal flow, or Greg command

**What it generates:**

```
BTC/USDT — 4H  |  2026-03-19 06:00 PT
─────────────────────────────────────────────────────
 89,000 ─────────────────────────────── TP2 🎯
 87,000 ─────────────────────────────── TP1 🎯
 85,420 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ CURRENT
 84,200 ╔═══ ENTRY ZONE ════╗
 83,500 ╚════════════════════╝ ← entry spread
 82,000 ─────────────────────────────── SL 🛡️
─────────────────────────────────────────────────────
 RSI(14): 58.2  |  MACD: bullish cross  |  ATR: 1,240
 Support: 83,500  84,100  |  Resistance: 87,200  89,000
```

**Chart outputs** (saved to `memory/charts/YYYY-MM-DD/`):
- `{ticker}-{timestamp}-proposal.png` — price action + S/R levels + entry/TP/SL zones
- `{ticker}-{timestamp}-indicators.png` — RSI + MACD + Bollinger on separate panel
- `{ticker}-{timestamp}-combined.png` — both panels stacked (attached to Discord)

**Skills:**
```
skills/analytics/chart-maker/
├── SKILL.md
└── scripts/
    ├── generate_proposal_chart.py    # price action + zones overlay
    ├── generate_indicator_chart.py   # RSI / MACD / BB panel
    └── combine_charts.py             # stacks panels, adds watermark
```

**Python stack**: `matplotlib` + `mplfinance` + OHLCV from `hyp-candles`

---

### 11.2 Full Trade Proposal Discord Message

When Signal Scout scores a signal > 0.7 and Sebastian assembles a proposal, the Discord message looks like this:

```
╔══════════════════════════════════════════════════════════════╗
║  📊 TRADE PROPOSAL — BTC Long                               ║
║  Signal: discord/trading-room  Score: 0.91  WF-017          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  [CHART IMAGE — BTC/USDT 4H attached below]                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  ENTRY PLAN                                                  ║
║  T1  40%  0.044 BTC  market @ ~84,200   (on approve)        ║
║  T2  35%  0.039 BTC  limit  @ 83,500    (GTC)               ║
║  T3  25%  0.027 BTC  limit  @ 82,800    (GTC)               ║
╠══════════════════════════════════════════════════════════════╣
║  TARGETS                                                     ║
║  TP1  🎯  87,000   (+3.3%)   50% of position                ║
║  TP2  🎯  89,000   (+5.7%)   50% of position                ║
║  SL   🛡️  81,500   (-3.2%)   100% position (always)         ║
╠══════════════════════════════════════════════════════════════╣
║  RISK METRICS                                                ║
║  R:R ratio         1 : 1.8   (TP1)  /  1 : 2.9  (TP2)      ║
║  Max loss          $368       (SL hit, all tranches)         ║
║  Portfolio at risk  3.2%      (of $11,500 total)            ║
║  Slippage est.     ~4 bps     (from L2 orderbook depth)     ║
║  Funding (8h)      0.012%     ($1.01 cost to hold)          ║
║  Drawdown if SL    -3.2%      (within 5% limit ✅)          ║
╠══════════════════════════════════════════════════════════════╣
║  TECHNICALS (from Chart Maker)                               ║
║  RSI(14)    58.2   neutral → bullish                        ║
║  MACD       bullish crossover confirmed on 4H               ║
║  ATR(14)    1,240  SL distance = 1.1× ATR ✅                ║
║  Key S/R    Support 83,500 · 82,800  Resistance 87,200      ║
╠══════════════════════════════════════════════════════════════╣
║  SIGNAL SOURCE                                              ║
║  Channel: #trading-room  |  Poster: @whale_alerts           ║
║  Original: "BTC reclaiming 84k, targeting 87k, SL 81.5k"   ║
╠══════════════════════════════════════════════════════════════╣
║  [✅ Approve & Execute]  [❌ Reject]  [⚠️ Modify Params]    ║
╚══════════════════════════════════════════════════════════════╝

📎  btc-20260319-0600-proposal.png  (chart attached)
📎  btc-20260319-0600-indicators.png  (RSI/MACD attached)
```

---

### 11.3 Trade Proposal Modals

#### ✅ Approve & Execute modal
```
╔══════════════════════════════════════════════════╗
║  ✅ Approve — BTC Long                           ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Adjust position size? (default: full plan)      ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "50%" or "T1 only" or leave blank     │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Max slippage override? (default: 20 bps)        ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Notes for Apex (optional)                       ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "Only fill T2 if price dips below 84k"│  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║              [Execute Now]   [Cancel]            ║
╚══════════════════════════════════════════════════╝
```

#### ❌ Reject modal
```
╔══════════════════════════════════════════════════╗
║  ❌ Reject — BTC Long                            ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Why? (feeds Signal Scout self-improve)          ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "R:R too low, need at least 1:3"      │  ║
║  │ or "BTC dominance too high right now"       │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Would you trade this with different params?     ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "Yes, but SL at 82k not 81.5k"        │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║              [Reject]    [Cancel]                ║
╚══════════════════════════════════════════════════╝
```

#### ⚠️ Modify Params modal
```
╔══════════════════════════════════════════════════╗
║  ⚠️ Modify — BTC Long                            ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  New SL price (leave blank = keep 81,500)        ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  New TP1 / TP2 (leave blank = keep current)      ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "86000 / 90000"                       │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Tranche adjustment (leave blank = keep plan)    ║
║  ┌────────────────────────────────────────────┐  ║
║  │ e.g. "T1 only, skip T2/T3"                 │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║  Notes                                           ║
║  ┌────────────────────────────────────────────┐  ║
║  │                                            │  ║
║  └────────────────────────────────────────────┘  ║
║                                                  ║
║       [Regenerate Proposal]    [Cancel]          ║
╚══════════════════════════════════════════════════╝
```

After Modify is submitted: Sebastian regenerates the proposal with new params, Chart Maker re-renders the chart with updated zones, and the updated card is posted as a **new Discord message** (not an edit) so the original is preserved in history.

---

### 11.4 Trade Proposal Flow (End-to-End)

```
Signal Scout detects signal in Discord
        │
        ▼
Signal scored > 0.7
        │
        ▼
Chart Maker fires (parallel, non-blocking)
  hyp-candles → OHLCV data
  hyp-atr     → SL distance suggestion
  hyp-levels  → S/R levels
  generates proposal.png + indicators.png
        │
        ▼
Risk Guard computes risk metrics (parallel)
  portfolio size → position % calc
  hyp-orderbook → slippage estimate
  hyp-funding   → 8h cost
  drawdown projection if SL hit
        │
        ▼
Sebastian assembles proposal card
  combines: signal + chart + risk metrics + tranches
        │
        ▼
Discord message posted to #execution-approvals
  chart PNGs attached as files
        │
        ▼
Greg taps on mobile
  ✅ Approve (+ optional modal)  →  Apex executes
  ❌ Reject  (+ required modal)  →  logged, signal scored down
  ⚠️ Modify  (+ params modal)    →  regenerate + repost
        │
        ▼
Post-execution:
  Apex sends fill report to #execution-approvals
  Chart Maker generates post-trade chart (entry marked)
  Eval JSON written for both signal-scout + apex-trade-executor
```

---

### 11.5 On-Demand Chart Generation

Greg can also request charts outside the proposal flow via Discord:

```
!chart BTC 4h              → price + S/R levels only
!chart BTC 1h indicators   → RSI + MACD + Bollinger panel
!chart BTC compare ETH     → dual-ticker comparison (1h)
!chart BTC full            → combined chart (all panels)
```

Chart Maker responds with PNG attached within ~10 seconds. Charts saved to `memory/charts/` and committed to repo by AlphaClaw's hourly sync — full chart history in git.

---

### 11.6 Updated Skills List (Chart Maker)

```
skills/analytics/chart-maker/
├── SKILL.md
└── scripts/
    ├── generate_proposal_chart.py    # OHLCV + entry/TP/SL zone overlay
    ├── generate_indicator_chart.py   # RSI / MACD / Bollinger
    ├── combine_charts.py             # stack panels + watermark
    └── on_demand_chart.py            # handles !chart Discord commands

skills/analytics/chart-maker/SKILL.md frontmatter:
  triggers: [trade_proposal, !chart, volume_spike]
  output: [PNG file, Discord attachment]
  dependencies: [hyp-candles, hyp-atr, hyp-levels]
  model: DeepSeek V3
```

---

## Part 12 — Obsidian Scribe

### 12.1 Architecture Decision: Separate Repo

The Obsidian vault is **its own private GitHub repo** — not a submodule of the OpenClaw workspace.

```
gblack686/trading-brain  (private)   ← Obsidian vault repo
gblack686/greg-trading-workspace     ← OpenClaw workspace repo (already planned)
```

**Why separate:**
- Greg accesses the vault remotely on iPhone/iPad — Obsidian Git plugin syncs directly to `trading-brain`
- The vault has its own commit cadence (every 5 min via plugin, not hourly like AlphaClaw)
- Obsidian-specific files (`.obsidian/`, plugins, themes, CSS) don't belong in the agent workspace
- Vault grows large over time (charts, attachments) — keeps workspace lean

**Mac Mini layout:**
```
~/trading-brain/        ← cloned gblack686/trading-brain (Obsidian vault)
~/.openclaw/workspace/  ← cloned gblack686/greg-trading-workspace (OpenClaw)
```

OpenClaw writes to `~/trading-brain/` after each event. The Obsidian Git plugin (or a Mac Mini launchd cron) commits and pushes those changes.

---

### 12.2 Vault Structure

```
trading-brain/
│
├── .obsidian/
│   ├── plugins/
│   │   ├── obsidian-git/          # Auto-commit + push + pull on startup
│   │   ├── dataview/              # Query evals, signals, trades as tables
│   │   ├── templater/             # Note templates
│   │   └── bases/                 # Obsidian Bases (core plugin)
│   └── snippets/
│       └── trading-dark.css       # Dark angular theme (from obsidian-agent-archiver)
│
├── daily/
│   └── 2026-03-19.md              # Morning brief + signals + trades + evals for the day
│
├── crypto/
│   └── hyperliquid/
│       ├── proposals/
│       │   └── 2026-03-19-BTC-long.md
│       ├── trades/
│       │   └── 2026-03-19-BTC-APEX-001.md
│       ├── signals/
│       │   └── 2026-03-19.md      # Append-only signal log
│       ├── evals/
│       │   ├── risk-guard-sl-audit/
│       │   │   └── 2026-03-19.md
│       │   └── morning-brief/
│       │       └── 2026-03-19.md
│       └── charts/
│           └── 2026-03-19/        # Chart PNGs committed here
│               └── BTC-0600-proposal.png
│
├── agents/
│   └── sessions/
│       └── 2026-03-19-sebastian.md   # Session summary per agent
│
└── _views/
    ├── eval-dashboard.md          # Dataview: latest eval scores table
    ├── open-trades.md             # Dataview: active positions
    └── signal-feed.md             # Dataview: recent signals
```

---

### 12.3 The `obsidian-scribe` Skill

A dedicated OpenClaw skill that receives structured event data and writes the correct Obsidian note.

```
skills/operations/obsidian-scribe/
├── SKILL.md
└── scripts/
    ├── scribe.py               # main dispatcher — routes event to correct writer
    ├── writers/
    │   ├── daily_note.py       # appends to daily/YYYY-MM-DD.md
    │   ├── trade_proposal.py   # creates crypto/hyperliquid/proposals/...
    │   ├── trade_execution.py  # creates crypto/hyperliquid/trades/...
    │   ├── signal_log.py       # appends to crypto/hyperliquid/signals/...
    │   ├── eval_report.py      # creates crypto/hyperliquid/evals/...
    │   └── session_summary.py  # creates agents/sessions/...
    └── templates/
        ├── daily-note.md
        ├── trade-proposal.md
        ├── trade-execution.md
        ├── signal-entry.md
        ├── eval-report.md
        └── session-summary.md
```

**`SKILL.md` trigger config:**
```yaml
triggers:
  - event: morning_brief_delivered
    writer: daily_note
  - event: trade_proposal_posted
    writer: trade_proposal
  - event: trade_approved
    writer: trade_execution
  - event: fill_detected
    writer: trade_execution   # appends fill to existing plan note
  - event: signal_scored
    writer: signal_log
  - event: eval_completed
    writer: eval_report
  - event: session_end
    writer: session_summary

vault_path: "~/trading-brain"
```

---

### 12.4 Note Templates (with Frontmatter)

#### Daily Note (`daily/YYYY-MM-DD.md`)
```markdown
---
date: 2026-03-19
type: daily
agents_active: [Sebastian, Risk Guard, Signal Scout]
trades_opened: 1
trades_closed: 0
portfolio_drawdown: 0.8%
fear_greed: 62
tags: [daily, trading]
---

# 2026-03-19

## Morning Brief
_delivered 06:00 PT by Sebastian_

{{morning_brief_content}}

## Signals Today
{{dataview: signal_log filtered by date}}

## Trades
{{dataview: trades filtered by date}}

## Evals
| Skill | Score | Passed |
|-------|-------|--------|
| risk-guard-sl-audit | 0.60 | ❌ |
| morning-brief | 0.96 | ✅ |

## Agent Notes
{{session_summaries for today}}
```

#### Trade Proposal (`crypto/hyperliquid/proposals/2026-03-19-BTC-long.md`)
```markdown
---
date: 2026-03-19
type: trade-proposal
ticker: BTC
direction: long
status: approved          # pending / approved / rejected / modified
signal_score: 0.91
signal_source: "#trading-room @whale_alerts"
entry_price: 84200
sl: 81500
tp1: 87000
tp2: 89000
rr_ratio: 1.8
portfolio_risk_pct: 3.2
approved_by: greg
approved_at: 2026-03-19T13:04:22Z
chart: "[[charts/2026-03-19/BTC-0600-proposal.png]]"
tags: [proposal, BTC, long]
---

# BTC Long — 2026-03-19

![[charts/2026-03-19/BTC-0600-proposal.png]]

## Proposal
| Field | Value |
|-------|-------|
| Entry | ~84,200 (market T1) |
| SL | 81,500 (-3.2%) |
| TP1 | 87,000 (+3.3%) |
| TP2 | 89,000 (+5.7%) |
| R:R | 1 : 1.8 (TP1) / 1 : 2.9 (TP2) |
| Risk | $368 max loss / 3.2% portfolio |

## Risk Metrics
- Slippage est: ~4 bps
- Funding (8h): $1.01
- Drawdown if SL: -3.2% (limit 5% ✅)

## Technicals
- RSI(14): 58.2 — neutral → bullish
- MACD: bullish crossover on 4H ✅
- ATR(14): 1,240 — SL = 1.1× ATR ✅

## Greg's Feedback
{{greg_modal_comments if any}}

## Execution
→ [[trades/2026-03-19-BTC-APEX-001]]
```

#### Eval Report (`crypto/hyperliquid/evals/risk-guard-sl-audit/2026-03-19.md`)
```markdown
---
date: 2026-03-19
type: eval-report
skill: risk-guard-sl-audit
agent: Risk Guard
run_id: run-20260319-130012
eval_score: 0.60
passed: false
threshold: 0.90
greg_rating: needs-work
tags: [eval, risk-guard]
---

# Eval — risk-guard-sl-audit — 2026-03-19

**Score**: 0.60 / 1.0 ❌ (threshold: 0.90)

## Criteria
| Criterion | Score | Weight | Note |
|-----------|-------|--------|------|
| all_positions_have_sl | 0.0 | 40% | ETH-PERP missing SL |
| drawdown_within_limits | 1.0 | 25% | 0.8% < 5% ✅ |
| alerts_fired_correctly | 1.0 | 20% | Telegram delivered ✅ |
| no_false_positives | 1.0 | 15% | Alert was real ✅ |

## Greg's Feedback
> "After detecting a missing SL, call hyp-atr and include a suggested SL level."

## Self-Improve
→ [GitHub Issue #14](https://github.com/gblack686/greg-trading-workspace/issues/14)
```

---

### 12.5 The Hook — Where It Lives

**In OpenClaw**, every skill's SKILL.md has a mandatory final step:

```markdown
## Post-Run Hook

After completion, invoke `obsidian-scribe` with:
- event: {event_type}
- data: {structured output JSON}
- vault_path: ~/trading-brain
```

This is enforced by the `damage-control-rules.yaml` — skills without a scribe call in their post-run section fail the `build` eval criterion `obsidian_scribe_wired: true`.

**In HEARTBEAT.md** (Sebastian's 30-min check):

```markdown
- After morning brief delivery → call obsidian-scribe: daily_note
- If any evals completed since last heartbeat → call obsidian-scribe: eval_report
- At session end (idle > 10 min) → call obsidian-scribe: session_summary
```

**As a GitHub Actions job** (`eval-reporter.yml` already fires post-run):

```yaml
- name: Write to Obsidian vault
  run: |
    # SSH into Mac Mini and trigger obsidian-scribe
    ssh mac-mini "cd ~/.openclaw/workspace && \
      openclaw run --agent Sebastian \
      'obsidian-scribe eval --run-id ${{ env.RUN_ID }} \
       --skill ${{ env.SKILL_NAME }}'"
```

> Note: This requires the Mac Mini SSH key stored as a GitHub secret (`MAC_MINI_SSH_KEY`). Alternatively, the Mac Mini polls for new eval JSONs every 5 min and triggers the scribe itself (no inbound SSH needed).

---

### 12.6 Obsidian Git Plugin Config

Installed in the vault (`.obsidian/plugins/obsidian-git/`). Settings:

```json
{
  "autoSaveInterval": 5,
  "autoPushOnCommit": true,
  "pullBeforePush": true,
  "commitMessage": "vault: {{date}} auto-sync",
  "autoCommitMessage": "vault: {{date}} {{hostname}}",
  "pullOnStartup": true,
  "syncMethod": "merge"
}
```

**iOS access** (Greg's iPhone):
1. Install **Obsidian** on iPhone
2. Install **Working Copy** (iOS Git client) — clone `gblack686/trading-brain`
3. In Obsidian → open vault from Working Copy folder
4. Enable **Obsidian Git** plugin on mobile
5. Plugin uses isomorphic-git (no native git required on iOS)
6. Auto-pulls on app open → trade proposals, evals, and charts appear on phone

**Alternative (simpler)**: Use **Obsidian Sync** (paid, $4/mo) — bidirectional, instant, no git config. The Mac Mini writes to vault files, Sync pushes to all devices.

---

### 12.7 Dataview Dashboards

Three always-on views in `_views/`:

**`eval-dashboard.md`** — live eval scores:
````markdown
```dataview
TABLE eval_score, passed, greg_rating, date
FROM "crypto/hyperliquid/evals"
SORT date DESC
LIMIT 20
```
````

**`open-trades.md`** — active positions:
````markdown
```dataview
TABLE ticker, direction, entry_price, sl, tp1, status
FROM "crypto/hyperliquid/trades"
WHERE status = "active"
SORT date DESC
```
````

**`signal-feed.md`** — recent signals:
````markdown
```dataview
TABLE ticker, direction, signal_score, signal_source, status
FROM "crypto/hyperliquid/proposals"
SORT date DESC
LIMIT 30
```
````

---

### 12.8 Mac Mini Setup (Obsidian Vault)

```bash
# 1. Clone vault repo
git clone git@github.com:gblack686/trading-brain.git ~/trading-brain

# 2. Verify OpenClaw can write to it
ls ~/trading-brain/daily/

# 3. Set vault path in obsidian-scribe skill env
# (in openclaw.json skills.entries.obsidian-scribe.env)
OBSIDIAN_VAULT_PATH=/Users/greg/trading-brain

# 4. Set up auto-commit cron on Mac Mini (fallback if Obsidian Git not running)
# launchd plist or simple cron:
# */5 * * * *  cd ~/trading-brain && git add -A && git commit -m "auto $(date)" && git push
```

---

### 12.9 Summary — How It All Connects

```
Any OpenClaw skill completes
        │
        ▼
obsidian-scribe called (wired in SKILL.md post-run + HEARTBEAT.md)
        │
        ├── Writes note to ~/trading-brain/{path}
        │
        ▼
Obsidian Git plugin (on Mac Mini or via cron)
        │
        ├── git add -A && git commit && git push
        │
        ▼
gblack686/trading-brain repo updated
        │
        ├── Greg's iPhone pulls on Obsidian open
        └── Greg's desktop Obsidian synced live

Charts (PNG files from Chart Maker)
        │
        ├── Saved to ~/trading-brain/crypto/hyperliquid/charts/YYYY-MM-DD/
        └── Embedded in proposal notes via [[wikilink]]
```

---

## Part 13 — Acceptance Criteria (Full System)

### Infrastructure
- [ ] Mac Mini workspace is the cloned `gblack686/greg-trading-workspace` repo
- [ ] AlphaClaw Docker container running on Mac Mini, dashboard accessible
- [ ] AlphaClaw hourly git sync visible as commits on GitHub
- [ ] `claw-roam` installed and pulls successfully after a test PR merge
- [ ] OpenClaw lists all agents: Sebastian, Risk Guard, Quant, Signal Scout, Chart Maker

### Build Pipeline
- [ ] `@claude build risk-guard-sl-audit` in a GitHub issue creates a worktree branch, builds the skill, opens a PR
- [ ] Merging the PR triggers `claw-roam` pull on Mac Mini within 5 minutes
- [ ] New skill appears in `openclaw agents list` or skill registry after pull

### Eval + Discord
- [ ] First execution posts approval card to `#approval-queue` on Discord
- [ ] Greg taps ✅ on mobile → skill runs → `approval-registry.json` updated
- [ ] Subsequent runs skip approval gate and run directly
- [ ] Every run writes a valid JSON to `evals/{skill-name}/run-*.json`
- [ ] Passing runs post compact summary to mapped Discord channel
- [ ] Failing runs post full alert to channel + self-improve issue opened on GitHub

### Self-Improve Loop
- [ ] `@claude` responds to self-improve issue, opens a PR with improvement
- [ ] Merged improvement re-runs eval and score improves above threshold

### Full System
- [ ] All 9 skills approved and running on cron by end of Week 2
- [ ] Weekly rollup appears in `evals/_aggregate/` every Sunday 8pm PT
- [ ] AlphaClaw watchdog sends Discord alert if OpenClaw crashes and auto-restarts
