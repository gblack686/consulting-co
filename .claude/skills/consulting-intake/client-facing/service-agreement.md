# Service Agreement: OpenClaw Agent Setup

**{company_name}**
**Effective Date**: {agreement_date}

---

## 1. Parties

This Service Agreement ("Agreement") is between:

- **Provider**: {company_name}, {company_address} ("we", "us", "our")
- **Client**: {client_name}, {client_email} ("you", "your")

## 2. Services

### 2.1 Scope

We will provide the following services ("Services"):

**a) Discovery Session** (90 minutes)
- Guided consultation to define your AI agent's personality, tools, workflows, and boundaries
- Session will be recorded (with your consent) for transcript processing

**b) Agent Build & Configuration**
- OpenClaw workspace files (SOUL.md, USER.md, IDENTITY.md, MEMORY.md, AGENTS.md, TOOLS.md, HEARTBEAT.md)
- Gateway configuration (openclaw.json)
- Custom skills per discovered workflow
- Cron job setup for scheduled tasks
- Domain expert systems (self-improving knowledge bases)

**c) Deployment**
- Installation to your OpenClaw instance
- Verification and smoke testing
- Walkthrough call to demonstrate the deployed system

**d) Documentation**
- Quality report with validation scores
- Expert system documentation for ongoing self-improvement

### 2.2 Out of Scope

The following are NOT included unless separately agreed:

- Ongoing maintenance or support beyond the delivery period
- Hardware procurement or VPS setup
- Third-party API subscription costs
- Custom software development beyond OpenClaw configuration
- Training beyond the walkthrough call

### 2.3 Delivery Timeline

| Milestone | Timeline |
|-----------|----------|
| Discovery session | {session_date} |
| Workspace files delivered | +1 business day |
| Domain experts delivered | +3 business days |
| Deployment & verification | +5 business days |
| Walkthrough call | +5-7 business days |

Timelines are estimates and may vary based on complexity.

## 3. Pricing & Payment

### 3.1 Service Tiers

| Tier | Domains | Skills | Price |
|------|---------|--------|-------|
| **Foundation** | 1-2 domains | Up to 4 skills | {foundation_price} |
| **Standard** | 3-4 domains | Up to 8 skills | {standard_price} |
| **Premium** | 5+ domains | Unlimited skills | {premium_price} |

### 3.2 Payment Terms

- **Payment method**: Credit or debit card via Stripe
- **Payment schedule**: {payment_schedule}
- **Currency**: USD

### 3.3 Stripe Payment

Payment is processed securely through **Stripe** (https://stripe.com). We do not store your card details. By providing payment information, you authorize us to charge the agreed amount per the payment schedule.

**Payment link**: {stripe_payment_link}

### 3.4 Refund Policy

- **Before discovery session**: Full refund, no questions asked
- **After discovery session, before delivery**: 50% refund
- **After delivery**: No refund, but we'll work with you to resolve any issues within 14 days of delivery

### 3.5 Additional Work

Work beyond the agreed scope will be quoted separately before any additional charges are incurred.

## 4. Client Responsibilities

You agree to:

- Complete the pre-session prep guide before the discovery call
- Provide accurate information about your tools, workflows, and preferences
- Provide API keys and credentials needed for your workflows
- Ensure your OpenClaw instance is accessible for deployment (SSH access)
- Be available for the walkthrough call within the delivery window
- Review delivered materials within 7 business days

## 5. Intellectual Property

### 5.1 Your Data

You retain full ownership of:
- All data discussed in the discovery session
- All workspace files, skills, and expert systems we create for you
- Your API keys, credentials, and tool configurations

### 5.2 Our Methods

We retain ownership of:
- Our consulting methodology and question frameworks
- Template structures and pipeline tooling
- TAC pattern library and quality rubrics

You receive a perpetual, non-exclusive license to use the delivered templates and patterns for your personal or business use.

### 5.3 Session Recording

- The discovery session will be recorded with your verbal or written consent
- The recording and transcript are used solely to build your agent configuration
- Recordings are deleted within 30 days of project completion
- We will not share recordings with third parties

## 6. Confidentiality

### 6.1 Your Information

We will not disclose your personal information, business workflows, tool configurations, or any data gathered during the engagement to any third party.

### 6.2 Exceptions

This does not apply to:
- Information you authorize us to share
- Information required by law
- Anonymized, aggregated data used to improve our methodology (no personally identifiable information)

## 7. Data Security

- All credentials are stored using environment variables, never hardcoded
- Deployed configurations use OpenClaw's `allowFrom` restrictions
- We follow the principle of least privilege in all agent configurations
- API keys provided during the session are used only for your agent setup
- We do not retain copies of your credentials after deployment

## 8. Limitation of Liability

### 8.1 Agent Behavior

While we configure your agent according to your specifications, AI systems may occasionally produce unexpected results. We are not liable for:
- Actions taken by your agent after deployment
- Costs incurred from API usage by your agent
- Consequences of autonomous agent actions you have authorized

### 8.2 Maximum Liability

Our total liability under this Agreement shall not exceed the total amount paid by you for the Services.

## 9. Term & Termination

### 9.1 Term

This Agreement begins on the Effective Date and concludes upon delivery of all Services or termination.

### 9.2 Termination

Either party may terminate this Agreement with 7 days written notice. Upon termination:
- We will deliver any completed work
- Refund policy (Section 3.4) applies
- Your data and credentials will be securely deleted from our systems

## 10. Dispute Resolution

Any disputes will be resolved through good-faith negotiation. If unresolved within 30 days, disputes will be submitted to binding arbitration under the rules of {arbitration_body} in {jurisdiction}.

## 11. Amendments

This Agreement may only be modified in writing, signed by both parties.

## 12. Entire Agreement

This Agreement constitutes the entire understanding between the parties and supersedes all prior negotiations, representations, or agreements.

---

## Signatures

**Provider**: {company_name}

Name: ______________________________
Signature: ______________________________
Date: ______________________________

**Client**: {client_name}

Name: ______________________________
Signature: ______________________________
Date: ______________________________

---

## Payment

After signing, complete payment here:

**{stripe_payment_link}**

Accepted payment methods: Visa, Mastercard, American Express, and other major cards via Stripe.

Questions? Contact us at {support_email}.
