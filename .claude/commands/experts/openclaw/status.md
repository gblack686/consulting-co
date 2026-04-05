---
allowed-tools: Read, Bash
description: Check OpenClaw instance and gateway status
---

# OpenClaw Expert - Status Check

Check the current status of the OpenClaw instance and gateway.

## Variables

EXPERTISE_PATH: .claude/commands/experts/openclaw/expertise.yaml
SSH: SSH key auth configured (ed25519, no passphrase)

## Instructions

1. Read expertise for context (get instance IP from expertise.yaml)
2. SSH to instance and run checks
3. Report findings in a clear summary

## Checks to Perform

```bash
# Replace <INSTANCE_IP> with the current instance IP from expertise.yaml
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local << 'STATUS'
export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:$PATH"

echo "=== OpenClaw Status Report ==="
echo "Generated: $(date)"
echo ""
echo "=== Instance Info ==="
echo "Hostname: $(hostname)"
echo "IP: $(curl -s ifconfig.me 2>/dev/null)"
echo "Uptime: $(uptime -p)"
echo ""
echo "=== Memory ==="
free -h
echo ""
echo "=== OpenClaw Version ==="
openclaw --version 2>&1
echo ""
echo "=== Gateway Service ==="
launchctl list | grep openclaw
echo ""
echo "=== Doctor ==="
openclaw doctor --non-interactive 2>&1 | tail -10
echo ""
echo "=== Models Status ==="
openclaw models status 2>&1
echo ""
echo "=== Channels ==="
openclaw channels list 2>&1
echo ""
echo "=== Skills ==="
ls ~/.openclaw/workspace/skills/ 2>/dev/null || echo "No skills directory"
echo ""
echo "=== Disk ==="
df -h / | tail -1
STATUS
```

## Report Format

```markdown
# OpenClaw Status Report

**Generated**: {timestamp}
**Instance**: {ip}

## Summary

| Component | Status |
|-----------|--------|
| Instance | {running/stopped} |
| Gateway Service | {active/inactive/failed} |
| OpenClaw Version | {version} |
| Doctor | {ok count} ok, {warn count} warnings, {error count} errors |
| Memory | {used}/{total} |
| Auth | {configured/missing} |
| Channels | {list} |
| Skills | {count} installed |

## Service Details

{Service status output}

## Doctor Output

{Doctor summary}

## Recommendations

{Any issues to address}
```
