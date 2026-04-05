# Research — Michael Fisch Session (2026-03-05)

## Q: How does the AWS Partner Program work for consulting firms?
**Asked by**: Greg (mentioned during session — wants to send Michael more info)
**Answer**: AWS has a Partner Network (APN) program with tiered benefits. As an ISV or consulting partner, Fish Group can qualify for:
- **Partner Funding Programs**: AWS provides cash/credits to qualified partners who bring clients onto AWS. This includes Migration Acceleration Program (MAP) funding and Well-Architected review credits.
- **Minimum spend thresholds**: Usually $100k+ ARR in customer AWS spend to qualify for significant funding. Fish Group with 15 clients could potentially aggregate to that level.
- **Entry point**: AWS Activate (for startups) or APN Select tier (free to join, requires certifications). Start at https://aws.amazon.com/partners/
- **Referral model**: AWS has referred new clients to consulting partners in the past — Greg's prior company benefited from this.
**Sources**: AWS Partner Network official docs, AWS Activate program
**Action**: Greg to send Michael a detailed breakdown + intro to his AWS contact from previous company

## Q: What is the Airtable API capable of for agents?
**Asked by**: Greg and Michael (discussed agent-driven Airtable management)
**Answer**: Airtable's REST API v0 is very robust. Agents can:
- Create/update/delete records in any table
- Create new bases and tables programmatically (via Metadata API)
- Manage views, fields, and automations
- Trigger automations externally via webhooks
- List all bases the API key has access to
- Full CRUD on all data — agents can effectively "operate" all of Airtable
**Sources**: Airtable API docs (airtable.com/api), Airtable Metadata API
**Action**: Emil to generate an Airtable personal access token scoped to Fish Group bases; add to Claude Code as a skill/tool

## Q: What is the ShipStation API capable of for order management?
**Asked by**: Michael (Piermont Brands shipment request workflow)
**Answer**: ShipStation has a comprehensive REST API that supports:
- Create/manage orders and shipments programmatically
- Get tracking info by order ID or shipment ID
- Rate quotes across carriers (FedEx, UPS, USPS, etc.)
- Webhook support for order status updates (agent can listen for "shipped" events)
- Manage warehouses, products, and stores
- Integrates natively with QuickBooks, Airtable, and Lovable via Zapier/direct API
**Sources**: ShipStation Developer Docs (developer.shipstation.com)
**Action**: Obtain ShipStation API key from Piermont's admin → add to agent as shipment-request skill

## Q: Can an agent manage employee access and credentials across dozens of systems?
**Asked by**: Michael (permissions agent use case — "can I have an agent that just does employee access?")
**Answer**: Yes, with caveats. An agent can manage access for:
- Google Workspace (via Admin SDK) — provision users, manage groups, add/remove app access
- AWS IAM — create users, assign roles, manage access keys
- Airtable — invite/remove collaborators, manage permissions per base
- Systems with REST APIs: most SaaS tools (Notion, Slack, etc.) have user management endpoints
- Password managers with APIs (1Password, Bitwarden) — create shared vaults, rotate credentials
- **Limitation**: Systems without APIs require browser automation (slower, more brittle)
**Action**: Build a "permissions-agent" skill that handles Google Workspace + AWS IAM first — covers ~80% of their stack

## Q: What's the best approach to replace Gary's Philippines CS team with agents?
**Asked by**: Michael (5 CS reps, $90k/year, handling email + phone support)
**Answer**:
- **Email support**: Replace immediately with an agent that reads incoming emails, fetches order/product data from relevant APIs, drafts and sends replies. 90%+ of routine CS email is fully automatable.
- **Phone support**: Use a voice AI layer (ElevenLabs + Twilio or Voiceflow) — agent answers calls, resolves common issues, escalates edge cases to human. Costs ~$0.10-0.30/minute vs. $18/hour for human agents.
- **Recommended stack**: Gmail API (email triage) + Twilio (phone) + ElevenLabs (voice) + knowledge base (product info, policies) + escalation path to Michael/Emil Slack DM
- **Estimated savings**: ~$80k/year after ~$10-15k setup and ~$5-10k/year running cost
**Action**: Scope Gary's CS agent as Phase 2 after Fish Group internal workflows are running. Needs: product catalog, order lookup API (likely Shopify or POS), return/refund policies
