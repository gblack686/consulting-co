#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# eagle/up.sh — Deploy Eagle stack + auto-destroy in 5 minutes
#
# Usage:
#   ./scripts/eagle/up.sh [--no-timer]
#
# Options:
#   --no-timer    Deploy without auto-destroy (you manage teardown manually)
# ─────────────────────────────────────────────────────────────
set -euo pipefail

REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:eagle-auto-destroyer"
SCHEDULER_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/eagle-scheduler-role"
AUTO_DESTROY=true

if [[ "${1:-}" == "--no-timer" ]]; then
  AUTO_DESTROY=false
fi

# ── 1. Deploy Eagle CDK stacks ─────────────────────────────
echo "🚀 Deploying Eagle stacks..."
# TODO: update this path to your Eagle CDK app directory
EAGLE_CDK_DIR="${EAGLE_CDK_DIR:-$(pwd)}"
echo "   CDK dir: $EAGLE_CDK_DIR"
echo "   (set EAGLE_CDK_DIR env var or update this script)"

cd "$EAGLE_CDK_DIR"
cdk deploy EagleCoreStack EagleComputeStack EagleEvalStack EagleStorageStack \
  --require-approval never \
  --outputs-file /tmp/eagle-outputs.json

echo "✅ Eagle deployed."

# ── 2. Schedule auto-destroy in 5 minutes ─────────────────
if [ "$AUTO_DESTROY" = true ]; then
  DESTROY_AT=$(date -u -d '+5 minutes' '+%Y-%m-%dT%H:%M:%S' 2>/dev/null \
    || python3 -c "from datetime import datetime,timedelta; print((datetime.utcnow()+timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S'))")

  SCHEDULE_NAME="eagle-auto-destroy-$(date +%s)"

  echo ""
  echo "⏱️  Scheduling auto-destroy at ${DESTROY_AT} UTC..."

  aws scheduler create-schedule \
    --region "$REGION" \
    --name "$SCHEDULE_NAME" \
    --schedule-expression "at(${DESTROY_AT})" \
    --flexible-time-window '{"Mode": "OFF"}' \
    --target "{
      \"Arn\": \"${LAMBDA_ARN}\",
      \"RoleArn\": \"${SCHEDULER_ROLE_ARN}\",
      \"Input\": \"{}\"
    }" \
    --action-after-completion DELETE \
    --no-cli-pager

  echo "✅ Auto-destroy scheduled for: ${DESTROY_AT} UTC (5 min)"
  echo "   To cancel: aws scheduler delete-schedule --name $SCHEDULE_NAME --region $REGION"
  echo "   To destroy now: ./scripts/eagle/down.sh"
else
  echo "⚠️  No auto-destroy timer set. Run ./scripts/eagle/down.sh when done."
fi
