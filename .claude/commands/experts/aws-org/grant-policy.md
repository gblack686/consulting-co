---
allowed-tools: Read, Bash, AskUserQuestion
description: Grant a least-privilege IAM policy to a sub-account user via cross-account role assumption
argument-hint: [account-name] [policy-name] [user-name]
---

# AWS Org Expert - Grant Policy

Grant a specific IAM policy to a user in a sub-account using the cross-account OrganizationAccountAccessRole pattern.

## Variables

ARGUMENTS: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/aws-org/expertise.yaml

## Instructions

1. Parse arguments to determine target account, policy, and user
2. Read expertise.yaml for account details and policy templates
3. Confirm the action with the user before proceeding
4. Execute the cross-account workflow
5. Verify the policy was applied
6. Clean up temp resources immediately

## Security Rules

- NEVER grant `iam:*`, `organizations:*`, `aws-portal:*`, `account:*`, or `support:*`
- NEVER grant `AdministratorAccess` or `PowerUserAccess` to sub-account users
- NEVER use `"Action": "*"` or `"Resource": "*"` together
- ALWAYS use a policy template from expertise.yaml or create a minimal custom one
- ALWAYS clean up the temp IAM user immediately after use
- ALWAYS confirm with the user before applying

## Workflow

### Step 1: Resolve Inputs

Parse ARGUMENTS for:
- **account**: Sub-account name or ID (e.g., "openclaw-prod" or "636143319914")
- **policy**: Policy template name (e.g., "lightsail_basic") or custom description
- **user**: IAM user in the sub-account (e.g., "claude-code")

If any are missing, ask the user.

Look up account details from expertise.yaml `sub_accounts` section.

### Step 2: Build Policy Document

If a policy template name is provided, use it from `expertise.yaml` `policy_templates`.
If a custom description is provided, generate a minimal policy following least-privilege.

Show the user the policy JSON and ask for confirmation.

### Step 3: Cross-Account Execution

```bash
# 1. Create temp IAM user in management account
aws iam create-user --user-name temp-org-admin

# 2. Attach admin policy (needed to assume cross-account role)
aws iam attach-user-policy --user-name temp-org-admin \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# 3. Create access key
aws iam create-access-key --user-name temp-org-admin

# 4. Assume OrganizationAccountAccessRole in target account
AWS_ACCESS_KEY_ID={temp_key} \
AWS_SECRET_ACCESS_KEY={temp_secret} \
aws sts assume-role \
  --role-arn "arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole" \
  --role-session-name "policy-grant"

# 5. Apply the policy using assumed role credentials
AWS_ACCESS_KEY_ID={session_key} \
AWS_SECRET_ACCESS_KEY={session_secret} \
AWS_SESSION_TOKEN={session_token} \
aws iam put-user-policy \
  --user-name {target_user} \
  --policy-name {policy_name} \
  --policy-document '{policy_json}'

# 6. IMMEDIATELY clean up temp user
aws iam delete-access-key --user-name temp-org-admin --access-key-id {temp_key}
aws iam detach-user-policy --user-name temp-org-admin \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
aws iam delete-user --user-name temp-org-admin
```

### Step 4: Verify

SSH to the sub-account instance and test the new permissions:

```bash
ssh -i ~/.ssh/lightsail-default.pem ubuntu@{instance_ip} \
  'aws sts get-caller-identity && aws {service} {read-only-test-command}'
```

### Step 5: Update Expertise

After successful grant, remind user to update `expertise.yaml` sub_accounts section to document the new policy.

## Report Format

```markdown
## Policy Grant Report

**Account**: {account_name} ({account_id})
**User**: {user_name}
**Policy**: {policy_name}
**Status**: {Applied / Failed}

### Policy Document

```json
{policy_json}
```

### Verification

{Test command output}

### Cleanup

- [x] Temp IAM user deleted
- [x] Temp access key deleted
- [x] Admin policy detached
```
