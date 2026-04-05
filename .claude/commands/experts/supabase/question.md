---
allowed-tools: Read, Grep, Glob, mcp__supabase__execute_sql, mcp__supabase__list_tables, mcp__supabase__search_docs
description: Answer questions about Supabase Vault secrets management without making changes
argument-hint: [question]
---

# Supabase Vault Expert - Question Mode

Answer the user's question by analyzing Supabase Vault configuration, secrets, and patterns. This prompt provides information without making any changes.

## Variables

USER_QUESTION: $1
EXPERTISE_PATH: .claude/commands/experts/supabase/expertise.yaml

## Instructions

- IMPORTANT: This is a question-answering task only - DO NOT create, edit, or delete any secrets
- Focus on Vault operations, encryption, security patterns, and integration approaches
- If the question requires changes, explain the approach conceptually without implementing
- Validate information from `EXPERTISE_PATH` against the actual Supabase project

## Workflow

1. **Load Expertise**
   - Read the `EXPERTISE_PATH` file to understand Vault architecture
   - Identify relevant sections for the USER_QUESTION

2. **Validate Against Database**
   - Query vault.decrypted_secrets to verify current secrets
   - Check helper functions if they exist
   - Verify schema matches documented structure

3. **Formulate Answer**
   - Provide direct answer with specific SQL examples
   - Include security considerations where relevant
   - Reference actual implementation patterns

## Question Categories

### Category 1: Secret Management Questions
Questions about storing, retrieving, or updating secrets.

**Examples**:
- "How do I store an API key?"
- "How do I retrieve a secret by name?"
- "How do I update an existing secret?"

**Resolution**:
1. Read expertise.yaml operations section
2. Query current secrets: `SELECT name, description FROM vault.decrypted_secrets`
3. Provide SQL examples with security best practices

### Category 2: Security Questions
Questions about encryption, access control, and security patterns.

**Examples**:
- "How is data encrypted?"
- "Who can access secrets?"
- "How do I restrict access?"

**Resolution**:
1. Read expertise.yaml security section
2. Explain AEAD encryption and key storage
3. Provide RLS and permission examples

### Category 3: Integration Questions
Questions about using secrets in Edge Functions, triggers, or external calls.

**Examples**:
- "How do I use secrets in Edge Functions?"
- "How do I call an API with a stored secret?"
- "How do I use secrets in webhooks?"

**Resolution**:
1. Read expertise.yaml integrations section
2. Explain the pattern for the specific use case
3. Provide code examples

### Category 4: Migration Questions
Questions about moving from AWS Secrets Manager or other systems.

**Examples**:
- "How do I migrate from AWS Secrets Manager?"
- "What's the cost savings?"
- "How do I export secrets?"

**Resolution**:
1. Read expertise.yaml migration section
2. Provide step-by-step migration plan
3. Calculate cost comparison

### Category 5: Troubleshooting Questions
Questions about errors, access issues, or unexpected behavior.

**Examples**:
- "Why can't I access my secrets?"
- "Why are secrets appearing in logs?"
- "How do I fix permission denied?"

**Resolution**:
1. Read expertise.yaml troubleshooting section
2. Query current state to diagnose
3. Provide specific fixes

## Key SQL Commands

```sql
-- List all secrets (metadata only)
SELECT name, description, created_at FROM vault.decrypted_secrets;

-- Get specific secret value
SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'SECRET_NAME';

-- Check vault schema
SELECT * FROM vault.secrets LIMIT 1;

-- Check if helper function exists
SELECT proname FROM pg_proc WHERE proname = 'get_secret';
```

## Report

```markdown
## Answer

{Direct answer to the USER_QUESTION}

## Details

{Supporting explanation with SQL examples if helpful}

## Security Notes

{Any relevant security considerations}

## Related Commands

```sql
-- Useful SQL for this topic
{sql 1}
{sql 2}
```

## Source Reference

- Primary: Supabase Vault documentation
- Expertise: `EXPERTISE_PATH` section: {section_name}
```
