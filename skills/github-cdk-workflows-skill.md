# GitHub & AWS CDK Workflows Skill

> **Purpose**: This document provides comprehensive knowledge for building a Claude agent skill that can assist with GitHub workflows, Git lifecycle management, and AWS CDK CI/CD pipelines.

---

## Table of Contents

1. [GitHub Platform Overview](#github-platform-overview)
2. [Git Lifecycle](#git-lifecycle)
3. [Issues Lifecycle](#issues-lifecycle)
4. [Pull Request Workflow](#pull-request-workflow)
5. [GitHub Actions CI/CD](#github-actions-cicd)
6. [AWS CDK Workflow Patterns](#aws-cdk-workflow-patterns)
7. [CDK Testing Strategies](#cdk-testing-strategies)
8. [Workflow File Templates](#workflow-file-templates)
9. [Log Retention & Observability](#log-retention--observability)
10. [Best Practices & Decision Matrix](#best-practices--decision-matrix)

---

## GitHub Platform Overview

### Core Features

| Feature | Purpose | Use Case |
|---------|---------|----------|
| **Repositories** | Host and version control code | Source code management |
| **Issues** | Track bugs, features, tasks | Project planning |
| **Pull Requests** | Code review and merge workflow | Collaboration |
| **Actions** | CI/CD automation pipelines | Build, test, deploy |
| **Projects** | Kanban-style project management | Sprint planning |
| **Discussions** | Community Q&A and announcements | Team communication |
| **Packages** | Package registry (npm, Docker, etc.) | Artifact storage |
| **Codespaces** | Cloud-based development environments | Remote development |
| **Copilot** | AI pair programming assistant | Code assistance |
| **Security** | Dependabot, code scanning, secrets | Vulnerability management |

### Feature Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GITHUB PLATFORM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Repositories│  │   Issues    │  │Pull Requests│  │  Actions    │        │
│  │             │  │             │  │    (PRs)    │  │   (CI/CD)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Projects   │  │ Discussions │  │    Wiki     │  │  Packages   │        │
│  │  (Boards)   │  │  (Forums)   │  │   (Docs)    │  │  (Registry) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Gists     │  │  Codespaces │  │   Copilot   │  │  Security   │        │
│  │ (Snippets)  │  │  (Cloud IDE)│  │    (AI)     │  │  (Scanning) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Git Lifecycle

### Working Areas

```
    WORKING         STAGING          LOCAL            REMOTE
    DIRECTORY        AREA           REPOSITORY       REPOSITORY
        │              │                │                │
        │              │                │                │
   ┌────┴────┐    ┌────┴────┐    ┌─────┴─────┐    ┌─────┴─────┐
   │         │    │         │    │           │    │           │
   │  Edit   │    │ Staged  │    │ Committed │    │  Pushed   │
   │  Files  │    │ Changes │    │  History  │    │  (GitHub) │
   │         │    │         │    │           │    │           │
   └────┬────┘    └────┬────┘    └─────┬─────┘    └─────┬─────┘
        │              │                │                │
        │──── git add ─►│                │                │
        │              │── git commit ──►│                │
        │              │                │──── git push ──►│
        │◄─────────────────────────────────── git pull ──│
        │◄─────────────────────────────────── git clone ─│
```

### Command Reference

| Command | From → To | Purpose |
|---------|-----------|---------|
| `git add <file>` | Working → Staging | Stage changes |
| `git add .` | Working → Staging | Stage all changes |
| `git commit -m "msg"` | Staging → Local | Create commit |
| `git push origin <branch>` | Local → Remote | Upload to GitHub |
| `git pull origin <branch>` | Remote → Local | Download & merge |
| `git fetch origin` | Remote → Local | Download only (no merge) |
| `git checkout -- <file>` | Staging → Working | Discard changes |
| `git reset HEAD <file>` | Local → Staging | Unstage file |
| `git stash` | Working → Stash | Temporarily store |
| `git stash pop` | Stash → Working | Restore stashed |

### Branching Model (GitFlow)

```
main/master    ●────●────●─────────────●────────────●────●─────────►
               │         ▲             │            ▲    │
               │         │             │            │    │
develop        │    ●────┴──●────●─────┴──●────●────┴────┼──●───────►
               │    │       │    │        │    │         │
               │    │       │    │        │    │         │
feature/       │    │  ●────┘    │        │    │         │
  auth         │    │  │         │        │    │         │
               │    │  ●         │        │    │         │
               │    │            │        │    │         │
feature/       │    │       ●────┘        │    │         │
  api          │    │       │             │    │         │
               │    │       ●             │    │         │
               │    │                     │    │         │
hotfix/        │    │                     │    ●─────────┘
  security     │    │                     │    │
               │    │                     │    ●

Legend:  ● = commit    ───► = branch continues    
         ▲ = merge     │ = branch relationship
```

---

## Issues Lifecycle

### States & Transitions

```
                        ┌─────────────┐
                        │    OPEN     │◄──────────────────┐
                        └──────┬──────┘                   │
                               │                          │
           ┌───────────────────┼───────────────────┐      │
           │                   │                   │      │
           ▼                   ▼                   ▼      │
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
    │  Duplicate  │    │  Won't Fix  │    │   Closed    │ │
    │   (Close)   │    │   (Close)   │    │  (Resolved) │ │
    └─────────────┘    └─────────────┘    └──────┬──────┘ │
                                                 │        │
                                                 │ Reopen │
                                                 └────────┘
```

### Issue Workflow

```
    ┌─────────┐      ┌─────────┐      ┌──────────┐      ┌─────────┐
    │ CREATED │ ───► │ TRIAGED │ ───► │ ASSIGNED │ ───► │ IN WORK │
    └─────────┘      └─────────┘      └──────────┘      └─────────┘
         │                │                │                 │
         ▼                ▼                ▼                 ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    LABELS & METADATA                         │
    │  • bug, feature, enhancement, documentation                  │
    │  • priority: critical, high, medium, low                     │
    │  • status: needs-triage, in-progress, blocked                │
    │  • milestone assignment                                       │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ LINKED   │ ───► │ PR OPENS │ ───► │  CLOSED  │
    │  TO PR   │      │ "Fixes   │      │   (Done) │
    │          │      │  #123"   │      │          │
    └──────────┘      └──────────┘      └──────────┘
```

### Common Labels

| Label | Purpose |
|-------|---------|
| `bug` | Something isn't working |
| `feature` | New feature request |
| `enhancement` | Improvement to existing feature |
| `documentation` | Documentation updates |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `priority: critical` | Must fix immediately |
| `priority: high` | Important, fix soon |
| `wontfix` | Will not be worked on |
| `duplicate` | Already exists |

---

## Pull Request Workflow

### PR Lifecycle

```
  ┌─────────────┐
  │ Create      │
  │ Feature     │
  │ Branch      │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   Develop   │────►│   Commit    │────►│   Push to   │
  │   Locally   │     │   Changes   │     │   Remote    │
  └─────────────┘     └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Open Pull  │
                                          │   Request   │
                                          └──────┬──────┘
         ┌───────────────────────────────────────┼───────────────────────────┐
         │                                       │                           │
         ▼                                       ▼                           ▼
  ┌─────────────┐                        ┌─────────────┐             ┌─────────────┐
  │   CI/CD     │                        │    Code     │             │  Link to    │
  │   Checks    │                        │   Review    │             │   Issues    │
  │   Run       │                        │             │             │ "Fixes #42" │
  └──────┬──────┘                        └──────┬──────┘             └─────────────┘
         │                                      │
         │          ┌───────────────────────────┘
         │          │
         ▼          ▼
  ┌─────────────────────────────────┐
  │      Request Changes?           │
  │                                 │
  │    YES              NO          │
  │     │                │          │
  │     ▼                ▼          │
  │  ┌──────┐      ┌──────────┐     │
  │  │Update│      │ Approved │     │
  │  │ Code │      │          │     │
  │  └──┬───┘      └────┬─────┘     │
  │     │               │           │
  │     └───────┐       │           │
  │             │       │           │
  └─────────────┼───────┼───────────┘
                │       │
                ▼       ▼
         ┌─────────────────┐
         │     MERGE       │
         │  ┌───────────┐  │
         │  │ • Merge   │  │
         │  │ • Squash  │  │
         │  │ • Rebase  │  │
         │  └───────────┘  │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Delete Branch  │
         │  Close Issues   │
         └─────────────────┘
```

### Merge Strategies

| Strategy | Result | Use When |
|----------|--------|----------|
| **Merge commit** | Preserves all commits + merge commit | Full history needed |
| **Squash and merge** | Combines all into one commit | Clean history preferred |
| **Rebase and merge** | Replays commits on top of base | Linear history required |

---

## GitHub Actions CI/CD

### Workflow Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ACTIONS WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

  TRIGGER                    WORKFLOW                        RESULT
  ═══════                    ════════                        ══════

  ┌──────────┐
  │  Push    │───┐
  └──────────┘   │
                 │         ┌─────────────────────────────────────────────┐
  ┌──────────┐   │         │               .github/workflows/            │
  │   PR     │───┼────────►│                                             │
  └──────────┘   │         │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
                 │         │  │  Job 1  │  │  Job 2  │  │  Job 3  │     │
  ┌──────────┐   │         │  │  Build  │─►│  Test   │─►│ Deploy  │     │
  │ Schedule │───┤         │  └─────────┘  └─────────┘  └─────────┘     │
  └──────────┘   │         │       │            │            │          │
                 │         │       ▼            ▼            ▼          │
  ┌──────────┐   │         │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
  │  Manual  │───┘         │  │ Runner  │  │ Runner  │  │ Runner  │     │
  └──────────┘             │  │ ubuntu  │  │ ubuntu  │  │ ubuntu  │     │
                           │  └─────────┘  └─────────┘  └─────────┘     │
                           └───────────────────┬─────────────────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Status    │
                                        │  ✓ Pass     │
                                        │  ✗ Fail     │
                                        └─────────────┘
```

### Trigger Events

| Event | Triggers On |
|-------|-------------|
| `push` | Any push to specified branches |
| `pull_request` | PR opened, updated, or synchronized |
| `schedule` | Cron-based schedule |
| `workflow_dispatch` | Manual trigger via UI/API |
| `release` | Release published |
| `workflow_call` | Called by another workflow |

### Workflow YAML Structure

```yaml
name: Workflow Name

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  GLOBAL_VAR: value

jobs:
  job-name:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install
        run: npm ci
      
      - name: Test
        run: npm test
```

---

## AWS CDK Workflow Patterns

### Recommended Workflow Layers

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    AWS CDK + AGENT CORE WORKFLOW LAYERS                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   LAYER 1: PR VALIDATION (Always Run)                                          │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│   │   Lint &     │  │    Unit      │  │   CDK Synth  │  │   CDK Diff   │       │
│   │   Format     │  │    Tests     │  │  (validate)  │  │   (preview)  │       │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                                 │
│   LAYER 2: STAGING (On Merge to main/develop)                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                         │
│   │  CDK Deploy  │  │   Smoke      │  │  Integration │                         │
│   │   Staging    │  │   Tests      │  │    Tests     │                         │
│   └──────────────┘  └──────────────┘  └──────────────┘                         │
│                                                                                 │
│   LAYER 3: PRODUCTION (Gated / Manual Approval)                                │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                         │
│   │   Manual     │  │  CDK Deploy  │  │   Health     │                         │
│   │   Approval   │──►│   Prod      │──►│   Checks     │                         │
│   └──────────────┘  └──────────────┘  └──────────────┘                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
.github/
└── workflows/
    ├── pr-validation.yml      # Runs on all PRs (lint, test, synth, diff)
    ├── deploy-staging.yml     # Runs on merge to main (auto-deploy staging)
    ├── deploy-prod.yml        # Manual trigger or tag-based (with approval)
    ├── destroy-preview.yml    # Cleanup ephemeral envs (optional)
    └── health-check.yml       # Scheduled cron job for prod monitoring
```

### Full Workflow Flow

```
                     Developer pushes feature branch
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         PR VALIDATION WORKFLOW                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │   ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐            │ │
│  │   │checkout│───►│install │───►│ lint   │───►│  test  │            │ │
│  │   └────────┘    │  deps  │    │        │    │ (unit) │            │ │
│  │                 └────────┘    └────────┘    └───┬────┘            │ │
│  │                                                 │                  │ │
│  │   ┌────────────┐    ┌────────────┐             │                  │ │
│  │   │ cdk synth  │◄───┤cdk snapshot│◄────────────┘                  │ │
│  │   └─────┬──────┘    │   tests    │                                │ │
│  │         │           └────────────┘                                │ │
│  │         ▼                                                         │ │
│  │   ┌────────────┐    ┌────────────────┐                           │ │
│  │   │  cdk diff  │───►│ Post diff as   │                           │ │
│  │   │            │    │ PR comment     │                           │ │
│  │   └────────────┘    └────────────────┘                           │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                          (PR approved & merged)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STAGING DEPLOYMENT WORKFLOW                         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐     │ │
│  │   │ Configure AWS │───►│  cdk deploy   │───►│ Smoke tests   │     │ │
│  │   │ OIDC creds    │    │  --staging    │    │               │     │ │
│  │   └───────────────┘    └───────────────┘    └───────┬───────┘     │ │
│  │                                                     │             │ │
│  │                              ┌──────────────────────┘             │ │
│  │                              ▼                                    │ │
│  │   ┌───────────────┐    ┌───────────────┐                         │ │
│  │   │ Integration   │───►│ Notify Slack  │                         │ │
│  │   │ tests (opt)   │    │ /Teams        │                         │ │
│  │   └───────────────┘    └───────────────┘                         │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                        (Manual approval / tag)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PRODUCTION DEPLOYMENT WORKFLOW                       │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐     │ │
│  │   │  Manual Gate  │───►│  cdk deploy   │───►│ Health checks │     │ │
│  │   │  (approval)   │    │  --prod       │    │               │     │ │
│  │   └───────────────┘    └───────────────┘    └───────┬───────┘     │ │
│  │                                                     │             │ │
│  │                              ┌──────────────────────┘             │ │
│  │                              ▼                                    │ │
│  │   ┌───────────────┐    ┌───────────────┐                         │ │
│  │   │ E2E tests     │───►│ Monitor /     │                         │ │
│  │   │ (if needed)   │    │ Alerting      │                         │ │
│  │   └───────────────┘    └───────────────┘                         │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### AWS Credential Management

**Recommended: OIDC Authentication (No stored secrets)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AWS AUTHENTICATION STRATEGY                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   RECOMMENDED: OIDC (No long-lived secrets!)                           │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                                                                 │  │
│   │   GitHub Actions ──OIDC Token──► AWS IAM ──Assume Role──► CDK   │  │
│   │                                                                 │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   Setup Steps:                                                          │
│   1. Create IAM OIDC Identity Provider for GitHub                      │
│   2. Create IAM Role with trust policy for GitHub repo                 │
│   3. Use aws-actions/configure-aws-credentials@v4                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## CDK Testing Strategies

### Testing Pyramid

```
                            ▲
                           ╱ ╲
                          ╱   ╲
                         ╱ E2E ╲         ← Expensive, slow, high confidence
                        ╱ Tests ╲           (Optional for dev → staging)
                       ╱─────────╲
                      ╱           ╲
                     ╱ Integration ╲     ← Deploy & verify resources
                    ╱    Tests      ╲       (Staging deploys)
                   ╱─────────────────╲
                  ╱                   ╲
                 ╱   Snapshot Tests    ╲  ← Compare CloudFormation output
                ╱   (CDK Assertions)    ╲    (Every PR)
               ╱─────────────────────────╲
              ╱                           ╲
             ╱       Unit Tests            ╲  ← Fast, cheap, run always
            ╱    (Constructs & Logic)       ╲    (Every commit)
           ╱─────────────────────────────────╲
```

### Test Types Reference

| Test Type | What It Tests | When to Run | Priority |
|-----------|---------------|-------------|----------|
| **Unit Tests** | Construct logic, helper functions | Every PR | Essential |
| **Snapshot Tests** | CloudFormation template hasn't changed unexpectedly | Every PR | Essential |
| **CDK Assertions** | Specific resources exist with correct config | Every PR | Essential |
| **CDK Diff** | Preview what will change before deploy | Every PR | Essential |
| **Smoke Tests** | Basic "is it alive" after deploy | Staging deploy | Recommended |
| **Integration Tests** | Resources work together (Lambda→S3, etc.) | Staging | Situational |
| **E2E Tests** | Full user flows across stack | Pre-prod gate | Usually overkill for dev |
| **Health Checks** | Endpoints respond, metrics OK | Post-deploy | Recommended for prod |

### CDK Assertion Examples (TypeScript)

```typescript
import { Template, Match } from 'aws-cdk-lib/assertions';
import * as cdk from 'aws-cdk-lib';
import { MyStack } from '../lib/my-stack';

describe('MyStack', () => {
  const app = new cdk.App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('Lambda function created with correct runtime', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'nodejs18.x',
      Handler: 'index.handler',
    });
  });

  test('S3 bucket has encryption enabled', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketEncryption: Match.objectLike({
        ServerSideEncryptionConfiguration: Match.anyValue(),
      }),
    });
  });

  test('Matches snapshot', () => {
    expect(template.toJSON()).toMatchSnapshot();
  });
});
```

---

## Workflow File Templates

### PR Validation Workflow

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation

on:
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    name: Lint, Test & CDK Synth
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Unit tests
        run: npm test
      
      - name: CDK Synth
        run: npx cdk synth
      
      - name: Snapshot tests
        run: npm run test:cdk

  diff:
    name: CDK Diff
    runs-on: ubuntu-latest
    needs: validate
    permissions:
      id-token: write
      contents: read
      pull-requests: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      
      - name: CDK Diff
        id: diff
        run: |
          npx cdk diff 2>&1 | tee diff-output.txt
          echo "diff<<EOF" >> $GITHUB_OUTPUT
          cat diff-output.txt >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      
      - name: Post diff to PR
        uses: actions/github-script@v7
        with:
          script: |
            const diff = `${{ steps.diff.outputs.diff }}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## CDK Diff\n\`\`\`\n${diff}\n\`\`\``
            });
```

### Staging Deployment Workflow

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy Staging
    runs-on: ubuntu-latest
    environment: staging
    permissions:
      id-token: write
      contents: read
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.STAGING_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      
      - name: CDK Deploy
        run: npx cdk deploy --all --require-approval never
      
      - name: Smoke tests
        run: |
          # Example: Test API endpoint is responding
          curl -f ${{ vars.API_ENDPOINT }}/health || exit 1
      
      - name: Notify on success
        if: success()
        run: echo "Staging deployment successful!"
      
      - name: Notify on failure
        if: failure()
        run: echo "Staging deployment failed!"
```

### Production Deployment Workflow

```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      confirm:
        description: 'Type "deploy" to confirm production deployment'
        required: true
  release:
    types: [published]

jobs:
  deploy:
    name: Deploy Production
    runs-on: ubuntu-latest
    environment: production
    if: github.event.inputs.confirm == 'deploy' || github.event_name == 'release'
    permissions:
      id-token: write
      contents: read
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.PROD_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      
      - name: CDK Deploy
        run: npx cdk deploy --all --require-approval never
      
      - name: Health check
        run: |
          for i in {1..5}; do
            curl -f ${{ vars.PROD_API_ENDPOINT }}/health && exit 0
            sleep 10
          done
          exit 1
      
      - name: Post-deploy validation
        run: npm run test:e2e || true
```

### Cleanup/Destroy Workflow

```yaml
# .github/workflows/destroy-preview.yml
name: Cleanup Preview Environment

on:
  pull_request:
    types: [closed]

jobs:
  cleanup:
    name: Destroy Preview Stack
    runs-on: ubuntu-latest
    if: startsWith(github.head_ref, 'feature/')
    permissions:
      id-token: write
      contents: read
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.DEV_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      
      - name: CDK Destroy
        run: npx cdk destroy --all --force
        env:
          STACK_SUFFIX: ${{ github.head_ref }}
```

---

## Log Retention & Observability

### GitHub Automatic Log Retention

| Log Type | Automatically Saved? | Default Retention |
|----------|---------------------|-------------------|
| Workflow run logs | ✅ Yes | 90 days |
| Job step output | ✅ Yes | 90 days |
| Console output (stdout/stderr) | ✅ Yes | 90 days |
| Timing & duration | ✅ Yes | 90 days |
| Uploaded artifacts | ✅ Yes | 90 days (configurable 1-90) |
| Workflow run metadata | ✅ Yes | 90 days |

### When to Implement External Logging

| Scenario | GitHub Logs Sufficient? |
|----------|------------------------|
| Debugging recent CI failures | ✅ Yes |
| 90 days retention meets needs | ✅ Yes |
| Single repo troubleshooting | ✅ Yes |
| Compliance > 90 days | ❌ No - stream to external |
| Cross-repo aggregation | ❌ No - use Datadog/Splunk |
| AWS unified observability | ❌ No - stream to CloudWatch |

### External Streaming Options

```yaml
# Stream to CloudWatch
- name: Send logs to CloudWatch
  run: |
    aws logs put-log-events \
      --log-group-name "/github/actions/${{ github.repository }}" \
      --log-stream-name "${{ github.run_id }}" \
      --log-events timestamp=$(date +%s000),message="$LOG_MESSAGE"
```

---

## Best Practices & Decision Matrix

### What to Include by Environment

| Component | Dev/PR | Staging | Production |
|-----------|--------|---------|------------|
| Lint & Format | ✅ | ✅ | ✅ |
| Unit Tests | ✅ | ✅ | ✅ |
| CDK Synth | ✅ | ✅ | ✅ |
| Snapshot Tests | ✅ | ✅ | ✅ |
| CDK Diff | ✅ | ✅ | ✅ |
| CDK Deploy | ❌ | ✅ | ✅ |
| Smoke Tests | ❌ | ✅ | ✅ |
| Integration Tests | ❌ | ⚠️ Optional | ✅ |
| E2E Tests | ❌ | ❌ | ⚠️ Optional |
| Health Checks | ❌ | ✅ | ✅ |
| Manual Approval | ❌ | ❌ | ✅ |
| Ephemeral Envs | ⚠️ Optional | ❌ | ❌ |

### Cost vs Benefit Analysis

| Feature | Benefit | Cost/Complexity | Recommendation |
|---------|---------|-----------------|----------------|
| OIDC Auth | High security | Medium setup | Always use |
| CDK Diff in PRs | High visibility | Low | Always use |
| Snapshot tests | Catch regressions | Low | Always use |
| Smoke tests | Validate deploys | Low | Always use |
| Ephemeral envs | Realistic testing | High ($$) | Skip unless needed |
| E2E in CI | Full coverage | High (slow) | Staging/prod only |
| Multi-region | Redundancy | Very high | Prod only |

---

## Agent Core Specific Considerations

When building workflows for autonomous agent systems:

### Pre-Deploy Checks
- Static analysis of agent behavior code
- Security scanning for dependencies
- Policy validation (what actions agent can take)
- Mock/simulated input validation

### Runtime Monitoring
- Agent health endpoints
- Decision audit trails
- Rate limiting validation
- Rollback triggers for anomalous behavior

### Deployment Strategies
- Canary deployments for agent updates
- Blue/green for zero-downtime switches
- Feature flags for gradual rollout
- Circuit breakers for failure isolation

---

## References

- [AWS CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
- [CDK Pipelines GitHub](https://github.com/cdklabs/cdk-pipelines-github)
- [AWS Cross-Account Deployment](https://aws.amazon.com/blogs/devops/cross-account-and-cross-region-deployment-using-github-actions-and-aws-cdk/)
- [GitHub Actions OIDC](https://github.com/aws-samples/github-actions-oidc-cdk-construct)
- [CDK TypeScript Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-cdk-typescript-iac/development-best-practices.html)






