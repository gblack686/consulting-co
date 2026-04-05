# Package Summary — Fish Group

**Client**: Michael Fisch + Emil (last name TBD)
**Session**: 60-Minute Agent Build — March 5, 2026
**Processed**: 2026-03-05

---

## Agent Identity

| Field | Value |
|-------|-------|
| Name | Finn 🐟 |
| Pattern | Pattern B — Multi-agent by domain |
| Channel | Claude Code CLI |
| Model tier | Medium (gemini-2.0-flash brain / claude-3-5-haiku muscle) |
| Est. monthly cost | ~$100-200/month (Fish Group) + $25-50/month per client |

---

## Domains & Agents

| Agent | Domain | Key Workflows |
|-------|--------|--------------|
| Finn 🐟 | Orchestrator | Route commands, morning ops brief, cross-client isolation |
| Client Ops 📋 | Client management | New client onboarding, welcome packages, offboarding |
| Data Agent 📊 | Airtable + QuickBooks + ShipStation | Piermont dashboard, shipment requests, QB sync |
| Permissions 🔑 | Access management | Provision/revoke users, AWS IAM, weekly audit |
| Gary's CS 🛒 | Customer service (Phase 2) | 24/7 email + voice AI, returns + refunds |

---

## Tools & APIs

| Tool | API | Status |
|------|-----|--------|
| Claude Code | Yes | Active — Michael has it installed |
| Google Workspace | Yes | Active — needs OAuth token |
| Airtable | Yes | Active — Emil to generate personal access token |
| AWS | Yes | Not yet — set up per-client accounts |
| QuickBooks | Yes | Active — Piermont credentials needed |
| ShipStation | Yes | Needs API key from Piermont admin |
| Twilio + ElevenLabs | Yes | Phase 2 — Gary's CS voice |

---

## Research Answers

All 5 questions researched and saved to `session_output/research/questions-answered.md`:

1. **AWS Partner Program**: Fish Group can qualify for partner funding — Greg to send details
2. **Airtable API**: Fully robust — agents can CRUD records, create bases, manage automations
3. **ShipStation API**: Create/track orders, webhook events, carrier rate quotes
4. **Permissions agent**: Fully feasible for Google Workspace, AWS IAM, Airtable
5. **Gary's CS agent**: Email triage now, voice AI (Phase 2) — ~$80k/year savings potential

---

## Next Steps for Greg

1. Send Michael the follow-up email with invoice + AWS partner program details (REVIEW BEFORE SEND)
2. Schedule follow-up session: Fish Group internal workflows (client onboarding + permissions)
3. Obtain Emil's full name and email for CC on all correspondence
4. Obtain Michael's primary email address (not captured in transcript)
5. Send AWS partner program intro — contact from previous company
6. Create GitHub repo: `gblack686/openclaw-fish-group`

---

## Next Steps for Michael + Emil

1. **Get hands dirty with Claude Code** — try building a simple skill or workflow this week
2. **Generate Airtable personal access token** — Airtable → Account → Developer hub → Personal access tokens
3. **Set up AWS accounts** — start with one account for Fish Group internal, then one per client
4. **Map Piermont workflows** — list the 2-3 most painful manual steps in the Piermont workflow before next session
5. **Send Emil's email** — so Greg can CC him on all correspondence going forward

---

## Files Delivered

```
20260305-michael-fisch/
├── workspace/
│   ├── SOUL.md         ✓
│   ├── USER.md         ✓
│   ├── IDENTITY.md     ✓
│   ├── MEMORY.md       ✓
│   ├── AGENTS.md       ✓
│   ├── TOOLS.md        ✓
│   ├── HEARTBEAT.md    ✓
│   └── openclaw.json   ✓  (5 agents, 11 skills)
├── session_output/
│   ├── client_profile.json   ✓
│   ├── tool_inventory.json   ✓
│   └── research/
│       └── questions-answered.md  ✓  (5 questions)
└── diagrams/
    └── fish-group-architecture.excalidraw.md  ✓
```

---

## Pending Items

- **Emil's email**: Unknown — required before sending any CC'd emails
- **Michael's primary email**: Not captured from transcript — check Gmail history
- **Billing**: Greg to send invoice separately
