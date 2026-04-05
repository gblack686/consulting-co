# Consulting Workflow Commands

Complete command set for managing consulting engagements from discovery to architecture decisions.

---

## 📋 Command Overview

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/consulting-questions` | View master question list | Before discovery calls |
| `/analyze-transcripts` | Analyze call transcripts → Generate architecture prep | After discovery, before architecture meeting |
| `/generate-adr` | Create Architecture Decision Record | After architecture meeting |

---

## 🔄 Complete Consulting Workflow

### Phase 1: Discovery Preparation

**Before the first client call:**

```bash
/consulting-questions
```

**What it does:**
- Shows all 85 categorized discovery questions
- Highlights critical priority questions
- Can filter by category (security, performance, etc.)

**Output:** Question list to guide your discovery call

---

### Phase 2: Discovery Calls

**Manual Step:** Conduct discovery calls with client
- Use the master questions as a guide
- Record or transcribe the conversations
- Save transcripts to a folder

**Suggested tools:**
- Zoom auto-transcription
- Otter.ai
- Manual notes in markdown

---

### Phase 3: Architecture Meeting Preparation

**After discovery calls, before architecture discussion:**

```bash
/analyze-transcripts path/to/transcript-folder
```

**What it does:**
- Reads all transcripts from the folder
- Analyzes coverage against 85 master questions
- Identifies gaps (fully answered, partial, not covered, conflicting)
- Extracts key information (goals, users, features, constraints)
- Generates targeted questions for architecture meeting
- Creates a meeting prep document

**Output:** Architecture discussion prep document with:
- Coverage summary
- What we know
- Critical questions to ask
- Red flags detected
- Suggested meeting agenda

---

### Phase 4: Architecture Discussion Meeting

**Manual Step:** Hold architecture meeting with client
- Use prep document questions as guide
- Make architecture decisions
- Record decisions and rationale
- Note alternatives considered

**Suggested approach:**
- Share prep document with participants beforehand
- Follow suggested agenda (10 min constraints, 15 min data, etc.)
- Document decisions in real-time

---

### Phase 5: Document Architecture Decisions

**After architecture meeting:**

```bash
/generate-adr path/to/meeting-notes.md
```

**What it does:**
- Extracts decisions from meeting notes
- Identifies alternatives considered and rationale
- Categorizes decisions (architecture, tech, data, security)
- Generates comprehensive ADR document
- Creates Mermaid architecture diagrams
- Documents risks, constraints, and next steps

**Output:** Complete Architecture Decision Record with:
- Executive summary
- All decisions with rationale
- Technology stack
- Architecture diagram
- Data flows
- Security architecture
- Risks and mitigations
- Next steps

---

## 🎯 Example End-to-End Workflow

### Scenario: New Client - E-commerce Platform

#### Week 1: Discovery

**Day 1 - Pre-call:**
```
/consulting-questions
```
Review critical + high priority questions for e-commerce projects

**Day 2 - Discovery Call #1:**
- Cover: Problem & Goals, Users, Business Context, Core Features
- Record transcript → Save as `transcripts/call-1-discovery.txt`

**Day 3 - Discovery Call #2:**
- Cover: Integrations, Security, Performance, Technical Stack
- Record transcript → Save as `transcripts/call-2-technical.txt`

#### Week 2: Architecture

**Day 1 - Prep for Architecture Meeting:**
```
/analyze-transcripts transcripts/
```

Output: Meeting prep document showing:
- ✅ Covered: Problem, goals, users, core features, integrations
- ⚠️ Partial: Performance expectations, data retention
- ❌ Missing: Specific AWS services preference, monitoring requirements

Critical questions generated:
1. What's the expected order volume at peak? (Black Friday)
2. Which payment gateway integration? (Stripe vs. PayPal vs. both)
3. Preference for database? (DynamoDB vs. Aurora)
4. Real-time inventory updates required?
5. Multi-region deployment needed?

**Day 3 - Architecture Meeting:**
- Use prep questions
- Decide on: Serverless architecture, DynamoDB, Stripe, CloudFront CDN
- Document alternatives considered
- Save notes as `meetings/architecture-decision-notes.md`

**Day 4 - Document Decisions:**
```
/generate-adr meetings/architecture-decision-notes.md
```

Output: ADR with complete architecture including:
- Decision: Serverless (Lambda + API Gateway) vs. ECS
- Rationale: Lower ops overhead, auto-scaling, pay-per-use
- Tech stack: Lambda (Python), DynamoDB, S3, CloudFront
- Architecture diagram showing complete data flow
- Security: Cognito + JWT tokens
- Monitoring: CloudWatch + X-Ray
- Next steps: Build POC of checkout flow

#### Week 3: Validation

**Final check:**
```
/consulting-questions
```

Verify all critical questions answered in ADR
- Map ADR sections to question categories
- Identify any remaining gaps
- Schedule follow-up if needed

---

## 💡 Power User Tips

### Tip 1: Chain Commands for Maximum Efficiency

**Discovery → Prep → Documentation:**
```bash
# After discovery calls
/analyze-transcripts transcripts/

