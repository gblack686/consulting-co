---
name: consulting-intake
description: "OpenClaw installation consulting pipeline. Processes a 90-minute consulting session transcript into a complete OpenClaw workspace with per-domain expert systems. Parses client goals, domains, workflows, and preferences into SOUL.md, USER.md, IDENTITY.md, MEMORY.md, AGENTS.md, TOOLS.md, HEARTBEAT.md, OpenClaw SKILL.md files, cron jobs, and full Claude Code expert directories (8+ files each) using TAC plan-build-improve-validate cycles. Use when processing a consulting transcript, building domain experts, or assembling a client workspace package."
---

# OpenClaw Consulting Intake Pipeline

## Overview

Transform a 90-minute consulting session transcript into a fully configured OpenClaw workspace with self-improving domain expert systems. This skill is the TAC Coding Expert — the meta-brain that knows how to build other experts.

## When to Use This Skill

- Processing a consulting session transcript into deliverables
- Building a domain expert system from a client spec
- Assembling OpenClaw workspace files from session data
- Validating a client workspace package before deployment
- User mentions "consulting intake", "process transcript", "build domain expert"

## Google Workspace Automation (GWS CLI)

This pipeline uses `gws` CLI skills (`.claude/skills/gws/`) to automate Google Workspace operations at each stage. Prerequisite: `gws auth login` (see `gws-shared/SKILL.md`).

### Pre-Session (after booking confirmed)
| Action | GWS Skill | Command |
|--------|-----------|---------|
| Send welcome email + prep guide | `gws-gmail-send` | `gws gmail messages send --to {email} --subject "..." --html --attach pre-session-prep.pdf` |
| Create client Drive folder | `recipe-organize-drive-folder` | Create `GBAutomation Clients/{Client Name}/` with subfolders |
| Share prep guide via Drive link | `recipe-email-drive-link` | Upload to Drive + email shareable link |
| Create 90-min session event | `gws-calendar-insert` | `gws calendar events insert --summary "OpenClaw Setup — {client}" --duration 90m` |
| Share service agreement | `recipe-share-doc-and-notify` | Share Google Doc + email notification |

### Post-Build (after Step 2: Build Workspace)
| Action | GWS Skill | Command |
|--------|-----------|---------|
| Create session Drive folder | `recipe-organize-drive-folder` | `{Client} — Session {YYYY-MM-DD}/deliverables/, workspace/, experts/` |
| Upload workspace files | `gws-drive-upload` | Batch upload SOUL.md, USER.md, etc. to client folder |
| Create PACKAGE_SUMMARY as Google Doc | `recipe-create-doc-from-template` | Generate viewable doc for client |

### Post-Deploy (after Step 5b)
| Action | GWS Skill | Command |
|--------|-----------|---------|
| Send delivery email | `gws-gmail-send` | "Your agent is live" + package summary + next steps |
| Draft delivery email from summary | `recipe-draft-email-from-doc` | Generate email body from PACKAGE_SUMMARY |
| Upload deliverables to Drive | `gws-drive-upload` | PACKAGE_SUMMARY.pdf, VALIDATION_REPORT.pdf |
| Schedule follow-up check-in | `gws-calendar-insert` | 30-min event 1 week after deploy |
| Log to client tracker sheet | `gws-sheets-append` | Append row: name, date, domains, score, status |
| Save session recording from email | `recipe-save-email-attachments` | Auto-save recording to client Drive folder |

### Ongoing Client Management
| Action | GWS Skill | Command |
|--------|-----------|---------|
| Weekly client digest | `gws-workflow-weekly-digest` | Summarize client emails + meetings |
| Pre-meeting briefing | `gws-workflow-meeting-prep` | Pull agenda, attendees, related docs |
| Inbox triage | `gws-gmail-triage` | Classify client vs prospect vs vendor |
| Email → task conversion | `gws-workflow-email-to-task` | Client requests become Google Tasks |
| Read recent client emails | `gws-gmail-read` | Quick lookup of correspondence |
| Generate engagement report | `recipe-generate-report-from-sheet` | Pull tracker data into formatted report |

## Session Naming Convention

Every client session lives in a `YYYYMMDD-{project}/` directory under `client-sessions/`:

