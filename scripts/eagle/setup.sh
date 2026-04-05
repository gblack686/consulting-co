#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# eagle/setup.sh — One-time setup: deploy the destroyer Lambda
#
# Run this ONCE. After this, up.sh and down.sh work automatically.
#
# Usage:
#   ./scripts/eagle/setup.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGION=us-east-1

echo "🔧 Setting up Eagle auto-destroyer infrastructure..."
echo "   This is a one-time setup — Lambda + IAM roles."
echo ""

aws cloudformation deploy \
  --region "$REGION" \
  --template-file "$SCRIPT_DIR/destroyer-stack.yaml" \
  --stack-name eagle-destroyer \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-cli-pager

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  ./scripts/eagle/up.sh           — deploy Eagle + 5-min auto-destroy"
echo "  ./scripts/eagle/up.sh --no-timer — deploy without auto-destroy"
echo "  ./scripts/eagle/down.sh         — tear down immediately"
