#!/usr/bin/env python3
"""Test asyncpg with Windows Selector Event Loop Policy fix"""
import asyncio
import sys

# Apply the Windows fix
if sys.platform == 'win32':
    print("Applying WindowsSelectorEventLoopPolicy...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_async_connection():
    """Test asyncpg connection with the Windows fix"""
    print("\nTesting asyncpg connection with Windows event loop fix...")

    try:
        import asyncpg

        # Try to create a connection pool
        print("Creating connection pool...")
        # Use direct connection (port 5432) instead of pooler
        pool = await asyncpg.create_pool(
            'postgresql://postgres.unickqnwfheaczccvgbw:G%5EqjC7F%24%40P65DqpN%2Ammv@db.unickqnwfheaczccvgbw.supabase.co:5432/postgres',
            min_size=1,
            max_size=2,
            command_timeout=60
        )

        print("✅ SUCCESS! Connection pool created!")

        # Test a simple query
        async with pool.acquire() as conn:
            result = await conn.fetchval('SELECT version()')
            print(f"✅ Query successful: {result[:50]}...")

        await pool.close()
        return True

    except ImportError:
        print("❌ asyncpg not installed")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_async_connection())
    sys.exit(0 if success else 1)
