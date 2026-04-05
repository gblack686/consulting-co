---
allowed-tools: Read, Bash, AskUserQuestion
description: Interactive OpenClaw installation wizard
argument-hint: [new|validate]
---

# OpenClaw Expert - Installation Wizard

Interactive installation wizard for deploying OpenClaw on the Mac Mini.

## Variables

MODE: $ARGUMENTS
SSH: SSH key auth configured (ed25519, no passphrase)
INSTALLATION_GUIDE: .claude/commands/experts/openclaw/INSTALLATION_GUIDE.md
EXPERTISE_PATH: .claude/commands/experts/openclaw/expertise.yaml

## Instructions

Guide the user through OpenClaw deployment on the Mac Mini.

### Mode: new (default)
Deploy a new OpenClaw instance on the Mac Mini.

### Mode: validate
Run validation checks on an existing OpenClaw deployment.

## Deployment on Mac Mini

### Prerequisites
- SSH key auth configured (ed25519, no passphrase) to greg@Gregs-Mac-mini.local
- Anthropic account (Max/Pro subscription or API key)
- Node.js 22.x (installed via Homebrew)

### Step 1: Verify Mac Mini Access

```bash
# Test SSH connection
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local "echo 'Connected' && uname -a"
```

Specs:
- **Host**: Gregs-Mac-mini.local (192.168.4.94)
- **OS**: macOS
- **Cost**: $0/month (local hardware)

### Step 2: Configure SSH Access

```bash
# SSH key auth is already configured (ed25519, no passphrase)
# Test connection
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local
```

### Step 3: Install on Mac Mini

SSH into the Mac Mini and run:

```bash
# Node.js should already be installed via Homebrew
node --version

# Install OpenClaw
npm install -g openclaw
openclaw --version

# Run setup
openclaw setup

# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code
claude login
```

### Step 4: Configure Authentication

```bash
# Option A: Max/Pro subscription
claude setup-token
# Copy the token, then:
cat > ~/.openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-oat01-YOUR_TOKEN_HERE
EOF

# Option B: API key
cat > ~/.openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
EOF

chmod 600 ~/.openclaw/.env
```

### Step 5: Start Gateway Service

```bash
# Start the gateway
openclaw gateway restart

# Verify it is running
launchctl list | grep openclaw

# Check logs
tail -f ~/.openclaw/logs/gateway.log
```

### Step 6: Verify Deployment

```bash
# Doctor check
openclaw doctor --non-interactive

# Model auth
openclaw models status

# Gateway logs
tail -10 ~/.openclaw/logs/gateway.log
```

### Step 7: Update expertise.yaml

After successful deployment, update the instance IP in expertise.yaml:
- Set `infrastructure.our_instance.instance_ip` to the new IP
- Update the `note` field to reflect the active instance

### Full Reference

For detailed step-by-step instructions including Telegram setup, agent configuration,
and dashboard access, read INSTALLATION_GUIDE.md:

```
.claude/commands/experts/openclaw/INSTALLATION_GUIDE.md
```

## Validation (existing instance)

Read expertise.yaml to get the current instance IP. If "TBD", inform user no instance exists.

```bash
INSTANCE_IP=<from expertise.yaml>

ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local << 'EOF'
export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:$PATH"
echo "=== OpenClaw Version ==="
openclaw --version 2>&1
echo "=== Services ==="
launchctl list | grep openclaw
echo "=== Doctor ==="
openclaw doctor --non-interactive 2>&1 | tail -5
echo "=== Skills ==="
ls ~/.openclaw/workspace/skills/ 2>/dev/null
echo "=== Gateway Logs ==="
tail -5 ~/.openclaw/logs/gateway.log
EOF
```

## Cost

| Component | Cost |
|-----------|------|
| Mac Mini (local) | $0/month |
| Electricity | ~$5/month |
| **Total** | **~$5/month** |
