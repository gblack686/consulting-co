#!/usr/bin/env python
# /// script
# requires-python = ">=3.7"
# dependencies = [
#   "asyncpg>=0.27.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
Simple migration runner using asyncpg (no psql required)
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncpg
from urllib.parse import unquote

# Load environment variables
load_dotenv()

DATABASE_URL_RAW = os.getenv("DATABASE_URL")

if not DATABASE_URL_RAW:
    print("❌ DATABASE_URL not found in .env file!")
    exit(1)

# URL-decode the password in the DATABASE_URL
# Format: postgresql://user:encoded_pass@host:port/db
# We need to decode just the password part
import re
match = re.match(r'(postgresql://[^:]+:)([^@]+)(@.+)', DATABASE_URL_RAW)
if match:
    prefix, encoded_password, suffix = match.groups()
    decoded_password = unquote(encoded_password)
    DATABASE_URL = prefix + decoded_password + suffix
    print(f"🔓 Decoded URL-encoded password")
else:
    DATABASE_URL = DATABASE_URL_RAW

MIGRATIONS = [
    "0_orchestrator_agents.sql",
    "1_agents.sql",
    "2_prompts.sql",
    "3_agent_logs.sql",
    "4_system_logs.sql",
    "5_indexes.sql",
    "6_functions.sql",
    "7_triggers.sql",
    "8_orchestrator_chat.sql",
]

async def run_migrations():
    """Run all migrations in order"""
    migrations_dir = Path(__file__).parent / "migrations"

    print(f"🔌 Connecting to: {DATABASE_URL[:50]}...")

    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database!")

        for migration_file in MIGRATIONS:
            migration_path = migrations_dir / migration_file

            if not migration_path.exists():
                print(f"⚠️  Skipping {migration_file} (not found)")
                continue

            print(f"\n📝 Running: {migration_file}")
            sql = migration_path.read_text()

            try:
                await conn.execute(sql)
                print(f"✅ {migration_file} - SUCCESS")
            except Exception as e:
                print(f"❌ {migration_file} - FAILED: {e}")
                raise

        print("\n" + "="*50)
        print("✅ All migrations completed successfully!")
        print("="*50)

        await conn.close()

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migrations())
