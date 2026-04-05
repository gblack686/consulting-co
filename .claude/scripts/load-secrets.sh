#!/bin/bash
# Load multiple secrets as environment variables
# Usage: source ./load-secrets.sh [profile]
# Profiles: core, infrastructure, all

PROFILE="${1:-core}"

# Supabase config
SUPABASE_URL="${SUPABASE_URL:-https://unickqnwfheaczccvgbw.supabase.co}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-}"

# Colors (only for stderr)
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

get_secret() {
    local secret_name="$1"
    curl -s -X POST \
        "${SUPABASE_URL}/rest/v1/rpc/get_secret" \
        -H "apikey: ${SUPABASE_SERVICE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"secret_name\": \"${secret_name}\"}" | tr -d '"'
}

load_secret() {
    local vault_name="$1"
    local env_name="${2:-$vault_name}"

    local value=$(get_secret "$vault_name")
    if [ -n "$value" ] && [ "$value" != "null" ]; then
        export "$env_name"="$value"
        echo -e "${GREEN}✓${NC} Loaded: $env_name" >&2
    else
        echo -e "${RED}✗${NC} Failed: $env_name" >&2
    fi
}

if [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo -e "${RED}Error: SUPABASE_SERVICE_KEY not set${NC}" >&2
    echo "Set it with: export SUPABASE_SERVICE_KEY=your-service-key" >&2
    return 1 2>/dev/null || exit 1
fi

echo "Loading secrets from Supabase Vault (profile: $PROFILE)..." >&2

case "$PROFILE" in
    core)
        # Core API keys
        load_secret "OPENAI_API_KEY"
        load_secret "ANTHROPIC_API_KEY"
        load_secret "LINEAR_API_KEY"
        load_secret "GOOGLE_AI_API_KEY"
        load_secret "JINA_AI_API_KEY"
        load_secret "YOUTUBE_API_KEY"
        ;;
    infrastructure)
        # Infrastructure credentials
        load_secret "INFRASTRUCTURE_SUPABASE"
        load_secret "INFRASTRUCTURE_LANGFUSE"
        load_secret "NEO4J_GRAPHITI"
        load_secret "CLI_DEFAULT"
        load_secret "LANGFUSE_S3"
        ;;
    github)
        # GitHub PATs
        load_secret "GITHUB_PAT_GBLACK686"
        load_secret "NIH_GITHUB_PAT"
        ;;
    all)
        # All secrets
        load_secret "OPENAI_API_KEY"
        load_secret "ANTHROPIC_API_KEY"
        load_secret "LINEAR_API_KEY"
        load_secret "GOOGLE_AI_API_KEY"
        load_secret "JINA_AI_API_KEY"
        load_secret "YOUTUBE_API_KEY"
        load_secret "APIFY_API_TOKEN"
        load_secret "APIFY_TOKEN"
        load_secret "REF_TOOLS_API_KEY"
        load_secret "INFRASTRUCTURE_SUPABASE"
        load_secret "INFRASTRUCTURE_LANGFUSE"
        load_secret "NEO4J_GRAPHITI"
        load_secret "CLI_DEFAULT"
        load_secret "LANGFUSE_S3"
        load_secret "AMPLIFY"
        load_secret "POSTGRES_PASSWORD"
        load_secret "GITHUB_PAT_GBLACK686"
        load_secret "NIH_GITHUB_PAT"
        load_secret "ANTHROPIC"
        load_secret "API_KEY"
        load_secret "CREDENTIALS"
        load_secret "GOOGLE_SERVICE_ACCOUNT"
        load_secret "TELEGRAM"
        ;;
    *)
        echo "Unknown profile: $PROFILE" >&2
        echo "Available profiles: core, infrastructure, github, all" >&2
        return 1 2>/dev/null || exit 1
        ;;
esac

echo "Done!" >&2
