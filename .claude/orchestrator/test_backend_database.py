#!/usr/bin/env python3
"""
Test the adapted database module with psycopg2.

This tests:
1. DNS resolution via dns_resolver module
2. Connection pool initialization
3. Synchronous database operations
4. Async wrapper functions
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'orchestrator_3_stream', 'backend'))

from modules.database import init_pool, get_orchestrator, close_pool


async def test_database_connection():
    """Test the complete database connection flow."""

    print("=" * 70)
    print("TESTING PSYCOPG2 DATABASE MODULE")
    print("=" * 70)

    try:
        # Step 1: Initialize connection pool
        print("\n[1/4] Initializing connection pool...")
        pool = await init_pool()
        print(f"✅ Pool initialized: {pool}")
        print(f"   - Pool connections: {pool.minconn} min, {pool.maxconn} max")

        # Step 2: Test synchronous connection from pool
        print("\n[2/4] Testing synchronous connection from pool...")
        from modules.database import get_connection
        with get_connection() as conn:
            print(f"✅ Got connection: {conn}")
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                result = cur.fetchone()
                print(f"✅ Query successful!")
                print(f"   PostgreSQL version: {result[0][:80]}...")

        # Step 3: Test async wrapper function
        print("\n[3/4] Testing async wrapper function (get_orchestrator)...")
        orchestrator = await get_orchestrator()
        if orchestrator:
            print(f"✅ Orchestrator found!")
            print(f"   - ID: {orchestrator['id']}")
            print(f"   - Status: {orchestrator['status']}")
            print(f"   - Working dir: {orchestrator.get('working_dir', 'N/A')}")
        else:
            print("ℹ️  No orchestrator exists yet (this is normal for first run)")

        # Step 4: Test table query
        print("\n[4/4] Testing database schema...")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = cur.fetchall()
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table[0]}")

        # Step 5: Clean up
        print("\n[5/5] Closing connection pool...")
        await close_pool()
        print("✅ Pool closed successfully")

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! Database module is working correctly!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)
