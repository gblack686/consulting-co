# Claude Code Consulting Workflow

> End-to-end process for delivering .claude repository consulting services
> Based on 8+ production implementations

---

## Workflow Overview

```
Discovery → Vibe Planning → Design → Implementation → Testing → Handoff → Support
  (1-2h)      (1-2h)        (2-4h)    (8-16h)        (2-4h)     (2h)      (ongoing)
```

**Total Project Timeline:** 16-30 hours (2-4 weeks)

---

## Phase 1: Discovery (1-2 hours)

### Objectives
- Understand client's project and technical environment
- Identify pain points and automation opportunities
- Assess team's technical capabilities
- Determine budget and timeline constraints

### Discovery Questions

**Project Context:**
- What type of project are you building? (web app, API, data pipeline, ML system, etc.)
- What problem are you solving for your users?
- What stage is the project at? (planning, MVP, production, scaling)
- What's your target launch date or timeline?

**Technical Stack:**
- What programming languages are you using?
- What frameworks and libraries?
- Which cloud provider? (AWS, Azure, GCP, on-prem)
- What database technologies?
- What CI/CD tools are you using?

**Team & Workflow:**
- How large is your development team?
- What's the team's experience level with AI tools?
- How do you currently track tasks? (Jira, ADO, GitHub Issues, Linear, Archon)
- What's your current development workflow?
- Do you use git branching strategies? Which one?

**Pain Points:**
- What takes the most time in your current workflow?
- Where do you see the most errors or rework?
- What repetitive tasks could be automated?
- What documentation is missing or out of date?

**Automation Needs:**
- Do you need time tracking? (billable hours, client reporting)
- Do you need code review automation?
- Do you need test generation?
- Do you need documentation generation?
- Do you need deployment automation?

**Integration Requirements:**
- Do you use Azure DevOps? (time tracking, boards, repos)
- Do you use Archon for task management?
- Do you need Slack/Teams notifications?
- Do you need calendar integration?
- Do you need knowledge graph / memory system?

**Budget & Constraints:**
- What's your budget for this engagement?
- Are there cost constraints for Claude API usage?
- Any compliance or security requirements?
- Any technology restrictions?

### Deliverables
- Discovery notes document
- Initial assessment of feasibility
- Rough effort estimate
- Go/no-go decision

---

## Phase 2: Vibe Planning Session (1-2 hours)

### Objectives
- Deep dive into .claude repository requirements
- Design the primitive system (commands, agents, hooks, skills)
- Identify observability and logging needs
- Create architectural blueprint

### Planning Session Format

**Voice conversation (Zoom/Meet) with screen sharing**

Use the **Vibe Planning Framework** (see VIBE-PLANNING-FRAMEWORK.md) to guide conversation.

### Key Decisions

**1. Permission Strategy**
- What should be the default permission mode? (plan, default, acceptEdits)
- Which tools should be explicitly allowed?
- Which tools should be denied?
- Do different agents need different permissions?

**2. Primitive Selection**

**Commands needed:**
- [ ] Time tracking (`/ado-log-time`, custom billing)
- [ ] Git operations (`/branch-start`, `/commit`, `/branch-cleanup`)
- [ ] Testing (`/test`, `/unit-test`, custom test runners)
- [ ] AWS operations (`/aws-sign-in`, custom AWS commands)
- [ ] Project management (`/generate-prp`, `/execute-prp`)
- [ ] Custom domain commands (specific to their project)

**Agents needed:**
- [ ] Architecture planner (Opus)
- [ ] Database architect (Sonnet)
- [ ] Test generator (Sonnet)
- [ ] Test runner (Haiku)
- [ ] Documentation generator (Sonnet)
- [ ] Scoping agent (Sonnet)
- [ ] Domain-specific agents (custom)

**Hooks needed:**
- [ ] SessionStart (load context)
- [ ] SessionEnd (cleanup)
- [ ] Stop (notifications, logging)
- [ ] PreToolUse (logging, validation)
- [ ] PostToolUse (logging, metrics)
- [ ] SubagentStop (multi-agent tracking)

**Skills needed:**
- [ ] AWS CDK diagram generation
- [ ] QA hardening workflows
- [ ] Client handoff materials
- [ ] Custom workflow skills

**3. Observability Level**

**Minimal:**
- Hook-based logging to files
- Simple work-status.md tracking

**Standard:**
- Hook-based logging
- work-status.md + feature tracking
- Basic ADO/Archon integration

**Advanced:**
- Full hook suite (9 events)
- Graphiti knowledge graph (Neo4j)
- Real-time dashboard (Vue + Bun)
- OpenTelemetry export
- Langfuse LLM tracing
- ADO/Archon full integration

**4. Integration Patterns**

