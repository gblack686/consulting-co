# RevStar QuickStart Conventions & Best Practices

## Project Structure

### Standard Directory Layout

```
quickstart-{client-name}/
├── .claude/
│   ├── commands/          # Custom slash commands
│   ├── agents/            # Sub-agent definitions
│   ├── skills/            # Project-specific skills
│   └── mcp.json          # MCP server configuration
├── backend/
│   └── poc{X}-{name}/
│       ├── code/
│       │   ├── lambda/    # Lambda functions
│       │   └── glue-jobs/ # Glue ETL jobs
│       └── infra/         # CDK infrastructure
│           ├── bin/
│           ├── lib/
│           └── cdk.json
├── frontend/              # UI application
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── tests/                 # Test suites
```

---

## Naming Conventions

### Lambda Functions

**Pattern**: `{service}-{action}-{resource}`

**Examples**:
- `s3-metadata-handler`
- `glue-trigger`
- `poc2-query`
- `query-results`
- `query-status`

### CDK Stacks

**Pattern**: `{Project}{PocNumber}{Purpose}Stack`

**Examples**:
- `BoardDirectorPoc2AdvancedStack`
- `BoardDirectorPoc2SimpleStack`
- `DataLakeFoundationStack`

### DynamoDB Tables

**Pattern**: `{Project}-{Purpose}-{Environment}`

**Examples**:
- `BoardDirector-Metadata-Dev`
- `BoardDirector-QueryResults-Prod`

### S3 Buckets

**Pattern**: `{project}-{purpose}-{account-id}-{region}`

**Examples**:
- `board-director-documents-123456789012-us-east-1`
- `board-director-processed-123456789012-us-east-1`

### Git Branches

**Pattern**: `{type}/{description}`

**Types**:
- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions

**Examples**:
- `feature/user-authentication`
- `fix/s3-metadata-handler`
- `refactor/lambda-error-handling`

### Git Commits

**Pattern**: `{type}: {description}`

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Maintenance

**Examples**:
- `feat: add user authentication module`
- `fix: resolve S3 metadata extraction issue`
- `docs: update architecture diagram`

---

## CDK Best Practices

### Stack Organization

1. **Separate Concerns**: One stack per logical boundary
2. **Shared Resources**: Create foundation stacks
3. **Environment Isolation**: Use parameters/context for environments
4. **Avoid Circular Dependencies**: Design stack boundaries carefully

### Construct Patterns

```typescript
// Good: Reusable constructs
export class ApiLambdaConstruct extends Construct {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: ApiLambdaProps) {
    super(scope, id);

    this.function = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(props.codePath),
      environment: props.environment,
      timeout: Duration.minutes(5),
      memorySize: 512,
    });
  }
}
```

### Resource Naming

```typescript
// Use consistent naming with project prefix
const table = new dynamodb.Table(this, 'MetadataTable', {
  tableName: `${projectName}-Metadata-${environment}`,
  partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  removalPolicy: RemovalPolicy.DESTROY, // Change for production
});
```

### Environment Variables

```typescript
// Centralize environment configuration
const commonEnv = {
  ENVIRONMENT: environment,
  LOG_LEVEL: 'INFO',
  PROJECT_NAME: projectName,
};

// Pass to Lambda
const handler = new lambda.Function(this, 'Handler', {
  environment: {
    ...commonEnv,
    TABLE_NAME: table.tableName,
  },
});
```

---

## Lambda Best Practices

### Function Structure

```python
# Standard Lambda handler structure
import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for {purpose}.

    Args:
        event: Lambda event object
        context: Lambda context object

    Returns:
        Response with statusCode and body
    """
    try:
        logger.info(f"Event: {json.dumps(event)}")

        # Business logic here
        result = process_event(event)

        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        }
```

### Error Handling

```python
# Use custom exceptions
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class ProcessingError(Exception):
    """Raised when processing fails."""
    pass

# Handle errors gracefully
def process_event(event):
    if not event.get('required_field'):
        raise ValidationError("Missing required_field")

    try:
        # Processing logic
        return result
    except Exception as e:
        raise ProcessingError(f"Processing failed: {str(e)}")
```

### Logging

```python
# Structured logging
logger.info("Processing started", extra={
    'event_id': event['id'],
    'user_id': event.get('user_id'),
    'operation': 'process',
})

# Log timing
import time
start_time = time.time()
# ... processing ...
duration = time.time() - start_time
logger.info(f"Processing completed in {duration:.2f}s")
```

---

## Testing Standards

### Unit Tests

```python
# Test file naming: test_{module_name}.py
import unittest
from unittest.mock import Mock, patch
from lambda_function import handler

class TestHandler(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.event = {
            'body': json.dumps({'key': 'value'})
        }
        self.context = Mock()

    def test_successful_processing(self):
        """Test successful event processing."""
        response = handler(self.event, self.context)
        self.assertEqual(response['statusCode'], 200)

    def test_missing_required_field(self):
        """Test error handling for missing fields."""
        event = {'body': json.dumps({})}
        response = handler(event, self.context)
        self.assertEqual(response['statusCode'], 400)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
# Test AWS service integrations
import boto3
import pytest

@pytest.fixture
def s3_bucket():
    """Create test S3 bucket."""
    s3 = boto3.client('s3')
    bucket_name = 'test-bucket'
    s3.create_bucket(Bucket=bucket_name)
    yield bucket_name
    # Cleanup
    s3.delete_bucket(Bucket=bucket_name)

def test_s3_upload(s3_bucket):
    """Test S3 file upload."""
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=s3_bucket,
        Key='test.txt',
        Body='test content'
    )
    # Verify upload
    response = s3.get_object(Bucket=s3_bucket, Key='test.txt')
    assert response['Body'].read() == b'test content'
```