```
client-sessions/
├── 20260221-greg-trading/
├── 20260301-jane-content/
└── 20260315-acme-support/
```

**Format**: `YYYYMMDD` (intake date) + `-` + `{client-project}` (kebab-case, descriptive).

This feeds directly into the GitHub branch name: `client/YYYYMMDD-{project}`.

## Pipeline Commands

### `/consulting-intake parse-transcript <path>`
Parse a consulting transcript into structured session output.
Output dir: `client-sessions/YYYYMMDD-{project}/`

### `/consulting-intake build-workspace <session_output_dir>`
Generate OpenClaw workspace files (SOUL, USER, IDENTITY, etc.) from parsed session data.

### `/consulting-intake build-domain <domain_spec.json>`
Build a complete expert system for one domain using plan-build-improve-validate.

### `/consulting-intake validate <package_dir>`
Quality-check the complete client package (experts + workspace + config).

### `/consulting-intake repo-setup <session_dir>`
Initialize or update the OpenClaw clients GitHub repo and create a client branch.

### `/consulting-intake deploy <package_dir> --host <ip> --key <path>`
Deploy the assembled package to a client's OpenClaw instance via SSH (or local copy for Windows).

## Architecture

```
GWS Pre-Session ──► Transcript → Parse → Build Workspace → Pi Extensions → Domain Experts → Validate → Deploy ──► GWS Handoff
│                                             │                  │                │                        │              │
│ gws-gmail-send (welcome)             YYYYMMDD-{project}/  Copy 16 .ts   ┌──────┼──────┐         branch: client/  gws-gmail-send (delivery)
│ gws-calendar-insert (session)        session_output/      .pi/agents/    ▼      ▼      ▼         YYYYMMDD-{project} gws-drive-upload (deliverables)
│ recipe-organize-drive-folder         workspace/           justfile Pi  PLAN  BUILD  IMPROVE                       gws-calendar-insert (follow-up)
│ recipe-share-doc-and-notify          experts/             recipes    (research)(write)(validate)                   gws-sheets-append (tracker)
│                                      extensions/                        │      │      │
│                                      .pi/agents/               Browser ─┘  Templates  Loop if <80%
│                                      dashboard/                YouTube
│                                           │
│                                    gws-drive-upload (workspace files)
│                                    recipe-create-doc-from-template
```

**Runtime Architecture** (what ships to client):
```
Vue Dashboard (port 3050)  ←→  Gateway Proxy  ←→  Pi Runtime (port 18789)
   Chat UI                      Event translation    Extensions loaded
   Event stream                 WebSocket bridge     .pi/agents/ definitions
   Agent cards                  /health endpoint     Skills (SKILL.md)
                                                     Workspace files
```

## Core Knowledge

This skill's intelligence comes from these reference files:

| Reference | Purpose |
|-----------|---------|
| `references/session-framework.md` | 30 discovery questions mapped to OpenClaw files |
| `references/openclaw-workspace-spec.md` | Format spec for all 7 workspace files |
| `references/skill-format-spec.md` | OpenClaw SKILL.md format with frontmatter rules |
| `references/expert-system-pattern.md` | The 8-file expert pattern (from eval expert) |
| `references/agent-architecture.md` | Full pipeline architecture with flow diagrams |
| `references/multi-agent-patterns.md` | 5 deployment patterns: single, domain, context, orchestrator, peer |
| `references/model-tiers.md` | 3 cost tiers (cheap/mid/pro) with OpenRouter model IDs and intelligent routing patterns |
| `references/tac-pattern-library.md` | Which TAC pattern applies to which workflow type |
| `references/quality-rubric.md` | Scoring criteria for validation (>= 80% to ship) |
| `references/pi-extension-selection.md` | Pi extension stacks: core set, selection matrix, justfile recipes |
| `references/github-repo-strategy.md` | Branch model, repo init, `.gitignore`, PR workflow |
| `client-facing/` | Welcome email, prep guide, agenda, glossary, service agreement |
| `templates/` | Shared workspace templates (SOUL, USER, IDENTITY, etc.) |
| `templates/agent-workspace/` | Per-domain agent workspace templates (Pattern B) |
| `templates/expert/` | Claude Code expert system templates (8-file pattern) |

