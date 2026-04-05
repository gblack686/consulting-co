---
allowed-tools: Read, Bash, AskUserQuestion
description: Revoke an IAM policy from a sub-account user via cross-account role assumption
argument-hint: [account-name] [policy-name] [user-name]
---

# AWS Org Expert - Revoke Policy

Remove a specific IAM policy from a user in a sub-account using the cross-account OrganizationAccountAccessRole pattern.

## Variables

ARGUMENTS: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/aws-org/expertise.yaml

## Instructions

1. Parse arguments to determine target account, policy, and user
2. Confirm the revocation with the user
3. Execute cross-account workflow to delete the inline policy
4. Verify the policy was removed
5. Clean up temp resources immediately

## Workflow

### Step 1: Resolve Inputs

Parse ARGUMENTS for:
- **account**: Sub-account name or ID
- **policy**: Policy name to revoke (e.g., "LightsailAccess")
- **user**: IAM user in the sub-account

If any are missing, ask the user.

### Step 2: List Current Policies (optional)

Before revoking, show the user what policies the target user currently has:

Use the cross-account pattern to run:
```bash
aws iam list-user-policies --user-name {target_user}
```

### Step 3: Cross-Account Execution

Same temp-user pattern as grant-policy, but call:

```bash
aws iam delete-user-policy \
  --user-name {target_user} \
  --policy-name {policy_name}
```

### Step 4: Clean Up and Verify

Delete temp user immediately, then verify from the sub-account instance that the permission is gone.

## Report Format

```markdown
## Policy Revocation Report

**Account**: {account_name} ({account_id})
**User**: {user_name}
**Policy Removed**: {policy_name}
**Status**: {Revoked / Failed}

### Cleanup

- [x] Temp IAM user deleted
```
