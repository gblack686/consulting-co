# RevStar QuickStart Command Primitives

This document defines all slash command primitives needed for the complete RevStar QuickStart workflow. Commands are the fundamental building blocks that compose into skills, workflows, and agent coordination strategies.

**Total Commands**: 110+

## Philosophy: Start with Commands, Build Up

Following the principle from `agent-skills-guide.md`:

> **"The prompt is the fundamental unit of knowledge work and of programming."**

Commands are the closest to bare metal (agent + LLM). Always start with commands, then compose them into:
- **Skills** (when multiple related commands form a reusable package)
- **Sub-agents** (when parallelization is needed)
- **Workflows** (when orchestrating multiple stages)

---

## CROSS-CUTTING COMMANDS (All Stages)

### /log-time-ado
**Purpose**: Log time to Azure DevOps work item
**Inputs**: Hours worked, work item ID, activity description
**Outputs**: ADO time entry confirmation
**Stage**: All stages
**MCP Tools**: ADO MCP Server (when available), Archon Task Manager
**Type**: Atomic
**Notes**: Call after completing any significant work

### /update-archon-task
**Purpose**: Update task status in Archon project management
**Inputs**: Task ID, new status (todo/doing/review/done), optional notes
**Outputs**: Updated task record
**Stage**: All stages
**MCP Tools**: Archon Task Manager (manage_task)
**Type**: Atomic

### /commit-changes
**Purpose**: Commit changes with proper RevStar conventions
**Inputs**: Files to commit, commit message (type: description format)
**Outputs**: Git commit hash, confirmation
**Stage**: All stages
**Type**: Atomic
**Conventions**: feat:, fix:, docs:, refactor:, test:, chore:

### /create-git-branch
**Purpose**: Create feature branch with proper naming
**Inputs**: Branch type (feature/fix/refactor/docs/test), description
**Outputs**: New branch name, checkout confirmation
**Stage**: All stages
**Type**: Atomic
**Pattern**: `{type}/{description}`

### /search-aws-docs
**Purpose**: Search AWS documentation for service information
**Inputs**: Search query (2-5 keywords)
**Outputs**: Relevant AWS documentation snippets
**Stage**: All stages
**MCP Tools**: AWS Documentation MCP (search_documentation, read_documentation)
**Type**: Atomic

### /search-code-patterns
**Purpose**: Find code examples and patterns
**Inputs**: Technology/pattern query (2-5 keywords)
**Outputs**: Code examples from RAG knowledge base
**Stage**: All stages
**MCP Tools**: Ref Documentation MCP, Archon RAG (rag_search_code_examples)
**Type**: Atomic

### /update-work-status
**Purpose**: Update work status log in .claude directory
**Inputs**: Status update text, current task
**Outputs**: Updated work-status.md file
**Stage**: All stages
**Type**: Atomic
**Location**: `.claude/work-status.md`

### /setup-git-worktree
**Purpose**: Create git worktree for parallel development
**Inputs**: Feature name, base branch
**Outputs**: Worktree path, branch created
**Stage**: All stages (primarily Development)
**Type**: Atomic
**Use Case**: Parallel feature development

---

## STAGE 1: DISCOVERY & REQUIREMENTS

### /create-discovery-questionnaire
**Purpose**: Generate structured discovery questionnaire
**Inputs**: Client name, industry, project type hint
**Outputs**: Discovery questionnaire YAML/markdown
**MCP Tools**: Brave Search (competitive research)
**Type**: Atomic

### /analyze-hubspot-deal
**Purpose**: Extract requirements from HubSpot deal information
**Inputs**: HubSpot deal URL or ID
**Outputs**: Structured requirements summary
**Type**: Atomic
**Notes**: Manual input expected (future HubSpot MCP)

### /process-fathom-transcript
**Purpose**: Extract key requirements from Fathom call transcript
**Inputs**: Fathom transcript text or URL
**Outputs**: Structured requirements, action items, stakeholders
**Type**: Atomic
**Focus**: Business objectives, constraints, technical requirements

### /create-stakeholder-list
**Purpose**: Document project stakeholders and roles
**Inputs**: Stakeholder information from discovery
**Outputs**: Stakeholder list YAML
**Type**: Atomic

