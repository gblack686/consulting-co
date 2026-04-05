# AWS KMS Credentials Storage Setup Guide

This guide explains how to securely store and retrieve all your credentials using AWS Secrets Manager (encrypted with AWS KMS).

## Why AWS Secrets Manager + KMS?

- **Encryption at Rest**: All secrets are encrypted using AWS KMS
- **Automatic Rotation**: Supports automatic credential rotation
- **Access Control**: Fine-grained IAM policies control who can access secrets
- **Audit Trail**: CloudTrail logs all secret access
- **Versioning**: Maintains version history of secrets
- **Cost Effective**: ~$0.40/month per secret + $0.05 per 10,000 API calls

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws --version
   aws configure
   ```

2. **IAM Permissions Required**
   - `secretsmanager:CreateSecret`
   - `secretsmanager:GetSecretValue`
   - `secretsmanager:UpdateSecret`
   - `secretsmanager:ListSecrets`
   - `kms:Decrypt`
   - `kms:Encrypt` (optional: uses default KMS key if not specified)

## Quick Start

### 1. Store All Credentials

Run the storage script to upload all credentials to AWS Secrets Manager:

```bash
# Make the script executable
chmod +x .claude/context/store-credentials-to-kms.sh

# Run the script
./.claude/context/store-credentials-to-kms.sh
```

This will create secrets in the format: `consulting-co/SECRET_NAME`

### 2. Retrieve Credentials

Use the retrieval script to fetch credentials:

```bash
# Make the script executable
chmod +x .claude/context/retrieve-credentials-from-kms.sh

# Interactive mode
./.claude/context/retrieve-credentials-from-kms.sh

# Direct retrieval
./.claude/context/retrieve-credentials-from-kms.sh openai-api-key
```

## Stored Secrets

All secrets are stored under the `consulting-co/` namespace:

### API Keys
- `gbautomation/core/openai-api-key` - OpenAI API Key
- `gbautomation/core/anthropic-api-key` - Anthropic Claude API Key
- `gbautomation/core/linear-api-key` - Linear API Key
- `gbautomation/core/apify-api-token` - Apify API Token
- `gbautomation/core/ref-tools-api-key` - Ref Tools API Key
- `revstar/shared/elevenlabs` - ElevenLabs TTS API Key

### AWS Credentials
- `consulting-co/aws-cli-default` - AWS CLI Default Profile
- `consulting-co/aws-board-director` - Board Director Project AWS Credentials
- `consulting-co/aws-nexus-compcorrect` - Nexus/CompCorrect AWS Credentials
- `consulting-co/aws-langfuse-s3` - Langfuse S3 AWS Credentials

### Database & Services
- `consulting-co/supabase-gbautomation` - Supabase Project Credentials
- `consulting-co/neo4j-graphiti` - Neo4j Knowledge Graph Credentials

### Observability
- `consulting-co/langfuse-consulting-co` - Langfuse Consulting-Co Org
- `consulting-co/langfuse-revstar` - Langfuse RevStar Org
- `consulting-co/langfuse-nexus` - Langfuse Nexus Instance

### Other
- `consulting-co/amplify-gb-automation` - AWS Amplify AppSync API
- `consulting-co/mcp-tokens` - MCP Server Access Tokens

## Manual AWS CLI Commands

### Retrieve a Secret
```bash
aws secretsmanager get-secret-value \
  --secret-id consulting-co/openai-api-key \
  --region us-east-1 \
  --query 'SecretString' \
  --output text
```

### List All Secrets
```bash
aws secretsmanager list-secrets \
  --region us-east-1 \
  --query 'SecretList[?starts_with(Name, `consulting-co/`)].Name'
```

### Update a Secret
```bash
aws secretsmanager update-secret \
  --secret-id consulting-co/openai-api-key \
  --secret-string "new-api-key-value" \
  --region us-east-1
```

### Delete a Secret (with recovery period)
```bash
aws secretsmanager delete-secret \
  --secret-id consulting-co/SECRET_NAME \
  --recovery-window-in-days 30 \
  --region us-east-1
```

## Integration Examples

### Bash Script Integration
```bash
#!/bin/bash
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id consulting-co/openai-api-key \
  --region us-east-1 \
  --query 'SecretString' \
  --output text)
```

### Python Integration
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=f'consulting-co/{secret_name}')
    return json.loads(response['SecretString'])

# Example usage
aws_creds = get_secret('aws-cli-default')
print(aws_creds['access_key_id'])
```

### Node.js Integration
```javascript
const { SecretsManagerClient, GetSecretValueCommand } = require("@aws-sdk/client-secrets-manager");

async function getSecret(secretName) {
  const client = new SecretsManagerClient({ region: "us-east-1" });
  const response = await client.send(
    new GetSecretValueCommand({ SecretId: `consulting-co/${secretName}` })
  );
  return JSON.parse(response.SecretString);
}

// Example usage
const apiKey = await getSecret('openai-api-key');
```

## Security Best Practices

1. **Use IAM Roles**: Prefer IAM roles over hardcoded credentials
2. **Least Privilege**: Grant minimal required permissions
3. **Enable CloudTrail**: Monitor all secret access
4. **Regular Rotation**: Rotate credentials periodically
5. **Tag Secrets**: Use tags for organization and cost tracking
6. **KMS Key Policies**: Use custom KMS keys for additional control

## Costs

Estimated monthly costs (us-east-1):
- **Storage**: 16 secrets × $0.40 = $6.40/month
- **API Calls**: ~10,000 retrievals × $0.05 = $0.50/month
- **Total**: ~$7/month

## Cleanup Local Credentials

After verifying KMS storage works, consider:

1. ✅ Keep `.env` files in `.gitignore`
2. ✅ Remove credentials from shell scripts
3. ✅ Secure or remove `.lightsail-default-key` file
4. ✅ Clear AWS credentials from `~/.aws/credentials` if using IAM roles
5. ✅ Update MCP configurations to use KMS retrieval

## Troubleshooting

### Permission Denied
```bash
# Check your IAM permissions
aws iam get-user
aws secretsmanager list-secrets --region us-east-1
```

### Secret Not Found
```bash
# Verify secret exists
aws secretsmanager describe-secret \
  --secret-id consulting-co/SECRET_NAME \
  --region us-east-1
```

### KMS Decryption Failed
```bash
# Check KMS key permissions
aws kms describe-key --key-id alias/aws/secretsmanager
```

## Next Steps

1. Run `store-credentials-to-kms.sh` to upload all credentials
2. Test retrieval with `retrieve-credentials-from-kms.sh`
3. Update your applications to fetch credentials from KMS
4. Set up automatic credential rotation (optional)
5. Configure CloudWatch alerts for secret access
