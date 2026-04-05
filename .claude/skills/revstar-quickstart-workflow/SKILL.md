---
name: revstar-quickstart-workflow
description: Guide users through creating comprehensive AI developer workflows for RevStar QuickStart projects. This skill helps plan end-to-end workflows from discovery to deployment, identifying primitives (skills, commands, agents), mapping human-in-the-loop checkpoints, and designing conditional logic. Use when users want to build Claude Code workflows for AWS-based QuickStart projects, agent coordination strategies, or systematic development processes with multiple stages, agents, and validation checkpoints.
---

# RevStar QuickStart Workflow Builder

## Overview

Create comprehensive AI developer workflows for RevStar QuickStart projects. This skill guides users through systematic workflow design, from initial discovery to client handoff, helping identify the right Claude Code primitives (skills, slash commands, agents, MCP tools) and establish human-in-the-loop validation checkpoints.

## When to Use This Skill

Use this skill when:
- Planning a new RevStar QuickStart project workflow
- Designing agent coordination strategies (sequential, parallel, conditional)
- Structuring multi-stage development processes
- Identifying which Claude Code features to use for specific tasks
- Creating workflows that require human validation checkpoints
- Mapping out end-to-end development cycles from discovery to deployment
- User mentions "workflow", "QuickStart", "agent coordination", or "development process"

## Building with Command Primitives

This workflow is built on **110+ slash command primitives** that form the foundation of all RevStar QuickStart operations. Commands are the fundamental unit—master them first, then compose them into skills and agents.

Reference `references/command-primitives.md` for the complete command catalog organized by workflow stage. Commands range from cross-cutting operations (`/commit-changes`, `/update-archon-task`) to stage-specific operations (`/create-data-model`, `/run-e2e-tests`).

**Command-First Approach**:
1. Start with atomic commands for single operations
2. Compose commands into workflows for complex processes
3. Package related commands into skills for reusability
4. Use sub-agents when parallelization is needed

**Implementation Roadmap**:
- Phase 1 (20 commands): Discovery → Scoping
- Phase 2 (20 commands): Planning → Development
- Phase 3 (21 commands): Testing → QA
- Phase 4 (23 commands): Handoff → CI/CD → Advanced

## Workflow Design Process

### Step 1: Understand the End-to-End Cycle

Start by understanding the complete project lifecycle:

1. **Ask Discovery Questions**:
   - What is the project goal and business context?
   - What are the key deliverables (features, architecture, documentation)?
   - What is the timeline and team structure?
   - Are there existing materials (Fathom transcripts, Miro boards, HubSpot deals)?
   - What level of client involvement is expected?

2. **Identify Major Stages**:
   Reference `references/workflow-stages.md` for the standard 8 stages:
   - Discovery & Requirements
   - Scoping & Architecture
   - Planning & PRD
   - Development & Implementation
   - Testing & Validation
   - QA Hardening & Documentation
   - Client Handoff
   - CI/CD & Monitoring

3. **Map Dependencies**:
   - Which stages must be sequential?
   - Which can run in parallel?
   - What are the conditional branches?

### Step 2: Identify Primitives and Tools

For each stage, determine the appropriate Claude Code features:

#### Choosing Between Skills, Commands, Agents, and MCPs

Reference the decision tree from `agent-skills-guide.md`:

**Use Custom Slash Commands when**:
- Single, focused operation
- Manual trigger preferred
- Direct control needed
- Examples: `/create-architecture`, `/generate-cdk-yaml`

**Use Skills when**:
- Multiple related operations
- Agent should autonomously invoke
- Reusable workflow package
- Examples: Document processing, code review, testing suite

**Use Sub-Agents when**:
- Parallel execution needed
- Isolated context acceptable
- Scalable workflows
- Examples: Multiple feature development, parallel testing

**Use MCP Tools when**:
- External service integration
- Third-party APIs
- Data retrieval from external sources
- Examples: Archon task manager, AWS documentation, Playwright testing

#### Standard MCP Tools for RevStar Projects

- **Archon MCP**: Task and project management
- **AWS Documentation MCP**: Service reference and best practices
- **Ref Documentation MCP**: Code patterns and examples
- **Playwright MCP**: Frontend testing and validation
- **AWS CloudWatch MCP**: Monitoring and logging
- **AWS Diagram Server MCP**: Architecture visualization

### Step 3: Design Agent Patterns

Reference `references/agent-patterns.md` for detailed agent definitions.

#### Standard Agents for QuickStart Projects

1. **Discovery Agent**: Requirements gathering
2. **Scoping Agent**: Architecture and design
3. **Planning Agent**: PRD and task breakdown
4. **Developer Agent(s)**: Feature implementation
5. **UI Reviewer Agent**: Frontend validation
6. **Testing Agent**: Comprehensive testing
7. **Documentation Agent**: Technical documentation

