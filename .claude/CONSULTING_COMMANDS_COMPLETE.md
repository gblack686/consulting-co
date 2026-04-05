# ✅ Consulting Commands - COMPLETE!

## 🎉 What Was Created

A complete **consulting workflow automation system** using slash commands for discovery, analysis, and architecture documentation.

---

## 📋 Commands Created

### 1. `/consulting-questions`
**Purpose:** Display master consulting discovery questions

**Usage:**
```bash
/consulting-questions                  # All 85 questions
/consulting-questions security         # Filter by category
/consulting-questions critical         # Only critical priority
```

**When:** Before discovery calls to prepare questions

---

### 2. `/analyze-transcripts`
**Purpose:** Analyze call transcripts and generate targeted architecture discussion questions

**Usage:**
```bash
/analyze-transcripts path/to/transcripts/
```

**What it does:**
1. Reads all transcript files from folder
2. Analyzes coverage against 85 master questions
3. Identifies gaps (✅ covered, ⚠️ partial, ❌ missing, 🔄 conflicting)
4. Extracts key information (goals, users, features, constraints)
5. Generates targeted questions for architecture meeting
6. Creates meeting prep document with:
   - Coverage summary by category
   - What we know from transcripts
   - Critical questions to ask (organized by: Architecture Foundation, Data, Security, Operations, Clarifications)
   - Red flags detected
   - Recommended meeting agenda

**When:** After discovery calls, before architecture meeting

**Output:** Meeting prep document saved to `specs/meetings/architecture-discussion-prep-[date].md`

---

### 3. `/generate-adr`
**Purpose:** Generate Architecture Decision Record from meeting notes

**Usage:**
```bash
/generate-adr path/to/meeting-notes.md
```

**What it does:**
1. Extracts decisions from meeting notes
2. Identifies alternatives considered and rationale
3. Categorizes decisions (architecture, tech, data, security, operations)
4. Generates comprehensive ADR with:
   - Executive summary
   - All decisions with pros/cons/rationale
   - Complete technology stack
   - Mermaid architecture diagrams
   - Data flows
   - Security architecture
   - Operational considerations
   - Risks and mitigations
   - Open questions and next steps
   - Approval section

**When:** After architecture discussion meeting

**Output:** ADR saved to `specs/architecture/ADR-[date]-[project-name].md`

---

## 🔄 Complete Workflow

### Phase 1: Pre-Discovery
```
/consulting-questions → Review master questions
```

### Phase 2: Discovery Calls
- Conduct calls using questions as guide
- Save transcripts to folder

### Phase 3: Architecture Prep
```
/analyze-transcripts transcripts/ → Generate prep document
```

### Phase 4: Architecture Meeting
- Use prep questions
- Make decisions
- Document in notes

### Phase 5: Documentation
```
/generate-adr meeting-notes.md → Create ADR
```

### Phase 6: Validation
```
/consulting-questions critical → Verify all answered
```

---

## 📁 Files Created

### Command Files
```
.claude/commands/scoping/
├── consulting-questions.md       # View master questions
├── analyze-transcripts.md        # Analyze transcripts → prep questions
├── generate-adr.md              # Generate Architecture Decision Record
├── CONSULTING_WORKFLOW_COMMANDS.md  # Complete workflow guide
└── README.md                     # Scoping commands overview
```

### Master Questions
```
specs/workflows/
├── MASTER_CONSULTING_QUESTIONS.md    # 85 questions, 19 categories
└── MASTER_QUESTIONS_SUMMARY.md       # Summary and stats
```

### Documentation
```
.claude/
└── CONSULTING_COMMANDS_COMPLETE.md   # This file
```

---

## 🎯 Example: Real Consulting Engagement

### Client: E-commerce Platform

**Week 1 - Discovery:**
```bash
# Day 1: Prep
/consulting-questions

# Day 2-3: Hold discovery calls
# Save: transcripts/call-1-discovery.txt
#       transcripts/call-2-technical.txt
```

