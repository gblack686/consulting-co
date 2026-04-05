# Vibe Planning Framework

> Interactive discovery session to design the perfect .claude repository
> Voice conversation guide for consultants

---

## Session Overview

**Duration:** 1-2 hours
**Format:** Voice call (Zoom/Meet) with screen sharing
**Participants:** Consultant + Client technical lead(s)
**Outcome:** Complete VIBE_PLAN.md document with architectural decisions

---

## Pre-Session Preparation

### Consultant Prep (30 minutes before)

**Review:**
- [ ] Discovery notes from Phase 1
- [ ] Client's tech stack
- [ ] Client's GitHub/GitLab repositories (if accessible)
- [ ] Similar projects in your portfolio

**Prepare:**
- [ ] Screen share with CLAUDE-CODE-ESSENTIALS-GUIDE.md open
- [ ] Blank VIBE_PLAN.md template
- [ ] Examples from similar projects
- [ ] Cost calculator spreadsheet

**Mindset:**
- This is collaborative design, not sales
- Ask "why" questions to understand context
- Show real examples from production systems
- Be honest about what's possible and what's not

---

##

 Session Structure

### Part 1: Project Context Deep Dive (15-20 min)

**Goal:** Understand the project holistically

#### Questions

**Q1: Tell me about your project's user journey.**
- Who are the end users?
- What problem does your software solve for them?
- What's the typical user workflow?

👉 **Listen for:** Complexity signals, async/sync patterns, data flow needs

**Q2: Walk me through your technical architecture.**
- Frontend → Backend → Database → External services
- What services do you use? (AWS, Azure, third-party APIs)
- How do components communicate?

👉 **Listen for:** Integration opportunities, observability needs, infrastructure complexity

**Q3: Describe your development workflow from idea to production.**
- How do features get planned?
- How do you assign work?
- How do you review code?
- How do you deploy?

👉 **Listen for:** Pain points, automation opportunities, manual processes

**Q4: What's your biggest bottleneck right now?**
- What takes the most time?
- What causes the most frustration?
- What do you wish was automated?

👉 **Listen for:** High-value automation targets, quick wins

---

### Part 2: Primitive Selection (30-40 min)

**Goal:** Design the command, agent, hook, and skill ecosystem

#### 2.1 Commands (Slash Commands)

**Introduction:**
"Commands are like shortcuts for common workflows. Let me show you examples..."

**Share screen:** Show `/ado-log-time`, `/branch-start`, `/test` examples

**Q5: Time Tracking - Do you need to track billable hours or time logging?**

If YES:
- What system? (ADO, Jira, Harvest, Toggl, custom)
- Weekly hour targets?
- Need evidence/validation? (AWS CloudWatch activity correlation)
- Child task hierarchy? (Parent work item → daily tasks)
- Calendar sync? (auto-log meetings)

✅ **Commands to add:**
- `/log-time` or `/ado-log-time`
- `/time-status`
- `/audit-time`

**Q6: Git Workflow - How do you manage branches and commits?**

