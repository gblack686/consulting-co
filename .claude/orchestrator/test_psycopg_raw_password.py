#!/usr/bin/env python3
"""Test psycopg3 with raw password and IP resolution"""
import asyncio
import sys
import socket

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def resolve_to_ip(hostname, port):
    """Synchronously resolve hostname to IP"""
    try:
        result = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        return result[0][4][0]
    except Exception as e:
        print(f"❌ DNS failed: {e}")
        return None

async def test_connection():
    """Test psycopg3 with resolved IP and raw password"""
    try:
        import psycopg
        from psycopg_pool import AsyncConnectionPool
        from psycopg.rows import dict_row

        # Resolve hostname first
        hostname = "aws-0-us-west-1.pooler.supabase.com"
        port = 6543
        print(f"Resolving {hostname}:{port}...")
        ip = resolve_to_ip(hostname, port)
        if not ip:
            return False
        print(f"✅ Resolved to: {ip}")

        # Use raw password (psycopg handles special chars)
        url = f"postgresql://postgres.unickqnwfheaczccvgbw:G^qjC7F$@P65DqpN*mmv@{ip}:{port}/postgres"

        print("Creating connection pool...")
        pool = AsyncConnectionPool(
            conninfo=url,
            min_size=1,
            max_size=2,
            kwargs={"row_factory": dict_row},
            timeout=60
        )

        print("✅ Pool created!")

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute('SELECT version()')
                result = await cur.fetchone()
                print(f"✅ Connected! PostgreSQL version: {result['version'][:60]}...")

        await pool.close()
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
