#!/bin/bash
# List all secrets from Supabase Vault or AWS Secrets Manager
# Usage: ./list-secrets.sh [--aws|--vault|--both]

set -e

SOURCE="${1:---both}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Supabase config
SUPABASE_URL="${SUPABASE_URL:-https://unickqnwfheaczccvgbw.supabase.co}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-}"

list_vault() {
    echo -e "${GREEN}=== Supabase Vault Secrets ===${NC}"

    if [ -z "$SUPABASE_SERVICE_KEY" ]; then
        echo -e "${RED}Error: SUPABASE_SERVICE_KEY not set${NC}"
        echo "Set it with: export SUPABASE_SERVICE_KEY=your-service-key"
        return 1
    fi

    # Query vault.decrypted_secrets via REST API
    curl -s -X GET \
        "${SUPABASE_URL}/rest/v1/rpc/list_vault_secrets" \
        -H "apikey: ${SUPABASE_SERVICE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        2>/dev/null || echo "Note: list_vault_secrets function not found. Use SQL Editor."

    echo ""
    echo -e "${CYAN}Vault secrets (from migration):${NC}"
    echo "  OPENAI_API_KEY          ANTHROPIC_API_KEY       APIFY_API_TOKEN"
    echo "  REF_TOOLS_API_KEY       GOOGLE_AI_API_KEY       JINA_AI_API_KEY"
    echo "  LINEAR_API_KEY          YOUTUBE_API_KEY         APIFY_TOKEN"
    echo "  INFRASTRUCTURE_SUPABASE NEO4J_GRAPHITI          INFRASTRUCTURE_LANGFUSE"
    echo "  CLI_DEFAULT             LANGFUSE_S3             AMPLIFY"
    echo "  POSTGRES_PASSWORD       GITHUB_PAT_GBLACK686    ANTHROPIC"
    echo "  API_KEY                 CREDENTIALS             NIH_GITHUB_PAT"
    echo "  GOOGLE_SERVICE_ACCOUNT  TELEGRAM"
    echo ""
}

list_aws() {
    echo -e "${YELLOW}=== AWS Secrets Manager ===${NC}"

    aws secretsmanager list-secrets \
        --query 'SecretList[*].[Name,Description]' \
        --output table 2>/dev/null || echo "AWS CLI not configured"
    echo ""
}

case "$SOURCE" in
    --vault)
        list_vault
        ;;
    --aws)
        list_aws
        ;;
    --both|*)
        list_vault
        echo ""
        list_aws
        ;;
esac
