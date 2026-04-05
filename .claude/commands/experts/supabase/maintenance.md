---
allowed-tools: Read, Write, Glob, Grep, mcp__supabase__execute_sql, mcp__supabase__list_tables, mcp__supabase__get_advisors
description: Run Supabase Vault health checks, security audits, and maintenance tasks
argument-hint: [--audit | --inventory | --rotate SECRET_NAME]
---

# Supabase Vault Expert - Maintenance Command

Execute Vault maintenance tasks including health checks, security audits, and secret inventory management.

## Purpose

Run security audits, check secret health, manage rotation, and generate inventory reports for Supabase Vault.

## Modes

### Mode 1: Security Audit (--audit)

Run a comprehensive security audit of the Vault configuration.

**Checks**:
1. Access control on vault tables
2. Helper function security
3. RLS status
4. Exposed secrets in logs (advisory)

**SQL Queries**:
```sql
-- Check table permissions
SELECT grantee, privilege_type, table_name
FROM information_schema.table_privileges
WHERE table_schema = 'vault';

-- Check function security
SELECT p.proname, p.prosecdef as security_definer
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public' AND p.proname LIKE '%secret%';

-- Check RLS status
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'vault';
```

### Mode 2: Secret Inventory (--inventory)

Generate a complete inventory of all stored secrets.

**Output**:
```markdown
## Vault Secret Inventory

**Generated**: {timestamp}
**Total Secrets**: {count}

| Name | Description | Created | Last Updated | Age (days) |
|------|-------------|---------|--------------|------------|
| {name} | {desc} | {created} | {updated} | {age} |

### Secrets by Age
- 0-30 days: {count}
- 31-90 days: {count}
- 90+ days: {count} (consider rotation)

### Unnamed Secrets
{List of secrets without names - should be documented}

### Recommendations
- {Secrets that should be rotated}
- {Missing descriptions to add}
```

**SQL Queries**:
```sql
-- Full inventory
SELECT
  name,
  description,
  created_at,
  updated_at,
  EXTRACT(day FROM NOW() - created_at) as age_days
FROM vault.decrypted_secrets
ORDER BY created_at;

-- Secrets needing attention
SELECT name, created_at
FROM vault.decrypted_secrets
WHERE created_at < NOW() - INTERVAL '90 days'
  OR description = ''
  OR name IS NULL;
```

### Mode 3: Secret Rotation (--rotate SECRET_NAME)

Guide through rotating a specific secret.

**Workflow**:
1. Verify secret exists
2. Prompt for new value
3. Update using vault.update_secret()
4. Verify update
5. Document rotation

**SQL**:
```sql
-- Get current secret info
SELECT id, name, description, updated_at
FROM vault.decrypted_secrets
WHERE name = '{SECRET_NAME}';

-- Update secret
SELECT vault.update_secret(
  '{secret_id}',
  '{new_value}',
  '{name}',
  '{description} - Rotated on {date}'
);

-- Verify
SELECT name, updated_at FROM vault.decrypted_secrets WHERE name = '{SECRET_NAME}';
```

## Health Check Queries

```sql
-- Vault extension status
SELECT * FROM pg_extension WHERE extname IN ('supabase_vault', 'pgsodium');

-- Secret count
SELECT COUNT(*) as total_secrets FROM vault.secrets;

-- Recent activity
SELECT name, updated_at
FROM vault.decrypted_secrets
WHERE updated_at > NOW() - INTERVAL '7 days'
ORDER BY updated_at DESC;

-- Orphaned keys (secrets without names)
SELECT id, created_at
FROM vault.secrets
WHERE name IS NULL;
```

## Report Format

```markdown
## Vault Maintenance Report

**Date**: {timestamp}
**Mode**: {audit/inventory/rotate}
**Status**: {HEALTHY | ATTENTION NEEDED | CRITICAL}

### Summary

- Total secrets: {count}
- Secrets needing rotation: {count}
- Security issues: {count}

### Details

{Mode-specific details}

### Actions Taken

- {Action 1}
- {Action 2}

### Recommendations

1. {Recommendation with priority}
2. {Recommendation with priority}

### Next Maintenance

- Scheduled rotation: {dates}
- Next audit: {date}
```

## Scheduled Maintenance Tasks

### Weekly
- [ ] Run inventory check
- [ ] Review secrets needing rotation

### Monthly
- [ ] Full security audit
- [ ] Update expertise with new patterns
- [ ] Review access logs (if enabled)

### Quarterly
- [ ] Rotate all secrets older than 90 days
- [ ] Review and clean up unused secrets
- [ ] Update documentation

## Troubleshooting During Maintenance

### Issue: Cannot access vault tables
```sql
-- Check your role
SELECT current_user, current_setting('role');

-- Reset to service_role if needed
SET ROLE service_role;
```

### Issue: Secret not updating
```sql
-- Get the correct UUID
SELECT id, name FROM vault.secrets WHERE name = 'SECRET_NAME';

-- Use the UUID in update
SELECT vault.update_secret('correct-uuid-here', 'new-value');
```

### Issue: Extension not found
```sql
-- Check enabled extensions
SELECT * FROM pg_extension;

-- Vault should be enabled by default on Supabase
```

## Integration with Supabase Advisors

Run security advisors to check for vault-related issues:

```
mcp__supabase__get_advisors with type: "security"
```

Look for:
- Missing RLS policies
- Exposed credentials
- Permission issues