### /validate-requirements
**Purpose**: Check requirements completeness and feasibility
**Inputs**: Discovery outputs
**Outputs**: Validation report, gaps identified
**MCP Tools**: Archon RAG (similar projects)
**Type**: Composed
**Calls**: /search-aws-docs, /search-code-patterns

---

## STAGE 2: SCOPING & ARCHITECTURE

### /create-data-model
**Purpose**: Generate data model YAML from requirements
**Inputs**: Requirements document, entities identified
**Outputs**: data-model.yaml with DynamoDB tables, access patterns
**MCP Tools**: AWS Documentation MCP (DynamoDB), Archon RAG
**Type**: Atomic
**Template**: `assets/data-model-template.yaml`

### /create-aws-services-architecture
**Purpose**: Generate AWS services architecture specification
**Inputs**: Requirements, data model
**Outputs**: aws-services.yaml with Lambda, API Gateway, S3, etc.
**MCP Tools**: AWS Documentation MCP
**Type**: Atomic
**Template**: `assets/aws-services-template.yaml`

### /create-ui-specification
**Purpose**: Generate UI specification with complete user flows
**Inputs**: Requirements, features list
**Outputs**: ui-spec.yaml with pages, components, routes, sample data
**Type**: Atomic
**Template**: `assets/ui-spec-template.yaml`
**Critical**: Must include complete user journeys and data flow

### /generate-architecture-diagram
**Purpose**: Create visual architecture diagram
**Inputs**: AWS services YAML
**Outputs**: Architecture diagram (PNG/Mermaid)
**MCP Tools**: AWS Diagram Server MCP (generate_diagram, list_icons)
**Type**: Atomic

### /estimate-aws-costs
**Purpose**: Generate cost estimate for proposed architecture
**Inputs**: AWS services YAML, expected usage patterns
**Outputs**: Cost estimate document with monthly projections
**MCP Tools**: AWS Documentation MCP (pricing)
**Type**: Atomic
**Include**: Cost optimization recommendations

### /validate-architecture
**Purpose**: Review architecture for best practices and issues
**Inputs**: Architecture YAML files
**Outputs**: Validation report, recommendations
**MCP Tools**: AWS Documentation MCP, Archon RAG
**Type**: Composed

### /create-technology-stack-doc
**Purpose**: Document technology choices and rationale
**Inputs**: Architecture decisions
**Outputs**: Technology stack documentation
**Type**: Atomic

---

## STAGE 3: PLANNING & PRD

### /create-prd
**Purpose**: Generate comprehensive Product Requirements Document
**Inputs**: Scoping outputs (data model, architecture, UI spec)
**Outputs**: Planning.md (PRD) with features, user stories, acceptance criteria
**Type**: Composed
**Aggregates**: All scoping outputs

### /create-agile-stories
**Purpose**: Break down features into 4-week sprint agile stories
**Inputs**: PRD, feature list
**Outputs**: Agile stories YAML with priorities, estimates, dependencies
**MCP Tools**: Archon Task Manager (manage_task - create multiple)
**Type**: Atomic
**Granularity**: 30 min - 4 hours per task

### /create-cdk-constructs-yaml
**Purpose**: Define CDK infrastructure patterns
**Inputs**: AWS services YAML
**Outputs**: cdk-constructs.yaml with reusable construct definitions
**MCP Tools**: AWS Documentation MCP (CDK patterns), Ref Documentation MCP
**Type**: Atomic

### /create-success-criteria
**Purpose**: Define measurable success criteria for project
**Inputs**: PRD, business objectives
**Outputs**: success-criteria.yaml with metrics, tests, benchmarks
**Type**: Atomic
**Template**: `assets/success-criteria-template.yaml`

### /create-test-plan
**Purpose**: Generate comprehensive test plan
**Inputs**: Features, user flows
**Outputs**: Test plan with unit, integration, E2E test specifications
**Type**: Atomic

### /create-hello-world-tests
**Purpose**: Generate initial E2E test scaffolding
**Inputs**: UI spec, routes
**Outputs**: Playwright test files for basic flows
**MCP Tools**: Playwright MCP (structure reference)
**Type**: Atomic

### /create-archon-project
**Purpose**: Initialize project in Archon with tasks
**Inputs**: Project name, description, agile stories
**Outputs**: Archon project ID, task IDs
**MCP Tools**: Archon Task Manager (manage_project, manage_task)
**Type**: Composed

