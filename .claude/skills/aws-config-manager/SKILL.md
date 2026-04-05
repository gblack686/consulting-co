---
name: aws-config-manager
description: Comprehensive AWS configuration management for credentials, secrets, account info, billing queries, and CloudWatch alerts. Use this skill when working with AWS resources, checking account settings, or managing infrastructure configurations.
---

# AWS Config Manager

## Overview

This skill provides comprehensive AWS configuration management, enabling Claude Code to:
- **Retrieve credentials** from profiles, environment, or AWS SSO
- **Access secrets** from AWS Secrets Manager and SSM Parameter Store
- **Query account info** including account numbers, regions, and identity details
- **Run billing queries** via AWS Cost Explorer
- **Manage CloudWatch alerts** - list, create, and modify alarms

## When to Use This Skill

Activate this skill when:
- User needs to check AWS credentials or configure profiles
- Retrieving secrets from Secrets Manager or SSM Parameter Store
- Checking account numbers, IAM identity, or region configuration
- Running cost/billing queries or analyzing AWS spend
- Managing CloudWatch alarms and metrics
- Setting up AWS infrastructure configurations

## Capabilities

### Credentials Management
- **List profiles** - Show all configured AWS profiles
- **Get credentials** - Retrieve access keys from profile/environment
- **Validate credentials** - Test if credentials are valid
- **SSO login** - Initiate AWS SSO authentication
- **Assume role** - Get temporary credentials via STS

### Secrets Management
- **List secrets** - Show all Secrets Manager secrets
- **Get secret** - Retrieve secret value by name/ARN
- **Get parameter** - Retrieve SSM Parameter Store values
- **List parameters** - Show parameters by path prefix
- **Create/Update secrets** - Store new secrets securely

### Account Information
- **Get caller identity** - Show current IAM user/role details
- **Get account ID** - Retrieve AWS account number
- **List regions** - Show available/enabled regions
- **Get organization info** - Show AWS Organizations details
- **List accounts** - Show all accounts in organization

### Billing & Cost Explorer
- **Get current month costs** - Query month-to-date spend
- **Get cost by service** - Break down costs by AWS service
- **Get cost by tag** - Group costs by resource tags
- **Get cost forecast** - Predict end-of-month costs
- **Compare periods** - Compare costs across time ranges

### CloudWatch Alerts
- **List alarms** - Show all CloudWatch alarms
- **Get alarm details** - View specific alarm configuration
- **Create alarm** - Set up new metric alarms
- **Update alarm** - Modify existing alarm thresholds
- **Delete alarm** - Remove alarms
- **Get alarm history** - View alarm state changes

## Configuration

Configuration is managed via `.claude/skills/aws-config-manager/config/aws-settings.json`:

```json
{
  "defaultProfile": "default",
  "defaultRegion": "us-east-1",
  "ssoStartUrl": "https://your-org.awsapps.com/start",
  "costExplorer": {
    "granularity": "DAILY",
    "defaultMetrics": ["UnblendedCost", "UsageQuantity"]
  },
  "secretsManager": {
    "defaultKmsKeyId": null,
    "secretPrefix": ""
  },
  "cloudwatch": {
    "namespaceFilter": null,
    "alarmPrefix": ""
  }
}
```

## How to Use This Skill

### 1. Check Current Identity

```bash
python scripts/account_info.py --action identity
```

Output:
```
Account: 123456789012
User ARN: arn:aws:iam::123456789012:user/developer
User ID: AIDAEXAMPLEUSER
```

### 2. List AWS Profiles

```bash
python scripts/credentials_manager.py --action list-profiles
```

### 3. Get Secret from Secrets Manager

```bash
python scripts/secrets_manager.py --action get-secret --name "prod/database/credentials"
```

### 4. Get SSM Parameter

```bash
python scripts/secrets_manager.py --action get-parameter --name "/app/config/api-key" --decrypt
```

### 5. Query Current Month Costs

```bash
python scripts/billing_query.py --action current-month
```

Output:
```json
{
  "period": "2026-01-01 to 2026-01-14",
  "total": "$1,234.56",
  "currency": "USD",
  "topServices": [
    {"service": "Amazon EC2", "cost": "$456.78"},
    {"service": "Amazon S3", "cost": "$234.56"}
  ]
}
```

### 6. Get Cost by Service

```bash
python scripts/billing_query.py --action by-service --start 2026-01-01 --end 2026-01-14
```

### 7. List CloudWatch Alarms

```bash
python scripts/cloudwatch_alerts.py --action list-alarms
```

### 8. Create CloudWatch Alarm

