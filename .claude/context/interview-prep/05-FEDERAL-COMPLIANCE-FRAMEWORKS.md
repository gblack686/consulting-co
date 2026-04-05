# Federal Compliance Frameworks

**Purpose**: Understand FedRAMP, FISMA, CUI, and other government security/compliance requirements

---

## 🔐 Overview: Why Federal Compliance is Different

Government systems face unique requirements:
- **Public trust**: Taxpayer data must be protected
- **National security**: Even unclassified data can be sensitive
- **Regulatory mandates**: Laws like FISMA require specific controls
- **Audit intensity**: IG (Inspector General) audits, GAO reviews, Congressional oversight

### How This Compares to Your Experience

| Your Background | Government Equivalent |
|----------------|----------------------|
| **HIPAA** (pharma data at Axtria) | **FedRAMP** (cloud systems for government) |
| **PHI** (Protected Health Information) | **CUI** (Controlled Unclassified Information) |
| **SOC 2 compliance** (enterprise SaaS) | **FISMA** (Federal Information Security Management Act) |
| **Azure security** (AT&T) | **AWS GovCloud** (government workloads) |

**Key Difference**: Government compliance is **more prescriptive** (specific controls mandated by law) vs. commercial compliance which is often **risk-based** (choose controls appropriate to risk).

---

## 🏛️ FedRAMP (Federal Risk and Authorization Management Program)

### What is FedRAMP?
**FedRAMP** is the government's standardized approach to:
- Security assessment of cloud services
- Authorization for use by federal agencies
- Continuous monitoring

**Think of it as**: "The government's version of SOC 2, but mandatory and much more rigorous"

### FedRAMP Impact Levels

| Level | Use Case | Example Data | Requirements |
|-------|----------|--------------|--------------|
| **Low** | Public information | Weather data, public websites | 125 controls |
| **Moderate** | Most federal systems | CUI, PII, acquisition data | 325 controls |
| **High** | National security systems | Law enforcement, intelligence | 421 controls |

**For your role**: The acquisition planning app will likely need **FedRAMP Moderate** because it handles:
- CUI (acquisition plans pre-solicitation)
- PII (contracting officer names, emails)
- Vendor pricing data (proprietary/confidential)

### FedRAMP Requirements (Moderate Level)

#### 1. Security Controls (NIST 800-53)
Based on **NIST SP 800-53** (catalog of security controls):
- **Access Control (AC)**: Role-based access, least privilege, session timeouts
- **Audit & Accountability (AU)**: Log all access, retain logs 1+ year
- **Identification & Authentication (IA)**: MFA required, PKI certificates
- **System & Communications Protection (SC)**: Encryption at rest/transit (FIPS 140-2)
- **Incident Response (IR)**: Breach notification within 1 hour

#### 2. Continuous Monitoring
- **Monthly scans**: Vulnerability scanning (e.g., Nessus, Qualys)
- **Annual assessments**: Independent 3PAO (Third Party Assessment Organization) audit
- **Real-time monitoring**: SIEM integration, anomaly detection

#### 3. Documentation Requirements
- **System Security Plan (SSP)**: How controls are implemented (~300 pages)
- **Security Assessment Report (SAR)**: 3PAO findings
- **Plan of Action & Milestones (POA&M)**: Remediation plan for gaps
- **Continuous Monitoring Plan**: Ongoing security posture

### FedRAMP and AWS

**Good News**: AWS already has FedRAMP authorizations:
- **AWS GovCloud** (US-East, US-West): FedRAMP High
- **AWS Commercial Regions**: FedRAMP Moderate (17+ services)

**What this means for you**:
- You can **inherit** AWS controls (e.g., physical security, network controls)
- You must still implement **application-level controls**:
  - Authentication/authorization in your Lambda functions
  - Encryption of data in S3/DynamoDB
  - Audit logging of API Gateway requests
  - Secure coding practices (OWASP Top 10)

### How Your AWS Experience Translates