#### Coordination Strategies

**Sequential**: Use for dependent stages
```
Discovery Agent → Scoping Agent → Planning Agent → Developer Agent
```

**Parallel**: Use for independent features (requires sub-agents)
```
        ┌─ Developer Agent 1 (Auth)
Main ───┼─ Developer Agent 2 (API)
        └─ Developer Agent 3 (Frontend)
```

**Conditional**: Use for decision-based flows
```
Testing Agent → Tests Pass? → Deployment Agent
                           └─ Tests Fail → Debug Agent
```

### Step 4: Establish Human-in-the-Loop Checkpoints

Identify critical validation points where human review is required:

**Critical Checkpoints** (Always require human approval):
- Architecture design approval
- Cost estimate sign-off
- Security review
- Production deployment
- Client handoff

**High Priority Checkpoints** (Recommended):
- Feature demonstrations
- Test result reviews
- Documentation completeness
- Performance validation

**Optional Checkpoints**:
- Code review for non-critical features
- Minor configuration changes

### Step 5: Create Output Documents

Generate structured workflow documentation using the asset templates:

#### Data Model (use `assets/data-model-template.yaml`)

Define:
- DynamoDB tables with access patterns
- S3 buckets with lifecycle policies
- Data relationships
- Sample data structures

#### AWS Services Architecture (use `assets/aws-services-template.yaml`)

Specify:
- Lambda functions with triggers
- API Gateway routes
- Cognito authentication
- Storage services
- Monitoring and alarms
- Cost estimates

#### UI Specifications (use `assets/ui-spec-template.yaml`)

Document:
- Page structures and routes
- Components library
- User flows with complete journeys
- Sample data for development
- Responsive design requirements
- Accessibility standards

#### Success Criteria (use `assets/success-criteria-template.yaml`)

Establish:
- Business success metrics
- Technical validation criteria
- Feature-specific tests
- Performance benchmarks
- Deployment checklist
- QA hardening checklist

### Step 6: Implementation Plan

Create a detailed implementation plan that includes:

1. **Task Breakdown**:
   - Use Archon MCP to create project and tasks
   - Break features into granular implementation steps
   - Assign priorities and dependencies

2. **Agent Assignments**:
   - Map which agents handle which tasks
   - Define input/output contracts
   - Establish coordination mechanisms

3. **Validation Steps**:
   - Unit tests for each feature
   - Integration tests for services
   - E2E tests for user flows
   - Performance benchmarks

4. **Timeline**:
   - 4-week sprint structure typical
   - Buffer for testing and iteration
   - Client feedback cycles

## Interactive Workflow Planning

When guiding users through workflow creation, use this conversational flow:

### Initial Assessment

Ask:
1. "What is the main goal of your QuickStart project?"
2. "Do you have existing materials like Fathom transcripts or Miro boards?"
3. "What is your timeline and team structure?"
4. "What level of client involvement is expected?"

### Stage-by-Stage Planning

For each stage:
1. Present the stage purpose and typical activities (from `references/workflow-stages.md`)
2. Ask: "What are the specific inputs for this stage?"
3. Ask: "What outputs do you need to produce?"
4. Identify: "Which agents or tools are best suited for these activities?"
5. Determine: "Are there human validation checkpoints needed?"

### Feature Deep Dive

For complex features (especially frontend):
1. "Let's list all features and sub-features"
2. "For each feature, describe the complete user journey"
3. "What happens after each user action? Where do they navigate?"
4. "Are there dependencies or backlinks between features?"
5. "What data needs to be collected and where should it be stored?"

Example deep dive questions for a document upload feature:
- "When a document is uploaded, where does it appear?"
- "Can users see it in multiple places (dashboard, settings)?"
- "How can users delete the document? From which pages?"
- "After deletion, does it disappear from all locations?"
- "What notifications or feedback does the user receive?"

### Conditional Logic and Error Handling

Ask about edge cases:
- "What happens if a test fails?"
- "How do we handle API errors?"
- "What if deployment fails?"
- "How do we rollback changes?"

## Best Practices from RevStar Experience

Reference `references/revstar-conventions.md` for detailed standards.

### Frontend Development

1. **Comprehensive Feature Lists**: Document every button, page, and interaction
2. **Sub-dependencies**: Break features into atomic tasks
3. **Complete User Journeys**: Map data flow through entire application
4. **Mobile Testing**: Validate layouts and prevent overlapping buttons
5. **Test-Driven Development**: Write tests before implementation

### Data Architecture

1. **Comprehensive Schemas**: Collect all data upfront in DynamoDB
2. **Reduce Lambda Calls**: Optimize table structure to minimize lookups
3. **Avoid Table Joins**: Design denormalized schemas when appropriate
4. **Single-Table Design**: Use DynamoDB best practices

### Code Quality

