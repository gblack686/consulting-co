---
name: supabase-query
description: "Query Supabase databases using natural language. Translates user intent into Supabase REST API calls via curl, returns formatted results. Supports select, insert, update, delete, RPC calls, and storage operations. Use when the user asks to query, read, write, or explore data in Supabase."
---

# Supabase Query Skill

## Overview

Translate natural language requests into Supabase PostgREST API calls. No SDK needed — uses `curl` against the Supabase REST API with the anon/service-role key.

## When to Use This Skill

- User says "query supabase", "check the database", "look up rows in …"
- User wants to insert, update, or delete records in Supabase
- User wants to list tables, inspect schema, or explore data
- User asks to call a Supabase RPC / Edge Function
- User wants to interact with Supabase Storage buckets

## Prerequisites

Two environment variables must be set (in `.env` or exported):

| Variable | Where to find it |
|---|---|
| `SUPABASE_URL` | Supabase Dashboard → Project Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Project Settings → API → `anon` `public` key |
| `SUPABASE_SERVICE_ROLE_KEY` | *(optional)* For admin operations that bypass RLS |

## Commands

### `/supabase-query select <table> [filters]`

Query rows from a table. Filters use PostgREST syntax.

**Examples:**
```
/supabase-query select users
/supabase-query select orders --filter "status=eq.pending" --limit 10
/supabase-query select products --filter "price=gte.100" --select "id,name,price" --order "price.desc"
```

**Implementation pattern:**
```bash
curl -s "${SUPABASE_URL}/rest/v1/<table>?<filters>" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Accept: application/json"
```

### `/supabase-query insert <table> <json_body>`

Insert one or more rows.

**Example:**
```
/supabase-query insert users '{"email": "test@example.com", "name": "Test User"}'
```

**Implementation pattern:**
```bash
curl -s "${SUPABASE_URL}/rest/v1/<table>" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '<json_body>'
```

### `/supabase-query update <table> <json_body> --filter <match>`

Update rows matching a filter.

**Example:**
```
/supabase-query update users '{"name": "Updated Name"}' --filter "id=eq.42"
```

**Implementation pattern:**
```bash
curl -s -X PATCH "${SUPABASE_URL}/rest/v1/<table>?<filter>" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '<json_body>'
```

### `/supabase-query delete <table> --filter <match>`

Delete rows matching a filter. **Filter is required** to prevent accidental full-table deletes.

**Example:**
```
/supabase-query delete users --filter "id=eq.42"
```

### `/supabase-query rpc <function_name> [json_args]`

Call a Postgres function exposed via Supabase RPC.

**Example:**
```
/supabase-query rpc get_monthly_revenue '{"month": "2026-03"}'
```

**Implementation pattern:**
```bash
curl -s "${SUPABASE_URL}/rest/v1/rpc/<function_name>" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '<json_args>'
```

### `/supabase-query schema [table]`

List all tables, or show columns for a specific table.

**Implementation pattern (list tables):**
```bash
# Uses the OpenAPI spec that PostgREST auto-generates
curl -s "${SUPABASE_URL}/rest/v1/" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Accept: application/openapi+json"
```

### `/supabase-query storage ls [bucket] [path]`

List Storage buckets, or files within a bucket.

### `/supabase-query raw <method> <path> [body]`

Escape hatch — make any raw REST call against the Supabase API.

**Example:**
```
/supabase-query raw GET "/rest/v1/users?select=id,email&limit=5"
```

## PostgREST Filter Reference

| Operator | Meaning | Example |
|---|---|---|
| `eq` | Equals | `status=eq.active` |
| `neq` | Not equals | `status=neq.deleted` |
| `gt` / `gte` | Greater than (or equal) | `price=gte.100` |
| `lt` / `lte` | Less than (or equal) | `age=lt.30` |
| `like` | Pattern match (% wildcard) | `name=like.*smith*` |
| `ilike` | Case-insensitive like | `email=ilike.*@gmail.com` |
| `in` | In list | `id=in.(1,2,3)` |
| `is` | Null check | `deleted_at=is.null` |
| `cs` | Contains (array/json) | `tags=cs.{news}` |
| `or` | OR conditions | `or=(status.eq.active,status.eq.pending)` |

## Execution Rules

1. **Always load credentials** — Before any curl call, check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set. If missing, tell the user what to configure.
2. **Pretty-print JSON** — Pipe output through `python3 -m json.tool` or `jq` for readability.
3. **Confirm destructive ops** — For `update`, `delete`, and `insert`, show the user the exact curl command and ask for confirmation before executing.
4. **Limit by default** — Add `&limit=50` to selects unless the user specifies otherwise, to avoid dumping huge tables.
5. **Use anon key by default** — Only use `SUPABASE_SERVICE_ROLE_KEY` when the user explicitly requests admin/bypass-RLS access.
6. **Handle errors gracefully** — If the API returns an error JSON (`{"message": "...", "code": "..."}`), surface it clearly to the user with suggested fixes.

## Natural Language Translation

When the user asks in plain English, map their intent:

| User says | Skill action |
|---|---|
| "show me all users" | `select users` |
| "find orders over $100" | `select orders --filter "total=gte.100"` |
| "add a new product" | `insert products '{...}'` (ask for fields) |
| "delete that row" | `delete <table> --filter "id=eq.<id>"` |
| "what tables do I have?" | `schema` |
| "run the monthly report function" | `rpc <function_name>` |
