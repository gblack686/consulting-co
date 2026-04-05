---
allowed-tools: Read, Grep, Glob, Write, Edit, mcp__supabase__execute_sql, mcp__supabase__list_tables, mcp__supabase__search_docs
description: Self-improve Supabase Vault expertise by validating against actual database
argument-hint: [optional: specific area to focus on]
---

# Supabase Vault Expert - Self-Improve Mode

Validate and update the Supabase Vault expertise knowledge base by comparing documented patterns against actual database implementation.

## Variables

FOCUS_AREA: $1
EXPERTISE_PATH: .claude/commands/experts/supabase/expertise.yaml

## Instructions

- Compare expertise.yaml against actual Supabase Vault state
- Identify discrepancies, outdated information, or missing knowledge
- Update expertise.yaml with accurate, current information
- Document learnings from actual usage patterns

## Workflow

1. **Validate Current Expertise**
   - Read EXPERTISE_PATH
   - Query actual vault schema and secrets
   - Compare documented vs actual patterns

2. **Identify Gaps**
   - New secrets not documented
   - Changed patterns not reflected
   - Missing helper functions
   - Outdated security recommendations

3. **Update Expertise**
   - Add new secret documentation
   - Update changed patterns
   - Refresh security details
   - Update integration examples

4. **Report Changes**
   - List what was updated
   - Explain why changes were made
   - Note any patterns worth highlighting

## Validation Queries

### Schema Validation
```sql
-- Check vault.secrets table structure
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_schema = 'vault' AND table_name = 'secrets';

-- Check if vault extension is enabled
SELECT * FROM pg_extension WHERE extname = 'supabase_vault';
```

### Secrets Inventory
```sql
-- List all stored secrets (metadata only)
SELECT name, description, created_at, updated_at
FROM vault.decrypted_secrets
ORDER BY created_at;

-- Count secrets
SELECT COUNT(*) as total_secrets FROM vault.secrets;
```

### Helper Functions Check
```sql
-- Check if get_secret function exists
SELECT proname, prosrc
FROM pg_proc
WHERE proname LIKE '%secret%';

-- Check function permissions
SELECT grantee, privilege_type
FROM information_schema.routine_privileges
WHERE routine_name = 'get_secret';
```

### Access Control Check
```sql
-- Check table permissions
SELECT grantee, privilege_type
FROM information_schema.table_privileges
WHERE table_schema = 'vault';
```

## Validation Checklist

### Schema
- [ ] vault.secrets table exists and matches documentation
- [ ] vault.decrypted_secrets view exists
- [ ] Column types are accurate
- [ ] Default values are correct

### Secrets
- [ ] All production secrets are documented
- [ ] Naming conventions are followed
- [ ] Descriptions are meaningful
- [ ] No orphaned/unused secrets

### Security
- [ ] Access control is properly configured
- [ ] Helper functions use SECURITY DEFINER
- [ ] No public access to vault tables
- [ ] service_role has appropriate access

### Integrations
- [ ] Edge Function patterns are current
- [ ] Database function patterns work
- [ ] pg_net integration documented if used

### Documentation
- [ ] All use cases are covered
- [ ] Troubleshooting is accurate
- [ ] Best practices are up to date

## Report Format

```markdown
## Self-Improvement Report

**Date**: {timestamp}
**Focus Area**: {FOCUS_AREA or "Full Validation"}

### Current State

- Total secrets stored: {count}
- Helper functions: {list or "none"}
- Access control status: {configured/needs attention}

### Changes Made to Expertise

1. **{Section}**
   - Before: {old value}
   - After: {new value}
   - Reason: {why changed}

### New Additions

- {New knowledge added}

### Secrets Inventory

| Name | Description | Last Updated |
|------|-------------|--------------|
| {name} | {desc} | {date} |

### Security Audit

| Check | Status | Notes |
|-------|--------|-------|
| Table permissions | {ok/issue} | {details} |
| Function security | {ok/issue} | {details} |
| RLS enabled | {ok/issue} | {details} |

### Recommendations

- {Suggested improvements}
- {Security enhancements needed}
- {Documentation gaps to fill}

### Validation Status

| Area | Status | Notes |
|------|--------|-------|
| Schema | {ok/updated/issue} | {details} |
| Secrets | {ok/updated/issue} | {details} |
| Security | {ok/updated/issue} | {details} |
| Integrations | {ok/updated/issue} | {details} |
```

## Auto-Update Rules

When finding discrepancies:
1. Schema changes -> Update schema section
2. New secrets -> Add to use_cases if relevant pattern
3. Security changes -> Update security section
4. New functions -> Add to helper_functions section
5. Issues found -> Add to troubleshooting section
