#!/usr/bin/env python3
"""Test psycopg3 connection with Windows-friendly approach"""
import asyncio
import sys
import os

# Apply the Windows fix
if sys.platform == 'win32':
    print("Applying WindowsSelectorEventLoopPolicy...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_psycopg_connection():
    """Test psycopg3 connection"""
    print("\nTesting psycopg3 connection...")

    try:
        import psycopg
        from psycopg_pool import AsyncConnectionPool
        from psycopg.rows import dict_row

        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres.unickqnwfheaczccvgbw:G%5EqjC7F%24%40P65DqpN%2Ammv@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres")

        print(f"Creating connection pool...")
        # Create async connection pool
        pool = AsyncConnectionPool(
            conninfo=database_url,
            min_size=1,
            max_size=2,
            kwargs={"row_factory": dict_row},
            timeout=60
        )

        print("✅ SUCCESS! Connection pool created!")

        # Test a simple query
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute('SELECT version()')
                result = await cur.fetchone()
                print(f"✅ Query successful: {result['version'][:50]}...")

        await pool.close()
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_psycopg_connection())
    sys.exit(0 if success else 1)
