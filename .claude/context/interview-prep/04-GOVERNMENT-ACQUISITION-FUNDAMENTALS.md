# Government Acquisition Fundamentals

**Purpose**: Understand the domain you'll be automating with GenAI agents

---

## 🏛️ What is Government Acquisition?

**Government Acquisition** is the process federal agencies use to purchase goods and services. It's governed by the **Federal Acquisition Regulation (FAR)** - a complex set of rules ensuring:
- Fair competition
- Transparency
- Compliance with laws
- Best value for taxpayers

### Why This Matters for Your Role
The GenAI application you'll build **automates the creation of acquisition planning documents** that currently take acquisition specialists weeks to prepare. Think of it as:
- **Your pharma work**: Automating patient journey analysis from messy healthcare data
- **Your CRM work**: Extracting structured insights from unstructured sales conversations
- **This role**: Extracting compliant acquisition plans from templates, SME input, and regulatory rules

---

## 📚 Federal Acquisition Regulation (FAR) - The Basics

### What is the FAR?
- **48 CFR (Code of Federal Regulations)** - the rulebook for all federal procurement
- **53 Parts** covering everything from acquisition planning to contract closeout
- **Updated regularly** - agencies must stay current with amendments

### Key FAR Parts Relevant to This Role

| FAR Part | Topic | Why It Matters for AI Automation |
|----------|-------|----------------------------------|
| **Part 7** | **Acquisition Planning** | **PRIMARY FOCUS** - This is what you're automating |
| Part 10 | Market Research | AI can scrape vendor databases, price histories |
| Part 11 | Describing Agency Needs | NLP to convert SME requirements → technical specs |
| Part 12 | Commercial Products/Services | Classification logic for buy decisions |
| Part 15 | Contracting by Negotiation | Document generation for RFPs, evaluation criteria |
| Part 16 | Contract Types | Decision trees for FFP vs. T&M vs. CPFF contracts |
| Part 36 | Construction/A&E Contracts | Specialized rules for infrastructure projects |

### FAR Part 7: Acquisition Planning (Your Core Domain)

**FAR 7.1** - Acquisition Plans (AP)
- **Purpose**: Document the strategy for acquiring goods/services
- **Required for**: Acquisitions >$10M (or lower thresholds set by agency)
- **Contents**: Market research, requirements, cost estimates, contract type justification, competition strategy

**Key Documents in Acquisition Planning**:
1. **Acquisition Plan (AP)**: Master strategy document
2. **Statement of Work (SOW)** or **Performance Work Statement (PWS)**: What the contractor will do
3. **Independent Government Cost Estimate (IGCE)**: What it should cost
4. **Market Research Report**: Who can do this work
5. **Justification & Approval (J&A)**: If not using full competition

---

## 🔄 The Acquisition Planning Process

### Traditional (Manual) Process
```
Step 1: Acquisition Specialist receives requirement from program office
  ↓
Step 2: Conducts market research (weeks of web searches, vendor calls)
  ↓
Step 3: Drafts SOW with technical SMEs (multiple review cycles)
  ↓
Step 4: Develops IGCE (researches pricing, labor rates, materials)
  ↓
Step 5: Selects contract type (FFP, T&M, CPFF) based on risk
  ↓
Step 6: Writes Acquisition Plan (synthesizes all above + FAR compliance)
  ↓
Step 7: Routes for approval (legal, contracting officer, program manager)
  ↓
Step 8: Revisions based on feedback (often 3-5 rounds)
  ↓
Result: 4-12 weeks to complete, high variability in quality
```

### AI-Augmented Process (What You'll Build)
```
Step 1: Acquisition Specialist inputs basic requirement into GenAI app
  ↓
Multi-Agent Workflow:
  - Agent 1: Market Research Agent → scrapes vendor databases, past contracts
  - Agent 2: SOW Generation Agent → uses templates + SME input + NLP
  - Agent 3: Cost Estimation Agent → RAG over historical pricing data
  - Agent 4: Compliance Agent → validates FAR requirements, flags risks
  - Agent 5: Document Assembly Agent → generates complete AP package
  ↓
Step 2: Specialist reviews/edits AI-generated draft (1-2 days)
  ↓
Result: 3-5 days to complete, consistent quality, audit trail
```

