---
allowed-tools: Read, Bash, Glob, Grep
description: Search AI-Agent-KB for skills matching a keyword and cross-reference with deployed OpenClaw skills
argument-hint: [keyword e.g. "supabase"]
---

# OpenClaw Expert - Find Skills

Search Obsidian AI-Agent-KB for skills, commands, agents, experts, and scripts matching a keyword, then cross-reference with what's already deployed on the OpenClaw instance.

## Variables

KEYWORD: $ARGUMENTS
SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local
KB_PATH: C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB
DEPLOY_TARGET: /Users/greg/.openclaw/workspace/skills

## Instructions

1. Validate that KEYWORD is provided. If empty, ask the user for a keyword.
2. Search the AI-Agent-KB across all entity directories for matches.
3. If an instance is available (IP is not "TBD"), get the list of already-deployed skills via SSH.
4. Cross-reference and output a results table.
5. Recommend which skills to deploy.

## Workflow

### Step 1: Search AI-Agent-KB

Search these directories for files matching the keyword:

- `{KB_PATH}/skills/`
- `{KB_PATH}/commands/`
- `{KB_PATH}/agents/`
- `{KB_PATH}/experts/`
- `{KB_PATH}/adws/`
- `{KB_PATH}/ai-docs/`
- `{KB_PATH}/scripts/`

Use both filename matching and content grep:

```bash
# Find by filename
find "{KB_PATH}" -path "*skills*" -o -path "*commands*" -o -path "*agents*" -o -path "*experts*" -o -path "*adws*" -o -path "*ai-docs*" -o -path "*scripts*" | grep -i "{KEYWORD}" 2>/dev/null

# Find by content
grep -ril "{KEYWORD}" "{KB_PATH}/skills/" "{KB_PATH}/commands/" "{KB_PATH}/agents/" "{KB_PATH}/experts/" "{KB_PATH}/adws/" "{KB_PATH}/ai-docs/" "{KB_PATH}/scripts/" 2>/dev/null
```

### Step 2: Get Deployed Skills from OpenClaw

```bash
# Via SSH
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "echo '=== Deployed Skills ===' && \
   ls ~/.openclaw/workspace/skills/ 2>/dev/null && \
   echo '' && \
   echo '=== Skill Details ===' && \
   for d in ~/.openclaw/workspace/skills/*/; do \
     [ -d \"\$d\" ] && echo \"\$(basename \$d): \$(head -3 \$d/SKILL.md 2>/dev/null)\"; \
   done"
```

If the instance IP is "TBD", skip this step and note that no instance is available for cross-referencing.

### Step 3: Cross-Reference and Classify

For each KB match:
- Check if a skill with a similar name exists in the deployed list
- Mark as: `deployed` (already on OpenClaw), `candidate` (good for deployment), or `reference-only` (not suitable)

### Step 4: Output Results

## Report Format

```markdown
# Find Skills: "{KEYWORD}"

**Generated**: {timestamp}
**Searched**: AI-Agent-KB ({count} directories)
**Instance**: Gregs-Mac-mini.local (or "No active instance")

## Results

| # | Name | Type | Tags | Status | Deployed | Recommendation |
|---|------|------|------|--------|----------|----------------|
| 1 | {name} | {type} | {tags} | {status} | {yes/no} | {deploy/skip/already deployed} |

## Recommended for Deployment

{List of candidates with brief reason}

## Already Deployed

{List of matches already on OpenClaw}

## Skipped (Reference Only)

{List of files that matched but aren't suitable}
```