### /plan-agent-coordination
**Purpose**: Design agent coordination strategy
**Inputs**: Features, dependencies, parallelization opportunities
**Outputs**: Agent coordination plan (sequential/parallel/conditional)
**Type**: Atomic
**Reference**: `references/agent-patterns.md`

---

## STAGE 4: DEVELOPMENT & IMPLEMENTATION

### Backend Development

#### /generate-lambda-function
**Purpose**: Generate Lambda function with boilerplate
**Inputs**: Function name, trigger type, environment variables
**Outputs**: Lambda function code (Python), tests, README
**MCP Tools**: AWS Documentation MCP, Ref Documentation MCP
**Type**: Atomic
**Follows**: RevStar Lambda conventions

#### /generate-cdk-stack
**Purpose**: Generate CDK stack from construct YAML
**Inputs**: CDK constructs YAML, stack name
**Outputs**: CDK TypeScript stack code
**MCP Tools**: AWS Documentation MCP (CDK), Ref Documentation MCP
**Type**: Atomic

#### /generate-api-gateway
**Purpose**: Generate API Gateway configuration
**Inputs**: API routes, Lambda functions, auth requirements
**Outputs**: CDK API Gateway construct code
**MCP Tools**: AWS Documentation MCP
**Type**: Atomic

#### /generate-dynamodb-table
**Purpose**: Generate DynamoDB table construct
**Inputs**: Table definition from data model YAML
**Outputs**: CDK DynamoDB construct with GSIs, LSIs
**MCP Tools**: AWS Documentation MCP (DynamoDB)
**Type**: Atomic

#### /generate-s3-bucket
**Purpose**: Generate S3 bucket construct with policies
**Inputs**: Bucket purpose, lifecycle policies, access requirements
**Outputs**: CDK S3 construct code
**MCP Tools**: AWS Documentation MCP (S3)
**Type**: Atomic

#### /generate-cognito-auth
**Purpose**: Generate Cognito authentication setup
**Inputs**: Auth requirements (user pool, identity pool, MFA)
**Outputs**: CDK Cognito construct code
**MCP Tools**: AWS Documentation MCP (Cognito)
**Type**: Atomic

#### /create-glue-job
**Purpose**: Generate AWS Glue ETL job
**Inputs**: Data sources, transformations, outputs
**Outputs**: Glue job Python script, CDK construct
**MCP Tools**: AWS Documentation MCP (Glue)
**Type**: Atomic

#### /create-step-function
**Purpose**: Generate Step Functions state machine
**Inputs**: Workflow steps, error handling
**Outputs**: Step Functions ASL definition, CDK construct
**MCP Tools**: AWS Documentation MCP (Step Functions)
**Type**: Atomic

#### /create-eventbridge-rules
**Purpose**: Configure EventBridge rules and patterns
**Inputs**: Event sources, targets, rules
**Outputs**: CDK EventBridge constructs
**MCP Tools**: AWS Documentation MCP (EventBridge)
**Type**: Atomic

#### /setup-opensearch
**Purpose**: Configure OpenSearch domain
**Inputs**: Index requirements, capacity planning
**Outputs**: CDK OpenSearch construct
**MCP Tools**: AWS Documentation MCP (OpenSearch)
**Type**: Atomic

#### /configure-bedrock-integration
**Purpose**: Set up AWS Bedrock integration
**Inputs**: Model requirements, prompt templates
**Outputs**: Bedrock integration code, CDK construct
**MCP Tools**: AWS Documentation MCP (Bedrock)
**Type**: Atomic

### Frontend Development

#### /generate-frontend-component
**Purpose**: Generate React/Next.js component
**Inputs**: Component spec from UI YAML
**Outputs**: React component code, styles, tests
**MCP Tools**: Ref Documentation MCP (React/Next.js)
**Type**: Atomic

#### /generate-frontend-page
**Purpose**: Generate Next.js page with routing
**Inputs**: Page spec from UI YAML
**Outputs**: Next.js page code, layout, data fetching
**MCP Tools**: Ref Documentation MCP (Next.js)
**Type**: Atomic

### Testing & Quality