**Azure DevOps:**
- Time tracking with weekly targets?
- Board snapshot automation?
- Calendar sync for meetings?
- Work item hierarchy (parent/child)?

**Archon MCP:**
- Use as primary task manager?
- RAG code example search?
- Cross-project task tracking?
- Override TodoWrite?

**Knowledge Graph (Graphiti):**
- Persistent memory across sessions?
- Temporal knowledge tracking?
- Semantic search for past context?
- Entity relationship mapping?

**Cloud Services:**
- AWS Parameter Store for secrets?
- CloudWatch for activity logging?
- S3 for artifacts?
- Bedrock for additional models?

**5. Model Strategy**

**Budget-conscious:**
- Default: Haiku for most tasks
- Specialized: Sonnet for complex reasoning
- Rare: Opus only for critical architecture

**Balanced:**
- Default: Sonnet for development
- Specialized: Opus for architecture
- Fast execution: Haiku for testing/docs

**Performance-focused:**
- Default: Sonnet
- Complex: Opus
- Everything else: Sonnet

### Deliverables
- VIBE_PLAN.md document with:
  - Agreed-upon primitives (commands, agents, hooks, skills)
  - Observability architecture
  - Integration specifications
  - Model selection strategy
  - Cost estimates
  - Timeline

---

## Phase 3: Design (2-4 hours)

### Objectives
- Create detailed .claude repository structure
- Write configuration specifications
- Design custom commands and agents
- Plan hook automation flows

### Design Activities

**1. Directory Structure Design**

Create folder structure document:
```
.claude/
├── settings.json
├── settings.local.json.template
├── agents/
│   ├── [agent-1].md
│   └── [agent-2].md
├── commands/
│   ├── [command-1].md
│   └── [command-2].md
├── hooks/
│   ├── [hook-1].py
│   └── [hook-2].py
├── skills/
├── [project-specific-dirs]/
└── docs/
    └── CLAUDE.md
```

**2. settings.json Specification**

Draft complete settings.json with:
- Environment variables
- Permission configuration
- Model selection
- MCP server configs
- Hook configurations
- Team-shared settings

**3. Agent Specifications**

For each agent, create spec document:
```markdown
# Agent: [Name]

**Model:** sonnet/opus/haiku
**Purpose:** [What this agent does]
**Triggers:** [When to use this agent]

## Permissions
- Allow: [tools]
- Deny: [tools]

## System Prompt
[Detailed prompt design]

## Examples
[Usage examples]
```

**4. Command Specifications**

For each command, create spec:
```markdown
# Command: /[name]

**Arguments:**
- arg1 (required): [description]
- arg2 (optional): [description]

## Behavior
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Implementation Notes
[Technical details]
```

**5. Hook Flow Diagrams**

Create flow diagrams for hook automation:
```
SessionStart
  ↓
Load git status → Load recent issues → Prime context
  ↓
Ready for work

Stop
  ↓
Log to Graphiti → Send TTS notification → Update work-status.md
  ↓
Session complete
```

**6. Integration Specifications**

Detail each integration:
- API endpoints
- Authentication methods
- Data formats
- Error handling
- Rate limiting considerations

### Deliverables
- Detailed .claude structure document
- settings.json specification
- Agent specifications (one per agent)
- Command specifications (one per command)
- Hook flow diagrams
- Integration specifications
- Cost and timeline estimates

---

## Phase 4: Implementation (8-16 hours)

### Objectives
- Build the .claude repository
- Implement all primitives
- Configure integrations
- Test all components

### Implementation Steps

**1. Repository Setup (1 hour)**

```bash
# Create repository structure
mkdir -p .claude/{agents,commands,hooks,skills,docs,ado,logging-service}

# Create base configuration files
touch .claude/settings.json
touch .claude/settings.local.json.template
touch .claude/visual-identity.json
touch .claude/PROJECT_CONFIG.txt
touch .claude/docs/CLAUDE.md

# Create .gitignore
echo "settings.local.json" >> .claude/.gitignore
```

**2. Configuration Implementation (2 hours)**

**settings.json:**
- Environment variables
- Permission configuration
- MCP servers
- Hook configurations

**settings.local.json.template:**
- Template with placeholders
- Documentation comments
- Instructions for team members

**visual-identity.json:**
- Project name
- Brand colors
- Icon/emoji
- Terminal theme

**3. Agent Implementation (2-4 hours)**

For each agent:
1. Create `.claude/agents/[agent-name].md`
2. Write YAML frontmatter (name, model, permissions)
3. Write detailed system prompt
4. Add usage examples
5. Test agent invocation

**4. Command Implementation (2-4 hours)**

