# Master Consulting Questions - Summary

## ✅ What Was Created

A **streamlined, categorized master list** of 85 consulting discovery questions with:
- ✅ No redundancies
- ✅ Simple, clear language
- ✅ 19 logical categories
- ✅ Priority markings
- ✅ Deliverable mapping

## 📍 Location

**Main File:**
```
specs/workflows/MASTER_CONSULTING_QUESTIONS.md
```

**Slash Command:**
```
/consulting-questions
```

---

## 📊 Question Breakdown

### 19 Categories (85 Total Questions)

1. **Problem & Goals** (7 questions)
2. **Users & Usage** (5 questions)
3. **Business Context** (5 questions)
4. **Core Features** (6 questions)
5. **Business Logic** (3 questions)
6. **Integrations** (5 questions)
7. **UI/UX** (2 questions)
8. **Performance & Scale** (5 questions)
9. **Security & Compliance** (7 questions)
10. **Data Management** (5 questions)
11. **Technical Stack** (6 questions)
12. **Constraints** (4 questions)
13. **History & Context** (3 questions)
14. **Validation & Testing** (4 questions)
15. **Monitoring & Metrics** (3 questions)
16. **Timeline & Scope** (4 questions)
17. **Team & Communication** (5 questions)
18. **Risks & Assumptions** (3 questions)
19. **Documentation & Access** (3 questions)

---

## 🎯 Priority Levels

### 🔴 Critical (13 questions)
Must ask on every discovery call:
- Questions: 1, 4, 5, 8, 18, 20, 27, 30, 39, 40, 57, 71, 75

### 🟡 High Priority (12 questions)
Ask unless already clear:
- Questions: 2, 6, 13, 21, 22, 34, 35, 41, 51, 64, 73, 78

### 🟢 Contextual (60 questions)
Ask when relevant to project type

---

## 🚀 Quick Usage Guide

### Discovery Call Flow

**First 15 minutes:** Problem & Goals (Q1-7)
- What problem, who has it, why now

**Next 20 minutes:** Core Features & Users (Q8-26)
- Must-have features, workflows, business logic

**Next 15 minutes:** Technical & Integration (Q27-59)
- Existing systems, AWS environment, constraints

**Final 10 minutes:** Validation & Logistics (Q64-85)
- Testing, timeline, team, next steps

---

## 📋 Deliverable Mapping

Each question maps to specific deliverables:

| Deliverable | Question Categories |
|-------------|-------------------|
| **Executive Summary** | Problem & Goals, Business Context |
| **Technical Specs** | Core Features, Business Logic, Technical Stack |
| **Architecture** | Integrations, Performance, Constraints |
| **Security Plan** | Security & Compliance |
| **Data Design** | Core Features, Data Management |
| **Testing Plan** | Validation & Testing |
| **Monitoring** | Monitoring & Metrics |
| **Project Plan** | Timeline, Team, Risks |

---

## 💡 Improvements Over Original

### What Changed

**Original (discovery_call_questions.md):**
- 39 numbered questions
- Many sub-questions creating redundancy
- Verbose explanations
- ~100+ total points to cover

**New (MASTER_CONSULTING_QUESTIONS.md):**
- 85 distinct questions
- No redundancies
- Simple, direct language
- Clear categories
- Priority marking
- Deliverable mapping

### Removed Redundancies

**Example duplicates eliminated:**
- "What's the business impact?" vs "Can you quantify the value?" → Kept both as distinct (qualitative vs quantitative)
- Multiple "timeline" questions → Consolidated to 4 clear questions
- Security questions spread across sections → Unified in Security & Compliance
- Testing/validation scattered → Consolidated in one category

### Simplified Language

**Before:** "What are your performance expectations? How fast should responses be? (real-time, seconds, minutes acceptable)"

**After:** "What's an acceptable response time?"

---

## 🎨 Usage Examples

### Full Discovery
```
/consulting-questions
```
Shows all 85 questions with categories

### Focused Deep-Dive
```
/consulting-questions security
```
Shows only Security & Compliance (Q39-45)

### Pre-Call Prep
```
/consulting-questions critical
```
Shows only the 13 must-ask questions

---

## 📁 Related Files

**Original Source:**
- `claude-repos/quickstart-acme-test-claude/PRPs/docs/discovery_call_questions.md`

**Consulting Framework:**
- `specs/workflows/agentic_systems_consulting_framework.md`

**Workflow Guide:**
- `specs/core-guides/CONSULTING-WORKFLOW.md`

---

## 🔄 Recommended Workflow

### Before Client Call
1. Review master questions: `/consulting-questions`
2. Mark questions already answered in materials
3. Prepare 3-5 custom follow-ups

### During Call (60 min)
1. Start with critical questions (15 min)
2. Cover high-priority based on project type (25 min)
3. Dive into relevant categories (15 min)
4. Wrap with timeline/team/risks (5 min)

### After Call
1. Flag gaps for follow-up
2. Map answers to deliverable sections
3. Schedule technical deep-dive if needed

### Follow-Up Technical Call (if needed)
Focus on categories: 6, 8, 9, 11, 12
- Integrations, Performance, Security, Stack, Constraints

---

## 📊 Statistics

**Total Questions:** 85
**Categories:** 19
**Critical Priority:** 13 (15%)
**High Priority:** 12 (14%)
**Contextual:** 60 (71%)
**Average Call Coverage:** ~30-35 questions (35-40%)
**Typical Call Duration:** 45-60 minutes

---

**Created:** 2025-11-14
**Purpose:** Streamlined consulting discovery questions
**Format:** Markdown with categorization and priority
**Access:** File or `/consulting-questions` slash command
