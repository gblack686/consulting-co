# Secret Mapping: AWS → Supabase Vault

## Migration completed: 2026-02-03

23 secrets migrated from AWS Secrets Manager to Supabase Vault.
Both systems retain the secrets (AWS as backup).

## Name Mapping

| Vault Name | AWS Name | Type |
|------------|----------|------|
| `OPENAI_API_KEY` | `gbautomation/core/openai-api-key` | API Key |
| `ANTHROPIC_API_KEY` | `gbautomation/core/anthropic-api-key` | API Key |
| `APIFY_API_TOKEN` | `gbautomation/core/apify-api-token` | API Token |
| `APIFY_TOKEN` | `gbautomation/core/apify-token` | API Token |
| `REF_TOOLS_API_KEY` | `gbautomation/core/ref-tools-api-key` | API Key |
| `GOOGLE_AI_API_KEY` | `gbautomation/core/google-ai-api-key` | API Key |
| `JINA_AI_API_KEY` | `gbautomation/core/jina-ai-api-key` | API Key |
| `LINEAR_API_KEY` | `gbautomation/core/linear-api-key` | API Key |
| `YOUTUBE_API_KEY` | `gbautomation/core/youtube-api-key` | API Key |
| `GOOGLE_SERVICE_ACCOUNT` | `gbautomation/core/google-service-account` | JSON Credentials |
| `INFRASTRUCTURE_SUPABASE` | `gbautomation/infrastructure/supabase` | JSON Credentials |
| `NEO4J_GRAPHITI` | `gbautomation/infrastructure/neo4j-graphiti` | JSON Credentials |
| `INFRASTRUCTURE_LANGFUSE` | `gbautomation/infrastructure/langfuse` | JSON Credentials |
| `CLI_DEFAULT` | `gbautomation/aws/cli-default` | JSON Credentials |
| `LANGFUSE_S3` | `gbautomation/aws/langfuse-s3` | JSON Credentials |
| `AMPLIFY` | `gbautomation/projects/gb-automation-landing/amplify` | JSON Credentials |
| `POSTGRES_PASSWORD` | `gbautomation/supabase/.../postgres_password` | Password |
| `GITHUB_PAT_GBLACK686` | `github-pat-gblack686` | PAT |
| `NIH_GITHUB_PAT` | `nih-github-pat` | PAT |
| `ANTHROPIC` | `claude-observability/anthropic` | API Key |
| `API_KEY` | `core/api-key` | API Key |
| `CREDENTIALS` | `core-neo4j/credentials` | JSON Credentials |
| `TELEGRAM` | `gbautomation/integrations/telegram` | JSON Credentials |

## Quick Usage

### Get a single secret (Vault)
```bash
# Bash
./get-secret.sh OPENAI_API_KEY

# Windows
get-secret.bat OPENAI_API_KEY
```

### Get a single secret (AWS)
```bash
# Bash
./get-secret.sh OPENAI_API_KEY --aws

# Windows
get-secret-aws.bat gbautomation/core/openai-api-key
```

### Export to environment variable
```bash
eval $(./export-secret.sh OPENAI_API_KEY)
```

### Load multiple secrets by profile
```bash
source ./load-secrets.sh core           # API keys
source ./load-secrets.sh infrastructure # Infra creds
source ./load-secrets.sh github         # GitHub PATs
source ./load-secrets.sh all            # Everything
```

## Prerequisites

Set the Supabase service key:
```bash
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Or in Windows:
```cmd
set SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Cost Comparison

| System | 23 Secrets/month | API Calls |
|--------|-----------------|-----------|
| AWS Secrets Manager | $9.20 + API costs | $0.05/10k |
| **Supabase Vault** | **$0** | **$0** |

**Monthly savings: ~$10+**

## SQL Functions Available

```sql
-- Get a secret by name
SELECT public.get_secret('OPENAI_API_KEY');

-- Get secret with default fallback
SELECT public.get_secret_or_default('MISSING_KEY', 'default-value');

-- List all secrets (metadata only)
SELECT * FROM public.list_vault_secrets();
```
