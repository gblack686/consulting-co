# Supabase Setup for Multi-Agent Orchestrator

## ✅ Credentials Added

I've added your Supabase credentials to `.env`:
- ✅ SUPABASE_URL
- ✅ SUPABASE_SERVICE_KEY
- ⚠️ DATABASE_URL (needs password)

## 🔑 Get Your Database Password

You need to get your Supabase database password to complete the `DATABASE_URL`:

### Option 1: From Supabase Dashboard (Recommended)

1. **Go to your project settings:**
   https://supabase.com/dashboard/project/unickqnwfheaczccvgbw/settings/database

2. **Find "Database Password" section**
   - Look for "Connection string" or "Database password"
   - You may need to reset the password if you don't have it

3. **Reset password (if needed):**
   - Click "Reset database password"
   - Copy the new password immediately
   - Update `.env` file

### Option 2: Use Connection Pooler

Supabase provides a connection pooler that's better for serverless:

**Format:**
```
postgresql://postgres.unickqnwfheaczccvgbw:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

## 📝 Update .env File

Once you have your password, update line 41 in `.env`:

**Before:**
```bash
DATABASE_URL=postgresql://postgres:[YOUR-DB-PASSWORD]@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres
```

**After (Direct Connection):**
```bash
DATABASE_URL=postgresql://postgres:your_actual_password@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres
```

**OR (Connection Pooler - Recommended):**
```bash
DATABASE_URL=postgresql://postgres.unickqnwfheaczccvgbw:your_actual_password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

## 🧪 Test Connection

After updating the password, test the connection:

```bash
# Test with psql (if installed)
psql "postgresql://postgres:your_password@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres" -c "SELECT version();"

# Or with Python
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:your_password@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres'))"
```

## ⚡ Quick Steps

1. Get password from: https://supabase.com/dashboard/project/unickqnwfheaczccvgbw/settings/database
2. Update line 41 in `.env`
3. Save file
4. Continue with migration!

## 🚨 Security Note

**Never commit your database password to git!**

The `.env` file should already be in `.gitignore`. Verify with:
```bash
grep ".env" .gitignore
```

## Need Help?

If you can't find the password:
1. Reset it from the Supabase dashboard
2. Use the new password immediately
3. Store it securely (password manager)

Ready to proceed once you have the password! 🎯