#### /generate-unit-tests
**Purpose**: Generate unit tests for code module
**Inputs**: Module/function code
**Outputs**: Unit test file (pytest/jest)
**MCP Tools**: Ref Documentation MCP (testing patterns)
**Type**: Atomic
**Approach**: TDD - can be called before implementation

#### /generate-integration-tests
**Purpose**: Generate integration tests for services
**Inputs**: Service integration points
**Outputs**: Integration test files
**MCP Tools**: Ref Documentation MCP
**Type**: Atomic

#### /run-linter
**Purpose**: Run code linter and auto-fix issues
**Inputs**: File paths or directory
**Outputs**: Linting report, fixed files
**Type**: Atomic
**Tools**: eslint/pylint/black
**When**: Before every commit

#### /run-unit-tests
**Purpose**: Execute unit test suite
**Inputs**: Test directory or specific files
**Outputs**: Test results, coverage report
**Type**: Atomic
**Tools**: pytest/jest

#### /run-integration-tests
**Purpose**: Execute integration test suite
**Inputs**: Test configuration
**Outputs**: Integration test results
**Type**: Atomic

### Deployment

#### /deploy-cdk-stack
**Purpose**: Deploy CDK stack to AWS
**Inputs**: Stack name, environment (dev/staging/prod)
**Outputs**: Deployment status, CloudFormation outputs
**Type**: Atomic
**Command**: `cdk deploy`

### Documentation

#### /document-api
**Purpose**: Generate API documentation
**Inputs**: API Gateway routes, Lambda handlers
**Outputs**: API documentation (OpenAPI/Swagger)
**Type**: Atomic

#### /document-code
**Purpose**: Generate inline code documentation
**Inputs**: Code files
**Outputs**: Updated files with docstrings/JSDoc
**Type**: Atomic

---

## STAGE 5: TESTING & VALIDATION

### /run-e2e-tests
**Purpose**: Execute end-to-end test suite with Playwright
**Inputs**: Test files, base URL
**Outputs**: E2E test results, screenshots, videos
**MCP Tools**: Playwright MCP
**Type**: Atomic

### /test-user-workflow
**Purpose**: Test specific user workflow end-to-end
**Inputs**: User workflow specification
**Outputs**: Test result, recorded session
**MCP Tools**: Playwright MCP
**Type**: Atomic

### /test-mobile-responsive
**Purpose**: Test mobile responsiveness of UI
**Inputs**: Pages to test, device configurations
**Outputs**: Screenshots, layout issues identified
**MCP Tools**: Playwright MCP (browser_resize, take_screenshot)
**Type**: Atomic

### /upload-test-data
**Purpose**: Upload sample data for testing
**Inputs**: Data files (CSV, JSON), target S3 bucket or table
**Outputs**: Upload confirmation, data IDs
**Type**: Atomic
**Tools**: AWS SDK

### /validate-data-flow
**Purpose**: Trace data flow through system
**Inputs**: Test data ID, expected path
**Outputs**: Data flow trace, validation report
**MCP Tools**: AWS CloudWatch MCP (logs inspection)
**Type**: Composed

### /run-security-tests
**Purpose**: Run OWASP top 10 security validation
**Inputs**: Application URLs, API endpoints
**Outputs**: Security scan report
**Type**: Atomic
**Tools**: Security scanning tools

### /run-performance-tests
**Purpose**: Execute performance benchmarks
**Inputs**: Performance test scripts, load parameters
**Outputs**: Performance metrics, bottlenecks identified
**MCP Tools**: AWS CloudWatch MCP
**Type**: Atomic

### /analyze-cloudwatch-logs
**Purpose**: Analyze CloudWatch logs for errors
**Inputs**: Log group name, time range
**Outputs**: Error summary, patterns identified
**MCP Tools**: AWS CloudWatch MCP (execute_log_insights_query, analyze_log_group)
**Type**: Atomic

### /check-test-coverage
**Purpose**: Generate test coverage report
**Inputs**: Coverage data files
**Outputs**: Coverage report with uncovered areas
**Type**: Atomic
**Tools**: Coverage analysis tools

### /create-bug-report
**Purpose**: Document bug with reproduction steps
**Inputs**: Bug description, steps to reproduce, screenshots
**Outputs**: Bug report document, optional GitHub issue
**MCP Tools**: Archon Task Manager (create bug task)
**Type**: Atomic

---

## STAGE 6: QA HARDENING & DOCUMENTATION

