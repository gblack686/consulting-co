# Sensitive Data Handling: PII, PHI, and CUI

**Purpose**: Leverage your pharma data experience to discuss sensitive data handling in government AI systems

---

## 🎯 Why This Matters for Your Interview

Your **strongest differentiator** is your Axtria experience handling sensitive patient data:
- **1B+ records** of prescription data
- **Longitudinal patient journeys** (potentially identifiable)
- **HIPAA-regulated environment**
- **De-identification & privacy-preserving analytics**

**How to position this**: "I've built AI/ML systems in highly regulated environments where data sensitivity was paramount. The principles I applied to patient data translate directly to handling CUI in government acquisition systems."

---

## 📊 Data Sensitivity Comparison

### Your Healthcare Experience → Government Context

| Healthcare (Axtria) | Government Acquisition | Core Principle |
|---------------------|------------------------|----------------|
| **PHI** (Protected Health Information) | **CUI** (Controlled Unclassified Information) | Sensitive data requiring safeguards |
| **HIPAA** compliance | **FedRAMP/FISMA** compliance | Regulatory framework |
| **Patient identifiers** (MRN, SSN, DOB) | **PII** (employee SSN, vendor contact info) | Direct identifiers |
| **Clinical data** (diagnoses, prescriptions) | **Procurement-sensitive data** (pricing, source selection) | Confidential business/operational data |
| **De-identification** (HIPAA Safe Harbor, Expert Determination) | **Redaction** (pre-public release, FOIA) | Privacy-preserving disclosure |
| **Minimum necessary** standard | **Need-to-know** access controls | Data minimization |
| **Business Associate Agreements** | **NIST 800-171** contractor requirements | Third-party data handling |

---

## 🏥 PHI (Protected Health Information) - Your Background

### What is PHI?
Under **HIPAA**, PHI is individually identifiable health information:
- **Identifiers**: Name, address, SSN, MRN, dates (except year), biometrics, photos
- **Health data**: Diagnoses, treatments, prescriptions, lab results, payment records

### HIPAA Requirements (Refresher)
1. **Administrative Safeguards**: Policies, training, access controls
2. **Physical Safeguards**: Facility access, workstation security
3. **Technical Safeguards**: Encryption, audit logs, authentication
4. **Breach Notification**: Report breaches of 500+ records to HHS within 60 days

### Your Axtria Work: What You Should Highlight

**Patient Prescription Adherence & Longitudinal Journeys**:
- **Data Volume**: 1B+ records (demonstrates scale)
- **Data Sensitivity**: Prescription data = PHI (diagnosis inferred from meds)
- **De-identification**: Likely used anonymized/pseudonymized data for analytics
- **Regulatory Compliance**: HIPAA controls for access, audit, encryption
- **Analytics on Sensitive Data**: Built ML models without exposing individual patient identity

**Example Talking Point**:
> "At Axtria, I processed over 1 billion prescription records to analyze patient adherence and treatment pathways for a leading pharmaceutical company. This data included sensitive health information - you can infer diagnoses from medications - so we implemented strict HIPAA controls: role-based access, encrypted data at rest in Redshift, audit logging of all queries, and de-identification before analysis. I built ML models in Dataiku DSS using aggregated/anonymized datasets to protect patient privacy while still generating actionable insights."

---

## 🆔 PII (Personally Identifiable Information) - Government Context

### What is PII?
Information that can identify an individual, either alone or combined with other data:
- **Direct identifiers**: SSN, driver's license, passport, biometrics
- **Indirect identifiers**: Name + ZIP code, DOB + city, email address

### PII in Government Acquisition Systems

Your AI app will handle PII from:
1. **Government employees**:
   - Contracting officers, program managers, technical evaluators
   - Names, email addresses, phone numbers, office locations
   - Potentially: SSN (for background checks), PIV card data

2. **Vendor employees**:
   - Proposal authors, key personnel, subcontractor staff
   - Contact info, resumes, certifications
   - Potentially: Salary/compensation data (in cost proposals)

### PII Protection Requirements (NIST 800-122)

**NIST SP 800-122** (Guide to Protecting PII):

1. **Identify PII**: Determine what data is PII and assess impact of disclosure
2. **Minimize Collection**: Only collect PII necessary for the mission
3. **Safeguard PII**: Encrypt, access controls, audit logging
4. **Quality & Integrity**: Ensure PII is accurate and up-to-date
5. **Limit Use & Retention**: Use only for authorized purposes, delete when no longer needed
6. **Accountability**: Assign responsibility, train staff, conduct audits

