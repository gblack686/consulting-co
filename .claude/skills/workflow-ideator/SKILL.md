---
name: workflow-ideator
description: "AI-generate workflow and skill ideas for a consulting client based on their business domain, APIs, pain points, and session context. Produces a prioritized catalog of automatable workflows with human-in-the-loop gates, validation steps, and complexity estimates."
---

# Workflow Ideator

## Overview

Takes everything we know about a client — profile, transcripts, tool inventory, session reports, business domain — and AI-generates a comprehensive catalog of workflows and skills that could be built for them. Combines general domain knowledge (e.g., "every accounting firm needs X") with client-specific context (e.g., "Piermont has 12 API integrations and AR aging follow-ups").

## When to Use

- After a consulting session when you need to brainstorm deliverables
- When a client asks "what else can we automate?"
- To generate a roadmap of skills to build over multiple sessions
- To prioritize which workflows to build first based on impact vs. effort

## Usage

```
/workflow-ideator <client-session-dir>
```

Example:
```
/workflow-ideator client-sessions/20260305-michael-fisch
```

## Inputs

The skill reads from the client session directory:

| File | Purpose | Required |
|------|---------|----------|
| `session_output/client_profile.json` | Business type, team, clients, focus areas | Yes |
| `session_output/tool_inventory.json` | APIs, tools, integrations available | Yes |
| `session_output/*.md` | Session reports, research, transcripts | Optional |
| `workspace/AGENTS.md` | Existing agent definitions | Optional |
| `workspace/TOOLS.md` | Existing tool connections | Optional |
| `PACKAGE_SUMMARY.md` | Prior deliverables and next steps | Optional |
| `diagrams/` | Architecture diagrams | Optional |

## Process

### Step 1: Load Client Context

