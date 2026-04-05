---
type: agent
title: Client Ops Agent
tags: [agent, client-ops, onboarding]
created: 2026-03-26
updated: 2026-03-26
role: Client Onboarding & Offboarding
phase: 1
status: building
---

# Client Ops Agent

> Handles the full lifecycle of Fish Group client onboarding and offboarding. Provisions AWS accounts, creates Airtable bases, generates welcome packages.

## Responsibilities

- New client workspace generation (Airtable base, Google Drive folder, welcome email draft)
- AWS sub-account provisioning per client (one account per client strategy)
- Client offboarding + access revocation
- Welcome package creation

## Skills

| Skill | Description |
|-------|-------------|
| `client-onboarding` | End-to-end new client setup |
| `client-offboarding` | Clean client offboarding + access removal |
| `setup-openclaw` | Deploy OpenClaw for new client environment |

## Trigger

```
/onboard [client name]
```

## Workflow

1. Receive onboarding request from [[finn|Finn]]
2. Create Airtable base from template
3. Provision AWS sub-account (if needed)
4. Set up Google Drive folder structure
5. Draft welcome email (requires Michael approval)
6. Log completion to Finn

## Related Workflows

- [[../workflows/new-client-workspace|New Client Workspace Generator]]
