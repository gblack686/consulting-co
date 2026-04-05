# OpenClaw Installation Guide

Complete installation guide for setting up OpenClaw with Claude Code on AWS Lightsail.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] AWS Account with console access
- [ ] Anthropic account with Claude Max/Pro subscription OR API key
- [ ] Telegram account (for bot setup)
- [ ] GitHub account (optional, for repo access)
- [ ] SSH client installed locally

---

## Phase 1: AWS Infrastructure Setup

### 1.1 Create AWS Lightsail Instance

```bash
# Via AWS Console or CLI
aws lightsail create-instances \
  --instance-names openclaw-4gb \
  --availability-zone us-east-1a \
  --blueprint-id ubuntu_22_04 \
  --bundle-id medium_3_0
```

**Recommended specs:**
- **RAM**: 4GB minimum (2GB may work but can be tight)
- **OS**: Ubuntu 22.04 LTS
- **Region**: us-east-1 (or your preferred region)
- **Cost**: ~$24/month for 4GB instance

### 1.2 Configure SSH Access

```bash
# Download default Lightsail key from AWS Console
# Save to: ~/.ssh/lightsail-default.pem

# Set permissions
chmod 600 ~/.ssh/lightsail-default.pem

# Test connection
ssh -i ~/.ssh/lightsail-default.pem ubuntu@<INSTANCE_IP>
```

### 1.3 (Optional) Create Isolated AWS Sub-Account

For production deployments, create an isolated AWS Organizations sub-account:

```bash
# Create sub-account
aws organizations create-account \
  --email openclaw-prod@yourdomain.com \
  --account-name openclaw-prod

# Create budget alert ($25/month recommended)
aws budgets create-budget \
  --account-id <SUB_ACCOUNT_ID> \
  --budget file://budget.json
```

### 1.4 Store AWS Credentials on Instance

SSH into instance and configure AWS CLI:

```bash
ssh -i ~/.ssh/lightsail-default.pem ubuntu@<INSTANCE_IP>

# Configure AWS credentials
aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: Region (us-east-1)
# Enter: Output format (json)

# Verify
aws sts get-caller-identity
```

---

## Phase 2: Install OpenClaw

### 2.1 Install Node.js

```bash
# Install Node.js 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should be v22.x
npm --version
```

### 2.2 Configure npm Global Directory

```bash
# Create npm global directory (avoids sudo for global installs)
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to PATH
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2.3 Install OpenClaw

```bash
npm install -g openclaw

# Verify installation
openclaw --version
```

### 2.4 Run OpenClaw Setup

```bash
openclaw setup
```

This creates:
- `~/.openclaw/openclaw.json` - Main configuration
- `~/.openclaw/workspace/` - Agent workspace
- `~/.openclaw/agents/` - Agent state directories

---

## Phase 3: Install Claude Code CLI

### 3.1 Install Claude Code

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

### 3.2 Authenticate Claude Code

```bash
# Login (opens browser for OAuth)
claude login

# Verify authentication
claude -p "Say hello"
```

---

## Phase 4: Configure Authentication

### 4.1 Option A: Using Max/Pro Subscription (Recommended)

Generate a setup-token from your Claude subscription:

```bash
# Generate setup-token (requires interactive terminal)
claude setup-token

# This opens a browser for OAuth authorization
# After authorizing, you'll receive a token like:
# sk-ant-oat01-xxxxx...

# Save this token - you'll need it in the next step
```

Create OpenClaw environment file with the OAuth token:

```bash
# Create environment file
cat > ~/.openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-oat01-YOUR_OAUTH_TOKEN_HERE
EOF

# Verify
cat ~/.openclaw/.env
```

### 4.2 Option B: Using API Key (Pay-per-use)

If you prefer using an API key:

```bash
# Get API key from https://console.anthropic.com/
cat > ~/.openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_API_KEY_HERE
EOF
```

---

## Phase 5: Configure Gateway Service

### 5.1 Create Systemd Service

```bash
# Get OpenClaw installation path
OPENCLAW_PATH=$(which openclaw)
NODE_PATH=$(which node)

