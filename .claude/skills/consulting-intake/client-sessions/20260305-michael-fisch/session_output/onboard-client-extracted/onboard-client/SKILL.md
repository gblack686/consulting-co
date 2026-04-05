---
name: onboard-client
description: >
  New client onboarding workflow for the Fisch Group fractional CFO practice.
  Invoke this skill whenever a new client is being onboarded — whether the user types
  `/onboard-client`, says "onboard a new client", "set up a new client workspace",
  "we have a new client", or asks to "provision" or "create" a client portal.
  This skill orchestrates the full setup sequence: GitHub repo fork, Supabase table
  provisioning, Lovable portal configuration, intake survey generation, and welcome
  email drafting — with mandatory human approval gates before any irreversible action.
---

# WF-003: New Client Workspace Generator

## Overview

This skill provisions a full client workspace for a new Fisch Group client. It is deliberately
designed with human-in-the-loop checkpoints: no infrastructure is created, and no emails sent,
until a human has reviewed and approved. Accuracy matters more than speed here.

**Trigger format:**
```
/onboard-client "Company Name" "contact@email.com"
```
You can also infer these from context if the user provides them conversationally.

---

## Step 0 — Parse Inputs

Extract:
- `COMPANY_NAME` — the client's company name (used for repo slug, Supabase project, display name)
- `CONTACT_EMAIL` — the primary contact's email
- `REPO_SLUG` — lowercase, hyphenated version of the company name (e.g., "Acme Corp" → `acme-corp`)

If either is missing, ask before proceeding.

---

## Step 1 — Generate Workspace Summary (HITL Checkpoint #1)

Before touching any system, present the following summary to the user and ask for explicit approval:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEW CLIENT WORKSPACE PROPOSAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Company:        {COMPANY_NAME}
  Contact email:  {CONTACT_EMAIL}
  Repo slug:      {REPO_SLUG}

  WHAT WILL BE CREATED:
  ✦ GitHub repo:      fisch-group/{REPO_SLUG}
    (forked from fisch-group/client-portal-template)
  ✦ Supabase project: {REPO_SLUG}
    Tables: clients, transactions, reports, users,
            platform_credentials, documents
  ✦ Lovable project:  {COMPANY_NAME} Portal
    (configured from portal template)
  ✦ Intake survey:    Drafted for your review
  ✦ Welcome email:    Drafted for your review (NOT sent until you approve)

  MANUAL STEPS REMAINING AFTER THIS RUN:
  □ Enter QuickBooks API key / OAuth credentials
  □ Enter Cin7 API key
  □ Enter any bank feed credentials
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Does everything look right? Type "yes" to continue, or tell me what to change.
```

Do not proceed until the user confirms.

---

## Step 2 — Fork GitHub Repo

Use the GitHub REST API via Bash to fork the template repo:

```bash
# Fork the template repo
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/fisch-group/client-portal-template/forks \
  -d '{"organization": "fisch-group", "name": "{REPO_SLUG}"}'
```

If `GITHUB_TOKEN` is not set in the environment, pause and ask the user to provide it or confirm it's configured.

**Validation gate:** After the API call, verify the repo exists by hitting
`https://api.github.com/repos/fisch-group/{REPO_SLUG}` and confirming a 200 response.
Report the repo URL to the user: `https://github.com/fisch-group/{REPO_SLUG}`

If the fork fails (e.g., repo already exists, permissions error), surface the exact error message
and pause — do not continue to Supabase provisioning until GitHub is confirmed.

---

## Step 3 — Provision Supabase Project & Tables

Use the Supabase MCP tools to create the project and run the schema migration.

### 3a. Create the Supabase project

Use `create_project` with:
- `name`: `{REPO_SLUG}`
- `organization_id`: retrieve via `get_organization` or `list_organizations` first
- `region`: `us-east-1` (default — confirm with user if they have a preference)

Wait for the project to become active before continuing (poll `get_project` until status is `ACTIVE_HEALTHY`).

### 3b. Run the schema migration

Use `apply_migration` to create the standard Fisch Group schema. The SQL for the migration is in
`references/schema.sql` — read that file and use it as the migration content.

**Validation gate:** After migration, use `list_tables` to confirm all 6 tables exist:
`clients`, `transactions`, `reports`, `users`, `platform_credentials`, `documents`

Report the Supabase project URL to the user.

---

## Step 4 — Configure Lovable Portal

Lovable is a web-based tool at https://lovable.dev. Use Claude in Chrome to:

