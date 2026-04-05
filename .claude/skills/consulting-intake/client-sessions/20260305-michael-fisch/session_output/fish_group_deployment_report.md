# Fish Group — AI Architecture & Deployment Options

**Prepared by:** GBAutomation Consulting  
**Date:** March 2026  
**For:** Michael Fisch  
**Confidential:** Fish Group only

---

## The Tool Spectrum: From Workflow to Autonomous

Before choosing a deployment model, it helps to understand where each tool sits on the agency spectrum.

| Tool | Who defines the steps? | Runs 24/7? | Best for | ~Monthly cost |
|------|------------------------|------------|----------|---------------|
| **n8n** | You do — visually | Yes (on server) | Deterministic, repeatable triggers | $80–150 |
| **Claude Code** | You set the goal; AI plans steps | No (requires human) | One-time builds, code generation, dev work | $20–200 |
| **OpenClaw** | Agent decides autonomously | Yes (cloud) | Autonomous workflows, repeatable ops | $100–200 |

**The winning strategy: use all three.** Claude Code builds and maintains the skills. OpenClaw runs them autonomously. n8n handles webhook triggers if needed. This is exactly what we're proposing for Fish Group.

---

## Deployment Options

### Option 1 — Local Dev (Claude Code on Laptop)
> **Rating:** Good Start

Michael or Emil runs Claude Code locally from their MacBook / PC.

The simplest entry point. You install Claude Code on your machine, give it access to your APIs (Airtable, Google, etc.) and work with it like a very smart pair programmer. You describe what you want, it builds it, you review.

**Pros**
- Zero server cost
- Instant setup (you already have it)
- Full control — you're in the loop on every step
- Best for exploration and building
- Works with any codebase locally

**Cons**
- Not always-on — laptop must be open
- No autonomous execution (you trigger everything)
- API keys stored locally (security risk if laptop lost)
- Doesn't scale to client-facing automation

**Cost:** $20/mo (Claude Max) + $0 server · Best for: building skills & one-time tasks

---

### Option 2 — Claude Professional with Seats
> **Rating:** Limited

Multiple Claude.ai Pro accounts for Michael, Emil, and team.

Good for writing, summarizing, and conversational AI — but **not suitable for automated workflows or agents**. No API access, no MCP servers, no persistent agents.

**Pros**
- Easy to provision seats for the whole team
- No technical setup required
- Good for writing, analysis, Q&A
- Clients can get seats too

**Cons**
- No API access — can't connect to Airtable, Google, etc.
- No persistent agents or cron jobs
- Not suitable for automation
- $20–25/seat/month adds up quickly

**Cost:** $20–25/seat/mo · Best for: team writing & analysis — not automation

---

### Option 3 — EC2 + OpenClaw (Always-On Autonomous Agent)
> **Rating:** Recommended

Fish Group internal agent running 24/7 on AWS EC2.

OpenClaw is installed on an EC2 instance (t3.small or t3.medium). It runs continuously, listening for webhook triggers, executing cron jobs, and processing tasks without anyone needing to be at a laptop. This is the "Finn 🐟" agent system we scoped in the session.

```
Fish Group AWS Architecture (Option 3)
─────────────────────────────────────────────────────
  [ Michael / Emil ]
       │  Claude Code CLI (local)
       │  (builds + edits skills in ~/.openclaw/)
       ▼
  [ EC2 Instance — t3.small — $17/mo ]
  ┌─────────────────────────────────────┐
  │  OpenClaw Gateway (:18789)          │
  │  ├── Finn 🐟 (main agent)           │
  │  ├── Client Ops agent               │
  │  ├── Data/Airtable agent            │
  │  └── Permissions agent              │
  │                                     │
  │  Secrets Manager (AWS KMS)          │
  │  OpenRouter → Gemini / Claude       │
  └─────────────────────────────────────┘
       │  API calls via secrets
       ▼
  [ External Tools ]
  ┌─────────────────────────────────────┐
  │  Google Workspace (Gmail, Drive)    │
  │  Airtable (all client bases)        │
  │  AWS IAM (per-client accounts)      │
  │  QuickBooks (Piermont)              │
  │  ShipStation (Piermont)             │
  └─────────────────────────────────────┘
─────────────────────────────────────────────────────
```