For each command:
1. Create `.claude/commands/[command-name].md`
2. Write YAML frontmatter (name, args, description)
3. Write command instructions
4. Add validation logic
5. Test command execution

**5. Hook Implementation (2-4 hours)**

For each hook:
1. Create `.claude/hooks/[hook-name].py`
2. Implement hook logic
3. Add error handling
4. Test hook execution
5. Configure in settings.json

**6. Integration Implementation (2-4 hours)**

**ADO Integration:**
- Configure connection strings
- Implement time logging scripts
- Set up board snapshot automation
- Test ADO API calls

**Archon Integration:**
- Configure MCP server
- Test task management
- Test RAG code search
- Validate archon_rules.md

**Graphiti Integration:**
- Set up Neo4j database
- Configure knowledge graph
- Implement logging scripts
- Test memory retrieval

**7. Observability Setup (1-2 hours)**

If advanced observability:
- Set up real-time dashboard
- Configure backend (Bun + SQLite)
- Set up frontend (Vue)
- Test event streaming
- Configure OpenTelemetry
- Set up Langfuse

**8. Documentation (1-2 hours)**

Create documentation:
- CLAUDE.md (quick reference)
- README.md (setup instructions)
- VIBE_PLAN.md (architectural decisions)
- Command documentation
- Agent documentation
- Hook documentation
- Integration guides

### Deliverables
- Complete .claude repository
- All primitives implemented and tested
- Integrations configured
- Documentation complete
- Working demo

---

## Phase 5: Testing (2-4 hours)

### Objectives
- Validate all commands work
- Test all agents
- Verify hooks execute correctly
- Validate integrations
- Performance testing

### Testing Checklist

**Command Testing:**
- [ ] All commands appear in `/` autocomplete
- [ ] Required arguments validated
- [ ] Optional arguments work with defaults
- [ ] Error handling works correctly
- [ ] Commands produce expected outputs

**Agent Testing:**
- [ ] All agents appear in `@` autocomplete
- [ ] Agents use correct models
- [ ] Permission overrides work
- [ ] Agents produce quality outputs
- [ ] Agent specialization is effective

**Hook Testing:**
- [ ] SessionStart executes on startup
- [ ] Stop executes when pressing stop button
- [ ] PreToolUse/PostToolUse capture events
- [ ] Hooks complete within timeout
- [ ] Hook output is logged correctly

**Integration Testing:**
- [ ] ADO time logging works
- [ ] Archon task management works
- [ ] Graphiti knowledge graph stores data
- [ ] MCP servers connect successfully
- [ ] AWS services authenticate correctly

**Permission Testing:**
- [ ] Default mode behaves correctly
- [ ] Allow list works
- [ ] Deny list blocks correctly
- [ ] Agent permission overrides work

**Performance Testing:**
- [ ] Session starts in < 5 seconds
- [ ] Commands respond quickly
- [ ] Hooks don't cause delays
- [ ] No memory leaks in long sessions

### Deliverables
- Test results document
- Bug list and fixes
- Performance metrics
- Validated .claude repository

---

## Phase 6: Handoff (2 hours)

### Objectives
- Transfer knowledge to client team
- Provide comprehensive documentation
- Train team on usage
- Establish support process

### Handoff Deliverables

**1. Documentation Package**

- **CLAUDE.md** - Quick reference guide
- **VIBE_PLAN.md** - Architectural decisions and rationale
- **README.md** - Setup and installation instructions
- **TROUBLESHOOTING.md** - Common issues and solutions
- **CHANGELOG.md** - Version history and updates

**2. Configuration Templates**

- **settings.local.json.template** - For new team members
- **PROJECT_CONFIG.txt.template** - Project variables
- **.env.template** - Environment variables

**3. Training Session (1-2 hours)**

**Agenda:**
- Overview of .claude repository structure
- Walkthrough of settings.json
- Demo of all commands
- Demo of all agents
- Explanation of hooks
- Integration overview
- Q&A

**Format:** Screen share + hands-on

**4. Video Recordings**

Record:
- Setup walkthrough (5-10 min)
- Command demos (10-15 min)
- Agent usage examples (10-15 min)
- Common workflows (15-20 min)

**5. Support Documentation**

- **Support channels** (Slack, email, etc.)
- **Response SLA** (24-48 hours)
- **Escalation process**
- **Update/maintenance schedule**

**6. Handoff Checklist**

- [ ] All documentation delivered
- [ ] Repository pushed to client's GitHub/GitLab
- [ ] Team members have access
- [ ] Training session completed
- [ ] Video recordings shared
- [ ] Support process established
- [ ] Invoice sent
- [ ] Feedback collected

### Deliverables
- Complete documentation package
- Trained client team
- Video recordings
- Support agreement
- Signed handoff acceptance

---

