# Workflow Catalog — Fish Group
**Generated**: 2026-03-12 | **Client**: Michael Fisch + Emil Caplow
**Domain**: Accounting & Finance Consulting (15 clients, 8-10 overseas bookkeepers)
**Primary Test Client**: Piermont Brands (Chica Cheetah + Caya brands)

---

## Executive Summary

**27 workflows** identified across 6 categories. Fish Group's unique position — an accounting firm with a Lovable-built client portal, 12 API integrations, and appetite for agentic automation — creates high-leverage opportunities across AR/AP, client operations, and multi-client management.

**Top 5 Quick Wins** (buildable in 1-2 hours each):
1. AR Aging Follow-Up Emails
2. Daily Cash Position Summary
3. New Client Workspace Generator
4. Data Discrepancy Checker (QuickBooks vs. Lovable)
5. Weekly Client Digest

---

## Quick Wins (High Impact, Low Complexity)

### WF-001: AR Aging Follow-Up Emails
**Category**: Custom (Michael explicitly requested this)
**What**: Every week, pull aging receivables from QuickBooks for each vendor, aggregate into a statement, and draft a follow-up email. Human reviews batch, then sends.
**APIs**: QuickBooks (AR Aging report), Gmail/Outlook
**Trigger**: Weekly schedule (Monday 9am ET)
**Human-in-the-Loop**:
- Review generated emails before sending (batch review pattern)
- Flag any vendor with disputes for manual handling
**Validation Gates**:
- AR totals match QuickBooks aging report
- No duplicate emails sent (check last sent date per vendor)
- Email contains correct vendor name, amounts, and contact
**Complexity**: Low | **Impact**: High | **Priority**: 9/10
**Prerequisites**: QuickBooks API key (Emil has sandbox), vendor contact list
**Build Time**: 2-3 hours

---

### WF-002: Daily Cash Position Summary
**Category**: Domain (standard for accounting firms)
**What**: Every morning, pull balances from Plaid (bank accounts) and QuickBooks (outstanding AR/AP), generate a one-page cash position summary, email to Michael.
**APIs**: Plaid (balances), QuickBooks (AR/AP totals)
**Trigger**: Daily schedule (7am ET)
**Human-in-the-Loop**: None needed — read-only report
**Validation Gates**:
- Bank balances match Plaid API response
- AR/AP totals reconcile with QuickBooks
- Report delivered successfully (email confirmation)
**Complexity**: Low | **Impact**: High | **Priority**: 9/10
**Prerequisites**: Plaid API key, QuickBooks API key
**Build Time**: 1-2 hours

---

### WF-003: New Client Workspace Generator
**Category**: Custom (Michael and Emil discussed this extensively)
**What**: When onboarding a new client, fork the Lovable portal template, create a new GitHub repo in Fisch-Group org, provision Supabase tables, configure API connections, and send welcome email.
**APIs**: GitHub (repo creation), Supabase (table provisioning), Gmail/Outlook (welcome email)
**Trigger**: Manual — `/onboard-client "Company Name" "contact@email.com"`
**Human-in-the-Loop**:
- Approve workspace details before provisioning
- Review welcome email before sending
- Manually enter API keys for the new client's QuickBooks/Cin7
**Validation Gates**:
- GitHub repo created and accessible
- Supabase tables created with correct schema
- Welcome email drafted (not sent until approved)
- All required API fields populated
**Complexity**: Low-Medium | **Impact**: High | **Priority**: 8/10
**Prerequisites**: Supabase migration from Lovable Cloud (BLOCKER), GitHub org admin access
**Build Time**: 3-4 hours

---