### How Your AT&T Experience Applies

At AT&T, you handled workforce data (likely PII):
- **Workforce analytics** → Employee names, locations, roles
- **Real estate analytics** → Occupancy data tied to individuals
- **IoT workplace tracking** → Badge swipe data (PII if identifiable)

**Talking Point**:
> "At AT&T, I built workforce analytics dashboards that processed employee location and occupancy data - which included PII like names and badge IDs. I implemented access controls in SQL Server to ensure only authorized HR/facilities teams could see individual-level data. For broader analytics, I aggregated data to department/building levels to minimize PII exposure. The same data minimization principle applies here: only show identifiable acquisition data to users with a need-to-know."

---

## 🔒 CUI (Controlled Unclassified Information) - Deeper Dive

### CUI in Healthcare vs. Government Acquisition

Both domains have "sensitive but not classified" data:

| Healthcare CUI | Acquisition CUI | Why It's Sensitive |
|----------------|----------------|-------------------|
| Research data (pre-publication) | Pre-solicitation acquisition plans | Premature disclosure harms competition |
| Clinical trial protocols (proprietary) | Vendor cost proposals (proprietary) | Trade secrets, competitive advantage |
| Patient complaints (under investigation) | Protest filings (under review) | Privacy, legal privilege |
| Drug pricing negotiations | Government cost estimates (IGCE) | Market distortion if leaked |

**Key Insight**: CUI isn't just one thing - it's a **family of sensitivity categories**. Your AI system must:
- **Tag data** with appropriate CUI category (e.g., "CUI//PROPIN" for proprietary info)
- **Enforce access controls** based on category (some users can see procurement CUI but not legal CUI)
- **Watermark outputs** so users know what they're handling

### CUI Marking & Handling

**CUI Markings** (from NIST 800-171 & 32 CFR Part 2002):

**Document-level**:
```
CUI

[Document content]

CUI
```

**With category/dissemination controls**:
```
CUI//SP-PROPIN//NOFORN

[Proprietary vendor pricing data - no foreign nationals]

CUI//SP-PROPIN//NOFORN
```

**Portion marking** (for mixed documents):
```
1. (U) This section is unclassified and public.
2. (CUI) This section contains vendor proposals and is CUI.
3. (U) This section is also public.
```

**Your AI System's CUI Obligations**:
- **Auto-detect CUI**: NLP to identify sensitive content (e.g., "IGCE", "source selection", vendor names)
- **Auto-mark outputs**: AI-generated acquisition plans should be stamped "CUI" with appropriate category
- **Audit CUI access**: Log who accessed CUI documents, when, what they did with them
- **Prevent CUI leakage**: Ensure prompts/responses containing CUI aren't logged in plaintext

---

## 🧬 Cancer Data Considerations (If Applicable)

**Note**: The job description focuses on government acquisition, not healthcare. However, if the federal client is **NIH, NCI (National Cancer Institute), CDC, or a health agency**, cancer data could be relevant.

### Cancer Research Data Sensitivity