1. Navigate to https://lovable.dev and confirm you're logged in
2. Find the existing `client-portal-template` project
3. Duplicate/fork it as a new project named `{COMPANY_NAME} Portal`
4. Update the project's configuration:
   - Set the Supabase project URL and anon key from Step 3
   - Set the client display name to `{COMPANY_NAME}`

**Important:** Lovable's UI can change. Use `read_page` to understand what's on screen before
taking actions. If you're uncertain about a step, pause and describe what you see to the user
rather than guessing. The user has flagged that human oversight is important here — do not
make changes you're not confident about.

If you cannot complete a Lovable step confidently, document it as a manual step for the user
instead of forcing it through.

---

## Step 5 — Generate Intake Survey

Create a formatted intake survey document (Markdown) that the team will send to the new client.
The survey should cover all four areas below. Save it as `{REPO_SLUG}-intake-survey.md` in the
outputs folder.

### Survey sections to include:

**Section A: Company Information**
- Legal entity name
- EIN / Tax ID
- State of incorporation
- Fiscal year end
- Primary business address
- Billing contact name & email

**Section B: Platform Access**
- QuickBooks: account type (Online/Desktop), admin email, whether to set up OAuth or API key access
- Cin7: account URL, API user email
- Bank feeds: list of banks/institutions, preferred connection method
- Any other financial platforms in use (payroll, expenses, etc.)

**Section C: Team Roster**
- List of client-side team members who will access the portal
  (Name, email, role/title, permission level: view-only or full access)
- Primary point of contact for day-to-day questions
- Executive sponsor / decision maker

**Section D: Document Access**
- Prior year financials (P&L, Balance Sheet) — request upload or link
- Chart of accounts (if customized)
- Any existing management reports or KPI dashboards
- Contracts or agreements relevant to financial reporting

Present the survey to the user for review before mentioning it in the welcome email.

---

## Step 6 — Draft Welcome Email (HITL Checkpoint #2)

Draft the welcome email and present it to the user. **Do not send until explicitly approved.**

```
Subject: Welcome to Fisch Group — Your Client Portal is Ready

Hi [Contact Name],

Welcome to the Fisch Group family! We're excited to kick off our engagement
with {COMPANY_NAME}.

To get started, we've set up a dedicated portal for your team. Your next step
is completing our brief intake form, which helps us connect to your financial
platforms and get your team set up with access.

👉 [Intake Survey Link — to be added after survey is hosted]

The form covers:
• Your company details and team roster
• Platform access (QuickBooks, Cin7, banking)
• Any existing financial documents you'd like to share

It should take about 10–15 minutes. Once submitted, we'll configure your portal
and be in touch within 1–2 business days.

In the meantime, feel free to reach out to [YOUR NAME] at [YOUR EMAIL] with
any questions.

Looking forward to working together,
[YOUR NAME]
Fisch Group
```

Ask the user:
1. Is the email content right, or do you want to adjust the tone/details?
2. Who should be listed as the sender (name + email)?
3. Should we send now via Outlook, or do you want to send manually?

Only send via Outlook if the user explicitly says to send now.

---

## Step 7 — Final Checklist & Handoff

Present a completion summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ONBOARDING COMPLETE — {COMPANY_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ GitHub repo:     github.com/fisch-group/{REPO_SLUG}
  ✅ Supabase:        [project URL]
  ✅ Lovable portal:  [project URL] (or ⚠️ manual setup needed)
  ✅ Intake survey:   {REPO_SLUG}-intake-survey.md
  ✅ Welcome email:   Drafted / Sent (per your choice)

  REMAINING MANUAL STEPS:
  □ Enter QuickBooks API key or complete OAuth setup
    → Add to Supabase: platform_credentials table, platform = 'quickbooks'
  □ Enter Cin7 API key
    → Add to Supabase: platform_credentials table, platform = 'cin7'
  □ Enter bank feed credentials
    → Add to Supabase: platform_credentials table, platform = 'bank_{institution}'
  □ Host the intake survey and update the welcome email link
  □ Schedule kickoff call with {COMPANY_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Error Handling Philosophy

This workflow touches live infrastructure. The guiding principle is: **pause and confirm rather
than guess and proceed.** Specifically:

- If any API call fails, stop and report the exact error before trying the next step
- If you're unsure whether a destructive action (deleting, overwriting) is about to happen, ask
- If a step requires a credential that isn't available, list what's needed and wait
- Never retry a failed infrastructure step automatically — surface the failure first

The user has explicitly flagged that human oversight is critical here.
