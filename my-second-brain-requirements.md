# My Second Brain - Requirements Template

> Fill this out during the workshop (Section 1.4). Your answers feed directly into the `/create-second-brain-prd <path to this file>` command, which generates your personalized build plan.

---

## 1. About You

- **Name:** Greg Black
- **Role/Title:** Founder & AI Consultant at GBAutomation
- **What I do daily** (1-2 sentences): I run an AI consulting business — onboarding clients, building custom AI agent systems (OpenClaw, Claude Code skills), managing client sessions, and doing prospect outreach on LinkedIn. I split time between client delivery, business development, and building internal tooling.
- **Timezone:** Pacific (US) — Los Angeles

---

## 2. Your Platforms

Check every platform you actively use and fill in the specific tool:

- [X] Email (e.g., Gmail, Outlook): Gmail (greg@gbautomation.xyz)
- [X] Calendar (e.g., Google Calendar, Outlook Calendar): Google Calendar
- [X] Task Management (e.g., Asana, Linear, Todoist, Jira): Linear
- [X] Chat/Messaging (e.g., Slack, Discord, Teams): Telegram (notifications), Discord (community)
- [X] Notes/Documents (e.g., Notion, Obsidian, Google Docs): Obsidian (vault: C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation)
- [X] Cloud Storage (e.g., Google Drive, Dropbox, OneDrive): Google Drive (GBAutomation Clients folder structure)
- [X] Code Hosting (e.g., GitHub, GitLab): GitHub
- [X] Community (e.g., Circle, Discord server, Mighty Networks): Discord (per-client servers — each consulting client gets their own Discord server for async communication and agent interaction)
- [ ] CRM (e.g., HubSpot, Salesforce, Pipedrive): ___
- [X] Other: LinkedIn (prospect outreach, content), Stripe (billing), AWS (infrastructure — Lightsail, Secrets Manager, KMS), Supabase (database/vault)

---

## 3. Top Tasks for AI

List 3-5 tasks you'd want your second brain to handle proactively:

**My list:**

1. Monitor Gmail for new prospect inquiries and client messages — draft replies in my voice and notify via Telegram
2. Track client session deadlines and deliverables — remind me before they're due
3. Scan LinkedIn for engagement opportunities and prospect signals
4. Keep client session notes, deliverables, and project status organized and searchable across Obsidian + Google Drive
5. Daily digest: summarize what happened across all channels (email, Linear, GitHub, client Discord servers) and surface what needs my attention today
6. Monitor client Discord servers for questions, blockers, or updates — draft responses and flag urgent items via Telegram

---

## 4. Proactivity Level

How bold should your agent be? Pick one:

- [ ] **Observer** - Notify only, never take action
- [ ] **Advisor** - Draft things for my review, but never send or post
- [X] **Assistant** - Act on low-risk items (log notes, organize files), ask for high-risk
- [ ] **Partner** - Act autonomously on most things, ask only for irreversible actions

---

## 5. Security Boundaries

What should your agent NEVER do without explicit permission?

- [X] Send emails or messages on my behalf
- [X] Post to social media
- [ ] Modify files outside the memory vault
- [X] Access financial data or make purchases
- [X] Delete anything
- [X] Other: Never send Telegram messages to clients (only to me), never push to main branch, never modify client billing in Stripe

---

## 6. Memory Categories

What types of knowledge matter most to you? Check all that apply and add your own:

- [X] Meeting notes and decisions
- [X] Project status and progress
- [X] Client/customer information
- [X] Research and learning notes
- [X] Personal goals and habits
- [X] Content ideas and drafts
- [ ] Team context (who does what, preferences, timezones)
- [X] Other: Client session history (intake answers, deliverables, follow-ups), prospect pipeline status, consulting pricing/packages

---

## 7. Infrastructure

- **Operating System:** [ ] Windows [X] macOS [ ] Linux
- **Deployment:** [ ] Local only [X] Local + cloud server (VPS)
- **Existing tools I already have set up:** Obsidian vault with AI-Agent-KB structure, Mac Mini (192.168.4.94) running OpenClaw v2026.3.13 as the always-on agent host, AWS Lightsail instances (OpenClaw gateway on 18.234.126.236), Google Workspace OAuth god token in AWS Secrets Manager, Claude Code with hooks system, Supabase for database/vault, launchd/cron for recurring scripts on Mac Mini, customer-gateway-proxy on port 3050, consulting-admin email_watcher already built

  (e.g., "I already use Obsidian", "I have a DigitalOcean droplet", "I'm comfortable with the terminal")

---

## 8. Integration Priority

Rank your top 3 integrations to build first (from your answers in Section 2):

1. Gmail (already have OAuth + email_watcher — extend with drafting + smart classification)
2. Google Calendar (booking links already active — add session prep and follow-up automation)
3. LinkedIn (prospect outreach and engagement tracking)

---

> After filling this out, run: `/create-second-brain-prd <path to this file>`