# Create service file
cat > ~/.config/systemd/user/openclaw-gateway.service << EOF
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
EnvironmentFile=$HOME/.openclaw/.env
ExecStart=$NODE_PATH $(dirname $OPENCLAW_PATH)/../lib/node_modules/openclaw/dist/index.js gateway --port 18789
Restart=always
RestartSec=5
KillMode=process
Environment=HOME=$HOME
Environment="PATH=$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
Environment=OPENCLAW_GATEWAY_PORT=18789
Environment=OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 24)

[Install]
WantedBy=default.target
EOF

# Enable lingering for user services
sudo loginctl enable-linger $USER

# Reload and start
systemctl --user daemon-reload
systemctl --user enable openclaw-gateway
systemctl --user start openclaw-gateway

# Check status
systemctl --user status openclaw-gateway
```

### 5.2 Verify Gateway is Running

```bash
# Check logs
journalctl --user -u openclaw-gateway -f

# Should see:
# [gateway] listening on ws://127.0.0.1:18789
# [heartbeat] started
```

---

## Phase 6: Configure Telegram Channel

### 6.1 Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "My OpenClaw Bot")
4. Choose a username (must end in `bot`, e.g., `myopenclaw_bot`)
5. Save the bot token (format: `1234567890:AAHxxxxx...`)

### 6.2 Enable Telegram Plugin

```bash
# Enable the Telegram plugin
openclaw plugins enable telegram

# Add Telegram channel with your bot token
openclaw channels add \
  --channel telegram \
  --token "YOUR_BOT_TOKEN_FROM_BOTFATHER" \
  --name "OpenClaw Bot"

# Restart gateway to apply changes
systemctl --user restart openclaw-gateway

# Verify channel is configured
openclaw channels list
```

### 6.3 Approve Your Telegram User

When you first message the bot, you'll receive a pairing code:

```
Pairing code: XXXXXXXX
Ask the bot owner to approve with:
openclaw pairing approve telegram <code>
```

Run the approval command:

```bash
openclaw pairing approve telegram XXXXXXXX
```

---

## Phase 7: Validation Checks

### 7.1 Run OpenClaw Doctor

```bash
openclaw doctor --non-interactive
```

**Expected output:**
- Security: No warnings
- Skills: Some eligible (missing requirements is OK)
- Plugins: Telegram loaded

### 7.2 Verify Model Status

```bash
openclaw models status
```

**Expected output:**
```
Default       : anthropic/claude-opus-4-5
Auth overview
- anthropic effective=env:sk-ant-o...xxxxx | source=env: ANTHROPIC_API_KEY
```

### 7.3 Verify Channels

```bash
openclaw channels list
```

**Expected output:**
```
Chat channels:
- Telegram default (OpenClaw Bot): configured, token=config, enabled
```

### 7.4 Check Gateway Logs

```bash
journalctl --user -u openclaw-gateway --no-pager -n 20
```

**Look for:**
- `[gateway] listening on ws://127.0.0.1:18789`
- `[telegram] [default] starting provider (@your_bot_name)`
- No authentication errors

### 7.5 Test Telegram Bot

1. Open Telegram
2. Search for your bot (e.g., @myopenclaw_bot)
3. Send: "Hello, please confirm you are working"
4. Bot should respond with Claude-generated text

---

## Phase 8: Agent Configuration

Personalize your OpenClaw agent with a name, identity, and personality.

### 8.1 Set Agent Identity

```bash
# Set agent name and emoji
openclaw agents set-identity --name "Gelby" --emoji "🤖" --theme "helpful AI assistant"

# Or set individually
openclaw agents set-identity --name "Gelby"
openclaw agents set-identity --emoji "🦾"
openclaw agents set-identity --theme "A knowledgeable and friendly coding assistant"
```

**Identity options:**
| Option | Description | Example |
|--------|-------------|---------|
| `--name` | Agent display name | "Gelby", "Assistant" |
| `--emoji` | Agent emoji/avatar | "🤖", "🦾", "🧠" |
| `--theme` | Brief personality description | "helpful coding assistant" |
| `--avatar` | URL to avatar image | "https://example.com/avatar.png" |

### 8.2 Create IDENTITY.md (Optional)

For more detailed personality configuration, create an IDENTITY.md file in your workspace:

