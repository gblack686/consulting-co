---
allowed-tools: Read, Bash, AskUserQuestion
description: Create a Lightsail instance in a sub-account with proper IAM setup
argument-hint: [account-name] [instance-name] [bundle e.g. small_3_0]
---

# AWS Org Expert - Create Lightsail Instance

Create a new Lightsail instance in a sub-account, ensuring the sub-account user has the necessary (and only the necessary) permissions.

## Variables

ARGUMENTS: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/aws-org/expertise.yaml

## Instructions

1. Parse arguments for account, instance name, and bundle size
2. Read expertise.yaml for account details and Lightsail reference
3. Verify the sub-account user has LightsailAccess policy (grant if missing)
4. Create the instance from the sub-account
5. Open required ports
6. Store SSH key and update expertise.yaml

## Workflow

### Step 1: Resolve Inputs

Parse ARGUMENTS:
- **account**: Sub-account name or ID (default: "openclaw-prod")
- **instance-name**: Name for the new instance (required)
- **bundle**: Lightsail bundle ID (default: "small_3_0" - 2GB/$12mo)

If missing, ask the user. Show bundle options from expertise.yaml:

| Bundle | CPU | RAM | Disk | Cost |
|--------|-----|-----|------|------|
| nano_3_0 | 2 vCPU | 512MB | 20GB | $3.50/mo |
| micro_3_0 | 2 vCPU | 1GB | 40GB | $5/mo |
| small_3_0 | 2 vCPU | 2GB | 60GB | $12/mo |
| medium_3_0 | 2 vCPU | 4GB | 80GB | $24/mo |
| large_3_0 | 2 vCPU | 8GB | 160GB | $48/mo |

### Step 2: Verify Sub-Account Permissions

Get sub-account credentials from Secrets Manager and test Lightsail access:

```bash
# Get credentials
CREDS=$(aws secretsmanager get-secret-value --secret-id '{credentials_secret}' --query SecretString --output text)

# Test Lightsail access
AWS_ACCESS_KEY_ID={from_creds} AWS_SECRET_ACCESS_KEY={from_creds} \
  aws lightsail get-bundles --query 'bundles[0].bundleId' --output text
```

If access denied, use `grant-policy` workflow to add LightsailAccess first.

### Step 3: Create Instance

Run from the sub-account credentials:

```bash
aws lightsail create-instances \
  --instance-names "{instance-name}" \
  --availability-zone "us-east-1a" \
  --blueprint-id "ubuntu_24_04" \
  --bundle-id "{bundle}" \
  --key-pair-name "LightsailDefaultKeyPair" \
  --output json
```

### Step 4: Wait for Instance and Get IP

```bash
# Poll until running
aws lightsail get-instance --instance-name "{instance-name}" \
  --query 'instance.state.name' --output text

# Get public IP
aws lightsail get-instance --instance-name "{instance-name}" \
  --query 'instance.publicIpAddress' --output text
```

### Step 5: Open Ports

```bash
# SSH (22) is open by default. Open additional ports as needed:
aws lightsail open-instance-public-ports \
  --instance-name "{instance-name}" \
  --port-info fromPort=80,toPort=80,protocol=tcp

aws lightsail open-instance-public-ports \
  --instance-name "{instance-name}" \
  --port-info fromPort=443,toPort=443,protocol=tcp
```

### Step 6: Verify SSH Access

```bash
ssh -i ~/.ssh/lightsail-default.pem -o StrictHostKeyChecking=no \
  ubuntu@{new_ip} 'echo "SSH OK"; uname -a'
```

## Security Checklist

- [ ] Instance uses Ubuntu 24.04 LTS (latest)
- [ ] Only required ports are opened (22, 80, 443)
- [ ] SSH key is the shared lightsail-default.pem
- [ ] Sub-account user has only LightsailAccess (no admin)
- [ ] Instance name follows convention: {purpose}-{env}

## Report Format

```markdown
## Lightsail Instance Created

**Account**: {account_name} ({account_id})
**Instance**: {instance-name}
**IP**: {public_ip}
**Bundle**: {bundle} ({specs})
**Blueprint**: Ubuntu 24.04
**Cost**: {monthly_cost}
**SSH**: `ssh -i ~/.ssh/lightsail-default.pem ubuntu@{public_ip}`

### Ports Open

| Port | Protocol | Service |
|------|----------|---------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |

### Next Steps

1. SSH in and configure the instance
2. Update expertise.yaml with new instance details
3. Store any new credentials in Secrets Manager
```