### External Reference
| Document | Location |
|----------|----------|
| OpenClaw Multi-Agent Architecture | `.claude/context/architecture/OPENCLAW_MULTI_AGENT_ARCHITECTURE.md` |
| Practical Guide to OpenClaw (PDF) | `.claude/context/openclaw-practical-guide.pdf` — full beginner guide by Matthew Berman |
| Soul file templates | `onlycrabs.ai` — community SOUL.md templates by personality type |
| Skills directory | `clawhub.ai` — 1,700+ community skills (check VirusTotal report before installing) |
| here.now hosting | `here.now` — instant static hosting for agent-published content (no account needed) |
| here.now SKILL.md | `npx skills add heredotnow/skill --skill here-now -g` — install so agent can publish URLs |
| Mac Mini Install Guide | `templates/mac-mini-install.md` |
| Mac Mini Agent (Steer/Drive/Listen) | `C:/Users/gblac/OneDrive/Desktop/tac/mac-mini-agent/` |
| Pi Extensions (16 reference implementations) | `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions/` |
| OpenClaw × Pi Patterns Plan | `.claude/context/OPENCLAW_PI_PATTERNS_PLAN.md` |

## Pipeline Detail

### Step 0: Pre-Session GWS Setup (run when session is booked)

1. `recipe-organize-drive-folder` — create `GBAutomation Clients/{Client Name}/` with subfolders: `deliverables/`, `workspace/`, `recordings/`
2. `gws-gmail-send` — send welcome email from `client-facing/welcome-email.md` template with pre-session prep attached
3. `recipe-share-doc-and-notify` — share service agreement as Google Doc for e-signature
4. `gws-calendar-insert` — create 90-min session event with video call link and agenda

### Step 1: Parse Transcript

Read `references/session-framework.md` for the question-to-file mapping. Extract:

1. **Client Profile** → `session_output/client_profile.json`
   - Name, timezone, pronouns, working hours
   - Current projects, interests
   - Communication preferences

2. **Soul & Vibe** → `session_output/soul_draft.md`
   - Core truths (quality bar, AI experience)
   - Boundaries (what agent must never do without asking)
   - Vibe (communication style, emoji usage, tone)
   - **SOUL shaping prompts** — extract these verbatim from the session, they go directly into SOUL.md:
     - Communication style: *"Talk like a slightly sarcastic friend who's really good at logistics"*
     - Output format: *"No filler words. No 'Great question!' Just help."*
     - Uncertainty handling: *"When you're not sure, say so. Don't hedge."*
     - Summary style: *"Lead with what I need to do, not what happened."*
     - Confirmation policy: *"Always confirm before sending anything on my behalf."*
   - Browse `onlycrabs.ai` for community soul templates matching the client's personality type

3. **Identity** → `session_output/identity.json`
   - Agent name, creature type, vibe, emoji

4. **Mission** → `session_output/mission_statement.md`
   - Mission statement
   - 90-day goals
   - Top autonomous task candidate

5. **Tool Inventory** → `session_output/tool_inventory.json`
   - Hardware (device type, specs)
   - Apps & tools (with API status)
   - API keys & subscriptions — always capture `openrouter_api_key` (recommended default LLM provider)
   - Channel preference (Telegram/Discord/WhatsApp)
   - Budget for AI costs
   - Models: capture `brain_model` and `muscle_model` in OpenRouter format (e.g. `openrouter/anthropic/claude-sonnet-4-5`)

6. **Domains** → `session_output/domains/{name}.json` (one per domain)
   - Domain name and description
   - Tools used in this domain
   - Frequency (daily/weekly/ad-hoc)

7. **Workflows** → `session_output/domains/{domain}/workflows/{name}.json`
   - Step-by-step procedure (from "train a new hire" question)
   - Trigger type (cron/webhook/heartbeat/on-demand)
   - Output format and delivery channel
   - Decision points (human approval gates)
   - Blast radius (what happens if it goes wrong)

8. **Autonomy Config** → `session_output/autonomy.json`
   - Autonomy level (ask-everything to just-get-it-done)
   - External communication permissions
   - Allowlist (who can talk to agent)
   - Session reset preferences

### Step 2: Build Workspace

Transform session_output into OpenClaw workspace files using templates in `templates/`.

Read `references/openclaw-workspace-spec.md` for exact format requirements.