1. **Linting**: Run before every commit
2. **Unit Tests**: 80%+ coverage target
3. **Integration Tests**: Validate service interactions
4. **E2E Tests**: Cover all user workflows
5. **Security**: OWASP Top 10 validation

### Agent Workflow

1. **Git Worktrees**: Use for parallel feature development
2. **Progressive Disclosure**: Load documentation only when needed
3. **Context Management**: Keep prompts focused (2-5 keywords for RAG)
4. **ADO Integration**: Log time to Azure DevOps
5. **Archon Tasks**: Track all work in Archon

## Example Workflow Output

When complete, produce a structured workflow document like:

```markdown
# QuickStart Workflow: [Project Name]

## Project Overview
- Goal: [Business objective]
- Timeline: 4 weeks
- Team: [Structure]

## Stage 1: Discovery
- **Agent**: Discovery Agent
- **Inputs**: HubSpot deal, initial discussions
- **Outputs**: Requirements document
- **Tools**: Brave Search MCP
- **Human Checkpoint**: ✓ Requirements validated

## Stage 2: Scoping
- **Agent**: Scoping Agent
- **Inputs**: Fathom transcripts, requirements
- **Outputs**:
  - Data model YAML
  - AWS services YAML
  - UI specification YAML
  - Architecture diagram
  - Cost estimate
- **Tools**: AWS Documentation MCP, AWS Diagram Server MCP
- **Human Checkpoint**: ✓ Architecture approved, ✓ Cost approved

## Stage 3: Planning
- **Agent**: Planning Agent
- **Inputs**: Scoping outputs
- **Outputs**:
  - Planning.md (PRD)
  - Agile stories
  - CDK construct YAML
  - Success criteria YAML
- **Tools**: Archon MCP, AWS Documentation MCP
- **Human Checkpoint**: ✓ PRD reviewed

## Stage 4: Development
- **Coordination**: Parallel (Sub-agents)
- **Agents**:
  - Developer Agent 1: Authentication module
  - Developer Agent 2: Document processing
  - Developer Agent 3: Frontend UI
- **Tools**: Ref MCP, AWS Documentation MCP, Archon MCP
- **Validation**: Unit tests, integration tests
- **Human Checkpoint**: ✓ Feature demos, ✓ Security review

## Stage 5: Testing
- **Agent**: Testing Agent + UI Reviewer Agent
- **Activities**: E2E tests with Playwright, mobile testing
- **Tools**: Playwright MCP, Chrome DevTools MCP
- **Human Checkpoint**: ✓ Test results reviewed

## Stage 6: QA Hardening
- **Agent**: Documentation Agent
- **Outputs**: README, API docs, deployment guide
- **Validation**: CDK diff check, package compilation
- **Human Checkpoint**: ✓ Documentation complete

## Stage 7: Handoff
- **Outputs**:
  - Handoff presentation
  - Video walkthrough
  - Access checklist
- **Human Checkpoint**: ✓ Client sign-off

## Stage 8: CI/CD
- **Setup**: GitHub Actions, CloudWatch monitoring
- **Monitoring**: Cost alerts, performance metrics
```

## Progressive Disclosure Reminders

**Always remember**:
- Load reference files only when needed for specific guidance
- Use asset templates as starting points, customize for each project
- Keep RAG queries short (2-5 keywords)
- Reference detailed docs rather than duplicating content

## Troubleshooting Common Workflow Issues

**Issue**: "I don't know which primitive to use"
→ Start with slash commands, upgrade to skills only when composing multiple operations. See `references/command-primitives.md` for the complete catalog.

**Issue**: "Which commands do I need for [stage]?"
→ Reference `references/command-primitives.md` organized by the 8 workflow stages with implementation priorities.

**Issue**: "My agents keep failing"
→ Check for proper input validation and clear output contracts

**Issue**: "Context window is overwhelming"
→ Use progressive disclosure, load docs only when needed

**Issue**: "Parallel execution not working"
→ Must use sub-agents explicitly for parallel tasks

**Issue**: "Costs are running high"
→ Reference cost optimization in `references/revstar-conventions.md`

**Issue**: "How do I implement these commands?"
→ Follow the 4-phase implementation roadmap in `references/command-primitives.md` (20-23 commands per phase)

## Next Steps After Workflow Design

1. **Initialize Project**: Create Archon project and tasks
2. **Set Up Repository**: Initialize git with proper structure
3. **Configure MCP Servers**: Add to `.claude/mcp.json`
4. **Create Slash Commands**: Build primitive commands first
5. **Build Skills**: Package related commands into skills
6. **Define Agents**: Configure sub-agents for parallel work
7. **Run Workflow**: Execute stage by stage with checkpoints

---

**Remember**: Workflows are iterative. Start simple, validate each stage, then expand. The goal is systematic, repeatable processes that produce consistent, high-quality results.
