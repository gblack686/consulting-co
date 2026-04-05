#!/usr/bin/env python3
"""Test psycopg3 SYNCHRONOUS connection (no asyncio issues)"""
import socket

def resolve_to_ip(hostname, port):
    """Synchronously resolve hostname to IP"""
    try:
        result = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        return result[0][4][0]
    except Exception as e:
        print(f"❌ DNS failed: {e}")
        return None

def test_sync_connection():
    """Test psycopg3 synchronous connection"""
    try:
        import psycopg
        from psycopg.rows import dict_row

        # Resolve hostname first
        hostname = "aws-0-us-west-1.pooler.supabase.com"
        port = 6543
        print(f"Resolving {hostname}:{port}...")
        ip = resolve_to_ip(hostname, port)
        if not ip:
            return False
        print(f"✅ Resolved to: {ip}")

        # Use raw password with IP
        url = f"postgresql://postgres.unickqnwfheaczccvgbw:G^qjC7F$@P65DqpN*mmv@{ip}:{port}/postgres"

        print("Connecting with SYNC psycopg...")
        with psycopg.connect(url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT version()')
                result = cur.fetchone()
                print(f"✅ SUCCESS! PostgreSQL: {result['version'][:60]}...")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_sync_connection()
    sys.exit(0 if success else 1)
