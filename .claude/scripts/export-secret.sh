#!/bin/bash
# Export a secret as an environment variable
# Usage: eval $(./export-secret.sh SECRET_NAME [VAR_NAME])

SECRET_NAME="$1"
VAR_NAME="${2:-$SECRET_NAME}"

# Supabase config
SUPABASE_URL="${SUPABASE_URL:-https://unickqnwfheaczccvgbw.supabase.co}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-}"

if [ -z "$SECRET_NAME" ]; then
    echo "# Usage: eval \$(./export-secret.sh SECRET_NAME [VAR_NAME])" >&2
    echo "# Example: eval \$(./export-secret.sh OPENAI_API_KEY)" >&2
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "# Error: SUPABASE_SERVICE_KEY not set" >&2
    echo "# Set it with: export SUPABASE_SERVICE_KEY=your-service-key" >&2
    exit 1
fi

# Get secret from vault
SECRET_VALUE=$(curl -s -X POST \
    "${SUPABASE_URL}/rest/v1/rpc/get_secret" \
    -H "apikey: ${SUPABASE_SERVICE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"secret_name\": \"${SECRET_NAME}\"}" | tr -d '"')

if [ -z "$SECRET_VALUE" ] || [ "$SECRET_VALUE" == "null" ]; then
    echo "# Error: Secret '$SECRET_NAME' not found" >&2
    exit 1
fi

# Output export command
echo "export ${VAR_NAME}='${SECRET_VALUE}'"
