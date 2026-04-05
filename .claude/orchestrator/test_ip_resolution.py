#!/usr/bin/env python3
"""Resolve hostname to IP and test connection"""
import socket
import asyncio
import sys
import os

# Apply the Windows fix
if sys.platform == 'win32':
    print("Applying WindowsSelectorEventLoopPolicy...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def resolve_hostname(hostname, port):
    """Synchronously resolve hostname to IP"""
    print(f"Resolving {hostname}:{port}...")
    try:
        result = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        ip = result[0][4][0]
        print(f"✅ Resolved to: {ip}")
        return ip
    except Exception as e:
        print(f"❌ Resolution failed: {e}")
        return None

async def test_with_ip():
    """Test psycopg3 connection using IP address"""
    try:
        import psycopg
        from psycopg_pool import AsyncConnectionPool
        from psycopg.rows import dict_row

        # Original connection string (using pooler)
        original_url = "postgresql://postgres.unickqnwfheaczccvgbw:G%5EqjC7F%24%40P65DqpN%2Ammv@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

        # Resolve hostname to IP
        hostname = "aws-0-us-west-1.pooler.supabase.com"
        port = 6543
        ip = resolve_hostname(hostname, port)

        if not ip:
            return False

        # Replace hostname with IP in connection string
        url_with_ip = original_url.replace(hostname, ip)
        print(f"\nUsing connection string with IP: {url_with_ip[:80]}...")

        print("Creating connection pool with IP address...")
        pool = AsyncConnectionPool(
            conninfo=url_with_ip,
            min_size=1,
            max_size=2,
            kwargs={"row_factory": dict_row},
            timeout=60
        )

        print("✅ SUCCESS! Connection pool created with IP!")

        # Test a simple query
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute('SELECT version()')
                result = await cur.fetchone()
                print(f"✅ Query successful: {result['version'][:50]}...")

        await pool.close()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_with_ip())
    sys.exit(0 if success else 1)
