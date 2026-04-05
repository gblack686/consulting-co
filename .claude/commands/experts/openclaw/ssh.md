---
allowed-tools: Read, Bash
description: SSH into the OpenClaw instance and run a command
argument-hint: [command to run]
---

# OpenClaw Expert - SSH Remote Command

Execute a command on the OpenClaw Mac Mini instance via SSH.

## Variables

COMMAND: $ARGUMENTS

## Instructions

1. Read expertise.yaml to get the current instance hostname
2. If no command provided, open interactive guidance
3. Execute the command on the remote instance via SSH
4. Return output

## Execution

```bash
# Use mDNS hostname (DHCP IP can change)
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  'export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:$PATH" && {COMMAND}'
```

## Common Commands

### Check Status
```bash
# OpenClaw doctor
openclaw doctor --non-interactive 2>&1

# Gateway health
curl -s http://localhost:18789/health

# Full status
openclaw status

# Models auth
openclaw models status

# Channel list
openclaw channels list
```

### Service Management
```bash
# Restart gateway
openclaw gateway restart

# View logs
tail -50 ~/.openclaw/logs/gateway.log

# LaunchAgent status
launchctl list | grep openclaw
```

### Workspace
```bash
# List workspace files
ls ~/.openclaw/workspace/

# List skills
ls ~/.openclaw/workspace/skills/

# View config
cat ~/.openclaw/openclaw.json
```

### Send Messages
```bash
# Telegram
openclaw message send --channel telegram --target 6777263736 --message "text"

# Discord (needs channel/user ID)
openclaw message send --channel discord --target <channel_id> --message "text"
```

## Important Notes

- Always export PATH: `export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:$PATH"`
- Use mDNS hostname `Gregs-Mac-mini.local` — IP is DHCP and can change
- SSH key auth (ed25519), no password needed
- Services are launchd: use `launchctl` and `openclaw gateway restart`, not systemctl
- Config is at `~/.openclaw/openclaw.json` (JSON format)
- Sudo requires password (no NOPASSWD configured yet)

## Report Format

```markdown
## Remote Command Execution

**Command**: {COMMAND}
**Instance**: Gregs-Mac-mini.local
**Method**: SSH (key auth)

## Output

```
{command output}
```
```
