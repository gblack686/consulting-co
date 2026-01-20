# AWS Bedrock Budget Alerts

Email alerts for every $1 spent on AWS Bedrock, with automatic blocking after $5/day.

## Quick Deploy

```bash
# Make script executable
chmod +x deploy.sh

# Deploy (replace with your email)
./deploy.sh your-email@example.com

# Or with custom daily limit
./deploy.sh your-email@example.com 10
```

## What Gets Created

| Resource | Description |
|----------|-------------|
| SNS Topic | `bedrock-budget-alerts` - receives budget notifications |
| Email Subscription | Your email subscribed to the topic |
| Daily Budget | `bedrock-daily-budget` - $5/day limit on Bedrock |
| IAM Deny Policy | `bedrock-budget-exceeded-deny` - blocks Bedrock access |
| IAM Role | `bedrock-budget-action-role` - for budget automation |

## Alert Thresholds

| Threshold | Amount | Action |
|-----------|--------|--------|
| 20% | $1 | Email alert |
| 40% | $2 | Email alert |
| 60% | $3 | Email alert |
| 80% | $4 | Email alert |
| 100% | $5 | Email alert + Block (if configured) |

## Enable Automatic Blocking

After deploying, configure the Budget Action to automatically block Bedrock:

### Option 1: AWS Console
1. Go to **AWS Console** > **Billing** > **Budgets**
2. Click **bedrock-daily-budget**
3. Go to **Actions** tab > **Add Action**
4. Configure:
   - Action type: **Apply IAM policy**
   - Threshold: **100%**
   - IAM policy: **bedrock-budget-exceeded-deny**
   - Attach to: Select your IAM users/roles that use Bedrock
5. Save

### Option 2: AWS CLI
```bash
# Get your IAM user/role ARN
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create budget action
aws budgets create-budget-action \
    --account-id "$ACCOUNT_ID" \
    --budget-name "bedrock-daily-budget" \
    --notification-type ACTUAL \
    --action-type APPLY_IAM_POLICY \
    --action-threshold ActionThresholdValue=100,ActionThresholdType=PERCENTAGE \
    --definition IamActionDefinition="{PolicyArn=arn:aws:iam::${ACCOUNT_ID}:policy/bedrock-budget-exceeded-deny,Users=[your-username]}" \
    --execution-role-arn "arn:aws:iam::${ACCOUNT_ID}:role/bedrock-budget-action-role" \
    --approval-model AUTOMATIC \
    --subscribers "[{\"SubscriptionType\":\"SNS\",\"Address\":\"arn:aws:sns:us-east-1:${ACCOUNT_ID}:bedrock-budget-alerts\"}]"
```

## Manual CLI Setup (Alternative)

If you prefer not to use CloudFormation:

```bash
# 1. Create SNS Topic
TOPIC_ARN=$(aws sns create-topic --name bedrock-budget-alerts --query TopicArn --output text)
aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol email --notification-endpoint your-email@example.com

# 2. Create Budget (save as budget.json first)
aws budgets create-budget --account-id $(aws sts get-caller-identity --query Account --output text) --budget file://budget.json --notifications-with-subscribers file://notifications.json
```

## Cleanup

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name bedrock-budget-alerts

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name bedrock-budget-alerts
```

## Notes

- **Email confirmation required**: Check your inbox and confirm the SNS subscription
- **Budget resets daily**: The $5 limit resets at midnight UTC
- **Blocking is preventive**: Once blocked, you must manually remove the deny policy
- **Cost data delay**: AWS cost data can have up to 24-hour delay; real-time blocking may not be instant