### /run-cdk-diff
**Purpose**: Check CDK infrastructure drift
**Inputs**: Stack name
**Outputs**: CDK diff output, changes identified
**Type**: Atomic
**Command**: `cdk diff`
**Critical**: Run before deployment

### /compile-packages
**Purpose**: Test package compilation on Windows/Mac
**Inputs**: Package directories
**Outputs**: Compilation results, platform-specific issues
**Type**: Atomic

### /validate-documentation
**Purpose**: Check documentation completeness
**Inputs**: Documentation directory
**Outputs**: Validation report, missing sections
**Type**: Composed

### /generate-readme
**Purpose**: Generate comprehensive README
**Inputs**: Project information, architecture, setup steps
**Outputs**: README.md
**Type**: Atomic
**Template**: RevStar README structure

### /generate-deployment-guide
**Purpose**: Create step-by-step deployment guide
**Inputs**: CDK stacks, prerequisites, environment configuration
**Outputs**: deployment-guide.md
**MCP Tools**: AWS Documentation MCP
**Type**: Atomic

### /generate-troubleshooting-guide
**Purpose**: Document common issues and solutions
**Inputs**: Known issues, CloudWatch logs analysis
**Outputs**: troubleshooting-guide.md
**Type**: Atomic

### /generate-architecture-documentation
**Purpose**: Create comprehensive architecture documentation
**Inputs**: Architecture diagrams, AWS services YAML
**Outputs**: architecture.md
**Type**: Atomic

### /audit-aws-services
**Purpose**: Verify all AWS services are documented
**Inputs**: Deployed stacks, documentation
**Outputs**: Audit report, missing services
**MCP Tools**: AWS CloudWatch MCP, AWS Documentation MCP
**Type**: Composed

### /optimize-costs
**Purpose**: Review and optimize AWS costs
**Inputs**: Current architecture, cost usage
**Outputs**: Cost optimization recommendations
**MCP Tools**: AWS CloudWatch MCP (cost metrics)
**Type**: Atomic

### /run-final-security-audit
**Purpose**: Final security review before handoff
**Inputs**: All code, infrastructure, configurations
**Outputs**: Security audit report
**Type**: Composed
**Tools**: Security audit tools

### /analyze-infinite-loop-risk
**Purpose**: Scan for potential infinite loop patterns
**Inputs**: Lambda functions, EventBridge rules
**Outputs**: Risk analysis report
**Type**: Atomic
**Critical**: Prevents costly infinite loop incidents

---

## STAGE 7: CLIENT HANDOFF

### /create-handoff-presentation
**Purpose**: Generate client handoff presentation slides
**Inputs**: Project overview, architecture, demos, next steps
**Outputs**: Handoff presentation (markdown/PPTX)
**Type**: Composed
**Reference**: Handoff skill if available

### /create-access-checklist
**Purpose**: Document all client access requirements
**Inputs**: AWS resources, credentials, external services
**Outputs**: access-checklist.md
**Type**: Atomic

### /create-next-steps-doc
**Purpose**: Document recommended next steps and roadmap
**Inputs**: Project status, future enhancements
**Outputs**: next-steps.md
**Type**: Atomic

### /record-walkthrough-video
**Purpose**: Create recorded video demonstration
**Inputs**: User workflows to demonstrate
**Outputs**: Video file paths, timestamps
**MCP Tools**: Playwright MCP (browser automation with recording)
**Type**: Atomic

### /update-readme-for-client
**Purpose**: Update README with client-specific information
**Inputs**: Current README, client details
**Outputs**: Updated README.md
**Type**: Atomic

### /create-support-plan
**Purpose**: Document support and maintenance plan
**Inputs**: Support channels, SLAs, maintenance procedures
**Outputs**: support-plan.md
**Type**: Atomic

### /verify-client-access
**Purpose**: Test client credentials and access
**Inputs**: Client credentials, resources to test
**Outputs**: Access verification report
**Type**: Atomic
**Tools**: AWS CLI

---

## STAGE 8: CI/CD & MONITORING

