#!/bin/bash
# Get a secret from Supabase Vault or AWS Secrets Manager
# Usage: ./get-secret.sh SECRET_NAME [--aws|--vault|--both]

set -e

SECRET_NAME="$1"
SOURCE="${2:---vault}"  # Default to vault

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Supabase config (load from environment or defaults)
SUPABASE_URL="${SUPABASE_URL:-https://unickqnwfheaczccvgbw.supabase.co}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-}"

show_help() {
    echo "Usage: ./get-secret.sh SECRET_NAME [--aws|--vault|--both]"
    echo ""
    echo "Get secrets from Supabase Vault or AWS Secrets Manager"
    echo ""
    echo "Arguments:"
    echo "  SECRET_NAME    Name of the secret to retrieve"
    echo "  --vault        Get from Supabase Vault (default)"
    echo "  --aws          Get from AWS Secrets Manager"
    echo "  --both         Get from both and compare"
    echo ""
    echo "Examples:"
    echo "  ./get-secret.sh OPENAI_API_KEY"
    echo "  ./get-secret.sh OPENAI_API_KEY --aws"
    echo "  ./get-secret.sh OPENAI_API_KEY --both"
    echo ""
    echo "Vault secrets available:"
    echo "  OPENAI_API_KEY, ANTHROPIC_API_KEY, LINEAR_API_KEY, GOOGLE_AI_API_KEY,"
    echo "  JINA_AI_API_KEY, YOUTUBE_API_KEY, GITHUB_PAT_GBLACK686, NIH_GITHUB_PAT,"
    echo "  INFRASTRUCTURE_SUPABASE, INFRASTRUCTURE_LANGFUSE, NEO4J_GRAPHITI,"
    echo "  CLI_DEFAULT, LANGFUSE_S3, AMPLIFY, POSTGRES_PASSWORD, TELEGRAM,"
    echo "  GOOGLE_SERVICE_ACCOUNT, APIFY_API_TOKEN, APIFY_TOKEN, REF_TOOLS_API_KEY,"
    echo "  ANTHROPIC, API_KEY, CREDENTIALS"
}

get_from_vault() {
    local secret_name="$1"

    if [ -z "$SUPABASE_SERVICE_KEY" ]; then
        echo -e "${RED}Error: SUPABASE_SERVICE_KEY not set${NC}" >&2
        echo "Set it with: export SUPABASE_SERVICE_KEY=your-service-key" >&2
        return 1
    fi

    # Use Supabase REST API to call the get_secret function
    local response=$(curl -s -X POST \
        "${SUPABASE_URL}/rest/v1/rpc/get_secret" \
        -H "apikey: ${SUPABASE_SERVICE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"secret_name\": \"${secret_name}\"}")

    # Remove quotes if present
    echo "$response" | tr -d '"'
}

get_from_aws() {
    local secret_name="$1"

    # Map Vault names back to AWS names
    local aws_name
    case "$secret_name" in
        OPENAI_API_KEY) aws_name="gbautomation/core/openai-api-key" ;;
        ANTHROPIC_API_KEY) aws_name="gbautomation/core/anthropic-api-key" ;;
        APIFY_API_TOKEN) aws_name="gbautomation/core/apify-api-token" ;;
        REF_TOOLS_API_KEY) aws_name="gbautomation/core/ref-tools-api-key" ;;
        INFRASTRUCTURE_SUPABASE) aws_name="gbautomation/infrastructure/supabase" ;;
        NEO4J_GRAPHITI) aws_name="gbautomation/infrastructure/neo4j-graphiti" ;;
        INFRASTRUCTURE_LANGFUSE) aws_name="gbautomation/infrastructure/langfuse" ;;
        CLI_DEFAULT) aws_name="gbautomation/aws/cli-default" ;;
        LANGFUSE_S3) aws_name="gbautomation/aws/langfuse-s3" ;;
        AMPLIFY) aws_name="gbautomation/projects/gb-automation-landing/amplify" ;;
        POSTGRES_PASSWORD) aws_name="gbautomation/supabase/unickqnwfheaczccvgbw/postgres_password" ;;
        GOOGLE_AI_API_KEY) aws_name="gbautomation/core/google-ai-api-key" ;;
        JINA_AI_API_KEY) aws_name="gbautomation/core/jina-ai-api-key" ;;
        GITHUB_PAT_GBLACK686) aws_name="github-pat-gblack686" ;;
        LINEAR_API_KEY) aws_name="gbautomation/core/linear-api-key" ;;
        ANTHROPIC) aws_name="claude-observability/anthropic" ;;
        API_KEY) aws_name="core/api-key" ;;
        CREDENTIALS) aws_name="core-neo4j/credentials" ;;
        NIH_GITHUB_PAT) aws_name="nih-github-pat" ;;
        YOUTUBE_API_KEY) aws_name="gbautomation/core/youtube-api-key" ;;
        GOOGLE_SERVICE_ACCOUNT) aws_name="gbautomation/core/google-service-account" ;;
        APIFY_TOKEN) aws_name="gbautomation/core/apify-token" ;;
        TELEGRAM) aws_name="gbautomation/integrations/telegram" ;;
        *) aws_name="$secret_name" ;;  # Try as-is
    esac

    aws secretsmanager get-secret-value \
        --secret-id "$aws_name" \
        --query 'SecretString' \
        --output text 2>/dev/null
}

# Main
if [ -z "$SECRET_NAME" ] || [ "$SECRET_NAME" == "--help" ] || [ "$SECRET_NAME" == "-h" ]; then
    show_help
    exit 0
fi

case "$SOURCE" in
    --vault)
        echo -e "${GREEN}[Vault]${NC} Getting: $SECRET_NAME" >&2
        get_from_vault "$SECRET_NAME"
        ;;
    --aws)
        echo -e "${YELLOW}[AWS]${NC} Getting: $SECRET_NAME" >&2
        get_from_aws "$SECRET_NAME"
        ;;
    --both)
        echo -e "${GREEN}[Vault]${NC}" >&2
        vault_value=$(get_from_vault "$SECRET_NAME" 2>/dev/null || echo "ERROR")
        echo "$vault_value"
        echo ""
        echo -e "${YELLOW}[AWS]${NC}" >&2
        aws_value=$(get_from_aws "$SECRET_NAME" 2>/dev/null || echo "ERROR")
        echo "$aws_value"
        ;;
    *)
        echo -e "${RED}Unknown option: $SOURCE${NC}" >&2
        show_help
        exit 1
        ;;
esac
