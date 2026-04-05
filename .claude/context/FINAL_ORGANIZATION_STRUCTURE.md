# Final AWS Secrets Manager Organization Structure

## Corrected Hierarchy

```
gbautomation/                          ← Personal/consulting business
├── core/
│   ├── openai-api-key
│   ├── anthropic-api-key
│   ├── apify-api-token
│   └── ref-tools-api-key
│
├── infrastructure/
│   ├── supabase
│   ├── neo4j-graphiti
│   └── langfuse
│
├── aws/
│   ├── cli-default
│   └── langfuse-s3
│
└── projects/
    └── gb-automation-landing/
        └── amplify

revstar/                               ← RevStar client work
├── shared/                            ← Shared across ALL RevStar projects
│   ├── elevenlabs
│   └── langfuse
│
├── board-director/
│   └── aws
│
├── nexus/
│   ├── aws
│   └── langfuse
│
├── compcorrect/
│   └── aws
│
├── parenting-autism/
│   └── [credentials TBD]
│
├── word-collections/
│   └── [credentials TBD]
│
├── perl-street/
│   └── [credentials TBD]
│
├── agentcore/
│   └── [credentials TBD]
│
├── acme-test/
│   └── [credentials TBD]
│
├── 1kosmos/
│   └── [credentials TBD]
│
├── dataforinclusion/
│   └── [credentials TBD]
│
├── epibone/
│   └── [credentials TBD]
│
├── hst-powers/
│   └── [credentials TBD]
│
├── roam365/
│   └── [credentials TBD]
│
└── theragraph/
    └── [credentials TBD]

wsc/                                   ← WSC client work (if any)
└── [to be added when WSC projects are found]
```

## Key Changes from Previous Version

### Before (Incorrect):
- ❌ `consulting-co/personal/` - Too nested
- ❌ `consulting-co/revstar/` - Unnecessary prefix

### After (Correct):
- ✅ `gbautomation/` - Personal/consulting business (top-level)
- ✅ `revstar/` - RevStar client (top-level)
- ✅ `wsc/` - WSC client (top-level, when needed)

## Organization Mapping

| Prefix | Type | Description |
|--------|------|-------------|
| `gbautomation/` | Personal | Your consulting business, personal projects |
| `revstar/` | Client | RevStar client work folder |
| `wsc/` | Client | WSC client work folder |

## All RevStar Quickstart Projects Found

From `../aws/RevStar/quickstarts/`:

1. ✅ **board-director** - Has AWS credentials
2. ✅ **nexus** - Has AWS credentials + Langfuse instance
3. ✅ **compcorrect** - Shares AWS with nexus
4. **parenting-autism** - Check for credentials
5. **word-collections** - Check for credentials
6. **perl-street** - Check for credentials
7. **agentcore** - Check for credentials
8. **acme-test** - Check for credentials
9. **1kosmos** - Check for credentials
10. **dataforinclusion** - Check for credentials
11. **epibone** - Check for credentials
12. **hst-powers** - Check for credentials
13. **roam365** - Check for credentials
14. **theragraph** - Check for credentials
15. **llm-ops-referral-buddy** - Check for credentials

## Shared vs Project-Specific Resources

### Shared Across ALL RevStar Projects (`revstar/shared/`)
- **ElevenLabs API Key** - All projects use same TTS
- **Langfuse Organization** - Default observability (unless project has own instance)

### Project-Specific (`revstar/{project-name}/`)
- **AWS Credentials** - Each project typically has own AWS account
- **Langfuse Instances** - Some projects (like Nexus) run their own
- **Project Databases** - Project-specific data stores

## AWS Tags for Each Organization

### GBAutomation Tags
```
Organization=gbautomation
Type=personal
Service=[service-name]
Project=[project-name]  (when applicable)
Environment=[dev|staging|production]
```

### RevStar Tags
```
Organization=revstar
Type=client
Project=[project-name]
Service=[service-name]
Environment=[dev|staging|production]
Shared=[true|false]  (for shared resources)
```

### WSC Tags (when added)
```
Organization=wsc
Type=client
Project=[project-name]
Service=[service-name]
Environment=[dev|staging|production]
```

## Common Query Examples

### List all personal (gbautomation) secrets:
```bash
aws secretsmanager list-secrets \
  --query 'SecretList[?starts_with(Name, `gbautomation/`)].Name'
```

### List all RevStar secrets:
```bash
aws secretsmanager list-secrets \
  --query 'SecretList[?starts_with(Name, `revstar/`)].Name'
```

### List only RevStar board-director secrets:
```bash
aws secretsmanager list-secrets \
  --query 'SecretList[?starts_with(Name, `revstar/board-director/`)].Name'
```

### List all RevStar shared resources:
```bash
aws secretsmanager list-secrets \
  --query 'SecretList[?starts_with(Name, `revstar/shared/`)].Name'
```

### Filter by organization tag:
```bash
aws secretsmanager list-secrets \
  --filters Key=tag-key,Values=Organization Key=tag-value,Values=revstar
```

### Filter by client type:
```bash
aws secretsmanager list-secrets \
  --filters Key=tag-key,Values=Type Key=tag-value,Values=client
```

## IAM Policy Example - Organization Level

### Grant access to ALL gbautomation secrets:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ],
    "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:gbautomation/*"
  }]
}
```

### Grant access to ALL RevStar secrets:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ],
    "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:revstar/*"
  }]
}
```

### Grant access to specific RevStar project + shared:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ],
    "Resource": [
      "arn:aws:secretsmanager:us-east-1:*:secret:revstar/shared/*",
      "arn:aws:secretsmanager:us-east-1:*:secret:revstar/board-director/*"
    ]
  }]
}
```

## Cost Tracking by Organization

### Enable Cost Allocation Tags:
1. AWS Billing Console → Cost Allocation Tags
2. Activate: `Organization`, `Type`, `Project`, `Service`

### View costs by organization:
```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=TAG,Key=Organization
```

Result will show:
- `gbautomation` costs (personal/consulting)
- `revstar` costs (client work)
- `wsc` costs (client work)

## Next Steps

1. ✅ Updated script: `store-credentials-to-kms-FINAL.bat`
2. ⏳ Run script to upload all credentials
3. ⏳ Verify with list commands
4. ⏳ Check remaining quickstart projects for credentials
5. ⏳ Add WSC projects if found
6. ⏳ Update applications to fetch from new paths
7. ⏳ Clean up local credential files

## Summary

- **GBAutomation** = Your personal/consulting business
- **RevStar** = Client work folder (NOT under gbautomation)
- **WSC** = Client work folder (NOT under gbautomation)
- Each organization is **top-level** in Secrets Manager
- Use **tags** to further categorize and filter
- Use **hierarchical naming** for logical structure within each org
