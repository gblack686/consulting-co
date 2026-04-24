# PartsBase — Senior AI Engineer, Martech — Interview Prep

**Interview date:** 2026-04-25 (tomorrow)
**Role:** Senior AI Engineer, Martech
**Comp:** $200K–$250K base, fully remote
**Recruiter message angle:** Builder role. Owns martech architecture, AI-driven automations, demand gen engine. Stack includes Clay, Claude, workflow orchestration, full-funnel optimization.

---

## 1. Company snapshot (memorize this)

- **What:** World's largest B2B online parts locator + marketplace for aviation, aerospace, and defense. Think "Alibaba for aircraft parts."
- **Founded:** 1996 by Robert Hammond (still CEO). Took it private in 2003 via Hammond Acquisition Corp.
- **HQ:** Boca Raton, FL (corporate record lists Deerfield Beach too).
- **Scale:**
  - 7,500+ aerospace companies across 199 countries use it
  - 30,000+ end users
  - 114M+ line items searchable; 15B+ parts indexed across PartStore
  - Funding raised historically: ~$45.5M (Crunchbase)
  - Annual revenue: $20M+ range publicly reported (likely higher — private)
- **Annual event:** PBExpo (Miami Beach) — 49% YoY attendance growth; they use it as their flagship GTM moment.

## 2. The product surface (what you'd be marketing)

| Product | What it is | Why it matters to Martech |
|---|---|---|
| **PartsBase community** | Legacy part-locator directory/RFQ platform | The 7,500-member moat — your install base for upsell |
| **PartStore / PartStore 2.0** | Transactional B2B marketplace (launched 2023, upgraded with Oro) — 130% YoY revenue growth in 2025, AOV +33% | The new revenue engine. Demand gen funds this. |
| **PBExpress** | Self-serve 5-minute onboarding wizard — $300 subscription, digital T&Cs, auto-provisioning | 153 new customers in 2025. This is a product-led growth motion your funnel feeds. |
| **PBExpo** | Annual trade show, Miami | Martech powers pre-event demand, on-site capture, post-event nurture |

**Insight:** They have two very different buyer journeys running in parallel:
1. **AOG ("Aircraft on Ground") — minutes matter.** Mechanic's plane is grounded, every hour costs thousands. This is intent-heavy, low-funnel, transactional.
2. **Enterprise procurement — months-long RFP cycles.** Large MROs and OEMs. ABM-style, long nurture.

Your martech has to serve BOTH, and you should say so unprompted.

## 3. Leadership & org signals

- **CEO:** Robert Hammond (founder, 25+ years tech, took 2 companies public before this)
- **CFO:** Amanda Matthews
- **HR Director:** Jennifer Figueroa
- **BD/Customer Programs:** Federiko Yap
- **No publicly listed CMO or CRO** — which explains why the Martech role is "owning the demand gen engine." You'd be the de facto technical martech architect in a marketing org that's probably led by a VP Marketing.
- **Implication for you:** High autonomy, real ownership, but also means you need to bring opinions. There isn't a senior martech leader above you who already has the blueprint.

## 4. Tech + martech stack (educated inference)

Confirmed or strongly implied:
- **Commerce platform:** OroCommerce (PartStore + PBExpress are Oro-powered)
- **AI:** Claude (explicit in their message to you)
- **GTM tooling:** Clay (explicit)
- **Workflow orchestration:** ambiguous — could be n8n / Zapier / Temporal / custom. Ask.

Likely adjacent (aviation B2B norms):
- Salesforce or HubSpot for CRM
- Marketo or HubSpot Marketing Hub for MA
- LinkedIn Sales Navigator + LinkedIn Ads (given B2B ABM pattern)
- Outreach / Salesloft for sales sequencing
- ZoomInfo / Apollo for enrichment (or replaced by Clay)
- Segment or RudderStack for CDP (possible)
- Google Analytics / GA4 + a BI tool (Looker/Tableau)

## 5. Where AI actually earns its keep for this business

Frame your answers around these five leverage points. Each maps to revenue.

1. **ICP-aware lead enrichment at scale**
   Clay + Claude to enrich 7,500 existing members × their ICP expansion list. Identify lookalikes (MROs of similar fleet size, same FAA/EASA certifications, same part-category spend). *Metric: SQL-to-pipeline lift.*

