---
allowed-tools: Read, Bash, Grep, Glob
description: Answer questions about AWS Organization, sub-accounts, Lightsail, and IAM policies
argument-hint: [question]
---

# AWS Org Expert - Question Mode

Answer questions about AWS Organization structure, sub-account management, Lightsail instances, cross-account IAM, and least-privilege policies.

## Variables

USER_QUESTION: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/aws-org/expertise.yaml

## Instructions

- IMPORTANT: This is a question-answering task only - DO NOT make changes
- Reference the expertise.yaml for account details, policy templates, and security rules
- If the question requires changes, explain the approach without implementing
- Always emphasize least-privilege and security rules

## Workflow

1. Read `EXPERTISE_PATH` for context
2. Identify relevant section (sub_accounts, cross_account_access, policy_templates, security_rules, lightsail)
3. Optionally run read-only AWS CLI commands to check current state
4. Formulate answer with specific details

## Safe Read-Only Commands

```bash
# Organization
aws organizations list-accounts --query 'Accounts[*].[Id,Name,Email,Status]' --output table

# Secrets
aws secretsmanager list-secrets --query 'SecretList[*].Name' --output text

# Lightsail (from sub-account instance via SSH)
ssh -i ~/.ssh/lightsail-default.pem ubuntu@{IP} 'aws lightsail get-instances --output table'
ssh -i ~/.ssh/lightsail-default.pem ubuntu@{IP} 'aws sts get-caller-identity'
```

## Report Format

```markdown
## Answer

{Direct answer}

## Details

{Supporting explanation}

## Security Notes

{Relevant security considerations from expertise.yaml security_rules}

## Reference

- Expertise: `EXPERTISE_PATH` section: {section_name}
```
