#!/bin/bash
# Deploy Bedrock Budget Alerts CloudFormation Stack
# Usage: ./deploy.sh your-email@example.com [daily-limit]

set -e

EMAIL="${1:?Error: Email address required. Usage: ./deploy.sh your-email@example.com [daily-limit]}"
DAILY_LIMIT="${2:-5}"
STACK_NAME="bedrock-budget-alerts"
REGION="${AWS_REGION:-us-east-1}"

echo "=========================================="
echo "Deploying Bedrock Budget Alerts"
echo "=========================================="
echo "Email: $EMAIL"
echo "Daily Limit: \$$DAILY_LIMIT"
echo "Region: $REGION"
echo "=========================================="

# Validate template
echo "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://bedrock-budget-alerts.yaml \
    --region "$REGION"

# Deploy stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file bedrock-budget-alerts.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        EmailAddress="$EMAIL" \
        DailyBudgetLimit="$DAILY_LIMIT" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: Check your email ($EMAIL) and confirm the SNS subscription!"
echo ""
echo "You will receive alerts at:"
echo "  - \$1 spent (20% of \$$DAILY_LIMIT)"
echo "  - \$2 spent (40% of \$$DAILY_LIMIT)"
echo "  - \$3 spent (60% of \$$DAILY_LIMIT)"
echo "  - \$4 spent (80% of \$$DAILY_LIMIT)"
echo "  - \$5 spent (100% - LIMIT REACHED)"
echo ""
echo "To enable automatic blocking after \$$DAILY_LIMIT/day:"
echo "1. Go to AWS Console > Billing > Budgets"
echo "2. Select 'bedrock-daily-budget'"
echo "3. Add a Budget Action to attach the deny policy"
echo ""
