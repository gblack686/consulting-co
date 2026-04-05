# Run Migrations Manually via Supabase SQL Editor

Due to Windows network/DNS issues with asyncpg, let's run the migrations directly in Supabase's SQL Editor.

## 🎯 Quick Steps

1. **Go to Supabase SQL Editor:**
   https://supabase.com/dashboard/project/unickqnwfheaczccvgbw/sql/new

2. **Copy and paste each migration file** (in order):

### Migration 1: Orchestrator Agents Table
```sql
-- File: 0_orchestrator_agents.sql
-- Copy content from: .claude/orchestrator/orchestrator_db/migrations/0_orchestrator_agents.sql
```

### Migration 2: Agents Table
```sql
-- File: 1_agents.sql
-- Copy content from: .claude/orchestrator/orchestrator_db/migrations/1_agents.sql
```

### Migration 3-8: Continue with remaining files...
```
2_prompts.sql
3_agent_logs.sql
4_system_logs.sql
5_indexes.sql
6_functions.sql
7_triggers.sql
8_orchestrator_chat.sql
```

## 📋 Automated Script

Or use this script to generate a single SQL file:

```bash
cd .claude/orchestrator/orchestrator_db
cat migrations/*.sql > all_migrations.sql
```

Then copy the contents of `all_migrations.sql` and run it in one go!

## ✅ Verify Tables Created

After running, check in Supabase Table Editor:
- orchestrator_agents
- agents
- prompts
- agent_logs
- system_logs
- orchestrator_chat

## 🔄 Alternative: Supabase CLI

If you have Supabase CLI installed:
```bash
supabase db push
```

Would you like me to:
1. Generate the combined SQL file for you?
2. Show you the migration SQL to copy/paste?
3. Try a different connection method?
