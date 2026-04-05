# TAC Pattern Library for Consulting Intake

Maps TAC patterns to OpenClaw workflow types discovered in consulting sessions.

## Pattern Selection Matrix

| Workflow Type | Primary TAC | Why | Applied To |
|---|---|---|---|
| Scheduled output (newsletter, report) | TAC-3 Template Engineering | Output follows a repeatable template | SKILL.md structure, output format |
| Research/discovery (trends, news) | TAC-6 One Agent One Purpose | Single focused task, one clear output | Skill design, model selection |
| Sync/integration (CRM, analytics) | TAC-5 Feedback Loops | Must validate data moved correctly | Validation step in skill |
| Content production (scripts, posts) | TAC-3 + TAC-9 Context | Template + heavy context from style prefs | Expertise.md, SOUL.md vibe |
| Approval workflows (tweets, emails) | TAC-5 + TAC-12 | Feedback + orchestration of human gate | Approval gate in skill |
| Self-improving tasks (learn patterns) | TAC-10 Self-Improving | Agent updates own skills over time | self-improve.md |
| Morning brief / daily summary | TAC-3 + TAC-5 | Template + feedback on what's useful | HEARTBEAT.md, cron job |
| Multi-step pipeline (research→draft→post) | TAC-7 ZTE | Full plan-build-test-review cycle | plan_build_improve.md |

## TAC Patterns Reference

### TAC-2: Adopt Your Agent's Perspective
**Applied to**: expertise.md construction
- The 12 leverage points determine what goes into the expert's mental model
- 4 In-Agent: Context, Model, Prompt, Tools
- 8 Through-Agent: Documentation, Types, Architecture, Tests, Planning, ADWs, Review, Observability

### TAC-3: Template Your Engineering
**Applied to**: SKILL.md files, domain-specific commands
- "Templates enable you to solve entire classes of problems"
- A SKILL.md IS a template — reusable instructions for an agent
- Every recurring workflow becomes a template skill

### TAC-5: Always Add Feedback Loops
**Applied to**: self-improve.md, validation phases
- "Given a unit of valuable work, how would you test and validate it?"
- Every skill needs a way to verify its output
- self-improve.md closes the feedback loop after execution

### TAC-6: One Agent, One Prompt, One Purpose
**Applied to**: skill design, model selection
- Each SKILL.md focuses on one workflow
- Don't combine "research topics AND write newsletter" into one skill
- Select model per skill: haiku for mechanical, sonnet for balanced, opus for complex

### TAC-7: Zero-Touch Engineering
**Applied to**: plan_build_improve.md structure
- Plan → Build → Test → Review → Generate → Ship
- Progressive maturity: start with plan-build, add test, then review
- The north star for each client's domain

### TAC-9: Elite Context Engineering
**Applied to**: expertise.md, MEMORY.md, SOUL.md
- R&D Framework: Reduce and Delegate
- Reduce: what's the minimum context this skill needs?
- Delegate: offload persistent context to MEMORY.md and expertise.md

### TAC-10: Self-Improving Prompts
**Applied to**: self-improve.md, expertise.md Part 7
- "Agents updating agents through prompts updating prompts"
- After each run, update expertise with learned patterns
- The expert gets smarter with every execution

### TAC-12: Multi-Agent Orchestration
**Applied to**: cross-domain workflows, agent team coordination
- PETER Framework: Prompt, Trigger, Environment, Review
- Use for workflows that span multiple domains
- Orchestrator dispatches domain-specific skills

## Model Selection Guide

| Task Complexity | Model | Cost | Use When |
|---|---|---|---|
| Transcript extraction, file moves | haiku | $ | Mechanical, no reasoning |
| SKILL.md writing, API research | sonnet | $$ | Structured output, good reasoning |
| Expert system design, quality review | opus | $$$ | Deep reasoning, complex judgment |

**Per agent in the pipeline**:
- Transcript parser: sonnet (structured extraction)
- Workspace builder: sonnet (template transforms)
- Domain expert builder: sonnet (structured writing)
- Browser research: sonnet (web navigation + extraction)
- YouTube research: haiku (transcript extraction is mechanical)
- Quality reviewer: opus (needs judgment for scoring)
