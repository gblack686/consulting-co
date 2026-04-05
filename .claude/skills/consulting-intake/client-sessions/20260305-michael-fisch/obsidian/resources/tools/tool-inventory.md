---
type: reference
title: Tool & API Inventory
tags: [tools, api, reference]
created: 2026-03-26
updated: 2026-03-26
---

# Tool & API Inventory

## Active Tools

| Tool | Purpose | API | Credentials Status |
|------|---------|-----|-------------------|
| **Claude Code** | AI agent runtime | Yes | Active — Michael has it installed |
| **Google Workspace** | Email, Drive, Calendar | OAuth | Needs OAuth token |
| **Airtable** | Operations / data management | REST API | Needs personal access token (Emil) |
| **QuickBooks** | Accounting | Intuit MCP or Python SDK | Needs developer setup (Emil) |
| **ShipStation** | Shipping / order management | REST API | Needs API key |
| **Lovable** | Customer portal frontend | N/A | Active — Piermont portal live |
| **Supabase** | Database | REST + SQL | Blocked on migration |
| **AWS** | Infrastructure | SDK | Needs sub-accounts provisioned |
| **OpenClaw** | Agent deployment | Gateway | Needs EC2 instance |

## Phase 2 Tools

| Tool | Purpose | For |
|------|---------|-----|
| **Twilio** | Phone/SMS | Gary's CS Agent |
| **ElevenLabs** | Voice AI | Gary's CS Agent |
| **Cin7** | Inventory | Piermont Brands |

## API Key Locations

All secrets will be stored in OpenClaw via `openclaw secrets set` once EC2 is deployed.
See [[../projects/openclaw-deploy|OpenClaw Deployment]] for full secrets checklist.