---

## 🎯 How AI Agents Automate Acquisition Planning

### Use Case 1: Document Generation
**Problem**: Writing a compliant SOW requires:
- Understanding FAR rules for performance-based contracting
- Using agency templates
- Incorporating technical requirements from SMEs
- Ensuring clarity and measurability

**AI Solution**:
- **RAG Pipeline**: Vectorize FAR Part 37 (Service Contracting) + agency templates + past SOWs
- **Agentic Workflow**:
  1. Extraction Agent: Pulls key requirements from SME emails/docs
  2. Template Agent: Selects appropriate SOW template based on requirement type
  3. Generation Agent: Drafts SOW using Claude Opus with FAR guardrails
  4. Compliance Agent: Validates output against FAR 37.6 (Performance-Based Acquisition)
- **Output**: First draft SOW in minutes, not weeks

### Use Case 2: Data Extraction & Enrichment
**Problem**: Developing IGCE requires:
- Researching labor rates for specific skill categories
- Finding historical pricing for similar contracts
- Calculating overhead, profit, travel, materials

**AI Solution**:
- **Web Scraping Agents**: Extract pricing from GSA schedules, SAM.gov, FPDS-NG
- **RAG over Historical Contracts**: "Find all IT services contracts for Dept of Defense in 2023-2024 with cloud migration SOWs"
- **Cost Estimation Agent**: Aggregates data, applies escalation factors, generates IGCE spreadsheet
- **Output**: Data-driven cost estimate with audit trail to source data

### Use Case 3: Compliance Checking
**Problem**: Acquisition Plans must comply with:
- FAR requirements (e.g., small business goals, competition requirements)
- Agency-specific policies
- Legal restrictions (e.g., prohibition on certain countries)

**AI Solution**:
- **Rule Encoding**: Convert FAR compliance rules into structured logic (decision trees, regex patterns)
- **Compliance Agent**: Scans draft AP for:
  - Missing required sections (per FAR 7.105)
  - Inconsistencies (e.g., sole-source justification without J&A)
  - Policy violations (e.g., contract length >5 years without approval)
- **Output**: Redline report with specific FAR citations and recommended fixes

---

## 🔐 Data Sensitivity in Government Acquisition

### Types of Acquisition Data

| Data Type | Sensitivity Level | Example | Handling Requirements |
|-----------|------------------|---------|----------------------|
| **Pre-solicitation planning** | CUI (Controlled Unclassified Information) | Draft SOWs, IGCEs | Encrypt at rest/transit, access controls |
| **Source selection** | CUI - High | Vendor proposals, evaluation scores | Need-to-know basis, audit logging |
| **Pricing data** | CUI | Vendor cost breakdowns | Protect from FOIA disclosure |
| **Protest information** | CUI - High | Losing vendor disputes | Legal privilege considerations |
| **Public solicitations** | Public | Final RFPs on SAM.gov | No restrictions after posting |

### Why This Matters for Your AI System
1. **Access Controls**: Not all users can see all data (e.g., contracting officers vs. technical evaluators)
2. **Audit Trails**: Every AI-generated document must be traceable to source data + prompt
3. **Data Retention**: Acquisition records must be kept per FAR 4.8 (7 years post-completion)
4. **FOIA Considerations**: AI training data may be subject to Freedom of Information Act requests

**How Your Pharma Experience Translates**:
- Patient data (Axtria) → CUI in government
- HIPAA compliance → FedRAMP compliance
- De-identification techniques → Redaction for public release
- Audit logging → Same principle, different regulation

---

## 💡 Key Talking Points for Interview

### When They Ask: "What do you know about government acquisition?"
**Your Answer**:
> "While I don't have direct government acquisition experience, I understand the core challenge: creating compliant, high-quality acquisition planning documents that adhere to FAR requirements while incorporating input from SMEs, market research, and historical data.
>
> In my pharma work at Axtria, I dealt with similarly complex regulatory environments - we processed patient data under strict compliance rules, maintained audit trails, and generated reports that had to withstand regulatory scrutiny.
>
> I see government acquisition as a document generation and workflow automation problem: extracting structured insights from unstructured inputs (SME interviews, market research, past contracts), applying rules (FAR compliance), and assembling compliant outputs (APs, SOWs, IGCEs). That's exactly what I built at GBAutomation with agentic RAG pipelines for CRM and sales intelligence."