# Hold architecture meeting using generated questions

# After meeting
/generate-adr meeting-notes.md

# Verify completeness
/consulting-questions critical
```

### Tip 2: Use Filters to Focus

**Pre-call focus:**
```bash
/consulting-questions critical        # Just the 13 must-asks
/consulting-questions security        # Security deep-dive
/consulting-questions performance     # Performance focus
```

**Post-transcript analysis:**
```bash
/analyze-transcripts transcripts/ --focus security
/analyze-transcripts transcripts/ --format json
```

### Tip 3: Save Everything

Suggested folder structure:
```
project-name/
├── transcripts/
│   ├── call-1-discovery.txt
│   ├── call-2-technical.txt
│   └── call-3-followup.txt
├── meetings/
│   ├── architecture-discussion-prep.md  (from /analyze-transcripts)
│   ├── architecture-meeting-notes.md    (manual)
│   └── ADR-2025-11-14-ecommerce.md     (from /generate-adr)
└── deliverables/
    ├── technical-requirements.md
    ├── architecture-diagram.png
    └── implementation-plan.md
```

### Tip 4: Iterate on ADRs

ADRs evolve:
```bash
# Initial architecture
/generate-adr meeting-1-notes.md
# Output: ADR v1.0

# After Phase 1 learnings
/generate-adr meeting-2-refinement.md
# Output: ADR v2.0 (supersedes v1.0)
```

### Tip 5: Use for Client Handoffs

Create client-ready documentation:
```bash
# Generate comprehensive ADR
/generate-adr final-architecture-notes.md

# Then offer to generate:
# - Email summary for stakeholders
# - Presentation slides
# - Implementation plan
# - GitHub issues for next steps
```

---

## 🔗 Integration with Other Tools

### With Obsidian
After generating ADR:
1. Save to Obsidian vault
2. Link to daily notes
3. Tag with project name
4. Create knowledge graph connections

### With GitHub
After ADR approval:
1. Create repository from ADR
2. Generate GitHub issues for implementation tasks
3. Set up project board based on next steps
4. Link ADR in README

### With AWS
Before implementation:
1. Use ADR to create CDK/Terraform templates
2. Set up AWS environments based on architecture
3. Create monitoring dashboards from operational requirements
4. Configure security based on ADR specifications

---

## 📊 Metrics & Quality Gates

### Discovery Completeness
After `/analyze-transcripts`, aim for:
- ✅ **90%+** of critical questions answered
- ✅ **75%+** of high priority questions answered
- ⚠️ **No conflicting** information between calls

### Architecture Readiness
After `/generate-adr`, verify:
- ✅ All major architecture decisions documented
- ✅ All trade-offs explicitly stated
- ✅ All risks identified with mitigations
- ✅ Technology stack fully specified
- ✅ Next steps clear and actionable

---

## 🚨 Common Pitfalls to Avoid

### ❌ Don't Skip Discovery
**Wrong:** Jump straight to architecture meeting
**Right:** Use `/consulting-questions` → Discovery → `/analyze-transcripts` → Architecture

### ❌ Don't Rely on Memory
**Wrong:** "I think they said they need 1000 users"
**Right:** Transcript shows "10,000 concurrent users at peak"

### ❌ Don't Document Decisions Without Context
**Wrong:** "We chose DynamoDB"
**Right:** "We chose DynamoDB over Aurora because: [rationale in ADR]"

### ❌ Don't Skip Gap Analysis
**Wrong:** Assume everything is covered
**Right:** Use `/analyze-transcripts` to find gaps before architecture meeting

---

## 📚 Related Documentation

- **Master Questions:** `specs/workflows/MASTER_CONSULTING_QUESTIONS.md`
- **Consulting Framework:** `specs/workflows/agentic_systems_consulting_framework.md`
- **Workflow Guide:** `specs/core-guides/CONSULTING-WORKFLOW.md`

---

**Created:** 2025-11-14
**Purpose:** Complete consulting workflow using slash commands
**Commands:** 3 core commands + integrations
**Workflow Steps:** Discovery → Analysis → Architecture → Documentation