| Your Experience (RevStar) | FedRAMP Requirement | How to Discuss |
|--------------------------|--------------------|--------------|
| **Lake Formation access controls** | AC-2 (Account Management) | "I implemented role-based access with Lake Formation, ensuring least privilege and audit logging of data access" |
| **IaC with CDK** | CM-2 (Baseline Configuration) | "I use infrastructure as code to ensure consistent, auditable deployments - critical for FedRAMP config management" |
| **Bedrock guardrails** | SC-7 (Boundary Protection) | "I implemented guardrails on LLM outputs to prevent data leakage - similar to FedRAMP's boundary protection controls" |
| **CloudWatch monitoring** | AU-2 (Audit Events) | "I set up comprehensive logging in CloudWatch - ready to extend for FedRAMP's audit retention requirements" |

---

## 📋 FISMA (Federal Information Security Management Act)

### What is FISMA?
**FISMA** is the **law** that requires federal agencies to:
- Implement information security programs
- Conduct annual security assessments
- Report incidents to US-CERT

**FedRAMP vs. FISMA**:
- **FedRAMP**: How to authorize **cloud services**
- **FISMA**: How agencies manage **all IT systems** (cloud or on-prem)

### FISMA Categorization (FIPS 199)

Federal systems are categorized by **impact** if confidentiality, integrity, or availability is lost:

| Impact | Confidentiality | Integrity | Availability |
|--------|----------------|-----------|--------------|
| **Low** | Limited disclosure | Minor errors | Brief downtime |
| **Moderate** | Serious disclosure | Significant errors | Extended downtime |
| **High** | Severe/catastrophic | Severe/catastrophic | Severe/catastrophic |