### When They Ask: "How would you approach building this?"
**Your Answer Framework**:
1. **Discovery**: "I'd start by shadowing acquisition specialists to understand their current workflow - what takes the most time? Where do errors occur? What parts are purely templated vs. require judgment?"

2. **Data Pipeline**: "Build a RAG foundation by vectorizing FAR text, agency templates, historical contracts, and vendor databases. Use metadata tagging for retrieval optimization - e.g., tag by contract type, agency, dollar value."

3. **Agent Architecture**: "Design specialized agents for each workflow step:
   - Document generation agents (SOW, IGCE, AP)
   - Data extraction agents (market research, pricing)
   - Compliance agents (FAR validation, policy checks)
   - Orchestrator agent to coordinate the workflow"

4. **Guardrails**: "Implement prompt engineering + evaluation frameworks to ensure outputs are factual, cite sources, and flag uncertainty. Every AI-generated claim should trace back to source documents."

5. **MLOps**: "Set up monitoring for quality drift, compliance violations, user feedback loops. Track which sections of APs get edited most by humans - that's where the model needs improvement."

### When They Ask: "What challenges do you anticipate?"
**Your Answer**:
- **Encoding tacit knowledge**: Acquisition specialists have years of experience interpreting FAR - we need to extract that into structured rules
- **Handling ambiguity**: FAR is sometimes vague (e.g., "best value") - agents need to flag when human judgment is required
- **Data quality**: Historical contracts may have inconsistent formats - need robust extraction pipelines
- **Change management**: Specialists may resist AI tools - need to position as augmentation, not replacement
- **Compliance evolution**: FAR gets amended - system needs version control and easy updates

---

## 📖 Resources to Skim Before Interview

1. **FAR Part 7** (Acquisition Planning): https://www.acquisition.gov/far/part-7
   - Just read 7.1 (Acquisition Plans) and 7.105 (Contents of Written Acquisition Plans)

2. **Sample Acquisition Plan Template**: Search "DoD Acquisition Plan template PDF"
   - Understand the sections: Requirements, Market Research, Competition, Cost, Schedule

3. **CUI Marking Guide**: https://www.archives.gov/cui
   - Understand "CUI" vs. "Classified" vs. "Public"

4. **FedRAMP Overview**: (covered in document 05-FEDERAL-COMPLIANCE-FRAMEWORKS.md)

---

## 🎯 Quick Reference: Acquisition Acronyms

You'll hear these in the interview - know them cold:

| Acronym | Full Term | What It Is |
|---------|-----------|------------|
| **FAR** | Federal Acquisition Regulation | The rulebook |
| **AP** | Acquisition Plan | Strategy document you're automating |
| **SOW** | Statement of Work | What the contractor does |
| **PWS** | Performance Work Statement | Outcome-based SOW |
| **IGCE** | Independent Government Cost Estimate | What it should cost |
| **J&A** | Justification & Approval | Why not full competition |
| **RFP** | Request for Proposal | Solicitation document |
| **FPDS-NG** | Federal Procurement Data System - Next Gen | Contract award database |
| **SAM.gov** | System for Award Management | Central vendor registry |
| **GSA** | General Services Administration | Manages schedules, contracts |
| **CUI** | Controlled Unclassified Information | Sensitive but not classified |
| **FFP** | Firm-Fixed-Price | Contract type (fixed price) |
| **T&M** | Time & Materials | Contract type (hourly + materials) |
| **CPFF** | Cost-Plus-Fixed-Fee | Contract type (costs + fee) |

---

## ✅ Self-Check Questions

Before the interview, test yourself:

1. What is the FAR and why does it matter?
2. What are the key components of an Acquisition Plan?
3. How would you use RAG to automate SOW generation?
4. What's the difference between CUI and Classified information?
5. Why is audit logging critical in government AI systems?

If you can answer these, you're ready to discuss the domain intelligently.