| Session Data | OpenClaw File | Template |
|---|---|---|
| client_profile + identity | USER.md, IDENTITY.md | `templates/USER.md.tmpl`, `templates/IDENTITY.md.tmpl` |
| soul_draft | SOUL.md | `templates/SOUL.md.tmpl` |
| mission_statement | MEMORY.md | `templates/MEMORY.md.tmpl` |
| autonomy + session prefs | AGENTS.md | `templates/AGENTS.md.tmpl` |
| tool_inventory | TOOLS.md | `templates/TOOLS.md.tmpl` |
| periodic workflows | HEARTBEAT.md | `templates/HEARTBEAT.md.tmpl` |
| model + channels + session | openclaw.json | `templates/openclaw.json.tmpl` |
| all of the above | justfile | `templates/justfile.tmpl` |

Fill `{CLIENT_NAME}`, `{AGENT_NAME}`, `{INTAKE_DATE}`, `{DOMAIN_LIST}` in the justfile template.
The justfile lives at the **repo root** (not inside `workspace/`) so clients can run `just setup` immediately after cloning.

**Upload to Google Drive** (GWS):
1. `recipe-organize-drive-folder` — create `{Client} — Session {YYYY-MM-DD}/` in client Drive folder with subfolders: `deliverables/`, `workspace/`, `experts/`
2. `gws-drive-upload` — upload workspace files (SOUL.md, USER.md, IDENTITY.md, etc.) to `workspace/` subfolder
3. `recipe-create-doc-from-template` — create PACKAGE_SUMMARY as a viewable Google Doc for the client

### Step 2b: Select Pi Extensions & Generate Agent Definitions

Read `references/pi-extension-selection.md` for the full selection matrix.

1. **Select extension stack** from session data:
   - `autonomy.json` → safety extensions (damage-control, purpose-gate, tilldone)
   - `tool_inventory.json` → cost extensions (tool-counter, tool-counter-widget)
   - `domains/` count + complexity → orchestration extensions (agent-team, agent-chain, subagent-widget)
   - `client_profile.json` → UX extensions (session-replay, pure-focus)

2. **Copy all 16 extensions** from `C:/Users/gblac/OneDrive/Desktop/tac/pi-vs-claude-code/extensions/` to `extensions/` in client workspace (core + samples)

3. **Generate `.pi/agents/`** from domains:
   - Standard agents: scout, planner, builder, reviewer (always)
   - Per-domain agents: one `.md` per domain with domain-specific system prompt + tools
   - `teams.yaml` with team combos per domain
   - `agent-chain.yaml` with plan-build-review + domain-specific chains

4. **Fill `{pi_extension_extras}` placeholder** in `openclaw.json.tmpl`

5. **Generate Pi justfile recipes** in `justfile.tmpl` (pi-core, pi-costs, pi-safe, etc.)

### Step 3: Build Domain Experts

For EACH domain in `session_output/domains/`, run the plan-build-improve-validate cycle.

Read `references/expert-system-pattern.md` for the 8-file structure.
Read `references/tac-pattern-library.md` for TAC pattern selection.

#### PLAN Phase
1. Load domain spec (name, tools, workflows)
2. Classify each workflow by TAC pattern:
   - Scheduled output → TAC-3 (Template Engineering)
   - Research/discovery → TAC-6 (One Agent One Purpose)
   - Sync/integration → TAC-5 (Feedback Loops)
   - Content production → TAC-3 + TAC-9 (Context Engineering)
3. Identify API research needs → dispatch browser agent:
   ```
   Task(subagent_type: "playwright-bowser-agent", prompt: "Research {tool} API...")
   ```
4. Identify tutorial research needs → dispatch youtube agent:
   ```
   Task(subagent_type: "youtube-transcript-agent", prompt: "Search OpenClaw {tool}...")
   ```
5. Determine domain-specific commands needed (see Command Selection Logic below)
6. Output: `specs/{domain}-plan.md`

#### BUILD Phase

**Before building any skill from scratch — search ClawHub first.**

ClawHub (`clawhub.ai`) is the OpenClaw community skill library with 1,700+ production skills. Check it before spending build cycles:

```
Task: "Search ClawHub at clawhub.ai for skills matching '{domain}' or '{workflow_name}'.
       Check VirusTotal security report on the skill page before installing.
       Return skill name, star count, VirusTotal status, and install command if found."
```

