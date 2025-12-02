# Remote Coding Agent - Setup Summary

**Date**: 2025-12-01
**Status**: ✅ Successfully configured and running

## Working Configuration

### Database Connection (Supabase)

**Connection String:**
```env
DATABASE_URL=postgresql://postgres.unickqnwfheaczccvgbw:jK9mP2xL7nQ4vR8wT3yU6hB5gN1fD0sA9zX8cV7bM6nL5kJ4hG3fD2sA1qW0eR9tY8uI7oP6@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

**Critical Details:**
- **Project**: unickqnwfheaczccvgbw
- **Region**: us-west-1 (NOT us-east-1!)
- **Username**: postgres.unickqnwfheaczccvgbw (session pooler format)
- **Password**: jK9mP2xL7nQ4vR8wT3yU6hB5gN1fD0sA9zX8cV7bM6nL5kJ4hG3fD2sA1qW0eR9tY8uI7oP6
- **Host**: aws-0-us-west-1.pooler.supabase.com
- **Port**: 5432 (session mode)

### AI Assistant

**Claude Code OAuth Token:**
```env
CLAUDE_CODE_OAUTH_TOKEN=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
DEFAULT_AI_ASSISTANT=claude
```

### Platform Adapters

**Telegram Bot:**
```env
TELEGRAM_BOT_TOKEN=7932711311:AAGovFJlihqc6pOjoxw8EKYb9Zdtq4acduA
TELEGRAM_STREAMING_MODE=stream
```

**GitHub:**
```env
GH_TOKEN=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PHeSS
GITHUB_TOKEN=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PHeSS
WEBHOOK_SECRET=your_random_secret_string
GITHUB_STREAMING_MODE=batch
```

## Database Schema

**Tables Created (via Supabase MCP):**
1. `remote_agent_codebases` - Repository metadata
2. `remote_agent_conversations` - Platform conversation tracking
3. `remote_agent_sessions` - AI session management

**Migration Applied:**
- `migrations/001_initial_schema.sql` via Supabase MCP server

## Running the Application

### On Host Machine (✅ Working)

```bash
cd C:\Users\gblac\OneDrive\Desktop\consulting-co\tools\remote-coding-agent
npm start
```

**Output:**
```
[Database] Connected successfully
[Telegram] Adapter initialized (mode: stream, timeout: disabled)
[GitHub] Webhook adapter ready
[Express] Health check server listening on port 3000
```

### Docker (❌ Not Working on Windows)

**Issue**: Docker Desktop on Windows has DNS resolution issues with Supabase pooler hostname
- Error: `EAI_AGAIN aws-0-us-west-1.pooler.supabase.com`
- Root cause: Windows Docker Desktop IPv6/DNS limitations
- Solution: Use host machine with `npm start` instead

## Key Lessons Learned

1. **Region Matters**: Initially tried `us-east-1`, but actual project is in `us-west-1`
2. **Username Format**: Must use `postgres.{projectref}` for Supabase session pooler (not just `postgres`)
3. **Password Special Characters**: Avoid `^`, `%`, `#` in passwords - causes URL encoding issues
4. **Windows Docker DNS**: Docker Desktop on Windows can't resolve Supabase pooler hostnames reliably
5. **Password Location**: Database password is in **Project Settings → Database**, NOT shown in connection strings
6. **Supabase Never Shows Password**: After initial reset, you must save it - Supabase won't show it again

## Health Checks

**Basic Health:**
```bash
curl http://localhost:3000/health
# Expected: {"status":"ok"}
```

**Database Health:**
```bash
curl http://localhost:3000/health/db
# Expected: {"status":"ok","database":"connected"}
```

**Concurrency:**
```bash
curl http://localhost:3000/health/concurrency
# Expected: {"status":"ok","active":0,"queued":0,"maxConcurrent":10}
```

## Troubleshooting Reference

### SCRAM Authentication Error
- **Cause**: Wrong password or password not set in Supabase
- **Fix**: Reset password in Supabase Project Settings → Database

### Tenant or User Not Found
- **Cause**: Wrong region or username format
- **Fix**: Verify region matches dashboard, use `postgres.{projectref}` username format

### EAI_AGAIN DNS Error
- **Cause**: Docker Desktop on Windows DNS issues
- **Fix**: Run on host machine with `npm start`

## Repository Location

```
C:\Users\gblac\OneDrive\Desktop\consulting-co\tools\remote-coding-agent
```

**Git Submodule:**
- Added as submodule in `consulting-co` project
- Upstream: https://github.com/dynamous-community/remote-coding-agent

## Next Steps

1. Test Telegram bot interaction
2. Configure GitHub webhooks (optional)
3. Test `/clone` and command system
4. Create custom commands in `.claude/commands/`
