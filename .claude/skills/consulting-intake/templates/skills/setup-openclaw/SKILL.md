---
name: setup-openclaw
description: "Infrastructure: Setup OpenClaw - Install OpenClaw, deploy workspace files, configure secrets, and verify the gateway is running"
---

# Setup OpenClaw

## Purpose

Bootstrap a fresh OpenClaw installation on a new host. Installs the CLI, deploys the workspace package from the client GitHub repo, sets all secrets, and verifies the gateway is healthy.

## Variables

- `host_type`: `local` (Windows/Mac running OpenClaw locally) or `remote` (Linux VPS/Lightsail)
- `host_ip`: IP address if remote (e.g. `18.234.126.236`)
- `ssh_key`: Path to SSH key if remote (e.g. `~/.ssh/lightsail-default.pem`)
- `repo_url`: GitHub repo URL with the workspace package (e.g. `https://github.com/gblack686/openclaw-greg-trading`)
- `openrouter_api_key`: OpenRouter API key to set as the primary LLM provider

## Instructions

- IMPORTANT: Never hardcode secrets — use `openclaw secrets set` for all API keys
- IMPORTANT: Verify gateway is running before declaring success (`openclaw doctor --non-interactive`)
- If installation fails with PATH errors, source ~/.bashrc and retry
- For remote hosts, all commands run via SSH unless noted otherwise
- If the host already has OpenClaw installed, skip Step 1 and go straight to Step 3

## Workflow

### Step 1: Install OpenClaw

**Local (Mac/Linux):**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
source ~/.bashrc
openclaw --version
```

**Local (Windows):**
```powershell
# Run in PowerShell as Administrator
iwr -useb https://openclaw.ai/install.ps1 | iex
```

**Remote (SSH):**
```bash
ssh -i {ssh_key} ubuntu@{host_ip} "curl -fsSL https://openclaw.ai/install.sh | bash && source ~/.bashrc && openclaw --version"
```

### Step 2: Onboard

Run the OpenClaw onboarding wizard to initialize the gateway and install the system service:

**Local:**
```bash
openclaw onboard --non-interactive --accept-risk --install-daemon
```

**Remote:**
```bash
ssh -i {ssh_key} ubuntu@{host_ip} "openclaw onboard --non-interactive --accept-risk --install-daemon"
```

### Step 3: Clone Workspace Repo

```bash
# Local
git clone {repo_url} ~/openclaw-workspace

# Remote
ssh -i {ssh_key} ubuntu@{host_ip} "git clone {repo_url} ~/openclaw-workspace"
```

### Step 4: Deploy Workspace Files

Copy workspace files to the OpenClaw config directory:

**Local:**
```bash
cp -r ~/openclaw-workspace/workspace/* ~/.openclaw/workspace/
cp -r ~/openclaw-workspace/workspace/skills/* ~/.openclaw/workspace/skills/ 2>/dev/null || true
```

**Remote:**
```bash
ssh -i {ssh_key} ubuntu@{host_ip} "cp -r ~/openclaw-workspace/workspace/* ~/.openclaw/ && mkdir -p ~/.openclaw/skills && cp -r ~/openclaw-workspace/workspace/skills/* ~/.openclaw/skills/ 2>/dev/null || true"
```

Or use SCP:
```bash
scp -r -i {ssh_key} workspace/* ubuntu@{host_ip}:~/.openclaw/
```

### Step 5: Set Secrets

Set all required API keys via the OpenClaw secrets store. Run one at a time:

```bash
# Primary LLM provider (OpenRouter)
openclaw secrets set OPENROUTER_API_KEY '{openrouter_api_key}'

# Additional secrets — prompt user for each value
openclaw secrets set TELEGRAM_BOT_TOKEN '<ask client>'
openclaw secrets set DISCORD_BOT_TOKEN '<ask client>'
# ... add any other secrets from TOOLS.md
```

**Remote:**
```bash
ssh -i {ssh_key} ubuntu@{host_ip} "openclaw secrets set OPENROUTER_API_KEY '{openrouter_api_key}'"
```

### Step 6: Restart Gateway

```bash
# Local (Linux/Mac systemd)
systemctl --user restart openclaw-gateway

# Local (Windows)
openclaw gateway restart

# Remote
ssh -i {ssh_key} ubuntu@{host_ip} "systemctl --user restart openclaw-gateway"
```

### Step 7: Verify

```bash
# Run health check
openclaw doctor --non-interactive

# Check gateway status
systemctl --user status openclaw-gateway

# List loaded skills
openclaw skills list

# List cron jobs
openclaw cron list
```

**Remote:**
```bash
ssh -i {ssh_key} ubuntu@{host_ip} "openclaw doctor --non-interactive && openclaw skills list"
```

### Step 8: Access Dashboard

**Local:** Open http://localhost:18789/

**Remote (SSH tunnel):**
```bash
ssh -L 18789:127.0.0.1:18789 -i {ssh_key} ubuntu@{host_ip} -N &
# Then open http://localhost:18789/
```

## Report

```
## OpenClaw Setup Report

**Host**: {local | remote @ host_ip}
**Status**: {Success | Failed}

### Steps Completed
- [x] OpenClaw installed (version: {version})
- [x] Onboarding complete
- [x] Workspace files deployed
- [x] Secrets set: {list of secret names, NOT values}
- [x] Gateway running
- [x] Doctor: {score or issues}

### Skills Loaded
{output of openclaw skills list}

### Cron Jobs
{output of openclaw cron list}

### Issues
{any errors or warnings, or "None"}

### Next Steps
- Open the dashboard: http://localhost:18789/ (or via SSH tunnel)
- Send a test message via {channel_type}
- Run the morning-brief skill to verify end-to-end
```