Read all available files from the session directory. Extract:
- **Business type** (e.g., accounting firm, e-commerce, SaaS)
- **Team composition** (who does what, technical skill level)
- **Clients** (who are their customers, what industries)
- **APIs/Tools** (what's connected, what's available)
- **Pain points** (what they complained about, what takes too long)
- **Existing workflows** (what they've already built)
- **Quotes/priorities** (what the client explicitly asked for)

### Step 2: Generate Domain Workflows (General)

Based on the business type, generate workflows that ANY business in that domain would benefit from. Use domain knowledge:

**For Accounting/Finance firms:**
- AR aging follow-up emails
- AP payment scheduling
- Monthly close checklist automation
- Client onboarding / offboarding
- Bank reconciliation alerts
- Tax document collection
- Revenue recognition tracking
- Expense report processing
- Payroll discrepancy detection
- Audit trail generation

**For E-commerce:**
- Inventory reorder alerts
- Shipping status notifications
- Customer review response
- Return/refund processing
- Price comparison monitoring
- Product listing optimization

**For Any B2B Service:**
- Client health scoring
- Meeting prep automation
- Invoice generation and follow-up
- Proposal generation
- Contract renewal reminders
- Time tracking aggregation
- Weekly/monthly client reports

### Step 3: Generate Client-Specific Workflows (Custom)

Based on the specific client's APIs, pain points, and requests, generate custom workflows that are unique to their situation. These should reference:
- Specific API integrations they have
- Specific clients they serve
- Specific team members and their roles
- Specific pain points from transcripts

### Step 4: Classify and Prioritize

For each workflow, determine:

| Field | Description |
|-------|-------------|
| **Name** | Short descriptive name |
| **Category** | Domain (general) or Custom (client-specific) |
| **Description** | What it does, why it matters |
| **APIs Required** | Which integrations are needed |
| **Trigger** | What starts the workflow (schedule, event, manual) |
| **Human-in-the-Loop** | Where humans must review/approve |
| **Validation Gates** | How to verify it worked correctly |
| **Complexity** | Low / Medium / High |
| **Impact** | Low / Medium / High |
| **Priority Score** | Impact / Complexity ratio (high impact + low complexity = do first) |
| **Prerequisites** | What needs to be set up first |
| **Estimated Build Time** | Rough time to build the skill |

### Step 5: Output

Generate two files:

#### 1. `workflow-catalog.md` — Human-readable report

```markdown
# Workflow Catalog — {Client Name}
Generated: {date}

## Executive Summary
{count} workflows identified across {n} categories.
Top 5 quick wins: ...

## Quick Wins (High Impact, Low Complexity)
### 1. {Workflow Name}
- **What**: {description}
- **APIs**: {list}
- **Trigger**: {schedule/event/manual}
- **Human-in-the-Loop**: {where humans review}
- **Validation**: {how to verify}
- **Build Time**: {estimate}
...

## Medium Effort (High Impact, Medium Complexity)
...

## Strategic (High Impact, High Complexity)
...

## Nice-to-Have (Medium/Low Impact)
...

## Prerequisites Checklist
- [ ] {API key / credential needed}
- [ ] {Integration to set up}
...
```

#### 2. `workflow-catalog.json` — Machine-readable catalog

```json
{
  "client": "...",
  "generated": "2026-03-12",
  "workflows": [
    {
      "id": "wf-001",
      "name": "...",
      "category": "domain|custom",
      "description": "...",
      "apis": ["QuickBooks", "Gmail"],
      "trigger": "schedule|event|manual",
      "schedule": "weekly|daily|monthly",
      "human_in_the_loop": [
        {"step": "review_email", "description": "Review generated email before sending"}
      ],
      "validation_gates": [
        {"gate": "data_check", "description": "Verify AR amounts match QuickBooks totals"}
      ],
      "complexity": "low|medium|high",
      "impact": "low|medium|high",
      "priority_score": 9,
      "prerequisites": ["quickbooks_api_key", "gmail_oauth"],
      "estimated_hours": 2,
      "status": "idea"
    }
  ]
}
```

## Output Location

All output goes to the client session directory:
```
client-sessions/{session}/session_output/
├── workflow-catalog.md
└── workflow-catalog.json
```

## Human-in-the-Loop Patterns

When generating workflows, apply these standard HITL patterns:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Review Before Send** | Any external communication | Review AR follow-up email before sending |
| **Approve Before Execute** | Financial transactions, data changes | Approve payment before processing |
| **Alert and Wait** | Anomaly detection | Flag unusual transaction, wait for human decision |
| **Batch Review** | High-volume repetitive tasks | Review batch of 20 vendor emails, approve all or edit |
| **Escalation** | When confidence is low | Agent unsure about categorization, escalate to human |
| **Audit Log** | Compliance-sensitive operations | Log all changes for review, no blocking gate |

## Validation Gate Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Data Reconciliation** | Compare output against source | AR totals match QuickBooks |
| **Format Check** | Verify output structure | Email has subject, body, correct recipient |
| **Threshold Check** | Verify values within bounds | Invoice amount < $10,000 (flag if above) |
| **Duplicate Detection** | Prevent duplicate actions | Don't send follow-up if already sent this week |
| **Rollback Ready** | Can undo the action | Draft email (not sent), staged data (not committed) |
| **Cross-Reference** | Verify against another system | Shipping address matches CRM record |

## Example: Fish Group

Running `/workflow-ideator client-sessions/20260305-michael-fisch` would generate workflows like:

**Quick Wins:**
1. AR Aging Follow-Up (QuickBooks + Gmail) — weekly automated vendor statements
2. New Client Workspace Setup (Lovable + Supabase + GitHub) — templated onboarding
3. Daily Cash Position Report (QuickBooks + Plaid) — morning summary email

**Medium Effort:**
4. Vendor Payment Scheduler (QuickBooks + Plaid) — schedule payments with approval
5. Multi-Client Dashboard Refresh (Cin7 + QuickBooks + Supabase) — sync all data nightly
6. Client Health Score (QuickBooks + Airtable) — weekly scoring of client engagement

**Strategic:**
7. Full Client Onboarding Agent (all APIs) — end-to-end workspace + API provisioning
8. AI-Powered Financial Review (QuickBooks + Claude) — monthly anomaly detection
9. Customer Service Agent for Gary's (Email + QuickBooks + ShipStation) — automated responses

## Notes

- Always include at least one HITL gate per workflow that touches external systems
- Financial workflows should ALWAYS have an approval gate before money moves
- Start with "Review Before Send" pattern for any email/notification workflows
- Prefer "Draft → Review → Send" over "Send → Undo" patterns
- Each workflow should be buildable as a standalone Claude Code skill