**Security note**: ~5% of ClawHub skills have been found to contain threats (data exfiltration, prompt injection, malware). Always check the VirusTotal report on the skill's ClawHub page before installing. Read the source (it's a text file). Be skeptical of recommendations from Discord strangers.

If a matching skill exists: install it, customize the config section, skip the BUILD phase for that workflow.
If not found: proceed with build from templates below.

Generate all files using templates in `templates/expert/`. Always include the universal `setup-openclaw` skill from `templates/skills/setup-openclaw/SKILL.md` — every client workspace needs it. Customize the secrets list based on their tool inventory.



1. `_index.md` — from `templates/expert/_index.md.tmpl`
2. `expertise.md` — from `templates/expert/expertise.md.tmpl` (7 parts)
3. `question.md` — from `templates/expert/question.md.tmpl` (6 categories)
4. `plan.md` — from `templates/expert/plan.md.tmpl`
5. `plan_build_improve.md` — from `templates/expert/plan_build_improve.md.tmpl`
6. `self-improve.md` — from `templates/expert/self-improve.md.tmpl`
7. Domain-specific commands — generated based on workflow types
8. OpenClaw SKILL.md files — from `templates/skill.md.tmpl` per workflow
9. Cron job definitions — CLI commands for `openclaw cron add`

#### IMPROVE Phase
1. Review built files against plan
2. Incorporate API research findings into expertise.md Part 6
3. Incorporate YouTube tutorial patterns into expertise.md Part 7
4. Update Part 7 (Patterns & Learnings) with build experience

#### VALIDATE Phase
Read `references/quality-rubric.md` for full scoring criteria.

Score each domain expert. If < 80%, loop back to BUILD with specific fixes.

### Step 3b: Quick Win First

**Goal: Get one working Telegram notification to the client within 24 hours of deploy — before all domains are complete.**

The most universally valuable quick win is a **morning briefing**. Every client type benefits:
- Trading → overnight moves, open positions, signal summary
- Content → scheduled posts, engagement metrics, content queue
- Business → daily task summary, calendar, email digest
- Dev → build status, open PRs, deploy health

**Morning brief is a default domain** — always include it unless the client explicitly opts out.

Quick win implementation order:
1. Deploy workspace with any working secrets (Telegram minimum)
2. Build `morning-brief` domain expert first (simplest — just assembles + sends text)
3. Test: manually trigger it via `openclaw cron trigger morning-brief`
4. Send to client via Telegram so they see something working on Day 1
5. Then continue building remaining domain experts

This is the **action-first principle** from the OpenClaw guide: show the output before showing the configuration. A client who gets a morning brief on Day 1 has proof of value before the full system is live.

### Step 4: Validate Package

Run `references/quality-rubric.md` against the complete assembled package.

### Step 5a: GitHub Repo Setup

Read `references/github-repo-strategy.md` for the full strategy.

**Each client gets their own private repo**:
```
github.com/gbauto/{client-project}
  main              ← delivered workspace (the client's files)
  update/YYYYMMDD   ← future iterations
```

**Procedure**:
1. Create private repo `gbauto/{client-project}`
   - Example: `gbauto/greg-trading`
2. Clone it locally to `~/openclaw-{client-project}`
3. Copy deliverables to the clone:
   - `workspace/` — all OpenClaw config files
   - `experts/` — domain expert systems
   - `PACKAGE_SUMMARY.md`, `VALIDATION_REPORT.md`
   - **Exclude**: `session_output/` (contains raw transcript data — internal only)
4. Commit: `"intake: {YYYYMMDD} {client} — {N} domains, score {score}/100"`
5. Push `main` to GitHub
6. Optionally invite client as read-only collaborator:
   ```bash
   gh api repos/gbauto/{client-project}/collaborators/{github-user} \
     --method PUT --field permission=pull
   ```

**For future iterations** (new features, updates):
```bash
git checkout -b "update/YYYYMMDD"
# make changes
git push -u origin "update/YYYYMMDD"
gh pr create --base main --head "update/YYYYMMDD" --title "[{client}] Update"
```

### Step 5b: Deploy

