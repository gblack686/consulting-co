---
allowed-tools: Read, Grep, Glob, Write, mcp__supabase__execute_sql, mcp__supabase__list_tables, mcp__supabase__search_docs
description: Create implementation plan for Supabase Vault secrets management
argument-hint: [feature or task description]
---

# Supabase Vault Expert - Plan Mode

Create an implementation plan for secrets management using Supabase Vault. Uses expertise context to ensure security best practices.

## Variables

TASK_DESCRIPTION: $1
EXPERTISE_PATH: .claude/commands/experts/supabase/expertise.yaml
PLAN_OUTPUT: specs/supabase-vault-{timestamp}.md

## Instructions

- Create a detailed implementation plan for the requested secrets management
- Ensure security best practices are followed
- Consider access control and encryption patterns
- Include testing and validation steps
- Save the plan to the specs directory

## Workflow

1. **Load Context**
   - Read the `EXPERTISE_PATH` file
   - Identify relevant patterns for the task
   - Query current vault state

2. **Analyze Requirements**
   - Break down TASK_DESCRIPTION into specific operations
   - Identify secrets to be stored/managed
   - Consider security implications

3. **Design Solution**
   - Define secret naming conventions
   - Plan helper functions if needed
   - Design access control strategy
   - Plan integration approach

4. **Create Plan**
   - Write detailed implementation steps
   - Include SQL scripts
   - Document rollback procedures
   - Save to PLAN_OUTPUT

## Plan Template

```markdown
# Supabase Vault Implementation Plan: {TASK_TITLE}

**Created**: {timestamp}
**Expert**: Supabase Vault
**Status**: Draft

## Overview

{Brief description of what will be implemented}

## Secrets to Manage

| Secret Name | Purpose | Source | Rotation Frequency |
|-------------|---------|--------|-------------------|
| {NAME} | {purpose} | {where it comes from} | {how often to rotate} |

## Implementation Steps

### Step 1: Create Helper Functions (if needed)

**Why**: Centralize secret access with proper security

```sql
-- Helper function for secure secret retrieval
CREATE OR REPLACE FUNCTION public.get_secret(secret_name TEXT)
RETURNS TEXT AS $$
DECLARE
  secret TEXT := '';
BEGIN
  SELECT decrypted_secret INTO secret
  FROM vault.decrypted_secrets
  WHERE name = secret_name LIMIT 1;
  RETURN secret;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

REVOKE ALL ON FUNCTION public.get_secret FROM public;
GRANT EXECUTE ON FUNCTION public.get_secret TO service_role;
```

### Step 2: Store Secrets

**Method**: Using vault.create_secret() (recommended)

```sql
-- Create secrets
SELECT vault.create_secret('{value}', '{NAME}', '{description}');
```

### Step 3: Configure Access Control

```sql
-- Ensure proper access restrictions
REVOKE ALL ON vault.decrypted_secrets FROM public;
GRANT SELECT ON vault.decrypted_secrets TO service_role;
```

### Step 4: Integration Code

{How secrets will be used in application code}

## Security Checklist

- [ ] Secrets created via vault.create_secret() (not INSERT)
- [ ] Access restricted to service_role only
- [ ] Helper functions use SECURITY DEFINER
- [ ] No secrets exposed to client-side code
- [ ] Secret names follow naming convention
- [ ] Descriptions added for documentation

## Testing

- [ ] Verify secrets created: `SELECT name FROM vault.decrypted_secrets`
- [ ] Test helper function: `SELECT public.get_secret('NAME')`
- [ ] Verify access control: Test with anon role (should fail)
- [ ] Test integration: Verify application can retrieve secrets

## Rollback

```sql
-- Remove secrets if needed
DELETE FROM vault.secrets WHERE name IN ('SECRET_1', 'SECRET_2');

-- Remove helper functions if needed
DROP FUNCTION IF EXISTS public.get_secret;
```

## Migration Notes

{If migrating from another system}
- Source system: {AWS Secrets Manager, etc.}
- Secrets to migrate: {list}
- Post-migration cleanup: {steps}

## Cost Impact

- Previous cost: {if migrating}
- New cost: $0 (included with Supabase)
- Monthly savings: {calculation}
```

## Key Patterns

### Secret Naming Convention
```
{SERVICE}_{PURPOSE}_{ENVIRONMENT}
Examples:
- OPENAI_API_KEY
- STRIPE_SECRET_KEY_PROD
- SENDGRID_API_KEY_STAGING
```

### Secure Retrieval Pattern
```sql
-- Always use helper function, never direct query in application code
SELECT public.get_secret('SECRET_NAME');
```

### Edge Function Integration
```typescript
// In Edge Function
const { data: apiKey } = await supabase.rpc('get_secret', {
  secret_name: 'API_KEY'
});
```
