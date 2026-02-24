---
name: setup-openclaw
description: "Infrastructure: Setup OpenClaw - Install OpenClaw on Greg's Windows laptop, deploy workspace files, configure secrets, and verify the gateway is running"
---

# Setup OpenClaw — Greg Trading

## Purpose

Bootstrap OpenClaw on Greg's local Windows machine. Installs the CLI, deploys the trading workspace from the GitHub repo, sets all trading API secrets, and verifies the gateway is healthy.

## Variables

- `host_type`: `local` (Greg's Windows laptop)
- `repo_url`: `https://github.com/gblack686/openclaw-greg-trading`
- `openrouter_api_key`: OpenRouter API key (get from openrouter.ai/keys)

## Instructions

- IMPORTANT: Never hardcode secrets — use `openclaw secrets set` for all API keys
- IMPORTANT: Verify gateway is running before declaring success (`openclaw doctor --non-interactive`)
- Greg is on Windows — use PowerShell for install, then use openclaw CLI from there
- If PATH issues arise after install, restart the terminal and retry

## Workflow

### Step 1: Install OpenClaw (Windows)

Open PowerShell as Administrator:
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

Or via npm (if Node.js 22+ is installed):
```powershell
npm install -g openclaw@latest
openclaw --version
```

### Step 2: Onboard

```bash
openclaw onboard --non-interactive --accept-risk --install-daemon
```

### Step 3: Clone Workspace Repo

```bash
git clone https://github.com/gblack686/openclaw-greg-trading ~/openclaw-greg-trading
```

### Step 4: Deploy Workspace Files

```bash
cp -r ~/openclaw-greg-trading/workspace/* ~/.openclaw/
mkdir -p ~/.openclaw/skills
cp -r ~/openclaw-greg-trading/workspace/skills/* ~/.openclaw/skills/
```

### Step 5: Set Secrets

Set all required API keys:

```bash
# Primary LLM (OpenRouter)
openclaw secrets set OPENROUTER_API_KEY '<your openrouter api key>'

# Trading
openclaw secrets set HYPERLIQUID_API_KEY '<from hyperliquid settings>'
openclaw secrets set HYPERLIQUID_SECRET '<from hyperliquid settings>'

# Communication
openclaw secrets set TELEGRAM_BOT_TOKEN '<from @BotFather>'

# Data sources
openclaw secrets set DISCORD_BOT_TOKEN '<from discord developer portal>'
openclaw secrets set YOUTUBE_API_KEY '<from google cloud console>'
```

### Step 6: Restart Gateway

```bash
openclaw gateway restart
# or on Windows:
systemctl --user restart openclaw-gateway
```

### Step 7: Verify

```bash
openclaw doctor --non-interactive
openclaw skills list
openclaw cron list
```

### Step 8: Access Dashboard

Open http://localhost:18789/ in your browser.

## Report

```
## OpenClaw Setup Report — Greg Trading

**Status**: {Success | Failed}

### Steps Completed
- [x] OpenClaw installed (version: {version})
- [x] Onboarding complete
- [x] Workspace files deployed from openclaw-greg-trading repo
- [x] Secrets set: OPENROUTER_API_KEY, HYPERLIQUID_API_KEY, HYPERLIQUID_SECRET, TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN, YOUTUBE_API_KEY
- [x] Gateway running
- [x] Doctor: {score or issues}

### Skills Loaded
{output of openclaw skills list}

### Issues
{any errors or warnings, or "None"}

### Next Steps
- Open dashboard: http://localhost:18789/
- Send a test message via Telegram
- Run scrape-discord to verify trading signal pipeline
```