**Example for Acquisition App**:
- **Confidentiality**: MODERATE (CUI exposure could harm vendors, competition)
- **Integrity**: MODERATE (Incorrect acquisition plans → wasted taxpayer $$)
- **Availability**: LOW (Downtime delays work but isn't catastrophic)
- **Overall**: **MODERATE**

### FISMA Compliance Requirements

1. **Continuous Diagnostics & Mitigation (CDM)**: Real-time security monitoring
2. **Risk Management Framework (RMF)**:
   - Categorize → Select Controls → Implement → Assess → Authorize → Monitor
3. **Annual FISMA Reporting**: Agencies report metrics to OMB (Office of Management & Budget)
4. **Incident Reporting**: Breaches → US-CERT within 1 hour

### How Your AT&T Experience Translates

| Your Experience | FISMA Requirement | How to Discuss |
|----------------|-------------------|--------------|
| **Data governance frameworks** | FISMA data inventory requirements | "At AT&T, I established data governance to track data flows - same discipline needed for FISMA data inventory" |
| **Error monitoring systems** | FISMA audit logging | "I built error monitoring to detect schema inconsistencies - extends naturally to FISMA audit requirements" |
| **Azure SQL Managed Instance migration** | FISMA config management | "I led a migration ensuring security baselines - same rigor needed for FISMA-compliant deployments" |

---

## 🔖 CUI (Controlled Unclassified Information)

### What is CUI?
**CUI** is information that requires **safeguarding or dissemination controls** per law/regulation/policy, but is **not classified**.

**Think of it as**: "Government's version of 'confidential business information'"

### CUI vs. Classified vs. Public

| Type | Example | Marking | Access |
|------|---------|---------|--------|
| **Public** | Press releases, published RFPs | None | Anyone |
| **CUI** | Pre-solicitation acquisition plans, vendor proposals | "CUI" banner/footer | Need-to-know, US persons |
| **Classified** | National security intel | "SECRET", "TOP SECRET" | Clearance required |

### CUI Categories Relevant to Acquisition

| CUI Category | Example in Acquisition Context | Why It's Sensitive |
|--------------|-------------------------------|-------------------|
| **Procurement & Acquisition** | Draft SOWs, IGCEs, source selection plans | Premature disclosure = unfair competitive advantage |
| **Proprietary Business Information** | Vendor cost breakdowns, trade secrets | Legally protected under procurement integrity rules |
| **Privacy** | Contracting officer contact info, vendor employee data | PII protections |
| **Legal Privilege** | Attorney opinions on protest disputes | Attorney-client privilege |

### CUI Handling Requirements (NIST 800-171)

**NIST SP 800-171** defines 110 security controls for protecting CUI in **non-federal systems** (contractors):

#### Key Controls for Your AI System

1. **Access Control**:
   - Limit access to authorized users only
   - Enforce least privilege
   - Separate duties (e.g., technical staff can't see source selection scores)

2. **Encryption**:
   - **At rest**: FIPS 140-2 validated encryption (AES-256)
   - **In transit**: TLS 1.2+ (no SSL, no TLS 1.0/1.1)

3. **Audit Logging**:
   - Log all access to CUI (who, what, when)
   - Retain logs 1+ year
   - Protect logs from tampering (write-once storage)

4. **Incident Response**:
   - Report CUI breaches to agency within 72 hours
   - Preserve forensic evidence

5. **Media Protection**:
   - Sanitize/destroy storage media (can't just "delete" files)
   - Use approved destruction methods (e.g., NIST 800-88 purge/destroy)

### How Your Agentic Systems Must Handle CUI

| AI Component | CUI Risk | Mitigation Strategy |
|--------------|----------|---------------------|
| **RAG Vector DB** | Embeddings may leak CUI content | Encrypt vectors, access controls on OpenSearch/pgvector |
| **Prompt Logging** | Prompts contain CUI from user queries | Redact/tokenize CUI in logs, restrict log access |
| **Model Fine-tuning** | Training data includes CUI documents | Use AWS Bedrock (ephemeral, doesn't train on your data) or SageMaker with isolated VPC |
| **Agent Memory** | Conversation history accumulates CUI | Encrypt DynamoDB tables, auto-expire sessions |
| **Output Documents** | Generated APs contain CUI | Watermark outputs with "CUI" markings, enforce download controls |

**Critical Point**: Even if the LLM (e.g., Claude in Bedrock) doesn't retain data, **your system's infrastructure** (S3 buckets, logs, databases) must protect CUI per NIST 800-171.

---

## 🛡️ Additional Federal Compliance Considerations

### 1. Authority to Operate (ATO)

**ATO** is the formal authorization to run a system in production:
- Issued by agency's Authorizing Official (AO)
- Based on risk assessment (RMF process)
- Typically 3-year term, then re-authorization required

**Your Role**: You won't get the ATO (that's the agency's job), but you must **design the system to be ATO-able**:
- Complete security documentation (SSP, SAR)
- Implement all required controls
- Demonstrate continuous monitoring

### 2. Section 508 (Accessibility)

Federal systems must be **accessible** to people with disabilities:
- WCAG 2.0 Level AA compliance
- Screen reader compatibility
- Keyboard navigation

**For your GenAI app**:
- Ensure UI is 508-compliant
- Provide alt-text for AI-generated diagrams
- Support assistive technologies

### 3. Privacy (Privacy Act, E-Government Act)

If the system processes **PII** (personally identifiable information):
- Conduct **Privacy Impact Assessment (PIA)**
- Publish **System of Records Notice (SORN)** (if applicable)
- Implement privacy controls (NIST 800-53 Appendix J)

**For acquisition app**: May contain PII of:
- Government employees (contracting officers, program managers)
- Vendor employees (proposal authors, key personnel)

### 4. Data Retention & Destruction

FAR requires acquisition records be retained:
- **7 years** after contract completion (FAR 4.805)
- May be longer for certain contract types (e.g., construction = 10 years)

**Implications for your system**:
- Can't auto-delete old data after X days (common in commercial SaaS)
- Must support legal holds (e.g., GAO audit, protest litigation)
- Destruction must follow NIST 800-88 (secure sanitization)

---

## 💡 Key Talking Points for Interview

### When They Ask: "What do you know about FedRAMP?"
**Your Answer**:
> "FedRAMP is the government's cloud security authorization framework based on NIST 800-53 controls. For a system handling acquisition data - which includes CUI like pre-solicitation plans and vendor pricing - we'd likely need FedRAMP Moderate authorization.
>
> The good news is AWS already has FedRAMP Moderate authorization for many services (Bedrock, Lambda, S3, DynamoDB), so we can inherit infrastructure controls. Our focus would be implementing application-level controls: strong authentication, encryption at rest/transit with FIPS 140-2 algorithms, comprehensive audit logging, and secure coding practices.
>
> At RevStar, I implemented similar patterns - encrypting data lakes with KMS, setting up Lake Formation access controls, and using IaC for consistent security baselines. The discipline is the same; the control catalog is just more extensive."

### When They Ask: "How do you ensure the AI system protects CUI?"
**Your Answer**:
> "Protecting CUI in an AI system requires controls at multiple layers:
>
> 1. **Data layer**: Encrypt all CUI at rest (S3, DynamoDB) with FIPS 140-2 validated crypto, enforce encryption in transit with TLS 1.2+
>
> 2. **Access layer**: Implement role-based access controls - not everyone should see source selection data. Use IAM policies, VPC isolation, and private API endpoints.
>
> 3. **Processing layer**: Use AWS Bedrock which doesn't train on customer data, ensuring CUI doesn't leak into model weights. For RAG, encrypt vector embeddings and restrict access to OpenSearch/pgvector.
>
> 4. **Audit layer**: Log every access to CUI documents - who queried what, when. Retain logs per NIST 800-171 (1+ year). Use CloudWatch + S3 for tamper-evident storage.
>
> 5. **Output layer**: Watermark AI-generated documents with CUI markings, enforce download controls.
>
> I handled similarly sensitive data at Axtria - patient prescription records under HIPAA. The principles are the same: least privilege, defense in depth, comprehensive audit trails."

### When They Ask: "How do you handle continuous monitoring?"
**Your Answer**:
> "Continuous monitoring for FedRAMP/FISMA requires three components:
>
> 1. **Vulnerability Management**: Monthly scans with tools like AWS Inspector, patch within required timeframes (e.g., critical vulns in 30 days for FedRAMP Moderate)
>
> 2. **Security Monitoring**: Real-time threat detection with GuardDuty, CloudTrail analysis, anomaly detection. Set up alerts for suspicious patterns - e.g., unauthorized access attempts, privilege escalation.
>
> 3. **Configuration Management**: Use AWS Config to continuously monitor compliance with security baselines. Detect drift from approved IaC configurations.
>
> At RevStar, I built LLMOps frameworks with monitoring and guardrails - the same pattern extends to security monitoring. The key is making it **actionable**: alerts must be specific enough that the SOC can respond, and dashboards must show compliance posture at a glance for auditors."

---

## 📊 Quick Reference: Compliance Acronyms

| Acronym | Full Term | What It Is |
|---------|-----------|------------|
| **FedRAMP** | Federal Risk and Authorization Management Program | Cloud security authorization |
| **FISMA** | Federal Information Security Management Act | Federal cybersecurity law |
| **CUI** | Controlled Unclassified Information | Sensitive but not classified data |
| **NIST** | National Institute of Standards and Technology | Sets government security standards |
| **NIST 800-53** | Security & Privacy Controls catalog | 1000+ controls for federal systems |
| **NIST 800-171** | Protecting CUI in Nonfederal Systems | 110 controls for contractors |
| **FIPS 140-2** | Federal Information Processing Standard | Cryptographic module validation |
| **ATO** | Authority to Operate | Permission to run system in production |
| **RMF** | Risk Management Framework | Process for authorizing systems |
| **3PAO** | Third Party Assessment Organization | Independent FedRAMP auditor |
| **US-CERT** | United States Computer Emergency Readiness Team | Federal incident response |

---

## ✅ Self-Check Questions

1. What is the difference between FedRAMP and FISMA?
2. What FedRAMP impact level would an acquisition planning app likely need?
3. What is CUI and why is it relevant to this role?
4. How does AWS's FedRAMP authorization help you, and what do you still need to implement?
5. What are three specific controls you'd implement to protect CUI in a RAG pipeline?

If you can answer these confidently, you're prepared to discuss federal compliance requirements.

---

## 🔗 Resources to Review (Optional)

- **FedRAMP Overview**: https://www.fedramp.gov/
- **NIST 800-171**: https://csrc.nist.gov/publications/detail/sp/800-171/rev-2/final
- **CUI Registry**: https://www.archives.gov/cui
- **AWS FedRAMP Compliance**: https://aws.amazon.com/compliance/fedramp/

**Time Investment**: 30-45 minutes to skim the overview pages. You don't need to memorize all controls, just understand the frameworks and how they apply to your system design.
