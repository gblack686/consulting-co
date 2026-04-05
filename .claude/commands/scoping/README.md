# Scoping Commands

Commands for managing consulting project scoping, discovery, and architecture decisions.

---

## 📋 Available Commands

### `/consulting-questions [filter]`
Display master consulting discovery questions for client calls.

**Usage:**
- `/consulting-questions` - Show all 85 questions
- `/consulting-questions security` - Filter by category
- `/consulting-questions critical` - Show only critical priority

**When to use:** Before discovery calls to prepare questions

---

### `/analyze-transcripts [folder]`
Analyze call transcripts and generate targeted architecture discussion questions.

**Usage:**
```
/analyze-transcripts path/to/transcripts/
```

**What it does:**
- Reads all transcript files from folder
- Analyzes coverage against 85 master questions
- Identifies gaps (covered, partial, missing, conflicting)
- Generates targeted questions for architecture meeting
- Creates meeting prep document

**When to use:** After discovery calls, before architecture meeting

---

### `/generate-adr [notes-file]`
Generate Architecture Decision Record from meeting notes.

**Usage:**
```
/generate-adr path/to/meeting-notes.md
```

**What it does:**
- Extracts decisions from meeting notes
- Documents alternatives and rationale
- Creates comprehensive ADR with diagrams
- Tracks risks and next steps

**When to use:** After architecture discussion meeting

---

## 🔄 Complete Scoping Workflow

### Phase 1: Pre-Discovery
```bash
/consulting-questions
```
Review master questions before client calls

### Phase 2: Discovery Calls
Manual: Conduct calls, save transcripts to folder

### Phase 3: Architecture Prep
```bash
/analyze-transcripts transcripts/
```
Generate targeted questions for architecture meeting

### Phase 4: Architecture Meeting
Manual: Hold meeting using prep questions, make decisions

### Phase 5: Documentation
```bash
/generate-adr meeting-notes.md
```
Create comprehensive Architecture Decision Record

### Phase 6: Validation
```bash
/consulting-questions critical
```
Verify all critical questions answered

---

## 📁 Files in This Directory

- **consulting-questions.md** - Master question list command
- **analyze-transcripts.md** - Transcript analysis command
- **generate-adr.md** - ADR generation command
- **CONSULTING_WORKFLOW_COMMANDS.md** - Complete workflow guide
- **README.md** - This file

---

## 🎯 Quick Reference

| Phase | Command | Output |
|-------|---------|--------|
| **Prep** | `/consulting-questions` | Question list |
| **Analysis** | `/analyze-transcripts [folder]` | Meeting prep doc |
| **Documentation** | `/generate-adr [notes]` | ADR document |

---

## 📚 Related Documentation

- **Master Questions:** `specs/workflows/MASTER_CONSULTING_QUESTIONS.md`
- **Consulting Framework:** `specs/workflows/agentic_systems_consulting_framework.md`
- **Summary:** `.claude/CONSULTING_COMMANDS_COMPLETE.md`

---

**Purpose:** Project scoping and architecture decision documentation
**Commands:** 3 core scoping commands
**Workflow:** Discovery → Analysis → Architecture → Documentation
