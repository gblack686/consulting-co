---
allowed-tools: Read, Glob, Grep, Edit, Bash, WebFetch
description: Self-improve OpenClaw expertise by validating against live instance and official docs
---

# OpenClaw Expert - Self-Improve Mode

> Validate and update OpenClaw expertise by scanning the live instance state, comparing against official documentation, and updating the expertise knowledge base with discoveries.

## Variables

EXPERTISE_PATH: .claude/commands/experts/openclaw/expertise.yaml
SSH: SSH key auth configured (ed25519, no passphrase)

## Instructions

- This command MODIFIES the expertise.yaml — it is the only expert command that writes
- Always validate findings against live instance state before updating expertise
- Compare what expertise.yaml claims vs what the instance actually has configured
- Fetch official docs when expertise seems outdated or incomplete

## Workflow

### Step 1: Load Current Expertise

```
Read: .claude/commands/experts/openclaw/expertise.yaml
```

Record the current state:
- Listed version
- Infrastructure specs
- Configuration sections
- Command references
- Troubleshooting entries

### Step 2: Audit Live Instance

SSH to the instance and collect current state:

```bash
# Get INSTANCE_IP from expertise.yaml first
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local << 'AUDIT'
export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:$PATH"

echo "=== VERSION ==="
openclaw --version 2>&1

echo "=== CONFIG ==="
cat ~/.openclaw/openclaw.json 2>&1

echo "=== GATEWAY STATUS ==="
launchctl list | grep openclaw

echo "=== MEMORY STATUS ==="
openclaw memory status 2>&1

echo "=== SKILLS ==="
ls ~/.openclaw/workspace/skills/ 2>/dev/null

echo "=== WORKSPACE CONTENTS ==="
ls ~/.openclaw/workspace/ 2>/dev/null

echo "=== DISK ==="
df -h / 2>&1

echo "=== AGENTS ==="
ls ~/.openclaw/agents/ 2>/dev/null

echo "=== CHANNELS CONFIGURED ==="
openclaw channels list 2>&1

echo "=== NPM GLOBAL PACKAGES ==="
npm list -g --depth=0 2>&1
AUDIT
```

### Step 3: Check Official Docs for Updates

Fetch key documentation pages:

```
WebFetch: https://docs.openclaw.ai/gateway/configuration-reference
  Prompt: List all configuration sections and any new fields

WebFetch: https://docs.openclaw.ai/concepts/agent
  Prompt: Extract agent runtime changes, new context files, and updated defaults
```

### Step 4: Compare and Identify Gaps

Build a comparison table:

| Area | Expertise Claims | Live Instance | Official Docs | Action |
|------|-----------------|---------------|---------------|--------|
| Version | {expertise_version} | {live_version} | {latest_npm} | Update if different |
| Config | {yaml_sections} | {json_keys} | {ref_sections} | Add missing |
| Commands | {listed_commands} | {available_commands} | {doc_commands} | Add missing |
| Troubleshooting | {listed_issues} | {observed_issues} | - | Add new issues |
| Skills | {listed_skills} | {installed_skills} | - | Update list |

### Step 5: Update Expertise

Edit `expertise.yaml` with discovered changes.

### Step 6: Report

```markdown
## OpenClaw Self-Improve Report

### Instance State
- **Version**: {installed} (latest: {npm_latest})
- **Gateway**: {status}
- **Channels**: {active_channels}

### Expertise Updates Made

| Section | Change | Details |
|---------|--------|---------|
| {section} | {change_type} | {description} |

### Recommendations
- {recommendation_1}
- {recommendation_2}
```
