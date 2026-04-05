# My Second Brain - Requirements Template

> Fish Group — filled out by GBAutomation on behalf of Emil Caplow & Michael Fisch

---

## 1. About You

- **Name:** Emil Caplow (primary operator), Michael Fisch (exec sponsor)
- **Role/Title:** Emil: Operations Lead at Fish Group (accounting & finance consulting firm). Michael: CFO / Managing Partner at Piermont Brands and Fish Group.
- **What I do daily** (1-2 sentences): Manage multi-client accounting engagements — onboarding new clients, running month-end close processes, tracking AR/AP across QuickBooks for multiple companies, coordinating with team members on deliverables, and maintaining the Lovable-built client portal (Piermont Brands).
- **Timezone:** Eastern (US)

---

## 2. Your Platforms

Check every platform you actively use and fill in the specific tool:

- [X] Email (e.g., Gmail, Outlook): Outlook (Fish Group internal), Gmail (3 clients on Google Workspace)
- [X] Calendar (e.g., Google Calendar, Outlook Calendar): Outlook Calendar
- [X] Task Management (e.g., Asana, Linear, Todoist, Jira): Airtable (task tracking per client)
- [X] Chat/Messaging (e.g., Slack, Discord, Teams): Slack (internal team + some clients)
- [X] Notes/Documents (e.g., Notion, Obsidian, Google Docs): Google Docs (client-facing), Lovable portal (internal dashboards)
- [X] Cloud Storage (e.g., Google Drive, Dropbox, OneDrive): OneDrive (Fish Group internal), Google Drive (client deliverables)
- [X] Code Hosting (e.g., GitHub, GitLab): GitHub (@Fisch-Group org — clientflow-dashboard, elevate-trust-showcase)
- [ ] Community (e.g., Circle, Discord server, Mighty Networks): ___
- [ ] CRM (e.g., HubSpot, Salesforce, Pipedrive): ___
- [X] Other: QuickBooks Online (multi-company — one per client, core of the business)
- [X] Other: Lovable.dev (client portal builder — React/Vite + Supabase)
- [X] Other: ShipStation (Piermont Brands order fulfillment)
- [X] Other: 1Password (credential management)

---

## 3. Top Tasks for AI

List 3-5 tasks you'd want your second brain to handle proactively:

**My list:**

1. Daily cash position summary — pull balances from QuickBooks (AR/AP/bank) across all client companies every morning, email a one-page report to Michael
2. AR aging follow-up emails — weekly, pull aging receivables per vendor from QuickBooks, draft follow-up emails for review before sending
3. New client onboarding — when a new client signs, create GitHub repo from template, provision Supabase tables, configure Lovable portal, send intake survey and welcome email
4. Data discrepancy checker — daily, compare QuickBooks source data against what's displayed in the Lovable portal (via Supabase), flag mismatches
5. Month-end close task tracker — track close process milestones per client in Airtable, nudge team members on overdue items, generate status report

---

## 4. Proactivity Level

How bold should your agent be? Pick one:

- [ ] **Observer** - Notify only, never take action
- [X] **Advisor** - Draft things for my review, but never send or post
- [ ] **Assistant** - Act on low-risk items (log notes, organize files), ask for high-risk
- [ ] **Partner** - Act autonomously on most things, ask only for irreversible actions

---

## 5. Security Boundaries

What should your agent NEVER do without explicit permission?

- [X] Send emails or messages on my behalf
- [X] Post to social media
- [X] Modify files outside the memory vault
- [X] Access financial data or make purchases
- [ ] Delete anything
- [X] Other: Never modify production QuickBooks records (read-only access to QB)
- [X] Other: Never create or delete GitHub repos without approval
- [X] Other: Never send data from one client's QuickBooks to another client (strict client isolation)

---

## 6. Memory Categories

What types of knowledge matter most to you? Check all that apply and add your own:

- [X] Meeting notes and decisions
- [X] Project status and progress
- [X] Client/customer information
- [ ] Research and learning notes
- [ ] Personal goals and habits
- [ ] Content ideas and drafts
- [X] Team context (who does what, preferences, timezones)
- [X] Other: Client onboarding status (which clients are active, what stage of onboarding, pending credentials)
- [X] Other: QuickBooks realm IDs and API connection status per client
- [X] Other: Month-end close calendar and deadlines per client
- [X] Other: Vendor contact lists and payment terms per client

---

## 7. Infrastructure

- **Operating System:** [X] Windows [ ] macOS [ ] Linux
- **Deployment:** [ ] Local only [X] Local + cloud server (VPS)
- **Existing tools I already have set up:**
  - Claude Co-Work (Emil's primary interface — comfortable with it, not yet comfortable with Claude Code CLI)
  - QuickBooks connected to Claude Co-Work (single company at a time)
  - GitHub @Fisch-Group org with 2 repos (clientflow-dashboard, elevate-trust-showcase)
  - Lovable.dev projects synced to GitHub
  - Airtable (active, Emil has personal access token)
  - 1Password for credential management
  - GBAutomation consulting support (Greg Black) for technical buildout

---

## 8. Integration Priority

Rank your top 3 integrations to build first (from your answers in Section 2):

1. QuickBooks Online (multi-company — this is the core of every workflow)
2. GitHub (repo creation, template cloning for client onboarding)
3. Outlook / Gmail (email drafting for AR follow-ups and client communications)

---

> After filling this out, run: `/create-second-brain-prd <path to this file>`
