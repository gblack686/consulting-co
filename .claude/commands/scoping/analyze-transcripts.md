---
description: Analyze call transcripts and generate targeted architecture discussion questions
---

Analyze call transcripts to identify what's been covered and generate targeted questions for an architecture discussion meeting.

## Instructions

If the user didn't provide a folder path, ask:
"What folder contains your call transcripts? (provide full path or relative path)"

Once you have the folder path:

### Step 1: Read All Transcripts

1. List all files in the provided folder
2. Read all transcript files (.txt, .md, .json, or specified format)
3. Combine into a single context

### Step 2: Analyze Coverage

Reference the master questions from:
`specs/workflows/MASTER_CONSULTING_QUESTIONS.md`

For each of the 19 question categories, determine:

1. **Fully Answered** ✅ - Clear, complete information provided
2. **Partially Answered** ⚠️ - Some info but needs clarification
3. **Not Covered** ❌ - No information found
4. **Conflicting** 🔄 - Different stakeholders gave different answers

### Step 3: Extract Key Information

From the transcripts, identify and summarize:

- **Project goal** - What problem are they solving?
- **Primary users** - Who will use this?
- **Must-have features** - Core functionality mentioned
- **Integrations mentioned** - Systems they need to connect to
- **Tech stack hints** - Any technologies, frameworks, or AWS services mentioned
- **Constraints mentioned** - Timeline, budget, compliance, technical limits
- **Stakeholders identified** - Who's involved and their roles
- **Success criteria** - How they'll measure success
- **Concerns raised** - Risks, unknowns, or worries expressed

### Step 4: Identify Gaps

Create a priority list of what's missing:

**🔴 Critical Gaps** - Essential for architecture design:
- Questions about core features not yet answered
- Integration details unclear
- Security/compliance requirements unknown
- Performance/scale expectations undefined
- AWS environment context missing

**🟡 Important Gaps** - Needed for complete design:
- Technical stack preferences unclear
- Data model undefined
- User workflows not fully mapped
- Monitoring requirements not discussed

**🟢 Nice to Know** - Helpful but can be deferred:
- Edge cases not explored
- Future phases unclear
- Team structure questions

### Step 5: Generate Architecture Discussion Questions

Create a **targeted question list** organized by:

#### A. Architecture Foundation (5-10 questions)
Questions to nail down the core architecture decisions:
- Based on what's missing from categories: Integrations, Performance, Technical Stack, Constraints

#### B. Data Architecture (3-5 questions)
Questions about data flow, storage, and processing:
- Based on gaps in: Core Features, Data Management, Business Logic

#### C. Security & Compliance (3-5 questions)
Questions about security requirements:
- Based on gaps in: Security & Compliance, Data Management

#### D. Operational Requirements (3-5 questions)
Questions about monitoring, scaling, and maintenance:
- Based on gaps in: Performance & Scale, Monitoring & Metrics

#### E. Clarifications & Conflicts (2-5 questions)
Questions to resolve ambiguities or conflicting information found in transcripts

### Step 6: Generate Meeting Prep Document

Create a formatted summary:

```markdown
# Architecture Discussion - Meeting Prep

**Date Prepared:** [today's date]
**Transcripts Analyzed:** [count] files from [folder]
**Analysis Summary:** [1-2 sentences]

---

## 📊 Coverage Summary

| Category | Status | Notes |
|----------|--------|-------|
| Problem & Goals | ✅ Covered | Clear understanding of core problem |
| Users & Usage | ⚠️ Partial | User count unclear |
| ... | ... | ... |

---

## 🎯 What We Know

[Bullet-point summary of key information extracted]

---

## ❓ Critical Questions for Architecture Discussion

### A. Architecture Foundation
1. [Question based on gap analysis]
2. [Question based on gap analysis]
...

### B. Data Architecture
1. [Question]
...

### C. Security & Compliance
1. [Question]
...

### D. Operational Requirements
1. [Question]
...

### E. Clarifications
1. [Question about conflict or ambiguity]
...

---

## 🚨 Red Flags Detected

[Any concerning patterns, conflicts, or risks identified]

---

## 💡 Recommendations for Meeting

1. **Focus Areas:** [Top 2-3 categories to prioritize]
2. **Time Allocation:** [Suggested minutes per section]
3. **Participants Needed:** [Based on questions, who should attend]
4. **Pre-Meeting Tasks:** [Any info that should be gathered beforehand]

---

## 📋 Meeting Agenda (Suggested)

1. **Review Constraints** (10 min) - [Specific questions]
2. **Data Flow Discussion** (15 min) - [Specific questions]
3. **Integration Deep-Dive** (15 min) - [Specific questions]
4. **Security Requirements** (10 min) - [Specific questions]
5. **Architecture Proposal** (10 min) - Present initial design

**Total Time:** ~60 minutes
```

---

## Output

Display the full meeting prep document and offer to:
1. Save it to a file (suggest: `specs/meetings/architecture-discussion-prep-[date].md`)
2. Generate a follow-up email template to send to meeting participants
3. Create a Miro/Mermaid diagram of the architecture based on current understanding

---

## Example Usage

```
/analyze-transcripts ~/consulting-co/transcripts/acme-discovery
/analyze-transcripts C:\projects\client-calls\discovery
```

---

## Tips

- **Before the meeting:** Share the prep document with technical stakeholders
- **During the meeting:** Use the questions as a guide, not a script
- **After the meeting:** Update the document with answers and decisions
- **Follow-up:** Use `/consulting-questions` to verify nothing was missed

---

## Advanced: Multi-Transcript Analysis

If transcripts are from multiple calls, the analysis will:
- Show evolution of understanding over time
- Highlight where answers changed between calls
- Identify who provided which information
- Flag inconsistencies between stakeholders
