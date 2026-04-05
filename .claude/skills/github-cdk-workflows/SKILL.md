# GitHub & AWS CDK Workflows Skill

> **Purpose**: Comprehensive knowledge for building GitHub workflows, Git lifecycle management, and AWS CDK CI/CD pipelines.

## Triggers

Use this skill when user mentions:
- GitHub Actions workflows
- CDK pipelines
- CI/CD setup
- PR validation workflows
- Deployment automation
- Git branching strategies

## Quick Reference

### Git Lifecycle

```
WORKING → STAGING → LOCAL → REMOTE
  edit    git add   commit   push
```

### GitHub Actions Workflow Structure

```yaml
name: Workflow Name

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Step Name
        run: npm ci
```

### AWS CDK Workflow Layers

| Layer | Purpose | When |
|-------|---------|------|
| **PR Validation** | Lint, test, synth, diff | All PRs |
| **Staging Deploy** | Deploy + smoke tests | Merge to main |
| **Production Deploy** | Manual approval + deploy | Release/manual |

## Workflow Templates

### PR Validation

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation

on:
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npx cdk synth

  diff:
    runs-on: ubuntu-latest
    needs: validate
    permissions:
      id-token: write
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - name: CDK Diff
        run: npx cdk diff 2>&1 | tee diff-output.txt
```

### Staging Deployment

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.STAGING_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: npx cdk deploy --all --require-approval never
      - name: Smoke tests
        run: curl -f ${{ vars.API_ENDPOINT }}/health
```

### Production Deployment

```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      confirm:
        description: 'Type "deploy" to confirm'
        required: true
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    if: github.event.inputs.confirm == 'deploy' || github.event_name == 'release'
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.PROD_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: npx cdk deploy --all --require-approval never
      - name: Health check
        run: |
          for i in {1..5}; do
            curl -f ${{ vars.PROD_API_ENDPOINT }}/health && exit 0
            sleep 10
          done
          exit 1
```

## CDK Testing

### Test Types Priority

| Test | When | Priority |
|------|------|----------|
| Unit Tests | Every PR | Essential |
| Snapshot Tests | Every PR | Essential |
| CDK Assertions | Every PR | Essential |
| CDK Diff | Every PR | Essential |
| Smoke Tests | Staging | Recommended |
| Integration | Staging | Situational |

### CDK Assertion Example

```typescript
import { Template, Match } from 'aws-cdk-lib/assertions';
import * as cdk from 'aws-cdk-lib';
import { MyStack } from '../lib/my-stack';

describe('MyStack', () => {
  const app = new cdk.App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('Lambda function created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'nodejs18.x',
    });
  });

  test('Matches snapshot', () => {
    expect(template.toJSON()).toMatchSnapshot();
  });
});
```

## AWS Authentication

**Always use OIDC (no stored secrets):**

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ vars.AWS_REGION }}
```

Setup steps:
1. Create IAM OIDC Identity Provider for GitHub
2. Create IAM Role with trust policy for GitHub repo
3. Use `aws-actions/configure-aws-credentials@v4`

## Directory Structure

```
.github/
└── workflows/
    ├── pr-validation.yml     # All PRs
    ├── deploy-staging.yml    # Merge to main
    ├── deploy-prod.yml       # Manual/release
    ├── destroy-preview.yml   # Cleanup (optional)
    └── health-check.yml      # Cron monitoring
```

## Best Practices Checklist

**PR Validation:**
- [ ] Lint & format checks
- [ ] Unit tests
- [ ] CDK synth
- [ ] Snapshot tests
- [ ] CDK diff posted to PR

**Staging:**
- [ ] Auto-deploy on merge
- [ ] Smoke tests after deploy
- [ ] Notifications (Slack/Teams)

**Production:**
- [ ] Manual approval gate
- [ ] Health checks post-deploy
- [ ] Rollback plan ready

## Commands

This skill provides guidance for:
- Creating GitHub Actions workflows
- Setting up CDK CI/CD pipelines
- Configuring AWS OIDC authentication
- Writing CDK tests
- Structuring multi-environment deployments

## References

- [AWS CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
- [CDK Pipelines GitHub](https://github.com/cdklabs/cdk-pipelines-github)
- [GitHub Actions OIDC](https://github.com/aws-samples/github-actions-oidc-cdk-construct)