**Week 2 - Architecture:**
```bash
# Day 1: Analyze and prep
/analyze-transcripts transcripts/

# Output shows:
# ✅ Covered: Problem, goals, users, core features
# ⚠️ Partial: Performance expectations, monitoring
# ❌ Missing: Specific AWS services, data retention
#
# Critical questions generated:
# 1. Expected order volume at peak? (Black Friday)
# 2. Payment gateway: Stripe vs PayPal vs both?
# 3. Database preference: DynamoDB vs Aurora?
# 4. Real-time inventory updates required?
# 5. Multi-region deployment needed?

# Day 3: Architecture meeting
# Use prep questions
# Make decisions
# Save: meetings/architecture-notes.md

# Day 4: Document
/generate-adr meetings/architecture-notes.md

# Output: Complete ADR with:
# - Decision: Serverless (Lambda + API Gateway)
# - Rationale: Lower ops, auto-scaling, pay-per-use
# - Stack: Python Lambda, DynamoDB, S3, CloudFront
# - Architecture diagram
# - Security: Cognito + JWT
# - Monitoring: CloudWatch + X-Ray
# - Next steps: Build checkout POC
```

**Week 3 - Validation:**
```bash
/consulting-questions critical

# Verify all 13 critical questions answered in ADR
# Schedule follow-up for any gaps
```

---

## 💡 Key Features

### Intelligent Gap Analysis
- Compares transcripts against 85 master questions
- Identifies what's been answered vs. what's missing
- Flags conflicting information between stakeholders
- Prioritizes questions for architecture meeting

### Comprehensive ADR Generation
- Captures decisions with full context
- Documents alternatives and trade-offs
- Creates architecture diagrams
- Tracks risks and mitigations
- Defines next steps

### Workflow Integration
- Commands build on each other
- Each phase informs the next
- Complete audit trail from discovery to architecture
- Client-ready documentation

---

## 📊 Coverage

### Master Questions
- **Total:** 85 questions
- **Categories:** 19
- **Priority Levels:** Critical (13), High (12), Contextual (60)

### Analysis Capabilities
- Transcript formats: .txt, .md, .json
- Multi-transcript analysis
- Gap detection across all categories
- Conflict identification
- Evolution tracking (if multiple calls)

### ADR Structure
- Executive summary
- Problem statement
- Architecture decisions (with alternatives)
- Technology stack (complete)
- Architecture diagrams (Mermaid)
- Data flows
- Security architecture
- Operational considerations
- Risks and mitigations
- Next steps

---

## 🚀 Quick Start

### First Consulting Engagement?

**Step 1:** Review questions before first call
```
/consulting-questions
```

**Step 2:** After discovery calls, analyze gaps
```
/analyze-transcripts your-transcripts-folder/
```

**Step 3:** After architecture meeting, document
```
/generate-adr your-meeting-notes.md
```

---

## 🔗 Integration Points

### With Obsidian
- Save ADRs to Obsidian vault
- Link to daily notes
- Tag by project
- Create knowledge graph

### With GitHub
- Create repo from ADR
- Generate issues from next steps
- Set up project board
- Link ADR in README

### With AWS
- Use ADR for CDK/Terraform
- Set up environments
- Configure monitoring
- Implement security specs

---

## 📈 Benefits

### For Consultants
- ✅ Never miss critical questions
- ✅ Comprehensive gap analysis
- ✅ Professional documentation
- ✅ Repeatable workflow
- ✅ Complete audit trail

### For Clients
- ✅ Clear architecture rationale
- ✅ All decisions documented
- ✅ Risks identified upfront
- ✅ Implementation roadmap
- ✅ Reference for future decisions

---

## 🎊 Summary

You now have a **complete consulting automation system** that:

1. **Guides discovery** with 85 categorized questions
2. **Analyzes transcripts** to find gaps and generate targeted questions
3. **Documents decisions** in comprehensive ADRs
4. **Creates diagrams** to visualize architecture
5. **Tracks next steps** for implementation

**All accessible through simple slash commands!**

---

**Created:** 2025-11-14
**Commands:** 3 core commands
**Total Questions:** 85
**Workflow Phases:** 6
**Document Types:** Meeting prep, ADR, summaries
**Integration:** Obsidian, GitHub, AWS