**Why cancer data is especially sensitive**:
1. **Genetic information**: Genome sequencing, biomarkers (highly identifiable, can't be anonymized easily)
2. **Diagnosis stigma**: Cancer diagnosis can affect employment, insurance, relationships
3. **Longitudinal tracking**: Decades of follow-up data (treatment → recurrence → survival)
4. **Family implications**: Genetic data reveals info about relatives (not just the patient)
5. **Research ethics**: IRB approvals, consent forms, data use agreements

**Regulatory Frameworks**:
- **HIPAA**: Standard healthcare privacy protections
- **GINA** (Genetic Information Nondiscrimination Act): Prohibits genetic discrimination
- **Common Rule** (45 CFR 46): Human subjects research protections
- **NIH Data Sharing Policy**: Requirements for sharing research data

### Cancer Data in Government AI Systems

**Possible Use Cases** (if relevant to this role):
1. **Cancer Moonshot initiatives**: NCI funding acquisition, grant proposal automation
2. **Clinical trial design**: AI to optimize trial protocols, patient matching
3. **Epidemiology**: Population-level cancer surveillance (e.g., SEER data)
4. **Precision medicine**: Genomic data → treatment recommendations

**Privacy Challenges**:
- **Re-identification risk**: Even "anonymized" genomic data can be re-identified via public genealogy databases
- **Inference attacks**: ML models can leak training data (e.g., membership inference on cancer patients)
- **Synthetic data**: Generating synthetic cancer datasets for training without exposing real patients

### How to Discuss (If Asked)

**Your Answer Framework**:
> "In my pharma work at Axtria, I dealt with longitudinal patient data that included chronic disease management - conceptually similar to cancer longitudinal studies. The key challenges were:
>
> 1. **De-identification complexity**: You can't just remove names - you need to consider quasi-identifiers (ZIP code + age + diagnosis = high re-identification risk). I worked with datasets that were de-identified using HIPAA Safe Harbor or Expert Determination methods.
>
> 2. **Data aggregation for privacy**: For population-level analytics, we aggregated to cohorts (e.g., 'patients on Drug X in Northeast region') rather than individual-level reporting.
>
> 3. **Access controls**: Clinical researchers had different access than commercial analysts. I designed role-based permissions to enforce these boundaries.
>
> If this acquisition app were supporting cancer research grants or clinical trial planning, I'd apply the same principles: strict access controls, audit logging, de-identification where possible, and differential privacy techniques if training ML models on patient data."

---

## 🛡️ Privacy-Preserving Techniques for AI Systems

### Techniques You Should Know

| Technique | What It Is | When to Use | Example in Acquisition AI |
|-----------|-----------|-------------|---------------------------|
| **De-identification** | Remove/mask direct identifiers | Sharing data for analysis | Redact vendor employee names before training summarization model |
| **Aggregation** | Report group statistics, not individuals | Public reporting, dashboards | Show "average contract value by agency" not "Contract X cost $Y" |
| **Differential Privacy** | Add calibrated noise to prevent individual inference | Training ML models | Train IGCE prediction model on historical contracts with DP guarantees |
| **Homomorphic Encryption** | Compute on encrypted data without decrypting | Cross-agency data sharing | Agencies share encrypted pricing data for market research without revealing to each other |
| **Federated Learning** | Train models on distributed data without centralization | Multi-agency model training | Each agency trains local acquisition plan generator, share only model weights |
| **Synthetic Data** | Generate fake-but-realistic data from real data distribution | Testing, demos, training | Create synthetic acquisition plans for developer testing without using real CUI |

### How to Implement in Your AWS Architecture

**Example: RAG Pipeline with PII Redaction**

```
User Query: "Show me acquisition plans for cloud migration projects"
    ↓
1. Query Preprocessing Agent
   - Detects if query contains PII/CUI
   - Logs query metadata (not content) for audit
    ↓
2. Retrieval Agent
   - Searches OpenSearch vector index
   - Retrieves top-k documents (encrypted at rest)
   - Applies access control: Does user have permission for these contracts?
    ↓
3. Redaction Agent (PRE-LLM)
   - Uses NER (Named Entity Recognition) to detect PII:
     - Names (contracting officers, vendors)
     - SSNs, phone numbers, emails
   - Replaces with tokens: "[CONTRACTING_OFFICER_1]", "[VENDOR_A]"
    ↓
4. Generation Agent (Bedrock Claude)
   - Generates summary of acquisition plans
   - Works on redacted documents, never sees PII
    ↓
5. Output Watermarking Agent
   - Stamps output with "CUI//SP-PROCUREMENT" marking
   - Logs: User X generated report Y at timestamp Z
    ↓
User receives: Compliant, de-identified summary with CUI markings
```

**Why This Matters**:
- **Principle of least privilege**: LLM doesn't need to see PII to summarize acquisition strategies
- **Audit trail**: Every step is logged for compliance reviews
- **Defense in depth**: Even if LLM leaks data, it's redacted data

---

## 💡 Key Talking Points for Interview

### When They Ask: "How do you handle sensitive data in AI systems?"
**Your Answer**:
> "I've worked with highly sensitive data in two contexts: patient prescription records at Axtria and government workforce data at AT&T. The core principles are the same:
>
> 1. **Data minimization**: Only collect and process the data you absolutely need. In acquisition AI, that means not storing raw proposal PDFs if you only need extracted pricing data.
>
> 2. **Access controls**: Role-based permissions - not everyone should see source selection evaluations. I've implemented this in Lake Formation and SQL Server.
>
> 3. **Encryption everywhere**: At rest (S3, DynamoDB), in transit (TLS 1.2+), and in use (consider AWS Nitro Enclaves for processing CUI).
>
> 4. **Audit logging**: Every access to sensitive data must be logged with who, what, when. I've built this in CloudWatch and Azure Monitor.
>
> 5. **De-identification where possible**: For training AI models, use redacted/synthetic data. For Bedrock, use its ephemeral processing - it doesn't train on your data.
>
> In this acquisition app, I'd implement a pre-processing pipeline that redacts PII before data ever reaches the LLM, ensuring we protect contracting officer identities and vendor employee information."

### When They Ask: "What's the difference between HIPAA and government data compliance?"
**Your Answer**:
> "HIPAA protects individually identifiable health information and applies to healthcare providers, insurers, and their business associates. Government data compliance - FedRAMP, FISMA, CUI - protects government operational data and applies to federal agencies and contractors.
>
> The frameworks are different, but the **principles are the same**:
> - **Risk-based security**: Identify what data is sensitive, assess impact of disclosure, apply controls proportionate to risk
> - **Encryption & access controls**: Protect data at rest and in transit, limit access to authorized users
> - **Audit & accountability**: Log all access, detect anomalies, respond to incidents
> - **Third-party oversight**: In HIPAA it's Business Associate Agreements; in government it's NIST 800-171 contractor requirements
>
> My HIPAA experience at Axtria taught me the discipline of handling regulated data. The specific controls differ (HIPAA breach notification = 60 days; FedRAMP = 1 hour), but the **mindset** is the same: treat sensitive data with extreme care, assume you'll be audited, and design systems that are secure by default."

---

## 🧪 Case Study: Longitudinal Patient Data → Acquisition Data

**How to draw the parallel in the interview**:

| Your Pharma Work | Government Acquisition Parallel |
|------------------|--------------------------------|
| **Problem**: Analyze patient adherence to chronic disease meds over 2-5 years | **Problem**: Analyze acquisition plan quality over time (pre-award → post-award) |
| **Data**: Prescription fills, diagnoses, insurance claims (PHI) | **Data**: Acquisition plans, contract awards, performance metrics (CUI) |
| **Challenge**: Longitudinal linkage requires patient identifiers, but HIPAA limits use | **Challenge**: Linking pre-solicitation data to post-award outcomes requires vendor identifiers, but CUI limits disclosure |
| **Solution**: Pseudonymization - replace patient IDs with tokens, maintain linkage table in secure environment | **Solution**: Tokenization - replace vendor names with anonymous IDs for analysis, detokenize only when authorized |
| **Analytics**: ML models predict adherence risk factors, identify high-value interventions | **Analytics**: ML models predict acquisition success factors, identify process improvements |
| **Output**: Aggregated insights for pharma client (e.g., "Patients who start med X within 30 days of diagnosis have 25% better adherence") | **Output**: Aggregated insights for acquisition leadership (e.g., "Contracts with AI-generated SOWs have 15% fewer mods") |

**Talking Point**:
> "At Axtria, I built analytics on longitudinal patient journeys - tracking individuals across years of prescriptions, diagnoses, and outcomes. The challenge was linking records over time while protecting patient identity under HIPAA. We used pseudonymization: replaced patient identifiers with tokens, maintained a secure linkage table, and ran analytics on tokenized data.
>
> I see a similar pattern in acquisition analytics: you want to track the full lifecycle of a contract - from acquisition plan creation → solicitation → award → performance - to identify what makes a successful acquisition. But you can't expose vendor identities or source selection details prematurely. The solution is the same: tokenization for analysis, strict access controls on the de-tokenization key, and aggregated reporting for insights."

---

## ✅ Self-Check Questions

1. What is the difference between PHI, PII, and CUI?
2. How does your HIPAA experience at Axtria translate to CUI handling in government?
3. What privacy-preserving technique would you use to train an AI model on vendor proposals without exposing proprietary data?
4. How would you implement a RAG pipeline that redacts PII before sending data to the LLM?
5. What is "CUI//SP-PROPIN//NOFORN" and when would you use it?

---

## 🔗 Resources (Optional)

- **NIST 800-122** (Guide to Protecting PII): https://csrc.nist.gov/publications/detail/sp/800-122/final
- **CUI Categories**: https://www.archives.gov/cui/registry/category-list
- **HIPAA vs. CUI Comparison**: Search "healthcare data in government research CUI"

**Bottom Line**: Your pharma data experience is a **huge asset**. Practice articulating how patient data protections map to government data protections, and you'll stand out as someone who deeply understands data sensitivity.