- Branching strategy? (feature/*, bugfix/*, hotfix/*)
- Commit message conventions? (Conventional Commits, custom)
- Need branch cleanup automation?
- Need PR/MR templates?

✅ **Commands to add:**
- `/branch-start [type/name]`
- `/branch-cleanup`
- `/commit [type] [message]`
- `/pr-create`

**Q7: Testing - How do you write and run tests?**

- Test frameworks? (Jest, Pytest, RSpec, etc.)
- Coverage requirements?
- Need test generation automation?
- Integration tests? E2E tests?

✅ **Commands to add:**
- `/test [filter]`
- `/unit-test [file]`
- `/generate-tests [file]`
- `/coverage`

**Q8: Cloud & Infrastructure - Do you use AWS, Azure, or GCP?**

If YES:
- Which services?
- Need credential management? (AWS Parameter Store, Secrets Manager)
- Need infrastructure-as-code? (CDK, Terraform, CloudFormation)
- Need deployment automation?

✅ **Commands to add:**
- `/aws-sign-in`
- `/deploy [environment]`
- `/infra-sync`

**Q9: Project Planning - How do you scope and plan features?**

- Do you create technical specs before coding?
- Need requirements → implementation workflow?
- Use PRD/PRPs?

✅ **Commands to add:**
- `/generate-prp [feature]`
- `/execute-prp [feature]`
- `/scope-feature`

**Q10: Domain-Specific Workflows - What repetitive tasks are unique to your domain?**

Examples:
- Data pipeline: `/run-pipeline`, `/validate-data`
- API development: `/generate-endpoint`, `/test-api`
- ML: `/train-model`, `/evaluate-model`

✅ **Commands to add:**
- [Custom commands based on domain]

---

#### 2.2 Agents (Specialized Subagents)

**Introduction:**
"Agents are like specialized team members with expertise. Let me show you the standard set..."

**Share screen:** Show agent examples with model selection

**Q11: Architecture & Design - Who makes architectural decisions on your team?**

- Need architecture planning help?
- Database schema design?
- API design?
- System design documentation?

✅ **Agents to add:**
- `@architecture-planner` (Opus) - System architecture specialist
- `@database-architect` (Sonnet) - Database schema designer
- `@api-designer` (Sonnet) - API endpoint specialist

**Q12: Testing & QA - How thorough is your testing process?**

- Need comprehensive test generation?
- Need test execution automation?
- Need QA hardening workflows?

✅ **Agents to add:**
- `@test-generator` (Sonnet) - Comprehensive test suite creation
- `@test-runner` (Haiku) - Fast test execution and analysis
- `@qa-specialist` (Sonnet) - Quality assurance expert

**Q13: Documentation - How's your documentation situation?**

- Need README generation?
- Need API documentation?
- Need architecture diagrams?
- Need code comments?

✅ **Agents to add:**
- `@documentation-generator` (Sonnet) - Creates comprehensive docs
- `@diagram-generator` (Sonnet) - Architecture visualizations

**Q14: Project Scoping - Do you need help translating requirements into technical specs?**

- Client calls → technical requirements?
- Feature requests → implementation plans?
- Cost estimation?

✅ **Agents to add:**
- `@scoping-agent` (Sonnet) - Requirements analysis
- `@revstar-scoping-agent` (Sonnet) - Full QuickStart scoping (if applicable)

**Q15: Domain Expertise - What specialized knowledge does your team need?**

Examples:
- Security: `@security-auditor`
- Performance: `@performance-optimizer`
- Accessibility: `@a11y-specialist`
- DevOps: `@devops-expert`

✅ **Agents to add:**
- [Custom domain agents]

---

#### 2.3 Hooks (Event-Driven Automation)

**Introduction:**
"Hooks run automatically at specific points in your workflow. They're like middleware for Claude Code."

**Share screen:** Show hook event timeline diagram

**Q16: Session Lifecycle - What should happen when a coding session starts/ends?**

**SessionStart possibilities:**
- Load git status
- Check for pending PRs
- Load recent issues/tickets
- Prime context with project docs
- Authenticate services (git, AWS, etc.)

**SessionEnd possibilities:**
- Save session summary
- Update work logs
- Clean up temporary files
- Send notifications

✅ **Hooks to add:**
- `SessionStart`: [selected automations]
- `SessionEnd`: [selected automations]

**Q17: Work Tracking - How do you want to track what was accomplished?**

**Stop hook possibilities:**
- Update work-status.md
- Log to knowledge graph (Graphiti)
- Send TTS/Slack notification
- Commit work-in-progress

✅ **Hooks to add:**
- `Stop`: [selected tracking]

**Q18: Observability - How much visibility do you need into Claude's actions?**

**Minimal:**
- Log major events to file

**Standard:**
- Log all tool usage
- Track command execution
- Monitor errors

**Advanced:**
- Real-time dashboard
- Tool usage metrics
- Cost tracking
- Performance monitoring

✅ **Hooks to add:**
- `PreToolUse`: [logging level]
- `PostToolUse`: [logging level]
- `SubagentStop`: [if using multi-agent workflows]

**Q19: Notifications - Do you want audio/visual notifications?**

- TTS (text-to-speech)?
- Slack messages?
- Desktop notifications?
- Email alerts?

✅ **Hooks to add:**
- `Notification`: [notification method]

---

#### 2.4 Skills (Reusable Capabilities)

**Introduction:**
"Skills are like plugins - pre-built workflows you can invoke."

**Q20: Do you need any of these standard skills?**

Standard Skills:
- [ ] **aws-cdk-diagram** - Generate architecture diagrams from CDK code
- [ ] **handoff** - Create client handoff materials (slides, checklists)
- [ ] **qa-hardening** - Comprehensive QA workflow
- [ ] **git-wizard** - Advanced git recovery and troubleshooting
- [ ] **revstar-quickstart-workflow** - Full QuickStart methodology

✅ **Skills to add:**
- [Selected from list]

**Q21: Do you have custom workflows that should be skills?**

Examples:
- Data pipeline orchestration
- Multi-stage deployment
- Compliance check workflows
- Report generation

✅ **Skills to add:**
- [Custom skills]

---

### Part 3: Integrations & Infrastructure (20-30 min)

**Goal:** Design integration architecture and select observability level

#### 3.1 Task Management

**Q22: How do you currently track tasks and projects?**

Options:
- **Azure DevOps** - Full integration available (boards, time tracking, repos)
- **Archon MCP** - Task management + RAG code search
- **Jira** - Custom integration needed
- **GitHub Issues** - Native git integration
- **Linear** - Custom integration needed
- **Other** - Assess feasibility

**If Azure DevOps:**
- Project name?
- Organization URL?
- Need time tracking? (20-hour weekly target?)
- Need board snapshots?
- Need calendar sync?

✅ **ADO Integration:**
- Time logging: YES/NO
- Board sync: YES/NO
- Calendar sync: YES/NO

**If Archon MCP:**
- Use as PRIMARY task manager? (overrides TodoWrite?)
- Need RAG code search?
- Cross-project tracking?

✅ **Archon Integration:**
- Primary task manager: YES/NO
- RAG search: YES/NO
- archon_rules.md: YES/NO

---

#### 3.2 Knowledge & Memory

**Q23: Do you need persistent memory across sessions?**

**Introduction to Graphiti:**
"Graphiti is a knowledge graph that remembers context from past sessions. It's like giving Claude a long-term memory."

**Benefits:**
- Remember past architectural decisions
- Recall previous solutions to similar problems
- Build knowledge base over time
- Semantic search for relevant context

**Cost:** Neo4j database + setup time

**Decision:**
- [ ] YES - Full Graphiti integration (Neo4j + logging hooks)
- [ ] NO - Session-based only

✅ **Knowledge Graph:**
- Graphiti: YES/NO
- If YES: Neo4j hosting? (Docker, cloud, managed)

---

#### 3.3 Observability Level

**Q24: How much visibility do you need into Claude's operations?**

**Share screen:** Show observability tier comparison

**Tier 1: Minimal** (included)
- File-based logging
- work-status.md tracking
- Basic error reporting

**Tier 2: Standard** (+2 hours setup)
- Comprehensive hook logging
- Feature tracking
- Command/agent usage stats
- JSON event logs

**Tier 3: Advanced** (+8 hours setup)
- Real-time dashboard (Vue + Bun)
- Live event streaming
- SQLite event database
- OpenTelemetry export
- Langfuse LLM tracing
- Cost tracking
- Performance metrics

✅ **Observability Tier:**
- [ ] Minimal
- [ ] Standard
- [ ] Advanced

---

#### 3.4 Cloud Services

**Q25: Which cloud services should Claude integrate with?**

**AWS:**
- [ ] Parameter Store (secrets management)
- [ ] CloudWatch (activity logging, time tracking evidence)
- [ ] S3 (artifact storage)
- [ ] Bedrock (additional models)
- [ ] Lambda (serverless functions)
- [ ] Other: [specify]

**Azure:**
- [ ] Key Vault (secrets)
- [ ] Application Insights (monitoring)
- [ ] Blob Storage (artifacts)
- [ ] Other: [specify]

**GCP:**
- [ ] Secret Manager
- [ ] Cloud Logging
- [ ] Cloud Storage
- [ ] Other: [specify]

**Third-Party:**
- [ ] Slack notifications
- [ ] GitHub/GitLab API
- [ ] Datadog/New Relic
- [ ] Other: [specify]

✅ **Cloud Integrations:**
- [List selected integrations]

---

### Part 4: Model Strategy & Cost (10-15 min)

**Goal:** Optimize model selection for performance and cost

**Q26: What's your budget for Claude API usage?**

**Share screen:** Show cost calculator

**Cost Factors:**
- Default model selection (Haiku < Sonnet < Opus)
- Agent model assignments
- Context window size
- Request frequency

**Model Strategy Templates:**

**Budget-Conscious** (~$50-100/month for 5 developers):
- Default: Haiku
- Complex tasks: Sonnet
- Critical architecture: Opus (rarely)

**Balanced** (~$200-400/month for 5 developers):
- Default: Sonnet
- Architecture: Opus
- Execution/testing: Haiku

**Performance-First** (~$500-1000/month for 5 developers):
- Default: Sonnet
- Everything complex: Opus
- Fast execution: Haiku

✅ **Model Strategy:**
- Default model: Haiku / Sonnet / Opus
- Architecture agent: Opus / Sonnet
- Test runner: Haiku / Sonnet
- Estimated monthly cost: $______

---

### Part 5: Security & Permissions (10-15 min)

**Goal:** Configure appropriate permission levels

**Q27: What's your team's experience with AI coding tools?**

- Never used AI tools → Plan mode default (safest)
- Used Copilot/ChatGPT → Default mode
- Experienced with AI → AcceptEdits mode
- Automation/CI/CD → BypassPermissions (specific contexts)

**Q28: What actions should be restricted?**

**Common restrictions:**
- [ ] Deny: `Bash(rm:*)` - Prevent deletions
- [ ] Deny: `Bash(git push --force:*)` - Prevent force pushes
- [ ] Deny: `Delete` - Require manual file deletion
- [ ] Deny: `Bash(npm publish:*)` - Prevent accidental publishes

**Q29: Should different agents have different permissions?**

Example:
- `@safe-reviewer` - Plan mode only (no modifications)
- `@test-runner` - Allow test execution, deny everything else
- `@deployment-agent` - Allow specific deployment commands only

✅ **Permission Strategy:**
- Default mode: [plan/default/acceptEdits]
- Global allow list: [tools]
- Global deny list: [tools]
- Per-agent overrides: [list]

**Q30: How should secrets be managed?**

Options:
- [ ] settings.local.json (gitignored, manual distribution)
- [ ] AWS Parameter Store (centralized, secure)
- [ ] .env files (gitignored, less secure)
- [ ] Cloud provider secret managers

✅ **Secrets Management:**
- Method: [selected method]

---

### Part 6: Timeline & Priorities (10 min)

**Goal:** Establish delivery timeline and phase priorities

**Q31: When do you need this delivered?**

**Timeline factors:**
- Complexity of requirements
- Number of integrations
- Observability level
- Custom development needed

**Typical timelines:**
- Minimal setup: 1 week
- Standard setup: 2 weeks
- Advanced setup: 3-4 weeks

✅ **Target delivery date:** [Date]

**Q32: What's the priority order?**

**Must-have (Week 1):**
- [ ] Basic commands
- [ ] Core agents
- [ ] Essential integrations

**Should-have (Week 2):**
- [ ] Advanced commands
- [ ] All agents
- [ ] Full integrations
- [ ] Standard observability

**Nice-to-have (Week 3+):**
- [ ] Custom skills
- [ ] Advanced observability
- [ ] Optimization
- [ ] Documentation polish

✅ **Phased delivery plan:**
- Phase 1: [features]
- Phase 2: [features]
- Phase 3: [features]

---

## Session Wrap-Up (5-10 min)

### Summary Review

**Consultant reads back:**

"Let me summarize what we've designed..."

**Primitives:**
- Commands: [count] - [key examples]
- Agents: [count] - [key examples]
- Hooks: [events configured]
- Skills: [count]

**Integrations:**
- [List all integrations]

**Observability:**
- Tier: [level]

**Model Strategy:**
- Default: [model]
- Estimated cost: $[amount]/month

**Timeline:**
- Target delivery: [date]
- Phased approach: [Yes/No]

**Budget:**
- Total project cost: $[amount]

### Next Steps

1. I'll create the detailed VIBE_PLAN.md document (24-48 hours)
2. You review and approve the plan
3. We begin implementation on [date]
4. Check-in calls every [frequency]
5. Handoff on [date]

### Questions?

[Q&A time]

### Feedback

"How did this session feel? Any concerns or excitement?"

---

## Post-Session Deliverable

### VIBE_PLAN.md Template

```markdown
# VIBE Plan: [Client Name] .claude Repository

**Date:** [Date]
**Client:** [Client Name]
**Project:** [Project Name]
**Consultant:** [Your Name]

## Executive Summary

[2-3 paragraph summary of the plan]

## Project Context

**User Journey:**
[Summary from Q1]

**Technical Architecture:**
[Summary from Q2]

**Development Workflow:**
[Summary from Q3]

**Primary Pain Points:**
[Summary from Q4]

## Primitive Design

### Commands ([count] total)

1. **Time Tracking**
   - `/ado-log-time` - [description]
   - `/time-status` - [description]

2. **Git Workflow**
   - `/branch-start` - [description]
   - `/commit` - [description]

[Continue for all command categories]

### Agents ([count] total)

1. **@architecture-planner** (Opus)
   - Purpose: [description]
   - Triggers: [when to use]

2. **@test-generator** (Sonnet)
   - Purpose: [description]
   - Triggers: [when to use]

[Continue for all agents]

### Hooks

**SessionStart:**
- Load git status
- [other automations]

**Stop:**
- Log to Graphiti
- [other automations]

[Continue for all configured hooks]

### Skills

- **aws-cdk-diagram** - [usage]
- [other skills]

## Integration Architecture

### Azure DevOps
- Organization: [URL]
- Project: [name]
- Features:
  - Time logging with 20-hour weekly target
  - Board snapshots
  - Calendar sync

### Archon MCP
- Primary task manager: YES
- RAG code search: YES
- archon_rules.md enforced

### Graphiti Knowledge Graph
- Neo4j hosting: [Docker/Cloud]
- Logging hooks: Stop, SessionEnd
- Semantic search enabled

### Cloud Services
- AWS Parameter Store: Secrets management
- AWS CloudWatch: Activity logging
- [other integrations]

## Observability

**Tier:** Advanced

**Components:**
- Real-time dashboard (Vue + Bun)
- SQLite event database
- OpenTelemetry export
- Langfuse LLM tracing
- Hook-based logging (all 9 events)

## Model Strategy

**Default:** Sonnet

**Agent-specific:**
- Architecture: Opus
- Testing: Haiku
- Everything else: Sonnet

**Estimated Cost:** $300/month (5 developers)

## Security & Permissions

**Default Mode:** acceptEdits

**Global Deny List:**
- `Bash(rm:*)`
- `Bash(git push --force:*)`
- `Delete`

**Secrets Management:** AWS Parameter Store

## Timeline & Deliverables

**Phase 1** (Week 1):
- Basic .claude structure
- Core commands (10)
- Core agents (5)
- Basic hooks
- ADO integration

**Phase 2** (Week 2):
- Remaining commands
- All agents
- Full hook suite
- Graphiti setup
- Observability dashboard

**Phase 3** (Week 3):
- Polish and optimization
- Documentation
- Training
- Handoff

**Target Delivery:** [Date]

## Budget

**Fixed Price:** $[Amount]

**Includes:**
- Implementation (Phases 1-3)
- Documentation
- 2-hour training session
- 30-day support

**Payment Terms:**
- 50% upfront
- 50% on completion

## Success Metrics

**Adoption:**
- 80%+ team usage within 30 days

**Efficiency:**
- 25% reduction in development time
- 50% reduction in repetitive tasks

**Quality:**
- 30% fewer bugs
- Better test coverage

## Approvals

**Client Signature:** _________________ Date: _______

**Consultant Signature:** _________________ Date: _______

---

**Approved and ready for implementation!**
```

---

## Tips for Effective Vibe Planning

### Before the Session

✅ **DO:**
- Review client's codebase beforehand
- Prepare relevant examples
- Have cost calculator ready
- Set up screen sharing

❌ **DON'T:**
- Wing it without preparation
- Assume client knows Claude Code
- Skip the "why" questions
- Rush through decisions

### During the Session

✅ **DO:**
- Ask clarifying questions
- Show real examples
- Be honest about limitations
- Validate understanding frequently
- Take detailed notes

❌ **DON'T:**
- Talk too much (listen more)
- Over-promise capabilities
- Use jargon without explaining
- Make decisions for the client
- Skip budget discussion

### After the Session

✅ **DO:**
- Send VIBE_PLAN.md within 48 hours
- Request explicit approval
- Clarify any open questions
- Set clear next steps

❌ **DON'T:**
- Start work without approval
- Change plan without discussion
- Assume agreement = approval
- Skip documentation

---

**This framework is based on 8 successful .claude repository implementations.**

**Version:** 1.0
**Author:** Greg Black / GB Automation
**Last Updated:** November 2025
