# Client Health — 2026-06-15

| Client | Deploy | Engage | Items | Billing | Signal | Total | Flag |
|--------|--------|--------|-------|---------|--------|-------|------|
| Greg Trading | 5 | 1 | 5 | 6 | 8 | 4.45 | ⚠️ NEEDS_ATTENTION |
| Cruz Creations (Erica) | 4 | 1 | 3 | 6 | 7 | 3.65 | ⚠️ NEEDS_ATTENTION |
| Fish Group (Michael Fisch) | 4 | 3 | 3 | 4 | 7 | 3.85 | ⚠️ NEEDS_ATTENTION |
| Garrett Shuster | 2 | 9 | 5 | 6 | 7 | 5.45 | ⚠️ NEEDS_ATTENTION |

> Weights: Deploy 30% · Engage 25% · Items 20% · Billing 15% · Signal 10%

---

## Scoring Notes

### Greg Trading
- **Session**: 2026-02-21 | **Last git touch**: 2026-04-05 (~71 days ago)
- **Deploy (5)**: Full workspace + 4-domain expert package built (validation 94/100). REQUIRED pre-deploy items still pending after 4 months: Telegram ID, model config (glm47 unverified), API keys.
- **Engage (1)**: 114 days since session. No contact activity detected.
- **Items (5)**: 3 REQUIRED pre-deploy blockers + 7 recommended follow-ups (quiet hours confirmation, testnet start, Discord channel IDs, etc.).
- **Billing (6)**: No billing data found. Neutral.
- **Signal (8)**: Session validation rated EXCELLENT (94/100). Package quality very high.

### Cruz Creations (Erica)
- **Session**: 2026-03-05 | **Last git touch**: 2026-04-05 (~71 days ago)
- **Deploy (4)**: Workspace config built (5 agents, 11 skills). All integrations still pending: Gmail OAuth, Google Drive, Shopify API key, WhatsApp Business API, ClassBento browser automation.
- **Engage (1)**: 102 days since session. No follow-up activity detected.
- **Items (3)**: 6+ open next steps for Greg (Google Workspace setup, Shopify key, WhatsApp, GitHub repo creation, OpenClaw deploy in ~2 weeks). 6 tasks for Erica (Google Photos, Claude migration, Mailchimp cancel, etc.) — none confirmed complete.
- **Billing (6)**: No billing data found. Neutral.
- **Signal (7)**: Session notes "warm, energetic". Client keen on moon phases, content automation.

### Fish Group (Michael Fisch)
- **Session**: 2026-03-05 (Session 1), 2026-03-12 (Session 2) | **Last git touch**: 2026-04-17 (~59 days ago)
- **Deploy (4)**: Workspace + Obsidian vault built. Has second session transcript (positive engagement sign). OpenClaw EC2 still unprovisioned — blocking Finn deployment.
- **Engage (3)**: Second session happened (2026-03-12); Fisch Group vault ontology updated 2026-04-17. ~59 days since last activity.
- **Items (3)**: 4 active blockers: (CRITICAL) Supabase migration — blocks all agent Piermont data access; (CRITICAL) QuickBooks API creds — blocks AR aging, cash position, discrepancy checker; (HIGH) OpenClaw EC2; (HIGH) Airtable token.
- **Billing (4)**: "Billing: Greg to send invoice separately" — unconfirmed paid status.
- **Signal (7)**: Two sessions completed; active second-brain architecture delivered. Positive trajectory but stuck on blockers.

### Garrett Shuster
- **Session**: 2026-04-05 | **Last git touch**: 2026-06-08 (~7 days ago)
- **Deploy (2)**: Deliverable was a consulting roadmap deck (PPTX) for Sylvan Hills x GBAutomation engagement — no agent workspace or OpenClaw config generated. Not an agent build session.
- **Engage (9)**: Files committed 2026-06-08 (7 days ago). Most recently active client.
- **Items (5)**: No client profile JSON. No formal next steps documented. Roadmap delivered — next step is unclear (proceed to agent build? additional sessions?).
- **Billing (6)**: No billing data found. Neutral.
- **Signal (7)**: PPTX roadmap delivered = tangible deliverable. Positive.

---

## ⚠️ Action Items — All Clients Below 6.0

### Greg Trading (4.45) — STALE: 114 days since session
- **Action**: Re-engage immediately. Agent is undeployed after 4 months.
  1. Send Greg a check-in (Telegram/email): confirm Telegram ID, verify OpenRouter model for glm47.
  2. Schedule a 30-min follow-up to complete the 3 REQUIRED pre-deploy items.
  3. Target live deployment by 2026-06-30.

### Cruz Creations / Erica (3.65) — STALE: 102 days, most open items
- **Action**: Priority re-engagement — lowest score, most pending setup work.
  1. Send Erica the "Next Steps" email that was noted in PACKAGE_SUMMARY.md (Google Photos, ChatGPT migration, Shopify API key).
  2. Set up Google Workspace + GitHub repo (`gblack686/openclaw-erica-creations`).
  3. WhatsApp Business API onboarding is the critical path blocker for agent channel.
  4. Erica is paying $50/month for Mailchimp unnecessarily — resolve to keep client happy.

### Fish Group / Michael Fisch (3.85) — Active blockers halting deployment
- **Action**: Unblock the critical path.
  1. Ping Emil: Supabase migration status + Airtable token generation (both Emil-owned).
  2. Provision OpenClaw EC2 for Finn (Greg-owned — should be Greg's top infra priority for this client).
  3. Follow up on invoice status — billing unclear.
  4. QuickBooks creds from Emil unblocks 3 core workflows immediately.

### Garrett Shuster (5.45) — Recent but undefined next step
- **Action**: Clarify engagement path.
  1. Follow up on the Sylvan Hills roadmap delivery — get feedback.
  2. Determine if this engagement proceeds to an agent build session.
  3. Create client_profile.json to standardize tracking.
  4. Document billing and next-step agreement.
