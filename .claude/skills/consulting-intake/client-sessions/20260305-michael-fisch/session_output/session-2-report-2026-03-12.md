# Fish Group - Session 2 Report
**Date**: March 12, 2026 | **Duration**: 1 hour 26 minutes
**Attendees**: Greg Black (GBAutomation), Michael Fisch (Fish Group), Emil Caplow (Fish Group)
**Meeting**: Google Meet — "45 min - AI Session"

---

## Session Summary

This was the second working session with Fish Group. The focus shifted from architecture planning (Session 1) to hands-on setup: connecting Lovable projects to GitHub, exploring Supabase access, and attempting to set up QuickBooks connectivity via Claude Code. Michael joined from an Uber after visiting Piermont Brands' office.

### Key Achievements
1. **Fish Group GitHub Organization created** — Emil set up `Fisch-Group` org on GitHub
2. **Greg added as admin** to the GitHub org (invite from @mikefisch211)
3. **Lovable → GitHub sync established** for the Piermont Brands portal project
4. **Supabase connection explored** — found project ID (OVAT) but credentials are with Michael
5. **QuickBooks MCP investigated** — found open-source QuickBooks Online MCP server but it requires Docker/Node setup (too complex for this session)
6. **Billing agreed** — $50/hr, 4 hours billed so far, Stripe invoice sent ($200)
7. **Emil's background confirmed** — he's the primary builder, familiar with Lovable, has QuickBooks developer program access

---

## Piermont Brands Portal — Current State

The portal Emil and Michael built in Lovable is **already in production**:
- **12 API integrations**: Sin7, QuickBooks, Plaid, resend inventory, and more
- **8-9 employees at Piermont actively using it**
- Built on Lovable's integrated Supabase backend
- Multiple tabs: AR/AP, inventory, client dashboard modules

### Architecture Insight
Michael described the vision: "run continuous and recursive agents on top of the data" — not just dashboards, but agents that can:
- Follow up on aging receivables weekly (email vendors with statements)
- Respond to vendor complaints by pulling context from multiple APIs
- Potentially auto-correct data issues flagged by clients

---

## Technical Findings

### Lovable → GitHub → Claude Code Workflow
- Lovable syncs projects to GitHub via built-in integration
- Once synced, Claude Code can connect to the GitHub repo and modify code
- Changes push back through GitHub sync to Lovable
- **Status**: Sync established for Piermont Brands project to Fisch-Group GitHub org

### Supabase Access
- Lovable uses its own built-in Supabase (not a separate Supabase Cloud account)
- Emil found two Supabase projects in Michael's account but neither matched the OVAT project ID
- **Blocker**: Michael needs to share Supabase credentials (username + password)
- The Supabase data includes all 12 API integrations' data

### QuickBooks Integration
- Emil has QuickBooks developer program access with client ID/secret
- Has both sandbox and production environments
- Attempted to set up via Claude Code web — connection was slow/unresponsive
- Found open-source QuickBooks Online MCP server on GitHub but requires Docker setup
- **Recommendation**: Build a Claude Code skill instead of using MCP (simpler, no Docker)

### Claude Code Setup
- Emil has Claude desktop app installed (basic $25/mo plan)
- Michael has Claude Code on desktop connected to VS Code
- Web version (claude.ai/code) was sluggish during the session
- Google Meet chat didn't work cross-organization (Greg's messages didn't show for Emil)

---

## Client Ecosystem Map

```
Fish Group (Michael + Emil)
    |
    +-- Piermont Brands (primary test client)
    |     +-- Sin7 (inventory)
    |     +-- QuickBooks (accounting)
    |     +-- Plaid (banking)
    |     +-- Resend (inventory/notifications)
    |     +-- 8+ more integrations
    |     +-- 8-9 employees using portal
    |
    +-- Gary's (retail, Philippines CS team)
    +-- Drop Fitness
    +-- ~12 other clients
    |
    Tools:
    +-- Lovable (frontend builder)
    +-- Supabase (backend/database via Lovable)
    +-- GitHub (Fisch-Group org — NEW)
    +-- QuickBooks Developer Program
    +-- 1Password (credential management)
    +-- Microsoft Outlook (email — not Google)
    +-- 3 clients on Google Workspace
```

---

## Key Quotes

> **Michael**: "We've got eight, nine different employees already using our portal. It's just getting everything out of email and out of their heads into one place."

> **Michael**: "I want to run continuous and recursive agents on top of the data here to be able to execute goals of ours."

