---
type: project
title: Supabase Migration
tags: [project, supabase, piermont, blocker]
created: 2026-03-26
updated: 2026-03-26
status: blocked
priority: critical
---

# Supabase Migration

> Migrate Piermont Brands from Lovable Cloud Supabase to their own Supabase instance. **Critical blocker** — agents cannot access Piermont data until this is done.

## Status: Blocked

Waiting on Emil to create Supabase project and export existing data.

## Why This Matters

Lovable's "Cloud mode" hosts Supabase internally — no external API access. Finn and the Data Agent need direct database access to run workflows (cash position, AR aging, discrepancy checks).

## Steps

1. [ ] Emil creates new Supabase project under Piermont's account
2. [ ] Export data from Lovable Cloud Supabase
3. [ ] Import into new Supabase project
4. [ ] Update Lovable to point to new Supabase URL + anon key
5. [ ] Test portal still works with new Supabase
6. [ ] Provide service role key to OpenClaw secrets
7. [ ] Verify agent access to Piermont data

## Related

- [[../contacts/clients/piermont-brands|Piermont Brands]]
- [[../agents/data-airtable|Data & Airtable Agent]]
- [[../tasks/blockers|Blockers]]
