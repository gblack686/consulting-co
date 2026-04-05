---
allowed-tools: Read, Bash
description: List all AWS Organization sub-accounts with their IAM users and policies
---

# AWS Org Expert - List Accounts

Show all sub-accounts in the AWS Organization with their status, IAM users, Lightsail instances, and applied policies.

## Variables

EXPERTISE_PATH: .claude/commands/experts/aws-org/expertise.yaml

## Instructions

1. List accounts from AWS Organizations
2. For each sub-account with stored credentials, check IAM policies and Lightsail instances
3. Present a consolidated view

## Workflow

### Step 1: List Organization Accounts

```bash
aws organizations list-accounts \
  --query 'Accounts[*].[Id,Name,Email,Status]' \
  --output table
```

### Step 2: For Each Sub-Account

For accounts with credentials in Secrets Manager, use the cross-account role to list:

```bash
# List IAM users
aws iam list-users --query 'Users[*].UserName' --output text

# For each user, list policies
aws iam list-user-policies --user-name {user} --output text

# List Lightsail instances
aws lightsail get-instances \
  --query 'instances[*].[name,state.name,publicIpAddress,bundleId]' \
  --output table
```

### Step 3: Cross-Reference with Expertise

Read expertise.yaml and compare documented state vs actual state.
Flag any discrepancies (undocumented policies, missing instances, etc.)

## Report Format

```markdown
# AWS Organization Overview

**Organization**: {org_id}
**Management Account**: {mgmt_id} ({mgmt_name})
**Total Sub-Accounts**: {count}

## Sub-Accounts

### {account_name} ({account_id})
- **Email**: {email}
- **Status**: {status}
- **IAM Users**: {user_list}
- **Policies**: {policy_list}
- **Lightsail Instances**: {instance_table}
- **Monthly Cost**: {estimated_cost}
```