2. **Intent signal mining from the marketplace itself**
   This is the killer insight. **PartsBase has proprietary intent data nobody else has** — search queries on 15B parts, failed RFQs, repeat-viewer behavior. An AI pipeline can:
   - Score accounts on their search activity ("buyer X is hunting a CFM56 HPT blade — alert the AM")
   - Detect upsell triggers (free member searching 50 parts/week → PartStore candidate)
   - Feed closed-loop attribution back to Clay/CRM
   *This is the single strongest point you can make. Mention it unprompted.*

3. **Autonomous outbound agents (Clay + Claude)**
   - Claygent scrapes prospect's public footprint (job reqs, press, filings) to tailor cold emails
   - Claude generates variants per persona (Director of Procurement vs. Chief Pilot vs. Maintenance Controller)
   - Multi-armed bandit on subject lines / send times
   *Metric: reply rate, meetings booked per SDR-hour saved.*

4. **AOG-specific funnel: minutes-to-activation**
   PBExpress already gets to 5 minutes. AI can compress it more:
   - Auto-classify inbound part-number queries and route to the right PartStore SKU
   - Pre-fill onboarding from the mechanic's operator/company context
   - Real-time Claude-driven chat to steer AOG buyers past procurement blockers
   *Metric: time-to-first-search, AOG conversion rate.*

5. **Attribution + RevOps glue**
   Connect marketing touches → PartStore transactions → LTV. Most martech orgs can't do this. AI-assisted stitching of anonymous web traffic, member IDs, and transactional revenue is a real moat.

## 6. The questions they'll probably ask (and how you answer)

### "Walk me through a martech architecture you've designed end-to-end."
Draw the funnel: capture → enrichment → routing → nurture → conversion → post-sale expansion. Name the tools at each layer. Name the data flows. End with an honest trade-off you made.

### "How would you use AI in our GTM engine?"
Use Section 5 above. Lead with **intent signal mining from the marketplace** — it's the answer they won't have heard. Then Clay+Claude autonomous outbound. Then AOG conversion.

### "Have you built autonomous agents?"
Yes — describe the Claude Code / Clay / CRM pattern. Be specific: tools used, handoff points, human-in-the-loop gates, evals you ran, failure modes you mitigated. If you use Claude Code + Clay at GBAutomation, pull a concrete example.

### "How do you measure martech?"
Answer in layers:
- **System health:** deliverability, lead hygiene, pipeline velocity
- **Pipeline KPIs:** SQL volume, SAL-to-SQL conversion, opportunity-to-close
- **Revenue KPIs:** pipeline created per $ spent, CAC, LTV, payback period
- **AI-specific:** lift vs control group, error rate of agent outputs, human-review rate declining over time

### "How do you work with Sales and RevOps?"
- SLAs on lead response time
- Weekly funnel review — shared dashboard, shared language
- Sales gets a veto on lead-quality thresholds; marketing gets a veto on over-contact
- Closed-loop attribution is a joint build

### "What's your take on Clay specifically?"
- Honest framing: Clay is great for enrichment + orchestration, dangerous as a system of record. Use it as a workflow layer on top of Salesforce/HubSpot, not instead.
- Real Clay wins: custom AI research columns, HTTP connectors into proprietary APIs (PartStore internal data → Clay table), webhook triggers into Salesforce/Outreach.
- Real Clay risks: cost per enrichment scales fast, data staleness, breaks if the source changes HTML.

### "What's your Claude philosophy?"
- Right tool for structured reasoning, extraction, drafting, classification.
- Caching + batching for cost. Sonnet for bulk, Opus for high-value generation.
- Evals matter: you don't ship an agent without a ground-truth set.
- Human-in-loop gates wherever the output touches a prospect's inbox.

### "Why PartsBase?"
Three threads:
1. **Proprietary data moat** — their marketplace produces intent signals nobody else has. Rare in martech roles.
2. **Measurable impact** — AOG is a clear, money-quantified use case. You can literally attribute revenue to reduced downtime.
3. **Builder autonomy** — no CMO/CRO buffer, direct impact, greenfield AI architecture to own.

## 7. Sharp questions YOU should ask them

(Asked in this order — signals seniority.)

