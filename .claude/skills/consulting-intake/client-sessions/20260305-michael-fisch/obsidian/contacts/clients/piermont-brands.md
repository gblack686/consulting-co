---
type: client
title: Piermont Brands
tags: [client, piermont, cpg, ecommerce]
created: 2026-03-26
updated: 2026-03-26
status: active
industry: CPG / Ecommerce
primary_contact: Michael Fisch
---

# Piermont Brands

> Fish Group's primary test client. CPG brand house currently running a Lovable-built portal in production.

## Brands

| Brand | Category |
|-------|----------|
| **Chica Cheetah** | CPG |
| **Caya** | CPG |

## Tech Stack

| Tool | Purpose | Status |
|------|---------|--------|
| **Lovable** | Customer portal (frontend) | Live in production |
| **Supabase (Lovable Cloud)** | Database | Needs migration to own instance |
| **Airtable** | Operations/data | Active |
| **ShipStation** | Shipping / order management | Active |
| **QuickBooks** | Accounting | Active |
| **Cin7** | Inventory management | Phase 2 |

**12 API integrations** active in the Lovable portal. 8-9 employees currently using it.

## Agent Coverage

- [[agents/data-airtable|Data & Airtable Agent]] — Airtable CRUD, QuickBooks sync, ShipStation shipment requests
- [[agents/permissions|Permissions Agent]] — Google Workspace + AWS IAM access management

## Critical Blocker

**Supabase migration required**: Lovable currently uses its own hosted Supabase instance ("Lovable Cloud mode"). To give Finn and other agents direct database access, Piermont must migrate to their own Supabase instance.

Steps:
1. Create new Supabase project under Piermont's account
2. Export data from Lovable Cloud Supabase
3. Import into new project
4. Update Lovable to point to new Supabase URL + anon key
5. Provide service role key to OpenClaw secrets

See [[projects/supabase-migration]] for full project tracking.

## Notes

- Michael has known Greg since high school (travel soccer)
- Primary test bed for Fish Group agent automation
- 8-9 employees actively using Lovable portal daily
