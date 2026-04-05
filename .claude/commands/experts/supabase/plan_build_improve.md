---
allowed-tools: Read, Grep, Glob, Write, Edit, mcp__supabase__execute_sql, mcp__supabase__apply_migration, mcp__supabase__list_tables, mcp__supabase__search_docs
description: Complete Vault workflow - plan, build, and self-improve expertise
argument-hint: [feature or task description]
---

# Supabase Vault Expert - Plan Build Improve Workflow

Complete ACT-LEARN-REUSE workflow for secrets management: plan the implementation, build it, validate, and update expertise with learnings.

## Variables

TASK_DESCRIPTION: $1
EXPERTISE_PATH: .claude/commands/experts/supabase/expertise.yaml

## Instructions

Execute the full secrets management workflow:
1. **PLAN** - Create implementation plan using expertise
2. **BUILD** - Implement the secrets and helper functions
3. **VALIDATE** - Test secret storage and retrieval
4. **IMPROVE** - Update expertise with learnings

## Phase 1: Plan

### Load Context
- Read EXPERTISE_PATH for existing patterns
- Query current vault state
- Identify security requirements

### Create Plan
- Define secrets to store
- Specify naming conventions
- Plan helper functions
- Document access control strategy

### Deliverable
- Implementation plan with clear steps
- Security checklist
- Rollback procedures

## Phase 2: Build

### Step 1: Create Helper Functions (if needed)

```sql
-- Secure secret retrieval function
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

-- Restrict access
REVOKE ALL ON FUNCTION public.get_secret FROM public;
GRANT EXECUTE ON FUNCTION public.get_secret TO service_role;
```

### Step 2: Store Secrets

```sql
-- Using vault.create_secret() - NEVER use INSERT directly
SELECT vault.create_secret(
  'actual-secret-value',
  'SECRET_NAME',
  'Description of what this secret is used for'
);
```

### Step 3: Configure Access Control

```sql
-- Ensure vault tables are protected
REVOKE ALL ON vault.secrets FROM public;
REVOKE ALL ON vault.decrypted_secrets FROM public;
GRANT SELECT ON vault.decrypted_secrets TO service_role;
```

### Step 4: Integration Code

**For Edge Functions:**
```typescript
// Supabase Edge Function
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
);

// Get secret via RPC
const { data: apiKey } = await supabase.rpc('get_secret', {
  secret_name: 'OPENAI_API_KEY'
});
```

**For Database Functions:**
```sql
CREATE OR REPLACE FUNCTION call_external_api(endpoint TEXT)
RETURNS json AS $$
DECLARE
  api_key TEXT;
  response json;
BEGIN
  -- Get secret
  api_key := public.get_secret('API_KEY');

  -- Use in HTTP call (requires pg_net)
  SELECT content INTO response
  FROM net.http_get(
    endpoint,
    headers := jsonb_build_object('Authorization', 'Bearer ' || api_key)
  );

  RETURN response;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Phase 3: Validate

### Test Secret Storage

```sql
-- Verify secrets were created
SELECT name, description, created_at
FROM vault.decrypted_secrets
WHERE name = 'SECRET_NAME';

-- Test retrieval (should return the value)
SELECT public.get_secret('SECRET_NAME');
```

### Test Access Control

```sql
-- This should work (as service_role)
SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'SECRET_NAME';

-- Verify anon/authenticated cannot access (test from application)
```

### Validation Checklist

- [ ] Secrets created successfully
- [ ] Helper function returns correct values
- [ ] Access control restricts public access
- [ ] Integration code retrieves secrets
- [ ] No secrets in application logs

## Phase 4: Improve

### Update Expertise

After successful implementation, update EXPERTISE_PATH with:

1. **New Secrets**
   - Add to use_cases section if new pattern
   - Document naming convention used

2. **New Functions**
   - Add to helper_functions section
   - Document usage patterns

3. **Security Learnings**
   - Note any access control configurations
   - Document permission patterns

4. **Integration Patterns**
   - Add new integration examples
   - Document edge cases found

### Learning Documentation

```markdown
## Implementation Learnings

**Task**: {TASK_DESCRIPTION}
**Date**: {timestamp}

### Secrets Created

| Name | Purpose | Integration |
|------|---------|-------------|
| {name} | {purpose} | {where used} |

### What Worked Well
- {Pattern or approach that was effective}

### Challenges Encountered
- {Issue}: {How it was resolved}

### Patterns to Reuse
- {Pattern worth documenting for future use}

### Expertise Updates Made
- {Section}: {What was updated}
```

## Workflow Summary

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    PLAN     │───>│    BUILD    │───>│  VALIDATE   │───>│   IMPROVE   │
│             │    │             │    │             │    │             │
│ - Context   │    │ - Functions │    │ - Test SQL  │    │ - Update    │
│ - Security  │    │ - Secrets   │    │ - Access    │    │   expertise │
│ - Steps     │    │ - Integrate │    │ - Integrat. │    │ - Document  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Quick Reference

**Create Secret**:
```sql
SELECT vault.create_secret('value', 'NAME', 'description');
```

**Retrieve Secret**:
```sql
SELECT public.get_secret('NAME');
```

**List All Secrets**:
```sql
SELECT name, description FROM vault.decrypted_secrets;
```

**Update Secret**:
```sql
SELECT vault.update_secret(
  (SELECT id FROM vault.secrets WHERE name = 'NAME'),
  'new-value'
);
```

**Delete Secret**:
```sql
DELETE FROM vault.secrets WHERE name = 'NAME';
```

## Security Reminders

1. **Never use INSERT** - Always use `vault.create_secret()` to avoid logging
2. **Restrict access** - Only service_role should access decrypted_secrets
3. **Use SECURITY DEFINER** - Helper functions should use this for proper permissions
4. **Document secrets** - Always add meaningful descriptions
5. **Rotate periodically** - Plan for secret rotation
