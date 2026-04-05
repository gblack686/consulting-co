---
allowed-tools: Read, Grep, Glob, Bash, WebFetch
description: Answer questions about OpenClaw setup, configuration, and usage
argument-hint: [question]
---

# OpenClaw Expert - Question Mode

Answer the user's question about OpenClaw by referencing the expertise knowledge base and optionally checking the live instance state.

## Variables

USER_QUESTION: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/openclaw/expertise.yaml
SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local

## Instructions

- IMPORTANT: This is a question-answering task only - DO NOT make configuration changes
- Focus on OpenClaw operations, gateway, agents, skills, and configuration
- If the question requires changes, explain the approach conceptually without implementing
- Validate information from `EXPERTISE_PATH` against the live instance when helpful

## Workflow

1. **Load Expertise**
   - Read the `EXPERTISE_PATH` file to understand OpenClaw architecture
   - Identify relevant sections for the USER_QUESTION

2. **Optionally Check Live State**
   - If an instance IP is available (not "TBD"), run commands via SSH to verify current state
   - Check systemd user service status
   - Query current configuration

3. **Formulate Answer**
   - Provide direct answer with specific commands
   - Include security considerations where relevant
   - Reference actual implementation patterns

## Question Categories

### Category 1: Installation & Deployment Questions
Questions about deploying, configuring, or updating OpenClaw on the Mac Mini.

**Resolution**:
1. Read expertise.yaml installation section
2. Reference INSTALLATION_GUIDE.md for full steps
3. Explain Mac Mini setup + npm install workflow

### Category 2: Gateway & Service Questions
Questions about the OpenClaw daemon, proxy, and connectivity.

**Resolution**:
1. Read expertise.yaml runtime section
2. Provide launchctl and SSH commands
3. Explain service architecture

### Category 3: Configuration Questions
Questions about openclaw.json format, valid keys, schema.

**Resolution**:
1. Read expertise.yaml config section
2. Explain JSON format and valid keys
3. Warn about invalid keys and autonomy gotcha

### Category 4: Agent & Task Questions
Questions about running agents, tasks, and skills.

**Resolution**:
1. Read expertise.yaml commands section
2. Explain openclaw agent, skills, memory commands
3. Provide SSH-based execution examples

### Category 5: Troubleshooting Questions
Questions about errors, issues, or unexpected behavior.

**Resolution**:
1. Read expertise.yaml troubleshooting section
2. Check live instance state via SSH (if available)
3. Provide specific fixes

## Key Commands for Live Checks

```bash
# Via SSH (preferred)
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "openclaw doctor --non-interactive 2>&1"

# Check gateway service
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "launchctl list | grep openclaw"

# Check gateway logs
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "tail -f ~/.openclaw/logs/gateway.log"
```

## Report Format

```markdown
## Answer

{Direct answer to the USER_QUESTION}

## Details

{Supporting explanation with commands if helpful}

## Commands

```bash
# Relevant commands for this topic
{command 1}
{command 2}
```

## Source Reference

- Expertise: `EXPERTISE_PATH` section: {section_name}
- OpenClaw Docs: https://docs.openclaw.ai
```