### E2E Tests with Playwright

```python
# frontend/tests/test_user_flow.py
from playwright.sync_api import Page, expect

def test_document_upload_flow(page: Page):
    """Test complete document upload workflow."""
    # Navigate to application
    page.goto("http://localhost:3000")

    # Login
    page.fill('input[name="email"]', 'test@example.com')
    page.fill('input[name="password"]', 'password')
    page.click('button[type="submit"]')

    # Upload document
    page.set_input_files('input[type="file"]', 'test-document.pdf')
    page.click('button:has-text("Upload")')

    # Verify document appears
    expect(page.locator('text=test-document.pdf')).to_be_visible()

    # Verify in settings
    page.click('a:has-text("Settings")')
    page.click('a:has-text("My Documents")')
    expect(page.locator('text=test-document.pdf')).to_be_visible()

    # Test delete functionality
    page.click('button:has-text("Delete")')
    page.click('button:has-text("Confirm")')
    expect(page.locator('text=test-document.pdf')).not_to_be_visible()
```

---

## Documentation Standards

### README Structure

```markdown
# {Project Name}

## Overview
Brief description of the project and its purpose.

## Architecture
High-level architecture diagram and description.

## Prerequisites
- Node.js 20+
- AWS CLI configured
- Python 3.11+

## Setup
Step-by-step setup instructions.

## Deployment
Deployment procedures for each environment.

## Testing
How to run tests.

## Troubleshooting
Common issues and solutions.

## Cost Considerations
Expected AWS costs and optimization tips.
```

### Code Documentation

```python
def process_document(document_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process document and extract metadata.

    This function reads a document from S3, extracts text content,
    analyzes metadata, and stores results in DynamoDB.

    Args:
        document_path: S3 path to document (s3://bucket/key)
        metadata: Additional metadata to associate with document
            - user_id: User identifier
            - upload_date: ISO format timestamp
            - document_type: Type classification

    Returns:
        Dictionary containing:
            - document_id: Generated document identifier
            - text_content: Extracted text
            - metadata: Combined metadata
            - processing_status: Success/failure status

    Raises:
        ValidationError: If document_path is invalid
        ProcessingError: If extraction fails

    Example:
        >>> metadata = {'user_id': '123', 'document_type': 'invoice'}
        >>> result = process_document('s3://bucket/doc.pdf', metadata)
        >>> print(result['document_id'])
        'doc-uuid-1234'
    """
    pass
```

---

## Security Best Practices

### IAM Policies

```typescript
// Principle of least privilege
const lambdaRole = new iam.Role(this, 'LambdaRole', {
  assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
  managedPolicies: [
    iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
  ],
});

// Grant specific permissions only
table.grantReadWriteData(lambdaRole);
bucket.grantRead(lambdaRole);
```

### Environment Secrets

```typescript
// Never hardcode secrets
// Use AWS Secrets Manager or Parameter Store
const secret = secretsmanager.Secret.fromSecretNameV2(
  this,
  'ApiKey',
  'quickstart/api-key'
);

const handler = new lambda.Function(this, 'Handler', {
  environment: {
    SECRET_ARN: secret.secretArn,
  },
});

secret.grantRead(handler);
```

### Input Validation

```python
# Always validate input
def validate_input(data: Dict[str, Any]) -> None:
    """Validate input data."""
    required_fields = ['user_id', 'document_path']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate format
    if not data['document_path'].startswith('s3://'):
        raise ValidationError("Invalid S3 path")
```

---

## Cost Optimization

### Lambda Configuration

```typescript
// Right-size Lambda functions
const handler = new lambda.Function(this, 'Handler', {
  memorySize: 512,  // Start small, monitor, adjust
  timeout: Duration.seconds(30),  // Be specific, not generous
  reservedConcurrentExecutions: 10,  // Prevent runaway costs
});

// Use ARM for cost savings
const handler = new lambda.Function(this, 'Handler', {
  architecture: lambda.Architecture.ARM_64,  // ~20% cost savings
});
```

### DynamoDB

```typescript
// Use on-demand for unpredictable workloads
const table = new dynamodb.Table(this, 'Table', {
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
});

// Use provisioned for predictable workloads
const table = new dynamodb.Table(this, 'Table', {
  billingMode: dynamodb.BillingMode.PROVISIONED,
  readCapacity: 5,
  writeCapacity: 5,
});
```

### OpenSearch

```typescript
// Use t3.small.search for development
// Avoid standby replicas unless necessary
const domain = new opensearch.Domain(this, 'Domain', {
  version: opensearch.EngineVersion.OPENSEARCH_2_11,
  capacity: {
    dataNodes: 1,
    dataNodeInstanceType: 't3.small.search',
    masterNodes: 0,  // Not needed for dev
  },
  ebs: {
    volumeSize: 10,  // Minimum for testing
    volumeType: ec2.EbsDeviceVolumeType.GP3,
  },
});
```

### Monitoring Costs

```typescript
// Set billing alarms
const alarm = new cloudwatch.Alarm(this, 'BillingAlarm', {
  metric: new cloudwatch.Metric({
    namespace: 'AWS/Billing',
    metricName: 'EstimatedCharges',
    statistic: 'Maximum',
  }),
  threshold: 100,  // Alert at $100
  evaluationPeriods: 1,
});
```

---

## Version Control

### .gitignore

```
# AWS
cdk.out/
.cdk.staging/
*.zip
cdk-outputs.json

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# Environment
.env
.env.local

# Logs
*.log
```

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature development
- `fix/*` - Bug fixes
- `release/*` - Release preparation

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```