**Pros**
- Always-on — runs cron jobs, listens for webhooks
- Secrets stored securely in AWS KMS
- Scales to multiple clients (one instance each)
- Claude Code on laptop connects to EC2 for edits
- OpenRouter models — cheaper than Anthropic direct
- One AWS account per client = isolated billing

**Cons**
- Requires initial server setup (~2hr)
- Small ongoing cost per EC2 instance
- Need SSH access to debug/update

**Cost:** $17–35/mo EC2 · $20–50/mo OpenRouter tokens · ~$5/mo KMS · **Total: ~$50–90/mo per instance**

---

### Option 4 — Hybrid: Local Claude Code + EC2 OpenClaw
> **Rating:** Recommended

The full Fish Group architecture — building locally, running autonomously in cloud.

Michael and Emil use Claude Code on their laptops to **build and edit skills**. Those skills live in a Git repo. EC2 runs OpenClaw, which pulls the latest skills and executes them autonomously.

```
Hybrid Architecture — Full Fish Group Setup
─────────────────────────────────────────────────────
  [ Michael + Emil — Local Dev ]
  ┌────────────────────────────────┐
  │  Claude Code CLI               │
  │  (builds skills, edits agents) │
  │  git push → GitHub repo        │
  └────────────────────────────────┘
            │ git pull (auto deploy)
            ▼
  [ EC2 — Fish Group Internal ]           [ EC2 — Per Client ]
  ┌───────────────────────────┐           ┌──────────────────────┐
  │  OpenClaw + Finn 🐟       │           │  OpenClaw (client)   │
  │  runs all Fish Group ops  │           │  Piermont / Gary's   │
  │  client onboarding        │           │  etc.                │
  │  permissions, briefs      │           └──────────────────────┘
  └───────────────────────────┘

  Claude Code on laptop can SSH into EC2 and make live edits,
  or work offline and push to deploy. Both modes work.
─────────────────────────────────────────────────────
```

**Pros**
- Local dev = fast iteration, no server round trips
- EC2 = always-on execution, no laptop dependency
- Git as source of truth for all skills
- Easy rollback if something breaks
- Emil can dev locally while Michael's agent runs on EC2
- Client EC2 accounts are isolated — their bill, their data

**Cons**
- Slightly more setup than a single option
- Requires Git workflow discipline

**Cost:** $20/mo Claude Code (local) · $50–90/mo EC2 Fish Group · $25–50/mo per client instance

---

## Our Recommendation for Fish Group

Start with Option 1 to get hands dirty. Move to Option 4 within 2–4 weeks.

### Phase 1 — Now (this week)
1. Michael + Emil: use Claude Code locally — build the first 2 skills (client onboarding, Airtable lookup)
2. Set up one AWS account for Fish Group internal with our per-client account strategy
3. Generate Airtable personal access token + Google Workspace OAuth

### Phase 2 — Follow-up Session (~2 weeks out)
1. Deploy OpenClaw on EC2 for Fish Group internal (Finn 🐟 goes live)
2. Connect Google Workspace, Airtable, AWS IAM via secrets
3. Wire up first autonomous workflow: new client onboarding
4. Set up morning ops brief cron job

### Phase 3 — Piermont + Gary's (4–8 weeks out)
1. Piermont gets their own EC2 instance with QuickBooks + ShipStation + Airtable agent
2. Build chat UI portal for Piermont (using Lovable + customer-gateway-proxy pattern)
3. Scope Gary's CS agent — email triage first, voice AI second

---

*Questions? Reply to this email or Slack Greg directly. Next session will go hands-on with EC2 setup + first skill deployment.*
