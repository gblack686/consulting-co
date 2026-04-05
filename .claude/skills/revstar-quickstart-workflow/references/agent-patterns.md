# RevStar Agent Patterns & Coordination

## Agent Types

### Discovery Agent

**Purpose**: Gather initial requirements and validate project scope.

**Inputs**:
- HubSpot Deal information
- Client meeting notes
- Preliminary discussions

**Outputs**:
- Structured questionnaire responses
- Scoping agent input document

**MCP Tools**:
- Brave Search (market research, competitor analysis)

**Triggers**:
- New QuickStart project initialization
- "discovery" or "requirements gathering" mentioned
- HubSpot deal reference provided

---

### Scoping Agent

**Purpose**: Transform requirements into technical specifications and architecture.

**Inputs**:
- Fathom transcripts
- POC specifications (if available)
- Miro boards (if available)
- Discovery agent outputs

**Outputs**:
- Data models (YAML)
- AWS services architecture (YAML)
- UI specifications with sample data (YAML)
- Architecture diagram (Mermaid)
- Cost estimate

**MCP Tools**:
- Brave Search (AWS patterns, best practices)
- Exa Search (ML publications for AI features)
- AWS Documentation (service specs)
- AWS Diagram Server (visualization)

**Triggers**:
- Discovery phase complete
- Architecture design needed
- "scope" or "design" mentioned
- Fathom transcript provided

---

### Planning Agent

**Purpose**: Create detailed implementation plan with agile stories and CDK constructs.

**Inputs**:
- Scoping outputs (data models, architecture, UI specs)
- Timeline constraints
- Resource availability

**Outputs**:
- Planning.md (PRD)
- Agile stories/boards (4-week sprint)
- CDK construct YAML
- Hello World E2E tests
- Success criteria YAML
- Frontend user stories YAML

**MCP Tools**:
- AWS Documentation (CDK patterns)
- Archon Task Manager (task creation)
- Ref Documentation Retriever

**Triggers**:
- Scoping approved
- "planning" or "PRD" mentioned
- Implementation plan needed

---

### Developer Agent

**Purpose**: Implement features with tests and documentation.

**Instructions**:
- Follow RevStar naming conventions
- Apply CDK best practices
- Implement test-driven development
- Document all APIs and modules
- Use progressive disclosure for context

**Activities**:
- Build features according to stories
- Write unit tests
- Create integration tests
- Run linters
- Document code
- Commit with conventions
- Push to GitHub

**MCP Tools**:
- AWS Documentation (API references)
- Ref Documentation Retriever (patterns)
- Archon Task Manager (status updates)

**Triggers**:
- Feature story assigned
- "implement" or "build" mentioned
- Development phase active

---

### UI Reviewer Agent

**Purpose**: Validate frontend functionality and user workflows.

**Instructions**:
- Test all user workflows
- Verify mobile responsiveness
- Check button layouts and overlapping
- Validate data flow
- Record test sessions

**Activities**:
- Execute E2E tests
- Verify UI/UX flows
- Test mobile layouts
- Create test recordings
- Report issues

**MCP Tools**:
- Playwright (browser automation)
- Chrome DevTools (debugging)

**Triggers**:
- Frontend features complete
- "test UI" or "validate frontend" mentioned
- E2E testing phase

---

### Testing Agent

**Purpose**: Comprehensive testing across all layers.

**Activities**:
- Run unit tests
- Execute integration tests
- Perform E2E tests
- Validate with real data
- Security testing (OWASP)
- Performance testing

**MCP Tools**:
- Playwright (E2E tests)
- AWS CloudWatch (monitoring)
- Chrome DevTools (frontend)

**Triggers**:
- Development phase complete
- "test" or "validate" mentioned
- QA phase active

---

### Documentation Agent

**Purpose**: Create comprehensive documentation.

**Activities**:
- Write README files
- Document APIs
- Create architecture docs
- Write troubleshooting guides
- Prepare handoff materials

**Triggers**:
- Feature complete
- "document" mentioned
- Handoff phase

---

## Administrative Agents

### ADO Agent

**Purpose**: Manage Azure DevOps tasks and time tracking.

**Activities**:
- Create work items
- Update task status
- Log time entries
- Generate reports

**MCP Tools**:
- ADO MCP Server (when available)
- Archon Task Manager

---

### Git Agent

**Purpose**: Manage git operations and workflows.

**Activities**:
- Create worktrees
- Manage branches
- Handle commits
- Review code
- Merge operations

**Triggers**:
- Parallel development needed
- Git operations required
- Code review requested

---

### Archon Agent

**Purpose**: Project and task management integration.

**Activities**:
- Create projects
- Manage tasks
- Track progress
- Update status
- Generate reports

**MCP Tools**:
- Archon Task Manager (all operations)

---

## Agent Coordination Strategies

### Sequential Coordination

**When to Use**:
- Features with dependencies
- Ordered deployment steps
- Pipeline stages

**Pattern**:
```
Agent A → Agent B → Agent C
```

**Example**:
1. Scoping Agent → outputs architecture
2. Planning Agent → creates implementation plan
3. Developer Agent → builds features
4. Testing Agent → validates functionality

---

### Parallel Coordination

**When to Use**:
- Independent features
- Multiple worktrees
- Scalable workflows

**Pattern**:
```
        ┌─ Agent A
Main ───┼─ Agent B
        └─ Agent C
```

**Example**:
- Developer Agent 1 → Authentication module
- Developer Agent 2 → API endpoints
- Developer Agent 3 → Frontend components

**Note**: Use sub-agents for true parallel execution.

---

### Conditional Coordination

**When to Use**:
- Decision-based workflows
- Test-dependent deployment
- Error handling

**Pattern**:
```
Agent A → Decision → Agent B (success)
                 └→ Agent C (failure)
```

**Example**:
1. Testing Agent runs tests
2. If tests pass → Deployment Agent
3. If tests fail → Debug Agent

---

## Best Practices

### Context Management

1. **Progressive Disclosure**: Load documentation only when needed
2. **Efficient Prompts**: Use 2-5 keyword queries for RAG search
3. **Focused Agents**: Each agent handles specific responsibilities
4. **Context Preservation**: Main conversation retains critical context

### Task Tracking

1. **Archon Integration**: All tasks logged in Archon
2. **Status Updates**: Real-time progress tracking
3. **ADO Sync**: Time logging to Azure DevOps
4. **Work Status Logs**: Maintain work-status.md in .claude directory

### Code Quality

1. **Test-Driven Development**: Write tests first
2. **Linting**: Run linters before commit
3. **Code Review**: Use GitHub code review or Code Rabbit
4. **Security**: OWASP top 10 validation
5. **Performance**: Monitoring and optimization

### Frontend Development

1. **Feature Lists**: Comprehensive feature documentation
2. **Sub-dependencies**: Break features into smaller tasks
3. **Data Flow**: Map complete user journeys
4. **Mobile Testing**: Validate responsive layouts
5. **Next.js Practices**: Follow framework best practices

### Data Architecture

1. **Comprehensive Schema**: Collect all data points upfront
2. **Reduce Lambda Calls**: Optimize data structure
3. **Avoid Table Joins**: Design denormalized schemas when appropriate
4. **DynamoDB Best Practices**: Single-table design patterns

### Agent Communication

1. **Clear Outputs**: Structured YAML/JSON outputs
2. **Validation**: Verify inputs before processing
3. **Error Handling**: Graceful failure with reporting
4. **Documentation**: Document all agent interactions