> **Michael**: "I think for now, just charge me hourly if you'd like. Whatever your rate is and then we'll figure out a product that we can buy from you."

> **Emil**: "I was reading an article about cloning your Lovable project with Supabase, opening it in Claude Code, doing fixes there, then sending it back to Lovable."

> **Michael on offering Greg a Fish Group email**: "I've had so many clients who will want your services... it would make sense for you to have an email."

---

## Discussion Items Requiring Research

### 1. Lovable → Claude Code Bidirectional Workflow
**Question**: What's the most effective way to edit Lovable projects through Claude Code?
**Answer**: Lovable has built-in **two-way GitHub sync**. Edits in Lovable auto-push to GitHub; commits pushed to GitHub auto-pull into Lovable. The workflow:
1. Create/iterate UI in Lovable (rapid chat-based prototyping)
2. Connect to GitHub via Lovable's built-in integration
3. Clone the repo locally, use Claude Code for backend logic and complex refactors
4. Push to GitHub — Lovable syncs automatically
5. Use Lovable for quick visual tweaks — GitHub syncs back

**Key caveat**: Merge conflicts can occur if you edit the same files in both tools simultaneously. Best practice: Lovable for UI, Claude Code for backend/logic.

**Sources**: [Lovable GitHub Integration Docs](https://docs.lovable.dev/integrations/github), [Lovable Git Integration](https://docs.lovable.dev/integrations/git-integration)

### 2. Lovable's Supabase — Critical Finding
**There are TWO modes:**

| Feature | Lovable Cloud (default) | Your Own Supabase Project |
|---------|------------------------|--------------------------|
| Who manages it | Lovable | You |
| Visible in Supabase Dashboard | No | Yes |
| Access to service_role key | No | Yes |
| External tool access (Claude Code) | **Not possible** | Yes |

**Lovable Cloud** provisions a hidden Supabase instance you **cannot access directly**. No dashboard, no service role key, no connection string. This explains why Emil couldn't find the OVAT project in Supabase — it's locked inside Lovable's cloud.

**Recommendation**: Migrate to **your own Supabase project** (free tier available). Create at supabase.com, paste Project URL + anon key into Lovable settings. This gives full access from Claude Code agents. Lovable documents the migration path.

**Sources**: [Lovable Supabase Docs](https://docs.lovable.dev/integrations/supabase), [Supabase: Identifying Lovable Cloud vs Supabase Backend](https://supabase.com/docs/guides/troubleshooting/identify-lovable-cloud-or-supabase-backend)

### 3. QuickBooks Integration — Two Options

**Option A: Official Intuit MCP Server** (recommended)
- Repo: [intuit/quickbooks-online-mcp-server](https://github.com/intuit/quickbooks-online-mcp-server)
- Requirements: Node.js 18+, npm (**no Docker needed** — during the call we thought Docker was required, but it's not)
- Setup: `git clone` + `npm install` + `npm run build`
- Auth: OAuth 2.0 via Intuit Developer portal
- Limitation: Currently sandbox-only (early preview)

**Option B: Python SDK** (for custom skills)
- Package: `python-quickbooks` + `intuit-oauth`
- `pip install python-quickbooks intuit-oauth`
- Supports all entities: Invoice, Customer, Vendor, Bill, Payment, Account
- Key APIs: Invoicing, AR/AP aging, Payments, Reports (P&L, Balance Sheet, Cash Flow)
- OAuth tokens expire hourly; refresh tokens last 100 days

**Note on pricing**: Core API calls (creates/updates) are free. CorePlus calls (reads/queries/reports) are now metered with tiered pricing.

**Sources**: [Intuit QBO MCP Server](https://github.com/intuit/quickbooks-online-mcp-server), [python-quickbooks on PyPI](https://pypi.org/project/python-quickbooks/)

### 4. Cin7 (Not "Sin7") — Inventory Management
The transcript references "Sin7" — this is **Cin7** (formerly "Dear Inventory"), a cloud-based inventory and order management platform.

- **API**: REST API with JSON, auth via API key + username (simpler than OAuth)
- **Endpoints**: Products, Stock, Pricing, Sales Orders, Purchase Orders, Payments, Contacts, Warehouses
- **QuickBooks integration**: Native built-in (no custom code needed) — syncs sales, purchases, credit notes, COGS, customer data
- **No official Python SDK** — use `requests` library with API key auth headers
- **Docs**: [api.cin7.com](https://api.cin7.com/) (Omni), [dearinventory.docs.apiary.io](https://dearinventory.docs.apiary.io/) (Core V2)

### 5. Client Onboarding Automation
**Question**: Can an agent spin up new client workspaces automatically?
**Answer**: Yes — build an "onboarding skill" that:
1. Creates a new Lovable project from template (via GitHub fork/clone)
2. Provisions Supabase tables for the new client
3. Configures API connections (QuickBooks, Cin7, etc.)
4. Sends welcome email to client contacts

### 6. Multi-Client Architecture
**Question**: Should each client have their own portal or one portal with a switcher?
**Recommendation**: Separate portals per client (current approach) is better for data isolation, security, client-specific customization, and simpler permissions. Use the "remix" workflow Emil is already doing — clone the template, connect client-specific APIs.

### 7. Dashboard vs. Chat Interface
**Discussion**: Emil questioned whether clients want to chat with data vs. use dashboards.
**Recommendation**: Both. Dashboards for routine views, chat for ad-hoc complex questions. The portal already has dashboards — adding a chat interface would complement (not replace) them.

### 8. Recommended Architecture
```
Supabase (YOUR OWN instance — shared data layer)
    |
    +-- Lovable front-end (UI, dashboards)
    +-- Claude Code agents (skills, automation)
    +-- QuickBooks MCP server (financial data)
    +-- Cin7 API (inventory data — API key auth)
    +-- GitHub (sync layer between Lovable and Claude Code)
```

---

## Next Steps

### For Greg (GBAutomation)
| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1 | **Get access to Fisch-Group GitHub org** | High | DONE - invited as admin |
| 2 | **Accept GitHub org invite** from @mikefisch211 | High | Pending |
| 3 | **Build sample skills** for Fish Group's APIs (QuickBooks, Sin7, Plaid) | High | Not started |
| 4 | **Generate AI sample skills** based on their existing API integrations | High | Not started |
| 5 | **Gather more context** on client workflows, specifics about Piermont/Gary's/Drop Fitness | Medium | Ongoing |
| 6 | **Build nuanced business logic** — AR follow-up rules, onboarding sequences, client-specific workflows | Medium | Not started |
| 7 | **Research Lovable → Claude Code workflow** thoroughly | Medium | In progress |
| 8 | **Prepare Emil for Claude Code** — create a getting-started guide tailored to his setup | Medium | Not started |
| 9 | **Send Stripe invoice** | High | DONE - $200 sent to mike@piermontbrands.com |
| 10 | **Consider Fish Group email** — Michael offered greg@fishgroup email for client work | Low | Pending discussion |

### For Michael (Fish Group)
| # | Action | Priority |
|---|--------|----------|
| 1 | **Share Supabase credentials** — username + password for the OVAT project | High |
| 2 | **Organize API keys in 1Password** — QuickBooks, Sin7, Plaid, etc. | High |
| 3 | **Share specific keys with Greg** via 1Password shared vault | High |
| 4 | **Accept Greg into GitHub org** as admin | High |
| 5 | **Identify top 3 AR follow-up use cases** for Piermont Brands | Medium |
| 6 | **Consider upgrading Claude plan** if token usage increases ($25 → $100/mo) | Low |

### For Emil (Fish Group)
| # | Action | Priority |
|---|--------|----------|
| 1 | **Enable 2FA on GitHub** for the Fisch-Group org | High |
| 2 | **Get Supabase access** from Michael for the Lovable projects | High |
| 3 | **Share QuickBooks sandbox credentials** (client ID + secret) with Greg | High |
| 4 | **Try Claude Code desktop** for a simple task (web version was slow) | Medium |
| 5 | **Send Greg the Lovable → Claude Code article** mentioned during the call | Medium |
| 6 | **Map all API integrations** — create a visual of which systems talk to which | Medium |
| 7 | **Share email address** with Greg for CC on correspondence | Medium |

---

## Billing Summary

| Item | Amount |
|------|--------|
| Session 1 (March 5) | Included in initial engagement |
| Session 2 prep + session (4 hours @ $50/hr) | $200.00 |
| **Invoice ENIDX5M1-0002** | **$200.00** |
| Status | Sent to mike@piermontbrands.com |
| Payment terms | Net 30 |

---

## Next Session
**When**: Same time next week (March 19, 2026)
**Focus**:
1. Connect to Supabase backend (if credentials provided)
2. Build first QuickBooks skill (AR aging report + email follow-up)
3. Walk through skill creation process with Emil
4. Demo agent running a workflow end-to-end

---

*Report generated by GBAutomation AI Agent from Google Meet transcript + session context*
*Transcript source: Google Drive — "45 min - AI Session - 2026/03/12 13:44 PDT"*
