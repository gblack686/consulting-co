---
allowed-tools: Read, Bash, AskUserQuestion
description: Create a new AWS Organization sub-account with a least-privilege IAM user
argument-hint: [purpose e.g. "eagle-demo"]
---

# AWS Org Expert - Create Sub-Account

Create a new AWS Organization sub-account with a dedicated IAM user following least-privilege principles.

## Variables

ARGUMENTS: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/aws-org/expertise.yaml

## Instructions

1. Parse the purpose/name for the new account
2. Create the sub-account via Organizations
3. Wait for account to become active
4. Assume OrganizationAccountAccessRole into the new account
5. Create a least-privilege IAM user
6. Store credentials in management account Secrets Manager
7. Update expertise.yaml

## Security Rules

- Email format: `gblack686+{purpose}@gmail.com`
- Account name format: `{purpose}` (e.g., "eagle-demo", "client-staging")
- IAM user starts with ZERO policies - add only what's needed via grant-policy
- NEVER attach AdministratorAccess or PowerUserAccess to sub-account users
- ALWAYS store credentials in management account Secrets Manager
- NEVER store management credentials on sub-account resources

## Workflow

### Step 1: Validate and Confirm

Ask the user to confirm:
- Account purpose/name
- Expected services needed (Lightsail, S3, etc.)
- Budget estimate

### Step 2: Create Account

```bash
aws organizations create-account \
  --email "gblack686+{purpose}@gmail.com" \
  --account-name "{purpose}" \
  --role-name "OrganizationAccountAccessRole"
```

### Step 3: Wait for Account

```bash
# Get the create-account request ID and poll
aws organizations describe-create-account-status \
  --create-account-request-id {request_id} \
  --query 'CreateAccountStatus.[State,AccountId]' \
  --output text
```

Poll until State is "SUCCEEDED".

### Step 4: Create IAM User in New Account

Use temp-user cross-account pattern to assume into the new account:

```bash
# Create IAM user
aws iam create-user --user-name {purpose}-agent

# Create access key
aws iam create-access-key --user-name {purpose}-agent
```

Do NOT attach any policies yet. Use `grant-policy` to add specific permissions later.

### Step 5: Store Credentials

Store in management account Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name "{purpose}/credentials" \
  --secret-string '{
    "account_id": "{new_account_id}",
    "account_name": "{purpose}",
    "user": "{purpose}-agent",
    "aws_access_key_id": "{access_key}",
    "aws_secret_access_key": "{secret_key}",
    "region": "us-east-1"
  }'
```

### Step 6: Update Expertise

Remind user to add the new account to `expertise.yaml` under `sub_accounts`.

## Report Format

```markdown
## New Sub-Account Created

**Account ID**: {account_id}
**Name**: {purpose}
**Email**: gblack686+{purpose}@gmail.com
**IAM User**: {purpose}-agent
**Credentials Secret**: {purpose}/credentials
**Policies**: None (use grant-policy to add)

### Next Steps

1. Run `/experts:aws-org:grant-policy {purpose} lightsail_basic {purpose}-agent` to add Lightsail access
2. Run `/experts:aws-org:create-instance {purpose} {instance-name} small_3_0` to create an instance
3. Update expertise.yaml with account details
```
