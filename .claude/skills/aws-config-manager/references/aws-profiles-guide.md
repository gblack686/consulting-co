# AWS Profiles and Credentials Guide

## Overview

This guide explains how to configure and manage AWS profiles for use with the aws-config-manager skill.

## Credential Types

### 1. Static Credentials (Long-term)

Store access keys directly in `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[development]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

**Security Note:** Avoid using long-term credentials when possible. Prefer SSO or assumed roles.

### 2. AWS SSO (Recommended)

Configure SSO profiles in `~/.aws/config`:

```ini
[profile sso-dev]
sso_start_url = https://my-sso-portal.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = DeveloperAccess
region = us-west-2
output = json

[profile sso-prod]
sso_start_url = https://my-sso-portal.awsapps.com/start
sso_region = us-east-1
sso_account_id = 987654321098
sso_role_name = ReadOnlyAccess
region = us-east-1
```

**Login:**
```bash
aws sso login --profile sso-dev
```

### 3. Assumed Roles

Configure role assumption in `~/.aws/config`:

```ini
[profile base]
region = us-east-1

[profile admin-role]
role_arn = arn:aws:iam::123456789012:role/AdminRole
source_profile = base
region = us-east-1

[profile cross-account]
role_arn = arn:aws:iam::987654321098:role/CrossAccountRole
source_profile = base
external_id = my-external-id
region = us-west-2
```

### 4. MFA-Protected Profiles

```ini
[profile mfa-user]
region = us-east-1

[profile mfa-protected]
role_arn = arn:aws:iam::123456789012:role/MFAProtectedRole
source_profile = mfa-user
mfa_serial = arn:aws:iam::123456789012:mfa/my-device
```

## Credential Precedence

AWS SDK uses credentials in this order:

1. **Environment Variables**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN`

2. **Shared Credentials File** (`~/.aws/credentials`)

3. **AWS Config File** (`~/.aws/config`)

4. **Container Credentials** (ECS task role)

5. **Instance Profile Credentials** (EC2 instance role)

## Environment Variables

```bash
# Static credentials
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Session token (for temporary credentials)
export AWS_SESSION_TOKEN="AQoDYXdzEJr..."

# Profile selection
export AWS_PROFILE="development"

# Region
export AWS_DEFAULT_REGION="us-east-1"
```

## Using Profiles with aws-config-manager

### List Available Profiles

```bash
python scripts/credentials_manager.py --action list-profiles
```

### Validate a Profile

```bash
python scripts/credentials_manager.py --action validate --profile development
```

### Get Profile Details

```bash
python scripts/credentials_manager.py --action profile-details --profile sso-dev
```

### Assume a Role

```bash
python scripts/credentials_manager.py --action assume-role \
  --role-arn arn:aws:iam::123456789012:role/AdminRole \
  --session-name my-session \
  --profile base
```

## Multi-Account Setup

For organizations with multiple AWS accounts:

```ini
# ~/.aws/config

# Management Account
[profile mgmt]
sso_start_url = https://corp.awsapps.com/start
sso_region = us-east-1
sso_account_id = 111111111111
sso_role_name = AdministratorAccess
region = us-east-1

# Development Account
[profile dev]
sso_start_url = https://corp.awsapps.com/start
sso_region = us-east-1
sso_account_id = 222222222222
sso_role_name = DeveloperAccess
region = us-west-2

# Production Account (Read-Only)
[profile prod-ro]
sso_start_url = https://corp.awsapps.com/start
sso_region = us-east-1
sso_account_id = 333333333333
sso_role_name = ReadOnlyAccess
region = us-east-1

# Production Account (Admin - requires MFA)
[profile prod-admin]
role_arn = arn:aws:iam::333333333333:role/AdminRole
source_profile = mgmt
mfa_serial = arn:aws:iam::111111111111:mfa/admin-user
```

## Best Practices

### 1. Use SSO When Possible
- No long-term credentials to manage
- Centralized access control
- Automatic credential rotation

### 2. Principle of Least Privilege
- Create profiles with minimal required permissions
- Use read-only profiles for exploration
- Reserve admin profiles for specific tasks

### 3. Naming Conventions
```
<environment>-<role>
Examples:
  dev-admin
  dev-readonly
  prod-readonly
  prod-deploy
```

### 4. Profile Aliases

In `aws-settings.json`, configure aliases for convenience:

```json
{
  "profiles": {
    "aliases": {
      "d": "development",
      "p": "production",
      "s": "staging"
    }
  }
}
```

### 5. Security

- Never commit credentials to version control
- Use `.gitignore` to exclude `~/.aws/credentials`
- Rotate access keys regularly (every 90 days)
- Enable MFA for sensitive operations
- Monitor credential usage with CloudTrail

## Troubleshooting

### "Unable to locate credentials"

1. Check if credentials file exists: `ls ~/.aws/credentials`
2. Verify environment variables: `env | grep AWS`
3. Ensure profile name is correct: `--profile <exact-name>`

### "The security token included in the request is expired"

For SSO profiles:
```bash
aws sso login --profile <profile-name>
```

For assumed roles, the session may have expired. Re-run the assume-role command.

### "Access Denied"

1. Verify the profile has required permissions
2. Check resource-based policies (e.g., S3 bucket policy)
3. Verify MFA is not required but not provided

### SSO Session Issues

Clear SSO cache and re-login:
```bash
rm -rf ~/.aws/sso/cache/*
aws sso login --profile <profile-name>
```

## Integration with Other Tools

### AWS CLI

```bash
aws s3 ls --profile development
aws ec2 describe-instances --profile production --region us-west-2
```

### Terraform

```hcl
provider "aws" {
  profile = "development"
  region  = "us-east-1"
}
```

### Boto3 (Python)

```python
import boto3

# Use specific profile
session = boto3.Session(profile_name='development')
s3 = session.client('s3')

# Use default profile
s3 = boto3.client('s3')
```

## Quick Reference

| Task | Command |
|------|---------|
| List profiles | `python scripts/credentials_manager.py -a list-profiles` |
| Validate credentials | `python scripts/credentials_manager.py -a validate -p <profile>` |
| SSO login | `aws sso login --profile <profile>` |
| Get identity | `python scripts/account_info.py -a identity -p <profile>` |
| Assume role | `python scripts/credentials_manager.py -a assume-role --role-arn <arn>` |