### WF-004: Data Discrepancy Checker
**Category**: Custom (Emil mentioned QuickBooks data doesn't always match Lovable display)
**What**: Compare QuickBooks source data against what's displayed in the Lovable portal (via Supabase). Flag any discrepancies in amounts, dates, or categorization.
**APIs**: QuickBooks (source data), Supabase (portal data)
**Trigger**: Daily schedule (after nightly data sync)
**Human-in-the-Loop**:
- Review flagged discrepancies
- Decide: fix in QuickBooks, fix in portal, or ignore (rounding)
**Validation Gates**:
- All QuickBooks accounts compared against Supabase records
- Discrepancy report includes: field, QB value, portal value, delta
- No false positives from known timing differences
**Complexity**: Low | **Impact**: High | **Priority**: 8/10
**Prerequisites**: Supabase migration, QuickBooks API key
**Build Time**: 2 hours

---

### WF-005: Weekly Client Digest
**Category**: Domain (standard for accounting firms)
**What**: For each active client, generate a weekly summary: new invoices, payments received, outstanding AR, inventory alerts (Cin7), and any flagged items. Email to Michael and Emil.
**APIs**: QuickBooks (financials), Cin7 (inventory), Supabase (portal data)
**Trigger**: Weekly schedule (Friday 4pm ET)
**Human-in-the-Loop**: None — informational report
**Validation Gates**:
- All 15 clients included (or explicitly marked as skipped with reason)
- Financial totals reconcile
- Report delivered to correct recipients
**Complexity**: Low | **Impact**: Medium | **Priority**: 7/10
**Prerequisites**: QuickBooks API, Cin7 API key
**Build Time**: 2-3 hours

---

## Medium Effort (High Impact, Medium Complexity)

### WF-006: Vendor Payment Scheduler
**Category**: Domain
**What**: Review upcoming AP payments, prioritize by due date and cash position, draft payment schedule for approval. Execute approved payments.
**APIs**: QuickBooks (AP, bill payments), Plaid (cash balances)
**Trigger**: Weekly schedule (Tuesday)
**Human-in-the-Loop**:
- **Approve payment schedule** before any payments execute (mandatory)
- Flag any payment > $5,000 for additional review
**Validation Gates**:
- Total payments don't exceed available cash
- No duplicate payments (check payment history)
- All payments have valid vendor bank details
**Complexity**: Medium | **Impact**: High | **Priority**: 8/10
**Prerequisites**: QuickBooks payment API access, bank account authorization
**Build Time**: 4-5 hours

---

### WF-007: Multi-Client Dashboard Sync
**Category**: Custom
**What**: Nightly sync of all client data from QuickBooks + Cin7 + Plaid into each client's Supabase instance. Update portal dashboards automatically.
**APIs**: QuickBooks, Cin7, Plaid, Supabase (write)
**Trigger**: Daily schedule (2am ET — off-hours)
**Human-in-the-Loop**:
- Alert if sync fails for any client
- Alert if data volume is abnormally high/low (possible API issue)
**Validation Gates**:
- Record counts match source system
- Financial totals reconcile pre/post sync
- Sync completion logged with timestamp and record counts
- Rollback available if sync corrupts data
**Complexity**: Medium | **Impact**: High | **Priority**: 7/10
**Prerequisites**: Supabase migration, all API keys per client
**Build Time**: 5-6 hours

---

### WF-008: Invoice Generator
**Category**: Domain
**What**: Generate and send invoices to Fish Group's clients based on time tracking, fixed fees, or milestone completion. Track payment status.
**APIs**: QuickBooks (invoice creation), Gmail/Outlook (delivery), Stripe (payment link)
**Trigger**: Monthly schedule or manual trigger
**Human-in-the-Loop**:
- Review invoice details before sending
- Approve any custom line items or discounts
**Validation Gates**:
- Invoice amounts match engagement terms
- Client billing details are current
- No duplicate invoices for same period
**Complexity**: Medium | **Impact**: High | **Priority**: 7/10
**Prerequisites**: QuickBooks API, client billing terms
**Build Time**: 3-4 hours

---

### WF-009: Client Health Scorer
**Category**: Domain
**What**: Weekly scoring of each client based on: payment timeliness, portal usage, open support tickets, data quality, and engagement level. Flag at-risk clients.
**APIs**: QuickBooks (payment history), Supabase (portal usage), Airtable (tickets)
**Trigger**: Weekly schedule
**Human-in-the-Loop**:
- Review flagged at-risk clients
- Decide on intervention (call, email, meeting)
**Validation Gates**:
- All 15 clients scored
- Score components weighted correctly
- Historical trend included (improving/declining)
**Complexity**: Medium | **Impact**: Medium | **Priority**: 6/10
**Prerequisites**: Define scoring criteria with Michael
**Build Time**: 3-4 hours

---

### WF-010: Bank Reconciliation Alert
**Category**: Domain
**What**: Compare bank transactions (Plaid) against QuickBooks entries. Flag unmatched transactions, missing deposits, or suspicious activity.
**APIs**: Plaid (transactions), QuickBooks (journal entries)
**Trigger**: Daily schedule
**Human-in-the-Loop**:
- Review unmatched transactions
- Categorize and record in QuickBooks
**Validation Gates**:
- All bank transactions from last 24 hours checked
- Match tolerance defined (±$0.01 for exact, ±$1 for rounding)
- Alert only on genuine mismatches (not timing differences)
**Complexity**: Medium | **Impact**: High | **Priority**: 7/10
**Prerequisites**: Plaid API, QuickBooks API
**Build Time**: 4 hours

---

### WF-011: Expense Report Processor
**Category**: Domain
**What**: Process expense reports from overseas bookkeepers. Categorize expenses, check against budget, flag policy violations, and post to QuickBooks.
**APIs**: Gmail/Outlook (receive reports), QuickBooks (expense posting), Claude (categorization)
**Trigger**: Event — new expense report email received
**Human-in-the-Loop**:
- Approve expenses over threshold ($500)
- Review flagged policy violations
**Validation Gates**:
- All expenses categorized to valid GL accounts
- Receipts attached for expenses > $25
- Budget check: alert if category exceeds monthly budget
**Complexity**: Medium | **Impact**: Medium | **Priority**: 6/10
**Prerequisites**: Expense policy document, GL account mapping
**Build Time**: 4-5 hours

---

### WF-012: Piermont Inventory Reorder Alert
**Category**: Custom (Piermont specific)
**What**: Monitor Cin7 inventory levels for Piermont's Chica Cheetah and Caya brands. Alert when stock drops below reorder point. Draft PO for approval.
**APIs**: Cin7 (inventory levels), QuickBooks (PO creation), Gmail (alert)
**Trigger**: Daily schedule
**Human-in-the-Loop**:
- Review and approve purchase orders before submission
- Adjust reorder quantities based on seasonal demand
**Validation Gates**:
- Reorder points defined per SKU
- PO quantities within min/max bounds
- Vendor lead times factored into urgency
**Complexity**: Medium | **Impact**: High | **Priority**: 7/10
**Prerequisites**: Cin7 API key, reorder point definitions per SKU
**Build Time**: 3-4 hours

---

### WF-013: Piermont Shipment Tracker
**Category**: Custom
**What**: Monitor ShipStation for Piermont shipments. Track delivery status, flag delays, and proactively notify customers of shipping updates.
**APIs**: ShipStation (shipment tracking), Gmail (customer notifications), Supabase (portal update)
**Trigger**: Event — shipment status change
**Human-in-the-Loop**:
- Review delay notifications before sending to customers
**Validation Gates**:
- Tracking numbers valid
- Customer email addresses current
- No duplicate notifications for same shipment
**Complexity**: Medium | **Impact**: Medium | **Priority**: 6/10
**Prerequisites**: ShipStation API key
**Build Time**: 3 hours

---

### WF-014: Tax Document Collector
**Category**: Domain
**What**: During tax season, automatically request W-9s, 1099s, and other tax documents from vendors and contractors. Track which are outstanding.
**APIs**: Gmail/Outlook (outreach), Airtable or Supabase (tracking), Google Drive (storage)
**Trigger**: Annual (January) + manual for new vendors
**Human-in-the-Loop**:
- Review request list before sending
- Follow up on non-responsive vendors
**Validation Gates**:
- All vendors above $600 threshold included
- Documents stored in correct client folder
- Completion percentage tracked and reported
**Complexity**: Medium | **Impact**: Medium | **Priority**: 5/10
**Prerequisites**: Vendor list with contact info, document templates
**Build Time**: 3-4 hours

---

### WF-015: Monthly Close Checklist
**Category**: Domain
**What**: Automated monthly close process: verify all transactions posted, reconcile accounts, generate trial balance, flag adjustments needed, produce close report.
**APIs**: QuickBooks (all financial data), Claude (analysis)
**Trigger**: Monthly schedule (1st business day)
**Human-in-the-Loop**:
- Review and approve adjusting journal entries
- Sign off on final trial balance
**Validation Gates**:
- All bank accounts reconciled
- AR/AP subledgers agree with GL
- Revenue recognition complete
- Intercompany eliminations applied (if applicable)
**Complexity**: Medium | **Impact**: High | **Priority**: 7/10
**Prerequisites**: Chart of accounts mapping, close procedures documentation
**Build Time**: 5-6 hours

---

## Strategic (High Impact, High Complexity)

### WF-016: Full Client Onboarding Agent
**Category**: Custom
**What**: End-to-end client onboarding: create workspace, provision all APIs, import historical data from QuickBooks, set up dashboards, configure alerts, create user accounts, send welcome package, schedule kickoff call.
**APIs**: All (QuickBooks, Cin7, Plaid, Supabase, GitHub, Gmail, Calendar)
**Trigger**: Manual — `/full-onboard "Company" "contact" "industry"`
**Human-in-the-Loop**:
- Approve onboarding plan
- Review imported data for accuracy
- Attend kickoff call
**Validation Gates**:
- All API connections verified (health check)
- Historical data imported and reconciled
- Dashboard rendering correctly
- User accounts active and accessible
- Welcome package delivered
**Complexity**: High | **Impact**: High | **Priority**: 7/10
**Prerequisites**: All individual workflows built first (WF-003, WF-007)
**Build Time**: 8-12 hours

---

### WF-017: AI Financial Review Agent
**Category**: Domain
**What**: Monthly AI-powered financial review: analyze P&L trends, compare against budget, detect anomalies, identify cost savings, and generate executive summary with recommendations.
**APIs**: QuickBooks (financial reports), Claude (analysis), Gmail (delivery)
**Trigger**: Monthly (after close — WF-015)
**Human-in-the-Loop**:
- Review AI recommendations before presenting to client
- Add context that AI may not have (one-time events, strategic decisions)
**Validation Gates**:
- Financial data matches QuickBooks reports
- Anomaly thresholds calibrated (no false alarms)
- Recommendations are actionable and specific
**Complexity**: High | **Impact**: High | **Priority**: 6/10
**Prerequisites**: Monthly close complete (WF-015), historical data for trend analysis
**Build Time**: 6-8 hours

---

### WF-018: Gary's Customer Service Agent
**Category**: Custom (Gary's specific — retail with Philippines CS team)
**What**: AI-powered email triage and response for Gary's customer service. Categorize inquiries, draft responses using order/shipping data, handle returns/refunds with approval workflow.
**APIs**: Gmail (inbound/outbound), ShipStation (order lookup), QuickBooks (refund processing), Claude (response generation)
**Trigger**: Event — new customer email
**Human-in-the-Loop**:
- Review AI-drafted responses before sending
- Approve refunds/returns over $50
- Escalate complaints to management
**Validation Gates**:
- Response tone matches brand guidelines
- Order data accurate (correct order referenced)
- Refund amounts within policy limits
- Response time < 4 hours during business hours
**Complexity**: High | **Impact**: High | **Priority**: 6/10
**Prerequisites**: Gary's email access, ShipStation API, response templates, policy document
**Build Time**: 8-10 hours

---

### WF-019: Multi-Client Financial Consolidation
**Category**: Domain
**What**: Consolidate financial data across all 15 clients into a Fish Group master view. Track total AUM, revenue by client, profitability analysis.
**APIs**: QuickBooks (per-client financials), Supabase (master database), Claude (analysis)
**Trigger**: Monthly schedule
**Human-in-the-Loop**: None — internal Fish Group report
**Validation Gates**:
- All 15 clients included
- Elimination of inter-client transactions
- Totals reconcile with individual client reports
**Complexity**: High | **Impact**: Medium | **Priority**: 5/10
**Prerequisites**: All clients on QuickBooks with API access
**Build Time**: 6-8 hours

---

### WF-020: Intelligent Vendor Communication Hub
**Category**: Custom
**What**: Centralized vendor communication system. When vendors email about invoices, payments, or disputes, AI reads the email, pulls relevant data from QuickBooks, drafts a response, and routes to the right person.
**APIs**: Gmail/Outlook (inbound), QuickBooks (data lookup), Claude (response), Airtable (ticket tracking)
**Trigger**: Event — vendor email received
**Human-in-the-Loop**:
- Review AI response before sending
- Escalate disputes to Michael
**Validation Gates**:
- Correct vendor identified
- Referenced invoices/payments match QuickBooks
- Response factually accurate
- Dispute flag triggers proper escalation
**Complexity**: High | **Impact**: High | **Priority**: 6/10
**Prerequisites**: Vendor email classification rules, QuickBooks API
**Build Time**: 6-8 hours

---

## Nice-to-Have (Medium/Low Impact)

### WF-021: LinkedIn Client Prospecting
**Category**: Domain
**What**: Monitor LinkedIn for potential new clients (companies seeking fractional CFO, bookkeeping, or accounting services). Draft outreach messages.
**APIs**: LinkedIn (search/messaging), Claude (personalization)
**Trigger**: Weekly schedule
**Human-in-the-Loop**: Review and approve all outreach messages
**Validation Gates**: Message personalization quality, no duplicate outreach
**Complexity**: Medium | **Impact**: Medium | **Priority**: 4/10
**Build Time**: 3-4 hours

---

### WF-022: Meeting Prep Agent
**Category**: Domain
**What**: Before each client meeting, pull recent financial data, open items, and portal activity. Generate a 1-page prep brief.
**APIs**: QuickBooks, Supabase, Google Calendar
**Trigger**: Event — 30 minutes before scheduled client meeting
**Human-in-the-Loop**: None — informational
**Validation Gates**: Data freshness (< 24 hours old), correct client matched to meeting
**Complexity**: Low | **Impact**: Medium | **Priority**: 5/10
**Build Time**: 2 hours

---

### WF-023: Contract Renewal Reminder
**Category**: Domain
**What**: Track client engagement terms and send renewal reminders 60/30/7 days before expiration.
**APIs**: Airtable or Supabase (contract data), Gmail (reminders)
**Trigger**: Daily schedule (check expirations)
**Human-in-the-Loop**: Review renewal terms before sending
**Validation Gates**: Contract dates accurate, no premature reminders
**Complexity**: Low | **Impact**: Low | **Priority**: 3/10
**Build Time**: 1-2 hours

---

### WF-024: Overseas Team Task Distributor
**Category**: Custom
**What**: Route bookkeeping tasks to the 8-10 overseas team members based on workload, skill, and timezone. Track completion.
**APIs**: Airtable (task management), Gmail (notifications)
**Trigger**: Event — new task created
**Human-in-the-Loop**: Override assignments if needed
**Validation Gates**: Balanced workload, SLA tracking, quality score per team member
**Complexity**: Medium | **Impact**: Medium | **Priority**: 4/10
**Build Time**: 4-5 hours

---

### WF-025: Portal Usage Analytics
**Category**: Custom
**What**: Track which portal features each client uses most, generate usage reports, identify underutilized features.
**APIs**: Supabase (usage logs), Claude (analysis)
**Trigger**: Monthly schedule
**Human-in-the-Loop**: None — informational
**Validation Gates**: All clients tracked, usage data accurate
**Complexity**: Low | **Impact**: Low | **Priority**: 3/10
**Build Time**: 2 hours

---

### WF-026: Drop Fitness Membership Billing Reconciler
**Category**: Custom (Drop Fitness specific)
**What**: Reconcile membership billing (recurring payments) against bank deposits. Flag failed payments, cancellations, and billing discrepancies.
**APIs**: QuickBooks (billing), Plaid (bank deposits)
**Trigger**: Weekly schedule
**Human-in-the-Loop**: Review flagged discrepancies
**Validation Gates**: All members accounted for, failed payments listed with reasons
**Complexity**: Medium | **Impact**: Medium | **Priority**: 4/10
**Build Time**: 3 hours

---

### WF-027: Automated Compliance Checklist
**Category**: Domain
**What**: Quarterly compliance check: verify all required filings submitted, licenses current, insurance up to date. Generate compliance scorecard per client.
**APIs**: Supabase (compliance tracking), Gmail (reminder emails)
**Trigger**: Quarterly schedule
**Human-in-the-Loop**: Verify compliance items, update status
**Validation Gates**: All required items checked, deadlines accurate
**Complexity**: Low | **Impact**: Medium | **Priority**: 4/10
**Build Time**: 2-3 hours

---

## Prerequisites Checklist

Before building any workflows, these need to be in place:

### Critical (Blocks Most Workflows)
- [ ] **Supabase migration from Lovable Cloud** — migrate to own Supabase instance for external access
- [ ] **QuickBooks API credentials** — Emil has sandbox, need production keys from Michael
- [ ] **Cin7 API key + username** — simple auth, no OAuth

### Important (Blocks Several Workflows)
- [ ] **Plaid API key** — for bank balance and transaction access
- [ ] **ShipStation API key** — for Piermont shipment tracking
- [ ] **Gmail/Outlook API access** — for email send/receive automation
- [ ] **GitHub Fisch-Group org admin** — Greg's invite accepted

### Nice-to-Have
- [ ] **Airtable personal access token** — for task management workflows
- [ ] **Google Calendar API** — for meeting prep workflow
- [ ] **LinkedIn API** — for prospecting workflow
- [ ] **1Password shared vault** — for secure credential sharing

---

## Recommended Build Order

### Phase 1: Foundation (Sessions 3-4)
1. WF-001: AR Aging Follow-Up ← Michael explicitly requested
2. WF-002: Daily Cash Position ← Quick win, high value
3. WF-004: Data Discrepancy Checker ← Solves Emil's pain point

### Phase 2: Client Operations (Sessions 5-6)
4. WF-003: New Client Workspace Generator ← Scales the business
5. WF-005: Weekly Client Digest ← Visibility across all clients
6. WF-010: Bank Reconciliation Alert ← Core accounting function

### Phase 3: Automation (Sessions 7-8)
7. WF-007: Multi-Client Dashboard Sync ← Automates data pipeline
8. WF-012: Piermont Inventory Reorder ← Cin7 integration
9. WF-015: Monthly Close Checklist ← Biggest time saver

### Phase 4: Intelligence (Sessions 9+)
10. WF-017: AI Financial Review ← Differentiator
11. WF-018: Gary's CS Agent ← Revenue opportunity
12. WF-016: Full Client Onboarding Agent ← Combines all above

---

*Generated by GBAutomation Workflow Ideator from Fish Group client context (Sessions 1-2)*
