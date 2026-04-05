#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# eagle/down.sh — Immediately tear down all Eagle dev infrastructure
#
# Usage:
#   ./scripts/eagle/down.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_NAME="eagle-auto-destroyer"

echo "💥 Eagle Teardown — invoking destroyer Lambda..."

aws lambda invoke \
  --function-name "$LAMBDA_NAME" \
  --payload '{}' \
  --region "$REGION" \
  --cli-binary-format raw-in-base64-out \
  /tmp/eagle-destroy-response.json

echo ""
echo "Response:"
cat /tmp/eagle-destroy-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/eagle-destroy-response.json

echo ""
echo "✅ Teardown initiated. CloudFormation stacks will finish deleting in ~5–10 min."
echo "   Monitor: https://console.aws.amazon.com/cloudformation/home?region=$REGION"
