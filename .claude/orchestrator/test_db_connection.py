#!/usr/bin/env python3
"""Test database connection from Docker container"""
import asyncio
import asyncpg
import sys

async def test_connection():
    # Use one of the resolved IPs
    database_url = "postgresql://postgres.unickqnwfheaczccvgbw:G^qjC7F$@P65DqpN*mmv@52.8.172.168:5432/postgres"

    print("Testing connection to Supabase...")
    print(f"URL: postgresql://postgres.unickqnwfheaczccvgbw:***@52.8.172.168:5432/postgres")

    try:
        conn = await asyncpg.connect(database_url, timeout=10)
        print("✅ Connection successful!")

        # Test query
        result = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {result}")

        await conn.close()
        return 0
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_connection())
    sys.exit(exit_code)