**Option A: ZeroClaw CDK (recommended for new clients)**
```bash
cd zeroclaw-deploy
npm install
cdk bootstrap  # first time only

# Deploy for a client — one command
cdk deploy \
  --context client={client-project} \
  --context openrouterKey={openrouter_api_key} \
  --context modelTier=cheap

# Output: static IP, gateway token, proxy URL
# Verify:
ssh ubuntu@<ip> "zeroclaw doctor"
curl http://<ip>:3050/health
```

Config: generates `config.toml` (ZeroClaw format) instead of `openclaw.json`.
Stack location: `zeroclaw-deploy/` in repo root.
Cost: $3.50/mo nano instance vs $24/mo for OpenClaw 4GB.

**Option B: Local Windows** (Greg's setup):
```bash
# Copy workspace files to OpenClaw directory
cp -r workspace/* ~/.openclaw/workspace/
cp -r workspace/skills/* ~/.openclaw/workspace/skills/

# Restart gateway
openclaw restart

# Install cron jobs
bash workspace/cron-setup.sh

# Verify
openclaw doctor
```

**Option C: Remote server** (manual SSH deploy):
```bash
tar -czf client-workspace.tar.gz workspace/ experts/
scp -i {key} workspace/* ubuntu@{host}:~/.openclaw/workspace/
scp -r -i {key} workspace/skills/* ubuntu@{host}:~/.openclaw/workspace/skills/
ssh -i {key} ubuntu@{host} "systemctl --user restart openclaw-gateway"
ssh -i {key} ubuntu@{host} "bash ~/cron-setup.sh"
ssh -i {key} ubuntu@{host} "openclaw doctor --non-interactive"
```

**Option D: Mac Mini** (OpenClaw + GUI/terminal automation):
Full guide: `templates/mac-mini-install.md`
```bash
# SSH into Mac Mini
ssh greg@{mac-mini-ip}

# Install deps + OpenClaw (Phases 1-9 from mac-mini-install.md)
brew install node@22 just tmux uv yq
npm install -g openclaw@latest
openclaw onboard

# Deploy workspace
scp -r workspace/* greg@{mac-mini-ip}:~/.openclaw/workspace/
scp -r workspace/skills/* greg@{mac-mini-ip}:~/.openclaw/workspace/skills/
ssh greg@{mac-mini-ip} "openclaw restart && openclaw doctor --non-interactive"

# Optional: Install mac-mini-agent for GUI automation (Phase 11)
ssh greg@{mac-mini-ip} "git clone https://github.com/disler/mac-mini-agent ~/mac-mini-agent"
ssh greg@{mac-mini-ip} "cd ~/mac-mini-agent/apps/steer && swift build -c release"
ssh greg@{mac-mini-ip} "cd ~/mac-mini-agent && just listen"  # Job server on port 7600
```

Stack: OpenClaw (skills, channels, cron) + Steer (GUI) + Drive (terminal) + Listen (jobs).
Ref: [mac-mini-agent](https://github.com/disler/mac-mini-agent) by IndyDevDan.
Cost: Hardware only — no monthly cloud fees.

### Step 5d: Client Handoff (GWS)

After deploy + smoke test pass, automate the client handoff via Google Workspace:

1. `recipe-draft-email-from-doc` — generate delivery email body from PACKAGE_SUMMARY
2. `gws-gmail-send` — send "Your agent is live" email with:
   - Package summary (inline or attached)
   - Quick-start commands for the client
   - Support channel info
   - Link to client Google Drive folder
3. `gws-drive-upload` — upload PACKAGE_SUMMARY.pdf + VALIDATION_REPORT.pdf to Drive `deliverables/` folder
4. `gws-calendar-insert` — schedule 30-min follow-up check-in 1 week after deploy
5. `gws-sheets-append` — log engagement to client tracker spreadsheet:
   - Client name, intake date, domain count, validation score, deploy target, status
6. `recipe-save-email-attachments` — if session recording arrives via email, auto-save to Drive `recordings/` folder

### Step 5c: Zero-Touch Bootstrap (Post-Deploy Hardening)

After deploying the workspace, run this checklist **before handing off to the client**. Every step that requires manual interaction is a future support ticket — eliminate them here.

#### 0. Secrets Discovery & Batch Injection

Before the client provides keys manually, scan for them automatically:

```bash
# 1. Scan project root .env
grep -v "^#" ~/.openclaw/workspace/.env 2>/dev/null | while IFS='=' read key val; do
  [ -n "$key" ] && [ -n "$val" ] && openclaw config set "env.$key" "$val"
done

# 2. Pull from AWS Secrets Manager (if client uses it)
# Pattern: secrets named {client-project}/{service}
aws secretsmanager list-secrets --query "SecretList[?contains(Name,'greg-trading')].Name" \
  | jq -r '.[]' | while read name; do
    aws secretsmanager get-secret-value --secret-id "$name" \
      --query SecretString --output text | jq -r 'to_entries[] | "\(.key)=\(.value)"'
  done | while IFS='=' read key val; do
    openclaw config set "env.$key" "$val"
  done
```

**What to look for in .env**:
- `OPENROUTER_API_KEY` → primary LLM access
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` → notification channel
- `DISCORD_BOT_TOKEN` or `DISCORD_USER_TOKEN` → signal feeds
- Service-specific keys (HYPERLIQUID, KIYOTAKA, SUPABASE, FRED, etc.)

#### 1. Discord: User Token > Bot Token

**Never use the bot OAuth invitation flow for signal feed channels.** Server channels are almost always role-restricted and the bot will get 403 on every fetch.

**Instead, extract the user token from the client's already-logged-in browser session**:

```javascript
// Run in Discord web app DevTools console (or via mac-mini-agent Drive terminal)
// Extracts auth token without any additional login
(() => {
  const iframe = document.createElement('iframe');
  document.head.append(iframe);
  const token = iframe.contentWindow.localStorage.token;
  iframe.remove();
  return token;
})()
```

Store it immediately:
```bash
# Store in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "openclaw/discord/user-token" \
  --secret-string "{\"token\":\"$DISCORD_USER_TOKEN\"}"

# Inject into OpenClaw
openclaw config set env.DISCORD_USER_TOKEN "$DISCORD_USER_TOKEN"
```

**Auth header format**: `"Authorization": user_token` (no "Bot " prefix).

Discord expert files use `DISCORD_USER_TOKEN` if present, fall back to `DISCORD_BOT_TOKEN`:
```python
def _discord_headers():
    user_token = os.getenv("DISCORD_USER_TOKEN")
    if user_token:
        return {"Authorization": user_token, "Content-Type": "application/json"}
    bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
    return {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
```

#### 2. Exec / Bash Access Verification

The `openclaw.json.tmpl` now includes `tools.elevated` with `"*": ["*"]` so exec is enabled by default. Verify immediately after first deploy:

```bash
# From agent session — confirm bash works
echo "exec test" && pwd && ls ~/.openclaw/workspace/

# If this fails, manually patch openclaw.json:
python3 -c "
import json
c = json.load(open('/Users/greg/.openclaw/openclaw.json'))
c.setdefault('tools', {}).setdefault('elevated', {})['enabled'] = True
c['tools']['elevated']['allowFrom'] = {
    'telegram': ['*'], 'discord': ['*'], 'session': ['*'], '*': ['*']
}
json.dump(c, open('/Users/greg/.openclaw/openclaw.json', 'w'), indent=2)
print('exec fixed')
" && openclaw gateway restart
```

#### 3. API Key Validation (Trading Clients)

For clients with exchange API access, **always test a real order place + cancel before claiming the pipeline is live**.

**Hyperliquid pattern** (API wallet → main account):
```python
# scripts/validate_api_keys.py
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account import Account
import os

wallet = Account.from_key(os.environ["HYP_KEY"])
exchange = Exchange(
    wallet,
    constants.MAINNET_API_URL,
    account_address=os.environ["HYPERLIQUID_ACCOUNT_ADDRESS"]
)

# Place a deeply out-of-money limit order (won't fill)
result = exchange.order("BTC", True, 0.001, 50000, {"limit": {"tif": "Gtc"}})
oid = result["response"]["data"]["statuses"][0]["resting"]["oid"]
print(f"✅ Order placed: oid={oid}")

# Cancel immediately
cancel = exchange.cancel("BTC", oid)
print(f"✅ Cancelled: {cancel['response']['data']['statuses'][0]}")
```

**Key validation rules**:
- API wallet address ≠ main account address — verify `account_address` param is set
- API wallets have trading-only permissions (no withdrawal) — confirm this in exchange UI
- Test order should be a limit far from market price so it never fills
- If `0x22f8...`-style key returns $0 balance, check `.env` for another key — API wallet keys are separate from main account keys

#### 4. Telegram Delivery Verification

Before declaring any scheduler job complete, send a real test message:

```bash
# Quick smoke test
python3 -c "
import httpx, os
token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id = os.environ['TELEGRAM_CHAT_ID']
r = httpx.post(
    f'https://api.telegram.org/bot{token}/sendMessage',
    json={'chat_id': chat_id, 'text': '✅ OpenClaw bootstrap complete — Sebastian is live', 'parse_mode': 'HTML'}
)
print(r.status_code, r.json())
"
```

#### 5. Post-Deploy Smoke Test Checklist

Run these after every new client deployment:

```
[ ] openclaw doctor --non-interactive  → exit 0
[ ] Gateway responding: curl http://localhost:18789/health → {"status":"ok"}
[ ] Exec works: send "run: echo hello" from agent session → response appears
[ ] Channels connected: send test message via each active channel (Telegram/Discord)
[ ] Cron registered: openclaw cron list → all expected jobs appear
[ ] Secrets visible: openclaw config get env → all injected keys present (redacted values)
[ ] API validated: run validate_api_keys.py → order placed + cancelled successfully
[ ] Scheduler daemon live: systemctl --user status openclaw-gateway → active (running)
[ ] Test signal scan: python3 scripts/signal_scout_scan.py --dry-run → parses without error
[ ] Telegram ping: manual message delivered successfully (step 4 above)
[ ] npm update: npm update -g openclaw@latest → confirm running latest version
[ ] Spending cap set: openrouter.ai/settings/limits → monthly cap configured (and console.anthropic.com if using Claude directly)
[ ] Exec approvals: ~/.openclaw/exec-approvals.json → defaults.security="full", ask="off", askFallback="full", autoAllowSkills=true (see Phase 6b of mac-mini-install.md)
```

Save results to `session_output/SMOKE_TEST_RESULTS.md` with datetime + pass/fail per item.

#### 6. Mac Mini Specific (launchd)

When deploying to Mac Mini via launchd plist (not systemd):

```bash
# Inject env vars into plist BEFORE loading
/usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:DISCORD_USER_TOKEN '$TOKEN'" \
  ~/Library/LaunchAgents/ai.hyperliquid.expert-scheduler.plist

# Load the daemon
launchctl load ~/Library/LaunchAgents/ai.hyperliquid.expert-scheduler.plist

# Verify loaded
launchctl list | grep hyperliquid
```

**Critical**: plist `EnvironmentVariables` are static — any key rotation requires:
1. Update plist with `PlistBuddy`
2. `launchctl unload` then `launchctl load`
3. Also update `openclaw.json` (separate env store for interactive sessions)

---

## Command Selection Logic

For each domain, analyze workflows and generate domain-specific commands:

| Workflow Type | Generated Command | Example |
|---|---|---|
| Scheduled outputs | `schedule-{type}.md` | schedule-newsletter, schedule-report |
| Research/discovery | `research-{topic}.md` | research-trends, research-competitors |
| Sync/integration | `sync-{tool}.md` | sync-pipeline, sync-analytics |
| Content production | `draft-{type}.md` | draft-script, draft-post |
| Analytics/reporting | `report-{metric}.md` | report-kpis, report-engagement |
| Maintenance/cleanup | `maintenance.md` | maintenance (standard) |

Every domain always gets the standard 6: `_index, expertise, question, plan, plan_build_improve, self-improve`.

## Research Agent Configs

### Browser Research (dispatched during PLAN)
```
Task(subagent_type: "playwright-bowser-agent")

Prompt: Research the {tool_name} API for OpenClaw integration.
Find: API docs URL, auth method, base URL, key endpoints,
      MCP server availability, ClawHub plugin availability.
Return: Structured JSON.
```

### YouTube Research (dispatched during PLAN)
```
Task(subagent_type: "youtube-transcript-agent")

Prompt: Search for "OpenClaw {tool_name} integration" tutorials.
Extract: Config steps, credentials needed, working prompts,
         skill examples, common pitfalls.
Save to: .claude/context/tac-scan/
```
