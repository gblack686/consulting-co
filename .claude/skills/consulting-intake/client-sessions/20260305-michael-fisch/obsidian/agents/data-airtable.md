---
type: agent
title: Data & Airtable Agent
tags: [agent, data, airtable, quickbooks]
created: 2026-03-26
updated: 2026-03-26
role: Data Operations
phase: 1
status: building
---

# Data & Airtable Agent

> Manages all data operations across Airtable, QuickBooks, and ShipStation. The financial and operational data backbone.

## Responsibilities

- Airtable CRUD operations (read, create, update, delete records)
- QuickBooks to Airtable sync
- ShipStation shipment requests and tracking
- Data discrepancy detection and flagging
- AR aging reports + follow-up draft generation

## Skills

| Skill | Description |
|-------|-------------|
| `airtable-sync` | Sync data between QuickBooks and Airtable |
| `shipment-request` | Create and track ShipStation shipments |
| `quickbooks-sync` | Pull QuickBooks data into Airtable |

## Triggers

```
/shipment [details]
/sync [client] [source]
/ar-aging [client]
```

## Key Integrations

| Tool | API | Status |
|------|-----|--------|
| **Airtable** | REST API (CRUD + webhooks) | Active |
| **QuickBooks** | Intuit MCP or Python SDK | Needs setup |
| **ShipStation** | REST API (orders, webhooks, carrier quotes) | Needs setup |
| **Cin7** | Inventory system (Piermont) | Phase 2 |

## QuickBooks Decision

Two paths evaluated in Session 2:
1. **Intuit MCP** — native integration, lower friction
2. **Python SDK** — more control, Emil has developer access

Decision: evaluate Intuit MCP first; fall back to Python SDK if rate limits or scope issues arise.

## Related Workflows

- [[../workflows/ar-aging-follow-up|AR Aging Follow-Up]]
- [[../workflows/daily-cash-position|Daily Cash Position]]
- [[../workflows/data-discrepancy-checker|Data Discrepancy Checker]]
