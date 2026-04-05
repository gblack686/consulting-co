# 1Password Scoped Access for AI Agents

## Overview
Set up a scoped API key in 1Password so AI agents can access only a subset of passwords/secrets using **Service Accounts**.

## Setup Steps

### 1. Create a Dedicated Vault
- In 1Password web → **New Vault** (e.g., "AI Agent Secrets")
- Move/copy only the credentials your agents need into this vault

### 2. Create a Service Account
- Go to **Developer** → **Service Accounts** → **New Service Account**
- Name it (e.g., `claude-agents`)
- Grant access to **only** the "AI Agent Secrets" vault
- Set permission level: **Read Only** (recommended) or Read/Write
- Copy the generated token (`ops_...`)

### 3. Use the Token in Your Agents
```bash
# Set the service account token
export OP_SERVICE_ACCOUNT_TOKEN="ops_your_token_here"

# Read a secret via CLI
op read "op://AI Agent Secrets/OpenAI/api-key"

# Or inject into a command
op run --env-file=.env.tpl -- your-agent-command
```

## Key Constraints

- Service accounts can only access **vaults explicitly granted** — they cannot see your personal or shared vaults
- You can create multiple service accounts with different vault access (e.g., one per agent/project)
- Tokens don't expire by default but can be revoked instantly
- No interactive login required — just the `OP_SERVICE_ACCOUNT_TOKEN` env var

## Storing the Token

Since you're already using AWS Secrets Manager, store the 1Password service account token there:

```bash
aws secretsmanager create-secret \
  --name "gbautomation/1password/service-account" \
  --secret-string '{"token": "ops_your_token_here"}'
```

Then your agents fetch the 1P token from AWS, then use it to read scoped secrets from 1Password.

## 1Password CLI Install (if needed)

```powershell
winget install AgileBits.1Password.CLI
```

---
*Session date: 2026-04-02*