## Phase 7: Support (Ongoing)

### Support Tiers

**Tier 1: Basic Support** (Included in project)
- **Duration:** 30 days post-handoff
- **Scope:** Bug fixes, clarification questions
- **Response time:** 24-48 hours
- **Channel:** Email

**Tier 2: Extended Support** (Monthly retainer)
- **Duration:** 3-12 months
- **Scope:** Updates, new commands/agents, optimization
- **Response time:** 24 hours
- **Channel:** Slack + email

**Tier 3: Premium Support** (Hourly)
- **Duration:** As needed
- **Scope:** Custom development, consulting
- **Response time:** Same day
- **Channel:** Slack + video calls

### Common Support Activities

**Bug Fixes:**
- Hook not executing
- Command errors
- Integration failures
- Permission issues

**Updates:**
- New commands
- New agents
- New integrations
- Configuration changes

**Optimization:**
- Performance improvements
- Cost reduction
- Workflow enhancements
- Best practices updates

**Training:**
- New team member onboarding
- Advanced usage sessions
- Custom workflow training

---

## Pricing Models

### Fixed Price Packages

**Starter Package** - $5,000
- Discovery + Vibe Planning
- Minimal .claude setup (5-10 commands, 3-5 agents)
- Basic hooks (SessionStart, Stop)
- Documentation
- 1-hour training
- 30-day support

**Professional Package** - $12,000
- Discovery + Vibe Planning
- Standard .claude setup (15-20 commands, 6-8 agents)
- Full hook suite
- Standard observability
- ADO or Archon integration
- Comprehensive documentation
- 2-hour training
- 30-day support

**Enterprise Package** - $25,000
- Discovery + Vibe Planning
- Advanced .claude setup (25+ commands, 10+ agents)
- Full hook suite
- Advanced observability (Graphiti + Dashboard)
- Multiple integrations (ADO, Archon, AWS, etc.)
- Custom skills and workflows
- Comprehensive documentation
- 4-hour training
- 60-day support

### Hourly Consulting
- **Rate:** $200-300/hour
- **Minimum:** 10 hours
- **Best for:** Custom requirements, ongoing development

### Retainer
- **Monthly:** $2,500-5,000
- **Includes:** 10-20 hours/month support and development
- **Best for:** Continuous improvement and support

---

## Success Metrics

### Client Success Indicators

**Adoption:**
- 80%+ of team using .claude repository daily
- 10+ commands used per week
- 5+ agent invocations per week

**Efficiency:**
- 20-30% reduction in development time
- 40-50% reduction in repetitive tasks
- 50%+ reduction in context switching

**Quality:**
- 30-40% fewer bugs
- 50%+ test coverage improvement
- Better documentation consistency

**Satisfaction:**
- 8+ NPS score
- Positive testimonial
- Referrals to other teams

### Consultant Success Indicators

**Delivery:**
- On-time delivery
- Within budget
- No critical bugs

**Client Relationship:**
- Smooth handoff
- Positive feedback
- Future engagement potential

**Portfolio:**
- Reusable components created
- Case study material
- Reference client

---

## Templates & Tools

### Project Tracking Template

```markdown
# Project: [Client Name] .claude Repository

## Timeline
- Discovery: [Date]
- Vibe Planning: [Date]
- Design: [Date]
- Implementation: [Date]
- Testing: [Date]
- Handoff: [Date]

## Budget
- Quoted: $[Amount]
- Actual: $[Amount]
- Hours: [Estimated] / [Actual]

## Status
- [ ] Discovery complete
- [ ] Vibe plan approved
- [ ] Design approved
- [ ] Implementation complete
- [ ] Testing complete
- [ ] Handoff complete

## Deliverables
- [ ] .claude repository
- [ ] Documentation
- [ ] Training
- [ ] Support setup

## Notes
[Project notes]
```

### Client Feedback Template

```markdown
# Client Feedback: [Client Name]

**Date:** [Date]
**Project:** [Project Name]

## What went well?
[Feedback]

## What could be improved?
[Feedback]

## Would you recommend our services?
[ ] Yes [ ] No

**Why?**
[Feedback]

## NPS Score (0-10)
[Score]

## Testimonial (optional)
[Testimonial]
```

---

## Next Steps After This Workflow

1. Review and customize this workflow for your business
2. Create the Vibe Planning Framework (detailed question set)
3. Build .claude boilerplate templates (Starter, Pro, Enterprise)
4. Set up your own consulting .claude repository
5. Create marketing materials (case studies, demos)
6. Launch your consulting service!

---

**This workflow is based on 8 production .claude implementations and consulting best practices.**

**Version:** 1.0
**Author:** Greg Black / GB Automation
**Last Updated:** November 2025
