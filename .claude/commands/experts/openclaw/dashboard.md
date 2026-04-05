---
allowed-tools: Read, Bash
description: Get instructions to access the OpenClaw dashboard
---

# OpenClaw Expert - Dashboard Access

Provide instructions for accessing the OpenClaw dashboard and checking service health.

## Variables

SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local
GATEWAY_PORT: 18789

## Instructions

1. Read expertise.yaml to get the current instance IP.
2. OpenClaw's gateway binds to 127.0.0.1 only. Access requires an SSH tunnel.

## Access Methods

### Method 1: SSH Tunnel to Gateway Dashboard (primary)

```bash
# Establish SSH tunnel
ssh -L 18789:127.0.0.1:18789 -o ConnectTimeout=10 greg@Gregs-Mac-mini.local

# Then open in browser:
# http://localhost:18789/?token=<gateway-token>
```

To get the gateway token:
```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "cat ~/.openclaw/openclaw.json | grep -A2 '\"auth\"'"
```

### Method 2: SSH Interactive Shell

```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local
```

Then run OpenClaw commands directly:
```bash
openclaw doctor --non-interactive
openclaw channels list
ls ~/.openclaw/workspace/skills/
```

### Method 3: Quick Health Check via SSH

```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "curl -s http://127.0.0.1:18789/ 2>/dev/null | head -5 || echo 'Gateway not responding on 18789'"
```

### Method 4: Customer Portal WebSocket (if proxy deployed)

If the customer-gateway-proxy is running on port 3050:
```
ws://Gregs-Mac-mini.local:3050?token=<customer-token>
```

## Troubleshooting

### Gateway not responding?

1. Check gateway service:
```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "launchctl list | grep openclaw"
```

2. Check gateway logs:
```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "tail -20 ~/.openclaw/logs/gateway.log"
```

3. Restart the gateway:
```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "openclaw gateway restart && sleep 2 && launchctl list | grep openclaw"
```

## Report

```markdown
## OpenClaw Access

**SSH Tunnel**: ssh -L 18789:127.0.0.1:18789 -o ConnectTimeout=10 greg@Gregs-Mac-mini.local
**Dashboard**: http://localhost:18789/?token=<gateway-token>
**SSH Shell**: ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local

### Status

{Gateway running: yes/no}
{Tunnel active: yes/no}
```