```bash
cat > ~/.openclaw/workspace/IDENTITY.md << 'EOF'
# Agent Identity

## Name
Gelby

## Personality
- Friendly and approachable
- Technical but explains concepts clearly
- Proactive in suggesting improvements
- Cautious with destructive operations

## Communication Style
- Concise responses unless detail is requested
- Uses code examples when helpful
- Asks clarifying questions when requirements are ambiguous

## Expertise Areas
- Full-stack development
- Cloud infrastructure (AWS, GCP)
- Python, TypeScript, Go
- DevOps and CI/CD
EOF
```

### 8.3 Workspace Bootstrap Files

OpenClaw looks for these files in `~/.openclaw/workspace/`:

| File | Purpose |
|------|---------|
| `IDENTITY.md` | Agent personality and communication style |
| `AGENTS.md` | Multi-agent configuration |
| `SOUL.md` | Core values and decision-making principles |
| `TOOLS.md` | Custom tool definitions |
| `CLAUDE.md` | Claude-specific instructions (similar to Claude Code) |

### 8.4 Verify Agent Configuration

```bash
# Check current agent identity
openclaw agents list

# View agent details
openclaw agents show main
```

---

## Phase 9: Dashboard Access (Optional)

### 9.1 Access via SSH Tunnel

The dashboard runs on localhost only. Access via SSH tunnel:

```bash
# From your local machine
ssh -L 18789:127.0.0.1:18789 -i ~/.ssh/lightsail-default.pem ubuntu@<INSTANCE_IP>

# Then open in browser:
# http://localhost:18789/?token=YOUR_GATEWAY_TOKEN
```

### 9.2 Get Gateway Token

```bash
# On the instance
cat ~/.openclaw/openclaw.json | grep -A2 '"auth"'
```

---

## Troubleshooting

### Authentication Errors

**"Missing auth" in models status:**
```bash
# Verify env file exists and has correct token
cat ~/.openclaw/.env

# Verify systemd service loads env file
grep EnvironmentFile ~/.config/systemd/user/openclaw-gateway.service

# Restart after changes
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway
```

### Telegram Bot Not Responding

```bash
# Check if Telegram plugin is enabled
openclaw plugins list | grep telegram

# Check channel status
openclaw channels list

# Check gateway logs for errors
journalctl --user -u openclaw-gateway --no-pager -n 50 | grep -i telegram
```

### Gateway Won't Start

```bash
# Check for port conflicts
ss -tlnp | grep 18789

# Check service status
systemctl --user status openclaw-gateway

# View full logs
journalctl --user -u openclaw-gateway --no-pager
```

### Token Refresh (OAuth)

OAuth tokens expire. To refresh:

```bash
# Re-run setup-token
claude setup-token

# Update ~/.openclaw/.env with new token
# Restart gateway
systemctl --user restart openclaw-gateway
```

---

## Quick Reference

### Key Paths

| Path | Description |
|------|-------------|
| `~/.openclaw/openclaw.json` | Main configuration |
| `~/.openclaw/.env` | Environment variables (API keys) |
| `~/.openclaw/agents/main/` | Default agent state |
| `~/.config/systemd/user/openclaw-gateway.service` | Systemd service |
| `~/.claude/.credentials.json` | Claude Code OAuth credentials |

### Key Commands

| Command | Description |
|---------|-------------|
| `openclaw doctor` | Health check |
| `openclaw models status` | Check authentication |
| `openclaw channels list` | List configured channels |
| `openclaw plugins list` | List plugins |
| `systemctl --user restart openclaw-gateway` | Restart gateway |
| `journalctl --user -u openclaw-gateway -f` | View live logs |

### Credentials Needed

| Credential | Source | Used For |
|------------|--------|----------|
| AWS Access Key | AWS Console | Instance management |
| SSH Key | Lightsail Console | SSH access |
| Anthropic OAuth Token | `claude setup-token` | Claude API (Max subscription) |
| Anthropic API Key | console.anthropic.com | Claude API (pay-per-use) |
| Telegram Bot Token | @BotFather | Telegram channel |
| GitHub PAT | GitHub Settings | Repository access |
| Gateway Token | Auto-generated | Dashboard access |

---

## Support

- OpenClaw Docs: https://docs.openclaw.ai
- Claude Code Docs: https://docs.anthropic.com/claude-code
- GitHub Issues: https://github.com/openclaw/openclaw/issues

---

*Last updated: 2026-02-03*
