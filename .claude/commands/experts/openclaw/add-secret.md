---
allowed-tools: Bash, Read, AskUserQuestion
description: Add AWS and/or Supabase credentials to OpenClaw instance
argument-hint: [aws|supabase|both]
---

# OpenClaw Expert - Add Secret

Add credentials to the OpenClaw instance via SSH.

## Variables

SECRET_TYPE: $ARGUMENTS (default: both)
SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local

## Instructions

1. Read expertise.yaml to get the current instance IP.
2. Based on SECRET_TYPE, add the appropriate credentials to `~/.openclaw/.env` on the instance.

### Step 0: Get Instance IP

Read `.claude/commands/experts/openclaw/expertise.yaml` and extract `infrastructure.our_instance.instance_ip`.
If the IP is "TBD", inform the user that no instance is deployed and suggest running the install wizard.

### Option: aws

Add AWS credentials:

```bash
# Retrieve from AWS Secrets Manager
AWS_CREDS=$(aws secretsmanager get-secret-value --secret-id gbautomation/aws-credentials --query SecretString --output text 2>/dev/null)

# If no dedicated secret, use local AWS config
if [ -z "$AWS_CREDS" ]; then
  AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
  AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
  AWS_REGION=$(aws configure get region)
fi

# Write env vars to instance via SSH
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local bash -s << 'REMOTE_EOF'
cat >> ~/.openclaw/.env << EOF
# AWS Credentials
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_REGION=${AWS_REGION:-us-east-1}
EOF
chmod 600 ~/.openclaw/.env
REMOTE_EOF
```

### Option: supabase

Add Supabase credentials:

```bash
# Retrieve from AWS Secrets Manager
SUPABASE_CREDS=$(aws secretsmanager get-secret-value --secret-id gbautomation/infrastructure/supabase --query SecretString --output text)
SUPABASE_URL=$(echo "$SUPABASE_CREDS" | python -c "import sys,json; print(json.load(sys.stdin)['url'])")
SUPABASE_KEY=$(echo "$SUPABASE_CREDS" | python -c "import sys,json; print(json.load(sys.stdin)['service_key'])")

# Write to instance via SSH
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local bash -s << 'REMOTE_EOF'
cat >> ~/.openclaw/.env << EOF
# Supabase Credentials
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=${SUPABASE_KEY}
EOF
chmod 600 ~/.openclaw/.env
REMOTE_EOF
```

### Option: both (default)

Run both aws and supabase options.

## Post-Actions

After adding secrets, restart services:

```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "openclaw gateway restart && \
   sleep 2 && \
   echo '=== Configured env vars (names only) ===' && \
   grep -E '^[A-Z]' ~/.openclaw/.env | sed 's/=.*/=***/'"
```

## Supported Secrets

| Secret | AWS Secrets Manager Path | Variables Added |
|--------|-------------------------|-----------------|
| AWS | gbautomation/aws-credentials | AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION |
| Supabase | gbautomation/infrastructure/supabase | SUPABASE_URL, SUPABASE_SERVICE_KEY |
| OpenRouter | gbautomation/core/openrouter-api-key | OPENROUTER_API_KEY |
| GitHub | gbautomation/github-pat | GITHUB_TOKEN |
| Linear | gbautomation/linear-api-key | LINEAR_API_KEY |

## Note

The OpenRouter API key should be added to `~/.openclaw/.env` the same way.
It is loaded by the launchd service on startup.
