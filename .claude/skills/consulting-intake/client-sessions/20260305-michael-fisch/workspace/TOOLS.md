# Tools — Fish Group

## Secret Management: 1Password

Secrets stored in 1Password vault `Client-FischGroup` with scoped service account `openclaw-fischgroup`.

```bash
# Local dev — inject secrets at runtime (never touch disk)
export OP_SERVICE_ACCOUNT_TOKEN="ops_..."
op run --env-file=.env.secrets -- claude

# OpenClaw on Mac Mini — use 1Password Connect Server (REST API on localhost:8080)
op run --env-file=.env.secrets -- openclaw start
```

## Phase 1 (Internal)

| Tool | API | Priority | Status | 1Password Item |
|------|-----|----------|--------|----------------|
| Microsoft 365 (Outlook, OneDrive, Teams) | Yes | Critical | Needs Azure AD app registration | `op://Client-FischGroup/microsoft-365/*` |
| GitHub (Fisch-Group org) | Yes | Critical | Needs scoped PAT (repo read/write) | `op://Client-FischGroup/github/personal-access-token` |
| Airtable | Yes | Critical | Emil to generate personal access token | `op://Client-FischGroup/airtable/api-key` |
| QuickBooks | Yes | High (Piermont) | Needs API credentials from Piermont | `op://Client-FischGroup/quickbooks/*` |
| ShipStation | Yes | High (Piermont) | Needs API key from Piermont admin | `op://Client-FischGroup/shipstation/*` |
| Supabase | Yes | High | Blocked until migration | `op://Client-FischGroup/supabase/*` |

## Phase 2 (Client-Facing)

| Tool | API | Priority | Status |
|------|-----|----------|--------|
| Twilio (voice/SMS) | Yes | Phase 2 | Not yet — Gary's CS |
| ElevenLabs (voice AI) | Yes | Phase 2 | Not yet — Gary's CS phone support |
| Gary's POS/order system | TBD | Phase 2 | Unknown — need to identify Gary's order system |
| LinkedIn | Yes | Phase 2 | Mentioned — business development use case |

## `.env.secrets` (1Password references — gitignored, no real values)

```bash
# Shared
OPENROUTER_API_KEY="op://GBAutomation-Shared/openrouter/api-key"

# Microsoft 365
MS_CLIENT_ID="op://Client-FischGroup/microsoft-365/client-id"
MS_CLIENT_SECRET="op://Client-FischGroup/microsoft-365/client-secret"
MS_TENANT_ID="op://Client-FischGroup/microsoft-365/tenant-id"
MS_REFRESH_TOKEN="op://Client-FischGroup/microsoft-365/refresh-token"

# GitHub
GITHUB_TOKEN="op://Client-FischGroup/github/personal-access-token"
GITHUB_ORG="Fisch-Group"

# Airtable
AIRTABLE_API_KEY="op://Client-FischGroup/airtable/api-key"

# QuickBooks (Piermont)
QUICKBOOKS_CLIENT_ID="op://Client-FischGroup/quickbooks/client-id"
QUICKBOOKS_CLIENT_SECRET="op://Client-FischGroup/quickbooks/client-secret"
QUICKBOOKS_REFRESH_TOKEN="op://Client-FischGroup/quickbooks/refresh-token"

# ShipStation (Piermont)
SHIPSTATION_API_KEY="op://Client-FischGroup/shipstation/api-key"
SHIPSTATION_API_SECRET="op://Client-FischGroup/shipstation/api-secret"

# Supabase (blocked until migration)
SUPABASE_URL="op://Client-FischGroup/supabase/url"
SUPABASE_SERVICE_KEY="op://Client-FischGroup/supabase/service-key"
```

## 1Password Vault Items to Create

| Item | Type | Fields |
|------|------|--------|
| `microsoft-365` | API Credential | `client-id`, `client-secret`, `tenant-id`, `refresh-token` |
| `github` | API Credential | `personal-access-token`, `org-name` |
| `airtable` | API Credential | `api-key` |
| `quickbooks` | API Credential | `client-id`, `client-secret`, `refresh-token` |
| `shipstation` | API Credential | `api-key`, `api-secret` |
| `supabase` | API Credential | `url`, `service-key` |