```bash
python scripts/cloudwatch_alerts.py --action create-alarm \
  --name "HighCPU-Production" \
  --metric CPUUtilization \
  --namespace AWS/EC2 \
  --threshold 80 \
  --comparison GreaterThanThreshold \
  --period 300 \
  --evaluation-periods 2
```

### 9. Get Cost Forecast

```bash
python scripts/billing_query.py --action forecast --days 30
```

### 10. Assume IAM Role

```bash
python scripts/credentials_manager.py --action assume-role \
  --role-arn arn:aws:iam::123456789012:role/AdminRole \
  --session-name cli-session
```

## Scripts

### scripts/credentials_manager.py
Manages AWS credentials and profiles:
- List available profiles
- Validate credentials
- Assume IAM roles
- SSO authentication
- Export credentials as environment variables

### scripts/secrets_manager.py
Manages secrets and parameters:
- AWS Secrets Manager operations (CRUD)
- SSM Parameter Store operations (CRUD)
- Batch retrieval of parameters by path
- Secret rotation status

### scripts/account_info.py
Retrieves account information:
- Get caller identity (STS)
- Account details
- Organization info
- Available regions
- Service quotas

### scripts/billing_query.py
Cost Explorer queries:
- Current month costs
- Cost breakdown by service/tag/region
- Cost forecasting
- Budget status
- Reserved Instance utilization

### scripts/cloudwatch_alerts.py
CloudWatch alarm management:
- List/describe alarms
- Create/update/delete alarms
- Alarm history
- Metric data queries
- Composite alarms

## Environment Variables

The skill respects standard AWS environment variables:

```bash
AWS_PROFILE=your-profile          # AWS profile to use
AWS_REGION=us-east-1              # Default region
AWS_ACCESS_KEY_ID=AKIA...         # Access key (if not using profiles)
AWS_SECRET_ACCESS_KEY=...         # Secret key
AWS_SESSION_TOKEN=...             # Session token (for temporary creds)
AWS_DEFAULT_OUTPUT=json           # Output format
```

## Dependencies

Python packages (see `requirements.txt`):
- `boto3>=1.34.0` - AWS SDK for Python
- `botocore>=1.34.0` - Core functionality
- `rich>=13.0.0` - Beautiful terminal output
- `click>=8.0.0` - CLI framework
- `python-dateutil>=2.8.0` - Date utilities

Install with:
```bash
cd .claude/skills/aws-config-manager
pip install -r requirements.txt
```

## Security Considerations

### Credential Handling
- Never logs or displays full secret values (shows `***` masked)
- Credentials are retrieved on-demand, not cached
- Supports MFA and SSO authentication
- Respects AWS credential chain precedence

### Secret Access
- Requires appropriate IAM permissions
- Logs secret access for audit trail
- Supports KMS encryption for secrets
- Parameter Store SecureString support

### Cost Data
- Read-only access to Cost Explorer
- No ability to modify budgets or billing
- Respects tag-based access controls

## IAM Permissions Required

Minimum IAM policy for full functionality:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "STSIdentity",
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity",
        "sts:AssumeRole"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManager",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:ListSecrets",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SSMParameters",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath",
        "ssm:DescribeParameters"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CostExplorer",
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetDimensionValues"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatch",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:DescribeAlarms",
        "cloudwatch:DescribeAlarmHistory",
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DeleteAlarms",
        "cloudwatch:GetMetricData"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Organizations",
      "Effect": "Allow",
      "Action": [
        "organizations:DescribeOrganization",
        "organizations:ListAccounts"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Credentials Not Found
```
Error: Unable to locate credentials
Solution:
- Run `aws configure` to set up default profile
- Set AWS_PROFILE environment variable
- Use --profile flag to specify profile
```

### Access Denied
```
Error: AccessDenied when calling GetSecretValue
Solution:
- Verify IAM permissions for secrets:read
- Check resource-based policy on secret
- Ensure KMS key permissions if encrypted
```

### Cost Explorer Not Enabled
```
Error: Cost Explorer has not been enabled
Solution:
- Enable Cost Explorer in AWS Console (Billing > Cost Explorer)
- Wait 24 hours for data to populate
- Requires account owner permissions
```

### SSO Token Expired
```
Error: The SSO session associated with this profile has expired
Solution:
- Run: aws sso login --profile your-sso-profile
- Or use: python scripts/credentials_manager.py --action sso-login
```

## Version

**Version:** 1.0.0
**Last Updated:** January 14, 2026
**Model Compatibility:** All Claude models (Haiku, Sonnet, Opus)
