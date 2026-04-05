# Scope of Work Generator

## Purpose
Generate a professional Scope of Work (SOW) document from a completed planning session transcript. The SOW follows a standardized template and is ready for customer review and approval.

## Trigger
Invoked after a planning session is completed and the customer has confirmed the summary. Can also be invoked manually via `/command-invoke scope-generator`.

## Input
- Planning session transcript (all messages from the customer-planning session)
- Customer ID and session metadata

## Process

### Step 1: Extract Requirements
Analyze the planning session transcript and extract:
- Core problem statement
- Success criteria (specific, measurable)
- Feature list (prioritized)
- Technical requirements
- Integration needs
- Compliance requirements
- Timeline constraints
- Stakeholders and decision-makers

### Step 2: Generate SOW Document
Fill the template below with extracted information. Be specific and concrete. Use the customer's own language where possible.

### Step 3: Estimate
Based on the extracted requirements and GB Automation's standard engagement model:
- Map features to phases
- Estimate phase durations
- Calculate budget range based on the Agentic Systems Program pricing ($50K/90 days baseline, adjusted for scope)

### Step 4: Output
Return the completed SOW as a markdown document. Signal to the frontend that the scope is ready for review.

## SOW Template

```markdown
# Scope of Work
**Prepared for:** [Customer Name]
**Prepared by:** GB Automation
**Date:** [Current Date]
**Version:** [1]

---

## 1. Project Overview
[2-3 paragraph summary of the project, the problem it solves, and the approach]

## 2. Objectives
- [ ] [Objective 1 - specific, measurable]
- [ ] [Objective 2]
- [ ] [Objective 3]

## 3. Deliverables

### Phase 1: Discovery & Architecture (Weeks 1-2)
- [ ] Technical architecture document
- [ ] Infrastructure design (AWS)
- [ ] Test fixture definitions
- [ ] CI/CD pipeline setup

### Phase 2: Core Development (Weeks 3-8)
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]
- [ ] Integration testing

### Phase 3: Agent Orchestration (Weeks 9-10)
- [ ] Multi-agent system deployment
- [ ] RAG / knowledge graph setup
- [ ] Specialized agent training

### Phase 4: Handoff & Enablement (Weeks 11-12)
- [ ] CloudFormation deployment kit
- [ ] Team training sessions
- [ ] Documentation package
- [ ] 30-day support period

## 4. Technical Requirements
- **Cloud Platform:** AWS
- **Key Services:** [List specific AWS services]
- **Integrations:** [List integration points]
- **Compliance:** [List requirements]
- **Performance:** [Response time, throughput, scale targets]

## 5. Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| Discovery & Architecture | 2 weeks | Architecture doc, test fixtures |
| Core Development | 6 weeks | Application, APIs, agents |
| Agent Orchestration | 2 weeks | Multi-agent system, RAG |
| Handoff & Enablement | 2 weeks | Training, docs, deployment |
| **Total** | **12 weeks** | |

## 6. Assumptions & Constraints
- [List key assumptions]
- [List constraints]
- AWS account access provided by client
- Stakeholder availability for weekly check-ins

## 7. Budget Estimate

| Item | Estimate |
|------|----------|
| Agentic Systems Program (12 weeks) | $[Amount] |
| AWS Infrastructure (estimated monthly) | $[Amount] |
| **Total** | **$[Amount]** |

*Budget includes 20+ hrs/week dedicated support, 3 Claude-powered agents, infrastructure setup, training, and 30-day post-launch support.*

## 8. Success Criteria
- [ ] [Criterion 1 - measurable]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## 9. Next Steps
1. Review and approve this Scope of Work
2. Sign engagement agreement
3. Schedule kickoff call
4. Provide AWS account access and integrations list

## 10. Terms
- Payment: 50% upfront, 25% at Phase 2 completion, 25% at handoff
- Changes to scope require written agreement and may adjust timeline/budget
- Intellectual property transfers to client upon final payment
- 30-day post-launch support included

---

**Approval**

| | Name | Signature | Date |
|---|------|-----------|------|
| Customer | | | |
| GB Automation | | | |
```

## Tone
- Professional and clear
- Specific (no vague language)
- Confident but not overpromising
- Use the customer's terminology for their domain

## Context Files
- Reference `CUSTOMER-PLANNING-WORKFLOW.md` for the full template
- Reference `agentic_systems_consulting_framework.md` for pricing and service structure
