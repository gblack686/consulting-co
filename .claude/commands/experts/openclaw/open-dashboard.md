---
allowed-tools: Bash, Read
description: Open SSH tunnel to OpenClaw dashboard and launch in browser
---

# OpenClaw Expert - Open Dashboard

Establish an SSH tunnel to the OpenClaw gateway and open the dashboard in a browser.

## Variables

SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local
GATEWAY_PORT: 18789

## Instructions

1. Read expertise.yaml to get the current instance IP.
2. If IP is "TBD", inform the user and stop.

## Execution

### Step 1: Check for Existing Tunnel

```bash
existing=$(netstat -an 2>/dev/null | grep "127.0.0.1:18789" | grep LISTEN || ss -tln 2>/dev/null | grep ":18789" || echo "")

if [ -n "$existing" ]; then
  echo "Tunnel already active on port 18789"
else
  echo "Starting SSH tunnel to OpenClaw gateway..."
  ssh -f -N -L 18789:127.0.0.1:18789 -o ConnectTimeout=10 greg@Gregs-Mac-mini.local
  sleep 2
  echo "SSH tunnel started"
fi
```

### Step 2: Open in Browser

```bash
echo "Opening dashboard in browser..."
start http://localhost:18789/ 2>/dev/null || open http://localhost:18789/ 2>/dev/null || xdg-open http://localhost:18789/ 2>/dev/null || echo "Open http://localhost:18789/ in your browser"

echo ""
echo "Dashboard: http://localhost:18789/?token=<gateway-token>"
echo ""
echo "To stop the tunnel later: pkill -f 'ssh.*18789.*Gregs-Mac-mini'"
```

### Step 3: Get Gateway Token (if needed)

```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "cat ~/.openclaw/openclaw.json | grep -A2 '\"auth\"'"
```

### Quick Service Check (no tunnel needed)

```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "launchctl list | grep openclaw && \
   echo '' && \
   openclaw doctor --non-interactive 2>&1 | tail -5"
```
