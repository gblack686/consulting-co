---
type: workflow
title: New Client Workspace Generator
tags: [workflow, onboarding, airtable, aws]
created: 2026-03-26
updated: 2026-03-26
status: planned
priority: high
phase: 1
agent: Client Ops Agent
trigger: manual
---

# New Client Workspace Generator

> One command spins up everything needed for a new Fish Group client.

## Trigger

**Manual**: `/onboard [client name]`

## Steps

1. Collect client info (name, industry, primary contact, email)
2. Create Airtable base from Fish Group template
3. Create Google Drive folder structure:
   - `/Fish Group Clients/[Client Name]/`
   - Subfolders: Financials, Contracts, Reports, Correspondence
4. Provision AWS sub-account (Fish Group AWS Org)
5. Set up IAM roles and permissions
6. Draft welcome email with portal access instructions
7. Require Michael approval before sending email
8. Log new client in master Airtable clients table
9. Create client file in vault: `/contacts/clients/{client-name}.md`

## Human-in-Loop Gates

1. Before AWS account creation (cost implications)
2. Before welcome email is sent

## Output

```
New Client Workspace Ready — [Client Name]

Created:
  Airtable Base: [link]
  Google Drive: [link]
  AWS Account: [account-id]
  Vault File: /contacts/clients/{name}.md

Pending your approval:
  Welcome email draft: [view]

Approve send? [Y/N]
```

## Prerequisites

- [ ] Airtable client template base ID configured
- [ ] Google Drive service account credentials
- [ ] AWS Organizations access (management account)

## Related

- [[../agents/client-ops|Client Ops Agent]]
