---
allowed-tools: Read, Bash
description: Run an agent task on OpenClaw
argument-hint: [task description]
---

# OpenClaw Expert - Run Task

Execute an agent task on the OpenClaw instance.

## Variables

TASK: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/openclaw/expertise.yaml
SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local

## Instructions

1. Read expertise.yaml to get the current instance IP
2. Parse the task description
3. Run the agent on the OpenClaw instance via SSH
4. Return the output

## Workflow

### Step 0: Get Instance IP

Read `EXPERTISE_PATH` and extract `infrastructure.our_instance.instance_ip`.
If the IP is "TBD", inform the user that no instance is deployed and suggest running the install wizard.

### Step 1: Validate Task

Ensure the task is provided:
- If empty, ask user for task description
- If provided, proceed with execution

### Step 2: Execute on Instance

```bash
# Via SSH
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "echo '=== Running OpenClaw Agent Task ===' && \
   echo 'Task: {TASK}' && \
   echo 'Time:' \$(date) && \
   openclaw agent --prompt \"{TASK}\" 2>&1 && \
   echo '=== Task Complete ==='"
```

### Step 3: For Long-Running Tasks

```bash
# Run in background via SSH
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "nohup openclaw agent --prompt \"{TASK}\" > ~/task-output.log 2>&1 &
   echo 'Task started in background. Check: tail -f ~/task-output.log'"
```

### Step 4: Check Background Task Output

```bash
# Check output of a background task
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "tail -50 ~/task-output.log"
```

## Task Types

### Code Task
```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "openclaw agent --prompt '...'"
```

### Background Task
```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "nohup openclaw agent --prompt '...' > ~/task-output.log 2>&1 &"
```

## Report Format

```markdown
## Task Execution

**Task**: {TASK}
**Started**: {timestamp}
**Instance**: Gregs-Mac-mini.local
**Status**: {completed/running/failed}

## Output

{Agent output}

## Notes

{Any relevant observations}
```
