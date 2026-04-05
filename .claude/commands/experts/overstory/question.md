---
type: expert-file
parent: "[[overstory/_index]]"
file-type: command
command-name: "question"
human_reviewed: false
tags: [expert-file, command, read-only]
---

# Overstory Expert - Question Mode

> Read-only command to query Overstory multi-agent orchestration without making any changes.

## Purpose
Answer questions about Overstory CLI, agent fleet management, merge resolution, inter-agent messaging, runtime abstraction, and multi-agent orchestration patterns **without making any code changes**.

## Usage
```
/experts:overstory:question [question]
```

## Allowed Tools
`Read`, `Grep`, `Glob`, `Agent` (Explore only)

---

## Workflow

1. **Receive question** from user
2. **Check expertise.md** first for cached knowledge
3. **If not found**, read the source file directly from `C:/Users/gblac/OneDrive/Desktop/overstory/`
4. **Return answer** with source reference

---

## Question Categories

### Category 1: Architecture Questions
Questions about Overstory's design, hierarchy, data flow.

**Examples**:
- "How does the agent hierarchy work?"
- "What are the 5 SQLite databases?"
- "How does the two-layer instruction system work?"

**Resolution**:
1. Read `expertise.md` for architecture summary
2. Read `C:/Users/gblac/OneDrive/Desktop/overstory/CLAUDE.md` for deep details
3. Read specific source files if needed

---

### Category 2: CLI Command Questions
Questions about specific `ov` commands and their usage.

**Examples**:
- "How do I spawn a builder agent?"
- "What does `ov doctor` check?"
- "How do I merge all completed branches?"

**Resolution**:
1. Read `expertise.md` CLI commands section
2. Read the specific command file: `C:/Users/gblac/OneDrive/Desktop/overstory/src/commands/{command}.ts`
3. Read `C:/Users/gblac/OneDrive/Desktop/overstory/README.md` for usage examples

---

### Category 3: Agent Role Questions
Questions about specific agent roles and their capabilities.

**Examples**:
- "What can a Lead agent do?"
- "What's the difference between Scout and Reviewer?"
- "How does the Monitor agent work?"

**Resolution**:
1. Read `expertise.md` agent roles section
2. Read the agent definition: `C:/Users/gblac/OneDrive/Desktop/overstory/agents/{role}.md`

---

### Category 4: Runtime Questions
Questions about runtime adapters and multi-provider support.

**Examples**:
- "How do I route scouts through OpenRouter?"
- "What runtimes does Overstory support?"
- "How does the Pi adapter work?"

**Resolution**:
1. Read `expertise.md` runtime section
2. Read `C:/Users/gblac/OneDrive/Desktop/overstory/src/runtimes/{runtime}.ts`
3. Read `C:/Users/gblac/OneDrive/Desktop/overstory/docs/runtime-abstraction.md`

---

### Category 5: Configuration Questions
Questions about config files, options, quality gates.

**Examples**:
- "How do I configure max concurrent agents?"
- "What quality gates are available?"
- "How does config.local.yaml work?"

**Resolution**:
1. Read `expertise.md` configuration section
2. Read `C:/Users/gblac/OneDrive/Desktop/overstory/src/config.ts`

---

### Category 6: Merge & Mail Questions
Questions about the merge system or inter-agent messaging.

**Examples**:
- "How does AI-resolve work?"
- "What message types are available?"
- "How do broadcast groups work?"

**Resolution**:
1. Read `expertise.md` merge/mail sections
2. Read `C:/Users/gblac/OneDrive/Desktop/overstory/src/merge/resolver.ts` or `src/mail/store.ts`

---

## Source Locations

### Primary Source
```
C:\Users\gblac\OneDrive\Desktop\overstory
├── README.md              Quick start + CLI reference
├── CLAUDE.md              Technical deep dive (709 lines)
├── STEELMAN.md            Risk analysis
├── src/commands/*.ts      CLI command implementations
├── src/runtimes/*.ts      Runtime adapters
├── agents/*.md            Agent role definitions
└── docs/                  Design documentation
```

---

## Report Format

```markdown
## Answer

{Direct answer to the question}

## Key Points

- {Point 1}
- {Point 2}
- {Point 3}

## Source Reference

- Primary: `{path/to/source}`

## Related
- {Related concept or command}
```
