# OpenClaw Mac Mini Install Guide

Complete setup for deploying an OpenClaw workspace on a Mac Mini (or any macOS machine). Adapts the Lightsail guide for macOS — uses Homebrew, launchd, and native tools.

---

## Prerequisites

- [ ] Mac Mini (M1/M2/M4 — any Apple Silicon)
- [ ] macOS 14+ (Sonoma or later)
- [ ] Admin account access
- [ ] OpenRouter API key (https://openrouter.ai/keys)
- [ ] GitHub PAT with repo read access
- [ ] Telegram account (for bot channel)
- [ ] Discord bot token (optional, for Discord channel)

---

## Phase 1: System Dependencies

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js 22+ and just command runner
brew install node@22 just

# Verify
node --version   # v22.x
npm --version
just --version

# Install pnpm (needed if building from fork)
npm install -g pnpm
```

---

## Phase 2: Install OpenClaw

### Option A: npm install (quickest)

```bash
npm install -g openclaw@latest
openclaw --version
```

### Option B: Build from GB Automation fork (branded UI)

```bash
git clone https://github.com/gblack686/openclaw.git ~/.gb-openclaw-build
cd ~/.gb-openclaw-build
pnpm install --frozen-lockfile
pnpm build
pnpm ui:build
npm install -g .
openclaw --version
```

---

## Phase 3: Onboard

```bash
openclaw onboard
```

This creates:
- `~/.openclaw/openclaw.json` — main config
- `~/.openclaw/workspace/` — agent workspace
- `~/.openclaw/agents/` — agent state

---

## Phase 4: Clone Client Workspace

For greg-trading:
```bash
git clone https://github.com/gblack686/openclaw-greg-trading ~/openclaw-greg-trading
cd ~/openclaw-greg-trading
```

Or for a new client workspace from the consulting-intake template:
```bash
# Copy template files and fill placeholders
cp -r /path/to/consulting-co/.claude/skills/consulting-intake/templates/skills/ ~/.openclaw/workspace/skills/
```

---

## Phase 5: Deploy Workspace

Using the justfile (if cloned from a client repo):
```bash
cd ~/openclaw-greg-trading
just setup    # deploy + skills + cron + restart + verify
```

Or manually:
```bash
# Copy workspace files
cp ~/openclaw-greg-trading/workspace/*.md ~/.openclaw/workspace/
cp ~/openclaw-greg-trading/workspace/openclaw.json ~/.openclaw/

# Copy skills
mkdir -p ~/.openclaw/workspace/skills
cp -r ~/openclaw-greg-trading/workspace/skills/* ~/.openclaw/workspace/skills/

# Copy domain-discovery skill (fundamental module)
cp -r /path/to/templates/skills/domain-discovery ~/.openclaw/workspace/skills/
```

---

## Phase 6: Set Secrets

```bash
# Primary LLM provider
openclaw secrets set OPENROUTER_API_KEY '<your key>'

# GitHub access (for domain-discovery skill)
openclaw secrets set GITHUB_TOKEN '<PAT with repo read>'

# Communication channels
openclaw secrets set TELEGRAM_BOT_TOKEN '<from @BotFather>'
openclaw secrets set DISCORD_BOT_TOKEN '<from discord dev portal>'  # optional

# Domain-specific (vary by client)
# openclaw secrets set HYPERLIQUID_API_KEY '<key>'
# openclaw secrets set YOUTUBE_API_KEY '<key>'
```

---

## Phase 6b: Exec Approvals — Headless Fix (CRITICAL for Telegram/Discord)

**This is the #1 setup mistake.** OpenClaw ships with `askFallback: "deny"` — meaning when there's no UI (always true on Telegram/Discord), all exec/bash commands are silently blocked. Fix this before testing anything.

```bash
# Write the correct exec-approvals.json
python3 -c "
import json, os
path = os.path.expanduser('~/.openclaw/exec-approvals.json')
c = json.load(open(path)) if os.path.exists(path) else {'version': 1, 'socket': {'path': os.path.expanduser('~/.openclaw/exec-approvals.sock'), 'token': 'change-me'}}
c['defaults'] = {'security': 'full', 'ask': 'off', 'askFallback': 'full', 'autoAllowSkills': True}
c['agents'] = {'main': {'security': 'full', 'ask': 'off', 'askFallback': 'full', 'autoAllowSkills': True}}
json.dump(c, open(path, 'w'), indent=2)
print('Done:', json.dumps(c, indent=2))
"

# Hard restart the gateway (force-kills and reloads the file)
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
sleep 4
curl -s http://localhost:18789/health  # should return {"ok":true,"status":"live"}
```

**Field values that matter:**

| Field | Correct Value | Wrong Value | Effect of Wrong |
|-------|--------------|-------------|-----------------|
| `security` | `"full"` | `"off"` / `"none"` | Invalid — silently ignored, falls back to block |
| `ask` | `"off"` | `"on-miss"` | Prompts for UI approval — unavailable on Telegram |
| `askFallback` | `"full"` | `"deny"` (default!) | **Blocks ALL exec when headless** |
| `autoAllowSkills` | `true` | `false` | Skills can't run their own executables |

**Restart command for Mac Mini (use this, not `openclaw gateway restart`):**
```bash
# Soft restart (may not reload exec-approvals.json):
launchctl kickstart gui/$(id -u)/ai.openclaw.gateway

# Hard restart (force-kills first — always use this after editing exec-approvals.json):
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
```

---

## Phase 6c: Audio Transcription — Telegram Voice Notes

**Telegram voice notes are NOT auto-transcribed** in OpenClaw 2026.3.x (known bug, open issue #7899 — `applyMediaUnderstanding` never called in the Telegram plugin). Config alone won't fix it. Use the OpenAI Whisper workaround below.

### Add to openclaw.json

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        maxBytes: 20971520,     // 20 MB
        echoTranscript: false,  // set true to confirm transcript back to user
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
        ]
      }
    }
  },
  env: {
    OPENAI_API_KEY: "sk-proj-..."   // from gbautomation/core/openai-api-key in AWS
  }
}
```

### Inject OPENAI_API_KEY from AWS

```bash
OPENAI_KEY=$(aws secretsmanager get-secret-value \
  --secret-id "gbautomation/core/openai-api-key" \
  --query SecretString --output text)

python3 -c "
import json
path = '/Users/greg/.openclaw/openclaw.json'
c = json.load(open(path))
c['env']['OPENAI_API_KEY'] = '$OPENAI_KEY'
json.dump(c, open(path, 'w'), indent=2)
print('Injected OPENAI_API_KEY')
"
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
```

### Manual Transcription Skill (workaround for Telegram bug)

Until the bug is fixed, Sebastian can transcribe a voice note on demand. Tell him:
> "Transcribe the voice note I just sent"

He will:
1. Download the OGG attachment via Telegram file API
2. Convert to WAV via ffmpeg: `ffmpeg -i input.ogg output.wav`
3. POST to OpenAI Whisper: `POST https://api.openai.com/v1/audio/transcriptions`
4. Return the transcript and act on it

Requires `ffmpeg` installed:
```bash
brew install ffmpeg
```

---

## Phase 7: Configure Gateway as launchd Service

On macOS, use launchd instead of systemd. This ensures OpenClaw starts on boot and restarts on crash.

```bash
# Find openclaw path
OPENCLAW_PATH=$(which openclaw)

# Create launchd plist
cat > ~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gbautomation.openclaw-gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>$OPENCLAW_PATH</string>
        <string>gateway</string>
        <string>--port</string>
        <string>18789</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.openclaw/logs/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.openclaw/logs/gateway.err</string>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p ~/.openclaw/logs

# Load the service
launchctl load ~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist

# Verify it's running
launchctl list | grep openclaw
curl -s http://localhost:18789/health || echo "Gateway starting..."
```

### Managing the service

```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist

# Start
launchctl load ~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist

# Restart (stop then start)
launchctl unload ~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist
launchctl load ~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist

# View logs
tail -f ~/.openclaw/logs/gateway.log
```

---

## Phase 8: Configure Channels

### Telegram (recommended first)

1. Message @BotFather on Telegram → `/newbot` → save token
2. Set the token: `openclaw secrets set TELEGRAM_BOT_TOKEN '<token>'`
3. Enable: `openclaw plugins enable telegram`
4. Restart gateway
5. Message your bot → get pairing code → `openclaw pairing approve telegram <CODE>`

### Discord (optional, for channel-based workflows)

1. Create bot at discord.com/developers → save token
2. Set the token: `openclaw secrets set DISCORD_BOT_TOKEN '<token>'`
3. Enable: `openclaw plugins enable discord`
4. Invite bot to your server with message read/write permissions
5. Restart gateway

---

## Phase 9: Verify

```bash
# Health check
openclaw doctor --non-interactive

# Check models
openclaw models status

# Check channels
openclaw channels list

# List skills
openclaw skills list

# Check cron
openclaw cron list

# Dashboard (local access)
open http://localhost:18789/openclaw/
```

---

## Phase 10: Bootstrap — Domain Discovery

After everything is running, kick off the self-organizing workflow:

```
Message your bot on Telegram:

"Hey, I've given you access to my GitHub repos via GITHUB_TOKEN.
Scan these orgs and repos:
- github.com/gblack686 (personal repos)
- github.com/gblack686-openclaw (TAC examples org)

Figure out what I'm working on. Group everything into domains.
For each domain, tell me:
1. What repos belong to it
2. What's the current status (active/warm/cold)
3. What's the goal
4. What's missing
5. Give me 3 reverse prompts to build deeper skills

Then help me archive this into my Obsidian vault."
```

See `bootstrap-prompts.md` for the full set of meta-prompts to run after install.

---

## Quick Reference

### Key Paths (macOS)

| Path | Description |
|------|-------------|
| `~/.openclaw/openclaw.json` | Main configuration |
| `~/.openclaw/workspace/` | Agent workspace (SOUL.md, etc.) |
| `~/.openclaw/workspace/skills/` | Installed skills |
| `~/.openclaw/agents/` | Agent state |
| `~/.openclaw/logs/` | Gateway logs |
| `~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist` | Service definition |

### Key Commands

| Command | Description |
|---------|-------------|
| `openclaw doctor` | Health check |
| `openclaw models status` | Auth + model status |
| `openclaw channels list` | Channel status |
| `openclaw skills list` | Installed skills |
| `openclaw cron list` | Scheduled jobs |
| `launchctl list \| grep openclaw` | Service status |
| `tail -f ~/.openclaw/logs/gateway.log` | Live logs |

### Differences from Lightsail

| Feature | Lightsail (Linux) | Mac Mini (macOS) |
|---------|-------------------|------------------|
| Package manager | apt | Homebrew |
| Service manager | systemd | launchd |
| Service file | `~/.config/systemd/user/openclaw-gateway.service` | `~/Library/LaunchAgents/com.gbautomation.openclaw-gateway.plist` |
| Restart | `systemctl --user restart openclaw-gateway` | unload + load plist |
| Logs | `journalctl --user -u openclaw-gateway -f` | `tail -f ~/.openclaw/logs/gateway.log` |
| SSH access | SSH from anywhere | Screen Sharing / SSH / local |
| Always-on | Yes (cloud) | Yes (if plugged in, no sleep) |

### Preventing Sleep (Mac Mini as server)

```bash
# Prevent sleep when plugged in (important for always-on agent)
sudo pmset -a disablesleep 1
sudo pmset -a sleep 0
sudo pmset -a displaysleep 0
sudo pmset -a disksleep 0
sudo pmset -a standby 0
sudo pmset -a autopoweroff 0
sudo pmset -a autorestart 1

# Verify
pmset -g | grep sleep
```

---

## Phase 11: Mac Mini Agent — GUI & Terminal Automation (Optional)

Install IndyDevDan's [mac-mini-agent](https://github.com/disler/mac-mini-agent) to give your OpenClaw agent full macOS GUI and terminal control. This turns the Mac Mini from a headless agent into one that can see screens, click buttons, type text, and orchestrate multiple terminal sessions.

### What You Get

| App | Language | Purpose |
|-----|----------|---------|
| **Steer** | Swift | GUI automation — screenshots, click, type, OCR, window management (14 commands) |
| **Drive** | Python | Terminal automation via tmux — run commands, poll output, fanout (6 commands) |
| **Listen** | Python/FastAPI | HTTP job server on port 7600 — fire-and-forget agent tasks |
| **Direct** | Python CLI | Remote client to submit/monitor jobs from another machine |

### Prerequisites

macOS permissions (must be set via System Settings GUI):

| Permission | Path | Why |
|------------|------|-----|
| Accessibility | Privacy & Security → Accessibility → Terminal | Steer clicks, types, reads UI |
| Screen Recording | Privacy & Security → Screen Recording → Terminal | Steer screenshots and OCR |
| Full Disk Access | Privacy & Security → Full Disk Access → Terminal | systemsetup + broad file access |

### Install

```bash
# Clone mac-mini-agent
git clone https://github.com/disler/mac-mini-agent ~/mac-mini-agent
cd ~/mac-mini-agent

# Install system deps
brew install tmux uv yq

# Build Steer (Swift CLI)
cd apps/steer && swift build -c release
sudo cp .build/release/steer /usr/local/bin/
cd ~/mac-mini-agent

# Setup Python apps (Drive, Listen, Direct)
cd apps/drive && uv sync && cd ~/mac-mini-agent
cd apps/listen && uv sync && cd ~/mac-mini-agent
cd apps/direct && uv sync && cd ~/mac-mini-agent

# Verify
steer --help
```

### Start the Job Server

```bash
cd ~/mac-mini-agent
just listen   # Starts on port 7600
```

Or as a launchd service (always-on):

```bash
cat > ~/Library/LaunchAgents/com.gbautomation.mac-mini-agent-listen.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gbautomation.mac-mini-agent-listen</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/just</string>
        <string>listen</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$HOME/mac-mini-agent</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.openclaw/logs/mac-mini-agent.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.openclaw/logs/mac-mini-agent.err</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.gbautomation.mac-mini-agent-listen.plist
```

### Send Jobs Remotely

From your primary machine (Windows/Mac):

```bash
# Submit a job
curl -X POST http://192.168.x.x:7600/job \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Open Safari, navigate to news.ycombinator.com, read top 3 headlines"}'

# Check job status
curl http://192.168.x.x:7600/job/<job_id>

# List all jobs
curl http://192.168.x.x:7600/jobs
```

Or using the Direct CLI:
```bash
cd ~/mac-mini-agent
just send "Open Safari and take a screenshot of the homepage"
just jobs          # List all
just job <id>      # Check specific
just latest 3      # Last 3 with details
just stop <id>     # Kill running job
```

### Key Patterns

**Observe-Act-Verify Loop** (Steer):
```
1. steer see --app Safari --json   → screenshot + accessibility tree
2. Parse JSON, identify target element
3. steer click --id B5              → ONE action
4. steer see --app Safari --json   → verify result
5. Repeat
```

**OCR Equalizer** — Native apps (Safari, Finder) return accessibility trees. Electron apps (VS Code, Slack, Notion) return empty trees. Use `steer ocr --store` to make all text clickable.

**Sentinel Protocol** (Drive):
```bash
drive run <session> "<command>"
# Wraps with: echo __START_<token> ; <cmd> ; echo __DONE_<token>:$?
# Deterministic completion detection + exit code capture
```

### OpenClaw + Mac Mini Agent Architecture

```
[Remote Machine]                     [Mac Mini]
                                     ┌─────────────────────────────┐
just send "<prompt>"                 │  Listen (port 7600)         │
  │                                  │    ├─ Spawns Claude Code    │
  ├─ POST /job ─────────────────────▶│    │  worker per job        │
  │                                  │    │                        │
  │                                  │  OpenClaw (port 18789)      │
  │                                  │    ├─ Skills + Channels     │
  │                                  │    ├─ Heartbeat + Cron      │
  │                                  │    └─ Telegram/Discord      │
  │                                  │                             │
  │                                  │  Steer (GUI control)        │
  │                                  │    ├─ Safari, Notion, etc.  │
  │                                  │    └─ OCR for Electron apps │
  │                                  │                             │
  │                                  │  Drive (terminal control)   │
  │                                  │    ├─ tmux sessions         │
  │                                  │    └─ Parallel agents       │
  │                                  └─────────────────────────────┘
```

### Verify Mac Mini Agent

```bash
# Steer
steer see --json | head -20
steer apps

# Drive
drive session create test-session
drive run test-session "echo hello"
drive session kill test-session

# Listen
curl -s http://localhost:7600/jobs

# Full test
just steer1-cc   # Research MacBooks with Claude Code
```

---

*Template by GBAutomation — based on INSTALLATION_GUIDE.md + greg-trading justfile + Alex Finn's OpenClaw patterns + IndyDevDan's mac-mini-agent*