### /setup-github-actions
**Purpose**: Configure GitHub Actions CI/CD pipeline
**Inputs**: Repository, deployment workflow requirements
**Outputs**: .github/workflows/*.yml files
**MCP Tools**: Ref Documentation MCP (GitHub Actions)
**Type**: Atomic

### /setup-codepipeline
**Purpose**: Configure AWS CodePipeline
**Inputs**: Source repository, build specs, deployment stages
**Outputs**: CDK CodePipeline construct
**MCP Tools**: AWS Documentation MCP (CodePipeline)
**Type**: Atomic

### /configure-cloudwatch-logging
**Purpose**: Set up centralized logging configuration
**Inputs**: Log groups, retention policies
**Outputs**: CloudWatch logs configuration
**MCP Tools**: AWS CloudWatch MCP
**Type**: Atomic

### /create-monitoring-dashboard
**Purpose**: Create CloudWatch dashboard for monitoring
**Inputs**: Metrics to track, alarm thresholds
**Outputs**: CloudWatch dashboard configuration
**MCP Tools**: AWS CloudWatch MCP
**Type**: Atomic

### /setup-cost-alerts
**Purpose**: Configure billing and cost alerts
**Inputs**: Budget thresholds, notification channels
**Outputs**: CloudWatch billing alarms
**MCP Tools**: AWS CloudWatch MCP
**Type**: Atomic
**Critical**: Prevent cost overruns

### /setup-performance-alarms
**Purpose**: Configure performance monitoring alerts
**Inputs**: Performance thresholds (latency, errors)
**Outputs**: CloudWatch alarms
**MCP Tools**: AWS CloudWatch MCP
**Type**: Atomic

### /document-rollback-procedure
**Purpose**: Document deployment rollback steps
**Inputs**: Deployment process, backup strategies
**Outputs**: rollback-procedure.md
**Type**: Atomic

### /test-rollback
**Purpose**: Test rollback mechanism
**Inputs**: Previous deployment version
**Outputs**: Rollback test results
**Type**: Atomic
**Tools**: CDK or deployment tools

### /test-cicd-pipeline
**Purpose**: Validate CI/CD pipeline functionality
**Inputs**: Test commit/branch
**Outputs**: Pipeline execution results
**Type**: Atomic
**Tools**: Git + pipeline trigger

### /analyze-cloudwatch-metrics
**Purpose**: Analyze performance metrics and trends
**Inputs**: Metric names, time range
**Outputs**: Metrics analysis report
**MCP Tools**: AWS CloudWatch MCP (get_metric_data)
**Type**: Atomic

---

## IMPLEMENTATION ROADMAP

### Phase 1: Essential Commands (Week 1)
**Priority**: Critical path for basic workflow

1. Cross-cutting commands (8 commands)
   - /commit-changes, /create-git-branch
   - /update-archon-task, /log-time-ado
   - /search-aws-docs, /search-code-patterns
   - /update-work-status, /setup-git-worktree

2. Discovery commands (5 commands)
   - /create-discovery-questionnaire
   - /process-fathom-transcript
   - /create-stakeholder-list
   - /validate-requirements

3. Scoping commands (7 commands)
   - /create-data-model
   - /create-aws-services-architecture
   - /create-ui-specification
   - /generate-architecture-diagram
   - /estimate-aws-costs
   - /validate-architecture

**Total**: 20 commands

### Phase 2: Development Commands (Week 2)
**Priority**: Enable feature implementation

1. Planning commands (8 commands)
   - /create-prd
   - /create-agile-stories
   - /create-cdk-constructs-yaml
   - /create-success-criteria
   - /create-test-plan
   - /create-archon-project
   - /plan-agent-coordination

2. Core development (12 commands)
   - /generate-lambda-function
   - /generate-cdk-stack
   - /generate-api-gateway
   - /generate-dynamodb-table
   - /generate-s3-bucket
   - /generate-cognito-auth
   - /generate-frontend-component
   - /generate-frontend-page
   - /generate-unit-tests
   - /run-linter
   - /run-unit-tests
   - /deploy-cdk-stack

**Total**: 20 commands

### Phase 3: Testing & Quality (Week 3)
**Priority**: Validation and documentation

1. Testing commands (10 commands)
   - /run-e2e-tests
   - /test-user-workflow
   - /test-mobile-responsive
   - /upload-test-data
   - /validate-data-flow
   - /run-security-tests
   - /run-performance-tests
   - /analyze-cloudwatch-logs
   - /check-test-coverage
   - /create-bug-report

2. QA commands (11 commands)
   - /run-cdk-diff
   - /compile-packages
   - /validate-documentation
   - /generate-readme
   - /generate-deployment-guide
   - /generate-troubleshooting-guide
   - /generate-architecture-documentation
   - /audit-aws-services
   - /optimize-costs
   - /run-final-security-audit
   - /analyze-infinite-loop-risk

**Total**: 21 commands

### Phase 4: Handoff & Advanced (Week 4)
**Priority**: Client delivery and specialized features

1. Handoff commands (7 commands)
   - /create-handoff-presentation
   - /create-access-checklist
   - /create-next-steps-doc
   - /record-walkthrough-video
   - /update-readme-for-client
   - /create-support-plan
   - /verify-client-access

2. CI/CD commands (10 commands)
   - /setup-github-actions
   - /setup-codepipeline
   - /configure-cloudwatch-logging
   - /create-monitoring-dashboard
   - /setup-cost-alerts
   - /setup-performance-alarms
   - /document-rollback-procedure
   - /test-rollback
   - /test-cicd-pipeline
   - /analyze-cloudwatch-metrics

3. Advanced commands (6 commands)
   - /create-glue-job
   - /create-step-function
   - /setup-opensearch
   - /configure-bedrock-integration
   - /create-eventbridge-rules

**Total**: 23 commands

### Implementation Summary
- **Phase 1**: 20 commands (Discovery → Scoping)
- **Phase 2**: 20 commands (Planning → Development)
- **Phase 3**: 21 commands (Testing → QA)
- **Phase 4**: 23 commands (Handoff → CI/CD → Advanced)
- **Grand Total**: 84 core commands + 26 specialized = 110+ commands

---

## COMMAND COMPOSITION PATTERNS

### Atomic Commands
**Characteristics**:
- Single, focused operation
- No dependencies on other commands
- Direct inputs → outputs
- Can be composed into workflows

**Example**: `/generate-lambda-function`
```
Input: function_name, trigger_type, env_vars
Process: Generate boilerplate code
Output: Lambda function .py file, test file, README
```

### Composed Commands
**Characteristics**:
- Orchestrate multiple atomic commands
- Handle complex workflows
- Aggregate outputs

**Example**: `/validate-architecture`
```
Calls:
  1. /search-aws-docs (best practices)
  2. /search-code-patterns (similar architectures)
  3. Analyze architecture files
  4. Generate validation report
```

**Example**: `/create-archon-project`
```
Calls:
  1. Archon manage_project (create)
  2. Parse agile stories YAML
  3. For each story:
     - Archon manage_task (create)
  4. /update-work-status
  5. Return project_id and task_ids
```

**Example**: `/audit-aws-services`
```
Calls:
  1. AWS CloudWatch MCP (list deployed resources)
  2. Read documentation files
  3. Compare deployed vs documented
  4. Generate gap analysis report
```

---

## MCP TOOL USAGE MATRIX

| MCP Tool | Commands Using It | Primary Use Cases |
|----------|-------------------|-------------------|
| Archon Task Manager | 10+ | Task management, project tracking, time logging |
| AWS Documentation MCP | 30+ | Service specs, best practices, pricing, patterns |
| AWS CloudWatch MCP | 15+ | Logging, metrics, monitoring, cost tracking |
| Playwright MCP | 8+ | E2E testing, UI validation, video recording |
| Ref Documentation MCP | 12+ | Code patterns, framework best practices |
| AWS Diagram Server MCP | 2 | Architecture visualization |
| Brave Search MCP | 2 | Market research, competitive analysis |

---

## IMPLEMENTATION GUIDELINES

### 1. Command Structure
Each command should follow this structure:

```markdown
### /command-name
**Purpose**: One-line description
**Inputs**:
  - input1: Description
  - input2: Description
**Outputs**: What is produced
**Stage**: Which workflow stage
**MCP Tools**: Tools used (if any)
**Type**: Atomic or Composed
**Notes**: Additional considerations
```

### 2. Error Handling
All commands must:
- Validate inputs before processing
- Handle failures gracefully
- Return clear error messages
- Log errors for debugging

### 3. Conventions
Commands must follow:
- RevStar naming conventions
- File structure standards
- Code quality requirements
- Security best practices

Reference: `references/revstar-conventions.md`

### 4. Testing
Each command should have:
- Unit tests
- Integration tests (if applicable)
- Usage examples
- Edge case documentation

### 5. Documentation
Each command needs:
- Clear usage instructions
- Example invocations
- Expected outputs
- Troubleshooting tips

### 6. Progressive Disclosure
Commands should:
- Load documentation only when needed
- Use 2-5 keyword queries for RAG
- Reference detailed docs rather than duplicating
- Keep context lean

### 7. Composability
Atomic commands should:
- Have clear input/output contracts
- Be independently useful
- Compose well with other commands
- Support workflow orchestration

### 8. Idempotency
When possible, commands should:
- Be safe to retry
- Check current state before acting
- Handle "already done" scenarios
- Avoid duplicate operations

### 9. Cost Awareness
Commands that deploy AWS resources should:
- Warn about potential costs
- Provide cost estimates
- Suggest optimization opportunities
- Include cleanup procedures

### 10. Logging
All commands should:
- Log to work-status.md
- Update Archon tasks
- Provide progress updates
- Record timing information

---

## COMMAND USAGE EXAMPLES

### Example 1: Discovery Phase Workflow
```bash
# User starts new project
/create-discovery-questionnaire client="Acme Corp" industry="FinTech"
/process-fathom-transcript transcript="path/to/transcript.txt"
/create-stakeholder-list
/validate-requirements
/commit-changes message="docs: add discovery documentation"
/update-archon-task task_id="T-001" status="done"
```

### Example 2: Architecture Design
```bash
# After discovery approved
/create-data-model requirements="discovery-output.yaml"
/create-aws-services-architecture requirements="discovery-output.yaml"
/create-ui-specification features="feature-list.yaml"
/generate-architecture-diagram services="aws-services.yaml"
/estimate-aws-costs services="aws-services.yaml"
/validate-architecture
# HUMAN CHECKPOINT: Review and approve architecture
```

### Example 3: Parallel Development
```bash
# Set up worktrees for parallel features
/setup-git-worktree feature="authentication" base="main"
/setup-git-worktree feature="document-processing" base="main"
/setup-git-worktree feature="frontend-ui" base="main"

# In worktree 1: Authentication
/generate-lambda-function name="auth-handler" trigger="api-gateway"
/generate-cognito-auth requirements="auth-spec.yaml"
/generate-unit-tests module="auth-handler"
/run-unit-tests
/commit-changes message="feat: add authentication module"

# In worktree 2: Document Processing (parallel)
/generate-lambda-function name="doc-processor" trigger="s3"
/generate-s3-bucket purpose="document-storage"
# ... similar pattern

# In worktree 3: Frontend (parallel)
/generate-frontend-page page="login"
/generate-frontend-component component="DocumentUploader"
# ... similar pattern
```

### Example 4: Testing & Validation
```bash
# Deploy and test
/deploy-cdk-stack stack="AcmeCorpStack" environment="dev"
/upload-test-data files="sample-data.csv" bucket="test-bucket"
/run-e2e-tests
/test-user-workflow workflow="document-upload-flow"
/test-mobile-responsive pages="all"
/analyze-cloudwatch-logs log_group="/aws/lambda/doc-processor"
/check-test-coverage
# HUMAN CHECKPOINT: Review test results
```

### Example 5: QA & Handoff
```bash
# Final checks
/run-cdk-diff stack="AcmeCorpStack"
/audit-aws-services
/run-final-security-audit
/optimize-costs

# Documentation
/generate-readme
/generate-deployment-guide
/generate-troubleshooting-guide
/generate-architecture-documentation

# Handoff
/create-handoff-presentation
/create-access-checklist
/record-walkthrough-video
/verify-client-access
# HUMAN CHECKPOINT: Client sign-off
```

---

## NEXT STEPS

1. **Prioritize Implementation**: Start with Phase 1 commands
2. **Create Command Files**: Build `.claude/commands/*.md` files
3. **Test Commands**: Validate each command independently
4. **Compose Workflows**: Build skills from command compositions
5. **Document Usage**: Create examples and troubleshooting guides
6. **Iterate**: Refine based on real project usage

---

**Remember**: Commands are the foundation. Master them first, then build up to skills, agents, and complete workflows. Every complex workflow is just a composition of well-designed command primitives.