1. "What does the current martech stack actually look like — CRM, MA, CDP, orchestration — and where's the biggest gap?"
2. "Who does this role report to, and how is success measured at 6 and 12 months?"
3. "How do Marketing, Sales, and RevOps currently share a pipeline number? Is there a single source of truth?"
4. "What's the split of revenue attribution between the legacy community subscription, PartStore transactions, and PBExpress self-serve?"
5. "On AI adoption — are there existing Clay/Claude builds I'd inherit, or is this greenfield?"
6. "How do you handle the data moat — are the marketplace search/query logs already in the warehouse and queryable for marketing, or is that a build?"
7. "What would a 'home run' in year one look like to you?"
8. "Who are the two or three people I'd be collaborating with most closely, and what are their titles?"
9. "You mentioned full-funnel optimization — when you say 'funnel,' do you mean the community membership funnel, PartStore transactional funnel, or both?"
10. "What's the deal around PBExpo — is the team treating that as a martech orchestration moment, or is it run separately by events?"

## 8. Red flags to listen for

- **"We don't have a CRM of record yet"** → polite warning sign; ask what that means for reporting.
- **"Marketing reports to Sales/CEO directly with no marketing ops person"** → you'd be hero AND sole person accountable. Can be a dream or a trap.
- **"We're not ready to invest in data/warehouse"** → then the AI vision can't ship.
- **"We need you to also manage the marketing team"** → this is an IC role by the title; if it creeps to management, renegotiate.
- **"Our Clay bill is already huge"** → usually means workflows aren't tuned; opportunity to show architecture value.

## 9. Comp strategy

- Band is $200K–$250K base. Fully remote.
- **Don't anchor first.** If forced, say "I'm targeting the top of your band given the scope — single-threaded owner of martech architecture, AI automations, and revenue influence — but I'm here to understand the role and the team first."
- Ask about equity (they're private — could be meaningful or nominal), bonus structure, and whether it's tied to pipeline/revenue KPIs.
- Ask about remote expectations — any travel to Boca Raton, PBExpo (Miami), customer meetings.

## 10. 48-hour quick wins you can name

If asked "what would you do in your first 90 days?":

- **Days 1–14:** Audit the stack. One-page architecture diagram. Identify the 3 biggest leaks in the funnel.
- **Days 15–45:** Instrument closed-loop attribution. Connect marketplace search data to marketing. Ship one Clay+Claude prospecting workflow with a clean eval harness.
- **Days 46–90:** Build the "marketplace-intent → sales alert" agent. Stand up a weekly funnel review. Retire at least one redundant tool.

---

## 11. One-liner for the opening

> "I've spent the last stretch building AI agents that connect demand signals to revenue — exactly the glue PartsBase's marketplace needs. The part of this role that stands out to me is that you're sitting on proprietary intent data that most B2B marketers would kill for, and the Clay/Claude stack you're already investing in is the right substrate to turn that into pipeline. I'd want to spend the conversation understanding where the current stack is, and where I can have the highest leverage in the first 90 days."

---

## Sources

- [PartsBase company overview — Crunchbase](https://www.crunchbase.com/organization/partsbase)
- [PartsBase 2026 PitchBook profile](https://pitchbook.com/profiles/company/132456-07)
- [PartsBase marketplace launch — DigitalCommerce360](https://www.digitalcommerce360.com/2023/03/15/a-long-time-aviation-parts-source-launches-a-b2b-marketplace/)
- [PartsBase + OroCommerce case study (PartStore 2.0 + PBExpress)](https://oroinc.com/b2b-ecommerce/customers/partsbase/)
- [PartStore 2.0 announcement — Yahoo Finance / BusinessWire](https://finance.yahoo.com/news/partsbase-announces-next-gen-transactional-185000129.html)
- [Robert Hammond CEO profile](https://www.linkedin.com/in/rhammond-partsbase/)
- [PartsBase executive team — Craft.co](https://craft.co/partsbase/executives)
- [Competitive landscape — Rotabull marketplaces guide](https://rotabull.com/blog/which-aircraft-parts-marketplaces-should-i-list-on)
- [PBExpo 2026](https://www.pbexpo.org/registration/)
- [Clay + Claude for GTM — Clay Bootcamp](https://claudecode.claybootcamp.com/)
- [Clay GTM engineering function](https://www.clay.com/blog/how-we-built-gtm-engineering-function)
