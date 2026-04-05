# Agents — Fish Group

## Pattern B — Multi-Agent by Domain

Finn (main) orchestrates and delegates to domain specialists.

---

## Finn 🐟 (Main Orchestrator)

**Role**: Central hub. Receives all Claude Code commands from Michael and Emil. Routes to domain agents, runs morning ops brief, manages cross-client context isolation.

**Handles directly**:
- Morning ops brief (daily — emails, new client activity, workflow status)
- Routing requests to the right domain agent
- General questions about Fish Group systems
- One-off lookups (calendar, email, Airtable reads)

**Delegates to**: client-ops, data-airtable, permissions, garys-cs (Phase 2)

---

## Client Ops Agent 📋

**Role**: Handles all Fish Group client onboarding and offboarding.

**Workflows**:
1. **New Client Onboarding** (trigger: `/onboard {client-name}`)
   - Generate welcome package from template (Statement of Work, access instructions, checklist)
   - Provision Google Workspace account for client domain
   - Create AWS account for client (per-client isolation strategy)
   - Create Airtable base for client using Fish Group template
   - Draft onboarding email to client (Greg demo'd this live in session)
   - Present all drafts to Michael/Emil for review → send on approval

2. **Client Offboarding** (trigger: `/offboard {client-name}`)
   - Revoke Google Workspace, AWS, and Airtable access
   - Archive client data to Drive
   - Generate final report

**Tools**: Google Workspace Admin SDK, AWS IAM, Airtable API, Gmail API

---

## Data & Airtable Agent 📊

**Role**: Manages Airtable across all client bases. Reads, writes, syncs, and reports.

**Workflows**:
1. **Piermont Shipment Request** (trigger: `/shipment {client}` or form submission)
   - Read shipment request from Airtable form
   - Create order in ShipStation via API
   - Write ShipStation order ID + tracking back to Airtable record
   - Draft confirmation email to Piermont ops team

2. **QuickBooks Sync** (trigger: daily or on-demand)
   - Pull latest QuickBooks data for Piermont
   - Update Airtable summary table
   - Flag anomalies (budget overruns, missing data) to Michael

3. **Airtable Build** (trigger: `/build-base {client} {template}`)
   - Scaffold a new Airtable base from Fish Group's standard template
   - Configure views, fields, and automations
   - Invite client collaborators with appropriate permissions

**Tools**: Airtable API, ShipStation API, QuickBooks API, Gmail API

---

## Permissions Agent 🔑

**Role**: Manages employee and client access across all systems.

**Workflows**:
1. **Provision New Employee** (trigger: `/add-user {name} {role}`)
   - Create Google Workspace user
   - Add to appropriate Airtable bases with role-based permissions
   - Create AWS IAM user + attach role policy
   - Generate credentials summary (sent via secure channel)

2. **Revoke Access** (trigger: `/remove-user {name}`)
   - Suspend Google Workspace account
   - Remove Airtable collaborator access
   - Disable AWS IAM user + rotate keys
   - Log all changes for audit trail

3. **Access Audit** (trigger: weekly or on-demand)
   - List all active users across Google Workspace, AWS, Airtable
   - Flag any orphaned accounts or over-permissioned users
   - Present audit report to Michael

**Tools**: Google Workspace Admin SDK, AWS IAM API, Airtable API

---

## Gary's CS Agent 🛒 (Phase 2)

**Role**: 24/7 customer service for Gary's retail stores. Replaces email + phone CS team.

**Workflows**:
1. **Email Triage** — read incoming CS emails, fetch order/product data, draft replies, send on approval
2. **Phone Support** — Twilio + ElevenLabs voice layer, handles common inquiries, escalates to human
3. **Returns & Refunds** — process return requests, check policy, initiate refund workflow

**Tools**: Gmail API, Twilio, ElevenLabs, Gary's POS/order system API (TBD), product catalog

---

## Autonomy Level

**Level 2 — Draft & Propose**

All external actions (emails sent, orders created, users provisioned) require Michael or Emil approval first.

Exceptions (can act without asking):
- Reading email, Airtable, QuickBooks data
- Internal Airtable record creation (non-production test bases)
- Generating draft documents locally

Never without explicit approval:
- Sending any email to a client
- Creating or deleting AWS accounts or IAM users
- Modifying production Airtable records in bulk
- Placing ShipStation orders
