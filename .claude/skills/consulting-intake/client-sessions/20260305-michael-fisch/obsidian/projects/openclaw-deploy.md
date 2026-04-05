---
type: project
title: OpenClaw EC2 Deployment
tags: [project, openclaw, infrastructure]
created: 2026-03-26
updated: 2026-03-26
status: planned
priority: high
---

# OpenClaw EC2 Deployment

> Deploy Finn and all specialist agents to an EC2 instance running OpenClaw.

## Steps

1. [ ] Provision EC2 instance (t3.small or t3.medium, ~$20-40/mo)
2. [ ] SSH in, install OpenClaw
3. [ ] Upload `workspace/openclaw.json` config
4. [ ] Add all secrets (see secrets checklist below)
5. [ ] Start Finn gateway on port 18789
6. [ ] Test with `/brief`

## Secrets Required

| Secret Key | Source | Status |
|------------|--------|--------|
| `GOOGLE_OAUTH_TOKEN` | Emil/Michael's Google account | Not set |
| `AIRTABLE_API_KEY` | Airtable settings | Not set |
| `QUICKBOOKS_CLIENT_ID` | Emil's developer account | Not set |
| `QUICKBOOKS_CLIENT_SECRET` | Emil's developer account | Not set |
| `SHIPSTATION_API_KEY` | ShipStation account | Not set |
| `AWS_ACCESS_KEY_ID` | Fish Group AWS | Not set |
| `AWS_SECRET_ACCESS_KEY` | Fish Group AWS | Not set |
| `SUPABASE_URL` | After migration | Blocked |
| `SUPABASE_SERVICE_KEY` | After migration | Blocked |

## Related

- [[../agents/finn|Finn]]
- [[supabase-migration|Supabase Migration (blocker)]]
