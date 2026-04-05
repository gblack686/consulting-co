# Expert System Pattern: The 8-File Structure

Source: eval expert in sample-multi-tenant-agent-core-app, TAC expert in consulting-co

## Standard Files (Every Domain Gets These)

```
experts/{domain}/
├── _index.md              Domain overview + command registry
├── expertise.md           Complete mental model (7+ parts)
├── question.md            Read-only query mode
├── plan.md                Planning workflow
├── plan_build_improve.md  Full ACT-LEARN-REUSE cycle
├── self-improve.md        Expertise update after runs
└── {domain-specific}.md   1-3 additional commands per domain
```

---

## 1. _index.md — Domain Overview

**Frontmatter**:
```yaml
---
type: expert
name: "{domain-name}"
domain: [{domain}, {related-tags}]
specialty: "{one-line description}"
status: active
created: {date}
updated: {date}
tags: [expert, domain-expertise, {domain}, openclaw]
---
```

**Sections**:
- **Domain Overview**: 2-3 sentences describing scope
- **Expert Type**: "Domain Expert" + specialization
- **Core Insight**: Blockquote with key principle
- **Key Capabilities**: Bullet list of what this expert can do
- **Expert Files**: Table linking to all command files
- **OpenClaw Skills**: Table of deployed skills (name, trigger, delivery)
- **Tools & APIs**: Table of connected tools (tool, API, auth, status)
- **Related**: Links to other experts
- **Changelog**: Version history

---

## 2. expertise.md — Complete Mental Model

**Frontmatter**:
```yaml
---
type: expert-file
parent: "[[{domain}/_index]]"
file-type: expertise
human_reviewed: false
tags: [expert-file, mental-model, {domain}]
last_updated: {date}
---
```

**Standard 7-Part Structure**:

### Part 1: Domain Architecture
- Overview of the client's workflow in this domain
- How tools connect to each other
- Key file locations and data flows

### Part 2: Primary Workflow
- Detailed steps for the most important workflow
- API endpoints used
- Expected inputs and outputs

### Part 3: Secondary Workflows
- Additional workflows in this domain
- Variations and edge cases

### Part 4: Tool Configuration
- Table of tools: base URL, auth header, key endpoints
- MCP server availability
- ClawHub plugin availability

### Part 5: Scheduling & Automation
- Cron jobs for this domain
- Heartbeat tasks
- Trigger patterns (webhook, event-driven)

### Part 6: Integration Points
- How this domain connects to other domains
- Shared tools or data sources
- Cross-domain workflow handoffs

### Part 7: Patterns & Learnings
- Patterns that work (populated after self-improve)
- Patterns to avoid
- Known issues
- Tips

**Target size**: 200-600 lines depending on domain complexity.

---

## 3. question.md — Read-Only Query Mode

**Frontmatter**:
```yaml
---
type: expert-file
parent: "[[{domain}/_index]]"
file-type: command
command-name: question
tags: [expert-file, command, read-only]
---
```

**Allowed Tools**: `Read, Glob, Grep, Bash(read-only)`

**Standard 6 Question Categories**:

1. **Workflow Questions** → Read expertise.md Part 2-3
   - "How does the [workflow] work?"
   - "What are the steps for [task]?"

2. **Tool/API Questions** → Read expertise.md Part 4
   - "What's the [tool] API endpoint?"
   - "How do I authenticate with [service]?"

3. **Scheduling Questions** → Read expertise.md Part 5
   - "When does [task] run?"
   - "How do I change the [cron] schedule?"

4. **Configuration Questions** → Read TOOLS.md + expertise.md Part 4
   - "What API keys does this need?"
   - "Where are the credentials stored?"

5. **Integration Questions** → Read expertise.md Part 6
   - "How does [domain] connect to [other domain]?"
   - "What data flows between [A] and [B]?"

6. **Troubleshooting Questions** → Read expertise.md Part 7
   - "Why did [task] fail?"
   - "What are common issues with [tool]?"

---

## 4. plan.md — Planning Workflow

**Allowed Tools**: `Read, Write, Glob, Grep, Bash`

**Workflow**:
1. Load expertise.md for current domain state
2. Analyze the requested change/addition
3. Classify by TAC pattern (TAC-3 template, TAC-5 feedback, TAC-6 focused)
4. Research if needed (dispatch browser/youtube agents)
5. Output: `specs/{domain}-{feature}.md` with implementation plan

---

## 5. plan_build_improve.md — Full ACT-LEARN-REUSE

**Allowed Tools**: `Task, TaskOutput, Read, Write, Edit, Glob, Grep, Bash`

**Workflow**:
```
ACT → LEARN → REUSE

Step 1: Plan (ACT) — Create TAC-informed implementation plan
Step 2: Build (ACT) — Execute the implementation
Step 3: Self-Improve (LEARN) — Update expertise with new patterns
```

**Flow Control**:
```
Receive Request → Plan → Plan Approved? → Build → Successful?
                   ↑ No                         ↑ No → Fix → Build
                   └─────────────────────────────┘
                                                    ↓ Yes
                                          HITL? → Review → Approved?
                                                            ↓ Yes
                                                     Self-Improve → Done
```

---

## 6. self-improve.md — Learning Workflow

**Allowed Tools**: `Read, Edit, Glob, Grep, Bash`

**Workflow**:
1. Gather latest run results (logs, outputs, errors)
2. Analyze outcome vs. expected behavior
3. Update expertise.md Part 7 with:
   - New patterns_that_work
   - New patterns_to_avoid
   - Updated known_issues
   - New tips
4. Update `last_updated` timestamp

---

## 7. Domain-Specific Commands

Generated based on workflow types discovered in the session:

| Workflow Type | Command Name | Purpose |
|---|---|---|
| Scheduled output | `schedule-{type}.md` | Produce and deliver scheduled content |
| Research/discovery | `research-{topic}.md` | Find and summarize information |
| Sync/integration | `sync-{tool}.md` | Synchronize data between tools |
| Content production | `draft-{type}.md` | Create draft content for review |
| Analytics/reporting | `report-{metric}.md` | Generate and deliver reports |
| Maintenance/ops | `maintenance.md` | Run health checks, cleanup, status |

**Standard structure for each**:
```yaml
---
type: expert-file
parent: "[[{domain}/_index]]"
file-type: command
command-name: {name}
model: sonnet  # or opus for complex commands
tags: [expert-file, command, {domain}]
---
```

Sections: Purpose, Allowed Tools, Workflow (phased), Report Format.
